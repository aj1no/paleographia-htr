import hashlib
import json
import logging
import threading
import time
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
    def __init__(self, config):
        self.config = config
        self.model = self.processor = None
        self.lock = threading.RLock()
        self.load_seconds = 0.0
        self.error = None
        self.identity = None

    def status(self):
        return {"state": "loaded" if self.model is not None else "unavailable" if self.error else "not_loaded",
                "configured_model": self.config["recognition"]["model"],
                "loaded_model": self.identity, "device": getattr(self, "device", None),
                "precision": self.config["recognition"].get("precision", "float32"),
                "load_seconds": self.load_seconds, "error": self.error}

    def load(self):
        with self.lock:
            if self.model is not None:
                return
            start = time.perf_counter()
            try:
                import torch
                from transformers import TrOCRProcessor, VisionEncoderDecoderModel
                settings = self.config["recognition"]
                identifier = settings["model"]
                revision = settings.get("revision", "main")
                local = Path(identifier)
                is_local = local.is_dir() or identifier.startswith((".", "/", "models/")) or ":" in identifier
                files = checkpoint_files(local) if is_local else None
                options = {"local_files_only": settings.get("local_files_only", True)}
                if not is_local:
                    options["revision"] = revision
                self.device = settings.get("device", "cpu")
                if self.device == "auto":
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                precision = settings.get("precision", "float32")
                if precision not in {"float32", "float16", "bfloat16"}:
                    raise ValueError("Precisão inválida.")
                if self.device == "cpu" and precision != "float32":
                    raise ValueError("CPU usa float32 neste piloto.")
                self.dtype = getattr(torch, precision)
                torch.manual_seed(self.config.get("experiment", {}).get("seed", 1831))
                processor = TrOCRProcessor.from_pretrained(identifier, use_fast=False, **options)
                model, loading_info = VisionEncoderDecoderModel.from_pretrained(identifier, dtype=self.dtype, output_loading_info=True, **options)
                model.to(self.device).eval()
                self.identity = {"id": identifier, "requested_revision": revision,
                                 "resolved_revision": getattr(model.config, "_commit_hash", None),
                                 "local_files_sha256": files, "fallback": False,
                                 "loading_info": loading_info}
                if is_local and (local/"provenance.json").is_file():
                    self.identity["preparation"] = json.loads((local/"provenance.json").read_text(encoding="utf-8"))
                    self.identity["resolved_revision"] = self.identity["preparation"].get("resolved_snapshot")
                self.processor, self.model = processor, model
                self.error = None
                logging.getLogger(__name__).info("TrOCR carregado: %s", self.identity)
            except Exception as exc:
                self.error = f"Modelo indisponível: {exc}. Instale .[htr] e execute prepare-weights explicitamente."
                raise ModelUnavailable(self.error) from exc
            finally:
                self.load_seconds = time.perf_counter() - start

    def recognize(self, image):
        """Contract accepts one line crop, never a full manuscript page."""
        with self.lock:
            self.load()
            import torch
            generation = self.config.get("generation", {})
            if generation.get("do_sample", False):
                raise ValueError("Piloto comparativo exige decodificação determinística (do_sample=false).")
            start = time.perf_counter()
            pixels = self.processor(images=image.convert("RGB"), return_tensors="pt").pixel_values.to(self.device, dtype=self.dtype)
            if self.device.startswith("cuda"):
                torch.cuda.synchronize()
            with torch.inference_mode():
                tokens = self.model.generate(pixels, **generation)
            if self.device.startswith("cuda"):
                torch.cuda.synchronize()
            generated = tokens[0].tolist()
            text = self.processor.batch_decode(tokens, skip_special_tokens=True)[0]
            eos = self.model.generation_config.eos_token_id
            eos_ids = eos if isinstance(eos, list) else [eos]
            limit_hit = len(generated)-1 >= generation.get("max_new_tokens", 128)
            return {"text_raw": text, "token_ids": generated,
                    "possible_truncation": limit_hit and generated[-1] not in eos_ids,
                    "generation_limit_reached": limit_hit, "model": self.identity,
                    "device": self.device, "precision": self.config["recognition"].get("precision", "float32"),
                    "generation": generation, "recognition_seconds": time.perf_counter()-start,
                    "seed": self.config.get("experiment", {}).get("seed", 1831),
                    "created_at": now()}


def prepare_weights(config, output):
    """Explicit network operation; save the resolved snapshot, processor and weights together."""
    settings = config["recognition"]
    destination = Path(output)
    if destination.exists():
        raise ValueError("Pesos exigem diretório novo.")
    from huggingface_hub import HfApi, snapshot_download
    from .io import run_id
    resolved = HfApi().model_info(settings["model"], revision=settings.get("revision", "main")).sha
    staging = destination.with_name(destination.name+".preparing-"+run_id())
    # local_dir uses real files and does not need Windows symlink privileges.
    snapshot_download(settings["model"], revision=resolved, local_dir=str(staging),
             allow_patterns=["*.json", "*.safetensors", "pytorch_model*.bin", "*.model", "vocab.*", "merges.txt", "*.txt"])
    files = checkpoint_files(staging)
    write_json(staging / "provenance.json", {"model": settings["model"], "revision": settings.get("revision"),
               "resolved_snapshot": resolved, "files": files, "prepared_at": now()})
    staging.rename(destination)
    return {"path": str(destination), "snapshot": resolved}


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
