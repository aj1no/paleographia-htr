import os
import subprocess
import sys

from paleographia.recognition import checkpoint_files, ModelUnavailable
from paleographia.training import training_run
import pytest


def test_imports_never_import_torch_or_download():
    script = "import paleographia.api, paleographia.training, paleographia.segmentation; import sys; assert 'torch' not in sys.modules; assert 'transformers' not in sys.modules"
    subprocess.run([sys.executable, "-c", script], check=True, env=dict(os.environ, HF_HUB_OFFLINE="1"))


def test_empty_checkpoint_not_a_trained_model(tmp_path):
    with pytest.raises(ModelUnavailable, match="incompleto"):
        checkpoint_files(tmp_path)


def test_dry_run_blocks_unreviewed_data_without_loading_model(corpus):
    root, config, pages, lines = corpus
    result = training_run(lines, pages, config, root/"training", root)
    assert result["status"] == "not_executed"
    assert not result["validation"]["valid"]


def test_cli_failed_validation_has_nonzero_exit(corpus):
    root, _, pages, rows = corpus
    from paleographia.io import write_jsonl
    write_jsonl(root/"lines.jsonl", rows)
    process = subprocess.run([sys.executable, "-m", "paleographia", "validate", "--manifest", str(root/"lines.jsonl"),
                "--pages", str(root/"pages.jsonl"), "--purpose", "evaluation", "--report", str(root/"report.json")], cwd=root, capture_output=True)
    assert process.returncode == 2 and (root/"report.json").is_file()
