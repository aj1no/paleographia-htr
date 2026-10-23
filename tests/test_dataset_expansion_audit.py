"""Actual saved optimization evidence; no model or Docker is run by these tests."""
import json
import shutil
from pathlib import Path

import pytest

from paleographia.io import sha256, write_json
from scripts.audit_dataset_expansion import audit

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = Path("docs/dataset_expansion_20261023")


@pytest.fixture
def published(tmp_path):
    inventory = json.loads((ROOT / BUNDLE / "inventory.json").read_bytes())
    for row in inventory["files"] + [{"path": (BUNDLE / "inventory.json").as_posix()}]:
        target = tmp_path / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / row["path"], target)
    return tmp_path, tmp_path / BUNDLE


def change_and_rehash(root, bundle, path, content):
    write_json(path, content)
    inventory = json.loads((bundle / "inventory.json").read_bytes())
    for row in inventory["files"]:
        if row["path"] == path.relative_to(root).as_posix():
            row["sha256"] = sha256(path)
    write_json(bundle / "inventory.json", inventory)


def test_real_saved_training_evidence_is_auditable_without_weights(published):
    root, bundle = published
    result = audit(root, bundle)
    assert result["valid"] and result["optimizer_steps"] == 2
    assert result["changed_trainable_tensors"] == 318 and result["reloaded_for_inference"]
    assert not result["scientific_experiment_completed"] and not result["test_used"]


def test_serialization_hash_change_cannot_substitute_for_tensor_change(published):
    root, bundle = published
    path = bundle / "training_ppocrv6_smoke/changed_tensors.json"
    changes = json.loads(path.read_bytes())
    changes[0]["before_sha256"] = changes[0]["after_sha256"]
    change_and_rehash(root, bundle, path, changes)
    with pytest.raises(ValueError, match="Mudanças reais"):
        audit(root, bundle)


def test_zero_optimizer_steps_cannot_be_reported_as_training(published):
    root, bundle = published
    path = bundle / "training_ppocrv6_smoke/worker_result.json"
    proof = json.loads(path.read_bytes())
    proof["optimizer_steps"] = 0
    change_and_rehash(root, bundle, path, proof)
    with pytest.raises(ValueError, match="Evidência incompleta"):
        audit(root, bundle)
