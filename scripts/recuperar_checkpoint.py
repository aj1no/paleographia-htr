"""Recupera o peso de um treino interrompido (queda de energia, atualização do Windows, tempo esgotado).

Uso, na raiz do projeto, com Docker aberto:
    python scripts/recuperar_checkpoint.py output/treino_noturno_D1_20261110T215803

O treino só exporta o peso (``best_*.safetensors``) no fim. Se ele é cortado antes, os checkpoints
``checkpoint_<época>-<acerto>.ckpt`` continuam na pasta. Este script escolhe o de maior acerto de
validação (no empate, o mais antigo, como o ``ketos``) e o converte com ``ketos convert``, na mesma
imagem Docker do treino, sem rede. Grava ``recuperacao.json`` com o checkpoint usado e o SHA-256.
Foi assim que o D1 foi salvo em 11/11/2026 (docs/experimentos/ppocrv6_ajustado_C/noturno_20261110).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
NOME = re.compile(r"^checkpoint_(\d+)-(\d\.\d+)(?:-v(\d+))?\.ckpt$")


def escolher(pasta):
    """O checkpoint de maior acerto; no empate, o de época menor e sem sufixo de versão (o primeiro salvo)."""
    candidatos = []
    for arquivo in pasta.glob("checkpoint_*.ckpt"):
        achado = NOME.match(arquivo.name)
        if achado:
            epoca, acerto, versao = int(achado[1]), float(achado[2]), int(achado[3] or 0)
            candidatos.append((-acerto, epoca, versao, arquivo))
    if not candidatos:
        raise SystemExit(f"Nenhum checkpoint em {pasta}.")
    return min(candidatos)[3]


def main(argv=None):
    from paleographia.config import load_config
    from paleographia.io import now, sha256

    sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit(__doc__)
    treino = (RAIZ / argv[0]).resolve()
    pasta = treino / "checkpoints"
    if list(pasta.glob("best_*.safetensors")):
        raise SystemExit("Este treino já exportou o peso; nada a recuperar.")
    escolhido = escolher(pasta)
    acerto = NOME.match(escolhido.name)[2]
    saida = pasta / f"best_{acerto}_recuperado.safetensors"
    imagem = load_config(RAIZ / "configs/finetune_ppocrv6.toml")["finetune"]["docker_image_id"]
    comando = ["docker", "run", "--rm", "--pull", "never", "--network", "none",
               "--mount", f"type=bind,source={pasta},target=/ck", imagem,
               "ketos", "convert", "-o", f"/ck/{saida.name}", f"/ck/{escolhido.name}"]
    print("Convertendo", escolhido.name, "→", saida.name, flush=True)
    subprocess.run(comando, check=True)
    registro = {"recovered_at": now(), "checkpoint": escolhido.name, "validation_score": float(acerto),
                "weights": saida.name, "sha256": sha256(saida), "docker_image_id": imagem,
                "note": "Treino interrompido antes da exportação; checkpoint escolhido pelo maior acerto de validação."}
    (treino / "recuperacao.json").write_text(json.dumps(registro, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Peso recuperado: {saida.relative_to(RAIZ)} (SHA-256 {registro['sha256'][:16]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
