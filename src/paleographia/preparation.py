"""Prepare an explicit review sample without promoting text or geometry to reference."""
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .data import Line, Page, bbox_valid, require_valid
from .io import read_jsonl, safe_path, sha256, write_jsonl


def ensure_archive_reference(root, entry, destination):
    """Recover only the exact archived member, verifying bytes before writing."""
    import hashlib
    root = Path(root)
    target = safe_path(root, destination)
    if target.exists():
        if sha256(target) != entry["sha256"]:
            raise ValueError("Referência existente divergente; não foi sobrescrita.")
        return
    archive = safe_path(root, "data/raw/" + entry["archive"])
    if sha256(archive) != entry["archive_sha256"]:
        raise ValueError("Arquivo compactado divergente.")
    if archive.suffix.lower() == ".rar":
        import rarfile
        container = rarfile.RarFile(archive)
    else:
        import zipfile
        container = zipfile.ZipFile(archive)
    with container:
        content = container.read(entry["original_name"])
    if hashlib.sha256(content).hexdigest() != entry["sha256"]:
        raise ValueError("Membro extraído divergente; nada foi gravado.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(content)


def _png(image):
    buffer = io.BytesIO()
    image.info.clear()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def prepare_sample(root, spec, comparison):
    root = Path(root)
    source = safe_path(root, spec["source_image"])
    if sha256(source) != spec["source_sha256"]:
        raise ValueError("Imagem fonte divergente.")
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    if image.size != (spec["width"], spec["height"]):
        raise ValueError("Dimensões da fonte divergentes.")
    boxes, region = spec["boxes"], spec["region_bbox_xyxy"]
    if not bbox_valid(region, *image.size) or any(not bbox_valid(b, *image.size) for b in boxes):
        raise ValueError("Caixa candidata inválida.")
    if any(b[0] < region[0] or b[1] < region[1] or b[2] > region[2] or b[3] > region[3] for b in boxes):
        raise ValueError("Caixa fora da região candidata.")
    if len(comparison["body_lines"]) < len(boxes):
        raise ValueError("Trechos da edição insuficientes.")
    edition = spec["edition"]
    ensure_archive_reference(root, edition["archive_member"], edition["path"])
    document = spec["document_id"]
    common = {"reference_source": edition["path"], "reference_pages": [1]}
    coverage = dict(common, region_id=spec["region_id"], bbox_xyxy=region,
                    review_status="pending_review", complete=False, reviewer=None, reviewed_at=None,
                    scope="Somente as cinco primeiras linhas do corpo; não cobre o restante do 269r.")
    page = Page(page_id=spec["page_id"], document_id=document, folio_id="269r", side="recto",
                source_image=spec["source_image"], original_name=source.name,
                width=image.width, height=image.height, source_sha256=spec["source_sha256"],
                source_url=spec["source_url"], credits=edition["credits"],
                usage_conditions="Fonte histórica e edição com condições próprias; MIT refere-se ao código.",
                transcribed_coverage=[coverage], dates=spec["dates"],
                planned_reviewer=spec["planned_reviewer"], comparison_source=spec["comparison_source"],
                identification_basis="Identificação proposta no caderno; correspondência ainda pendente.",
                geometry_notes=spec["geometry_notes"]).model_dump()
    lines, outputs = [], {}
    for index, box in enumerate(boxes):
        origin = comparison["body_lines"][index]
        observations = [o for o in comparison.get("human_observations", [])
                        if index + 1 in o["comparison_lines"]]
        path = spec["image_directory"] + f"/linha_{index + 1:02d}.png"
        published = dict(common, kind="published_paleographic_transcription",
                         text=origin["published_text"], sha256=edition["archive_member"]["sha256"],
                         credits=edition["credits"], human_observations=observations,
                         assisted_proposal=origin.get("current_discussion_display", origin["published_text"]),
                         note="Texto publicado de apoio; confirmações parciais não validam a linha inteira.")
        line = Line(line_id=f"l_traslado_269r_body_{index + 1:02d}", page_id=spec["page_id"],
                    document_id=document, folio_id="269r", region_id=spec["region_id"],
                    reading_order=index, source_image=spec["source_image"], crop_image=path,
                    bbox_xyxy=box, source_width=image.width, source_height=image.height,
                    source_sha256=spec["source_sha256"], split_group=document,
                    transform_id=spec["transform_id"], **common,
                    published_reference=published, comparison_line=index + 1,
                    dates=spec["dates"], planned_reviewer=spec["planned_reviewer"],
                    context_image=spec["context_image"], geometry_notes=spec["geometry_notes"]).model_dump()
        lines.append(line)
        outputs[path] = _png(image.crop(box))
    block = image.crop(region)
    outputs[spec["context_image"]] = _png(block.copy())
    draw = ImageDraw.Draw(block)
    font = ImageFont.load_default(size=18)
    for index, (x1, y1, x2, y2) in enumerate(boxes, 1):
        bounds = (x1-region[0], y1-region[1], x2-region[0]-1, y2-region[1]-1)
        draw.rectangle(bounds, outline="#d42929", width=2)
        draw.rectangle((bounds[0], bounds[1], bounds[0]+24, bounds[1]+24), fill="white")
        draw.text((bounds[0]+3, bounds[1]), str(index), font=font, fill="#b80000")
    outputs[spec["overlay_image"]] = _png(block)
    # Preflight the entire set before writing; repeat never overwrites human edits.
    manifests = [(spec["pages_path"], [page]), (spec["lines_path"], lines)]
    existing = [safe_path(root, p).exists() for p, _ in manifests]
    if any(existing) and not all(existing):
        raise ValueError("Catálogo parcial existente; escolha outra saída, sem sobrescrever.")
    for path, expected in manifests:
        target = safe_path(root, path)
        if target.exists() and read_jsonl(target) != expected:
            raise ValueError("Catálogo contém revisão ou preparação diferente; não foi sobrescrito.")
    for path, content in outputs.items():
        target = safe_path(root, path)
        if target.exists():
            with Image.open(target) as prior, Image.open(io.BytesIO(content)) as expected:
                if prior.size != expected.size or prior.convert("RGB").tobytes() != expected.tobytes():
                    raise ValueError("Imagem existente divergente; não foi sobrescrita.")
    for path, content in outputs.items():
        target = safe_path(root, path)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(content)
    for path, expected in manifests:
        target = safe_path(root, path)
        if not target.exists():
            write_jsonl(target, expected)
    require_valid(lines, root, "catalog", [page])
    return {"pages": 1, "lines": len(lines), "status": "pending_review",
            "preserved_existing_catalog": all(existing)}
