"""Troca os recortes automáticos por projeção do teste reservado pelos do segmentador blla.

Uso, na raiz do projeto:  python scripts/resegmentar_teste_blla.py

Só segmentação: o blla desenha linhas de base e polígonos, não lê texto. Nenhum reconhecedor
roda e o workspace continua com o reconhecimento desligado. Recusa trocar se alguma linha das
páginas já tiver texto, revisão ou ajuste humano. As revisões anteriores ficam no histórico do
workspace (cada gravação cria uma revisão nova).
"""
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.services import ReviewService  # noqa: E402

CONFIG = RAIZ / "configs/curation_teste_pagamento.toml"
PAGINAS = ("pagamento_f113v", "pagamento_f114r")


def main():
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["recognition"]["backend"] == "disabled", "o teste exige o reconhecedor desligado"
    service = ReviewService(RAIZ, config)
    estado = service.state()
    if estado.get("predictions"):
        raise SystemExit("O workspace do teste tem predições; nada foi alterado.")
    das_paginas = [linha for linha in estado["lines"] if linha["page_id"] in PAGINAS]
    tocadas = [linha["line_id"] for linha in das_paginas
               if linha.get("text_diplomatic") or linha.get("reviewer")
               or linha.get("review_status") != "pending_review"
               or linha.get("geometry_status") != "pending_review"
               or linha.get("segmentation_method") not in ("opencv", "projection")]
    if tocadas:
        raise SystemExit(f"{len(tocadas)} linhas já têm trabalho humano; nada foi alterado.")
    if das_paginas:
        restantes = [linha for linha in estado["lines"] if linha["page_id"] not in PAGINAS]
        service.save(dict(estado, lines=restantes), "remove_unreviewed_projection_lines")
    for pagina in PAGINAS:
        linhas = service.segment(pagina, "kraken_blla")
        print(pagina, len(linhas), "linhas", sum(linha["region_id"] == "margem" for linha in linhas), "na margem")
    print("revisão atual:", service.state()["revision"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
