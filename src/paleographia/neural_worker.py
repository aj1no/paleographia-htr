"""Kraken 6.0.0 worker; run with its separate Python 3.11/3.12 environment.

This file deliberately uses no imports from paleographia (NumPy constraints differ).
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if importlib.metadata.version("kraken") != "6.0.0":
        raise ValueError("Adaptador requer Kraken 6.0.0.")
    from PIL import Image
    import torch
    from kraken import blla
    from kraken.lib.vgsl import TorchVGSLModel
    start = time.perf_counter()
    model = TorchVGSLModel.load_model(args.weights)
    if model.model_type != "segmentation":
        raise ValueError("Pesos devem ser de segmentação, não reconhecimento.")
    load_seconds = time.perf_counter() - start
    with Image.open(args.input) as opened:
        image = opened.convert("RGB")
    start = time.perf_counter()
    with torch.inference_mode():
        result = blla.segment(image, model=model, device=args.device, raise_on_error=True)
    lines, boxes = [], []
    for line in result.lines:
        if not line.boundary:
            raise ValueError("Linha neural sem polígono; não inventar recorte.")
        xs, ys = zip(*line.boundary)
        box = [max(0, math.floor(min(xs))), max(0, math.floor(min(ys))),
               min(image.width, math.ceil(max(xs))), min(image.height, math.ceil(max(ys)))]
        if box[0] >= box[2] or box[1] >= box[3]:
            raise ValueError("Polígono neural degenerado.")
        boxes.append(box)
        lines.append({"boundary": line.boundary, "baseline": line.baseline})
    output = {"boxes": boxes, "lines": lines, "load_seconds": load_seconds,
              "inference_seconds": time.perf_counter()-start,
              "weights_sha256": hashlib.sha256(Path(args.weights).read_bytes()).hexdigest(),
              "runtime": {p: importlib.metadata.version(p) for p in ("kraken", "torch", "numpy", "Pillow")}}
    Path(args.output).write_text(json.dumps(output), encoding="utf-8")


if __name__ == "__main__":
    main()
