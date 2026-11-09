"""Avaliação final ÚNICA do teste reservado congelado em 09/11/2026.

Uso, na raiz do projeto, com Docker aberto:  python scripts/avaliar_teste_final.py

Confere o SHA-256 da referência congelada e de cada recorte, roda cada configuração final do
PP-OCRv6 (base, ajustado A, ajustado B) uma única vez pelo mesmo worker de inferência do editor
e grava CER e WER em NFC, por linha, por documento e no total. A métrica é a mesma da validação
de 1795 (scripts/avaliar_validacao.py). Um modelo que já tem resultado gravado não roda de novo.
"""
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import jiwer
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.io import now, sha256  # noqa: E402
from paleographia.kraken_recognition import KrakenRecognizer  # noqa: E402

PASTA = RAIZ / "docs/revisao_humana/teste_reservado_congelado_20261109"
SAIDA = PASTA / "avaliacao_final.json"
MODELOS = {
    "PP-OCRv6 base": ("models/kraken_ppocrv6_medium/medium.safetensors",
                      "15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9"),
    "PP-OCRv6 ajustado A": ("models/ppocrv6_ajustado_A_20261106/medium_ajustado_A_gravado.safetensors",
                            "04194328e5d12b4f7a72bb2764a0c4c76f5030e9856e5c41ce96d04ab8b7c148"),
    "PP-OCRv6 ajustado B": ("models/ppocrv6_ajustado_B_20261107/medium_ajustado_B_gravado.safetensors",
                            "52b2ad55829ad63d6e79c632de431521aeac0abe591fe60197dd1cbfc64fc384"),
}
DOCKER = {"docker_image": "paleographia-kraken:7.1.0-cpu",
          "docker_image_id": "sha256:511fb2e2b76db8de0d3eb87dcf04398f7a02fc06b5d91887629b2492f826af5b",
          "device": "cpu", "precision": "float32", "timeout_seconds": 300}


def nfc(texto):
    return " ".join(unicodedata.normalize("NFC", texto or "").split())


def metricas(refs, hyps):
    return {"lines": len(refs), "chars": sum(map(len, refs)), "words": sum(len(r.split()) for r in refs),
            "cer": round(jiwer.cer(refs, hyps), 4), "wer": round(jiwer.wer(refs, hyps), 4)}


def referencia():
    congelamento = json.loads((PASTA / "congelamento.json").read_text(encoding="utf-8"))
    if sha256(PASTA / "referencia.jsonl") != congelamento["reference_sha256"]:
        raise SystemExit("A referência mudou depois do congelamento; avaliação recusada.")
    linhas = [json.loads(l) for l in (PASTA / "referencia.jsonl").read_text(encoding="utf-8").splitlines() if l]
    for linha in linhas:
        if sha256(RAIZ / linha["crop_image"]) != linha["crop_sha256"]:
            raise SystemExit(f"Recorte alterado depois do congelamento: {linha['line_id']}")
    return congelamento, linhas


def main():
    congelamento, linhas = referencia()
    resultado = (json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else
                 {"reference_sha256": congelamento["reference_sha256"], "normalization": "NFC, espaços simplificados",
                  "metric": "jiwer.cer e jiwer.wer agregados (mesmo cálculo da validação de 1795)",
                  "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                               cwd=RAIZ).stdout.strip(),
                  "models": {}})
    for nome, (pesos, esperado) in MODELOS.items():
        if nome in resultado["models"]:
            print(nome, "já avaliado; não roda de novo.")
            continue
        if sha256(RAIZ / pesos) != esperado:
            raise SystemExit(f"{nome}: pesos diferentes dos avaliados na validação.")
        reconhecedor = KrakenRecognizer(dict(DOCKER, model=pesos, sha256=esperado), RAIZ)
        reconhecedor.load()
        inicio, linhas_saida = now(), []
        try:
            for linha in linhas:
                with Image.open(RAIZ / linha["crop_image"]) as imagem:
                    hyp = nfc(reconhecedor.recognize(imagem.convert("RGB")).get("text_raw"))
                ref = nfc(linha["text_diplomatic"])
                linhas_saida.append({"line_id": linha["line_id"], "document_id": linha["document_id"],
                                     "page_id": linha["page_id"], "reading_order": linha["reading_order"],
                                     "ref": ref, "hyp": hyp, "cer": round(jiwer.cer(ref, hyp), 4)})
        finally:
            reconhecedor.close()
        por_doc = {}
        for doc in sorted({l["document_id"] for l in linhas_saida}):
            sel = [l for l in linhas_saida if l["document_id"] == doc]
            por_doc[doc] = metricas([l["ref"] for l in sel], [l["hyp"] for l in sel])
        resultado["models"][nome] = {
            "weights": pesos, "sha256": esperado, "started_at": inicio, "finished_at": now(),
            "total": metricas([l["ref"] for l in linhas_saida], [l["hyp"] for l in linhas_saida]),
            "by_document": por_doc, "rows": linhas_saida}
        SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total = resultado["models"][nome]["total"]
        print(nome, "CER", total["cer"], "WER", total["wer"],
              {d: (m["cer"], m["wer"]) for d, m in por_doc.items()}, flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
