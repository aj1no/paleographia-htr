"""Executa 18 células e confere resultados; --checkout-remoto simula a preparação Colab."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

BASE = Path(__file__).resolve().parent


def tabelas(pasta):
    result = {}
    for caminho in sorted(pasta.glob('*.csv')):
        with caminho.open(encoding='utf-8-sig', newline='') as stream:
            result[caminho.name] = list(csv.DictReader(stream))
    return result


def validar(raiz, saida, remoto=False):
    raiz, saida = Path(raiz).resolve(), Path(saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(BASE / 'colaboracao_colab.ipynb', as_version=4)
    if remoto:
        # Apenas explicita o ramo Colab e o destino em um kernel Linux comum.
        # Não simula a interface hospedada nem o download do navegador.
        nb.cells[1].source = nb.cells[1].source.replace(
            'RAIZ_COLAB = preparar_ambiente_colab()',
            'RAIZ_COLAB = preparar_ambiente_colab(colab=True, destino=' + repr(str(raiz)) + ')')
    elif not raiz.is_dir():
        raise ValueError('Checkout local inexistente.')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['MPLBACKEND'] = 'Agg'
    with tempfile.TemporaryDirectory(prefix='kernel_colab_') as temp:
        kernel_root = Path(temp)
        kernel = kernel_root / 'colab-validacao'
        kernel.mkdir()
        (kernel / 'kernel.json').write_text(json.dumps({
            'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
            'display_name': 'Validação do notebook Colab', 'language': 'python',
        }), encoding='utf-8')
        manager = KernelManager(kernel_name='colab-validacao',
            kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
        client = NotebookClient(nb, km=manager, timeout=600, allow_errors=False,
            resources={'metadata': {'path': str(saida if remoto else raiz)}})
        try:
            executado = client.execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
    nbformat.validate(executado)
    cells = [c for c in executado.cells if c.cell_type == 'code']
    assert len(cells) == 18
    assert [c.execution_count for c in cells] == list(range(1, 19))
    assert not any(o.output_type == 'error' for c in cells for o in c.outputs)
    derivados = raiz / 'output/equipe_colab_20261023'
    calculos = derivados / 'calculos'
    arquivado = raiz / 'docs/entregas/pi_iv_pln_20261022'
    resultado = json.loads((calculos / 'resultado_notebook.json').read_bytes())
    referencia = json.loads((arquivado / 'resultado_notebook.json').read_bytes())
    for campo in ['tipo', 'linhas', 'ressalvas', 'regioes', 'metricas', 'reconferencia',
                  'novas_inferencias', 'treino', 'teste_reservado']:
        assert resultado[campo] == referencia[campo], campo
    assert tabelas(calculos / 'tabelas') == tabelas(arquivado / 'tabelas')
    assert len(tabelas(calculos / 'tabelas')) == 6
    equipe = json.loads((derivados / 'resumo_participacao.json').read_bytes())
    assert all(not r['salvo'] and r['estado'] == 'pendente'
               for r in equipe['formularios_desta_execucao'].values())
    assert equipe['registros_individuais_encontrados'] == 0
    assert not list(derivados.glob('contribuicoes_*.zip'))
    nbformat.write(executado, saida / 'execucao_validacao.ipynb')
    recibo = {
        'resultado': 'aprovado', 'tipo': 'linux_com_preparacao_remota' if remoto else 'checkout_local',
        'servico_colab_hospedado_testado': False, 'download_no_navegador_testado': False,
        'celulas_codigo_executadas': 18, 'tabelas_identicas_a_20261022': 6,
        'linhas': resultado['linhas'], 'ressalvas': resultado['ressalvas'],
        'metricas': resultado['metricas'], 'registros_humanos_historicos': 17,
        'novos_registros_individuais': 0, 'novas_inferencias': 0,
        'notebook_sha256': hashlib.sha256((BASE / 'colaboracao_colab.ipynb').read_bytes()).hexdigest(),
        'python': platform.python_version(), 'sistema': platform.system(),
        'ambiente': {n: importlib.metadata.version(n) for n in ['nbformat', 'nbclient', 'ipykernel']},
        'ambiente_kernel': resultado['ambiente'],
    }
    (saida / 'validacao.json').write_text(json.dumps(recibo, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(recibo, ensure_ascii=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raiz', type=Path, default=BASE.parents[2])
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--checkout-remoto', action='store_true')
    args = parser.parse_args()
    validar(args.raiz, args.saida, args.checkout_remoto)
