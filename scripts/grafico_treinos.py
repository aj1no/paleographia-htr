"""Curvas de validação dos treinos A, B, C, D1 e D2, lidas dos registros publicados.

Uso, na raiz do projeto:  python scripts/grafico_treinos.py
Grava docs/treinos/curvas_validacao.png. Não roda nenhum modelo: só lê os validation_history.json.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
REGISTROS = {
    "A": "docs/experimentos/ppocrv6_ajuste_fino_20261105/gravacao_20261106/treino_A",
    "B": "docs/experimentos/ppocrv6_ajuste_fino_20261105/gravacao_20261107/treino_B",
    "C": "docs/experimentos/ppocrv6_ajustado_C/gravacao_20261110/treino_C",
    "D1": "docs/experimentos/ppocrv6_ajustado_C/noturno_20261110/D1",
    "D2": "docs/experimentos/ppocrv6_ajustado_C/noturno_20261110/D2",
}
CORES = {"A": "#8a8f98", "B": "#5b7fbf", "C": "#c0662f", "D1": "#2f8a5b", "D2": "#9b59b6"}
PAINEIS = [("Validação de 1795 (7 linhas): escolheu o checkpoint de A, B e C", ["A", "B", "C"]),
           ("Validação 101r + 1795 (38 linhas): escolheu o checkpoint de D1 e D2", ["D1", "D2"])]


def curva(nome):
    historico = json.loads((RAIZ / REGISTROS[nome] / "validation_history.json").read_text(encoding="utf-8"))
    pontos, contagem = [], {}
    for item in historico:
        epoca = item["epoch"]
        contagem[epoca] = contagem.get(epoca, 0) + 1
        # Quatro validações por época (freq 0,25): a k-ésima fica em época + k/4.
        pontos.append((epoca + contagem[epoca] / 4, 100 * item["metrics"]["val_accuracy"]))
    return pontos


def main():
    figura, eixos = plt.subplots(1, 2, figsize=(13, 4.6), dpi=150)
    for eixo, (titulo, nomes) in zip(eixos, PAINEIS):
        for nome in nomes:
            pontos = curva(nome)
            x, y = zip(*pontos)
            eixo.plot(x, y, marker="o", markersize=3.5, linewidth=1.8, color=CORES[nome], label=nome)
            melhor = max(range(len(y)), key=lambda i: (y[i], -i))  # o ketos guarda o primeiro a atingir o recorde
            eixo.plot(x[melhor], y[melhor], marker="*", markersize=14, color=CORES[nome],
                      markeredgecolor="white", markeredgewidth=0.8)
            eixo.annotate(f"{nome}: {y[melhor]:.2f}%".replace(".", ","), (x[melhor], y[melhor]),
                          textcoords="offset points", xytext=(6, 6), fontsize=8.5, color=CORES[nome])
        eixo.set_title(titulo, fontsize=10, loc="left")
        eixo.set_xlabel("época de treino")
        eixo.set_ylabel("acerto de caracteres na validação (%)")
        eixo.grid(alpha=0.25)
        eixo.spines[["top", "right"]].set_visible(False)
        eixo.legend(frameon=False, fontsize=9, loc="lower right")
    figura.suptitle("Ajuste fino do PP-OCRv6: acerto na validação a cada quarto de época (estrela = checkpoint escolhido)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    saida = RAIZ / "docs/treinos/curvas_validacao.png"
    saida.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(saida, facecolor="white")
    print(saida.relative_to(RAIZ))


if __name__ == "__main__":
    main()
