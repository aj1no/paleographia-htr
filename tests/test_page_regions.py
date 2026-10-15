import copy

import pytest
from fastapi.testclient import TestClient

from paleographia.api import create_app
from test_api import TestRecognizer


def coverages(count):
    return [{"region_id": "page" if i == 0 else "margin", "bbox_xyxy": [0, i*100, 600, (i+1)*100],
             "reference_source": None, "reference_pages": [i+1], "complete": True,
             "review_status": "validated", "reviewer": f"Revisor anterior {i}",
             "reviewed_at": "2026-10-14T12:00:00+00:00", "provenance": {"note": f"origem {i}"}}
            for i in range(count)]


@pytest.mark.parametrize("count", [0, 1, 2])
def test_metadata_save_preserves_all_regions_history_and_reopen(corpus, count):
    root, config, pages, lines = copy.deepcopy(corpus)
    pages[0]["transcribed_coverage"] = coverages(count)
    lines[0]["split"] = "exploratory"
    app = create_app(root, config, TestRecognizer())
    initial = app.state.service.import_catalog(pages, lines)
    before = copy.deepcopy(initial)
    with TestClient(app) as client:
        assert '/review.js' in client.get('/').text
        assert 'captureDrafts' in client.get('/review.js').text
        path = f"/api/pages/{pages[0]['page_id']}"
        # Include an unchanged full list too: a client round trip must not stamp it.
        response = client.patch(path, json={"revision": initial["revision"], "changes": {
            "credits": "Créditos conferidos", "transcribed_coverage": coverages(count)}})
        assert response.status_code == 200
        assert response.json()["transcribed_coverage"] == before["pages"][0]["transcribed_coverage"]
        assert response.json()["reviewed_at"] == pages[0]["reviewed_at"]
        assert client.patch(path, json={"revision": initial["revision"], "changes": {"credits": "Obsoleto"}}).status_code == 409
    recovered = create_app(root, config, TestRecognizer()).state.service.state()
    assert recovered["pages"][0]["transcribed_coverage"] == coverages(count)
    assert recovered["lines"] == lines
    old = root/config["paths"]["workspace"]/"revisions"/(initial["revision"]+".json")
    import json
    assert json.loads(old.read_text(encoding="utf-8")) == before


def test_edit_second_region_and_block_orphans(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    pages[0]["transcribed_coverage"] = coverages(2)
    lines[1]["region_id"] = "margin"
    app = create_app(root, config, TestRecognizer())
    initial = app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        path = f"/api/pages/{pages[0]['page_id']}"
        updated = coverages(2)
        updated[1]["bbox_xyxy"] = [1, 100, 599, 200]
        response = client.patch(path, json={"revision": initial["revision"], "changes": {"transcribed_coverage": updated}})
        assert response.status_code == 200
        saved = response.json()["transcribed_coverage"]
        assert saved[0] == coverages(2)[0]
        assert saved[1]["bbox_xyxy"] == updated[1]["bbox_xyxy"]
        assert saved[1]["provenance"] == updated[1]["provenance"]
        assert saved[1]["reviewer"] == pages[0]["reviewer"]
        assert saved[1]["reviewed_at"] != coverages(2)[1]["reviewed_at"]
        revision = client.get('/api/catalog').json()["revision"]
        for regions in (saved[:1], [dict(c, region_id="renamed") if c["region_id"] == "margin" else c for c in saved]):
            response = client.patch(path, json={"revision": revision, "changes": {"transcribed_coverage": regions}})
            assert response.status_code == 409 and "linhas associadas" in response.json()["detail"]
        assert client.get('/api/catalog').json()["revision"] == revision
        # Reassign the existing line explicitly, then the region can be removed.
        assert client.patch(f"/api/lines/{lines[1]['line_id']}", json={"changes": {"region_id": "page"}, "revision": revision}).status_code == 200
        revision = client.get('/api/catalog').json()["revision"]
        assert client.patch(path, json={"revision": revision, "changes": {"transcribed_coverage": saved[:1]}}).status_code == 200
    assert create_app(root, config, TestRecognizer()).state.service.state()["pages"][0]["transcribed_coverage"] == saved[:1]
