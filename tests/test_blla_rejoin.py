"""blla pieces cut off a line are glued back before anyone reads them (no Docker)."""
import hashlib

from PIL import Image, ImageDraw

from paleographia.blla_segmentation import rejoin_line, side_fragments
from paleographia.services import ReviewService


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def line(lid, box, region="page", order=0, **extra):
    return {"line_id": lid, "page_id": "p", "document_id": "d", "folio_id": "f", "region_id": region,
            "reading_order": order, "source_image": "img.png", "crop_image": None, "bbox_xyxy": box,
            "source_width": 400, "source_height": 200, "split_group": "d", "source_sha256": "0" * 64,
            "review_status": "pending_review", "geometry_status": "pending_review", "text_diplomatic": None,
            "blla_geometry": {"baseline": [[box[0], box[3] - 5], [box[2], box[3] - 5]], "boundary": rect(*box)},
            **extra}


def test_side_fragments_pairs_cut_words_and_leaves_margin_notes():
    main = line("m", [60, 40, 300, 70], order=0)
    left = line("a", [20, 42, 52, 68], "margem", 1)        # first word, 8 px to the left
    right = line("b", [310, 38, 350, 66], "margem", 2)     # last word, 10 px to the right
    note = line("n", [360, 120, 395, 150], "margem", 3)    # margin number, another row
    far = line("z", [0, 40, 10, 70], "margem", 4)          # same row but 50 px away
    groups = side_fragments([main, left, right, note, far])
    assert {k: sorted(p["line_id"] for p in v) for k, v in groups.items()} == {"m": ["a", "b"]}


def page_image(path):
    image = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(image)
    for x in (25, 70, 150, 250, 320):
        draw.rectangle([x, 50, x + 20, 62], fill="black")
    image.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_record(sha):
    return {"page_id": "p", "document_id": "d", "folio_id": "f", "side": "unknown", "source_image": "img.png",
            "original_name": "img.png", "width": 400, "height": 200, "source_sha256": sha,
            "correspondence_status": "pending_review", "transcribed_coverage": []}


def test_rejoin_line_crops_the_union_and_keeps_order(tmp_path):
    sha = page_image(tmp_path / "img.png")
    main, left = line("m", [60, 40, 300, 70], order=5), line("a", [20, 42, 52, 68], "margem", 6)
    out = rejoin_line(page_record(sha), main, [left], tmp_path / "seg", tmp_path)
    assert out["bbox_xyxy"][0] <= 20 and out["bbox_xyxy"][2] >= 300
    assert out["reading_order"] == 5 and out["region_id"] == "page" and out["merged_from"] == ["a", "m"]
    crop = Image.open(tmp_path / out["crop_image"]).convert("L")
    assert crop.width >= 280 and min(crop.getdata()) < 50   # the cut-off word is inside the new crop


def test_service_never_touches_lines_with_human_work(tmp_path):
    sha = page_image(tmp_path / "img.png")
    service = ReviewService(tmp_path, {"paths": {"workspace": "ws"}, "recognition": {"backend": "disabled"}})
    lines = [line("m1", [60, 40, 300, 70], order=0), line("a1", [20, 42, 52, 68], "margem", 1),
             line("m2", [60, 120, 300, 150], order=2, review_status="validated", text_diplomatic="lida",
                  reviewer="R", reviewed_at="2026-11-09T00:00:00Z"),
             line("a2", [20, 122, 52, 148], "margem", 3)]
    for item in lines:
        item["source_sha256"] = sha
    service.save({"revision": None, "pages": [page_record(sha)], "lines": lines, "predictions": []}, "seed")
    rejoined = service.rejoin_blla_pieces("p")
    assert [r["merged_from"] for r in rejoined] == [["a1", "m1"]]
    ids = {item["line_id"] for item in service.state()["lines"]}
    assert {"m2", "a2"} <= ids and not {"m1", "a1"} & ids
    assert service.rejoin_blla_pieces("p") == []
