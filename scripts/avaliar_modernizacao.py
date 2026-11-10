"""Avalia a leitura modernizada automática contra a edição modernizada do Arquivo Histórico.

Uso, na raiz do projeto:  python scripts/avaliar_modernizacao.py [saida.json] [--v1]

Por padrão avalia a versão em uso (v2, ``modernizacao_v2``); ``--v1`` avalia a primeira versão.

Pares: linhas com transcrição diplomática validada por humano e a mesma linha na edição
modernizada do AHMJ (que preserva a quebra de linha do original). Comparação em minúsculas,
NFC, sem pontuação, porque a edição atualiza a pontuação e as maiúsculas de nomes (normas 10
e 13) e o modernizador não mexe nelas. O teste reservado (pagamento) não entra aqui.
"""
import json
import string
import sys
from pathlib import Path

import jiwer

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia import modernizacao, modernizacao_v2  # noqa: E402
from paleographia.modernizacao import nfc  # noqa: E402

VERSOES = {1: modernizacao.modernizar_linha, 2: modernizacao_v2.modernizar_linha}

PARES = RAIZ / "docs/experimentos/modernizacao_20261107/pares_avaliacao.json"
SINAIS = str.maketrans("", "", string.punctuation + "“”‘’«»…[]†♱")


def comparavel(texto):
    return " ".join(nfc(texto).lower().translate(SINAIS).split())


def alinhar_palavras(a, b):
    """Alinhamento de Levenshtein entre listas de palavras; devolve pares (i, j) substituídos ou iguais."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    i, j, pares = n, m, []
    while i and j:
        if d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            pares.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif d[i][j] == d[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    return pares[::-1]


def main(saida=None, versao=2, pares=None):
    modernizar_linha = VERSOES[versao]
    pares = pares if pares is not None else json.loads(PARES.read_text(encoding="utf-8"))["pares"]
    assert not any(p["document_id"] == "pagamento_thomas_pardo" for p in pares), "teste reservado fora"
    diplomaticas = [comparavel(p["diplomatica"]) for p in pares]
    edicoes = [comparavel(p["edicao"]) for p in pares]
    linhas, sugestoes = [], []
    certas = erradas = desnecessarias = 0
    for par, diplomatica, edicao in zip(pares, diplomaticas, edicoes):
        sugestao, trocas = modernizar_linha(par["diplomatica"])
        sugestoes.append(comparavel(sugestao))
        a, b, c = diplomatica.split(), comparavel(sugestao).split(), edicao.split()
        # Cada palavra trocada pelo modernizador: certa se coincide com a da edição alinhada.
        alvo = dict(alinhar_palavras(a, c))
        for i, (antes, depois) in enumerate(zip(a, b)):
            if antes == depois or len(a) != len(b):
                continue
            if i in alvo and c[alvo[i]] == depois:
                certas += 1
            elif i in alvo and c[alvo[i]] == antes:
                desnecessarias += 1
            else:
                erradas += 1
        linhas.append({"document_id": par["document_id"], "linha": par["linha"], "diplomatica": par["diplomatica"],
                       "sugestao": sugestao, "edicao": par["edicao"], "trocas": trocas,
                       "wer_antes": jiwer.wer(edicao, diplomatica), "wer_depois": jiwer.wer(edicao, comparavel(sugestao))})
    resultado = {
        "versao": versao, "pares": len(pares), "palavras_da_edicao": sum(len(e.split()) for e in edicoes),
        "sem_modernizar": {"cer": jiwer.cer(edicoes, diplomaticas), "wer": jiwer.wer(edicoes, diplomaticas)},
        "modernizado": {"cer": jiwer.cer(edicoes, sugestoes), "wer": jiwer.wer(edicoes, sugestoes)},
        "trocas": {"certas": certas, "erradas": erradas, "desnecessarias": desnecessarias},
        "linhas": linhas,
    }
    if saida:
        Path(saida).write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return resultado


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    argumentos = [a for a in sys.argv[1:] if a != "--v1"]
    r = main(argumentos[0] if argumentos else None, versao=1 if "--v1" in sys.argv else 2)
    print(f"versão {r['versao']}")
    for chave in ("sem_modernizar", "modernizado"):
        print(f"{chave:15s} CER {r[chave]['cer']:.2%}  WER {r[chave]['wer']:.2%}")
    print("trocas:", r["trocas"])
    for linha in r["linhas"]:
        print(f"{linha['wer_antes']:.0%} -> {linha['wer_depois']:.0%}  {linha['sugestao']}")
        print(f"{'':12s}{linha['edicao']}")
