import hashlib
import importlib.util
import io
import json
import os
import shutil
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from paleographia.api import create_app
from paleographia.data import validate
from paleographia.io import (deterministic_json_bytes, read_jsonl, same_json_content,
                            sha256, verify_digest, write_jsonl, write_snapshot)
from paleographia.preparation import ensure_archive_reference, prepare_sample
from paleographia.services import Conflict, ReviewService


def test_snapshot_bytes_are_deterministic_under_both_line_endings(tmp_path, monkeypatch):
    value = {"z": "ação", "a": [1, None]}
    expected = b'{\n  "a": [\n    1,\n    null\n  ],\n  "z": "a\xc3\xa7\xc3\xa3o"\n}\n'
    assert deterministic_json_bytes(value) == expected
    for ending in ["\r\n", "\n"]:
        monkeypatch.setattr(os, "linesep", ending)
        path = write_snapshot(tmp_path, dict(reversed(list(value.items()))))
        assert path.read_bytes() == expected
        assert path.name == "snapshot_" + hashlib.sha256(expected).hexdigest() + ".json"
    assert verify_digest(path, hashlib.sha256(expected).hexdigest())
    crlf = expected.replace(b"\n", b"\r\n")
    assert same_json_content(crlf, expected)
    assert hashlib.sha256(crlf).digest() != hashlib.sha256(expected).digest()
    path.write_bytes(b"corrupted synthetic fixture")
    with pytest.raises(ValueError, match="não foi sobrescrito"):
        write_snapshot(tmp_path, value)
    assert path.read_bytes() == b"corrupted synthetic fixture"
    with pytest.raises(ValueError):
        deterministic_json_bytes({"invalid": float("nan")})


@pytest.mark.skipif(not shutil.which("git"), reason="Git is required for blob verification")
def test_eight_published_legacy_snapshots_remain_byte_identical():
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location("traslado_history", root / "scripts/traslado_history.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.verify_history(root, root / module.DIRECTORY / "integridade.json")
    assert report["valid"] and len(report["snapshots"]) == 8
    assert all(r["published_verified"] and r["semantic_match"] for r in report["snapshots"])


@pytest.fixture
def sample(tmp_path):
    image = Image.new("RGB", (100, 100))
    image.putdata([(x, y, (x+y) % 256) for y in range(100) for x in range(100)])
    image.save(tmp_path / "source.png")
    reference = tmp_path / "reference.pdf"
    reference.write_bytes(b"Synthetic reference, not historical text or HTR evidence.")
    spec = {"source_image": "source.png", "source_sha256": sha256(tmp_path / "source.png"),
            "width": 100, "height": 100, "page_id": "p_synthetic", "document_id": "one_document",
            "region_id": "first5", "source_url": "https://example.invalid/source",
            "comparison_source": "comparison.json", "planned_reviewer": "Planned only",
            "dates": {"described_act": "1656-12-14", "copy_heading_year": 1767},
            "edition": {"path": "reference.pdf", "archive_member": {"sha256": sha256(reference)},
                        "credits": "Synthetic edition"},
            "boxes": [[0, i*15, 100, i*15+20] for i in range(5)],
            "region_bbox_xyxy": [0, 0, 100, 100], "geometry_notes": "Pending synthetic geometry",
            "transform_id": "test_only", "pages_path": "catalog/pages.jsonl",
            "lines_path": "catalog/lines.jsonl", "image_directory": "images/lines",
            "context_image": "images/context.png", "overlay_image": "images/overlay.png"}
    comparison = {"body_lines": [{"published_text": f"Published synthetic {n}"} for n in range(5)],
                  "human_observations": [{"id": "partial", "comparison_lines": [2, 3],
                                          "original_message": "Partial only", "scope": "A word"}]}
    return tmp_path, spec, comparison


def test_preparation_crops_pixels_preserves_sources_and_refuses_review_overwrite(sample):
    root, spec, comparison = sample
    assert prepare_sample(*sample)["lines"] == 5
    pages, lines = read_jsonl(root / spec["pages_path"]), read_jsonl(root / spec["lines_path"])
    before = (root / spec["lines_path"]).read_bytes()
    with Image.open(root / spec["source_image"]) as source:
        for index, line in enumerate(lines):
            assert line["reading_order"] == index and line["split_group"] == spec["document_id"]
            assert line["text_diplomatic"] is None and line["text_modernized"] is None
            assert line["reference_kind"] == "unknown" and line["split"] is None
            assert line["review_status"] == line["geometry_status"] == "pending_review"
            with Image.open(root / line["crop_image"]) as crop:
                assert crop.tobytes() == source.crop(line["bbox_xyxy"]).tobytes()
    assert lines[1]["published_reference"]["human_observations"] == comparison["human_observations"]
    assert not pages[0]["transcribed_coverage"][0]["complete"]
    assert validate(lines, root, "catalog", pages)["valid"]
    assert not validate(lines, root, "evaluation", pages)["valid"]
    assert prepare_sample(*sample)["preserved_existing_catalog"]
    assert (root / spec["lines_path"]).read_bytes() == before
    lines[0]["text_diplomatic"] = "Human draft; preserve"
    write_jsonl(root / spec["lines_path"], lines)
    changed = (root / spec["lines_path"]).read_bytes()
    with pytest.raises(ValueError, match="não foi sobrescrito"):
        prepare_sample(*sample)
    assert (root / spec["lines_path"]).read_bytes() == changed


def test_reference_recovery_verifies_archived_member_and_never_overwrites(tmp_path):
    archive = tmp_path / "data/raw/reference.zip"
    archive.parent.mkdir(parents=True)
    content = b"Synthetic archived edition"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("folder/edition.pdf", content)
    entry = {"archive": archive.name, "archive_sha256": sha256(archive),
             "original_name": "folder/edition.pdf", "sha256": hashlib.sha256(content).hexdigest()}
    ensure_archive_reference(tmp_path, entry, "recovered/edition.pdf")
    assert (tmp_path / "recovered/edition.pdf").read_bytes() == content
    (tmp_path / "recovered/edition.pdf").write_bytes(b"Different source")
    with pytest.raises(ValueError, match="não foi sobrescrita"):
        ensure_archive_reference(tmp_path, entry, "recovered/edition.pdf")
    assert (tmp_path / "recovered/edition.pdf").read_bytes() == b"Different source"


def test_evaluation_stays_blocked_when_only_region_coverage_is_pending(sample):
    from paleographia.evaluation import evaluate
    root, spec, comparison = sample
    prepare_sample(*sample)
    pages, lines = read_jsonl(root / spec["pages_path"]), read_jsonl(root / spec["lines_path"])
    pages[0].update(correspondence_status="validated", reviewer="Synthetic reviewer",
                    reviewed_at="2026-10-16T12:00:00+00:00")
    for line in lines:
        line.update(text_diplomatic="Synthetic human fixture", reference_kind="human_diplomatic",
                    review_status="validated", geometry_status="validated",
                    reviewer="Synthetic reviewer", reviewed_at="2026-10-16T12:00:00+00:00")
    assert validate(lines, root, "evaluation", pages)["valid"]
    with pytest.raises(ValueError, match="Cobertura completa"):
        evaluate(lines, [], root / "blocked_evaluation", root, pages)
    assert not (root / "blocked_evaluation/metrics.json").exists()


def test_separate_workspace_api_and_export_preserve_published_metadata(sample):
    root, spec, comparison = sample
    prepare_sample(*sample)
    pages, lines = read_jsonl(root / spec["pages_path"]), read_jsonl(root / spec["lines_path"])
    original_config = {"paths": {"workspace": "workspace1831"}}
    original = ReviewService(root, original_config)
    original.import_catalog(pages, lines)
    original_pointer = (original.workspace / "current.json").read_bytes()
    config = {"paths": {"workspace": "workspace_traslado"},
              "presentation": {"automatic_transcription_enabled": False}}
    app = create_app(root, config)
    app.state.service.import_catalog(pages, lines)
    with pytest.raises(Conflict):
        app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        catalog = client.get("/api/catalog").json()
        assert len(catalog["lines"]) == 5
        assert client.get(f"/lines/{pages[0]['page_id']}/{lines[0]['line_id']}.png").status_code == 200
        assert client.get(f"/api/pages/{pages[0]['page_id']}/image").status_code == 200
        response = client.patch('/api/lines/' + lines[0]['line_id'], json={
            "changes": {"text_diplomatic": "Human draft"}, "revision": catalog["revision"]})
        assert response.status_code == 200
        assert response.json()["published_reference"] == lines[0]["published_reference"]
        assert response.json()["review_status"] == "pending_review"
        exported = zipfile.ZipFile(io.BytesIO(client.get('/api/export').content))
        saved = [json.loads(row) for row in exported.read('lines.jsonl').splitlines()]
        assert saved[0]["published_reference"] == lines[0]["published_reference"]
        assert not validate(saved, root, "evaluation", pages)["valid"]
    assert (original.workspace / "current.json").read_bytes() == original_pointer


def test_real_sample_crops_match_versioned_original_without_needing_local_pdf():
    root = Path(__file__).parents[1]
    lines = read_jsonl(root / "data/manifests/traslado_269r/lines.jsonl")
    assert len(lines) == 5 and len({r["split_group"] for r in lines}) == 1
    with Image.open(root / lines[0]["source_image"]) as source:
        for line in lines:
            with Image.open(root / line["crop_image"]) as crop:
                assert crop.tobytes() == source.convert("RGB").crop(line["bbox_xyxy"]).tobytes()
