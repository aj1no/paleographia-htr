"""Integrity and review-state tests; synthetic archives are not corpus evidence."""
import hashlib
import json
import zipfile

import pytest

from paleographia import corpus_expansion as expansion
from paleographia.io import read_jsonl, sha256, write_json, write_jsonl


def archive_fixture(tmp_path, monkeypatch, entries=None, inventory=None):
    entries = entries or {"README.md": b"source", "never_execute.py": b"raise RuntimeError('DO NOT RUN')"}
    inventory = inventory or {n: hashlib.sha256(v).hexdigest() for n, v in entries.items()}
    archive = tmp_path / "corpus.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for name, content in entries.items():
            z.writestr(expansion.PACKAGE + "/" + name, content)
        z.writestr(expansion.PACKAGE + "/INVENTARIO_EXPANDIDO_SHA256.json", json.dumps(inventory))
    monkeypatch.setattr(expansion, "ARCHIVE_SHA256", sha256(archive))
    return archive


def test_archive_is_verified_and_scripts_are_only_preserved(tmp_path, monkeypatch):
    archive = archive_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(expansion, "index_sources", lambda *a: {"labels_created": 0})
    assert expansion.incorporate(archive, "sources", "catalog", tmp_path) == {"labels_created": 0}
    assert (tmp_path / "sources/never_execute.py").read_bytes().startswith(b"raise RuntimeError")
    with pytest.raises(ValueError, match="pastas novas"):
        expansion.incorporate(archive, "sources", "catalog2", tmp_path)


@pytest.mark.parametrize("name", ["../escape.py", "D:/outside.py", "folder\\escape.py", "/absolute.py"])
def test_archive_paths_cannot_escape_destination(tmp_path, monkeypatch, name):
    archive = archive_fixture(tmp_path, monkeypatch, {name: b"unsafe"})
    with pytest.raises(ValueError, match="inseguro"):
        expansion.incorporate(archive, "sources", "catalog", tmp_path)
    assert not (tmp_path / "sources").exists()


def test_internal_hash_mismatch_is_rejected_before_extraction(tmp_path, monkeypatch):
    archive = archive_fixture(tmp_path, monkeypatch, {"README.md": b"source"}, {"README.md": "0" * 64})
    with pytest.raises(ValueError, match="Hash divergente"):
        expansion.incorporate(archive, "sources", "catalog", tmp_path)
    assert not (tmp_path / "sources").exists()


def test_unexpected_archive_and_aliases_are_rejected(tmp_path, monkeypatch):
    archive = archive_fixture(tmp_path, monkeypatch, {"File.txt": b"a", "file.txt": b"b"})
    with pytest.raises(ValueError, match="duplicados"):
        expansion.incorporate(archive, "sources", "catalog", tmp_path)
    monkeypatch.setattr(expansion, "ARCHIVE_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="SHA-256 do ZIP"):
        expansion.incorporate(archive, "sources", "catalog", tmp_path)


def test_document_reproductions_cannot_create_independent_groups():
    assert expansion.document_group("traslado_criacao_vila") == "tt_pbr_0004_026_traslado_1767"
    assert expansion.MANUSCRIPT_PAGES["c7ffb34ac9b8c735"] == [9, 10, 11, 12]
    assert expansion.document_group("posturas_1831") == "jundiai_atas_sessao_1831-07-11"


def test_restore_missing_bytes_is_idempotent_and_never_overwrites(tmp_path, monkeypatch):
    # The lightweight CI intentionally does not install the optional PDF extra.
    import sys
    monkeypatch.setitem(sys.modules, "pypdf", None)
    archive = archive_fixture(tmp_path, monkeypatch)
    catalog = tmp_path / "catalog"
    write_json(catalog / "incorporation.json", {"archive_sha256": sha256(archive), "source_root": "sources"})
    write_jsonl(catalog / "sources.jsonl", [])
    write_jsonl(catalog / "embedded_images.jsonl", [])
    first = expansion.restore(archive, catalog, tmp_path)
    assert first["files_restored"] == 3 and not first["catalogs_modified"]
    assert expansion.restore(archive, catalog, tmp_path)["files_restored"] == 0
    path = tmp_path / "sources/README.md"
    path.write_bytes(b"local change")
    with pytest.raises(ValueError, match="não sobrescreve"):
        expansion.restore(archive, catalog, tmp_path)
    assert path.read_bytes() == b"local change"


def test_published_block_is_pending_and_cannot_be_used_for_training():
    from pathlib import Path
    from paleographia.data import validate
    root = Path(__file__).resolve().parents[1]
    block = root / "docs/dataset_expansion_20261023/curation_sessao_1795_bloco01"
    rows, pages = read_jsonl(block / "lines.jsonl"), read_jsonl(block / "pages.jsonl")
    assert len(rows) == 8
    assert all(r["text_diplomatic"] is None and r["text_published"] and r["review_status"] == "pending_review"
               and r["geometry_status"] == "pending_review" and not r["visual_confirmation"] for r in rows)
    # The committed manifest records status even in a checkout without local ZIP.
    assert not validate(rows, root, "training", pages)["valid"]


def test_core_statuses_are_preserved_in_additive_catalog():
    from pathlib import Path
    from collections import Counter
    root = Path(__file__).resolve().parents[1]
    rows = read_jsonl(root / "data/manifests/corpus_expandido_v02/core_lines.jsonl")
    assert Counter(r["review_status"] for r in rows) == {"validated": 16, "pending_review": 8}
    assert sum(r["historical_reservation"] for r in rows) == 8
    for row in rows:
        original = row["frozen_sample"]
        assert row["review_status"] == original["estado_textual"]
        assert row["geometry_status"] == original["estado_geometria"]
        assert row["subsequent_reconference"] == original["reconferencia_posterior"]
        assert row["partition"] == "development" and row["split"] is None
