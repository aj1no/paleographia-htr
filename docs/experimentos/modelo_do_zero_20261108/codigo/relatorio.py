"""Junta os resultados de runs/ em RESULTADOS.md e gera a figura da reconstrução não supervisionada."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
RUNS = AQUI / "runs"

DESCRICAO = {
    "supervisionado_do_zero": "Pesos aleatórios, todas as linhas rotuladas",
    "ssl_ajuste_completo": "Pré-treino não supervisionado + todas as linhas rotuladas",
    "poucos_rotulos_do_zero": "Pesos aleatórios, 5% das linhas rotuladas",
    "poucos_rotulos_ssl": "Pré-treino não supervisionado + 5% das linhas rotuladas",
    "sonda_aleatoria": "Encoder aleatório congelado; só a saída aprende",
    "sonda_ssl": "Encoder do pré-treino congelado; só a saída aprende",
}
REFERENCIA_PROJETO = [  # números do projeto principal na mesma validação de 1795 (7 linhas)
    ("PP-OCRv6 medium (pré-treinado, sem ajuste)", 0.1420, 0.5672),
    ("PP-OCRv6 ajustado A (Traslado)", 0.1072, 0.4179),
    ("PP-OCRv6 ajustado B (Traslado + Inquisição)", 0.1014, 0.3881),
]


def pct(x):
    return f"{100 * x:.2f}%".replace(".", ",")


def figura_ssl():
    exemplos = sorted((RUNS / "ssl").glob("exemplo_*.npz"), key=lambda p: int(p.stem.split("_")[1]))
    if not exemplos:
        return None
    d = np.load(exemplos[-1])
    orig, ent, rec = d["original"], d["entrada"], d["reconstrucao_coluna_norm"]
    H, W = orig.shape
    T = rec.shape[0]
    blocos = orig[:, : T * 4].reshape(H, T, 4).transpose(1, 0, 2).reshape(T, H * 4)
    # só para exibir: devolve média e desvio de cada coluna original
    rec = rec * (blocos.std(-1, keepdims=True) + 1e-3) + blocos.mean(-1, keepdims=True)
    rec = rec.reshape(T, H, 4).transpose(1, 0, 2).reshape(H, T * 4)
    mascarado = (ent[:, : T * 4] == 0).all(0)
    montagem = ent[:, : T * 4].copy()
    montagem[:, mascarado] = rec[:, mascarado]
    linhas = [orig[:, : T * 4], ent[:, : T * 4], montagem]
    img = np.concatenate([np.pad(1 - np.clip(x, 0, 1), ((4, 4), (0, 0)), constant_values=1) for x in linhas])
    destino = AQUI / "figura_reconstrucao_ssl.png"
    Image.fromarray((img * 255).astype(np.uint8)).save(destino)
    return destino.name


def main():
    linhas = ["# Modelo do zero e treino não supervisionado — resultados", ""]
    resumo = json.loads((AQUI / "dados/resumo.json").read_text(encoding="utf-8"))
    linhas += ["Dados: " + ", ".join(f"{k}: {v}" for k, v in resumo.items()), ""]
    linhas += ["| Experimento | Linhas rotuladas | Passos | Checkpoint | CER val. Inquisição | CER 1795 | WER 1795 | CER 1767 | Min |",
               "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |"]
    for nome, desc in DESCRICAO.items():
        r_path = RUNS / nome / "resultado.json"
        if not r_path.exists():
            linhas.append(f"| {desc} | — | — | não terminou | | | | | |")
            continue
        r = json.loads(r_path.read_text(encoding="utf-8"))
        c = json.loads((RUNS / nome / "config.json").read_text(encoding="utf-8"))
        doc = r["val_jundiai"]["por_documento"]
        s95 = doc.get("sessao_1795", {})
        c67 = doc.get("carta_jose_gomes_1767", {})
        linhas.append(f"| {desc} | {c['linhas_rotuladas']} | {c['passos']} | {r['checkpoint'].split(' (')[0]} | "
                      f"{pct(r['val_inq']['cer'])} | {pct(s95.get('cer', float('nan')))} | "
                      f"{pct(s95.get('wer', float('nan')))} | {pct(c67.get('cer', float('nan')))} | {r['minutos']} |")
    linhas += ["", "Referência do projeto principal na mesma validação de 1795 (7 linhas):", "",
               "| Modelo | CER | WER |", "| --- | ---: | ---: |"]
    linhas += [f"| {n} | {pct(c)} | {pct(w)} |" for n, c, w in REFERENCIA_PROJETO]
    fig = figura_ssl()
    if fig:
        linhas += ["", f"![Reconstrução do pré-treino não supervisionado]({fig})", "",
                   "De cima para baixo: linha original; linha com trechos apagados; trechos apagados preenchidos "
                   "pelo modelo (contraste de cada coluna devolvido só para a figura)."]
    melhor = RUNS / "supervisionado_do_zero" / "resultado.json"
    if melhor.exists():
        r = json.loads(melhor.read_text(encoding="utf-8"))
        linhas += ["", "## Linhas de Jundiaí transcritas pelo modelo do zero", "", "| Documento | Referência | Modelo |",
                   "| --- | --- | --- |"]
        linhas += [f"| {x['documento']} | {x['referencia']} | {x['modelo']} |" for x in r["val_jundiai"]["linhas_transcritas"]]
    (AQUI / "RESULTADOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
