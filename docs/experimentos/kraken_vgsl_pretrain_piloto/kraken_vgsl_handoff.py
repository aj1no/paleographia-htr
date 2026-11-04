"""Materializa referências já validadas para verificar a transferência VGSL."""
import sys
from pathlib import Path

from PIL import Image
from paleographia.io import read_jsonl, sha256, write_json


out = Path(sys.argv[1])
out.mkdir()
source = Path("data/manifests/corpus_expandido_v02/core_lines.jsonl")
rows = {row["line_id"]: row for row in read_jsonl(source)}
evidence = []
for split, numbers in (("train", (1, 2, 3, 4, 5, 6)), ("validation", (7, 8))):
    directory = out / split
    directory.mkdir()
    paths = []
    for number in numbers:
        row = rows[f"l_traslado_269r_body_{number:02d}"]
        assert row["partition"] == "development" and row["review_status"] == "validated"
        assert row["reference_kind"] == "human_diplomatic" and row["geometry_status"] == "validated"
        assert row["text_diplomatic"].strip()
        image_path = Path(row["crop_image"])
        destination = directory / (row["line_id"] + ".png")
        with Image.open(image_path) as image:
            gray = image.convert("L")
            gray.info.clear()
            gray.save(destination)
        target = destination.with_suffix(".gt.txt")
        target.write_text(row["text_diplomatic"], encoding="utf-8", newline="\n")
        paths.append(f"/work/handoff_data/{split}/{destination.name}")
        evidence.append({
            "role": split, "line_id": row["line_id"], "source_crop_sha256": sha256(image_path),
            "png_sha256": sha256(destination), "target_sha256": sha256(target),
        })
    (out / f"{split}.lst").write_text("\n".join(paths) + "\n", encoding="utf-8", newline="\n")
write_json(out / "inventory.json", {
    "mode": "technical_handoff", "test_used": False,
    "reference_manifest": source.as_posix(), "reference_manifest_sha256": sha256(source),
    "records": evidence,
})
