"""Import line-level ground truth from PAGE XML (e.g. Transkribus exports) as training pairs.

Each TextLine becomes a polygon crop (same convention as the blla crops) and its
line-level TextEquiv/Unicode becomes the label. Lines are skipped when the text is
empty, marked uncertain (``??``) or tagged ``unclear``, or contains characters the
recognizer's codec cannot emit (training with ``--resize fail`` would abort).
"""
import hashlib
import random
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from .blla_segmentation import polygon_crop
from .io import relative, sha256


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _child(element, name):
    return next((c for c in element if _local(c.tag) == name), None)


def read_page_xml(path):
    """Return ``(image_filename, [(line_id, polygon, text, custom)])`` in document order."""
    root = ET.parse(path).getroot()
    page = next(e for e in root.iter() if _local(e.tag) == "Page")
    lines = []
    for line in (e for e in page.iter() if _local(e.tag) == "TextLine"):
        coords = _child(line, "Coords")
        equiv = _child(line, "TextEquiv")
        unicode_ = _child(equiv, "Unicode") if equiv is not None else None
        if coords is None or unicode_ is None:
            continue
        points = [tuple(int(float(v)) for v in p.split(",")) for p in coords.get("points", "").split()]
        lines.append((line.get("id"), points, unicode_.text or "", line.get("custom", "")))
    return page.get("imageFilename"), lines


def skip_reason(text, custom, alphabet, nfd=True):
    if not text.strip():
        return "vazia"
    if "??" in text:
        return "duvida_marcada"
    if "unclear" in custom:
        return "unclear"
    if alphabet is not None:
        form = unicodedata.normalize("NFD" if nfd else "NFC", text)
        if any(ch not in alphabet for ch in form):
            return "caractere_fora_do_alfabeto"
    return None


def import_pairs(page_dir, image_dir, output_dir, root, alphabet=None, per_page=2, limit=None, seed=1831,
                 document_id="externo", label_source="externo_page_xml"):
    """Sample up to ``per_page`` usable lines per page (more hands, fewer lines each)."""
    root, output_dir = Path(root), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    rng = random.Random(seed)
    pairs, skipped = [], {}
    for xml in sorted(Path(page_dir).glob("*.xml")):
        image_name, lines = read_page_xml(xml)
        usable = []
        for line_id, polygon, text, custom in lines:
            reason = skip_reason(text, custom, alphabet)
            if reason or len(polygon) < 3:
                skipped[reason or "poligono"] = skipped.get(reason or "poligono", 0) + 1
                continue
            usable.append((line_id, polygon, text))
        rng.shuffle(usable)
        chosen = usable[:per_page]
        if not chosen:
            continue
        image_path = Path(image_dir) / image_name
        with Image.open(image_path) as opened:
            image = opened.convert("RGB")
        for line_id, polygon, text in chosen:
            box, crop = polygon_crop(image, polygon)
            if box[2] - box[0] < 20 or box[3] - box[1] < 8:
                skipped["recorte_minimo"] = skipped.get("recorte_minimo", 0) + 1
                continue
            name = hashlib.sha256(f"{xml.name}|{line_id}".encode()).hexdigest()[:20]
            path = output_dir / f"x_{name}.png"
            crop.save(path)
            pairs.append({"crop_image": relative(path, root), "text": " ".join(text.split()), "document_id": document_id,
                          "split": "train", "label_source": label_source, "source_page_xml": xml.name,
                          "source_image": image_name, "source_image_sha256": sha256(image_path), "source_line_id": line_id})
    rng.shuffle(pairs)
    if limit:
        pairs = pairs[:limit]
    return pairs, skipped
