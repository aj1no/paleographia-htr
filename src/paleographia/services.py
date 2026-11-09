import copy
import hashlib
import io
import json
import threading
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .data import Line, Page, bbox_valid, check_reviewer
from .io import now, relative, run_id, safe_path, sha256, write_json, write_jsonl
from .backends import create_recognizer
from .segmentation import crop_line, segment_pages


class Conflict(ValueError):
    pass


# Fields whose change means the reviewer is attesting something new.
ATTESTED_LINE_FIELDS = ("text_diplomatic", "bbox_xyxy", "reading_order", "region_id", "reviewer",
                        "review_status", "geometry_status", "reference_kind", "reference_source", "reference_pages")


class ReviewService:
    """One local process, serialized model access and immutable state revisions."""
    def __init__(self, root, config, recognizer=None):
        self.root = Path(root).resolve()
        self.config = config
        self.workspace = safe_path(self.root, config["paths"]["workspace"])
        self.lock = threading.RLock()
        self.recognizer = recognizer or create_recognizer(config, self.root)

    def state(self):
        pointer = self.workspace / "current.json"
        if not pointer.exists():
            return {"revision": None, "pages": [], "lines": [], "predictions": []}
        current = json.loads(pointer.read_text(encoding="utf-8"))["revision"]
        return json.loads((self.workspace/"revisions"/(current+".json")).read_text(encoding="utf-8"))

    def save(self, state, action):
        revision = run_id()
        result = dict(state, revision=revision, parent_revision=state.get("revision"), action=action, saved_at=now())
        write_json(self.workspace/"revisions"/(revision+".json"), result)
        write_json(self.workspace/"current.json", {"revision": revision})
        return result

    def import_catalog(self, pages, lines):
        from .data import validate
        report = validate(lines, self.root, "catalog", pages)
        if not report["valid"]:
            raise ValueError("; ".join(report["errors"]))
        for page in pages:
            Page.model_validate(page)
            if sha256(safe_path(self.root, page["source_image"])) != page["source_sha256"]:
                raise ValueError("Fonte de página divergente.")
        with self.lock:
            state = self.state()
            if state["pages"] or state["lines"]:
                raise Conflict("Importe catálogo em workspace vazio para preservar a revisão existente.")
            return self.save(dict(state, pages=pages, lines=lines), "import_catalog")

    def import_upload(self, content, original_name, dpi=200, max_pages=30):
        """Import an uploaded file: JPEG/PNG/TIFF as is, other images as PNG, and each PDF page as an image.

        Returns the list of imported pages (one per PDF page). PDF pages are rendered at ``dpi``
        with PyMuPDF (the ``pdf`` extra); nothing else in the upload is kept.
        """
        name = Path(original_name or "imagem").name
        if not content:
            raise ValueError("Envie um arquivo não vazio.")
        if content[:5] == b"%PDF-":
            try:
                import pymupdf
            except ImportError as exc:
                raise ValueError("Para importar PDF, instale o extra pdf (pymupdf).") from exc
            try:
                document = pymupdf.open(stream=content, filetype="pdf")
            except Exception as exc:  # pymupdf raises its own error types
                raise ValueError("PDF inválido.") from exc
            with document:
                if document.page_count == 0:
                    raise ValueError("O PDF não tem páginas.")
                if document.page_count > max_pages:
                    raise ValueError(f"O PDF tem {document.page_count} páginas; envie até {max_pages} por vez.")
                stem = Path(name).stem
                return [self.import_image(page.get_pixmap(dpi=dpi).tobytes("png"),
                                          f"{stem} · página {number} do PDF.png")
                        for number, page in enumerate(document, start=1)]
        try:
            with Image.open(io.BytesIO(content)) as opened:
                fmt = opened.format
                if fmt not in {"JPEG", "PNG", "TIFF"}:
                    if opened.width * opened.height > 40_000_000:
                        raise ValueError("Imagem excede 40 milhões de pixels.")
                    buffer = io.BytesIO()
                    opened.convert("RGB").save(buffer, "PNG")
                    content, name = buffer.getvalue(), Path(name).stem + ".png"
        except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
            raise ValueError("Formato não reconhecido. Envie uma imagem (JPEG, PNG, TIFF, WEBP…) ou um PDF.") from exc
        return [self.import_image(content, name)]

    def import_image(self, content, original_name):
        if not content or len(content) > 25 * 1024 * 1024:
            raise ValueError("Envie imagem não vazia de até 25 MiB.")
        try:
            with Image.open(io.BytesIO(content)) as opened:
                if opened.width * opened.height > 40_000_000:
                    raise ValueError("Imagem excede 40 milhões de pixels.")
                if opened.format not in {"JPEG", "PNG", "TIFF"}:
                    raise ValueError("Formatos aceitos: JPEG, PNG, TIFF.")
                opened.load()
                width, height, fmt = opened.width, opened.height, opened.format
        except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
            raise ValueError("Imagem inválida.") from exc
        checksum = hashlib.sha256(content).hexdigest()
        page_id = "p_" + checksum[:20]
        with self.lock:
            state = self.state()
            previous = next((p for p in state["pages"] if p["page_id"] == page_id), None)
            if previous:
                return previous
            path = self.root/"data/raw/uploads"/(page_id+{"JPEG":".jpg", "PNG":".png", "TIFF":".tif"}[fmt])
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and sha256(path) != checksum:
                raise Conflict("Colisão na identificação da fonte.")
            if not path.exists():
                path.write_bytes(content)
            cached = self._demo_cache(checksum)
            if cached and not any(p["page_id"] == cached["page"]["page_id"] for p in state["pages"]):
                # Demonstração: o fólio já foi processado antes; as linhas e a leitura do modelo
                # voltam na hora, marcadas como vindas desse processamento anterior.
                page = dict(cached["page"], source_image=relative(path, self.root))
                state["pages"].append(page)
                state["lines"].extend(cached["lines"])
                state["predictions"].extend(cached["predictions"])
                self.save(state, "import_image_demo_cache")
                return dict(page, from_demo_cache=True, cached_lines=len(cached["lines"]),
                            cached_at=cached.get("processed_at"))
            page = Page(page_id=page_id, document_id="unassigned_"+page_id, folio_id=page_id,
                        source_image=relative(path, self.root), original_name=Path(original_name or "imagem").name,
                        width=width, height=height, source_sha256=checksum).model_dump()
            state["pages"].append(page)
            self.save(state, "import_image")
            return page

    def _demo_cache(self, checksum):
        """Pre-processed folio for demonstrations, keyed by the image SHA-256 (``[demo] cache_dir``)."""
        directory = self.config.get("demo", {}).get("cache_dir")
        if not directory:
            return None
        entry = safe_path(self.root, directory)/f"{checksum}.json"
        if not entry.is_file():
            return None
        cached = json.loads(entry.read_text(encoding="utf-8"))
        if cached.get("page", {}).get("source_sha256") != checksum:
            return None
        if not all(safe_path(self.root, l["crop_image"]).is_file() for l in cached["lines"]):
            return None
        return cached

    def get_page(self, page_id, state=None):
        return next((p for p in (state or self.state())["pages"] if p["page_id"] == page_id), None)

    def segment(self, page_id, method=None):
        method = method or self.config.get("segmentation", {}).get("default_method", "opencv")
        with self.lock:
            state = self.state()
            page = self.get_page(page_id, state)
            if page is None:
                raise KeyError(page_id)
            if any(l["page_id"] == page_id for l in state["lines"]):
                raise Conflict("A página já tem linhas. Ajuste ou rejeite os recortes existentes para preservar suas revisões.")
            output = self.workspace/"segments"/run_id()
            if method == "kraken_blla":
                from .blla_segmentation import segment_page_blla
                lines = segment_page_blla(page, output, self.root, self.config.get("recognition", {}))
            else:
                lines, _ = segment_pages([page], method, self.config, output, self.root)
            state["lines"].extend(lines)
            self.save(state, "segment")
            if method == "kraken_blla" and self.rejoin_blla_pieces(page_id):
                lines = sorted((l for l in self.state()["lines"] if l["page_id"] == page_id),
                               key=lambda l: l["reading_order"])
            return lines

    def rejoin_blla_pieces(self, page_id, max_gap=40):
        """Glue the first/last words that blla cut off back onto their line, before anyone reads them.

        Only lines with no human work (no text, never reviewed) are touched; the replaced lines stay
        in the revision history and the new line lists them in ``merged_from``.
        """
        from .blla_segmentation import rejoin_line, side_fragments

        def untouched(line):
            return (not line.get("text_diplomatic") and not line.get("reviewed_at")
                    and line["review_status"] == "pending_review" and line["geometry_status"] == "pending_review")
        with self.lock:
            state = self.state()
            page = self.get_page(page_id, state)
            if page is None:
                raise KeyError(page_id)
            lines = [l for l in state["lines"] if l["page_id"] == page_id and l["review_status"] != "rejected"]
            by_id = {l["line_id"]: l for l in lines if l.get("blla_geometry", {}).get("boundary")}
            groups = {main: [p for p in pieces if p["line_id"] in by_id and untouched(p)]
                      for main, pieces in side_fragments(list(by_id.values()), max_gap).items()
                      if untouched(by_id[main])}
            groups = {main: pieces for main, pieces in groups.items() if pieces}
            if not groups:
                return []
            output = self.workspace/"segments"/run_id()
            rejoined = [rejoin_line(page, by_id[main], pieces, output, self.root) for main, pieces in groups.items()]
            gone = {lid for line in rejoined for lid in line["merged_from"]}
            # Cropping takes a moment; apply to the newest revision and only if nobody touched those lines.
            fresh = self.state()
            current = {l["line_id"]: l for l in fresh["lines"]}
            if not all(lid in current and untouched(current[lid]) for lid in gone):
                raise Conflict("Linhas alteradas durante a junção; nada foi gravado. Tente de novo.")
            fresh["lines"] = [l for l in fresh["lines"] if l["line_id"] not in gone] + rejoined
            self.save(fresh, "rejoin_blla_pieces")
            return rejoined

    def join_lines(self, line_id, other_id, expected_revision=None):
        """Join two lines of the same page into one crop, at the reviewer's request.

        Refuses validated lines (the reviewer must reopen them first). Any draft text is kept, in
        left-to-right order. The new line takes the reading order of the wider line; both originals
        stay in the revision history and are listed in ``merged_from``.
        """
        from .blla_segmentation import rejoin_line
        with self.lock:
            state = self.state()
            if expected_revision and state["revision"] != expected_revision:
                raise Conflict("A revisão mudou; recarregue antes de juntar.")
            if line_id == other_id:
                raise ValueError("Escolha duas linhas diferentes.")
            byid = {l["line_id"]: l for l in state["lines"]}
            if line_id not in byid or other_id not in byid:
                raise KeyError(other_id if line_id in byid else line_id)
            a, b = byid[line_id], byid[other_id]
            if a["page_id"] != b["page_id"]:
                raise ValueError("As linhas são de fólios diferentes.")
            if "validated" in (a["review_status"], b["review_status"]):
                raise Conflict("Uma das linhas já está validada. Volte-a para pendente antes de juntar.")
            if "rejected" in (a["review_status"], b["review_status"]):
                raise ValueError("Uma das linhas foi rejeitada.")
            main, piece = (a, b) if (a["bbox_xyxy"][2] - a["bbox_xyxy"][0]) >= (b["bbox_xyxy"][2] - b["bbox_xyxy"][0]) else (b, a)
            page = self.get_page(a["page_id"], state)
            joined = rejoin_line(page, main, [piece], self.workspace/"segments"/run_id(), self.root)
            textos = [l.get("text_diplomatic") or "" for l in sorted((a, b), key=lambda l: l["bbox_xyxy"][0])]
            joined.update(region_id=main["region_id"],
                          text_diplomatic=" ".join(t.strip() for t in textos if t.strip()) or None,
                          exclusion_reason=None)
            state["lines"] = [l for l in state["lines"] if l["line_id"] not in (line_id, other_id)] + [joined]
            self.save(state, "join_lines")
            return joined

    def add_line(self, page_id, box, region_id="page", reading_order=0):
        with self.lock:
            state = self.state()
            page = self.get_page(page_id, state)
            if not page:
                raise KeyError(page_id)
            if any(l["page_id"] == page_id and l["region_id"] == region_id and l["reading_order"] == reading_order and l["review_status"] != "rejected" for l in state["lines"]):
                raise Conflict("Ordem de leitura já utilizada nessa região.")
            output = self.workspace/"crops"/run_id()
            output.mkdir(parents=True)
            line = crop_line(page, box, reading_order, region_id, output, self.root, "human", "manual_"+run_id())
            # Annotation identity persists across later geometry revisions.
            line["line_id"] = "l_"+uuid.uuid4().hex[:20]
            state["lines"].append(line)
            self.save(state, "add_line")
            return line

    def update_page(self, page_id, changes, expected_revision=None):
        with self.lock:
            state = self.state()
            if expected_revision and state["revision"] != expected_revision:
                raise Conflict("A revisão mudou; recarregue antes de salvar.")
            page = self.get_page(page_id, state)
            if page is None:
                raise KeyError(page_id)
            allowed = {"document_id", "folio_id", "side", "correspondence_status", "reviewer", "source_url",
                       "credits", "usage_conditions", "transcribed_coverage"}
            if set(changes)-allowed:
                raise ValueError("Campo de página não editável.")
            updated = copy.deepcopy(dict(page, **changes))
            identity_fields = {"document_id", "folio_id", "side", "correspondence_status", "reviewer"}
            if any(updated.get(key) != page.get(key) for key in identity_fields):
                updated["reviewed_at"] = now() if updated["correspondence_status"] == "validated" else None
            if updated["correspondence_status"] == "validated":
                if updated["document_id"].startswith("unassigned_"):
                    raise ValueError("Identifique o documento antes de validar.")
                check_reviewer(updated)
            previous_regions = {c["region_id"]: c for c in page["transcribed_coverage"]}
            region_ids = set()
            for coverage in updated["transcribed_coverage"]:
                if not bbox_valid(coverage.get("bbox_xyxy"), updated["width"], updated["height"]) or not coverage.get("region_id"):
                    raise ValueError("Cobertura da região inválida.")
                if coverage["region_id"] in region_ids:
                    raise ValueError("Nome de região repetido.")
                region_ids.add(coverage["region_id"])
                if coverage != previous_regions.get(coverage["region_id"]):
                    if coverage.get("review_status") == "validated":
                        coverage["reviewer"] = updated["reviewer"]
                        coverage["reviewed_at"] = now()
                        check_reviewer(coverage)
                    else:
                        coverage["reviewer"] = None
                        coverage["reviewed_at"] = None
                elif coverage.get("review_status") == "validated":
                    check_reviewer(coverage)
                if coverage.get("reference_source") and not safe_path(self.root, coverage["reference_source"]).is_file():
                    raise ValueError("Fonte da cobertura ausente.")
                if not all(type(n) is int and n > 0 for n in coverage.get("reference_pages", [])):
                    raise ValueError("Páginas de referência inválidas.")
            removed = set(previous_regions) - region_ids
            if any(l["page_id"] == page_id and l["region_id"] in removed for l in state["lines"]):
                raise Conflict("A região tem linhas associadas. Reatribua essas linhas antes de remover ou renomear a região.")
            Page.model_validate(updated)
            for line in state["lines"]:
                if line["page_id"] == page_id and any(updated[key] != page[key] for key in ("document_id", "folio_id")):
                    line.update(document_id=updated["document_id"], folio_id=updated["folio_id"], split_group=updated["document_id"], split=None)
            state["pages"] = [updated if p["page_id"] == page_id else p for p in state["pages"]]
            self.save(state, "update_page")
            return updated

    def update_line(self, line_id, changes, expected_revision=None):
        with self.lock:
            state = self.state()
            if expected_revision and state["revision"] != expected_revision:
                raise Conflict("A revisão mudou; recarregue antes de salvar.")
            line = next((l for l in state["lines"] if l["line_id"] == line_id), None)
            if line is None:
                raise KeyError(line_id)
            allowed = {"bbox_xyxy", "reading_order", "region_id", "text_diplomatic", "text_modernized",
                       "reference_source", "reference_pages", "reference_kind", "review_status", "reviewer",
                       "geometry_status", "exclusion_reason", "lexical_assistance"}
            if set(changes)-allowed:
                raise ValueError("Campo de linha não editável.")
            updated = dict(line, **changes)
            if "lexical_assistance" in changes:
                from .lexicon import append_assistance
                updated["lexical_assistance"] = append_assistance(
                    self.root, self.config.get("lexicon", {}).get("directory", "data/lexicon"),
                    line.get("lexical_assistance", []), changes["lexical_assistance"])
            if any(l["line_id"] != line_id and l["review_status"] != "rejected" and l["page_id"] == updated["page_id"] and l["region_id"] == updated["region_id"] and l["reading_order"] == updated["reading_order"] for l in state["lines"]):
                raise Conflict("Ordem de leitura duplicada.")
            if updated["bbox_xyxy"] != line["bbox_xyxy"]:
                page = self.get_page(line["page_id"], state)
                output = self.workspace/"crops"/run_id()
                output.mkdir(parents=True)
                crop = crop_line(page, updated["bbox_xyxy"], updated["reading_order"], updated["region_id"], output, self.root, "human", "manual_"+run_id())
                updated.update(crop_image=crop["crop_image"], transform_id=crop["transform_id"], split=None)
                if "crop_sha256" in updated:
                    updated["crop_sha256"] = sha256(safe_path(self.root, crop["crop_image"]))
                updated["geometry_status"] = changes.get("geometry_status", "pending_review")
                updated["review_status"] = changes.get("review_status", "pending_review")
            if updated["review_status"] == "validated" or updated["geometry_status"] == "validated":
                # reviewed_at dates the human attestation. Saving unrelated fields
                # (modernized text, exclusion note, lexical history) keeps it.
                if not line.get("reviewed_at") or any(updated.get(key) != line.get(key) for key in ATTESTED_LINE_FIELDS):
                    updated["reviewed_at"] = now()
                check_reviewer(updated)
            else:
                updated["reviewed_at"] = None
            if updated["review_status"] == "validated" and (not updated.get("text_diplomatic", "") or not updated["text_diplomatic"].strip() or updated["reference_kind"] != "human_diplomatic"):
                raise ValueError("Validar exige transcrição paleográfica humana; edição modernizada não basta.")
            if updated.get("reference_source") and not safe_path(self.root, updated["reference_source"]).is_file():
                raise ValueError("Fonte da edição não encontrada.")
            Line.model_validate(updated)
            state["lines"] = [updated if l["line_id"] == line_id else l for l in state["lines"]]
            self.save(state, "update_line")
            return updated

    def recognize_page(self, page_id):
        from .recognition import recognize_lines
        with self.lock:
            state = self.state()
            if self.get_page(page_id, state) is None:
                raise KeyError(page_id)
            lines = [l for l in state["lines"] if l["page_id"] == page_id and l["review_status"] != "rejected"]
            if not lines:
                raise ValueError("Ajuste/crie os recortes antes de reconhecer.")
            from .data import require_valid
            require_valid(lines, self.root, "catalog", state["pages"])
            output = self.workspace/"predictions"/(run_id()+".jsonl")
            predictions = recognize_lines(lines, self.recognizer, output, self.root)
            state["predictions"].extend(predictions)
            self.save(state, "recognize")
            return predictions

    def export(self, output):
        with self.lock:
            state = self.state()
            output = Path(output)
            if output.exists():
                raise ValueError("Exportação exige diretório novo.")
            write_jsonl(output/"pages.jsonl", state["pages"])
            write_jsonl(output/"lines.jsonl", state["lines"])
            write_jsonl(output/"predictions.jsonl", state["predictions"])
            write_json(output/"provenance.json", {"revision": state["revision"], "exported_at": now()})
            return output
