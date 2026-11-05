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
    xs, ys = [p[0] for p in polygon], [p[1] for p in polygon]
    box = [max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad),
           min(image.width, int(max(xs)) + pad + 1), min(image.height, int(max(ys)) + pad + 1)]
    crop = image.crop(box)
    mask = Image.new("L", crop.size, 0)
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
