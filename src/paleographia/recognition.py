import json
from pathlib import Path

from PIL import Image

from .io import now, safe_path, sha256, write_json, write_jsonl


class ModelUnavailable(RuntimeError):
    pass


def checkpoint_files(path):
    path = Path(path)
    if not (path / "config.json").is_file() or not (path / "preprocessor_config.json").is_file():
        raise ModelUnavailable("Checkpoint incompleto: config.json/preprocessor_config.json ausentes.")
    if not any((path / name).is_file() for name in ("tokenizer.json", "sentencepiece.bpe.model", "spiece.model", "vocab.json")):
        raise ModelUnavailable("Checkpoint incompleto: tokenizador ausente.")
    if not any((path / name).is_file() for name in ("model.safetensors", "pytorch_model.bin", "model.safetensors.index.json", "pytorch_model.bin.index.json")):
        raise ModelUnavailable("Checkpoint incompleto: pesos ausentes.")
    # Shard references must exist, too. from_pretrained validates model architecture.
    for name in ("model.safetensors.index.json", "pytorch_model.bin.index.json"):
        if (path / name).is_file():
            for shard in set(json.loads((path/name).read_text())["weight_map"].values()):
                if not (path / shard).is_file():
                    raise ModelUnavailable(f"Shard ausente: {shard}")
    return {p.name: sha256(p) for p in sorted(path.iterdir()) if p.is_file()}


class TrOCRRecognizer:
    """Migration shim: legacy entry points cannot load or execute TrOCR."""
    load_seconds = 0.0

    def __init__(self, config):
        self.config = config

    def status(self):
        from .backends import LEGACY_MESSAGE
        return {"state": "disabled", "backend": "disabled", "loaded_model": None,
                "load_seconds": 0.0, "error": LEGACY_MESSAGE}

    def load(self):
        from .backends import LEGACY_MESSAGE
        raise ModelUnavailable(LEGACY_MESSAGE)

    def recognize(self, image):
        self.load()


def prepare_weights(config, output):
    from .backends import prepare_backend_weights
    return prepare_backend_weights(config, output)


def recognize_lines(lines, recognizer, output, root=Path.cwd()):
    if Path(output).exists():
        raise ValueError("Predições são imutáveis; escolha nova saída.")
    predictions = []
    from .io import run_id
    execution_id = run_id()
    # Loading failure is explicit, not a successful empty transcription run.
    recognizer.load()
    for line in lines:
        base = {k: line[k] for k in ("line_id", "page_id", "region_id", "reading_order", "bbox_xyxy")}
        base.update({"crop_image": line["crop_image"], "source_sha256": line["source_sha256"]})
        base["execution_id"] = execution_id
        try:
            with Image.open(safe_path(root, line["crop_image"])) as image:
                base.update(recognizer.recognize(image))
            base["status"] = "ok"
        except Exception as exc:
            base.update(status="failed", error=str(exc), text_raw="")
        predictions.append(base)
    write_jsonl(output, predictions)
    write_json(Path(output).with_suffix(".run.json"), {"recognizer": recognizer.status(), "count": len(lines),
                "failures": sum(p["status"] != "ok" for p in predictions)})
    return predictions
