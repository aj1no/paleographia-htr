"""Audita e reexecuta o notebook congelado em checkout limpo, sem inferência."""
import argparse
import base64
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

DELIVERY = Path('docs/entregas/pi_iv_pln_20261020')
OUTPUT = Path('output/entrega_academica_269r24_20261020')
DOUBTS = [11, 15, 16, 17, 19, 20, 23, 24]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def check_environment(root):
    require(not (root/OUTPUT).exists(), 'A saída já existe. Use um checkout limpo; derivados existentes não serão sobrescritos.')
    for name in ['models', 'data/workspace', 'data/workspace_traslado_269r']:
        require(not (root/name).exists(), 'Use checkout sem pesos ou workspace: '+name)


def snapshot(root):
    records = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root).decode().split('\0')
    result = {}
    for record in filter(None, records):
        metadata, name = record.split('\t', 1)
        if metadata.split()[0] == '160000':
            continue
        path = root/name
        require(path.is_file(), 'Entrada versionada ausente: '+name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def source(cell):
    text = cell['source']
    return ''.join(text) if isinstance(text, list) else text


def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def verify_generated(root, output):
    archived = root/DELIVERY
    result = read(output/'resultado_notebook.json')
    original = read(archived/'resultado_notebook.json')
    for key in ['tipo', 'linhas', 'ressalvas', 'regioes', 'metricas',
                'arquivos_experimento_inalterados', 'novas_inferencias', 'treino', 'teste_reservado']:
        require(result[key] == original[key], 'Recálculo divergente: '+key)
    require(result['linhas'] == 24 and result['ressalvas'] == 8 and result['regioes'] == 5,
            'Linhas, ressalvas ou blocos divergentes.')
    require(result['novas_inferencias'] == 0 and not result['treino'] and not result['teste_reservado'],
            'Resultado promovido indevidamente ou nova inferência declarada.')
    require(result['workspace_conferido'] is False and result['workspace_arquivos_inalterados'] is None,
            'A reprodução deve ocorrer sem workspace.')
    notebook, saved = read(output/'comparacao_reproduzivel.ipynb'), read(archived/'comparacao_reproduzivel.ipynb')
    require([(c['cell_type'], source(c)) for c in notebook['cells']] ==
            [(c['cell_type'], source(c)) for c in saved['cells']], 'Fontes do notebook foram alteradas.')
    cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
    require(len(cells) == 9 and [c['execution_count'] for c in cells] == list(range(1, 10)),
            'Notebook não executado integralmente.')
    require(all(o['output_type'] != 'error' for c in cells for o in c['outputs']), 'Erro em célula do notebook.')
    images = [o['data']['image/png'] for c in cells for o in c['outputs'] if 'image/png' in o.get('data', {})]
    require(len(images) == 2 and all(base64.b64decode(''.join(i) if isinstance(i, list) else i).startswith(b'\x89PNG')
                                  for i in images), 'Figuras incorporadas ausentes.')
    expected_csv = {p.name for p in (archived/'tabelas').glob('*.csv')}
    require(len(expected_csv) == 5 and {p.name for p in (output/'tabelas').glob('*.csv')} == expected_csv,
            'Conjunto de tabelas divergente.')
    for name in expected_csv:
        require(csv_rows(output/'tabelas'/name) == csv_rows(archived/'tabelas'/name), 'Tabela divergente: '+name)
    require([int(r['linha']) for r in csv_rows(output/'tabelas/ressalvas.csv')] == DOUBTS, 'Oito ressalvas perdidas.')
    from PIL import Image
    for name in ['cer_wer', 'cer_blocos']:
        with Image.open(output/'figuras'/(name+'.png')) as image:
            require(image.width >= 1000 and image.height >= 600, 'Figura PNG incompleta.')
            image.verify()
        require(ET.parse(output/'figuras'/(name+'.svg')).getroot().tag.endswith('svg'), 'SVG inválido.')
    preview = (output/'comparacao_reproduzivel.html').read_text(encoding='utf-8')
    require(preview.count('data:image/png;base64,') == 2 and '<script src=' not in preview, 'HTML incompleto ou externo.')
    require('diagnóstico de desenvolvimento' in preview.lower(), 'Identificação de desenvolvimento ausente.')
    return {'linhas': 24, 'ressalvas': DOUBTS, 'regioes': 5, 'metricas': result['metricas'],
            'celulas_codigo_executadas': 9, 'figuras_incorporadas': 2,
            'tabelas_identicas': 5, 'figuras_png_svg': 4, 'novas_inferencias': 0}


def run(root):
    root = Path(root).resolve()
    check_environment(root)
    before = snapshot(root)
    output = root/OUTPUT
    output.mkdir(parents=True)
    report = {'resultado': 'em_execucao', 'tipo': 'diagnostico_de_desenvolvimento', 'novas_inferencias': 0}
    env = dict(os.environ, PYTHONPATH=str(root/'src'), PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', MPLBACKEND='Agg')
    auditor = root/DELIVERY/'verificar_entrega.py'
    try:
        subprocess.run([sys.executable, str(auditor)], cwd=root, env=env, check=True)
        (root/'tmp').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='ci_academica_', dir=root/'tmp') as temp:
            temp = Path(temp)
            require(temp.resolve().is_relative_to((root/'tmp').resolve()), 'Diretório temporário fora da área prevista.')
            shutil.copyfile(Path(__file__).with_name('ci_academica_guard.py'), temp/'sitecustomize.py')
            guarded = dict(env, PYTHONPATH=str(temp), PALEOGRAPHIA_CI_ROOT=str(root),
                           PALEOGRAPHIA_CI_LOG=str(output/'protecao.jsonl'),
                           JUPYTER_CONFIG_DIR=str(temp/'jupyter'), IPYTHONDIR=str(temp/'ipython'),
                           JUPYTER_RUNTIME_DIR=str(temp/'runtime'), MPLCONFIGDIR=str(temp/'matplotlib'))
            subprocess.run([sys.executable, str(root/DELIVERY/'executar_notebook.py')],
                           cwd=root, env=guarded, timeout=600, check=True)
        events = [json.loads(line) for line in (output/'protecao.jsonl').read_text(encoding='utf-8').splitlines()]
        require(not any(e['evento'] == 'bloqueado' for e in events), 'A execução tentou uma operação proibida.')
        require(any(e.get('kernel') for e in events) and any(e.get('kernel') is False for e in events),
                'Proteções não confirmadas no executor e no kernel.')
        report.update(verify_generated(root, output))
        subprocess.run([sys.executable, str(auditor)], cwd=root, env=env, check=True)
        require(snapshot(root) == before, 'Um arquivo versionado foi alterado durante a reprodução.')
        for name in ['models', 'data/workspace', 'data/workspace_traslado_269r']:
            require(not (root/name).exists(), 'Diretório de pesos/workspace foi criado: '+name)
        report.update(resultado='aprovado', arquivos_versionados_preservados=len(before),
                      protecao_executor_e_kernel=True, entrada_sem_pesos_e_workspace=True)
    except Exception as exc:
        report.update(resultado='reprovado', erro=str(exc))
        raise
    finally:
        if snapshot(root) != before:
            report.update(resultado='reprovado', arquivos_versionados_preservados=False)
        (output/'ci_academica.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='Checkout limpo a conferir.')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.root), ensure_ascii=True))
    except Exception as exc:
        print('CI acadêmica: '+str(exc), file=sys.stderr)
        raise SystemExit(2)
