"""Roda o ajuste fino do PP-OCRv6 mostrando o progresso no terminal (para acompanhar ou gravar).

Uso, na raiz do projeto, com Docker Desktop aberto:
    python scripts/treinar_ao_vivo.py demo   # ~6 min na GTX 1650: 40 linhas do Traslado, 1 época
    python scripts/treinar_ao_vivo.py A      # Traslado (191 linhas), até 12 épocas
    python scripts/treinar_ao_vivo.py B      # Traslado + 550 linhas públicas da Inquisição

Cada execução grava em uma pasta nova de output/ (console.log, validações, checkpoints).
O treino roda no contêiner Docker: na GPU NVIDIA se houver (imagem de treino CUDA),
senão na CPU, muito mais lenta. O teste reservado (pagamento) é recusado pelo código.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DADOS = ROOT / "docs/experimentos/ppocrv6_ajuste_fino_20261105/dados"


def gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def treino_em_andamento():
    """Nomes de contêineres de treino já rodando (dois treinos juntos esgotam GPU e memória)."""
    try:
        out = subprocess.run(["docker", "ps", "--filter", "name=paleographia-finetune", "--format", "{{.Names}}"],
                             capture_output=True, text=True, timeout=30)
        return [n for n in out.stdout.split() if n]
    except (OSError, subprocess.TimeoutExpired):
        return []


def pares(modo):
    if modo == "B":
        return json.loads((DADOS / "pares_traslado_mais_inquisicao.json").read_text(encoding="utf-8"))
    todos = json.loads((DADOS / "pares_filtrados.json").read_text(encoding="utf-8"))
    if modo == "demo":
        treino = [p for p in todos if p["split"] == "train"][:40]
        return treino + [p for p in todos if p["split"] == "validation"]
    return todos


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("modo", choices=["demo", "A", "B"])
    args = parser.parse_args(argv)
    from paleographia.config import load_config
    from paleographia.ppocrv6_finetune import run

    rodando = treino_em_andamento()
    if rodando:
        print(f"Já existe um treino rodando ({', '.join(rodando)}). Espere terminar ou pare-o antes:")
        print("  docker rm -f " + " ".join(rodando))
        return 2
    config = load_config(ROOT / "configs/finetune_ppocrv6.toml")
    settings = config["finetune"]
    placa = gpu()
    if not placa:
        settings.update(device="cpu", docker_image_id=config["recognition"]["docker_image_id"])
    settings["log_every"] = 1
    if args.modo == "demo":
        # Folga para o gravador de tela e o Windows: menos núcleos e memória no contêiner.
        settings.update(max_epochs=1, min_epochs=1, freq=0.5, augment_variants=0, lag=2, quit="fixed",
                        threads=3, memory="5g")
    selecionados = pares(args.modo)
    faltando = [p["crop_image"] for p in selecionados if not (ROOT / p["crop_image"]).is_file()]
    contagem = {}
    for p in selecionados:
        chave = f"{p['split']} · {p['label_source']}"
        contagem[chave] = contagem.get(chave, 0) + 1
    saida = ROOT / "output" / f"treino_ao_vivo_{args.modo}_{datetime.now():%Y%m%dT%H%M%S}"

    print("=" * 78)
    print(f"PaleographIA · ajuste fino do PP-OCRv6 medium · modo {args.modo}")
    print(f"Início: {datetime.now():%d/%m/%Y %H:%M:%S}")
    print(f"Dispositivo: {'GPU ' + placa if placa else 'CPU (sem GPU NVIDIA; bem mais lento)'}")
    print(f"Imagem Docker: {settings.get('docker_image_id') or config['recognition']['docker_image_id']}")
    print("Dados:")
    for chave, n in sorted(contagem.items()):
        print(f"  {n:4d}  {chave}")
    print(f"Taxa {settings['learning_rate']}, lote {settings['batch_size']} (acumula {settings['accumulate']}), "
          f"até {settings['max_epochs']} época(s), BatchNorm congelada, rótulos {settings['normalization']}")
    print(f"Saída: {saida.relative_to(ROOT)}")
    print("=" * 78, flush=True)
    if faltando:
        print(f"Faltam {len(faltando)} recortes (ex.: {faltando[0]}). Gere-os antes com o pipeline de dados.")
        return 1
    inicio = time.monotonic()
    resultado = run(selecionados, config, saida, ROOT, execute=True, timeout_hours=12, stream=True)
    prova = resultado.get("evidence", {})
    print("=" * 78)
    print(f"Fim: {datetime.now():%d/%m/%Y %H:%M:%S} · duração {(time.monotonic() - inicio) / 60:.1f} min")
    print(f"Situação: {prova.get('status')} · passos {prova.get('optimizer_steps')} · épocas {prova.get('epochs_run')}")
    if prova.get("selected_checkpoint"):
        print(f"Melhor validação: {float(prova['selected_checkpoint']['validation_score']):.2%} de acerto de caracteres")
        print(f"Peso exportado: {prova['final_weights']['path']} (SHA-256 {prova['final_weights']['sha256'][:16]}…)")
    if prova.get("reason"):
        print(f"Motivo: {prova['reason']}")
    print("=" * 78)
    return 0 if prova.get("status") == "executed" else 1


if __name__ == "__main__":
    sys.exit(main())
