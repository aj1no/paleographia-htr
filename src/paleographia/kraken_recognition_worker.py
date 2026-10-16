"""Kraken 7.1 JSON-lines worker. Receives only crop PNGs, never references.

Uses native ImageInputTransforms and CTCRecognitionInferenceMixin._rec_predict
on already extracted lines. No segmentation/polygon extraction or line detection.
This private CTC entry point is deliberately pinned to Kraken 7.1.
"""
import argparse
import base64
import contextlib
import hashlib
import importlib.metadata
import io
import json
import platform
import sys
import time
from pathlib import Path


def emit(value):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        started = time.perf_counter()
        digest = hashlib.sha256(Path(args.weights).read_bytes()).hexdigest()
        if digest != args.sha256:
            raise ValueError("Hash dos pesos do worker divergente.")
        if importlib.metadata.version("kraken") not in {"7.1", "7.1.0"}:
            raise ValueError("Worker requer Kraken 7.1.")
        with contextlib.redirect_stdout(sys.stderr):
            import torch
            from PIL import Image
            from kraken.tasks import RecognitionTaskModel
            from kraken.configs import RecognitionInferenceConfig
            from kraken.lib.dataset import ImageInputTransforms
            torch.set_num_threads(2)
            torch.set_num_interop_threads(1)
            torch.manual_seed(1831)
            torch.use_deterministic_algorithms(True)
            model = RecognitionTaskModel.load_model(args.weights)
            net = model.net
            if net.__class__.__name__ != "PPOCRv6Model" or net.variant != "medium":
                raise ValueError("Pesos não são PP-OCRv6 medium.")
            config = RecognitionInferenceConfig(accelerator="cpu", device=1, precision="32-true",
                                                batch_size=1, num_line_workers=0, padding=16,
                                                bidi_reordering=False)
            net.prepare_for_inference(config)
            batch, channels, height, width = net.input
            # Zenodo v1 metadata says height=96 although its card describes 128.
            # Follow the actual checkpoint's native preprocessing, before any output.
            if (channels, height, width) != (3, 96, 0):
                raise ValueError("Entrada do modelo diverge dos metadados RGB/96/largura variável.")
            transforms = ImageInputTransforms(batch, height, width, channels, (16, 0),
                                               False, dtype=net._m_dtype)
        identity = {"id": "zenodo:21788410/medium.safetensors", "sha256": digest,
                    "backend": "kraken_ppocrv6", "architecture": type(net).__name__,
                    "variant": net.variant, "model_input": list(net.input), "seg_type": net.seg_type,
                    "runtime": {p: importlib.metadata.version(p) for p in
                                ("kraken", "torch", "torchvision", "numpy", "Pillow", "safetensors", "lightning")},
                    "python": platform.python_version(), "platform": platform.platform(), "fallback": False}
        emit({"ready": True, "identity": identity, "load_seconds": time.perf_counter()-started})
    except Exception as exc:
        emit({"ready": False, "error": f"{type(exc).__name__}: {exc}"})
        return 1
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line)
            request_id = request["request_id"]
            started = time.perf_counter()
            raw = base64.b64decode(request["image_png"], validate=True)
            with Image.open(io.BytesIO(raw)) as opened:
                image = opened.convert("RGB")
            pixel_sha = hashlib.sha256(image.tobytes()).hexdigest()
            if pixel_sha != request["pixel_sha256"]:
                raise ValueError("Pixels da entrada divergentes no transporte.")
            with contextlib.redirect_stdout(sys.stderr), torch.inference_mode():
                tensor = transforms(image).unsqueeze(0)
                lens = torch.LongTensor([tensor.shape[-1]])
                decoded, lengths = net._rec_predict(tensor, lens)
                text = "".join(item[0] for item in decoded[0])
                tokens = net.outputs[0, :, :int(lengths[0])].argmax(dim=0).tolist()
            emit({"request_id": request_id, "ok": True, "text_raw": text, "token_ids": tokens,
                  "recognition_seconds": time.perf_counter()-started,
                  "preprocessing": {"input_size": list(image.size), "pixel_sha256": pixel_sha,
                                    "tensor_shape": list(tensor.shape), "line_height": height,
                                    "horizontal_padding": 16, "valid_norm": False,
                                    "line_detection": False, "polygon_extraction": False,
                                    "transform": "Kraken 7.1 ImageInputTransforms (baseline line convention)"}})
        except Exception as exc:
            emit({"request_id": request_id, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
