import importlib.util
from pathlib import Path

import pytest


def test_missing_crop_can_be_rebuilt_without_overwriting(corpus):
    root, _, pages, rows = corpus
    module_path = Path(__file__).parents[1]/"scripts/materialize_pilot.py"
    spec = importlib.util.spec_from_file_location("materialize_pilot", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    crop = root/rows[0]["crop_image"]
    original = crop.read_bytes()
    crop.unlink()  # Disposable synthetic test fixture only.
    assert module.materialize(pages, rows, root)["created"] == 1
    assert crop.read_bytes() == original
    crop.write_bytes(b"invalid fixture")
    with pytest.raises(OSError):
        module.materialize(pages, rows, root)
    assert crop.read_bytes() == b"invalid fixture"
