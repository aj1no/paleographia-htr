"""Explicit backend selection. No legacy fallback, downloads, or loading at import."""
from pathlib import Path

from .recognition import ModelUnavailable

LEGACY_MESSAGE = "TrOCR desativado neste projeto. Migre recognition.backend para kraken_ppocrv6; a revisão manual continua disponível."


class DisabledRecognizer:
    load_seconds = 0.0

    def __init__(self, reason=LEGACY_MESSAGE, state="disabled"):
        self.reason, self.state = reason, state

    def status(self):
        return {"state": self.state, "backend": "disabled", "load_seconds": 0.0,
                "loaded_model": None, "error": self.reason}

    def load(self):
        raise ModelUnavailable(self.reason)

    def recognize(self, image):
        self.load()

    def close(self):
        pass


def create_recognizer(config, root=None):
    settings = config.get("recognition", {})
    backend = settings.get("backend", "disabled")
    model = str(settings.get("model", "")).replace("\\", "/").lower()
    if "trocr" in model or backend in {"trocr", "disabled"}:
        return DisabledRecognizer()
    if backend == "kraken_ppocrv6":
        from .kraken_recognition import KrakenRecognizer
        return KrakenRecognizer(settings, Path(root or Path.cwd()))
    return DisabledRecognizer(f"Backend desconhecido: {backend}. Configure kraken_ppocrv6 ou disabled.", "unavailable")


def prepare_backend_weights(config, output):
    backend = config.get("recognition", {}).get("backend")
    recognizer = create_recognizer(config)
    if backend != "kraken_ppocrv6" or isinstance(recognizer, DisabledRecognizer):
        recognizer.load()
        raise ModelUnavailable(LEGACY_MESSAGE)
    from .kraken_recognition import download_weights
    return download_weights(output)
