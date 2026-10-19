"""Fixtures lexicais sintéticas; a conferência documental real tem teste separado."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from paleographia.api import create_app
from paleographia.lexicon import Lexicon
from test_api import TestRecognizer


def synthetic_entry(form, number):
    return {"id": f"synthetic_{number}", "form": form, "repertoire": "portugues_historico", "language": "português",
        "language_note": "SINTÉTICO: não é verbete documental.", "kind": "teste", "meaning": None,
        "note": "SINTÉTICO, exclusivo de teste.", "attestation_period": "período sintético",
        "source_id": "test_only", "volume": "teste", "printed_page": "1", "pdf_page": 1,
        "locator": "página sintética 1", "url": "https://example.org/test-only", "source_file": None,
        "source_sha256": None, "evidence": "verificado_na_fonte", "checked_by": "Teste sintético",
        "checked_at": "2026-10-19T12:00:00+00:00", "extraction": "fixture sintética", "corpus_origin": None}


def write_lexicon(root, rows=None):
    folder = root/"data/lexicon"
    folder.mkdir(parents=True, exist_ok=True)
    sources = {"version": "test-only-v1", "sources": [{"id": "test_only", "title": "Fonte SINTÉTICA",
        "url": "https://example.org/test-only", "publication_period": "teste",
        "use_conditions": "Exclusivo de teste; não é fonte histórica."}]}
    rows = rows if rows is not None else [synthetic_entry(form, i) for i, form in enumerate(
        ["Anno", "do", "Jundiahy", "mõr", "Casa", "da", "terra"])]
    (folder/"sources.json").write_text(json.dumps(sources, ensure_ascii=False), encoding="utf-8")
    (folder/"entries.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in rows), encoding="utf-8")
    return rows


def test_query_preserves_forms_nfc_case_accents_and_conservative_distance(tmp_path):
    write_lexicon(tmp_path)
    lexicon = Lexicon(tmp_path)
    assert lexicon.query("Anno")["candidates"][0]["match"] == "exact"
    assert lexicon.query("anno")["candidates"][0]["replacement"] == "Anno"
    assert lexicon.query("mo\u0303r")["candidates"][0]["replacement"] == "mõr"
    assert lexicon.query("mor")["candidates"][0]["match"] == "accent"
    c = lexicon.query("Sundiahy")["candidates"][0]
    assert (c["replacement"], c["distance"], c["match"]) == ("Jundiahy", 1, "edit_distance")
    for query in ("f", "u", "j", "xyzxyzxyz"):
        assert lexicon.query(query)["candidates"] == []
    assert "probabilidade" not in c  # Distance is not calibrated confidence.


def test_splitting_is_generic_and_does_not_join_physical_lines(tmp_path):
    write_lexicon(tmp_path)
    lexicon = Lexicon(tmp_path)
    assert lexicon.query("Annodo")["candidates"][0]["replacement"] == "Anno do"
    assert lexicon.query("Casadaterra")["candidates"][0]["replacement"] == "Casa da terra"
    assert lexicon.query("ca / torze")["candidates"] == []
    assert lexicon.query("Deste / rro")["candidates"] == []
    assert lexicon.query("abai / xo")["candidates"] == []


def test_pending_and_repertoires_and_origin_filter(tmp_path):
    rows = write_lexicon(tmp_path)
    origin = {"document_id": "doc-test", "split_group": "group-test", "revision": "test-revision",
              "line_id": "test-line", "split": None, "dataset_role": "development",
              "reviewer": "Pessoa de teste", "reviewed_at": "2026-10-19T12:00:00+00:00"}
    rows[2].update(repertoire="acervo", evidence="atestado_no_acervo", corpus_origin=origin, language=None)
    rows.append(dict(synthetic_entry("Pendente", 90), evidence="pendente"))
    rows.append(dict(synthetic_entry("abá", 91), repertoire="indigena", language="idioma sintético identificado pela fonte"))
    write_lexicon(tmp_path, rows)
    lexicon = Lexicon(tmp_path)
    assert not lexicon.query("Pendente")["candidates"]
    assert not lexicon.query("Sundiahy", "portugues_historico")["candidates"]
    assert lexicon.query("Sundiahy", "acervo")["candidates"][0]["entries"][0]["meaning"] is None
    assert not lexicon.query("Sundiahy", exclude_groups=["group-test"])["candidates"]
    assert lexicon.query("abá", "indigena")["candidates"][0]["entries"][0]["language"].startswith("idioma sintético")


@pytest.mark.parametrize("damage", ["locator", "source", "duplicate", "date", "origin", "language", "page", "hash", "variant"])
def test_invalid_evidence_is_rejected(tmp_path, damage):
    rows = write_lexicon(tmp_path)
    if damage == "locator": rows[0]["locator"] = ""
    elif damage == "source": rows[0]["source_id"] = "unknown"
    elif damage == "duplicate": rows.append(copy.deepcopy(rows[0]))
    elif damage == "date": rows[0]["checked_at"] = "2026-10-19"
    elif damage == "origin": rows[0]["repertoire"] = "acervo"
    elif damage == "language": rows[0].update(repertoire="indigena", language=None)
    elif damage == "page": rows[0].update(printed_page=None, pdf_page=None)
    elif damage == "hash": rows[0].update(source_file="data/lexicon/sources.json", source_sha256="0"*64)
    elif damage == "variant": rows[0]["variant_of"] = "unknown"
    write_lexicon(tmp_path, rows)
    with pytest.raises(ValueError, match="Base lexical indisponível"):
        Lexicon(tmp_path)


def test_query_bounds_and_original_form_not_modified(tmp_path):
    write_lexicon(tmp_path)
    lexicon = Lexicon(tmp_path)
    before = copy.deepcopy(lexicon.entries)
    for query in ("", " "*4, "x"*81):
        with pytest.raises(ValueError): lexicon.query(query)
    with pytest.raises(ValueError): lexicon.query("Anno", repertoire="tudo_inventado")
    with pytest.raises(ValueError): lexicon.query("Anno", limit=9)
    assert len(lexicon.query("Anno", limit=1)["candidates"]) == 1
    assert lexicon.entries == before


def application(lexicon, before="Em Sundiahy", start=3, end=11):
    candidate = lexicon.query("Sundiahy")["candidates"][0]
    return {"version": lexicon.version, "fingerprint": lexicon.fingerprint, "candidate_id": candidate["id"],
            "query": "Sundiahy", "repertoire": "all", "before": before,
            "after": before[:start]+candidate["replacement"]+before[end:], "start": start, "end": end}


def test_api_application_persists_provenance_without_promoting_or_rewriting_history(corpus):
    root, config, pages, lines = corpus
    write_lexicon(root)
    app = create_app(root, config, TestRecognizer())
    initial = app.state.service.import_catalog(pages, lines)
    old_file = app.state.service.workspace/"revisions"/(initial["revision"]+".json")
    old_bytes = old_file.read_bytes()
    pid, lid = pages[0]["page_id"], lines[0]["line_id"]
    with TestClient(app) as client:
        assert client.post(f"/api/pages/{pid}/recognize").status_code == 200
        state = client.get('/api/catalog').json()
        response = client.post('/api/lexicon/query', json={"text": "Sundiahy"})
        assert response.status_code == 200 and response.json()["candidates"][0]["replacement"] == "Jundiahy"
        assert client.get('/api/catalog').json() == state
        event = application(Lexicon(root), before="📜 Sundiahy", start=2, end=10)
        changes = {"text_diplomatic": event["after"], "lexical_assistance": [event]}
        result = client.patch(f'/api/lines/{lid}', json={"changes": changes, "revision": state["revision"]})
        assert result.status_code == 200, result.text
        saved = result.json()
        assert saved["review_status"] == saved["geometry_status"] == "pending_review"
        assert saved["reference_kind"] == "unknown"
        assert saved["lexical_assistance"][0]["entry_ids"] == ["synthetic_2"]
        assert saved["lexical_assistance"][0]["recorded_at"]
        current = client.get('/api/catalog').json()
        assert current["pages"] == state["pages"] and current["predictions"] == state["predictions"]
        assert old_file.read_bytes() == old_bytes
        assert client.patch(f'/api/lines/{lid}', json={"changes": changes, "revision": state["revision"]}).status_code == 409
        assert client.patch(f'/api/lines/{lid}', json={"changes": {"lexical_assistance": []}}).status_code == 422
        # An unavailable lexicon must not block manual editing or preservation of prior events.
        (root/'data/lexicon/sources.json').write_text('{}', encoding='utf-8')
        assert not client.post('/api/lexicon/query', json={"text": "Anno"}).json()["available"]
        assert client.patch(f'/api/lines/{lid}', json={"changes": {"text_diplomatic": "Outra leitura", "lexical_assistance": saved["lexical_assistance"]}}).status_code == 200
    assert create_app(root, config, TestRecognizer()).state.service.state()["lines"][0]["lexical_assistance"] == saved["lexical_assistance"]


@pytest.mark.parametrize("damage", ["fingerprint", "candidate", "after", "range"])
def test_api_rejects_stale_or_forged_application(corpus, damage):
    root, config, pages, lines = corpus
    write_lexicon(root)
    app = create_app(root, config, TestRecognizer())
    initial = app.state.service.import_catalog(pages, lines)
    event = application(Lexicon(root))
    if damage == "fingerprint": event["fingerprint"] = "0"*64
    elif damage == "candidate": event["candidate_id"] = "invented"
    elif damage == "after": event["after"] = "texto sem fonte"
    else: event["start"] = 100
    with TestClient(app) as client:
        assert client.patch(f'/api/lines/{lines[0]["line_id"]}', json={"changes": {"lexical_assistance": [event]}}).status_code == 422
        assert client.get('/api/catalog').json()["revision"] == initial["revision"]


def test_real_curated_attestations_are_literal_and_sources_are_auditable():
    root = Path(__file__).parents[1]
    lexicon = Lexicon(root)
    assert len(lexicon.entries) == 21
    assert sum(e["repertoire"] == "indigena" for e in lexicon.entries) == 0
    for entry in lexicon.entries:
        if entry["corpus_origin"]:
            rows = [json.loads(line) for line in (root/entry["source_file"]).read_text(encoding='utf-8').splitlines()]
            source = next(r for r in rows if r["line_id"] == entry["corpus_origin"]["line_id"])
            assert source["review_status"] == "validated" and entry["form"] in source["text_diplomatic"]
            assert source["reviewer"] == entry["corpus_origin"]["reviewer"]
        else:
            assert (entry["volume"], entry["printed_page"], entry["pdf_page"]) in {("1", "385", 493), ("4", "206", 222)}
            assert hashlib.sha256((root/entry["evidence_file"]).read_bytes()).hexdigest() == entry["evidence_sha256"]
