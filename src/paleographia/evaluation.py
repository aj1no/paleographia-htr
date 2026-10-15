import unicodedata
from collections import defaultdict
from pathlib import Path

import jiwer

from .data import require_valid
from .io import write_json, write_jsonl


def normalize(text):
    """NFC + whitespace only, applied equally; preserve case and diacritics."""
    return " ".join(unicodedata.normalize("NFC", text).split())


def counts(reference, prediction):
    ref, pred = normalize(reference), normalize(prediction)
    results = {}
    for name, result in (("characters", jiwer.process_characters(ref, pred)),
                         ("words", jiwer.process_words(ref, pred))):
        size = result.hits + result.substitutions + result.deletions
        errors = result.substitutions + result.deletions + result.insertions
        results[name] = {"substitutions": result.substitutions, "deletions": result.deletions,
                         "insertions": result.insertions, "hits": result.hits,
                         "reference_length": size, "errors": errors,
                         "rate": errors / size if size else None}
    return results


def aggregate(results):
    combined = {}
    for name in ("characters", "words"):
        totals = {key: sum(r[name][key] for r in results) for key in
                  ("substitutions", "deletions", "insertions", "hits", "reference_length", "errors")}
        totals["rate"] = totals["errors"] / totals["reference_length"] if totals["reference_length"] else None
        combined[name] = totals
    return combined


def overlap(a, b):
    intersection = max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))
    aa, ab = (a[2]-a[0])*(a[3]-a[1]), (b[2]-b[0])*(b[3]-b[1])
    return intersection / (aa+ab-intersection) if aa+ab-intersection else 0, intersection / min(aa, ab) if min(aa, ab) else 0


def segmentation_metrics(reference, predicted, threshold=.5, overlap_threshold=.2):
    candidates, ref_edges, pred_edges = [], defaultdict(list), defaultdict(list)
    for i, ref in enumerate(reference):
        for j, pred in enumerate(predicted):
            iou, coverage = overlap(ref["bbox_xyxy"], pred["bbox_xyxy"])
            if iou >= threshold:
                candidates.append((iou, i, j))
            if coverage >= overlap_threshold:
                ref_edges[i].append(j)
                pred_edges[j].append(i)
    used_r, used_p, matches = set(), set(), []
    # Deterministic descending-IoU greedy matching; frozen before test use.
    for iou, i, j in sorted(candidates, key=lambda x: (-x[0], x[1], x[2])):
        if i not in used_r and j not in used_p:
            used_r.add(i)
            used_p.add(j)
            matches.append({"reference_id": reference[i]["line_id"], "prediction_id": predicted[j]["line_id"], "iou": iou})
    return {"reference_lines": len(reference), "detected_lines": len(predicted), "correct": len(matches),
            "unmatched_reference": len(reference)-len(matches), "unmatched_detected": len(predicted)-len(matches),
            "omitted": sum(not ref_edges[i] for i in range(len(reference))),
            "spurious": sum(not pred_edges[j] for j in range(len(predicted))),
            "split_reference_lines": sum(len(v)>1 for v in ref_edges.values()),
            "merged_detected_lines": sum(len(v)>1 for v in pred_edges.values()),
            "matches": matches, "iou_threshold": threshold, "overlap_threshold": overlap_threshold,
            "matching": "descending_iou_greedy_one_to_one", "geometry": "axis_aligned_bbox_xyxy"}


def evaluate(reference, predictions, output_dir, root=Path.cwd(), pages=None, threshold=.5, overlap_threshold=.2):
    require_valid(reference, root, "evaluation", pages)
    if Path(output_dir).exists():
        raise ValueError("Avaliação exige saída nova.")
    by_region, pred_region = defaultdict(list), defaultdict(list)
    for row in reference:
        by_region[(row["page_id"], row["region_id"])].append(row)
    seen = set()
    for row in predictions:
        if row["line_id"] in seen:
            raise ValueError("Predição com ID duplicado.")
        seen.add(row["line_id"])
        if not isinstance(row.get("text_raw"), str) or row.get("status") not in {"ok", "failed"}:
            raise ValueError("Predição exige text_raw e status ok/failed explícitos.")
        pred_region[(row["page_id"], row["region_id"])].append(row)
    details, line_details, geometries, exclusions = [], [], [], []
    for key, refs in sorted(by_region.items()):
        refs.sort(key=lambda r: r["reading_order"])
        preds = sorted(pred_region.get(key, []), key=lambda r: r["reading_order"])
        # Scope needs a known complete reference; otherwise omissions/spurious lines are unknowable.
        if pages is not None:
            page = next(p for p in pages if p["page_id"] == key[0])
            coverage = next((c for c in page["transcribed_coverage"] if c["region_id"] == key[1]), None)
            if not coverage or coverage.get("review_status") != "validated" or coverage.get("complete") is not True:
                raise ValueError(f"Cobertura completa da região {key} não foi revisada.")
            from .data import bbox_valid, check_reviewer
            check_reviewer(coverage)
            if not bbox_valid(coverage["bbox_xyxy"], page["width"], page["height"]):
                raise ValueError("Cobertura inválida.")
            bounds = coverage["bbox_xyxy"]
            for row in [*refs, *preds]:
                box = row.get("bbox_xyxy")
                if not bbox_valid(box, page["width"], page["height"]) or not (bounds[0] <= box[0] < box[2] <= bounds[2] and bounds[1] <= box[1] < box[3] <= bounds[3]):
                    raise ValueError("Linha fora da cobertura revisada.")
        expected_sha = refs[0]["source_sha256"]
        if any(p.get("source_sha256") != expected_sha for p in preds):
            raise ValueError("Predição e referência provêm de fontes diferentes.")
        from .data import bbox_valid
        if any(not bbox_valid(p.get("bbox_xyxy"), refs[0]["source_width"], refs[0]["source_height"]) for p in preds):
            raise ValueError("Predição sem geometria.")
        ref_text = " ".join(r["text_diplomatic"] for r in refs)
        pred_text = " ".join(p["text_raw"] if p["status"] == "ok" else "" for p in preds)
        metrics = counts(ref_text, pred_text)
        details.append({"page_id": key[0], "region_id": key[1], "reference": ref_text,
                        "prediction": pred_text, "metrics": metrics,
                        "processing_failures": sum(p["status"] != "ok" for p in preds)})
        geometry = segmentation_metrics(refs, preds, threshold, overlap_threshold)
        geometry.update(page_id=key[0], region_id=key[1])
        geometries.append(geometry)
        prediction_map = {p["line_id"]: p for p in preds}
        matches = {m["reference_id"]: prediction_map[m["prediction_id"]] for m in geometry["matches"]}
        for ref in refs:
            pred = matches.get(ref["line_id"])
            text = pred["text_raw"] if pred and pred["status"] == "ok" else ""
            line_details.append({"line_id": ref["line_id"], "prediction_id": pred["line_id"] if pred else None,
                                 "reference": ref["text_diplomatic"], "prediction": text,
                                 "metrics": counts(ref["text_diplomatic"], text)})
    for key, rows in pred_region.items():
        if key not in by_region:
            exclusions.append({"region": key, "count": len(rows), "reason": "outside_reference_coverage"})
    summary = {"normalization": "Unicode NFC + whitespace collapse; preserve case/diacritics",
               "aggregation_unit": "ordered_complete_region; micro counts",
               "metrics": aggregate([d["metrics"] for d in details]),
               "regions": len(details), "reference_lines": len(reference), "predicted_lines": len(predictions),
               "segmentation": geometries, "out_of_scope": exclusions,
               "limitations": ["BBox approximation for neural polygons", "Line metrics omit unpaired spurious lines; primary region metric counts their insertions."]}
    write_json(Path(output_dir)/"metrics.json", summary)
    write_jsonl(Path(output_dir)/"regions.jsonl", details)
    write_jsonl(Path(output_dir)/"lines.jsonl", line_details)
    return summary
