"""CPU line recognizer for the pinned RapidAI conversion of Paddle's Latin model.

Preprocessing/CTC contract follows RapidAI/RapidOCR at
7cfd3d9ef786a2e538ca30df700325e72e85b5f5 (Apache-2.0),
python/rapidocr/ch_ppocr_rec/{main,utils}.py. No detection or text correction.
"""
import hashlib
import math
import time
from pathlib import Path

import cv2
import numpy as np

from .io import now, sha256

MODEL_SHA256 = "b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a"
MODEL_URL = "https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv5/rec/latin_PP-OCRv5_rec_mobile.onnx"
REGISTRY_REVISION = "7cfd3d9ef786a2e538ca30df700325e72e85b5f5"
MODEL_ID = "PaddlePaddle/latin_PP-OCRv5_mobile_rec"


def prepare_pixels(image):
    """Single RGB PIL crop -> BGR, height 48, width >=320, linear resize, [-1,1]."""
    bgr = np.asarray(image.convert("RGB"))[:, :, ::-1]
    height, width = bgr.shape[:2]
    target_width = int(48 * max(320 / 48, width / height))
    resized_width = min(math.ceil(48 * width / height), target_width)
    resized = cv2.resize(bgr, (resized_width, 48), interpolation=cv2.INTER_LINEAR)
    normalized = (resized.astype(np.float32).transpose(2, 0, 1) / 255 - .5) / .5
    pixels = np.zeros((1, 3, 48, target_width), dtype=np.float32)
    pixels[0, :, :, :resized_width] = normalized
    return pixels


def decode_ctc(scores, characters):
    """Greedy CTC: collapse consecutive tokens, then remove blank (index zero)."""
    scores = np.asarray(scores)
    if scores.ndim != 3 or scores.shape[0] != 1 or scores.shape[2] != len(characters):
        raise ValueError("Saída ONNX incompatível com o dicionário CTC.")
    if not np.isfinite(scores).all():
        raise ValueError("Saída ONNX contém valores não finitos.")
    tokens = scores[0].argmax(axis=1)
    selected = np.ones(len(tokens), dtype=bool)
    selected[1:] = tokens[1:] != tokens[:-1]
    selected &= tokens != 0
    return "".join(characters[i] for i in tokens[selected]), tokens.tolist()


class LatinONNXRecognizer:
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.session = None
        self.identity = None
        self.error = None
        self.load_seconds = 0.0

    def status(self):
        return {"state": "loaded" if self.session else "unavailable" if self.error else "not_loaded",
                "configured_model": MODEL_ID, "loaded_model": self.identity,
                "device": "cpu", "precision": "float32", "load_seconds": self.load_seconds,
                "error": self.error}

    def load(self):
        if self.session is not None:
            return
        start = time.perf_counter()
        try:
            if sha256(self.model_path) != MODEL_SHA256:
                raise ValueError("Hash dos pesos ONNX divergente.")
            import onnxruntime as ort
            options = ort.SessionOptions()
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1
            options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            session = ort.InferenceSession(str(self.model_path), sess_options=options,
                                           providers=["CPUExecutionProvider"])
            metadata = session.get_modelmeta().custom_metadata_map
            dictionary = metadata["character"]
            self.characters = ["blank", *dictionary.splitlines(), " "]
            if session.get_outputs()[0].shape[-1] != len(self.characters):
                raise ValueError("Dicionário embutido diverge da saída ONNX.")
            self.input_name = session.get_inputs()[0].name
            self.identity = {"id": MODEL_ID, "conversion": "RapidAI/RapidOCR ONNX",
                             "registry_revision": REGISTRY_REVISION, "url": MODEL_URL,
                             "sha256": MODEL_SHA256, "dictionary_sha256": hashlib.sha256(dictionary.encode()).hexdigest(),
                             "dictionary_classes_with_blank_space": len(self.characters), "fallback": False,
                             "onnxruntime": ort.__version__, "providers": session.get_providers(),
                             "threads": 1, "execution_mode": "ORT_SEQUENTIAL"}
            self.session = session
        except Exception as exc:
            self.error = str(exc)
            raise
        finally:
            self.load_seconds = time.perf_counter() - start

    def recognize(self, image):
        self.load()
        start = time.perf_counter()
        pixels = prepare_pixels(image)
        scores = self.session.run(None, {self.input_name: pixels})[0]
        text, tokens = decode_ctc(scores, self.characters)
        return {"text_raw": text, "token_ids": tokens, "model": self.identity,
                "device": "cpu", "precision": "float32", "possible_truncation": False,
                "generation_limit_reached": False, "decoding": "greedy_ctc_blank_0",
                "preprocessing": {"color": "BGR", "height": 48, "min_width": 320,
                                  "resize": "cv2.INTER_LINEAR; preserve aspect ratio; right zero padding",
                                  "normalization": "(pixel/255 - 0.5)/0.5", "input_shape": list(pixels.shape)},
                "recognition_seconds": time.perf_counter()-start, "created_at": now()}
