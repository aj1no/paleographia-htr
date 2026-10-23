import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from conftest import reviewed
from paleographia.io import read_jsonl, sha256, write_json
from paleographia.ppocrv6_training import docker_command, run, select_data


def smoke_fixture(corpus):
    from PIL import Image
    root, config, pages, rows = corpus
    rows = [dict(r, partition="development") for r in reviewed(rows)]
    # Synthetic glyphs are only seven pixels high; add real source context so
    # the crop meets the fixed 96/2560 native input limits used in this test.
    for row in rows:
        row["bbox_xyxy"][1] -= 10
        row["bbox_xyxy"][3] += 10
        with Image.open(root / row["source_image"]) as im:
            im.convert("RGB").crop(row["bbox_xyxy"]).save(root / row["crop_image"])
    settings = {"engine": "ketos", "mode": "technical_smoke", "epochs": 1, "batch_size": 1,
                "train_line_ids": [rows[0]["line_id"]], "validation_line_ids": [rows[1]["line_id"]]}
    return root, config, pages, rows, settings


def test_smoke_requires_reviewed_development_and_disjoint_explicit_ids(corpus):
    root, _, pages, rows, settings = smoke_fixture(corpus)
    selected, protocol, report = select_data(rows, pages, settings, root)
    assert report["valid"] and not protocol["scientific_evaluation"] and not protocol["test_used"]
    for change in ({"review_status": "pending_review"}, {"geometry_status": "pending_review"},
                   {"partition": "curation"}, {"split": "test"}):
        altered = copy.deepcopy(rows)
        altered[0].update(change)
        with pytest.raises(ValueError):
            select_data(altered, pages, settings, root)
    with pytest.raises(ValueError, match="IDs explícitos"):
        select_data(rows, pages, dict(settings, validation_line_ids=settings["train_line_ids"]), root)


def test_scientific_protocol_does_not_allow_pending_independence(corpus):
    root, _, pages, rows, _ = smoke_fixture(corpus)
    write_json(root / "partitions.json", {"groups": [{"document_id": "doc1831", "independence_status": "pending_review"}]})
    with pytest.raises(ValueError, match="independência"):
        select_data(rows, pages, {"mode": "scientific", "partition_protocol": "partitions.json"}, root)


def test_exposed_development_cannot_be_scientific_test(corpus):
    root, _, pages, rows, _ = smoke_fixture(corpus)
    write_json(root / "partitions.json", {"groups": [{"document_id": "doc1831", "independence_status": "validated",
               "scientific_split": "test", "reviewer": "test reviewer", "reviewed_at": "2026-10-23T12:00:00+00:00"}]})
    with pytest.raises(ValueError, match="previamente exposto"):
        select_data([dict(r, split="test") for r in rows], pages,
                    {"mode": "scientific", "partition_protocol": "partitions.json"}, root)


def test_docker_is_offline_and_base_worker_data_are_readonly(tmp_path):
    command = docker_command("sha256:fixed", *[tmp_path / n for n in ("base", "worker", "data", "out")], "check")
    assert command[command.index("--network") + 1] == "none"
    assert command[command.index("--pull") + 1] == "never"
    mounts = [s for s in command if s.startswith("type=bind")]
    assert len(mounts) == 4 and all(",readonly" in s for s in mounts[:3])
    assert ",readonly" not in mounts[3] and "TORCHDYNAMO_DISABLE=1" in command


def test_dry_run_exports_only_selected_development_and_never_runs_training(corpus, monkeypatch):
    root, config, pages, rows, settings = smoke_fixture(corpus)
    model = root / "base.safetensors"
    model.write_bytes(b"SYNTHETIC WEIGHTS; NEVER LOADED")
    image_id = "sha256:" + "1" * 64
    config.update(recognition={"backend": "kraken_ppocrv6", "model": model.name, "sha256": sha256(model),
                               "docker_image_id": image_id, "device": "cpu", "precision": "float32"}, training=settings)
    calls = []
    def fake_process(command, **kw):
        calls.append(command)
        assert command[:3] != ["docker", "run", "--rm"]
        return SimpleNamespace(stdout=image_id + "\n", returncode=0)
    monkeypatch.setattr("paleographia.ppocrv6_training.subprocess.run", fake_process)
    # Unselected pending text is never inspected to build targets or parameters.
    rows.append(dict(rows[2], line_id="reserved", partition="reserved", split="test", text_diplomatic=object()))
    result = run(rows, pages, config, root / "dry", root)
    assert result["status"] == "ready_dry_run" and not result["test_used"]
    assert not (root / "dry/data/test").exists()
    assert len(list((root / "dry/data").rglob("*.gt.txt"))) == 2
    assert all("reserved" not in p.read_text(encoding="utf8") for p in (root / "dry/data").glob("*.lst"))
    assert not (root / "dry/checkpoints").exists()
    assert sha256(model) == config["recognition"]["sha256"]


def test_failures_are_not_reported_as_execution(corpus):
    root, config, pages, rows, settings = smoke_fixture(corpus)
    result = run(rows, pages, config, root / "failed", root, execute=True)
    assert result["status"] == "failed" and result["reason"]
    assert json.loads((root / "failed/training.json").read_bytes())["status"] == "failed"
