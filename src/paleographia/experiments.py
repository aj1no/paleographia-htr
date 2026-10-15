import importlib.metadata
import json
import platform
import subprocess
import time
from pathlib import Path

from .data import validate
from .evaluation import evaluate
from .io import now, sha256, write_json
from .recognition import TrOCRRecognizer, recognize_lines
from .segmentation import segment_pages


def provenance(config, manifests=()):
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    except (subprocess.CalledProcessError, OSError):
        commit, dirty = None, None
    versions = {}
    for name in ("paleographia", "Pillow", "numpy", "opencv-python-headless", "torch", "transformers", "jiwer", "fastapi"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"created_at": now(), "config": config, "commit": commit, "working_tree_dirty": dirty,
            "python": platform.python_version(), "platform": platform.platform(), "versions": versions,
            "manifests": {str(p): sha256(p) for p in manifests if Path(p).is_file()}}


def compare(pages, reference, config, output_dir, root=Path.cwd(), manifest_paths=()):
    output = Path(output_dir)
    if output.exists():
        raise ValueError("Comparação exige diretório novo.")
    output.mkdir(parents=True)
    write_json(output/"provenance.json", provenance(config, manifest_paths))
    # Integrity/partition checks need the complete catalogue: filtering first
    # hides leakage. Pending rows outside the selection are not evaluation targets.
    global_report = validate(reference, root, "catalog", pages)
    selected_split = config["experiment"].get("split", "exploratory")
    selected = [r for r in reference if isinstance(r, dict) and r.get("split") == selected_split]
    selected_report = validate(selected, root, "evaluation", pages)
    report = {"valid": global_report["valid"] and selected_report["valid"],
              "global": global_report, "selected": selected_report,
              "errors": (["Catálogo completo: " + e for e in global_report["errors"]]
                         + ["Seleção: " + e for e in selected_report["errors"]])}
    if not selected:
        report["errors"].append("Nenhuma linha no conjunto selecionado: " + selected_split)
    write_json(output/"validation.json", report)
    results = {"status": "not_executed", "split": selected_split,
               "methods": {}, "reference_lines": len(selected),
               "groups": len({r.get("split_group") for r in selected}),
               "exclusions": [{"line_id": r.get("line_id") if isinstance(r, dict) else None,
                               "reason": (r.get("exclusion_reason") if isinstance(r, dict) else None) or "different_or_unassigned_split"}
                              for r in reference if r not in selected]}
    if not report["valid"]:
        results["reason"] = "Referências/splits não aptos; " + "; ".join(report["errors"])
        results["methods"] = {m: {"status": "not_executed", "reason": results["reason"]} for m in ("opencv", "kraken", "human_crops")}
        write_json(output/"comparison.json", results)
        return results
    region_keys = {(r["page_id"], r["region_id"]) for r in selected}
    selected_pages = [dict(p, transcribed_coverage=[c for c in p["transcribed_coverage"] if (p["page_id"], c["region_id"]) in region_keys])
                      for p in pages if any(r["page_id"] == p["page_id"] for r in selected)]
    if any(not p["transcribed_coverage"] for p in selected_pages):
        results["reason"] = "Coberturas explícitas ausentes; defina-as antes de executar."
        write_json(output/"comparison.json", results)
        return results
    recognizer = TrOCRRecognizer(config)
    for method in ("opencv", "kraken", "human_crops"):
        start = time.perf_counter()
        try:
            timings = []
            if method == "human_crops":
                detected = selected
            else:
                detected, timings = segment_pages(selected_pages, method, config, output/method/"segmentation", root)
            load_before = recognizer.load_seconds
            predictions = recognize_lines(detected, recognizer, output/method/"predictions.jsonl", root)
            summary = evaluate(selected, predictions, output/method/"evaluation", root, selected_pages,
                               config["experiment"].get("iou_threshold", .5), config["experiment"].get("overlap_threshold", .2))
            elapsed = time.perf_counter()-start
            results["methods"][method] = {"status": "executed", "metrics": summary["metrics"], "total_seconds": elapsed,
                    "recognizer_initial_load_seconds": recognizer.load_seconds if load_before == 0 else 0,
                    "recognition_seconds": sum(p.get("recognition_seconds", 0) for p in predictions),
                    "segmentation_timings": timings, "failures": sum(p["status"] != "ok" for p in predictions)}
        except Exception as exc:
            results["methods"][method] = {"status": "not_executed", "reason": str(exc), "elapsed_seconds": time.perf_counter()-start}
    results["recognizer"] = recognizer.status()
    successful = [m for m, r in results["methods"].items() if r["status"] == "executed"]
    results["status"] = "executed" if len(successful) == 3 else "partial" if successful else "not_executed"
    if all(m in successful for m in ("opencv", "kraken")):
        samples = {}
        for method in ("opencv", "kraken"):
            from .io import read_jsonl
            for row in read_jsonl(output/method/"evaluation/regions.jsonl"):
                key = row["page_id"]+"/"+row["region_id"]
                samples.setdefault(key, {})[method] = row
        wins = []
        for key, methods in samples.items():
            a, b = methods["opencv"]["metrics"]["characters"]["errors"], methods["kraken"]["metrics"]["characters"]["errors"]
            wins.append({"region": key, "winner": "tie" if a == b else "opencv" if a < b else "kraken", "details": methods})
        write_json(output/"error_comparison.json", wins)
    write_json(output/"comparison.json", results)
    return results
