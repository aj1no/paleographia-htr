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
        assert client.patch(f"/api/lines/{lid}", json={"changes": changes, "revision": state["revision"]}).status_code == 422
        changes["reviewer"] = "Test reviewer"
        response = client.patch(f"/api/lines/{lid}", json={"changes": changes, "revision": state["revision"]})
        assert response.status_code == 200 and response.json()["reviewed_at"]
        assert client.patch(f"/api/lines/{lid}", json={"changes": changes, "revision": state["revision"]}).status_code == 409
        state = client.get("/api/catalog").json()
        assert state["predictions"][0]["text_raw"] == "TEST ONLY"
        assert next(l for l in state["lines"] if l["line_id"] == lid)["text_diplomatic"] == "Humano"
        assert len(list((root/config["paths"]["workspace"]/"revisions").glob("*.json"))) >= 4
        response = client.patch(f"/api/lines/{lid}", json={"changes": {"bbox_xyxy": [50, 40, 500, 90]}, "revision": state["revision"]})
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
        response = client.patch(f"/api/pages/{page['page_id']}", json={"changes": {"source_image": "../secret"}, "revision": client.get("/api/catalog").json()["revision"]})
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


def test_upload_accepts_pdf_pages_and_other_image_formats(corpus):
    import io

    import pytest
    from PIL import Image
    pymupdf = pytest.importorskip("pymupdf")
    root, config, pages, lines = corpus
    app = create_app(root, config, TestRecognizer())
    pdf = pymupdf.open()
    for texto in ("primeira", "segunda"):
        pdf.new_page(width=300, height=400).insert_text((40, 60), texto)
    webp = io.BytesIO()
    Image.new("RGB", (120, 80), (200, 180, 150)).save(webp, "WEBP")
    with TestClient(app) as client:
        response = client.post("/api/pages", files={"file": ("livro.pdf", pdf.tobytes(), "application/pdf")})
        assert response.status_code == 200
        body = response.json()
        assert len(body["imported_pages"]) == 2 and body["page_id"] == body["imported_pages"][0]
        names = {p["page_id"]: p["original_name"] for p in client.get("/api/catalog").json()["pages"]}
        assert names[body["imported_pages"][1]] == "livro · página 2 do PDF.png"
        response = client.post("/api/pages", files={"file": ("foto.webp", webp.getvalue(), "image/webp")})
        assert response.status_code == 200 and response.json()["original_name"] == "foto.png"
        assert client.get(f"/api/pages/{response.json()['page_id']}/image").status_code == 200
        bad = client.post("/api/pages", files={"file": ("x.pdf", b"%PDF-quebrado", "application/pdf")})
        assert bad.status_code == 400


def test_demo_cache_brings_back_a_preprocessed_folio_on_upload(corpus, tmp_path):
    import hashlib
    import io
    import json

    from PIL import Image
    root, config, pages, lines = corpus
    picture = io.BytesIO()
    Image.new("RGB", (200, 120), (210, 190, 160)).save(picture, "JPEG")
    content = picture.getvalue()
    checksum = hashlib.sha256(content).hexdigest()
    crop = root / "demo_cache" / "l_demo.png"
    crop.parent.mkdir(parents=True)
    Image.new("RGB", (180, 20), "white").save(crop)
    page_id = "p_" + checksum[:20]
    entry = {"page": {"page_id": page_id, "document_id": "demo", "folio_id": "101r", "side": "recto",
                      "source_image": "x.jpg", "original_name": "Fólio 101 reto.JPG", "width": 200, "height": 120,
                      "source_sha256": checksum, "correspondence_status": "pending_review", "transcribed_coverage": []},
             "lines": [{"line_id": "l_demo", "page_id": page_id, "document_id": "demo", "folio_id": "101r",
                        "region_id": "page", "reading_order": 0, "source_image": "x.jpg",
                        "crop_image": "demo_cache/l_demo.png", "bbox_xyxy": [10, 10, 190, 30], "source_width": 200,
                        "source_height": 120, "split_group": "demo", "source_sha256": checksum,
                        "review_status": "pending_review", "geometry_status": "pending_review"}],
             "predictions": [], "processed_at": "2026-11-09T20:00:00Z"}
    (crop.parent / f"{checksum}.json").write_text(json.dumps(entry), encoding="utf-8")
    app = create_app(root, dict(config, demo={"cache_dir": "demo_cache"}), TestRecognizer())
    with TestClient(app) as client:
        body = client.post("/api/pages", files={"file": ("foto.jpg", content, "image/jpeg")}).json()
        assert body["from_demo_cache"] is True and body["cached_lines"] == 1 and body["page_id"] == page_id
        catalog = client.get("/api/catalog").json()
        assert [l["line_id"] for l in catalog["lines"] if l["page_id"] == page_id] == ["l_demo"]
        again = client.post("/api/pages", files={"file": ("foto.jpg", content, "image/jpeg")}).json()
        assert "from_demo_cache" not in again  # já está na lista: não duplica


def test_upload_of_an_image_already_in_the_catalog_opens_the_existing_folio(corpus):
    root, config, pages, lines = corpus
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    content = (root / pages[0]["source_image"]).read_bytes()
    with TestClient(app) as client:
        body = client.post("/api/pages", files={"file": ("de novo.png", content, "image/png")}).json()
        assert body["page_id"] == pages[0]["page_id"]
        assert len(client.get("/api/catalog").json()["pages"]) == len(pages)
