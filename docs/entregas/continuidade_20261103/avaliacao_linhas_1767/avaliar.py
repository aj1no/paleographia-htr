"""Conferir entradas congeladas e comparar os dois reconhecedores por linha."""
import argparse
import json
from pathlib import Path

from paleographia.data import require_valid
from paleographia.evaluation import aggregate, counts
from paleographia.io import read_jsonl, safe_path, sha256, write_json, write_jsonl


BUNDLE = Path(__file__).resolve().parent
PREDICTION_FIELDS = (
    "line_id", "page_id", "region_id", "reading_order", "bbox_xyxy", "crop_image", "source_sha256",
)


def load_inputs(root):
    protocol = json.loads((BUNDLE / "protocolo.json").read_bytes())
    for path, expected in protocol["input_sha256"].items():
        if sha256(safe_path(root, path)) != expected:
            raise ValueError(f"Entrada congelada alterada: {path}")
    references = read_jsonl(BUNDLE / "referencias.jsonl")
    inputs = read_jsonl(BUNDLE / "recortes.jsonl")
    excluded = read_jsonl(BUNDLE / "exclusoes.jsonl")
    pages = read_jsonl(BUNDLE / "paginas.jsonl")
    require_valid(references, root, "evaluation", pages)
    require_valid(inputs, root, "catalog", pages)
    coverage = pages[0]["transcribed_coverage"][0]
    selected_ids = [r["line_id"] for r in references]
    excluded_ids = [row["line_id"] for row in excluded]
    if selected_ids != protocol["included_line_ids"] or excluded_ids != coverage["excluded_reference_line_ids"]:
        raise ValueError("Seleção ou exclusões divergentes.")
    if coverage["complete"] or set(selected_ids + excluded_ids) != set(coverage["covered_line_ids"]):
        raise ValueError("A cobertura precisa registrar a região parcial e todas as linhas.")
    for reference, entry in zip(references, inputs, strict=True):
        if any(reference[key] != entry[key] for key in PREDICTION_FIELDS):
            raise ValueError(f"Entrada de reconhecimento divergente: {reference['line_id']}")
        if entry["text_diplomatic"] is not None or entry["text_modernized"] is not None:
            raise ValueError("Manifesto de reconhecimento contém texto de referência.")
    return protocol, references, excluded


def score(model, prediction_path, references, expected):
    predictions = read_jsonl(prediction_path)
    run_path = prediction_path.with_suffix(".run.json")
    run = json.loads(run_path.read_bytes())
    loaded = run["recognizer"]["loaded_model"]
    if any(loaded.get(key) != value for key, value in expected["loaded_model"].items()):
        raise ValueError(f"Identidade do modelo divergente: {model}")
    if [p["line_id"] for p in predictions] != [r["line_id"] for r in references]:
        raise ValueError(f"IDs ou ordem das previsões divergentes: {model}")

    details = []
    for reference, prediction in zip(references, predictions, strict=True):
        if any(reference[key] != prediction.get(key) for key in PREDICTION_FIELDS):
            raise ValueError(f"Previsão com recorte divergente: {model} / {reference['line_id']}")
        status = prediction.get("status")
        raw = prediction.get("text_raw")
        if status not in {"ok", "failed"} or not isinstance(raw, str):
            raise ValueError(f"Previsão sem texto bruto ou estado válido: {model} / {reference['line_id']}")
        details.append({
            "model": model, "line": reference["reading_order"] + 1, "line_id": reference["line_id"],
            "reference": reference["text_diplomatic"], "prediction_raw": raw, "status": status,
            "metrics": counts(reference["text_diplomatic"], raw if status == "ok" else ""),
        })
    failures = sum(row["status"] == "failed" for row in details)
    if run["count"] != len(details) or run["failures"] != failures:
        raise ValueError(f"Recibo da execução divergente: {model}")
    return details, {
        "metrics": aggregate([row["metrics"] for row in details]), "failures": failures,
        "predictions_sha256": sha256(prediction_path), "run_sha256": sha256(run_path),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ppocrv5", type=Path)
    parser.add_argument("--ppocrv6", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    supplied = (args.ppocrv5, args.ppocrv6, args.output_dir)
    if any(supplied) and not all(supplied):
        parser.error("Informe as duas previsões e o diretório de saída juntos.")
    protocol, references, excluded = load_inputs(Path.cwd())
    if args.output_dir is None:
        print(f"Entradas conferidas: {len(references)} referências e {len(excluded)} exclusões.")
        return

    summary = {
        "scope": protocol["scope"], "normalization": protocol["normalization"],
        "aggregation_unit": "line_micro_counts", "included_lines": [r["reading_order"] + 1 for r in references],
        "excluded_lines": [r["line"] for r in excluded], "models": {},
    }
    details = []
    for model, path in (("ppocrv5", args.ppocrv5), ("ppocrv6", args.ppocrv6)):
        rows, result = score(model, path, references, protocol["models"][model])
        details.extend(rows)
        summary["models"][model] = result
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_json(args.output_dir / "comparacao.json", summary)
    write_jsonl(args.output_dir / "por_linha.jsonl", details)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
