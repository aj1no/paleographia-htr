"""Análise de erros e pós-correção lexical, sem reconhecedor."""
import json
from pathlib import Path

import jiwer

from paleographia.pln_erros import (TIPOS, Vocabulario, alinhar, analisar, classificar, corrigir_linha,
                                    levenshtein)


def test_alinhamento_conta_o_mesmo_que_o_cer():
    for ref, hyp in [("de São Paulo, em casas", "de Saõ Paulo em Cazas"), ("ando sobre", "lando sobre"), ("", "x")]:
        erros = sum(op != "=" for op, *_ in alinhar(ref, hyp))
        assert erros == levenshtein(ref, hyp)
        if ref:
            assert abs(erros / len(ref) - jiwer.cer(ref, hyp)) < 1e-9


def test_classifica_os_tipos_linguisticos():
    ref = "de São Paulo, em casas de Nˢᵃ"
    assert classificar("S", "c", "C", ref, ref.index("casas")) == TIPOS[3]          # maiúscula
    assert classificar("S", "ã", "a", ref, ref.index("ã")) == TIPOS[4]              # acento ou til
    assert classificar("S", "s", "z", ref, ref.index("casas") + 2) == TIPOS[5]      # grafia histórica
    assert classificar("D", ",", "", ref, ref.index(",")) == TIPOS[1]               # pontuação
    assert classificar("D", " ", "", ref, 2) == TIPOS[0]                            # espaço
    assert classificar("S", "ˢ", "o", ref, ref.index("ˢ")) == TIPOS[2]              # abreviatura
    assert classificar("S", "P", "B", ref, ref.index("Paulo")) == TIPOS[6]          # nome próprio


def test_analise_soma_os_erros_do_cer():
    pares = [("de São Paulo", "de Saõ Paulo"), ("em casas", "em Cazas")]
    r = analisar(pares)
    assert r["erros"] == sum(v["erros"] for v in r["por_tipo"].values()) == 4
    assert abs(r["cer"] - jiwer.cer([p[0] for p in pares], [p[1] for p in pares])) < 1e-9


def test_pos_correcao_e_sugestao_separada_e_preserva_o_que_esta_no_vocabulario():
    vocab = Vocabulario(["Salvador de Oliveira Prado", "na mesma Villa"])
    bruto = "Selvador de Oliviera Prado, xy"
    for metodo in ("A", "B"):
        sugestao, trocas = corrigir_linha(bruto, vocab, metodo)
        assert sugestao.startswith("Salvador de Oliveira Prado,") and sugestao.endswith("xy")
        assert {"de": "Selvador", "para": "Salvador"} in trocas
    assert bruto == "Selvador de Oliviera Prado, xy"


def test_vocabulario_da_analise_nao_usa_a_validacao():
    raiz = Path(__file__).resolve().parents[1]
    pares = json.loads((raiz / "docs/experimentos/ppocrv6_ajuste_fino_20261105/dados/"
                               "pares_traslado_mais_inquisicao.json").read_text(encoding="utf-8"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("analise_pln", raiz / "scripts/analise_pln.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    treino, _, validacao = modulo.textos_de_treino()
    assert validacao and not set(validacao) & set(treino)
    assert all(p["split"] == "train" for p in pares if p["text"] in treino)
    assert not any(p["document_id"] == "pagamento_thomas_pardo" for p in pares)
