"""Avaliação nova da leitura modernizada: contrato do livro 12 (1763) contra a edição do AHMJ.

Uso, na raiz do projeto:  python scripts/avaliar_modernizacao_contrato12.py

Diplomática: as 24 linhas do corpo da página 9 do PDF (fl. 1) na referência congelada de
09/11 (só leitura; o arquivo não é alterado e o hash é conferido). Edição: o fl. 1 da edição
modernizada (Gilson Santos, revisão Isabella Ferraro, AHMJ), que mantém as linhas do
original. A linha 1 da edição (``Registro de uma petição``) está na margem e fica de fora,
como as outras 10 peças de margem que o blla separou.

Pareamento: as 24 linhas do corpo, em ordem de leitura, com as linhas 2 a 25 da edição, em
ordem. Quando o blla mandou para a margem uma palavra do começo ou do fim da linha (``ou``,
``na``, ``os``), a linha diplomática fica menor que a da edição. Por isso a edição é cortada no
trecho de palavras contíguas mais parecido com a diplomática (menor CER). O corte depende só
da diplomática e da edição, nunca da saída de um modernizador, e vale igual para v1 e v2.
Também se informa o resultado sem corte.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import jiwer

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import avaliar_modernizacao as avaliacao  # noqa: E402

REFERENCIA = RAIZ / "docs/revisao_humana/teste_reservado_congelado_20261109/referencia.jsonl"
REFERENCIA_SHA256 = "2d0fb78e021f72a971a2ae8ccacbc72544b560a5c7e57b1366cf2fe273a6fee0"
EDICAO = RAIZ / "data/raw/corpus_expandido_v02/fontes/contrato_livro12_1763/modernized_edition_c7ffb34ac9b8c735.pdf"
EDICAO_SHA256 = "c7ffb34ac9b8c735bf5b25cfa6c32d98b3e752fbc8744fa9a8feb14489620e07"
SAIDA = RAIZ / "docs/experimentos/modernizacao_20261107"


def sha256(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def linhas_da_edicao():
    """Linhas do fl. 1 da edição, sem números de linha, título nem créditos."""
    import pymupdf
    with pymupdf.open(EDICAO) as pdf:
        texto = "\n".join(pdf[i].get_text("text") for i in range(pdf.page_count))
    trecho = texto.split("[fl.1]", 1)[1].split("[fl.2]", 1)[0]
    saida = []
    for linha in trecho.splitlines():
        linha = linha.strip()
        if not linha or re.fullmatch(r"\d+\.?", linha) or linha.startswith(("Transcrição e edição", "Revisão:")):
            continue
        saida.append(linha)
    return saida


def recortar(diplomatica, edicao):
    """Trecho contíguo de palavras da edição mais parecido com a diplomática."""
    alvo, palavras = avaliacao.comparavel(diplomatica), edicao.split()
    melhor = (jiwer.cer(alvo, avaliacao.comparavel(edicao)), edicao)
    for inicio in range(len(palavras)):
        for fim in range(inicio + 1, len(palavras) + 1):
            trecho = " ".join(palavras[inicio:fim])
            if avaliacao.comparavel(trecho):
                cer = jiwer.cer(alvo, avaliacao.comparavel(trecho))
                if cer < melhor[0] - 1e-9:
                    melhor = (cer, trecho)
    return melhor[1]


def pares():
    assert sha256(REFERENCIA) == REFERENCIA_SHA256, "referência congelada mudou"
    assert sha256(EDICAO) == EDICAO_SHA256, "edição mudou"
    referencia = [json.loads(l) for l in REFERENCIA.read_text(encoding="utf-8").splitlines() if l.strip()]
    corpo = sorted((l for l in referencia if l["document_id"] == "contrato_livro12_1763"
                    and l["page_id"] == "contrato12_pdf_p09" and l["region_id"] != "margem"),
                   key=lambda l: l["reading_order"])
    edicao = linhas_da_edicao()[1:]                       # a linha 1 está na margem
    assert len(corpo) == 24 and len(edicao) >= 24, (len(corpo), len(edicao))
    return [{"document_id": "contrato_livro12_1763", "linha": numero, "line_id": l["line_id"],
             "diplomatica": l["text_diplomatic"], "edicao": recortar(l["text_diplomatic"], e), "edicao_inteira": e}
            for numero, (l, e) in enumerate(zip(corpo, edicao), start=2)]


def main():
    lista = pares()
    (SAIDA / "pares_contrato12.json").write_text(json.dumps({
        "descricao": "Contrato do livro 12 (1763), fl. 1: diplomática da referência congelada de 09/11 (Tiago "
                     "Avelar) × edição modernizada do AHMJ (Gilson Santos; revisão Isabella Ferraro). Uso sem fins "
                     "comerciais, com crédito. Linha = número da linha na edição.",
        "referencia_sha256": REFERENCIA_SHA256, "edicao_sha256": EDICAO_SHA256, "pares": lista,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    resultado = {}
    for corte in ("trecho", "inteira"):
        usados = [dict(p, edicao=p["edicao"] if corte == "trecho" else p["edicao_inteira"]) for p in lista]
        for versao in (1, 2):
            r = avaliacao.main(versao=versao, pares=usados)
            resultado[f"{corte}_v{versao}"] = {k: r[k] for k in ("pares", "palavras_da_edicao", "sem_modernizar",
                                                                 "modernizado", "trocas")}
            if corte == "trecho":
                resultado[f"linhas_v{versao}"] = r["linhas"]
    (SAIDA / "resultado_contrato12.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8", newline="\n")
    return resultado


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    r = main()
    for corte in ("trecho", "inteira"):
        v1, v2 = r[f"{corte}_v1"], r[f"{corte}_v2"]
        print(f"[{corte}] {v1['pares']} linhas, {v1['palavras_da_edicao']} palavras")
        print(f"  sem modernizar CER {v1['sem_modernizar']['cer']:.2%}  WER {v1['sem_modernizar']['wer']:.2%}")
        print(f"  v1             CER {v1['modernizado']['cer']:.2%}  WER {v1['modernizado']['wer']:.2%}  {v1['trocas']}")
        print(f"  v2             CER {v2['modernizado']['cer']:.2%}  WER {v2['modernizado']['wer']:.2%}  {v2['trocas']}")
