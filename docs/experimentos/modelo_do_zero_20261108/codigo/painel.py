"""Gera prints/painel_<nome>.png com as curvas do treino e, se houver, linhas de Jundiaí transcritas."""
import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = Path(__file__).resolve().parent
TINTA, SECUNDARIA, GRADE, SERIE = "#1f2328", "#59636e", "#d8dee4", "#2f6fb0"


def eixo(ax, titulo, ylabel):
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    ax.set_xlabel("passo", color=SECUNDARIA)
    ax.set_ylabel(ylabel, color=SECUNDARIA)
    ax.grid(color=GRADE, linewidth=0.6)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=SECUNDARIA)


def main(nome):
    pasta = AQUI / "runs" / nome
    log = [json.loads(x) for x in (pasta / "log.jsonl").read_text(encoding="utf-8").splitlines()] \
        if (pasta / "log.jsonl").exists() else []
    if not log:
        return
    resultado = json.loads((pasta / "resultado.json").read_text(encoding="utf-8")) \
        if (pasta / "resultado.json").exists() else None
    tem_cer = "cer_val_inq" in log[0]
    fig = plt.figure(figsize=(12, 7.5 if resultado else 4.2), dpi=110)
    grade = fig.add_gridspec(2 if resultado else 1, 2, height_ratios=[1, 0.9] if resultado else [1])
    passos = [r["passo"] for r in log]
    ax = fig.add_subplot(grade[0, 0])
    ax.plot(passos, [r["perda"] for r in log], color=SERIE, linewidth=2)
    eixo(ax, "Perda de treino" + (" (CTC)" if tem_cer else " (reconstrução, sem texto)"), "perda")
    if tem_cer:
        ax = fig.add_subplot(grade[0, 1])
        ax.plot(passos, [100 * r["cer_val_inq"] for r in log], color=SERIE, linewidth=2, marker="o", markersize=4)
        melhor = min(log, key=lambda r: r["cer_val_inq"])
        ax.annotate(f"melhor: {100 * melhor['cer_val_inq']:.2f}%", (melhor["passo"], 100 * melhor["cer_val_inq"]),
                    textcoords="offset points", xytext=(-10, 12), ha="right", color=TINTA, fontsize=9)
        eixo(ax, "CER na validação interna (Inquisição, 953 linhas)", "CER (%)")
    elif __import__("relatorio").figura_ssl():
        ax = fig.add_subplot(grade[0, 1])
        ax.imshow(plt.imread(AQUI / "figura_reconstrucao_ssl.png"), cmap="gray", aspect="auto")
        ax.set_axis_off()
        ax.set_title("original / apagado / preenchido pelo modelo", loc="left", fontsize=11, color=TINTA)
    if resultado:
        ax = fig.add_subplot(grade[1, :])
        ax.set_axis_off()
        jdi = resultado["val_jundiai"]
        cab = (f"Jundiaí (medida final, uma vez): CER {100 * jdi['cer']:.2f}%  WER {100 * jdi['wer']:.2f}%   |   "
               f"validação interna: CER {100 * resultado['val_inq']['cer']:.2f}%   |   {resultado['checkpoint']}")
        linhas = [cab, ""]
        for x in jdi["linhas_transcritas"][:6]:
            linhas.append(textwrap.shorten(f"ref.:   {x['referencia']}", 120))
            linhas.append(textwrap.shorten(f"modelo: {x['modelo']}", 120))
        ax.text(0, 1, "\n".join(linhas), va="top", family="monospace", fontsize=9, color=TINTA)
    fig.suptitle(f"PaleographIA do zero — {nome}", x=0.01, ha="left", fontsize=13, color=TINTA)
    fig.tight_layout()
    (AQUI / "prints").mkdir(exist_ok=True)
    fig.savefig(AQUI / "prints" / f"painel_{nome}.png")


if __name__ == "__main__":
    main(sys.argv[1])
