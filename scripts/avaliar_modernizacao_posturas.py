"""Avalia a leitura modernizada nas Posturas de 1831 contra a edição modernizada do AHMJ.

Uso, na raiz do projeto:  python scripts/avaliar_modernizacao_posturas.py

Lê as linhas validadas dos fólios 100r, 100v e 101r na aplicação oficial
(``data/demo_apresentacao``), alinha cada uma com a linha da edição (que mantém a quebra do
original; o começo do 100r não está na edição) e compara v1, v2 e v3 como
``avaliar_modernizacao.py``. Grava os pares e o resultado em ``docs/experimentos/modernizacao_20261107/``.
Desde 10/11 estas linhas são de **desenvolvimento** da v3: os erros da v2 nelas guiaram a v3.
"""
import difflib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))
import avaliar_modernizacao as av  # noqa: E402
from paleographia.modernizacao_v2 import modernizar_linha  # noqa: E402

ED = [RAIZ / f"data/raw/transcriptions/codigo_de_posturas_-_1831_p00{i}.txt" for i in (1, 2, 3)]


def edicao():
    folios, atual = {}, None
    for arq in ED:
        for linha in arq.read_text(encoding="utf-8").splitlines():
            t = linha.strip()
            if t.startswith("[fl"):
                atual = "f100v" if "100v" in t else ("f100r" if "100" in t else "f101r")
                continue
            if not t or t.isdigit() or t in ("Prado", "(...)") or t.startswith(("Transcrição", "Revisão:", "Sessão de", "Transcrição das")):
                continue
            if atual:
                folios.setdefault(atual, []).append(t)
    return folios


def linhas_validadas():
    W = RAIZ / "data/demo_apresentacao/workspace"
    rev = json.loads((W / "current.json").read_text(encoding="utf-8"))["revision"]
    st = json.loads((W / "revisions" / f"{rev}.json").read_text(encoding="utf-8"))
    saida = {}
    for f in ("f100r", "f100v", "f101r"):
        ls = sorted([l for l in st["lines"] if l["page_id"] == f"posturas1831_{f}" and l["review_status"] == "validated"],
                    key=lambda l: l["reading_order"])
        saida[f] = [l["text_diplomatic"] for l in ls]
    return saida


def alinhar(dip, ed):
    """Alinhamento em ordem: pares (i, j, similaridade >= 0,45) entre a v2 de ``dip[i]`` e ``ed[j]``."""
    a = [av.comparavel(modernizar_linha(x)[0]) for x in dip]
    b = [av.comparavel(x) for x in ed]
    sim = [[difflib.SequenceMatcher(None, x, y).ratio() for y in b] for x in a]
    n, m = len(a), len(b)
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            s = sim[i][j] if sim[i][j] >= 0.45 else -1
            best[i][j] = max(best[i + 1][j], best[i][j + 1], s + best[i + 1][j + 1] if s > 0 else -1)
    i = j = 0
    pares = []
    while i < n and j < m:
        s = sim[i][j]
        if s >= 0.45 and best[i][j] == s + best[i + 1][j + 1]:
            pares.append((i, j, s)); i += 1; j += 1
        elif best[i][j] == best[i + 1][j]:
            i += 1
        else:
            j += 1
    return pares


if __name__ == "__main__":
    from paleographia import modernizacao_v3
    av.VERSOES[3] = modernizacao_v3.modernizar_linha
    sys.stdout.reconfigure(encoding="utf-8")
    pasta = RAIZ / "docs/experimentos/modernizacao_20261107"
    ed, dip = edicao(), linhas_validadas()
    pares = []
    for f in ("f100r", "f100v", "f101r"):
        for i, j, s in alinhar(dip[f], ed[f]):
            pares.append({"document_id": "posturas_1831", "linha": f"{f}:{i}", "diplomatica": dip[f][i], "edicao": ed[f][j], "sim": round(s, 2)})
    (pasta / "pares_posturas.json").write_text(json.dumps({"pares": pares}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    resultado = {}
    for versao in (1, 2, 3):
        r = av.main(None, versao=versao, pares=pares)
        resultado[f"v{versao}"] = {k: r[k] for k in ("sem_modernizar", "modernizado", "trocas", "palavras_da_edicao")}
        print(f"v{versao}: modernizado CER {r['modernizado']['cer']:.2%} WER {r['modernizado']['wer']:.2%} trocas {r['trocas']}")
    print(f"sem modernizar: CER {r['sem_modernizar']['cer']:.2%} WER {r['sem_modernizar']['wer']:.2%}; {len(pares)} linhas, {r['palavras_da_edicao']} palavras")
    (pasta / "resultado_posturas.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
