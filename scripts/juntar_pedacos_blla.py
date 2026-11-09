"""Junta à linha os pedaços que o blla cortou (primeira ou última palavra virando "margem").

Uso, na raiz do projeto:
    python scripts/juntar_pedacos_blla.py configs/curation_teste_contrato12.toml [--simular]

Só mexe em linhas sem trabalho humano (sem texto e nunca revisadas). As linhas substituídas ficam
no histórico de revisões do workspace e a linha nova lista as originais em ``merged_from``. Não roda
nenhum reconhecedor: só recorta de novo a imagem com os polígonos que o blla já tinha desenhado.
"""
import argparse
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.blla_segmentation import side_fragments  # noqa: E402
from paleographia.services import ReviewService  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--simular", action="store_true", help="só conta, sem gravar")
    args = parser.parse_args()
    config = tomllib.loads((RAIZ / args.config).read_text(encoding="utf-8"))
    service = ReviewService(RAIZ, config)
    for page in service.state()["pages"]:
        if args.simular:
            lines = [l for l in service.state()["lines"]
                     if l["page_id"] == page["page_id"] and l["review_status"] != "rejected"
                     and l.get("blla_geometry", {}).get("boundary")]
            grupos = side_fragments(lines)
            print(page["page_id"], "pares possíveis (inclui linhas já revisadas):", len(grupos))
            continue
        feitas = service.rejoin_blla_pieces(page["page_id"])
        print(page["page_id"], "linhas refeitas:", len(feitas))
    print("revisão atual:", service.state()["revision"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
