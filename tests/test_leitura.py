"""Modo leitura: a página existe e o contrato de salvamento que ela usa não mexe no recorte."""
import copy

from fastapi.testclient import TestClient

from paleographia.api import create_app
from test_api import TestRecognizer


def test_reading_page_is_served_and_links_back(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        page = client.get("/leitura")
        assert page.status_code == 200
        for marker in ('id="mine"', 'id="ruler"', "differingWords", "/api/lines/", 'href="/"'):
            assert marker in page.text
        assert 'href="/leitura"' in client.get("/").text


def test_reading_mode_saves_only_text_status_and_reviewer(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    lines[0].update(geometry_status="pending_review")
    app = create_app(root, config, TestRecognizer())
    state = app.state.service.import_catalog(pages, lines)
    line = state["lines"][0]
    path = f"/api/lines/{line['line_id']}"
    with TestClient(app) as client:
        # Validar sem revisor é recusado pelo servidor, não só pela página.
        refused = client.patch(path, json={"revision": state["revision"], "changes": {
            "text_diplomatic": "Anno do Nacimento", "review_status": "validated", "reference_kind": "human_diplomatic"}})
        assert refused.status_code == 422
        validated = client.patch(path, json={"revision": state["revision"], "changes": {
            "text_diplomatic": "Anno do Nacimento", "review_status": "validated",
            "reference_kind": "human_diplomatic", "reviewer": "Revisora"}})
        assert validated.status_code == 200
        body = validated.json()
        assert body["review_status"] == "validated" and body["reviewer"] == "Revisora" and body["reviewed_at"]
        # O modo leitura não toca na geometria: recorte, ordem e conferência do recorte ficam como estavam.
        for key in ("bbox_xyxy", "reading_order", "region_id", "geometry_status", "crop_image"):
            assert body[key] == line[key]
        revision = client.get("/api/catalog").json()["revision"]
        draft = client.patch(path, json={"revision": revision, "changes": {
            "text_diplomatic": "Anno do Nacimento de", "review_status": "pending_review"}})
        assert draft.status_code == 200
        assert draft.json()["review_status"] == "pending_review" and draft.json()["reviewed_at"] is None
        # Uma página aberta com a revisão antiga recebe conflito em vez de sobrescrever.
        stale = client.patch(path, json={"revision": revision, "changes": {"text_diplomatic": "x", "review_status": "pending_review"}})
        assert stale.status_code == 409
