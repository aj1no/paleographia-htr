"""Reutiliza o diagramador PLN2026 preservado, lendo o artigo desta versão."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    gerador = runpy.run_path(str(BASE.parent / 'pi_iv_pln_20261023_entrega/gerar_artigo.py'))
    gerar = gerador['main']
    gerar.__globals__['BASE'] = BASE
    gerar()
