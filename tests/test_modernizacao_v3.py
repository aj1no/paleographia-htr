"""Leitura modernizada v3: artigo, réis, futuro em texto normativo, palavras grudadas, hífen de quebra."""
import hashlib
from pathlib import Path

from paleographia.modernizacao_v3 import modernizar_linha, modernizar_linhas
from paleographia.textos import juntar

RAIZ = Path(__file__).resolve().parents[1]


def moderna(texto, **opcoes):
    return modernizar_linha(texto, **opcoes)[0]


def test_v2_continua_intacta():
    codigo = (RAIZ / "src/paleographia/modernizacao_v2.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(codigo).hexdigest() == "bdd34ffe6c7311c3b562a6c9b7eef72d72e194320b261eb47ee554182b579ed8"


def test_artigo_ordinal_e_reis():
    assert moderna("Art. 1° Niguem poderá vender armas ofencivas") == "Artigo 1º Niguem poderá vender armas ofensivas"
    assert moderna("Art.3° O Escravo naõ poderaõ") == "Artigo 3º O escravo não poderão"
    assert moderna("e pagará oito mil reis de multa") == "e pagará oito mil réis de multa"
    assert moderna("os reis de Portugal") == "os reis de Portugal"


def test_futuro_em_texto_normativo_e_preterito_em_narrativa():
    linhas = modernizar_linhas(["mais officiais não", "construiraõ, ou concertaraõ armas aos escravos", "terá oito dias de prisaõ"])
    assert linhas[1].startswith("construirão, ou concertarão")
    assert modernizar_linhas(["e logo derão principio a obra", "e se forão embora"]) == ["e logo deram principio a obra", "e se foram embora"]


def test_palavra_grudada_partida_e_rara():
    assert moderna("dias, eo senhor") == "dias, e o senhor"
    assert moderna("tera apena de quatro dias") == "terá a pena de quatro dias"
    assert moderna("sem a lugador certo") == "sem alugador certo"
    assert moderna("duzentos acoites") == "duzentos açoites"
    assert moderna("com cincoenta açoites") == "com cinquenta açoites"
    assert moderna("Paço da Camara") == "Paço da Câmara"


def test_minuscula_so_em_papel_depois_de_artigo_ou_possessivo():
    assert moderna("seu Senhor. O Contraventor tera") == "seu senhor. O contraventor terá"
    assert moderna("o dito Senhor Governador") == "o dito Senhor Governador"
    assert moderna("Paschoal Dias Rodrigues") == "Paschoal Dias Rodrigues"
    assert modernizar_linhas(["Freguezia de Nossa", "Senhora do Desterro"])[1].startswith("Senhora")


def test_hifen_de_quebra_enchimento_e_antes_de_maiuscula():
    assert juntar(["e paga -", "rá quatro mil"]) == "e pagará quatro mil"
    assert juntar(["vinte mil reis de -", "multa sendo"]) == "vinte mil reis de multa sendo"
    assert juntar(["requezita do Juiz de-", "PAz os jornaleiros"]) == "requezita do Juiz de PAz os jornaleiros"
    assert juntar(["cumpri-", "mento da ordem"]) == "cumprimento da ordem"
    assert moderna("para lhe man -", partida_no_fim=True) == "para lhe man -"
