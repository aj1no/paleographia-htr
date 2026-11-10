"""Palavras a conferir: fora do dicionário atual depois da modernização, sem marcar pedaço de palavra partida."""
from paleographia.duvidas import duvidas, duvidas_por_linha, localizar


def marcadas(texto, **opcoes):
    return [(texto[a:z], tipo) for a, z, tipo in duvidas(texto, **opcoes)]


def test_marca_erro_de_leitura_e_nome_proprio():
    texto = "Sobre o quinto em que o Fiscal prorpem aos batecins, e Pentiado."
    assert marcadas(texto) == [("prorpem", "duvida"), ("batecins", "duvida"), ("Pentiado", "nome")]


def test_nao_marca_palavra_atual_acento_abreviatura_nem_numero():
    assert marcadas("Art. 1° Ninguém poderá vender pólvora pra ja, nem polvora, no ano de 1831 em Jundiaí") == []


def test_pedaco_de_palavra_partida_na_quebra_fica_de_fora():
    diplomaticas = ["trabalham so-", "bre si em officinas"]
    modernas = ["trabalham so-", "bre si em oficinas"]
    assert marcadas(modernas[1]) == [("bre", "duvida")]
    assert duvidas_por_linha(diplomaticas, modernas) == [[], []]


def test_localizar_acha_a_linha_inteira_antes_da_partida():
    linhas = [(14, "O Fiscal requisita do Juiz de"), (15, "Paz os jornaleiros"), (16, "mais devidade concluir")]
    texto = "O Fiscal requisita do Juiz de Paz os jornaleiros mais devidade concluir"
    assert [d[3] for d in localizar(duvidas(texto), texto, linhas)] == [16]
    linhas = [(5, "o Fiscal prorpem me"), (6, "lativamenete aos")]
    texto = "o Fiscal prorpem melativamenete aos"
    assert [(texto[a:z], n) for a, z, _, n in localizar(duvidas(texto), texto, linhas)] == [("prorpem", 5), ("melativamenete", 5)]
