"""Experimento da noite de 10/11: o treino nas Posturas ajuda a ler um fólio das Posturas que o modelo não viu?

Uso, na raiz do projeto, com Docker aberto e nenhum treino rodando:
    python scripts/treino_noturno.py D1     # mesma receita do C
    python scripts/treino_noturno.py D2     # idem, com 2 variações aumentadas por linha (o C usa 1)
    python scripts/treino_noturno.py C2     # só se o D2 ganhar do D1: receita do D2 com todos os pares do C

Os pares saem de ``pares_C.json``: treino = Traslado + Posturas 100r e 100v; validação = sessão de 1795
+ Posturas 101r (31 linhas, fora do treino). Assim a parada antecipada e a escolha do checkpoint olham
também para as Posturas, e não só para as 7 linhas de 1795. Nenhum destes pesos vai para a aplicação:
é experimento de desenvolvimento, para escolher a receita. O C2 é o candidato final dessa receita:
treina com as 94 linhas das Posturas e valida só em 1795, como o C, para os dois serem comparáveis. O teste reservado continua de fora
(o ``run`` recusa os documentos reservados).
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PARES_C = ROOT / "docs/experimentos/ppocrv6_ajustado_C/dados/pares_C.json"
FOLIO_DEV = "f101r"
VARIANTES = {
    "D1": {"augment_variants": 1},
    "D2": {"augment_variants": 2},
    "C2": {"augment_variants": 2},
}


def pares_dev(segurar=True):
    if not segurar:
        return json.loads(PARES_C.read_text(encoding="utf-8"))
    saida = []
    for par in json.loads(PARES_C.read_text(encoding="utf-8")):
        par = dict(par)
        if par["document_id"].startswith("jundiai_atas") and par["folio"] == FOLIO_DEV:
            par["split"] = "validation"
        saida.append(par)
    return saida


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("variante", choices=sorted(VARIANTES))
    args = parser.parse_args(argv)
    from paleographia.config import load_config
    from paleographia.ppocrv6_finetune import run

    config = load_config(ROOT / "configs/finetune_ppocrv6.toml")
    settings = config["finetune"]
    # Teto de 6 épocas para caber na noite; a parada antecipada (2 épocas sem melhora) continua valendo.
    settings.update(log_every=1, threads=4, memory="7g", max_epochs=6, **VARIANTES[args.variante])
    pares = pares_dev(segurar=args.variante != "C2")
    contagem = {}
    for p in pares:
        chave = f"{p['split']} · {p['document_id']}"
        contagem[chave] = contagem.get(chave, 0) + 1
    saida = ROOT / "output" / f"treino_noturno_{args.variante}_{datetime.now():%Y%m%dT%H%M%S}"
    print(f"{args.variante}: {VARIANTES[args.variante]} · até {settings['max_epochs']} épocas · {saida.name}")
    for chave, n in sorted(contagem.items()):
        print(f"  {chave}: {n}")
    (saida.parent / f"{saida.name}_pares.json").write_text(json.dumps(pares, ensure_ascii=False, indent=1) + "\n",
                                                          encoding="utf-8", newline="\n")
    resultado = run(pares, config, saida, ROOT, execute=True, timeout_hours=7, stream=True)
    prova = resultado.get("evidence", {})
    print(f"Situação: {prova.get('status')} · épocas {prova.get('epochs_run')}")
    if prova.get("selected_checkpoint"):
        print(f"Melhor validação: {float(prova['selected_checkpoint']['validation_score']):.2%}")
        print(f"Peso: {prova['final_weights']['path']}")
    return 0 if prova.get("status") == "executed" else 1


if __name__ == "__main__":
    sys.exit(main())
