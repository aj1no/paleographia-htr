"""Aba Textos: só linhas validadas, texto corrido com palavras partidas unidas, e tema em todas as telas."""
import copy

from fastapi.testclient import TestClient

from paleographia.api import create_app
from paleographia.textos import juntar
from test_api import TestRecognizer


def test_juntar_une_palavra_partida_na_quebra_de_linha():
    assert juntar(["aos ca", "torze Dias"]) == "aos catorze Dias"
    assert juntar(["Freguezia de Nossa senhora do Des", "terro de Jundiahy"]) == "Freguezia de Nossa senhora do Desterro de Jundiahy"
    assert juntar(["cumpri-", "mento da ordem"]) == "cumprimento da ordem"
    assert juntar(["em Jundiahy.", "Anno"]) == "em Jundiahy. Anno"


def test_textos_trazem_so_linhas_validadas_e_marcam_lacunas(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    texts = ["aos ca", "torze Dias", "rascunho que não pode aparecer"]
    for line, text in zip(lines, texts):
        line.update(text_diplomatic=text, reference_kind="human_diplomatic", reviewer="Ana",
                    review_status="validated", reviewed_at="2026-10-15T12:00:00+00:00")
    lines[2].update(review_status="pending_review", reviewed_at=None)
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        body = client.get(f"/api/pages/{pages[0]['page_id']}/textos").json()
        assert client.get("/api/pages/nao_existe/textos").status_code == 404
    assert body["validadas"] == 2 and body["total"] == len(lines)
    text_block = next(b for b in body["corpo"] if b["tipo"] == "texto")
    assert text_block["diplomatica"] == "aos catorze Dias"
    assert [l["numero"] for l in text_block["linhas"]] == [1, 2]
    assert body["corpo"][-1] == {"tipo": "lacuna", "numeros": list(range(3, len(lines) + 1))}
    assert "rascunho" not in str(body)


def test_todas_as_telas_usam_o_tema_compartilhado(corpus):
    root, config, pages, lines = copy.deepcopy(corpus)
    app = create_app(root, config, TestRecognizer())
    app.state.service.import_catalog(pages, lines)
    with TestClient(app) as client:
        css, js = client.get("/tema.css"), client.get("/tema.js")
        assert css.status_code == 200 and ":root[data-theme=dark]" in css.text and "[hidden]{display:none!important}" in css.text
        assert js.status_code == 200 and "prefers-color-scheme: dark" in js.text
        for path in ("/", "/leitura", "/textos", "/folio-texto", "/repertorio"):
            page = client.get(path).text
            assert '<script src="/tema.js"></script>' in page and 'href="/tema.css"' in page and 'id="themeToggle"' in page, path
