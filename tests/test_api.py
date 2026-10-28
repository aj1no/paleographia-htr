from fastapi.testclient import TestClient

from paleographia.api import create_app
from paleographia.recognition import ModelUnavailable


class TestRecognizer:
    """TEST ONLY: output exercises persistence, never a real transcription."""
    __test__ = False

    def load(self):
        pass

    def status(self):
        return {"state": "test_only", "load_seconds": 0}

    def recognize(self, image):
        return {"text_raw": "TEST ONLY", "model": {"id": "test-only"}}


class Unavailable(TestRecognizer):
    def load(self):
        raise ModelUnavailable("test unavailable")


def test_api_invalid_upload_and_unavailable_model(corpus):
    root, config, pages, lines = corpus
    app = create_app(root, config, Unavailable())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        response = client.post("/api/pages", files={"file": ("bad.jpg", b"bad", "image/jpeg")})
        assert response.status_code == 400
        response = client.post(f"/api/pages/{pages[0]['page_id']}/recognize")
        assert response.status_code == 503 and response.json()["review_available"]
        assert client.get("/health").status_code == 200
        assert client.get("/api/pages/no-such-page/image").status_code == 404


def test_api_processing_crop_geometry_review_and_raw_history(corpus):
    root, config, pages, lines = corpus
    app = create_app(root, config, TestRecognizer())
    with TestClient(app) as client:
        source = root/pages[0]["source_image"]
        response = client.post("/process-folio", files={"file": ("Fólio com acento.png", source.read_bytes(), "image/png")})
        assert response.status_code == 200
        data = response.json()
        assert data["total_lines"] == 3
        row = data["lines"][0]
        assert client.get(row["image_url"]).status_code == 200
        pid, lid = data["page_id"], row["line_id"]
        assert client.post(f"/api/pages/{pid}/recognize").status_code == 200
        state = client.get("/api/catalog").json()
        changes = {"text_diplomatic": "Humano", "review_status": "validated", "reference_kind": "human_diplomatic", "geometry_status": "validated"}
        assert client.patch(f"/api/lines/{lid}", json={"changes": changes}).status_code == 422
        changes["reviewer"] = "Test reviewer"
        response = client.patch(f"/api/lines/{lid}", json={"changes": changes, "revision": state["revision"]})
        assert response.status_code == 200 and response.json()["reviewed_at"]
        assert client.patch(f"/api/lines/{lid}", json={"changes": changes, "revision": state["revision"]}).status_code == 409
        state = client.get("/api/catalog").json()
        assert state["predictions"][0]["text_raw"] == "TEST ONLY"
        assert next(l for l in state["lines"] if l["line_id"] == lid)["text_diplomatic"] == "Humano"
        assert len(list((root/config["paths"]["workspace"]/"revisions").glob("*.json"))) >= 4
        response = client.patch(f"/api/lines/{lid}", json={"changes": {"bbox_xyxy": [50, 40, 500, 90]}})
        assert response.status_code == 200 and response.json()["review_status"] == "pending_review"
        assert client.get("/api/export").headers["content-type"] == "application/zip"
        assert client.get("/").status_code == 200
    recovered = create_app(root, config, TestRecognizer())
    assert recovered.state.service.state()["predictions"][0]["text_raw"] == "TEST ONLY"


def test_exif_preview_and_path_validation(corpus):
    import io
    from PIL import Image
    root, config, _, _ = corpus
    picture = Image.new("RGB", (200, 100), "white")
    exif = Image.Exif()
    exif[274] = 6
    buffer = io.BytesIO()
    picture.save(buffer, format="JPEG", exif=exif)
    app = create_app(root, config, TestRecognizer())
    with TestClient(app) as client:
        page = client.post("/api/pages", files={"file": ("girado.jpg", buffer.getvalue(), "image/jpeg")}).json()
        response = client.get(f"/api/pages/{page['page_id']}/image")
        with Image.open(io.BytesIO(response.content)) as preview:
            assert preview.size == (200, 100) and not preview.getexif()
        response = client.patch(f"/api/pages/{page['page_id']}", json={"changes": {"source_image": "../secret"}})
        assert response.status_code == 422


def test_geometry_edit_refreshes_existing_crop_hash_in_export(corpus):
    import io
    import json
    import zipfile

    from paleographia.io import sha256

    root, config, pages, lines = corpus
    original = lines[0]
    original["crop_sha256"] = sha256(root / original["crop_image"])
    old_crop_bytes = (root / original["crop_image"]).read_bytes()
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        before = client.get("/api/catalog").json()
        revision_path = (root / config["paths"]["workspace"] / "revisions"
                         / (before["revision"] + ".json"))
        original_revision_bytes = revision_path.read_bytes()
        box = list(original["bbox_xyxy"])
        box[1] = max(0, box[1] - 10)
        response = client.patch(f"/api/lines/{original['line_id']}", json={
            "revision": before["revision"], "changes": {"bbox_xyxy": box}})
        assert response.status_code == 200
        saved = response.json()
        assert saved["line_id"] == original["line_id"]
        assert saved["crop_image"] != original["crop_image"]
        assert saved["crop_sha256"] == sha256(root / saved["crop_image"])
        assert saved["crop_sha256"] != original["crop_sha256"]
        assert (root / original["crop_image"]).read_bytes() == old_crop_bytes
        assert revision_path.read_bytes() == original_revision_bytes
        with zipfile.ZipFile(io.BytesIO(client.get("/api/export").content)) as archive:
            exported = [json.loads(row) for row in archive.read("lines.jsonl").splitlines()]
        assert next(row for row in exported if row["line_id"] == saved["line_id"]) == saved
