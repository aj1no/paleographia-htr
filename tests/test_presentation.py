from fastapi.testclient import TestClient

from paleographia.api import create_app
from paleographia.presentation import present_prediction
from test_api import TestRecognizer


def test_portuguese_review_does_not_translate_or_destroy_raw_output(corpus):
    root, config, pages, lines = corpus
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        result = client.post(f"/api/pages/{pages[0]['page_id']}/recognize").json()
        assert result[0]["text_raw"] == "TEST ONLY"
        assert result[0]["presentation"]["status"] == "unavailable_in_portuguese"
        assert "português indisponível" in result[0]["presentation"]["text"]
        catalog = client.get("/api/catalog").json()
        assert catalog["predictions"][0]["presentation"] == result[0]["presentation"]
        assert not catalog["presentation_policy"]["automatic_transcription_enabled"]
        stored = app.state.service.state()["predictions"][0]
        assert stored["text_raw"] == "TEST ONLY" and "presentation" not in stored
        source = root/pages[0]["source_image"]
        processed = client.post("/process-folio?recognize=true", files={
            "file": ("Fólio.png", source.read_bytes(), "image/png")}).json()
        assert "português indisponível" in processed["lines"][0]["text"]
        response = client.patch("/api/lines/ausente", json={"changes": {}, "unexpected": True})
        assert response.status_code == 422
        assert response.json()["detail"] == "Há campos ausentes ou inválidos. Confira os valores e tente novamente."


def test_failed_and_obsolete_predictions_have_portuguese_messages(corpus):
    _, config, _, lines = corpus
    line = lines[0]
    prediction = {"status": "failed", "error": "English technical failure", "text_raw": ""}
    view = present_prediction(prediction, line, config)
    assert view["status"] == "failed" and "English" not in str(view)
    prediction.update(status="ok", bbox_xyxy=[0, 0, 1, 1], text_raw="Foreign output")
    view = present_prediction(prediction, line, config)
    assert view["status"] == "outdated" and "Foreign" not in str(view)
