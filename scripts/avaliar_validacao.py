"""Compara pesos PP-OCRv6 nas mesmas linhas, com CER/WER em NFC (a métrica do projeto).

Usa o worker de inferência do editor (imagem Docker de CPU avaliada), o mesmo caminho das
sugestões no editor. Uso, na raiz do projeto, com Docker aberto:

    python scripts/avaliar_validacao.py . PARES.json validation PESO1.safetensors [PESO2 ...]

PARES.json é uma lista de pares (crop_image, text, split); a saída em JSON tem, por peso,
o SHA-256, CER e WER agregados e a leitura de cada linha. Nunca rode no teste reservado
antes da avaliação final única.
"""
import json, sys, unicodedata
from pathlib import Path
from PIL import Image
import jiwer
root = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root / "src"))
from paleographia.kraken_recognition import KrakenRecognizer
from paleographia.io import sha256
pairs = [p for p in json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if p["split"] == sys.argv[3]]
from paleographia.ppocrv6_finetune import RESERVED_TEST_DOCUMENTS
if any(p["document_id"] in RESERVED_TEST_DOCUMENTS for p in pairs):
    sys.exit("Teste reservado: use só na avaliação final única, com script próprio.")
n = lambda s: " ".join(unicodedata.normalize("NFC", s or "").split())
results = {}
for weights in sys.argv[4:]:
    rel = Path(weights).resolve().relative_to(root).as_posix()
    settings = {"model": rel, "sha256": sha256(root / rel), "docker_image": "paleographia-kraken:7.1.0-cpu",
                "docker_image_id": "sha256:511fb2e2b76db8de0d3eb87dcf04398f7a02fc06b5d91887629b2492f826af5b",
                "device": "cpu", "precision": "float32", "timeout_seconds": 300}
    rec = KrakenRecognizer(settings, root); rec.load()
    refs, hyps, rows = [], [], []
    for p in pairs:
        with Image.open(root / p["crop_image"]) as im:
            hyp = n(rec.recognize(im.convert("RGB")).get("text_raw"))
        ref = n(p["text"]); refs.append(ref); hyps.append(hyp)
        rows.append({"ref": ref, "hyp": hyp, "cer": round(jiwer.cer(ref, hyp), 4)})
    rec.close()
    results[rel] = {"sha256": settings["sha256"], "lines": len(rows), "chars": sum(map(len, refs)),
                    "cer": round(jiwer.cer(refs, hyps), 4), "wer": round(jiwer.wer(refs, hyps), 4), "rows": rows}
    print(rel, "CER", results[rel]["cer"], "WER", results[rel]["wer"], flush=True)
print(json.dumps(results, ensure_ascii=False, indent=1))
