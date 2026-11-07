"""Gráfico (SVG, sem dependências) do CSV gravado por scripts/desempenho_treino.ps1.

Uso: python scripts/grafico_desempenho.py desempenho.csv saida.svg "Título"
Seis painéis pequenos, um por medida, cada um com o próprio eixo (nunca dois eixos no mesmo painel).
"""
import csv
import sys
from datetime import datetime
from html import escape

SUPERFICIE, TINTA, TINTA2, GRADE, SERIE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
PAINEIS = [  # coluna, título, unidade, mínimo, máximo (None = automático)
    ("gpu_uso_pct", "Uso da GPU", "%", 0, 100),
    ("gpu_mem_mib", "Memória da GPU (de 4.096 MiB)", "MiB", 0, 4096),
    ("gpu_temp_c", "Temperatura da GPU", "°C", 0, 100),
    ("gpu_potencia_w", "Potência da GPU (limite 50 W)", "W", 0, 50),
    ("cpu_windows_pct", "CPU do Windows", "%", 0, 100),
    ("ram_usada_gb", "Memória do Windows em uso", "GB", 0, None),
]


def ler(caminho):
    with open(caminho, encoding="utf-8-sig") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    horas = [datetime.fromisoformat(r["horario"]) for r in linhas]
    return linhas, horas


def painel(x0, y0, w, h, linhas, horas, coluna, titulo, unidade, vmin, vmax):
    valores = [float(r[coluna]) if r[coluna] else None for r in linhas]
    validos = [v for v in valores if v is not None]
    if vmax is None:
        vmax = float(linhas[0].get("ram_total_gb") or max(validos))
    t0, t1 = horas[0].timestamp(), horas[-1].timestamp()
    px = lambda t: x0 + (t.timestamp() - t0) / (t1 - t0) * w  # noqa: E731
    py = lambda v: y0 + h - (v - vmin) / (vmax - vmin) * h  # noqa: E731
    media = sum(validos) / len(validos)
    out = [f'<text x="{x0}" y="{y0 - 22}" font-size="14" font-weight="600" fill="{TINTA}">{escape(titulo)}</text>',
           f'<text x="{x0}" y="{y0 - 6}" font-size="12" fill="{TINTA2}">média {media:.1f} {unidade} · '
           f'mín. {min(validos):.1f} · máx. {max(validos):.1f}</text>']
    for frac in (0, 0.5, 1):
        v = vmin + frac * (vmax - vmin)
        y = py(v)
        out.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        out.append(f'<text x="{x0 - 6}" y="{y + 4:.1f}" font-size="11" fill="{TINTA2}" text-anchor="end">{v:g}</text>')
    pontos = " ".join(f"{px(t):.1f},{py(v):.1f}" for t, v in zip(horas, valores) if v is not None)
    out.append(f'<polyline points="{pontos}" fill="none" stroke="{SERIE}" stroke-width="2" '
               'stroke-linejoin="round" stroke-linecap="round"/>')
    passo = 1800  # rótulo a cada 30 min
    t = (int(t0) // passo + 1) * passo
    while t < t1:
        x = x0 + (t - t0) / (t1 - t0) * w
        out.append(f'<text x="{x:.1f}" y="{y0 + h + 16}" font-size="11" fill="{TINTA2}" text-anchor="middle">'
                   f'{datetime.fromtimestamp(t):%H:%M}</text>')
        t += passo
    return out


def main(entrada, saida, titulo):
    linhas, horas = ler(entrada)
    largura, w, h, gx, gy, topo = 960, 380, 120, 100, 70, 96
    corpo = [f'<rect width="100%" height="100%" fill="{SUPERFICIE}"/>',
             f'<text x="24" y="34" font-size="18" font-weight="700" fill="{TINTA}">{escape(titulo)}</text>',
             f'<text x="24" y="56" font-size="12" fill="{TINTA2}">{horas[0]:%d/%m/%Y %H:%M} a {horas[-1]:%H:%M} · '
             f'{len(linhas)} medições a cada 30 s · fonte: nvidia-smi, Windows e docker stats</text>']
    for i, (coluna, nome, unidade, vmin, vmax) in enumerate(PAINEIS):
        x0 = 60 + (i % 2) * (w + gx)
        y0 = topo + 40 + (i // 2) * (h + gy)
        corpo += painel(x0, y0, w, h, linhas, horas, coluna, nome, unidade, vmin, vmax)
    altura = topo + 40 + 3 * (h + gy) - 20
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
           f'viewBox="0 0 {largura} {altura}" font-family="Segoe UI, Arial, sans-serif">'
           f'<title>{escape(titulo)}</title>' + "".join(corpo) + "</svg>\n")
    with open(saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(svg)


if __name__ == "__main__":
    main(*sys.argv[1:4])
