"""Modernizador v2: caixa, palavras partidas na linha, nomes próprios e pretérito em -ão."""
import hashlib
from pathlib import Path

from paleographia import modernizacao
from paleographia.modernizacao_v2 import modernizar_linha, modernizar_linhas

RAIZ = Path(__file__).resolve().parents[1]
V1_SHA256 = "cc00fbfb1b4000abe29583267e7e80302ea9754a7c097a0fab90c86fe3cca6e5"


def leitura(texto):
    return modernizar_linha(texto)[0]


def test_v1_continua_intacta():
    codigo = (RAIZ / "src/paleographia/modernizacao.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(codigo).hexdigest() == V1_SHA256


def test_caixa_no_meio_da_palavra_e_palavras_gramaticais():
    assert leitura("e Com TOdos os moradores") == "e com todos os moradores"
    assert leitura("Com isto se acabou") == "Com isto se acabou"            # início de frase fica
    assert leitura("feito. Em seguida") == "feito. Em seguida"
    assert leitura("o Capitão Camargo") == "o Capitão Camargo"


def test_palavra_partida_dentro_da_linha():
    assert leitura("Com quistas de Jundiahy") == "Conquistas de Jundiaí"
    assert leitura("e tão bem os oficiais") == "e também os oficiais"
    assert leitura("a fim de que") == "a fim de que"
    assert leitura("estando hy o mto padre") == "estando hy o mto padre"     # abreviatura sem vogal
    assert leitura("e de vendo pagar") == "e de vendo pagar"                 # as duas partes existem


def test_nomes_proprios_em_grafia_antiga():
    assert leitura("Joam Pires do Riberão") == "João Pires do Ribeirão"
    assert leitura("Manoel Joze de Parnahiba") == "Manuel José de Parnaíba"


def test_preterito_em_ao_vira_am_e_substantivo_fica():
    assert leitura("os quais deraõ e forão") == "os quais deram e foram"
    assert leitura("se achavão e Havião") == "se achavam e Haviam"
    assert leitura("pela mesma Razão") == "pela mesma Razão"
    assert leitura("do Lugar do Fundaõ") == "do Lugar do Fundão"
    assert leitura("farão o que") == "farão o que"                          # ``faram`` não existe


def test_o_que_a_v1_ja_fazia_continua():
    for texto in ("de outros muⁱᵗᵒˢ que", "Antonio estaua", "ha de ser", "em ato de vereança, trat-", "V.Mag.ᵉ"):
        assert leitura(texto) == modernizacao.modernizar_linha(texto)[0], texto
    assert modernizar_linhas(["por nos assinado em seu cumpri", "mento e na forma dele"]) == \
        ["por nos assinado em seu cumpri", "mento e na forma dele"]


def test_trocas_explicam_o_motivo():
    trocas = modernizar_linha("Com quistas e derão")[1]
    assert {"de": "Com quistas", "para": "Conquistas", "motivo": "palavra unida"} in trocas
    assert {"de": "derão", "para": "deram", "motivo": "pretérito em -am"} in trocas
