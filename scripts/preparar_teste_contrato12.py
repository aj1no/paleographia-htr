"""Cria a curadoria às cegas do contrato do livro 12 (1763), segundo documento do teste reservado.

Uso, na raiz do projeto:  python scripts/preparar_teste_contrato12.py

As quatro imagens do manuscrito já estão extraídas do PDF da edição no inventário do corpus
(data/manifests/corpus_expandido_v02/pdf_images/c7ffb34ac9b8c735/, páginas 9 a 12 do PDF). O
script só cataloga essas imagens, conferindo o SHA-256 do inventário, e desenha as linhas com o
segmentador blla do Kraken. Nenhum reconhecedor roda, o texto da edição não é lido e o workspace
nasce com o reconhecimento desligado. Recusa rodar se o workspace já existir.
"""
import json
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.services import ReviewService  # noqa: E402

CONFIG = RAIZ / "configs/curation_teste_contrato12.toml"
INVENTARIO = RAIZ / "data/manifests/corpus_expandido_v02/embedded_images.jsonl"
FONTE = "c7ffb34ac9b8c735"
PAGINAS_PDF = (9, 10, 11, 12)
CATALOGO = ("https://jundiai.sismu.app/obra/101489/contrato-para-exploracao-de-minas-auriferas-em-"
            "territorios-jundiaienses-em-1763-o-texto-contem-descricoes-sobre-africanos-afro-brasileiros-"
            "povos-originarios-e-quilombos")
CREDITOS = ("Arquivo Histórico Municipal de Jundiaí (SISMU), registro 02317; Cartório Olgado, livro 12, "
            "folhas 278 e 279; edição modernizada: Gilson Santos (AHMJ), revisão Isabella Ferraro (AHMJ).")


def paginas():
    linhas = [json.loads(linha) for linha in INVENTARIO.read_text(encoding="utf-8").splitlines() if linha.strip()]
    imagens = {r["pdf_page"]: r for r in linhas
               if r["source_id"] == FONTE and r.get("manuscript_candidate") and r["width"] > 1000}
    assert sorted(imagens) == list(PAGINAS_PDF), sorted(imagens)
    return [{
        "page_id": f"contrato12_pdf_p{n:02d}",
        "document_id": "contrato_livro12_1763",
        # Fólio e face ficam para o revisor identificar na imagem (folhas 278 e 279, segundo o catálogo).
        "folio_id": f"pdf_p{n:02d}",
        "side": "unknown",
        "source_image": imagens[n]["path"],
        "original_name": f"edição livro 12, página {n} do PDF, imagem {imagens[n]['embedded_image_index']}",
        "width": imagens[n]["width"],
        "height": imagens[n]["height"],
        "source_sha256": imagens[n]["sha256"],
        "correspondence_status": "pending_review",
        "source_url": CATALOGO,
        "credits": CREDITOS,
        "usage_conditions": "Consultar condições do acervo antes de redistribuir as imagens.",
        "transcribed_coverage": [],
    } for n in PAGINAS_PDF]


def main():
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["recognition"]["backend"] == "disabled", "o teste exige o reconhecedor desligado"
    service = ReviewService(RAIZ, config)
    if service.workspace.exists():
        raise SystemExit(f"{service.workspace} já existe; nada foi alterado.")
    service.import_catalog(paginas(), [])
    for pagina in service.state()["pages"]:
        linhas = service.segment(pagina["page_id"], "kraken_blla")
        print(pagina["page_id"], len(linhas), "linhas", sum(l["region_id"] == "margem" for l in linhas), "na margem")
    estado = service.state()
    assert not estado["predictions"]
    print("revisão atual:", estado["revision"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
