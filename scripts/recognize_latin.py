"""Explicit download, or local inference on frozen line crops; no detector."""
import argparse
import urllib.request
from pathlib import Path

from paleographia.io import read_jsonl, sha256, write_json
from paleographia.latin_ocr import LatinONNXRecognizer, MODEL_SHA256, MODEL_URL
from paleographia.recognition import recognize_lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="models/latin_PP-OCRv5_mobile_rec/model.onnx")
    parser.add_argument("--download", action="store_true", help="Explicit network access; checks pinned SHA256")
    parser.add_argument("--lines")
    parser.add_argument("--output")
    args = parser.parse_args()
    model = Path(args.model)
    if args.download:
        if model.exists():
            if sha256(model) != MODEL_SHA256:
                raise ValueError("Modelo existente divergente; não foi sobrescrito.")
        else:
            import hashlib
            content = urllib.request.urlopen(MODEL_URL, timeout=120).read()
            if hashlib.sha256(content).hexdigest() != MODEL_SHA256:
                raise ValueError("Download divergente; nada foi gravado.")
            model.parent.mkdir(parents=True, exist_ok=True)
            with model.open("xb") as stream:
                stream.write(content)
        print(f"Pesos verificados: {MODEL_SHA256}")
    if bool(args.lines) != bool(args.output):
        parser.error("Informe --lines e --output juntos.")
    if args.lines:
        from paleographia.experiments import provenance
        predictions = recognize_lines(read_jsonl(args.lines), LatinONNXRecognizer(model), args.output)
        write_json(Path(args.output).with_suffix(".provenance.json"), provenance({}, [args.lines]))
        print({"lines": len(predictions), "failures": sum(p["status"] != "ok" for p in predictions)})


if __name__ == "__main__":
    main()
