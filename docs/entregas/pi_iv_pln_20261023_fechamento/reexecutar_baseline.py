"""Reexecuta o Colab publicado localmente, com as proteções acadêmicas existentes."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = ROOT / 'output/fechamento_20261023/baseline'


def main(saida=OUT):
    saida = Path(saida).resolve()
    if not saida.is_relative_to(ROOT / 'output'):
        raise ValueError('A saída da validação deve ficar em output/.')
    saida.mkdir(parents=True, exist_ok=True)
    (ROOT / 'tmp').mkdir(exist_ok=True)
    log = saida / 'protecao.jsonl'
    if log.exists():
        raise ValueError('Recibo de proteção já existe; preserve a rodada anterior antes de executar outra.')
    # Preserva o cache da rodada em tmp/. No Windows/OneDrive, a limpeza
    # automática pode falhar mesmo depois do encerramento correto do kernel.
    temp = Path(tempfile.mkdtemp(prefix='guard_fechamento_', dir=ROOT / 'tmp')).resolve()
    assert temp.is_relative_to((ROOT / 'tmp').resolve())
    shutil.copyfile(ROOT / 'scripts/ci_academica_guard.py', temp / 'sitecustomize.py')
    env = dict(os.environ, PYTHONPATH=str(temp), PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
        PALEOGRAPHIA_CI_ROOT=str(ROOT), PALEOGRAPHIA_CI_LOG=str(log),
        HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', MPLBACKEND='Agg',
        JUPYTER_CONFIG_DIR=str(temp / 'jupyter'), IPYTHONDIR=str(temp / 'ipython'),
        JUPYTER_RUNTIME_DIR=str(temp / 'runtime'), MPLCONFIGDIR=str(temp / 'matplotlib'))
    subprocess.run([sys.executable,
        str(ROOT / 'docs/entregas/pi_iv_pln_20261023_colab/validar_colab.py'),
        '--raiz', str(ROOT), '--saida', str(saida)], cwd=ROOT, env=env, check=True, timeout=600)
    events = [json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
    assert not any(e['evento'] == 'bloqueado' for e in events)
    assert any(e.get('kernel') for e in events) and any(e.get('kernel') is False for e in events)
    print(json.dumps(dict(resultado='aprovado', protecao_executor_e_kernel=True,
        operacoes_bloqueadas=0, novas_inferencias=0, treino=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, default=OUT)
    main(parser.parse_args().saida)
