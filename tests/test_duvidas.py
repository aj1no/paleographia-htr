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


def test_glossario_numera_notas_na_ordem_e_repete_o_numero(tmp_path):
    import json

    from paleographia.glossario import Notas, verbetes
    arquivo = tmp_path / "glossario.json"
    arquivo.write_text(json.dumps({"verbetes": [
        {"termo": "rocio", "formas": ["rocio", "rossio"], "situacao": "conferida", "nota": "terreno público", "fontes": []},
        {"termo": "magotes", "formas": ["magotes"], "situacao": "rascunho", "nota": "grupos", "fontes": []}]}), encoding="utf-8")
    notas = Notas(verbetes(arquivo))
    texto = "andar em Magotes no Rossio e no rocio"
    assert [(texto[a:z], n) for a, z, n in notas.marcar(texto)] == [("Magotes", 1), ("Rossio", 2), ("rocio", 2)]
    assert [n["termo"] for n in notas.lista] == ["magotes", "rocio"]
    assert notas.conferida("rocio") and not notas.conferida("magotes")
    assert verbetes(tmp_path / "nao_existe.json") == {}


def test_verbete_conferido_deixa_de_ser_duvida():
    from paleographia.textos import textos_validados
    page = {"page_id": "p", "folio_id": "1r"}
    linhas = [{"page_id": "p", "line_id": "l1", "region_id": "corpo", "reading_order": 0, "review_status": "validated",
               "text_diplomatic": "dentro do rocio da Villa"}]
    rascunho = {"rocio": {"termo": "rocio", "formas": ["rocio"], "situacao": "rascunho", "nota": "n", "fontes": []}}
    conferida = {"rocio": dict(rascunho["rocio"], situacao="conferida")}
    bloco = textos_validados(page, linhas, rascunho)["corpo"][0]
    assert bloco["notas"] == [[10, 15, 1]] and [d[2] for d in bloco["duvidas"]] == ["duvida"]
    corpo = textos_validados(page, linhas, conferida)
    assert corpo["corpo"][0]["duvidas"] == [] and corpo["notas"][0]["termo"] == "rocio"
