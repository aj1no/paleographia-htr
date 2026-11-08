"""Roda a sequência da noite, um treino por vez, retomando do que já terminou.

Ordem (do mais importante para a curiosidade):
 1. supervisionado_do_zero   CRNN-CTC com pesos aleatórios e todas as linhas rotuladas
 2. ssl                      pré-treino não supervisionado (sem nenhum texto)
 3. sonda_ssl / sonda_aleatoria   encoder congelado; só a camada de saída aprende
 4. poucos_rotulos_*         5% das linhas rotuladas: do zero × a partir do pré-treino
 5. ssl_ajuste_completo      pré-treino + todas as linhas rotuladas
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PY = sys.executable
TRAVA = AQUI / "runs" / ".treinando"

ETAPAS = [
    ("supervisionado_do_zero", ["treinar.py", "--nome", "supervisionado_do_zero", "--passos", "{P_SUP}"]),
    ("ssl", ["pretreino_ssl.py", "--nome", "ssl", "--passos", "{P_SSL}"]),
    ("sonda_ssl", ["treinar.py", "--nome", "sonda_ssl", "--passos", "{P_SONDA}", "--init", "runs/ssl/encoder.pt",
                   "--congelar", "--avaliar_cada", "500"]),
    ("sonda_aleatoria", ["treinar.py", "--nome", "sonda_aleatoria", "--passos", "{P_SONDA}", "--congelar",
                         "--avaliar_cada", "500"]),
    ("poucos_rotulos_do_zero", ["treinar.py", "--nome", "poucos_rotulos_do_zero", "--passos", "{P_POUCOS}",
                                "--fracao", "0.05", "--avaliar_cada", "500"]),
    ("poucos_rotulos_ssl", ["treinar.py", "--nome", "poucos_rotulos_ssl", "--passos", "{P_POUCOS}",
                            "--fracao", "0.05", "--init", "runs/ssl/encoder.pt", "--avaliar_cada", "500"]),
    ("ssl_ajuste_completo", ["treinar.py", "--nome", "ssl_ajuste_completo", "--passos", "{P_SUP}",
                             "--init", "runs/ssl/encoder.pt"]),
]


def feito(nome):
    pasta = AQUI / "runs" / nome
    return (pasta / "resultado.json").exists() or (pasta / "FIM").exists()


def main():
    passos = json.loads((AQUI / "passos.json").read_text())
    (AQUI / "runs").mkdir(exist_ok=True)
    if TRAVA.exists():
        raise SystemExit(f"já há um treino rodando (trava {TRAVA}); um por vez")
    TRAVA.write_text(str(os.getpid()))
    if os.name == "nt":  # impede o sono por inatividade só enquanto este processo roda
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    try:
        for nome, args in ETAPAS:
            if feito(nome):
                print(f"[{time.strftime('%H:%M')}] {nome}: já feito", flush=True)
                continue
            pasta = AQUI / "runs" / nome
            pasta.mkdir(parents=True, exist_ok=True)
            cmd = [PY, "-u"] + [x.format(**passos) for x in args]
            print(f"[{time.strftime('%H:%M')}] {nome}: começando", " ".join(cmd[2:]), flush=True)
            with (pasta / "console.log").open("w", encoding="utf-8") as saida:
                proc = subprocess.Popen(cmd, cwd=AQUI, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        env=os.environ | {"PYTHONIOENCODING": "utf-8"}, text=True,
                                        encoding="utf-8", errors="replace", bufsize=1)
                for texto in proc.stdout:  # mostra na janela e guarda no log
                    saida.write(texto)
                    saida.flush()
                    if not texto.startswith("{"):
                        print(f"  {nome} | {texto.rstrip()[:150]}", flush=True)
                r = proc
                r.wait()
            subprocess.run([PY, "painel.py", nome], cwd=AQUI)
            if r.returncode != 0:
                print(f"[{time.strftime('%H:%M')}] {nome}: FALHOU (código {r.returncode}); veja console.log", flush=True)
                continue
            if nome == "ssl":
                (pasta / "FIM").write_text(time.strftime("%Y-%m-%dT%H:%M:%S"))
            print(f"[{time.strftime('%H:%M')}] {nome}: terminou", flush=True)
    finally:
        TRAVA.unlink(missing_ok=True)
    subprocess.run([PY, "relatorio.py"], cwd=AQUI)


if __name__ == "__main__":
    main()
