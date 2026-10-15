import hashlib
import json
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw

from .data import Line, Page, bbox_valid
from .io import relative, safe_path, sha256, write_json, write_jsonl


def opencv_boxes(image, config):
    import cv2
    import numpy as np
    width, height = image.size
    gray = np.asarray(image.convert("L"))
    block = config.get("block_size", 31)
    if type(block) is not int or block < 3 or block % 2 == 0:
        raise ValueError("block_size deve ser ímpar e >= 3.")
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, block, config.get("threshold_c", 15))
    if config.get("detector", "contours") == "projection":
        # Reuses the legacy horizontal-profile idea without pairing peaks to text.
        margin = round(width * config.get("horizontal_margin_ratio", .06))
        left, right = margin, width-margin
        smooth = max(1, round(height*config.get("smoothing_ratio", .003)))
        profile = np.convolve(binary[:, left:right].sum(axis=1), np.ones(smooth)/smooth, mode="same")
        cutoff = np.median(profile) + config.get("peak_threshold_std", .2)*np.std(profile)
        candidates = np.where((profile[1:-1] > profile[:-2]) & (profile[1:-1] >= profile[2:]) & (profile[1:-1] > cutoff))[0]+1
        distance = max(2, round(height*config.get("min_peak_distance_ratio", .019)))
        peaks = []
        for candidate in candidates[np.argsort(profile[candidates])[::-1]]:
            if all(abs(int(candidate)-peak) >= distance for peak in peaks):
                peaks.append(int(candidate))
        peaks.sort()
        boxes = []
        for i, peak in enumerate(peaks):
            start = max(0, peak-distance//2) if i == 0 else peaks[i-1]+int(np.argmin(profile[peaks[i-1]:peak]))
            end = min(height, peak+distance//2+1) if i == len(peaks)-1 else peak+int(np.argmin(profile[peak:peaks[i+1]]))
            if end > start:
                boxes.append([left, start, right, end])
        return boxes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,
             (max(1, round(width * config.get("kernel_width_ratio", .025))), config.get("kernel_height", 3)))
    connected = cv2.dilate(binary, kernel, iterations=config.get("iterations", 1))
    contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    padding = config.get("padding", 4)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (w >= width * config.get("min_width_ratio", .12)
                and height * config.get("min_height_ratio", .002) <= h <= height * config.get("max_height_ratio", .12)):
            boxes.append([max(0, x-padding), max(0, y-padding),
                          min(width, x+w+padding), min(height, y+h+padding)])
    return sorted(boxes, key=lambda b: (b[1], b[0]))


def kraken_boxes(image, config, workdir):
    weights = Path(config["weights"]).resolve()
    if not weights.is_file():
        raise ValueError(f"Segmentação neural não executada: pesos ausentes em {weights}.")
    python = config.get("python", ".venv-kraken/Scripts/python.exe")
    if not Path(python).is_file():
        raise ValueError("Kraken requer ambiente separado; veja docs/environment.md.")
    workdir = Path(workdir)
    image.save(workdir / "neural_input.png")
    process = subprocess.run([str(Path(python).resolve()), str(Path(__file__).with_name("neural_worker.py")),
                  "--input", str(workdir / "neural_input.png"), "--output", str(workdir / "neural_result.json"),
                  "--weights", str(weights), "--device", config.get("device", "cpu")],
                 capture_output=True, text=True, timeout=600)
    if process.returncode:
        raise ValueError("Segmentação neural não executada: " + process.stderr[-3000:])
    return json.loads((workdir / "neural_result.json").read_text(encoding="utf-8"))


def crop_line(page, box, order, region_id, output_dir, root, method, transform_id):
    if not bbox_valid(box, page["width"], page["height"]):
        raise ValueError("Recorte fora dos limites.")
    identity = f"{page['page_id']}|{region_id}|{order}|{box}"
    lid = "l_" + hashlib.sha256(identity.encode()).hexdigest()[:20]
    crop_path = Path(output_dir) / (lid + ".png")
    with Image.open(safe_path(root, page["source_image"])) as image:
        cropped = image.convert("RGB").crop(box)
        cropped.info.clear()  # Browser EXIF auto-rotation must not change original pixel coordinates.
        cropped.save(crop_path)
    return Line(line_id=lid, page_id=page["page_id"], document_id=page["document_id"],
                folio_id=page["folio_id"], region_id=region_id, reading_order=order,
                source_image=page["source_image"], crop_image=relative(crop_path, root),
                bbox_xyxy=box, source_width=page["width"], source_height=page["height"],
                split_group=page["document_id"], source_sha256=page["source_sha256"],
                transform_id=transform_id, segmentation_method=method).model_dump()


def segment_pages(pages, method, config, output_dir, root=Path.cwd()):
    output_dir, root = Path(output_dir), Path(root)
    if output_dir.exists():
        raise ValueError("Segmentação exige saída nova; não sobrescreva revisões.")
    output_dir.mkdir(parents=True)
    lines, timings, failures = [], [], []
    for raw in pages:
        page = Page.model_validate(raw).model_dump()
        source = safe_path(root, page["source_image"])
        if sha256(source) != page["source_sha256"]:
            raise ValueError("Fonte alterada desde o inventário.")
        with Image.open(source) as opened:
            image = opened.convert("RGB")
            image.info.clear()
        if image.size != (page["width"], page["height"]):
            raise ValueError("Dimensões divergentes.")
        overlay = image.copy()
        drawing = ImageDraw.Draw(overlay)
        regions = page.get("transcribed_coverage") or [{"region_id": "page", "bbox_xyxy": [0, 0, *image.size]}]
        for region in regions:
            box = region["bbox_xyxy"]
            if not bbox_valid(box, *image.size):
                raise ValueError("Geometria da região inválida.")
            region_id = region["region_id"]
            start = time.perf_counter()
            details = {}
            if method == "opencv":
                boxes = opencv_boxes(image.crop(box), config.get("segmentation", {}))
            elif method == "kraken":
                work = output_dir / ("worker_" + hashlib.sha256(f"{page['page_id']}|{region_id}".encode()).hexdigest()[:12])
                work.mkdir()
                details = kraken_boxes(image.crop(box), config["neural"], work)
                boxes = details["boxes"]
            else:
                raise ValueError("Método desconhecido.")
            seconds = time.perf_counter() - start
            transform = hashlib.sha256(json.dumps({"method": method, "config": config, "region": box}, sort_keys=True).encode()).hexdigest()
            for order, b in enumerate(boxes):
                absolute = [b[0]+box[0], b[1]+box[1], b[2]+box[0], b[3]+box[1]]
                line = crop_line(page, absolute, order, region_id, output_dir, root, method, transform)
                if details:
                    line["neural_weights_sha256"] = details["weights_sha256"]
                    line["neural_geometry"] = details["lines"][order]
                lines.append(line)
                drawing.rectangle(absolute, outline="#e56c39", width=max(1, image.width//500))
                drawing.text((absolute[0], absolute[1]), str(order), fill="#004cff")
            timings.append({"page_id": page["page_id"], "region_id": region_id,
                            "segmentation_seconds": seconds, "details": details.get("runtime"),
                            "initial_load_seconds": details.get("load_seconds", 0)})
        overlay.save(output_dir / (page["page_id"] + "_overlay.png"))
    write_jsonl(output_dir / "lines.jsonl", lines)
    write_json(output_dir / "segmentation.json", {"method": method, "timings": timings,
               "failures": failures, "config": config, "count": len(lines)})
    return lines, timings
