"""Congela os dados do piloto comparativo VGSL. Execute na raiz do projeto."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

from paleographia.data import require_valid
from paleographia.evaluation import normalize
from paleographia.io import read_jsonl, sha256, write_json, write_jsonl


protocol = Path("docs/entregas/continuidade_20261103/particoes_ppocrv6_20261104/protocolo_candidato.json")
pretrain_report = Path("docs/experimentos/kraken_vgsl_pretrain_piloto/resultado.json")
prior = json.loads(pretrain_report.read_bytes())
pretrain_weights = Path(prior["pretraining"]["weights"])
assert sha256(pretrain_weights) == prior["artifacts_sha256"][pretrain_weights.as_posix()]
pretrain_data_path = Path("output/kraken_vgsl_pretrain_smoke_01/input/inventory.json")
assert sha256(pretrain_data_path) == prior["artifacts_sha256"][pretrain_data_path.as_posix()]
pretrained_documents = {row["document_id"] for row in json.loads(pretrain_data_path.read_bytes())["records"]}
draft = json.loads(protocol.read_bytes())
groups = {group["document_id"]: group for group in draft["groups"]}
documents = ("tt_pbr_0004_026_traslado_1767", "carta_jose_gomes_1767", "sessao_1795")
assert not set(documents[1:]) & pretrained_documents
out = Path(sys.argv[1])
out.mkdir(parents=True)
(out / "weights_initial").mkdir()
shutil.copyfile(pretrain_weights, out / "weights_initial/pretrained.safetensors")
(out / "supervised").mkdir()
(out / "evaluation_images").mkdir()
(out / "models").mkdir()
records = []
refs = []
pixel_roles = {}
text_roles = {}
for index, document in enumerate(documents):
    group = groups[document]
    manifests = {key: Path(group[key]) for key in ("reference_manifest", "page_manifest")}
    assert all(sha256(path) == group[key + "_sha256"] for key, path in manifests.items())
    rows_by_id = {row["line_id"]: row for row in read_jsonl(manifests["reference_manifest"])}
    rows = [rows_by_id[line_id] for line_id in group["line_ids"]]
    assert len(rows) == (16, 3, 7)[index]
    require_valid(rows, Path.cwd(), "evaluation", read_jsonl(manifests["page_manifest"]))
    for position, row in enumerate(rows):
        assert row["document_id"] == document
        role = ("train" if position < 12 else "monitor") if index == 0 else "evaluation"
        dest_folder = out / ("evaluation_images" if index else f"supervised/{role}")
        dest_folder.mkdir(exist_ok=True)
        source = Path(row["crop_image"])
        destination = dest_folder / (row["line_id"] + ".png")
        with Image.open(source) as image:
            gray = image.convert("L")
            pixels = hashlib.sha256(str(gray.size).encode() + gray.tobytes()).hexdigest()
            gray.info.clear()
            gray.save(destination)
        if pixels in pixel_roles:
            raise ValueError(f"Imagem repetida: {source}")
        pixel_roles[pixels] = role
        text = normalize(row["text_diplomatic"])
        if text in text_roles and text_roles[text] != role:
            raise ValueError(f"Texto de linha repetido entre papéis: {row['line_id']}")
        text_roles[text] = role
        if role == "evaluation":
            refs.append({"line_id": row["line_id"], "document_id": document, "reading_order": row["reading_order"],
                         "reference": row["text_diplomatic"], "image": destination.name})
        else:
            destination.with_suffix(".gt.txt").write_text(text, encoding="utf-8", newline="\n")
        records.append({
            "line_id": row["line_id"], "document_id": document, "role": role, "source": source.as_posix(),
            "source_sha256": sha256(source), "image_sha256": sha256(destination), "gray_pixel_sha256": pixels,
            "image": destination.relative_to(out).as_posix(),
            "normalized_reference_sha256": hashlib.sha256(text.encode()).hexdigest(),
        })
for role in ("train", "monitor"):
    images = ["/data/" + Path(row["image"]).relative_to("supervised").as_posix() for row in records if row["role"] == role]
    (out / f"supervised/{role}.lst").write_text("\n".join(images) + "\n", encoding="utf-8", newline="\n")
write_jsonl(out / "evaluation_references.jsonl", refs)
write_json(out / "inventory.json", {
    "protocol": protocol.as_posix(), "protocol_sha256": sha256(protocol),
    "scope": "exploratory_document_holdout",
    "pretrained_documents": sorted(pretrained_documents),
    "initial_weights_sha256": sha256(pretrain_weights),
    "official_scientific_split": None,
    "records": records,
})
