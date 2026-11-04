"""Compara hipóteses congeladas com as referências diplomáticas do piloto."""
import json
import sys
from collections import Counter
from pathlib import Path

import jiwer

from paleographia.evaluation import aggregate, counts, normalize
from paleographia.io import read_jsonl, sha256, write_json


def error_patterns(rows, unit):
    process = jiwer.process_characters if unit == "characters" else jiwer.process_words
    operations = Counter()
    for row in rows:
        aligned = process(normalize(row["reference"]), normalize(row["prediction"]))
        ref = aligned.references[0]
        hyp = aligned.hypotheses[0]
        for item in aligned.alignments[0]:
            source = ref[item.ref_start_idx:item.ref_end_idx]
            target = hyp[item.hyp_start_idx:item.hyp_end_idx]
            if item.type == "substitute":
                operations.update(("substituicao", before, after) for before, after in zip(source, target, strict=True))
            elif item.type == "delete":
                operations.update(("omissao", before, "") for before in source)
            elif item.type == "insert":
                operations.update(("insercao", "", after) for after in target)
    return [
        {"operation": op, "reference": ref, "prediction": hyp, "count": count}
        for (op, ref, hyp), count in sorted(operations.items(), key=lambda pair: (-pair[1], pair[0]))[:12]
    ]


def report_scope(rows):
    return {
        "lines": len(rows),
        "blank_predictions": sum(not normalize(row["prediction"]) for row in rows),
        "metrics": aggregate([row["metrics"] for row in rows]),
        "character_patterns": error_patterns(rows, "characters"),
        "word_patterns": error_patterns(rows, "words"),
    }


def main():
    run = Path(sys.argv[1])
    output = Path(sys.argv[2])
    pred_path = run / "predictions/predictions.json"
    ref_path = run / "evaluation_references.jsonl"
    inventory_path = run / "inventory.json"
    predictions = json.loads(pred_path.read_bytes())
    inventory = json.loads(inventory_path.read_bytes())
    refs = read_jsonl(ref_path)
    images = {row["line_id"]: row["image_sha256"] for row in inventory["records"] if row["role"] == "evaluation"}
    assert set(images) == {row["line_id"] for row in refs}
    report = {}
    for name, model in predictions["models"].items():
        found = {line["line_id"]: line for line in model["lines"]}
        if len(found) != len(refs) or set(found) != set(images):
            raise ValueError(f"Cobertura divergente para {name}.")
        rows = []
        for ref in refs:
            line = found[ref["line_id"]]
            if line["image_sha256"] != images[ref["line_id"]]:
                raise ValueError(f"Imagem divergente para {ref['line_id']}.")
            text = line["text_raw"]
            rows.append({**ref, "prediction": text, "metrics": counts(ref["reference"], text)})
        report[name] = {
            "weights_sha256": model["weights_sha256"],
            "overall": report_scope(rows),
            "documents": {
                doc: report_scope([row for row in rows if row["document_id"] == doc])
                for doc in sorted({row["document_id"] for row in rows})
            },
            "lines": rows,
        }
    tracked = [pred_path, ref_path, inventory_path]
    for name in predictions["models"]:
        for suffix in ("command.json", "train.log", "resume_command.json", "resume.log", predictions["models"][name]["weights"].split("/", 1)[1],
                       predictions["models"][name]["checkpoint"].split("/", 1)[1]):
            tracked.append(run / "models" / name / suffix)
    write_json(output, {
        "scope": inventory["scope"], "scientific_split": None,
        "normalization": "NFC + whitespace collapse; case and diacritics preserved",
        "aggregation": "Sum of edit counts per line divided by sum of reference lengths",
        "architecture": predictions["vgsl_spec"], "models": report,
        "inputs_sha256": {path.as_posix(): sha256(path) for path in tracked},
    })
    for name, result in report.items():
        print(name)
        for doc, scope in {**result["documents"], "all": result["overall"]}.items():
            c, w = (scope["metrics"][unit] for unit in ("characters", "words"))
            print(f"  {doc}  CER {c['rate']:.2%} ({c['errors']}/{c['reference_length']})"
                  f"  WER {w['rate']:.2%} ({w['errors']}/{w['reference_length']})"
                  f"  vazias {scope['blank_predictions']}")


if __name__ == "__main__":
    main()
