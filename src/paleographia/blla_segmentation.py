"""Neural line segmentation with Kraken's default ``blla`` model, in the pinned Docker runtime.

The projection segmenter slices a page into horizontal bands and fails on slanted,
large or bleed-through handwriting. ``blla`` returns one baseline and one polygon
per text line. Each line becomes a crop of its polygon bounding box with the
outside of the polygon filled with the paper colour, so the recognizer sees one
line only. Geometry stays in original-image pixels; polygons are kept on the line.
"""
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .data import Line, bbox_valid
from .io import relative, safe_path, sha256, write_json, write_jsonl

DOCKER_IMAGE = "paleographia-kraken:7.1.0-cpu"
MODEL_IN_IMAGE = "/usr/local/lib/python3.12/site-packages/kraken/blla.mlmodel"


def run_blla(image_path, settings=None, timeout=900):
    """Run ``kraken segment -bl`` on one image without network; return Kraken's JSON."""
    settings = settings or {}
    image_path = Path(image_path).resolve()
    if "," in str(image_path):
        raise ValueError("O mount Docker requer caminhos sem vírgula.")
    image = settings.get("docker_image", DOCKER_IMAGE)
    with tempfile.TemporaryDirectory(prefix="paleographia-blla-") as out:
        command = ["docker", "run", "--rm", "--network", "none", "--cpus", str(settings.get("cpus", 4)),
                   "--memory", settings.get("memory", "6g"), "--read-only",
                   "--tmpfs", "/tmp:rw,size=512m", "--env", "HOME=/tmp",
                   "--mount", f"type=bind,source={image_path},target=/in/page{image_path.suffix.lower()},readonly",
                   "--mount", f"type=bind,source={Path(out).resolve()},target=/out",
                   "--entrypoint", "kraken", settings.get("docker_image_id") or image,
                   "-i", f"/in/page{image_path.suffix.lower()}", "/out/page.json", "segment", "-bl"]
        started = time.perf_counter()
        done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
        if done.returncode != 0 or not (Path(out) / "page.json").is_file():
            raise RuntimeError("Segmentação neural falhou: " + (done.stderr or done.stdout)[-1500:])
        result = json.loads((Path(out) / "page.json").read_text(encoding="utf-8"))
    result["_seconds"] = time.perf_counter() - started
    return result


def ordered_lines(result):
    lines = [line for line in result.get("lines", []) if line.get("boundary") and line.get("baseline")]
    orders = result.get("line_orders") or []
    ids = [line.get("id") for line in lines]
    if orders and orders[0] and all(isinstance(i, int) for i in orders[0]) and sorted(orders[0]) == list(range(len(lines))):
        return [lines[i] for i in orders[0]]
    if orders and orders[0] and set(orders[0]) == set(ids):
        index = {line["id"]: line for line in lines}
        return [index[i] for i in orders[0]]
    return sorted(lines, key=lambda line: (min(p[1] for p in line["baseline"]), line["baseline"][0][0]))


def polygon_crop(image, polygon, pad=6, grow=5):
    """Crop the polygon's box; keep pixels inside the (slightly grown) polygon, paper colour outside."""
    return polygons_crop(image, [polygon], pad, grow)


def polygons_crop(image, polygons, pad=6, grow=5):
    """Same as ``polygon_crop`` for the union of several polygons (a line rejoined from pieces)."""
    xs, ys = [p[0] for poly in polygons for p in poly], [p[1] for poly in polygons for p in poly]
    box = [max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad),
           min(image.width, int(max(xs)) + pad + 1), min(image.height, int(max(ys)) + pad + 1)]
    crop = image.crop(box)
    mask = Image.new("L", crop.size, 0)
    for polygon in polygons:
        ImageDraw.Draw(mask).polygon([(x - box[0], y - box[1]) for x, y in polygon], fill=255)
    if grow:
        mask = mask.filter(ImageFilter.MaxFilter(2 * grow + 1))
    gray = crop.convert("L")
    # Paper colour: median of the brighter half of the crop.
    values = sorted(gray.getdata())
    bright = values[len(values) // 2:] or values
    level = bright[len(bright) // 2]
    rgb = [px for px, g in zip(crop.getdata(), gray.getdata()) if g >= level] or list(crop.getdata())
    paper = tuple(sorted(c[i] for c in rgb)[len(rgb) // 2] for i in range(3))
    background = Image.new("RGB", crop.size, paper)
    background.paste(crop, (0, 0), mask)
    return box, background


def segment_page_blla(page, output_dir, root, settings=None, result=None):
    """Segment one catalogued page; write masked crops and return Line records in reading order."""
    root, output_dir = Path(root), Path(output_dir)
    if output_dir.exists():
        raise ValueError("Segmentação exige saída nova; não sobrescreva revisões.")
    source = safe_path(root, page["source_image"])
    if sha256(source) != page["source_sha256"]:
        raise ValueError("Fonte alterada desde o inventário.")
    output_dir.mkdir(parents=True)
    result = result or run_blla(source, settings)
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        image.info.clear()
    if image.size != (page["width"], page["height"]):
        raise ValueError("Dimensões divergentes.")
    raw = ordered_lines(result)
    widths = sorted(max(p[0] for p in l["boundary"]) - min(p[0] for p in l["boundary"]) for l in raw) or [1]
    median_width = widths[len(widths) // 2]
    transform = hashlib.sha256(json.dumps({"method": "kraken_blla", "model": MODEL_IN_IMAGE,
                                           "crop": "polygon_box_pad6_grow5_paper_fill"}).encode()).hexdigest()
    lines, overlay = [], image.copy()
    drawing = ImageDraw.Draw(overlay)
    for order, geometry in enumerate(raw):
        polygon = [(int(x), int(y)) for x, y in geometry["boundary"]]
        box, crop = polygon_crop(image, polygon)
        if not bbox_valid(box, image.width, image.height):
            continue
        width = box[2] - box[0]
        region = "page" if width >= 0.35 * median_width else "margem"
        lid = "l_" + hashlib.sha256(f"{page['page_id']}|blla|{order}|{box}".encode()).hexdigest()[:20]
        path = output_dir / (lid + ".png")
        crop.save(path)
        line = Line(line_id=lid, page_id=page["page_id"], document_id=page["document_id"],
                    folio_id=page["folio_id"], region_id=region, reading_order=order,
                    source_image=page["source_image"], crop_image=relative(path, root), bbox_xyxy=box,
                    source_width=page["width"], source_height=page["height"], split_group=page["document_id"],
                    source_sha256=page["source_sha256"], transform_id=transform,
                    segmentation_method="kraken_blla").model_dump()
        line["blla_geometry"] = {"baseline": geometry["baseline"], "boundary": geometry["boundary"]}
        line["crop_sha256"] = sha256(path)
        lines.append(line)
        drawing.polygon(polygon, outline="#e56c39" if region == "page" else "#999999")
        drawing.text(tuple(geometry["baseline"][0]), str(order), fill="#004cff")
    overlay.save(output_dir / (page["page_id"] + "_overlay.png"))
    write_jsonl(output_dir / "lines.jsonl", lines)
    write_json(output_dir / "segmentation.json", {"method": "kraken_blla", "model": MODEL_IN_IMAGE,
               "seconds": result.get("_seconds"), "count": len(lines), "transform_id": transform})
    return lines


def side_fragments(lines, max_gap=40, min_overlap=0.5, tolerance=30):
    """Pair each short ``margem`` piece with the full line it continues on the same row.

    blla sometimes cuts the first or last word of a line into a separate short line. A piece is
    paired when at least ``min_overlap`` of its height overlaps a ``page`` line and the horizontal
    gap between them is at most ``max_gap`` pixels (small overlaps up to ``tolerance`` allowed).
    Returns {main line_id: [pieces]}; pieces away from every line (true margin notes) stay out.
    """
    mains = [line for line in lines if line["region_id"] == "page"]
    groups = {}
    for piece in lines:
        if piece["region_id"] != "margem":
            continue
        b, best = piece["bbox_xyxy"], None
        for main in mains:
            m = main["bbox_xyxy"]
            if min(b[3], m[3]) - max(b[1], m[1]) < min_overlap * (b[3] - b[1]):
                continue
            if b[2] <= m[0] + tolerance:
                gap = m[0] - b[2]
            elif b[0] >= m[2] - tolerance:
                gap = b[0] - m[2]
            else:
                continue
            if gap <= max_gap and (best is None or abs(gap) < best[0]):
                best = (abs(gap), main)
        if best:
            groups.setdefault(best[1]["line_id"], []).append(piece)
    return groups


def rejoin_line(page, main, pieces, output_dir, root):
    """Crop one line again from its blla polygon plus the polygons of its side pieces."""
    root, output_dir = Path(root), Path(output_dir)
    source = safe_path(root, page["source_image"])
    if sha256(source) != page["source_sha256"]:
        raise ValueError("Fonte alterada desde o inventário.")
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        image.info.clear()
    parts = sorted([main, *pieces], key=lambda line: line["bbox_xyxy"][0])
    polygons = [[(int(x), int(y)) for x, y in part["blla_geometry"]["boundary"]] for part in parts]
    for left, right in zip(parts, parts[1:]):
        # Bridge the gap between neighbouring pieces over the rows they share.
        a, b = left["bbox_xyxy"], right["bbox_xyxy"]
        top, bottom = max(a[1], b[1]), min(a[3], b[3])
        if bottom > top and b[0] > a[2]:
            polygons.append([(a[2] - 2, top), (b[0] + 2, top), (b[0] + 2, bottom), (a[2] - 2, bottom)])
    box, crop = polygons_crop(image, polygons)
    if not bbox_valid(box, image.width, image.height):
        raise ValueError("Recorte inválido.")
    merged = [part["line_id"] for part in parts]
    lid = "l_" + hashlib.sha256(("|".join(merged) + f"|{box}").encode()).hexdigest()[:20]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / (lid + ".png")
    crop.save(path)
    transform = hashlib.sha256(json.dumps({"method": "kraken_blla_rejoined", "model": MODEL_IN_IMAGE,
                                           "crop": "polygons_box_pad6_grow5_paper_fill"}).encode()).hexdigest()
    line = Line(line_id=lid, page_id=main["page_id"], document_id=main["document_id"], folio_id=main["folio_id"],
                region_id="page", reading_order=main["reading_order"], source_image=main["source_image"],
                crop_image=relative(path, root), bbox_xyxy=box, source_width=main["source_width"],
                source_height=main["source_height"], split_group=main["split_group"],
                source_sha256=main["source_sha256"], transform_id=transform).model_dump()
    line.update(segmentation_method="kraken_blla", crop_sha256=sha256(path), merged_from=merged,
                blla_geometry={"parts": [{"line_id": p["line_id"], **p["blla_geometry"]} for p in parts]})
    return line
