"""Audit a published development experiment without loading model weights."""
import json
from pathlib import Path

from PIL import Image

from .data import require_valid
from .evaluation import evaluate
from .io import read_jsonl, safe_path, sha256


def artifact_for_hash(root, row):
    """Old code can evolve; retain the exact implementation bytes in an archive."""
    current = safe_path(root, row["path"])
    if current.is_file() and sha256(current) == row["sha256"]:
        return current
    if ((row["path"].endswith((".py", ".js")) and row["path"].startswith(("src/", "scripts/")))
            or row["path"] == "runtime/kraken_ppocrv6/README.md"):
        for revision in ("31997a4", "3284e07", "75b7b24"):
            archived = safe_path(root, f"docs/experimentos/implementation_{revision}/"+row["path"])
            if archived.is_file() and sha256(archived) == row["sha256"]:
                return archived
    return current


def verify_files(root, bundle):
    root = Path(root)
    inventory = json.loads((Path(bundle)/"inventory.json").read_bytes())
    seen = set()
    for row in inventory["files"]:
        path = artifact_for_hash(root, row)
        if row["path"] in seen:
            raise ValueError("Inventário com caminho duplicado.")
        seen.add(row["path"])
        if sha256(path) != row["sha256"]:
            raise ValueError(f"Hash divergente: {row['path']}")
    return inventory


def restore_support(root, bundle):
    """Offline, explicit recovery of the exact edition PDF at its original path."""
    root = Path(root)
    inventory = verify_files(root, bundle)
    for row in inventory.get("restore_support", []):
        source, target = safe_path(root, row["published"]), safe_path(root, row["original"])
        if sha256(source) != row["sha256"]:
            raise ValueError("Fonte de apoio divergente.")
        if target.exists():
            if sha256(target) != row["sha256"]:
                raise ValueError("Fonte existente divergente; não foi sobrescrita.")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(source.read_bytes())


def check_control(reference, predictions):
    keys = ("line_id", "page_id", "region_id", "reading_order", "bbox_xyxy", "crop_image", "source_sha256")
    if len(predictions) != len(reference):
        raise ValueError("Quantidade de predições diverge do controle.")
    for ref, pred in zip(reference, predictions):
        if any(ref[key] != pred.get(key) for key in keys):
            raise ValueError("IDs, ordem ou recortes divergem do controle congelado.")


def audit_bundle(root, bundle, output):
    """Recompute region AND line scores from saved raw outputs into a new directory."""
    root, bundle, output = Path(root), Path(bundle), Path(output)
    inventory = verify_files(root, bundle)
    if output.exists():
        raise ValueError("Auditoria exige saída nova.")
    # Original baseline receipts keep their old paths; this mapping preserves bytes.
    mappings = {row["original"]: row for row in inventory["original_to_published"]}
    original_hashes = json.loads((bundle/"baseline_trocr/frozen_reference.json").read_bytes())["source_hashes"]
    for original, digest in original_hashes.items():
        mapping = mappings[original]
        if sha256(safe_path(root, mapping["published"])) != digest:
            raise ValueError("Referência original congelada divergente.")
    diagnostic = json.loads((bundle/"baseline_trocr/diagnostico.json").read_bytes())
    for row in diagnostic["files"]:
        if sha256(safe_path(root, mappings[row["path"]]["published"])) != row["sha256"]:
            raise ValueError("Artefato diverge do diagnóstico original.")
    protocol = json.loads((bundle/"protocol.json").read_bytes())
    if protocol["dataset_role"] != "development" or protocol["reserved_test_available"]:
        raise ValueError("Esta amostra é desenvolvimento, sem teste reservado disponível.")
    pages = read_jsonl(bundle/"reference/catalogo/pages.jsonl")
    lines = read_jsonl(bundle/"reference/linhas_exploratorias.jsonl")
    original_lines = read_jsonl(bundle/"reference/catalogo/lines.jsonl")
    if len(lines) != protocol["lines"] or len({r["document_id"] for r in lines}) != 1:
        raise ValueError("Escopo documental divergente.")
    for original, current in zip(original_lines, lines):
        expected = dict(original, split="exploratory", split_group=original["document_id"])
        if current != expected:
            raise ValueError("Atribuição exploratória alterou a referência humana.")
    if len(original_lines) != len(lines):
        raise ValueError("Catálogo e referência têm quantidades distintas.")
    require_valid(lines, root, "evaluation", pages)
    for row in lines:
        with Image.open(safe_path(root, row["source_image"])) as source, Image.open(safe_path(root, row["crop_image"])) as crop:
            expected = source.convert("RGB").crop(row["bbox_xyxy"])
            if crop.convert("RGB").tobytes() != expected.tobytes() or crop.size != expected.size:
                raise ValueError("Pixels do recorte divergem da caixa na fonte.")
    for snapshot in (bundle/"reference/snapshots").glob("snapshot_*.json"):
        if sha256(snapshot) != snapshot.stem.removeprefix("snapshot_"):
            raise ValueError("Snapshot difere do endereço de conteúdo.")
        state = json.loads(snapshot.read_bytes())
        if (state["revision"] != protocol["workspace_revision"] or state["pages"] != pages
                or state["lines"] != original_lines):
            raise ValueError("Snapshot e catálogo humano exportado divergem.")
    results = {}
    for name in protocol["runs"]:
        run = bundle/name
        predictions = read_jsonl(run/"predictions.jsonl")
        check_control(lines, predictions)
        result = evaluate(lines, predictions, output/name, root, pages)
        expected = json.loads((run/"evaluation/metrics.json").read_bytes())
        if result != expected:
            raise ValueError(f"Métricas recalculadas divergentes: {name}")
        for filename in ("regions.jsonl", "lines.jsonl"):
            if read_jsonl(output/name/filename) != read_jsonl(run/"evaluation"/filename):
                raise ValueError(f"Detalhes recalculados divergentes: {name}/{filename}")
        results[name] = result["metrics"]
    comparison = json.loads((bundle/"comparison.json").read_bytes())
    if comparison["runs"] != results or comparison["dataset_role"] != "development":
        raise ValueError("Tabela comparativa diverge das métricas recalculadas.")
    return {"verified_files": len(inventory["files"]), "dataset_role": "development",
            "lines": len(lines), "results": results}
