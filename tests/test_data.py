import copy

import pytest

from paleographia.data import associate, make_splits, validate
from paleographia.io import sha256, write_jsonl
from paleographia.segmentation import segment_pages
from conftest import reviewed


def test_explicit_mapping_shared_pdf_page_is_pending(corpus):
    root, _, pages, _ = corpus
    (root/"edition.pdf").write_bytes(b"fixture-reference-existence-only")
    second = dict(pages[0], page_id="p_second", folio_id="f100v")
    write_jsonl(root/"input.jsonl", [pages[0], second])
    mappings = [dict(page_id=p["page_id"], document_id="doc1831", folio_id=p["folio_id"],
                     correspondence_status="pending_review", transcribed_coverage=[{
                         "region_id": "edition", "bbox_xyxy": [0, 0, 600, 300],
                         "reference_source": "edition.pdf", "reference_pages": [3, 4] if i else [3]}])
                for i, p in enumerate([pages[0], second])]
    write_jsonl(root/"mapping.jsonl", mappings)
    result = associate(root/"input.jsonl", root/"mapping.jsonl", root/"mapped.jsonl", root)
    assert [r["transcribed_coverage"][0]["reference_pages"] for r in result] == [[3], [3, 4]]
    assert all(r["correspondence_status"] == "pending_review" for r in result)
    mappings[0]["correspondence_status"] = "validated"
    write_jsonl(root/"mapping.jsonl", mappings)
    with pytest.raises(ValueError, match="revisor"):
        associate(root/"input.jsonl", root/"mapping.jsonl", root/"invalid.jsonl", root)


def test_modernized_cannot_be_evaluation_reference(corpus):
    root, _, pages, rows = corpus
    rows = reviewed(rows)
    rows[0].update(reference_kind="modernized_edition", text_modernized="Ação", text_diplomatic=None)
    report = validate(rows, root, "evaluation", pages)
    assert not report["valid"]
    assert "paleográfica" in str(report["errors"])


@pytest.mark.parametrize("problem", ["duplicate", "missing", "geometry", "checksum", "reviewer", "association", "crop"])
def test_data_integrity_blocks_evaluation(corpus, problem):
    root, _, pages, rows = corpus
    rows = reviewed(rows)
    if problem == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    elif problem == "missing":
        rows[0]["source_image"] = "absent.png"
    elif problem == "geometry":
        rows[0]["bbox_xyxy"] = [10, 0, 1, 100]
    elif problem == "checksum":
        rows[0]["source_sha256"] = "0"*64
    elif problem == "reviewer":
        rows[0]["reviewer"] = " "
    elif problem == "association":
        rows[0]["folio_id"] = "wrong"
    else:
        rows[0]["crop_image"] = "absent.png"
    assert not validate(rows, root, "evaluation", pages)["valid"]


def test_leakage_by_document_source_and_derivatives(corpus):
    root, _, _, rows = corpus
    rows = reviewed(rows)
    rows[0].update(split="train", split_group="one")
    rows[1].update(split="test", split_group="two", document_id="changed", derived_from=rows[0]["line_id"])
    report = validate(rows, root, "catalog")
    assert not report["valid"] and "vazamento" in str(report["errors"])


def test_rerun_keeps_originals_and_no_text_pairing(corpus):
    root, config, pages, rows = corpus
    before = sha256(root/pages[0]["source_image"])
    other, _ = segment_pages(pages, "opencv", config, root/"data/processed/run2", root)
    assert [r["line_id"] for r in rows] == [r["line_id"] for r in other]
    assert len(rows) == 3
    assert all(r["text_diplomatic"] is None for r in rows)
    assert sha256(root/pages[0]["source_image"]) == before
    assert rows[0]["bbox_xyxy"][1] < rows[1]["bbox_xyxy"][1]
    with pytest.raises(ValueError, match="saída nova"):
        segment_pages(pages, "opencv", config, root/"data/processed/run2", root)


def test_split_refuses_artificial_groups(corpus):
    _, _, _, rows = corpus
    with pytest.raises(ValueError, match="bloqueados"):
        make_splits(rows)
    result, protocol = make_splits(rows, exploratory=True)
    assert {r["split"] for r in result} == {"exploratory"}
    assert protocol["seed"] == 1831


def test_duplicate_pages_and_cross_platform_path_traversal(corpus):
    root, _, pages, rows = corpus
    assert not validate(rows, root, "catalog", pages+pages)["valid"]
    from paleographia.io import safe_path
    for value in ("../secret", "C:/secret", "data\\..\\secret", "/secret"):
        with pytest.raises(ValueError):
            safe_path(root, value)


def test_rejected_candidate_can_share_active_reading_order(corpus):
    root, _, pages, rows = corpus
    rejected = dict(rows[0], line_id="l_rejected", review_status="rejected", exclusion_reason="Spurious detection")
    assert validate(rows+[rejected], root, "catalog", pages)["valid"]
    assert not validate(rows+[rejected], root, "evaluation", pages)["valid"]


def test_invalid_json_record_types_produce_validation_report(tmp_path):
    report = validate(["not a line"], tmp_path, "training", [{"page_id": []}, "not a page"])
    assert report["valid"] is False and len(report["errors"]) >= 4
    assert report["statuses"] == {"invalid_record": 1}
