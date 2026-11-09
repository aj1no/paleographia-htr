"""Intervalos de confiança do teste final, a partir das predições já gravadas (nenhum modelo roda).

Uso, na raiz do projeto:  python scripts/analisar_teste_final.py

Lê avaliacao_final.json e calcula, por bootstrap de linhas (2.000 reamostragens, semente fixa),
o IC 95% do CER de cada modelo, por documento e no total, e a diferença pareada de cada modelo
ajustado em relação ao base. A análise "sem pedaços de margem" é post hoc e vem identificada assim.
"""
import json
import random
import sys
from pathlib import Path

import jiwer

PASTA = Path(__file__).resolve().parents[1] / "docs/revisao_humana/teste_reservado_congelado_20261109"
N, SEMENTE = 2000, 7


def cer(rows):
    return jiwer.cer([r["ref"] for r in rows], [r["hyp"] for r in rows])


def ic(valores):
    valores = sorted(valores)
    return [round(valores[int(0.025 * len(valores))], 4), round(valores[int(0.975 * len(valores)) - 1], 4)]


def bootstrap(rows, funcao):
    rnd = random.Random(SEMENTE)
    return ic([funcao([rows[rnd.randrange(len(rows))] for _ in rows]) for _ in range(N)])


def main():
    avaliacao = json.loads((PASTA / "avaliacao_final.json").read_text(encoding="utf-8"))
    referencia = {json.loads(l)["line_id"]: json.loads(l)
                  for l in (PASTA / "referencia.jsonl").read_text(encoding="utf-8").splitlines() if l}
    modelos = avaliacao["models"]
    base = {r["line_id"]: r for r in modelos["PP-OCRv6 base"]["rows"]}
    saida = {"method": f"bootstrap de linhas, {N} reamostragens, semente {SEMENTE}; IC 95% por percentis",
             "reference_sha256": avaliacao["reference_sha256"], "models": {}}
    for nome, dados in modelos.items():
        rows = dados["rows"]
        texto = [r for r in rows if referencia[r["line_id"]]["region_id"] == "page"]
        item = {"cer": round(cer(rows), 4), "cer_ic95": bootstrap(rows, cer),
                "by_document": {doc: {"lines": len(sel), "cer": round(cer(sel), 4), "cer_ic95": bootstrap(sel, cer)}
                                for doc in sorted({r["document_id"] for r in rows})
                                for sel in [[r for r in rows if r["document_id"] == doc]]},
                "post_hoc_sem_pedacos_de_margem": {"lines": len(texto), "cer": round(cer(texto), 4),
                                                   "cer_ic95": bootstrap(texto, cer)},
                "empty_predictions": sum(not r["hyp"] for r in rows)}
        if nome != "PP-OCRv6 base":
            item["diferenca_para_base_ic95"] = bootstrap(
                rows, lambda s: cer(s) - cer([base[r["line_id"]] for r in s]))
        saida["models"][nome] = item
    (PASTA / "analise_intervalos.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
