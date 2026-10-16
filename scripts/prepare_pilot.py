"""Reproducible candidate catalog from the inspected repository archives.

Run after `extract` + `inventory`. This never validates a source or transcript.
"""
import argparse
import json
from pathlib import Path

from paleographia.config import load_config
from paleographia.data import Page
from paleographia.io import read_jsonl, relative, write_json, write_jsonl
from paleographia.segmentation import segment_pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted", default="data/raw/import_20261015")
    parser.add_argument("--inventory", default="data/manifests/inventory.jsonl")
    parser.add_argument("--output-pages", default="data/manifests/pages.jsonl")
    parser.add_argument("--output-lines", default="data/manifests/lines.jsonl")
    parser.add_argument("--output-dir", default="data/processed/pilot_initial")
    args = parser.parse_args()
    if Path(args.output_pages).exists() or Path(args.output_lines).exists():
        raise ValueError("Manifests do piloto já existem. Escolha novas saídas para preservar revisões.")
    root = Path.cwd()
    extracted = Path(args.extracted)
    extraction = json.loads((extracted/"extraction.json").read_text(encoding="utf-8"))
    sources = {relative(extracted/r["output"], root): r for r in extraction}
    candidates = {
        "6e82cef18b04_198b675a9b65d183.jpg": ("jundiai_atas_1831_f100r", "recto", [3]),
        "6e82cef18b04_32db5d33c13da16a.jpg": ("jundiai_atas_1831_f100v", "verso", [3, 4]),
        "6e82cef18b04_25e7dfc19b66631a.jpg": ("jundiai_atas_1831_f101r", "recto", [4, 5]),
    }
    # These names identify exact archive members inspected on 2026-10-15, not order.
    edition = relative(extracted/"6e82cef18b04_094cbf86c7ec88ea.pdf", root)
    pages = []
    for page in read_jsonl(args.inventory):
        candidate = candidates.get(Path(page["source_image"]).name)
        if not candidate:
            continue
        folio_id, side, reference_pages = candidate
        page.update(document_id="jundiai_atas_sessao_1831-07-11", folio_id=folio_id, side=side,
                    original_name=sources[page["source_image"]]["original_name"].split("/")[-1],
                    archive_provenance=sources[page["source_image"]],
                    reference_candidates=[{"reference_source": edition, "reference_pages": reference_pages,
                     "reference_kind": "modernized_edition", "review_status": "pending_review",
                     "note": "100r: edição começa na linha editorial 17; cobertura geométrica ainda não delimitada." if side == "recto" and "100r" in folio_id else "Conferir limites da cobertura e identidade documental."}])
        pages.append(Page.model_validate(page).model_dump())
    if len(pages) != 3:
        raise ValueError("Os três membros exatos do arquivo inspecionado não foram encontrados.")
    config = load_config()
    lines, timings = segment_pages(pages, "opencv", config, args.output_dir, root)
    write_jsonl(args.output_pages, pages)
    write_jsonl(args.output_lines, lines)
    write_json(Path(args.output_dir)/"pilot_status.json", {"pages": len(pages), "candidate_crops": len(lines),
               "human_validated_lines": 0, "target": "30–50 linhas após revisão", "timings": timings,
               "evaluation": "blocked_human_review", "training": "blocked_human_review_and_single_document"})
    print(json.dumps({"pages": len(pages), "candidate_crops": len(lines), "human_validated_lines": 0}))


if __name__ == "__main__":
    main()
