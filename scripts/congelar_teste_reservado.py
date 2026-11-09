"""Congela a referência do teste reservado antes da avaliação final única.

Uso, na raiz do projeto:  python scripts/congelar_teste_reservado.py

Lê as duas curadorias às cegas (pagamento a Thomas Pardo e contrato do livro 12), confere que
nenhuma tem predição de modelo e exporta só as linhas validadas como transcrição diplomática
humana, com revisor. Copia cada recorte para uma pasta local fora do Git e grava:

- docs/revisao_humana/teste_reservado_congelado_20261109/referencia.jsonl  (texto e hashes)
- docs/revisao_humana/teste_reservado_congelado_20261109/congelamento.json (revisões e contagens)

Recusa rodar se o congelamento já existir: a referência não muda depois de congelada.
"""
import json
import shutil
import sys
import tomllib
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.io import now, sha256  # noqa: E402
from paleographia.services import ReviewService  # noqa: E402

DATA = "20261109"
DESTINO = RAIZ / f"docs/revisao_humana/teste_reservado_congelado_{DATA}"
RECORTES = RAIZ / f"data/teste_reservado_congelado_{DATA}/recortes"
CURADORIAS = ("configs/curation_teste_pagamento.toml", "configs/curation_teste_contrato12.toml")
CAMPOS = ("line_id", "document_id", "page_id", "folio_id", "region_id", "reading_order", "bbox_xyxy",
          "source_image", "source_sha256", "text_diplomatic", "reference_kind", "reviewer", "reviewed_at",
          "geometry_status", "exclusion_reason", "merged_from")


def main():
    if DESTINO.exists() or RECORTES.exists():
        raise SystemExit("O teste já foi congelado; nada foi alterado.")
    linhas, revisoes = [], {}
    for caminho in CURADORIAS:
        config = tomllib.loads((RAIZ / caminho).read_text(encoding="utf-8"))
        assert config["recognition"]["backend"] == "disabled", caminho
        estado = ReviewService(RAIZ, config).state()
        if estado["predictions"]:
            raise SystemExit(f"{caminho}: há predições de modelo; o teste deixou de ser às cegas.")
        revisoes[caminho] = {"workspace": config["paths"]["workspace"], "revision": estado["revision"],
                             "lines_total": len(estado["lines"]),
                             "status": dict(Counter(l["review_status"] for l in estado["lines"]))}
        for linha in estado["lines"]:
            if linha["review_status"] != "validated":
                continue
            assert (linha.get("text_diplomatic") or "").strip(), linha["line_id"]
            assert linha.get("reference_kind") == "human_diplomatic", linha["line_id"]
            assert (linha.get("reviewer") or "").strip(), linha["line_id"]
            assert not linha.get("exclusion_reason"), linha["line_id"]
            linhas.append(linha)
    linhas.sort(key=lambda l: (l["document_id"], l["page_id"], l["reading_order"]))
    RECORTES.mkdir(parents=True)
    DESTINO.mkdir(parents=True)
    registros = []
    for linha in linhas:
        origem = RAIZ / linha["crop_image"]
        if linha.get("crop_sha256") and sha256(origem) != linha["crop_sha256"]:
            raise SystemExit(f"Recorte alterado desde a segmentação: {linha['line_id']}")
        copia = RECORTES / (linha["line_id"] + ".png")
        shutil.copyfile(origem, copia)
        registro = {campo: linha.get(campo) for campo in CAMPOS}
        registro.update(crop_image=copia.relative_to(RAIZ).as_posix(), crop_sha256=sha256(copia),
                        crop_from_workspace=linha["crop_image"])
        registros.append(registro)
    referencia = DESTINO / "referencia.jsonl"
    referencia.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros), encoding="utf-8")
    por_documento = {}
    for r in registros:
        d = por_documento.setdefault(r["document_id"], {"lines": 0, "chars": 0, "reviewers": Counter()})
        d["lines"] += 1
        d["chars"] += len(r["text_diplomatic"])
        d["reviewers"][r["reviewer"]] += 1
    congelamento = {
        "frozen_at": now(),
        "rule": "Referência fixa. Cada configuração final roda uma única vez neste conjunto; nada aqui entra em "
                "treino, escolha de checkpoint ou parâmetros.",
        "reference_sha256": sha256(referencia),
        "lines": len(registros),
        "chars": sum(len(r["text_diplomatic"]) for r in registros),
        "by_document": {k: dict(v, reviewers=dict(v["reviewers"])) for k, v in por_documento.items()},
        "workspaces": revisoes,
        "crops_local_dir": RECORTES.relative_to(RAIZ).as_posix(),
        "model_predictions_before_freeze": 0,
    }
    (DESTINO / "congelamento.json").write_text(json.dumps(congelamento, ensure_ascii=False, indent=1) + "\n",
                                               encoding="utf-8")
    print(json.dumps({k: v for k, v in congelamento.items() if k != "workspaces"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
