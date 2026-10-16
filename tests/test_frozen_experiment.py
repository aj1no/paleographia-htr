import json
import shutil
from pathlib import Path

import pytest

from paleographia.frozen_experiment import artifact_for_hash, audit_bundle, check_control, restore_support
from paleographia.io import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = Path("docs/experimentos/traslado_269r_20261016")


@pytest.fixture
def published_checkout(tmp_path):
    # Only versioned inputs: no local workspace, extracted PDF, weights or network.
    inventory = json.loads((ROOT/BUNDLE/"inventory.json").read_bytes())
    for row in inventory["files"] + [{"path": (BUNDLE/"inventory.json").as_posix()}]:
        target = tmp_path/row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        source = artifact_for_hash(ROOT, row) if "sha256" in row else ROOT/row["path"]
        shutil.copyfile(source, target)
    return tmp_path, tmp_path/BUNDLE, inventory


def test_published_artifacts_reproduce_both_metrics_in_fresh_checkout(published_checkout):
    root, bundle, _ = published_checkout
    restore_support(root, bundle)
    result = audit_bundle(root, bundle, root/"audit")
    assert result["dataset_role"] == "development" and result["lines"] == 5
    baseline = result["results"]["baseline_trocr"]
    latin = result["results"]["latin_ppocrv5"]
    assert (baseline["characters"]["errors"], baseline["characters"]["reference_length"]) == (195, 242)
    assert (baseline["words"]["errors"], baseline["words"]["reference_length"]) == (45, 45)
    assert (latin["characters"]["errors"], latin["characters"]["reference_length"]) == (138, 242)
    assert (latin["words"]["errors"], latin["words"]["reference_length"]) == (43, 45)
    with pytest.raises(ValueError, match="saída nova"):
        audit_bundle(root, bundle, root/"audit")


def test_corrupt_prediction_stops_before_creating_results(published_checkout):
    root, bundle, _ = published_checkout
    path = bundle/"baseline_trocr/predictions.jsonl"
    path.write_bytes(path.read_bytes()+b"\n")
    with pytest.raises(ValueError, match="Hash divergente"):
        audit_bundle(root, bundle, root/"audit")
    assert not (root/"audit").exists()


def test_recovery_never_overwrites_divergent_edition(published_checkout):
    root, bundle, inventory = published_checkout
    path = root/inventory["restore_support"][0]["original"]
    path.parent.mkdir(parents=True)
    path.write_bytes(b"user changed reference")
    with pytest.raises(ValueError, match="não foi sobrescrita"):
        restore_support(root, bundle)
    assert path.read_bytes() == b"user changed reference"


def test_control_rejects_reordered_or_recropped_predictions():
    lines = read_jsonl(ROOT/BUNDLE/"reference/linhas_exploratorias.jsonl")
    predictions = read_jsonl(ROOT/BUNDLE/"latin_ppocrv5/predictions.jsonl")
    with pytest.raises(ValueError, match="controle congelado"):
        check_control(lines, list(reversed(predictions)))
    predictions[0]["bbox_xyxy"][1] += 1
    with pytest.raises(ValueError, match="controle congelado"):
        check_control(lines, predictions)
