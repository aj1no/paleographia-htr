"""Análise linguística dos erros e pós-correção lexical (A × B) sobre predições já salvas.

Uso, na raiz do projeto:  python scripts/analise_pln.py [saida.json]
Não roda reconhecedor, GPU nem Docker. Vocabulário: só transcrições de treino e data/lexicon.
"""
import json
import sys
from pathlib import Path

import jiwer

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.pln_erros import (TIPOS, Vocabulario, analisar, corrigir_linha,  # noqa: E402
                                    normalizar, palavras)

DADOS = RAIZ / "docs/experimentos/ppocrv6_ajuste_fino_20261105/dados"
NOMES = {"models/kraken_ppocrv6_medium/medium.safetensors": "PP-OCRv6 base",
         "models/ppocrv6_ajustado_A_20261106/medium_ajustado_A_gravado.safetensors": "Ajustado A (Traslado)",
         "models/ppocrv6_ajustado_B_20261107/medium_ajustado_B_gravado.safetensors": "Ajustado B (Traslado + Inquisição)",
         "models/ppocrv6_ajustado_D1_20261110/medium_ajustado_D1.safetensors": "Ajustado D1 (Traslado + Posturas)"}


def metricas(refs, hyps):
    refs, hyps = [normalizar(r) for r in refs], [normalizar(h) for h in hyps]
    return {"cer": jiwer.cer(refs, hyps), "wer": jiwer.wer(refs, hyps)}


def textos_de_treino():
    pares = json.loads((DADOS / "pares_traslado_mais_inquisicao.json").read_text(encoding="utf-8"))
    treino = [p["text"] for p in pares if p["split"] == "train"]
    validacao = [p["text"] for p in pares if p["split"] != "train"]
    lexico = [json.loads(linha)["form"] for linha in
              (RAIZ / "data/lexicon/entries.jsonl").read_text(encoding="utf-8").splitlines() if linha.strip()]
    return treino, lexico, validacao


def main(saida=None):
    predicoes = json.loads((DADOS / "avaliacao_validacao_base_A_B_nfc.json").read_text(encoding="utf-8"))
    treino, lexico, validacao = textos_de_treino()
    vocab = Vocabulario(treino + lexico)
    palavras_validacao = set(palavras(" ".join(validacao)))
    resultado = {
        "vocabulario": {"fontes": "transcrições de treino (Traslado alinhado + humano, Inquisição CC BY 4.0) e data/lexicon",
                        "linhas_de_treino": len(treino), "formas_do_lexico": len(lexico),
                        "formas_distintas": len(vocab.frequencia),
                        "palavras_da_validacao_tambem_no_vocabulario": sorted(palavras_validacao & set(vocab.frequencia)),
                        "palavras_da_validacao_fora_do_vocabulario": sorted(palavras_validacao - set(vocab.frequencia))},
        "modelos": {}}
    for chave, dados in predicoes.items():
        refs = [r["ref"] for r in dados["rows"]]
        hyps = [r["hyp"] for r in dados["rows"]]
        analise = analisar(list(zip(refs, hyps)))
        analise["confusoes"] = [{"referencia": a, "predicao": b, "vezes": n}
                                for (a, b), n in analise["confusoes"].most_common(15)]
        modelo = {"bruto": metricas(refs, hyps), "erros": analise, "pos_correcao": {}}
        for metodo in ("A", "B"):
            linhas = [corrigir_linha(h, vocab, metodo) for h in hyps]
            modelo["pos_correcao"][metodo] = {
                **metricas(refs, [t for t, _ in linhas]),
                "linhas": [{"referencia": normalizar(r), "bruto": normalizar(h), "sugestao": t, "trocas": tr}
                           for r, h, (t, tr) in zip(refs, hyps, linhas)]}
        resultado["modelos"][NOMES.get(chave, chave)] = modelo
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    if saida:
        Path(saida).write_text(texto + "\n", encoding="utf-8", newline="\n")
    return resultado


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    r = main(sys.argv[1] if len(sys.argv) > 1 else None)
    print("vocabulário:", r["vocabulario"]["formas_distintas"], "formas")
    for nome, m in r["modelos"].items():
        a, b = m["pos_correcao"]["A"], m["pos_correcao"]["B"]
        print(f"{nome}: bruto CER {m['bruto']['cer']:.2%} WER {m['bruto']['wer']:.2%} | "
              f"A {a['cer']:.2%} / {a['wer']:.2%} | B {b['cer']:.2%} / {b['wer']:.2%}")
        for t in TIPOS:
            e = m["erros"]["por_tipo"][t]
            print(f"   {t:40s} {e['erros']:3d}  {e['parcela_dos_erros']:.0%}")
