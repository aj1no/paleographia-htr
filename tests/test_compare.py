"""Synthetic control-flow checks, never HTR accuracy evidence."""
import copy
import json

import pytest
from PIL import Image

from conftest import reviewed
from paleographia import experiments
from paleographia.__main__ import main
from paleographia.io import sha256, write_jsonl


def independent_catalog(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    first = reviewed([lines[0]])[0]
    first["split"] = "test"
    second_page = copy.deepcopy(pages[0])
    second_source = root/"data/raw/independente.png"
    with Image.open(root/pages[0]["source_image"]) as image:
        image.putpixel((599, 299), (0, 0, 0))
        image.save(second_source)
    second_page.update(page_id="p_independent", document_id="doc_other", folio_id="f_other",
                       source_image=second_source.relative_to(root).as_posix(), source_sha256=sha256(second_source),
                       correspondence_status="pending_review", reviewer=None, reviewed_at=None)
    second = dict(lines[0], line_id="l_independent", split="train", split_group="doc_other",
                  **{k: second_page[k] for k in ("page_id", "document_id", "folio_id", "source_image", "source_sha256")})
    pages.append(second_page)
    pages[0]["transcribed_coverage"] = [{"region_id": first["region_id"], "bbox_xyxy": [0, 0, 600, 300],
        "complete": True, "review_status": "validated", "reviewer": "Revisor de teste",
        "reviewed_at": "2026-10-15T12:00:00+00:00"}]
    config["experiment"]["split"] = "test"
    return root, config, pages, [first, second]


def forbidden(*args, **kwargs):
    pytest.fail("Partição inválida não pode inicializar modelos nem executar métodos.")


@pytest.mark.parametrize("leak", ["document", "group", "folio", "source", "derived", "siblings"])
def test_compare_blocks_global_leakage_before_any_model(corpus, monkeypatch, leak):
    root, config, pages, rows = independent_catalog(corpus)
    if leak in {"document", "folio"}:
        key = leak + "_id"
        pages[1][key] = rows[1][key] = pages[0][key]
    elif leak == "group":
        rows[1]["split_group"] = rows[0]["split_group"]
    elif leak == "source":
        for key in ("source_image", "source_sha256"):
            pages[1][key] = rows[1][key] = pages[0][key]
    elif leak == "derived":
        rows[1]["derived_from"] = rows[0]["line_id"]
    else:
        rows[0]["derived_from"] = rows[1]["derived_from"] = "l_parent"
    for name in ("segment_pages", "create_recognizer", "recognize_lines"):
        monkeypatch.setattr(experiments, name, forbidden)
    output = root/"comparison"
    result = experiments.compare(pages, rows, config, output, root)
    report = json.loads((output/"validation.json").read_text(encoding="utf-8"))
    assert result["status"] == "not_executed"
    assert all(m["status"] == "not_executed" for m in result["methods"].values())
    assert not report["valid"] and not report["global"]["valid"]
    assert report["selected"]["valid"]  # The selection alone hides the conflict.
    assert "vazamento" in result["reason"]


def install_test_only_methods(monkeypatch, reference):
    calls = []

    class TestOnlyRecognizer:
        """TEST ONLY. No weights, downloads or real manuscript interpretation."""
        load_seconds = 0

        def __init__(self, config, root=None):
            calls.append("initialize_test_only")

        def load(self):
            calls.append("load_test_only")

        def recognize(self, image):
            return {"text_raw": "SAÍDA SINTÉTICA DE TESTE", "model": {"id": "test-only"}}

        def status(self):
            return {"state": "test_only", "load_seconds": 0}

    def test_only_segment(pages, method, config, output, root):
        calls.append(method)
        return [r for r in reference if r["split"] == config["experiment"]["split"]], []

    monkeypatch.setattr(experiments, "create_recognizer", TestOnlyRecognizer)
    monkeypatch.setattr(experiments, "segment_pages", test_only_segment)
    return calls


@pytest.mark.parametrize("exploratory", [False, True])
def test_compare_valid_selection_runs_with_pending_rows_outside(corpus, monkeypatch, exploratory):
    root, config, pages, rows = independent_catalog(corpus)
    if exploratory:
        pages, rows = pages[:1], rows[:1]
        config["experiment"]["split"] = rows[0]["split"] = "exploratory"
    calls = install_test_only_methods(monkeypatch, rows)
    output = root/"comparison"
    result = experiments.compare(pages, rows, config, output, root)
    report = json.loads((output/"validation.json").read_text(encoding="utf-8"))
    assert report["valid"] and report["global"]["valid"] and report["selected"]["valid"]
    assert result["status"] == "executed"
    assert {"opencv", "kraken"}.issubset(calls)
    assert result["reference_lines"] == result["groups"] == 1
    assert result["recognizer"]["state"] == "test_only"
    assert (output/"error_comparison.json").is_file()


def test_compare_empty_selection_and_cli_failure(corpus, monkeypatch, capsys):
    root, config, pages, rows = independent_catalog(corpus)
    config["experiment"]["split"] = "validation"
    for name in ("segment_pages", "create_recognizer", "recognize_lines"):
        monkeypatch.setattr(experiments, name, forbidden)
    result = experiments.compare(pages, rows, config, root/"empty", root)
    assert result["status"] == "not_executed" and "Nenhuma linha" in result["reason"]
    config["experiment"]["split"] = "test"
    rows[1]["split_group"] = rows[0]["split_group"]
    write_jsonl(root/"pages.jsonl", pages)
    write_jsonl(root/"lines.jsonl", rows)
    (root/"compare.toml").write_text('[paths]\npages="pages.jsonl"\nlines="lines.jsonl"\n[experiment]\nsplit="test"\n', encoding="utf-8")
    monkeypatch.chdir(root)
    assert main(["compare", "--config", "compare.toml", "--output-dir", "cli"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "not_executed"


def test_compare_reports_global_integrity_failure_outside_selection(corpus, monkeypatch):
    root, config, pages, rows = independent_catalog(corpus)
    rows.append("registro inválido")
    for name in ("segment_pages", "create_recognizer", "recognize_lines"):
        monkeypatch.setattr(experiments, name, forbidden)
    output = root/"invalid_catalog"
    result = experiments.compare(pages, rows, config, output, root)
    assert result["status"] == "not_executed" and "Catálogo completo" in result["reason"]
    assert not json.loads((output/"validation.json").read_text(encoding="utf-8"))["global"]["valid"]
