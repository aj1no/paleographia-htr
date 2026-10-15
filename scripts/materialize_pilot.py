"""Rebuild only missing crops from versioned boxes; never overwrite sources/review."""
import argparse
from pathlib import Path

from PIL import Image

from paleographia.data import Line, bbox_valid, require_valid
from paleographia.io import read_jsonl, safe_path, sha256


def materialize(pages, lines, root):
    created = existing = 0
    for page in pages:
        source = safe_path(root, page["source_image"])
        if sha256(source) != page["source_sha256"]:
            raise ValueError("Fonte ausente/alterada; extraia o arquivo original correto.")
        with Image.open(source) as opened:
            image = opened.convert("RGB")
            image.info.clear()
            if image.size != (page["width"], page["height"]):
                raise ValueError("Dimensões da fonte divergentes.")
            for line in [r for r in lines if r["page_id"] == page["page_id"]]:
                Line.model_validate(line)
                if line["source_image"] != page["source_image"] or line["source_sha256"] != page["source_sha256"]:
                    raise ValueError("Associação inconsistente.")
                if not bbox_valid(line["bbox_xyxy"], *image.size) or not line["crop_image"]:
                    raise ValueError("Linha sem geometria/caminho de recorte.")
                crop = image.crop(line["bbox_xyxy"])
                path = safe_path(root, line["crop_image"])
                if path.exists():
                    with Image.open(path) as prior:
                        if prior.size != crop.size or prior.convert("RGB").tobytes() != crop.tobytes():
                            raise ValueError(f"Recorte existente diverge da fonte/caixa: {path}; não foi sobrescrito.")
                    existing += 1
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("xb") as output:
                        crop.save(output, format="PNG")
                    created += 1
    require_valid(lines, root, "catalog", pages)
    return {"created": created, "existing_unchanged": existing}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default="data/manifests/pages.jsonl")
    parser.add_argument("--lines", default="data/manifests/lines.jsonl")
    args = parser.parse_args()
    print(materialize(read_jsonl(args.pages), read_jsonl(args.lines), Path.cwd()))


if __name__ == "__main__":
    main()
