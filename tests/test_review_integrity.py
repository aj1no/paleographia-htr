"""Provenance and write-safety guarantees of the review API (synthetic data only)."""
from fastapi.testclient import TestClient

from paleographia.api import create_app

from conftest import reviewed
from test_api import TestRecognizer

ORIGINAL_STAMP = "2026-10-15T12:00:00+00:00"


def client_for(corpus, validated=True):
    root, config, pages, lines = corpus
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, reviewed(lines) if validated else lines)
    return app, lines


def patch_line(client, line_id, changes, revision=None):
    revision = revision or client.get("/api/catalog").json()["revision"]
    return client.patch(f"/api/lines/{line_id}", json={"changes": changes, "revision": revision})


def test_unrelated_save_keeps_validation_timestamp(corpus):
    app, lines = client_for(corpus)
    with TestClient(app) as client:
        response = patch_line(client, lines[0]["line_id"], {"text_modernized": "Ação de 1831 (modernizada)",
                                                            "exclusion_reason": None})
        assert response.status_code == 200, response.text
        saved = response.json()
        assert saved["review_status"] == "validated"
        assert saved["reviewed_at"] == ORIGINAL_STAMP


def test_new_attestation_refreshes_validation_timestamp(corpus):
    app, lines = client_for(corpus)
    with TestClient(app) as client:
        response = patch_line(client, lines[0]["line_id"], {"text_diplomatic": "Acção de 1831"})
        assert response.status_code == 200, response.text
        assert response.json()["reviewed_at"] != ORIGINAL_STAMP
        response = patch_line(client, lines[1]["line_id"], {"reviewer": "Outra pessoa revisora"})
        assert response.status_code == 200, response.text
        assert response.json()["reviewed_at"] != ORIGINAL_STAMP


def test_edit_without_revision_is_rejected_and_not_saved(corpus):
    app, lines = client_for(corpus, validated=False)
    with TestClient(app) as client:
        before = client.get("/api/catalog").json()
        for path, changes in ((f"/api/lines/{lines[0]['line_id']}", {"text_diplomatic": "Sem base"}),
                              (f"/api/pages/{before['pages'][0]['page_id']}", {"folio_id": "f101r"})):
            assert client.patch(path, json={"changes": changes}).status_code == 422
            assert client.patch(path, json={"changes": changes, "revision": ""}).status_code == 422
        assert client.get("/api/catalog").json()["revision"] == before["revision"]


def test_cross_origin_writes_are_refused(corpus):
    app, lines = client_for(corpus, validated=False)
    root = corpus[0]
    picture = (root / corpus[2][0]["source_image"]).read_bytes()
    with TestClient(app) as client:
        before = client.get("/api/catalog").json()["revision"]
        for origin in ("https://example.org", "null", "http://127.0.0.1:9999"):
            headers = {"Origin": origin}
            upload = client.post("/api/pages", files={"file": ("x.png", picture, "image/png")}, headers=headers)
            assert upload.status_code == 403
            edit = client.patch(f"/api/lines/{lines[0]['line_id']}", headers=headers,
                                json={"changes": {"text_diplomatic": "Intrusa"}, "revision": before})
            assert edit.status_code == 403
        assert client.get("/api/catalog").json()["revision"] == before
        # Reads stay open, and the editor's own origin may still write.
        assert client.get("/health", headers={"Origin": "https://example.org"}).status_code == 200
        own = client.patch(f"/api/lines/{lines[0]['line_id']}", headers={"Origin": "http://testserver"},
                           json={"changes": {"text_diplomatic": "Rascunho"}, "revision": before})
        assert own.status_code == 200, own.text


def test_empty_model_output_is_reported_as_no_writing_found():
    from paleographia.api import present_predictions
    from paleographia.config import load_config
    from pathlib import Path
    config = load_config(Path(__file__).parents[1] / "configs/editor_folios.toml")
    settings, policy = config["recognition"], config["presentation"]
    identity = {"backend": "kraken_ppocrv6", "sha256": settings["sha256"],
                "docker_image_id": settings["docker_image_id"], "worker_sha256": policy["evaluated_worker_sha256"]}
    line = {"line_id": "l1", "bbox_xyxy": [0, 0, 10, 10]}
    rows = present_predictions([dict(line, status="ok", text_raw=raw, model=identity) for raw in ("", "  ", "Aos vinte")],
                               [line], config)
    assert [r["presentation"]["status"] for r in rows] == ["empty", "empty", "candidate"]
    assert "não encontrou escrita" in rows[0]["presentation"]["text"]
    assert rows[2]["presentation"]["text"] == "Aos vinte" and rows[0]["text_raw"] == ""
