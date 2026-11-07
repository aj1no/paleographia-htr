"""Leitura modernizada automática: separada da diplomática e conservadora."""
import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient

from paleographia.modernizacao import modernizar_linha, modernizar_palavra
from test_review_integrity import client_for, patch_line

RAIZ = Path(__file__).resolve().parents[1]


def test_atualiza_grafia_acentos_e_abreviaturas():
    texto = "annos nesta Villa de Nˢᵃ senhora, os officiaes da Camara he hum Capitam"
    sugestao, trocas = modernizar_linha(texto)
    assert sugestao == "anos nesta Vila de Nossa senhora, os oficiais da Câmara é um Capitão"
    assert {"de": "Villa", "para": "Vila", "motivo": "grafia atualizada"} in trocas
    assert texto == "annos nesta Villa de Nˢᵃ senhora, os officiaes da Camara he hum Capitam"
    assert modernizar_linha("de outros muⁱᵗᵒˢ que")[0] == "de outros muitos que"
    assert modernizar_linha("Antonio estaua")[0] == "Antônio estava"     # grafia brasileira


def test_e_conservadora_com_nomes_palavras_curtas_e_fragmentos():
    # Nome próprio no meio da linha só recebe regras que não trocam letras.
    assert modernizar_linha("o Capitão Camargo")[0] == "o Capitão Camargo"
    assert modernizar_linha("Ferreyra")[0] == "Ferreira"
    # Palavras curtas ficam como estão; fim de linha partido também.
    assert modernizar_linha("ha de ser")[0] == "ha de ser"
    assert modernizar_linha("em ato de vereança, trat-")[0] == "em ato de vereança, trat-"
    # Abreviatura que não se resolve fica como foi escrita.
    assert modernizar_palavra("xqzᵗ")[0] is None
    assert modernizar_linha("V.Mag.ᵉ")[0] == "V.Mag.ᵉ"


def test_avaliacao_nao_usa_o_teste_e_nao_piora_a_edicao():
    spec = importlib.util.spec_from_file_location("avaliar_modernizacao", RAIZ / "scripts/avaliar_modernizacao.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    pares = json.loads(modulo.PARES.read_text(encoding="utf-8"))["pares"]
    assert pares and not any(p["document_id"] == "pagamento_thomas_pardo" for p in pares)
    r = modulo.main()
    assert r["modernizado"]["wer"] < r["sem_modernizar"]["wer"]
    assert r["trocas"]["certas"] > r["trocas"]["erradas"]


def test_texto_do_folio_traz_leitura_modernizada_separada(corpus):
    app, lines = client_for(corpus, validated=False)
    with TestClient(app) as client:
        page_id = client.get("/api/catalog").json()["pages"][0]["page_id"]
        assert patch_line(client, lines[0]["line_id"], {"text_diplomatic": "nesta Villa"}).status_code == 200
        assert patch_line(client, lines[1]["line_id"], {"text_diplomatic": "da Camara",
                                                        "text_modernized": "da Câmara Municipal"}).status_code == 200
        data = client.get(f"/api/pages/{page_id}/text").json()
        primeira, segunda = data["lines"][0], data["lines"][1]
        assert primeira["text"] == "nesta Villa" and primeira["modernized"] == "nesta Vila"
        assert primeira["modernized_source"] == "automatica"
        assert segunda["modernized"] == "da Câmara Municipal" and segunda["modernized_source"] == "edicao"
        assert all(r["modernized"] == "" and r["modernized_source"] is None for r in data["lines"][2:])
        assert data["modernized_text"].splitlines()[:2] == ["nesta Vila", "da Câmara Municipal"]


def test_palavra_dividida_na_quebra_de_linha_fica_inteira():
    from paleographia.modernizacao import modernizar_linhas
    linhas = ["por nos assinado em seu cumpri", "mento e na forma dele", "os officiaes em acto, trat-", "ando sobre"]
    assert modernizar_linhas(linhas) == ["por nos assinado em seu cumpri", "mento e na forma dele",
                                         "os oficiais em ato, trat-", "ando sobre"]
    assert modernizar_linhas(["nesta Villa", None, ""]) == ["nesta Vila", "", ""]
