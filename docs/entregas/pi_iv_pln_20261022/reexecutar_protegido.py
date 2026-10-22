"""Reexecuta a versão de 22/10 com as proteções acadêmicas já existentes."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = ROOT / 'output/entrega_academica_269r24_20261022'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT / 'tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='guard_entrega_20261022_', dir=ROOT / 'tmp') as temp:
        temp = Path(temp)
        assert temp.resolve().is_relative_to((ROOT / 'tmp').resolve())
        shutil.copyfile(ROOT / 'scripts/ci_academica_guard.py', temp / 'sitecustomize.py')
        env = dict(os.environ, PYTHONPATH=str(temp), PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
                   HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', MPLBACKEND='Agg',
                   PALEOGRAPHIA_CI_ROOT=str(ROOT), PALEOGRAPHIA_CI_LOG=str(OUT / 'protecao.jsonl'),
                   JUPYTER_CONFIG_DIR=str(temp / 'jupyter'), IPYTHONDIR=str(temp / 'ipython'),
                   JUPYTER_RUNTIME_DIR=str(temp / 'runtime'), MPLCONFIGDIR=str(temp / 'matplotlib'))
        subprocess.run([sys.executable, str(BASE / 'executar_notebook.py')], cwd=ROOT,
                       env=env, timeout=600, check=True)
    events = [json.loads(line) for line in (OUT / 'protecao.jsonl').read_text(encoding='utf-8').splitlines()]
    assert not any(e['evento'] == 'bloqueado' for e in events), 'Operação proibida durante a reexecução.'
    assert any(e.get('kernel') for e in events) and any(e.get('kernel') is False for e in events)
    print(json.dumps({'resultado': 'aprovado', 'protecao_executor_e_kernel': True,
                      'operacoes_bloqueadas': 0, 'novas_inferencias': 0}))


if __name__ == '__main__':
    main()
