"""Canonical data, explicit associations and conservative validation."""
import random
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .io import read_jsonl, relative, safe_path, sha256, write_json, write_jsonl

Review = Literal["pending_review", "validated", "rejected"]


class Record(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


class Page(Record):
    page_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    document_id: str = Field(min_length=1)
    folio_id: str = Field(min_length=1)
    side: Literal["recto", "verso", "unknown"] = "unknown"
    source_image: str
    original_name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    correspondence_status: Review = "pending_review"
    reviewer: str | None = None
    reviewed_at: str | None = None
    source_url: str | None = None
    credits: str | None = None
    usage_conditions: str | None = None
    transcribed_coverage: list[dict] = Field(default_factory=list)


class Line(Record):
    line_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    page_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    document_id: str = Field(min_length=1)
    folio_id: str = Field(min_length=1)
    region_id: str = Field(min_length=1)
    reading_order: int = Field(ge=0)
    source_image: str
    crop_image: str | None
    bbox_xyxy: list[int] | None
    source_width: int = Field(gt=0)
    source_height: int = Field(gt=0)
    text_diplomatic: str | None = None
    text_modernized: str | None = None
    reference_source: str | None = None
    reference_pages: list[int] = Field(default_factory=list)
    reference_kind: Literal["modernized_edition", "human_diplomatic", "unknown"] = "unknown"
    review_status: Review = "pending_review"
    reviewer: str | None = None
    reviewed_at: str | None = None
    geometry_status: Review = "pending_review"
    split: Literal["train", "validation", "test", "exploratory"] | None = None
    split_group: str
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    transform_id: str | None = None
    exclusion_reason: str | None = None
    derived_from: str | None = None


def bbox_valid(box, width, height):
    return (isinstance(box, list) and len(box) == 4
            and all(type(v) is int for v in box)
            and 0 <= box[0] < box[2] <= width
            and 0 <= box[1] < box[3] <= height)


def check_reviewer(row):
    if not isinstance(row.get("reviewer"), str) or not row["reviewer"].strip():
        raise ValueError("Revisão validada exige revisor identificado.")
    try:
        stamp = datetime.fromisoformat(row.get("reviewed_at") or "")
        if stamp.tzinfo is None:
            raise ValueError()
    except ValueError:
        raise ValueError("Revisão exige reviewed_at ISO-8601 com fuso.") from None


def inventory(input_dir, output, root=Path.cwd()):
    input_dir, root = Path(input_dir), Path(root)
    if not input_dir.is_dir():
        raise ValueError(f"Entrada ausente: {input_dir}. Coloque fontes em data/raw/inbox/.")
    rows, sources = [], []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue
        checksum = sha256(path)
        name = relative(path, root)
        sources.append({"path": name, "sha256": checksum, "bytes": path.stat().st_size})
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
            continue
        with Image.open(path) as image:
            image.load()
            width, height = image.size
        # Include path identity so duplicate files are visible rather than silently removed.
        import hashlib
        pid = "p_" + hashlib.sha256(name.encode()).hexdigest()[:16]
        rows.append(Page(page_id=pid, document_id="unassigned_" + pid,
                         folio_id=pid, source_image=name, original_name=path.name,
                         width=width, height=height, source_sha256=checksum).model_dump())
    if Path(output).exists():
        raise ValueError("Inventário existente: escolha nova saída para preservar associações.")
    write_jsonl(output, rows)
    write_json(Path(output).with_suffix(".sources.json"), sources)
    return {"images": len(rows), "files": len(sources), "validated": 0}


def extract_archives(input_dir, output_dir):
    """Never move originals, overwrite files or extract outside the destination."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError("Extração exige diretório de saída novo.")
    output_dir.mkdir(parents=True)
    report = []
    for archive in sorted(Path(input_dir).glob("*")):
        if archive.suffix.lower() not in {".zip", ".rar"}:
            continue
        if archive.suffix.lower() == ".zip":
            container = zipfile.ZipFile(archive)
        else:
            import rarfile
            container = rarfile.RarFile(archive)
        with container:
            for entry in container.infolist():
                if entry.is_dir():
                    continue
                # Portable generated names also avoid legacy Windows path length issues.
                original = entry.filename
                if ".." in Path(original.replace("\\", "/")).parts or Path(original).is_absolute():
                    raise ValueError("Arquivo compactado contém caminho inseguro.")
                import hashlib
                key = hashlib.sha256(original.encode()).hexdigest()[:16]
                suffix = Path(original).suffix.lower()
                if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
                    suffix = ".bin"
                destination = output_dir / (sha256(archive)[:12] + "_" + key + suffix)
                with container.open(entry) as source, destination.open("xb") as target:
                    import shutil
                    shutil.copyfileobj(source, target)
                report.append({"archive": archive.name, "archive_sha256": sha256(archive),
                               "original_name": original, "output": destination.name,
                               "sha256": sha256(destination)})
    write_json(output_dir / "extraction.json", report)
    return report


def associate(pages_path, mapping_path, output, root=Path.cwd()):
    """Mapping selects explicit source pages/regions; order is never an association."""
    pages = read_jsonl(pages_path)
    mappings = read_jsonl(mapping_path)
    by_id = {p["page_id"]: p for p in pages}
    seen = set()
    for mapping in mappings:
        pid = mapping["page_id"]
        if pid not in by_id or pid in seen:
            raise ValueError(f"page_id ausente ou repetido no mapeamento: {pid}")
        seen.add(pid)
        if not mapping.get("document_id") or not mapping.get("folio_id"):
            raise ValueError("Informe documento e fólio explicitamente.")
        if mapping.get("correspondence_status", "pending_review") == "validated":
            check_reviewer(mapping)
        page = by_id[pid]
        allowed = {"document_id", "folio_id", "side", "correspondence_status", "reviewer",
                   "reviewed_at", "source_url", "credits", "usage_conditions", "transcribed_coverage"}
        page.update({key: value for key, value in mapping.items() if key in allowed})
        for coverage in page["transcribed_coverage"]:
            if not bbox_valid(coverage.get("bbox_xyxy"), page["width"], page["height"]):
                raise ValueError("Cobertura exige geometria explícita válida.")
            if not coverage.get("region_id") or not coverage.get("reference_pages"):
                raise ValueError("Cobertura exige região e páginas da edição (base 1).")
            if not all(type(n) is int and n > 0 for n in coverage["reference_pages"]):
                raise ValueError("Páginas da edição devem ser inteiros positivos.")
            if not safe_path(root, coverage["reference_source"]).is_file():
                raise ValueError("Fonte da edição ausente.")
        Page.model_validate(page)
    if Path(output).resolve() == Path(pages_path).resolve() or Path(output).exists():
        raise ValueError("Associação exige saída nova; preserve o inventário anterior.")
    write_jsonl(output, pages)
    return pages


def validate(rows, root=Path.cwd(), purpose="catalog", pages=None, grouping="document"):
    errors, warnings = [], []
    if not rows and purpose != "catalog":
        errors.append("Manifest vazio; nenhuma referência apta.")
    pages_by_id = {p["page_id"]: p for p in (pages or [])
                   if isinstance(p, dict) and isinstance(p.get("page_id"), str)}
    if pages is not None:
        seen_pages = set()
        for page in pages:
            try:
                parsed = Page.model_validate(page)
                if parsed.page_id in seen_pages:
                    raise ValueError("page_id duplicado.")
                seen_pages.add(parsed.page_id)
                source = safe_path(root, parsed.source_image)
                with Image.open(source) as image:
                    if image.size != (parsed.width, parsed.height) or sha256(source) != parsed.source_sha256:
                        raise ValueError("Dimensões/checksum da página divergentes.")
                if parsed.correspondence_status == "validated":
                    check_reviewer(page)
                regions = set()
                for coverage in parsed.transcribed_coverage:
                    rid = coverage.get("region_id")
                    if not rid or rid in regions or not bbox_valid(coverage.get("bbox_xyxy"), parsed.width, parsed.height):
                        raise ValueError("Região duplicada ou geometria inválida.")
                    regions.add(rid)
                    if coverage.get("review_status") == "validated":
                        check_reviewer(coverage)
                    if coverage.get("reference_source") and not safe_path(root, coverage["reference_source"]).is_file():
                        raise ValueError("Fonte da cobertura inexistente.")
                    if not all(type(n) is int and n > 0 for n in coverage.get("reference_pages", [])):
                        raise ValueError("Páginas de referência inválidas.")
            except (ValueError, OSError, KeyError) as exc:
                errors.append(f"Página {page.get('page_id') if isinstance(page, dict) else 'inválida'}: {exc}")
    ids, orders = set(), set()
    owners = defaultdict(dict)
    file_checks = {}
    for index, row in enumerate(rows):
        label = row.get("line_id", f"registro {index}") if isinstance(row, dict) else f"registro {index}"
        try:
            line = Line.model_validate(row)
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", line.line_id):
                raise ValueError("line_id deve ser portável.")
            if label in ids:
                raise ValueError("ID duplicado.")
            ids.add(label)
            order = (line.page_id, line.region_id, line.reading_order)
            if line.review_status != "rejected":
                if order in orders:
                    raise ValueError("Ordem de leitura duplicada na região.")
                orders.add(order)
            source = safe_path(root, line.source_image)
            if not source.is_file():
                raise ValueError("Fonte inexistente.")
            if source not in file_checks:
                with Image.open(source) as image:
                    file_checks[source] = (sha256(source), image.size)
            checksum, size = file_checks[source]
            if checksum != line.source_sha256 or size != (line.source_width, line.source_height):
                raise ValueError("Checksum ou dimensões da fonte divergentes.")
            if line.bbox_xyxy is not None and not bbox_valid(line.bbox_xyxy, *size):
                raise ValueError("Geometria inválida.")
            if line.crop_image:
                with Image.open(safe_path(root, line.crop_image)) as crop:
                    crop.load()
                    box = line.bbox_xyxy
                    if box is None or crop.size != (box[2] - box[0], box[3] - box[1]):
                        raise ValueError("Recorte não corresponde à geometria.")
            if line.reference_source and not safe_path(root, line.reference_source).is_file():
                raise ValueError("Fonte da referência inexistente.")
            if any(n <= 0 for n in line.reference_pages):
                raise ValueError("Páginas de referência devem ser positivas.")
            if line.review_status == "validated" or line.geometry_status == "validated":
                check_reviewer(row)
            if pages is not None:
                page = pages_by_id.get(line.page_id)
                if not page or any(row[k] != page[k] for k in ("document_id", "folio_id", "source_image", "source_sha256")):
                    raise ValueError("Associação inconsistente entre linha e página.")
                if purpose != "catalog" and page["correspondence_status"] != "validated":
                    raise ValueError("Correspondência de página pendente.")
            if purpose != "catalog":
                if line.document_id.startswith("unassigned_"):
                    raise ValueError("Documento ainda não identificado.")
                if (line.review_status != "validated" or line.geometry_status != "validated"
                        or line.reference_kind != "human_diplomatic" or not line.text_diplomatic
                        or not line.text_diplomatic.strip() or not line.crop_image or line.bbox_xyxy is None
                        or not line.transform_id or line.exclusion_reason):
                    raise ValueError("Exige referência paleográfica e geometria revisadas, crop e proveniência; modernizada/pendente/excluída não é alvo.")
            if line.split:
                keys = [("group", line.split_group), ("folio", line.folio_id), ("source", checksum)]
                if grouping == "document":
                    keys.append(("document", line.document_id))
                if line.derived_from:
                    keys.extend([("line", line.derived_from)])
                keys.append(("line", line.line_id))
                for key in keys:
                    if owners[key] and line.split not in owners[key]:
                        errors.append(f"{label}: vazamento entre conjuntos por {key}.")
                    owners[key][line.split] = label
            elif purpose == "training":
                raise ValueError("Treino exige split persistido.")
        except (ValueError, OSError, KeyError, ValidationError) as exc:
            errors.append(f"{label}: {exc}")
    if purpose == "training" and set(r.get("split") if isinstance(r, dict) else None for r in rows) != {"train", "validation", "test"}:
        errors.append("Treino exige grupos separados em train, validation e test.")
    return {"valid": not errors, "purpose": purpose, "rows": len(rows),
            "statuses": dict(Counter(r.get("review_status") if isinstance(r, dict) else "invalid_record" for r in rows)),
            "errors": errors, "warnings": warnings}


def require_valid(rows, root, purpose="evaluation", pages=None):
    report = validate(rows, root, purpose, pages)
    if not report["valid"]:
        raise ValueError("; ".join(report["errors"]))
    return report


def make_splits(rows, seed=1831, exploratory=False):
    groups = sorted({r["document_id"] for r in rows})
    if len(groups) < 3 and not exploratory:
        raise ValueError(f"Somente {len(groups)} grupos; treino/validação/teste bloqueados. Use exploratório sem treino.")
    random.Random(seed).shuffle(groups)
    assignment = {g: ("exploratory" if exploratory else "validation" if i == 0 else "test" if i == 1 else "train") for i, g in enumerate(groups)}
    result = [dict(r, split=assignment[r["document_id"]], split_group=r["document_id"]) for r in rows]
    return result, {"seed": seed, "grouping": "document", "assignments": assignment,
                    "counts": dict(Counter(r["split"] for r in result)),
                    "limitation": "Exploratório; sem inferência de generalização." if exploratory else "Poucos grupos; proporções não impostas."}
