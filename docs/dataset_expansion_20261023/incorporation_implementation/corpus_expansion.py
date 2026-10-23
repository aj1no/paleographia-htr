"""Offline, additive incorporation of the supplied v0.2 source corpus.

Package scripts are preserved as sources and are never executed. All generated
paths are relative to the project root. PDF extraction creates candidates only.
"""
import hashlib
import importlib.metadata
import json
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from PIL import Image

from .data import Page, validate
from .io import read_jsonl, relative, safe_path, sha256, write_json, write_jsonl

PACKAGE = "PaleographIA_Corpus_Expandido_v0_2_20261023"
ARCHIVE_SHA256 = "62e1c3da154b4dcc9bdf63715c01eba788d7a2f6f5cce7a973938755772e25bd"
# Visually inspected combined PDFs: these pages contain manuscript reproductions.
MANUSCRIPT_PAGES = {
    "3348a51ef10d9d1b": [5, 6], "3c0132189f5574d5": [4],
    "479bc2535feed70e": [6, 7, 8], "500a24d6a2ea8b93": [5],
    "ba07a3fb9769e23b": [4], "c7ffb34ac9b8c735": [9, 10, 11, 12],
    "e1c779a4713340ad": list(range(1, 10)),
}
FOLIOS = {"7d9c6e3e9a0728b1": ("4", "unknown"),
          "37eec7f6ae756ba4": ("113v", "verso"), "bfa219c731ebc77b": ("114r", "recto"),
          "413d1502555f62d4": ("100r", "recto"), "2d0bc739ae48eeda": ("100v", "verso"),
          "c001a2648e01c5c4": ("101r", "recto"), "3f35cc69b6c96ee1": ("91r", "recto")}
CREDITS = {
    "carta_jose_gomes_1767": "Transcrição e edição: Júlia Munhoz e Matheus Bellodi (AHMJ). Revisão: Isabella Ferraro (AHMJ).",
    "contrato_livro12_1763": "Transcrição e edição: Gilson Santos (AHMJ). Revisão: Isabella Ferraro (AHMJ).",
    "contrato_livro13_1763": "Transcrição e edição: Gilson Santos (AHMJ). Revisão: Isabella Ferraro (AHMJ).",
    "pagamento_thomas_pardo": "Transcrição e edição: Gilson Santos (AHMJ). Revisão: Isabella Ferraro (AHMJ).",
    "posturas_1831": "Transcrição e edição: Paulo Vicentini (AHMJ). Revisão: Isabella Ferraro e Gilson Santos (AHMJ).",
    "sessao_1795": "Transcrição e edição: Gilson Santos Lino. Revisão: Isabella Ferraro (AHMJ).",
    "traslado_criacao_vila": "Ana Caroline C. Miranda, paleógrafa responsável; Thiago Paschoal, paleógrafo revisor. Memorabilia Paleografia e Diplomática.",
}


def document_group(candidate):
    return {"traslado_criacao_vila": "tt_pbr_0004_026_traslado_1767",
            "posturas_1831": "jundiai_atas_sessao_1831-07-11"}.get(candidate, candidate)


def _member(name):
    p = PurePosixPath(name)
    if (not name or "\\" in name or ":" in name or p.is_absolute()
            or ".." in p.parts or p.as_posix() != name):
        raise ValueError("Caminho inseguro no corpus: " + name)
    return name


def incorporate(archive, source_dir, output_dir, root=Path.cwd()):
    """Validate the exact supplied archive before writing any source bytes."""
    root, archive = Path(root).resolve(), Path(archive)
    source_dir, output_dir = safe_path(root, source_dir), safe_path(root, output_dir)
    if source_dir.exists() or output_dir.exists():
        raise ValueError("Incorporação exige duas pastas novas; preserve as anteriores.")
    if source_dir == output_dir or source_dir in output_dir.parents or output_dir in source_dir.parents:
        raise ValueError("Pastas de fontes e derivados devem ser separadas.")
    if sha256(archive) != ARCHIVE_SHA256:
        raise ValueError("SHA-256 do ZIP diferente da versão v0.2 recebida.")
    with zipfile.ZipFile(archive) as z:
        prefix = PACKAGE + "/"
        names = [e.filename for e in z.infolist() if not e.is_dir()]
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError("Membros duplicados no ZIP.")
        for name in names:
            _member(name)
            if not name.startswith(prefix):
                raise ValueError("Raiz inesperada no ZIP.")
        inventory_name = "INVENTARIO_EXPANDIDO_SHA256.json"
        inventory = json.loads(z.read(prefix + inventory_name))
        for name in inventory:
            _member(name)
        if {n[len(prefix):] for n in names} != set(inventory) | {inventory_name}:
            raise ValueError("Inventário incompleto do ZIP.")
        for name, digest in inventory.items():
            _member(name)
            if hashlib.sha256(z.read(prefix + name)).hexdigest() != digest:
                raise ValueError("Hash divergente no ZIP: " + name)
        source_dir.mkdir(parents=True)
        for name in names:
            path = safe_path(source_dir, name[len(prefix):])
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(z.read(name))
    output_dir.mkdir(parents=True)
    return index_sources(source_dir, output_dir, root, archive.name)


def index_sources(source_dir, output_dir, root, archive_name):
    from pypdf import PdfReader

    def rel(path):
        return relative(path, root)

    sources = read_jsonl(source_dir / "inventario_fontes.jsonl")
    origin = json.loads((source_dir / "inventario_origem_20261016.json").read_bytes())
    if len(sources) != 15 or {s["sha256"] for s in sources} != {s["sha256"] for s in origin["files"]}:
        raise ValueError("As 15 fontes não correspondem ao inventário de origem.")
    indexed, images, pdf_pages, embedded = [], [], [], []
    for s in sources:
        path = safe_path(source_dir, s["path"])
        if sha256(path) != s["sha256"] or path.stat().st_size != s["bytes"]:
            raise ValueError("Fonte alterada: " + s["path"])
        item = dict(s, path=rel(path), document_id=document_group(s["candidate_group"]),
                    transcription_type=s["kind"], credits=CREDITS[s["candidate_group"]],
                    credits_status="editorial_credit; not new line reviewer", independence_status="pending_review",
                    edition_source_ids=[r["source_id"] for r in sources if r["candidate_group"] == s["candidate_group"] and r["kind"] in {"modernized_edition", "published_paleographic_transcription"}])
        indexed.append(item)
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(path)
            for number, page in enumerate(reader.pages, 1):
                text_path = output_dir / "editorial" / s["source_id"] / f"p{number:03d}.txt"
                text_path.parent.mkdir(parents=True, exist_ok=True)
                text = page.extract_text() or ""
                text_path.write_text(text, encoding="utf-8", newline="\n")
                pdf_pages.append({"source_id": s["source_id"], "document_id": item["document_id"],
                                  "pdf_page": number, "text_raw_path": rel(text_path),
                                  "text_sha256": sha256(text_path), "characters": len(text),
                                  "labels_created": 0, "source_sha256": s["sha256"]})
                for i, obj in enumerate(page.images):
                    # Preserve all image objects, including logos; classify separately.
                    ipath = output_dir / "pdf_images" / s["source_id"] / f"p{number:03d}_i{i:02d}{Path(obj.name).suffix}"
                    ipath.parent.mkdir(parents=True, exist_ok=True)
                    ipath.write_bytes(obj.data)
                    with Image.open(ipath) as im:
                        w, h = im.size
                    candidate = number in MANUSCRIPT_PAGES.get(s["source_id"], []) and min(w, h) >= 200
                    entry = {"image_id": f"{s['source_id']}_p{number:03d}_i{i:02d}",
                             "candidate_group": s["candidate_group"], "document_id": item["document_id"],
                             "path": rel(ipath), "sha256": sha256(ipath), "width": w, "height": h,
                             "source_id": s["source_id"], "source_path": rel(path), "source_sha256": s["sha256"],
                             "pdf_page": number, "embedded_image_index": i,
                             "manuscript_candidate": candidate, "classification": "visual_page_inspection_v1"}
                    embedded.append(entry)
                    if candidate:
                        images.append(entry)
        else:
            with Image.open(path) as im:
                w, h = im.size
            images.append({"image_id": s["source_id"], "candidate_group": s["candidate_group"],
                           "document_id": item["document_id"], "path": rel(path), "sha256": s["sha256"],
                           "width": w, "height": h, "source_id": s["source_id"], "source_path": rel(path),
                           "source_sha256": s["sha256"], "pdf_page": None, "embedded_image_index": None,
                           "manuscript_candidate": True})
    # Multiple reproductions remain visible in occurrences; identical pixel content
    # shares a page identity. Different reproductions still share a document group.
    unique, pages = {}, []
    for im in images:
        with Image.open(safe_path(root, im["path"])) as opened:
            rgb = opened.convert("RGB")
            pixel_hash = hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()
        folio, side = FOLIOS.get(im["image_id"], (None, "unknown"))
        im.update(pixel_sha256=pixel_hash, folio_id=folio, side=side, review_status="pending_review",
                  folio_provenance="original_filename; visual correspondence pending" if folio else None)
        key = (im["document_id"], pixel_hash)
        page_id = "p_c02_" + hashlib.sha256((im["document_id"] + pixel_hash).encode()).hexdigest()[:16]
        im["page_id"] = page_id
        if key in unique:
            im["duplicate_of"] = unique[key]
            continue
        unique[key] = im["image_id"]
        pages.append(Page(page_id=page_id, document_id=im["document_id"], folio_id=folio or "unknown_" + page_id, side=side,
                          source_image=im["path"], original_name=Path(im["path"]).name,
                          width=im["width"], height=im["height"], source_sha256=im["sha256"],
                          candidate_group=im["candidate_group"], pdf_page=im["pdf_page"],
                          source_id=im["source_id"], credits=CREDITS[im["candidate_group"]],
                          folio_provenance=im["folio_provenance"],
                          catalog_url=next(s.get("catalog_url") for s in sources if s["source_id"] == im["source_id"])).model_dump())
    # Preserve the frozen core and its additive reconference, with no promotions.
    core_dir = source_dir / "nucleo_anotado_269r"
    samples = read_jsonl(core_dir / "amostras.jsonl")
    frozen = {r["line_id"]: r for r in read_jsonl(core_dir / "origem/linhas_congeladas.jsonl")}
    core = []
    for sample in samples:
        row = dict(frozen[sample["sample_id"]])
        row.update(source_image=rel(core_dir / sample["page_image_path"]),
                   crop_image=rel(core_dir / sample["image_path"]),
                   reference_source=rel(core_dir / sample["edition_path"]), split=None,
                   partition="development", text_published=sample["texto_publicado"],
                   reference_policy=sample["reference_policy"], historical_reservation=sample["ressalva_historica"],
                   subsequent_reconference=sample["reconferencia_posterior"],
                   frozen_sample=sample, crop_sha256=sample["crop_sha256"])
        if row["review_status"] != sample["estado_textual"] or row["geometry_status"] != sample["estado_geometria"]:
            raise ValueError("Estado divergente no núcleo histórico.")
        if sha256(safe_path(root, row["crop_image"])) != row["crop_sha256"]:
            raise ValueError("Recorte do núcleo alterado.")
        core.append(row)
    core_pages = read_jsonl(core_dir / "origem/paginas_congeladas.jsonl")
    for p in core_pages:
        p["source_image"] = rel(core_dir / "imagens/paginas/269r.jpg")
        for coverage in p["transcribed_coverage"]:
            coverage["reference_source"] = rel(core_dir / "apoio/edicao.pdf")
    report = validate(core, root, "catalog", core_pages)
    if not report["valid"]:
        raise ValueError(str(report["errors"]))
    for name, rows in [("sources", indexed), ("pdf_pages", pdf_pages), ("embedded_images", embedded),
                       ("image_occurrences", images), ("pages", pages), ("core_lines", core), ("core_pages", core_pages)]:
        write_jsonl(output_dir / (name + ".jsonl"), rows)
    groups = []
    for candidate in sorted({s["candidate_group"] for s in sources}):
        group = document_group(candidate)
        groups.append({"candidate_group": candidate, "document_id": group, "split_group": group,
                       "source_ids": [s["source_id"] for s in sources if s["candidate_group"] == candidate],
                       "image_occurrences": sum(i["document_id"] == group for i in images),
                       "unique_pixel_pages": sum(p["document_id"] == group for p in pages),
                       "independence_status": "pending_review", "scientific_split": None,
                       "partition": "development" if candidate in {"traslado_criacao_vila", "posturas_1831"} else "curation",
                       "historical_catalog": {"posturas_1831": "data/manifests/pages.jsonl",
                                              "traslado_criacao_vila": "data/manifests/traslado_269r/pages.jsonl"}.get(candidate),
                       "eligible_new_pairs": 0})
    write_json(output_dir / "partitions.json", {"status": "blocked_pending_independent_reviewed_groups",
               "random_partition": False, "test_reserved": True, "groups": groups,
               "note": "269r e todos os derivados do traslado já são desenvolvimento; não podem virar teste."})
    summary = {"archive_name": archive_name, "archive_sha256": ARCHIVE_SHA256,
               "package": PACKAGE, "source_root": rel(source_dir), "generated_root": rel(output_dir),
               "sources": len(sources), "candidate_groups": len(groups), "pdf_pages": len(pdf_pages),
               "embedded_image_objects": len(embedded), "manuscript_image_occurrences": len(images),
               "unique_pixel_pages": len(pages), "frozen_core_lines": len(core),
               "image_count_note": "Ocorrências/reproduções, não fólios independentes; JPEGs e PDFs podem codificar os mesmos manuscritos de maneiras diferentes.",
               "core_text_statuses": dict(Counter(r["review_status"] for r in core)),
               "historical_reservations": sum(r["historical_reservation"] for r in core),
               "new_human_validations": 0, "new_training_pairs": 0,
               "versions": {p: importlib.metadata.version(p) for p in ["pypdf", "Pillow"]},
               "validation": report}
    write_json(output_dir / "incorporation.json", summary)
    return summary


def restore(archive, catalog_dir, root=Path.cwd()):
    """Restore only absent source/image bytes; never rewrite committed catalogs."""
    from pypdf import PdfReader

    root, catalog = Path(root).resolve(), Path(catalog_dir)
    summary = json.loads((catalog / "incorporation.json").read_bytes())
    if sha256(archive) != ARCHIVE_SHA256 or summary["archive_sha256"] != ARCHIVE_SHA256:
        raise ValueError("ZIP diferente do corpus registrado.")
    source_dir = safe_path(root, summary["source_root"])
    restored = 0

    def put(path, content, expected):
        nonlocal restored
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError("Bytes divergentes na restauração: " + str(path))
        if path.exists():
            if sha256(path) != expected:
                raise ValueError("Arquivo existente divergente; restauração não sobrescreve: " + str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(content)
            restored += 1

    with zipfile.ZipFile(archive) as z:
        prefix = PACKAGE + "/"
        raw_inventory = z.read(prefix + "INVENTARIO_EXPANDIDO_SHA256.json")
        inventory = json.loads(raw_inventory)
        # Verify every entry before restoring anything.
        for name, expected in inventory.items():
            _member(name)
            if hashlib.sha256(z.read(prefix + name)).hexdigest() != expected:
                raise ValueError("Hash divergente no ZIP.")
        for name, expected in inventory.items():
            put(safe_path(source_dir, name), z.read(prefix + name), expected)
        put(source_dir / "INVENTARIO_EXPANDIDO_SHA256.json", raw_inventory, hashlib.sha256(raw_inventory).hexdigest())
    sources = {s["source_id"]: s for s in read_jsonl(catalog / "sources.jsonl")}
    readers = {}
    for image in read_jsonl(catalog / "embedded_images.jsonl"):
        sid = image["source_id"]
        if sid not in readers:
            source = safe_path(root, sources[sid]["path"])
            if sha256(source) != sources[sid]["sha256"]:
                raise ValueError("Fonte divergente no catálogo.")
            readers[sid] = PdfReader(source)
        content = readers[sid].pages[image["pdf_page"] - 1].images[image["embedded_image_index"]].data
        put(safe_path(root, image["path"]), content, image["sha256"])
    return {"status": "restored", "files_restored": restored, "catalogs_modified": False}


def prepare_review_block(catalog_dir, spec_path, output_dir, root=Path.cwd()):
    """Create reviewable candidates with editorial support, never adopted labels."""
    from PIL import ImageDraw
    from .segmentation import crop_line

    root, catalog_dir = Path(root).resolve(), Path(catalog_dir)
    output = Path(output_dir)
    if output.exists():
        raise ValueError("Bloco de revisão exige saída nova.")
    spec = json.loads(Path(spec_path).read_bytes())
    sources = read_jsonl(catalog_dir / "sources.jsonl")
    source = next(s for s in sources if s["source_id"] == spec["source_id"])
    reference = next(s for s in sources if s["source_id"] == spec["reference_source_id"])
    page = next(p for p in read_jsonl(catalog_dir / "pages.jsonl") if p["source_id"] == spec["source_id"])
    page = dict(page, credits=spec["credits"], folio_note=spec["folio_note"],
                transcribed_coverage=[{"region_id": spec["region_id"],
                                      "bbox_xyxy": [95, 325, 1030, 721],
                                      "reference_source": reference["path"], "reference_pages": [spec["reference_page"]],
                                      "review_status": "pending_review", "complete": False}])
    if sha256(safe_path(root, source["path"])) != source["sha256"] or sha256(safe_path(root, reference["path"])) != reference["sha256"]:
        raise ValueError("Fonte ou edição alterada.")
    output.mkdir(parents=True)
    lines = []
    with Image.open(safe_path(root, page["source_image"])) as im:
        overlay = im.convert("RGB")
    overlay.save(output / "context.jpg", quality=92)
    draw = ImageDraw.Draw(overlay)
    transform = sha256(spec_path)
    for order, candidate in enumerate(spec["lines"]):
        row = crop_line(page, candidate["bbox_xyxy"], order, spec["region_id"], output, root,
                        "manual_candidate_not_human_approved", transform)
        row.update(text_published=candidate["text_published"], text_modernized=candidate["text_published"],
                   text_diplomatic=None, reference_kind="modernized_edition", reference_policy="historical_visible_form_required",
                   target_policy="docs/transcription_policy.md", reference_source=reference["path"],
                   reference_pages=[spec["reference_page"]], published_line=candidate["published_line"],
                   edition_sha256=reference["sha256"], credits=spec["credits"],
                   alignment_status="candidate_pending_human_confirmation", coverage_status="pending_review",
                   visual_confirmation=False, reviewer=None, reviewed_at=None,
                   doubt="Conferir limites e leitura histórica; expansões, caixa e grafia da edição são modernizadas.",
                   editorial_expansions="Edição desenvolve abreviaturas sem marcação; não copiar automaticamente ao alvo.",
                   crop_sha256=sha256(safe_path(root, row["crop_image"])), source_pdf_page=None,
                   reproduction_pdf_page=4, reproduction_source_id=spec["reference_source_id"],
                   reproduction_correspondence_status="pending_review")
        lines.append(row)
        draw.rectangle(row["bbox_xyxy"], outline="#cc3300", width=3)
        draw.text((row["bbox_xyxy"][0] - 25, row["bbox_xyxy"][1]), str(order + 1), fill="#0033cc")
    overlay.save(output / "overlay.jpg", quality=92)
    report = validate(lines, root, "catalog", [page])
    if not report["valid"]:
        raise ValueError(str(report["errors"]))
    write_jsonl(output / "pages.jsonl", [page])
    write_jsonl(output / "lines.jsonl", lines)
    write_json(output / "review.json", {"status": "pending_human_review", "candidate_lines": len(lines),
               "new_validations": 0, "spec_path": relative(spec_path, root), "spec_sha256": transform,
               "catalog_validation": report, "folio_note": spec["folio_note"],
               "decisions_needed": ["Correspondência da imagem, fólio e lado", "Geometria de cada recorte e cobertura parcial",
                                    "Transcrição histórica visível de cada linha, com dúvidas e abreviaturas"],
               "published_text_origin": "Transcrito visualmente da edição, página 3; alinhamento ainda candidato."})
    return {"status": "pending_human_review", "candidate_lines": len(lines), "new_validations": 0}
