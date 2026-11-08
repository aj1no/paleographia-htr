"""Leituras às cegas, concordância, tempos anônimos e exportação PAGE XML."""
import copy

from fastapi.testclient import TestClient

from paleographia.api import create_app
from paleographia.page_xml_import import read_page_xml
from test_api import TestRecognizer


def make(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    app = create_app(root, config, TestRecognizer())
    state = app.state.service.import_catalog(pages, lines)
    return root, app, state


def test_blind_readings_never_touch_the_line_and_stay_hidden(corpus):
    root, app, state = make(corpus)
    line, page_id = state["lines"][0], state["lines"][0]["page_id"]
    with TestClient(app) as client:
        assert client.post("/api/conferencia/cegas", json={"line_id": line["line_id"], "reviewer": "", "text": "x"}).status_code == 422
        assert client.post("/api/conferencia/cegas", json={"line_id": "nao_existe", "reviewer": "Ana", "text": "x"}).status_code == 404
        for reviewer, text in (("Ana", "Anno do Nacimento"), ("Bia", "Annodo Nacimento"), ("Ana", "Anno do Nacimento de")):
            assert client.post("/api/conferencia/cegas", json={"line_id": line["line_id"], "reviewer": reviewer, "text": text}).status_code == 200
        status = client.get("/api/conferencia/cegas", params={"page_id": page_id, "revisor": "Bia"}).json()
        # Só contagens: nenhum texto vaza para quem ainda está transcrevendo.
        assert status == {line["line_id"]: {"count": 2, "mine": True}}
        assert "Nacimento" not in str(status)
        catalog = client.get("/api/catalog").json()
        assert catalog["lines"][0] == state["lines"][0] and catalog["revision"] == state["revision"]
        result = client.get("/api/conferencia/concordancia", params={"page_id": page_id}).json()
    # Vale a última leitura de cada revisor: "Anno do Nacimento de" × "Annodo Nacimento".
    pair = result["lines"][0]["pairs"][0]
    assert pair["reviewers"] == ["Ana", "Bia"] and pair["distance"] == 4
    assert abs(result["rate"] - 4 / ((20 + 16) / 2)) < 1e-9
    assert result["lines"][0]["readings"] == {"Ana": "Anno do Nacimento de", "Bia": "Annodo Nacimento"}


def test_timing_is_anonymous_and_validated(corpus):
    root, app, state = make(corpus)
    line = state["lines"][0]
    body = {"line_id": line["line_id"], "seconds": 42.0, "condition": "com_sugestao", "action": "validada", "chars": 40}
    with TestClient(app) as client:
        assert client.post("/api/conferencia/tempo", json=body).status_code == 200
        assert client.post("/api/conferencia/tempo", json=dict(body, seconds=20.0, condition="sem_sugestao")).status_code == 200
        assert client.post("/api/conferencia/tempo", json=dict(body, seconds=0)).status_code == 422
        assert client.post("/api/conferencia/tempo", json=dict(body, condition="outra")).status_code == 422
        assert client.post("/api/conferencia/tempo", json=dict(body, reviewer="Ana")).status_code == 422
        summary = client.get("/api/conferencia/tempo").json()
    assert summary["com_sugestao"]["median_seconds"] == 42.0 and summary["sem_sugestao"]["lines"] == 1
    stored = (app.state.service.workspace/"conferencia"/"tempos_conferencia.jsonl").read_text(encoding="utf-8")
    assert "reviewer" not in stored and "text" not in stored


def test_page_xml_export_round_trips_through_the_importer(corpus, tmp_path):
    root, app, state = make(corpus)
    page, lines = state["pages"][0], state["lines"]
    with TestClient(app) as client:
        client.patch(f"/api/lines/{lines[0]['line_id']}", json={"revision": state["revision"], "changes": {
            "text_diplomatic": "Nˢᵃ Senhora", "review_status": "validated", "reference_kind": "human_diplomatic", "reviewer": "Ana"}})
        response = client.get(f"/api/pages/{page['page_id']}/pagexml")
        assert client.get("/api/pages/nao_existe/pagexml").status_code == 404
    assert response.status_code == 200 and response.headers["content-type"].startswith("application/xml")
    path = tmp_path/"saida.page.xml"
    path.write_bytes(response.content)
    image, read = read_page_xml(path)
    assert image == page["original_name"]
    kept = [l for l in lines if l["review_status"] != "rejected"]
    assert [r[0] for r in read] == [l["line_id"] for l in sorted(kept, key=lambda l: (l["reading_order"], str(l["region_id"])))]
    first = next(r for r in read if r[0] == lines[0]["line_id"])
    x1, y1, x2, y2 = lines[0]["bbox_xyxy"]
    assert first[1] == [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    assert first[2] == "Nˢᵃ Senhora" and "status:validated" in first[3] and "reviewer:Ana" in first[3]
