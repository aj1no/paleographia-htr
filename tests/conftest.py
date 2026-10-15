from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from paleographia.config import load_config
from paleographia.data import inventory
from paleographia.io import read_jsonl
from paleographia.segmentation import segment_pages


@pytest.fixture
def corpus(tmp_path):
    source = tmp_path/"data/raw/Entrada com acentos"
    source.mkdir(parents=True)
    image = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(image)
    # Synthetic marks, not manuscript evidence or a recognition benchmark.
    for y in (60, 140, 220):
        for x in range(50, 500, 24):
            draw.rectangle((x, y, x+14, y+6), fill="black")
    image.save(source/"Fólio 100 reto.png")
    config = load_config(Path(__file__).parents[1]/"configs/pilot.toml")
    inventory(source, tmp_path/"pages.jsonl", tmp_path)
    pages = read_jsonl(tmp_path/"pages.jsonl")
    pages[0].update(document_id="doc1831", folio_id="f100r", correspondence_status="validated",
                    reviewer="Test reviewer", reviewed_at="2026-10-15T12:00:00+00:00")
    lines, _ = segment_pages(pages, "opencv", config, tmp_path/"data/processed/run1", tmp_path)
    return tmp_path, config, pages, lines


def reviewed(rows):
    return [dict(r, review_status="validated", geometry_status="validated", text_diplomatic="Ação de 1831",
                 reference_kind="human_diplomatic", reviewer="Test reviewer",
                 reviewed_at="2026-10-15T12:00:00+00:00") for r in rows]
