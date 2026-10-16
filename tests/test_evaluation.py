import pytest

from paleographia.evaluation import aggregate, counts, evaluate, segmentation_metrics
from conftest import reviewed


def test_counts_and_no_clipping():
    assert counts("abc", "axc")["characters"]["substitutions"] == 1
    assert counts("abc", "ac")["characters"]["deletions"] == 1
    assert counts("a", "aaaa")["characters"]["rate"] == 3
    assert counts("a b", "")["words"]["deletions"] == 2
    assert counts("", "a")["characters"]["insertions"] == 1
    assert counts("", "a")["characters"]["rate"] is None
    assert counts("ação", "acao")["characters"]["errors"] == 2
    assert counts("á", "a\u0301")["characters"]["rate"] == 0
    result = aggregate([counts("abc", "axc"), counts("a", "")])
    assert result["characters"]["rate"] == .5


def test_omitted_and_spurious_lines_penalize_region(corpus):
    root, _, pages, rows = corpus
    refs = reviewed(rows)
    for ref in refs:
        ref["text_diplomatic"] = "a"
    preds = [dict(r, text_raw="a", status="ok") for r in refs[:1]]
    result = evaluate(refs, preds, root/"missing", root)
    assert result["metrics"]["words"]["deletions"] == 2
    assert result["segmentation"][0]["omitted"] == 2
    extra = dict(preds[0], line_id="spurious", reading_order=10, bbox_xyxy=[0, 0, 10, 10], text_raw="a a a a")
    result = evaluate(refs, preds+[extra], root/"extra", root)
    assert result["metrics"]["words"]["insertions"] == 2


def test_failed_prediction_is_empty_not_excluded(corpus):
    root, _, _, rows = corpus
    refs = reviewed(rows)
    predictions = [dict(r, text_raw="fabricated error text", status="failed") for r in refs]
    result = evaluate(refs, predictions, root/"failed", root)
    assert result["metrics"]["characters"]["rate"] == 1


def test_partial_coverage_requires_human_confirmation(corpus):
    root, _, pages, rows = corpus
    with pytest.raises(ValueError, match="Cobertura"):
        evaluate(reviewed(rows), [], root/"partial", root, pages)


def test_splits_and_merges_have_explicit_geometry():
    ref = [{"line_id": "r", "bbox_xyxy": [0, 0, 100, 20]}]
    preds = [{"line_id": "a", "bbox_xyxy": [0, 0, 45, 20]}, {"line_id": "b", "bbox_xyxy": [55, 0, 100, 20]}]
    assert segmentation_metrics(ref, preds)["split_reference_lines"] == 1
    assert segmentation_metrics(preds, ref)["merged_detected_lines"] == 1
