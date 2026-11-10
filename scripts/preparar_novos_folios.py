"""Cria a curadoria assistida dos fólios novos para treino (10/11/2026).

Uso, na raiz do projeto:  python scripts/preparar_novos_folios.py

Seis imagens do corpus v0.2 sem uso no treino supervisionado: Código de Posturas de 1831
(100r, 100v, 101r), carta de José Gomes de Gouveia de 1767 (fólio 4) e contrato do livro 13
de 1763 (páginas 5 e 6 do PDF da edição). O script confere o SHA-256 de cada imagem, desenha
as linhas com o blla (juntando os pedaços cortados) e pede a leitura do ajustado B, que fica
como sugestão. A equipe corrige e valida no modo leitura; só linhas validadas viram rótulo.

Ficam de fora, e o script recusa: o teste reservado (pagamento a Thomas Pardo, contrato do
livro 12) e a validação de 1795. Recusa rodar se o workspace já existir.
"""
import json
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.services import ReviewService  # noqa: E402

CONFIG = RAIZ / "configs/novos_folios.toml"
FONTES = RAIZ / "data/manifests/corpus_expandido_v02/sources.jsonl"
EMBUTIDAS = RAIZ / "data/manifests/corpus_expandido_v02/embedded_images.jsonl"
PROIBIDOS = {"pagamento_thomas_pardo", "contrato_livro12_1763", "sessao_1795"}
USO = "Uso acadêmico, sem fins comerciais, com crédito ao Arquivo Histórico Municipal de Jundiaí."

# (source_id, page_id, folio_id, side, nome)
IMAGENS = (
    ("413d1502555f62d4", "posturas1831_f100r", "f100r", "recto", "Código de Posturas - 1831, Fólio 100 reto"),
    ("2d0bc739ae48eeda", "posturas1831_f100v", "f100v", "verso", "Código de Posturas - 1831, Fólio 100 verso"),
    ("c001a2648e01c5c4", "posturas1831_f101r", "f101r", "recto", "Código de Posturas - 1831, Fólio 101 reto"),
    ("7d9c6e3e9a0728b1", "carta1767_f4", "f4", "unknown", "Carta de José Gomes de Gouveia, 1767, Fólio 4"),
)
CONTRATO13 = ("3348a51ef10d9d1b", (5, 6))


def ler(caminho):
    return [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()]


def paginas():
    fontes = {f["source_id"]: f for f in ler(FONTES)}
    saida = []
    for fonte, page_id, folio, lado, nome in IMAGENS:
        f = fontes[fonte]
        assert f["kind"] == "manuscript_image" and f["candidate_group"] not in PROIBIDOS, fonte
        saida.append({"page_id": page_id, "document_id": f["document_id"], "folio_id": folio, "side": lado,
                      "source_image": f["path"], "original_name": nome, "source_sha256": f["sha256"],
                      "source_url": f["catalog_url"], "credits": f["credits"]})
    edicao = fontes[CONTRATO13[0]]
    assert edicao["candidate_group"] not in PROIBIDOS
    embutidas = {e["pdf_page"]: e for e in ler(EMBUTIDAS)
                 if e["source_id"] == CONTRATO13[0] and e.get("manuscript_candidate")}
    assert sorted(embutidas) == list(CONTRATO13[1]), sorted(embutidas)
    for n in CONTRATO13[1]:
        e = embutidas[n]
        saida.append({"page_id": f"contrato13_pdf_p{n:02d}", "document_id": edicao["document_id"],
                      "folio_id": f"pdf_p{n:02d}", "side": "unknown", "source_image": e["path"],
                      "original_name": f"Contrato do livro 13, 1763, página {n} do PDF da edição",
                      "source_sha256": e["sha256"], "source_url": edicao["catalog_url"], "credits": edicao["credits"],
                      "width": e["width"], "height": e["height"]})
    from PIL import Image
    for p in saida:
        if "width" not in p:
            with Image.open(RAIZ / p["source_image"]) as imagem:
                p["width"], p["height"] = imagem.size
        p.update(correspondence_status="pending_review", usage_conditions=USO, transcribed_coverage=[])
        assert p["document_id"] not in PROIBIDOS, p
    return saida


def main():
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    service = ReviewService(RAIZ, config)
    if service.workspace.exists():
        raise SystemExit(f"{service.workspace} já existe; nada foi alterado.")
    service.import_catalog(paginas(), [])
    for pagina in service.state()["pages"]:
        linhas = service.segment(pagina["page_id"], "kraken_blla")
        print(pagina["page_id"], len(linhas), "linhas", sum(l["region_id"] == "margem" for l in linhas), "na margem",
              flush=True)
        predicoes = service.recognize_page(pagina["page_id"])
        print("   ", len(predicoes), "leituras do ajustado B", flush=True)
    print("revisão atual:", service.state()["revision"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
