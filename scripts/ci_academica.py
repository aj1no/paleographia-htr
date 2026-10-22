"""Audita e reexecuta uma das entregas congeladas em checkout limpo, sem inferência."""
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

DEFAULT_VERSION = '20261020'
VERSIONS = {'20261020': {'cells': 9, 'tables': 5}, '20261022': {'cells': 10, 'tables': 6}}
# Os caminhos padrão preservam o uso anterior sem argumentos.
DELIVERY = Path('docs/entregas/pi_iv_pln_' + DEFAULT_VERSION)
OUTPUT = Path('output/entrega_academica_269r24_' + DEFAULT_VERSION)
DOUBTS = [11, 15, 16, 17, 19, 20, 23, 24]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def delivery_paths(version):
    require(version in VERSIONS, 'Versão acadêmica não permitida: ' + str(version))
    return Path('docs/entregas/pi_iv_pln_' + version), Path('output/entrega_academica_269r24_' + version)


def check_environment(root, version=DEFAULT_VERSION):
    _, output = delivery_paths(version)
    require(not (root/output).exists(), 'A saída já existe. Use um checkout limpo; derivados existentes não serão sobrescritos.')
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


def verify_reconference(root, output, archived):
    result = read(output/'resultado_notebook.json')['reconferencia']
    require(result == read(archived/'resultado_notebook.json')['reconferencia'],
            'Recibo da reconferência divergente.')
    review = root/'docs/revisao_humana/traslado_269r/reconferencia_ressalvas_20261021'
    consolidated = read(review/'consolidacao.json')
    require(result['linhas'] == DOUBTS and result['registros_humanos'] == 17
            and result['pacote_20261020_preservado'] is True
            and result['catalogo_promovido'] is False and result['alvos_alterados'] is False
            and result['leitura_independente_da_edicao'] is False,
            'Reconferência promovida indevidamente.')
    require(result['inventario_sha256'] == hashlib.sha256((review/'inventario.json').read_bytes()).hexdigest(),
            'Origem da reconferência divergente.')
    require(consolidated['novo_total_de_linhas_validadas_no_catalogo'] is None
            and not consolidated['duvidas_foram_zeradas']
            and not consolidated['referencia_humana_independente_da_edicao']
            and consolidated['linhas_com_duvidas_visuais_expressamente_mantidas'] == [11, 19, 23, 24],
            'Dúvidas ou dependência da edição alteradas.')
    require(len(consolidated['historico']['eventos_humanos_ordenados']) == 17,
            'Histórico de decisões incompleto.')
    rows = csv_rows(output/'tabelas/reconferencia_ressalvas.csv')
    require([int(row['linha']) for row in rows] == DOUBTS, 'Reconferência sem as oito ressalvas históricas.')
    original_rows = {int(r['linha']): r for r in csv_rows(root/DELIVERY/'tabelas/ressalvas.csv')}
    for row, decision in zip(rows, consolidated['resultados_por_linha']):
        require(int(row['linha']) == decision['linha']
                and row['alvo_congelado_20261020'] == decision['texto_adotado_na_referencia_congelada']
                == original_rows[decision['linha']]['alvo_adotado'], 'Alvo histórico alterado na reconferência.')
        require(row['ressalva_original_20261020'] == original_rows[decision['linha']]['ressalva_preservada'],
                'Ressalva histórica apagada na reconferência.')
        for field, key in [('decisao_reconferencia_20261021', 'trecho_adotado'),
                           ('confirmacoes_visuais_pontuais', 'confirmacoes_visuais_novas'),
                           ('apoio_editorial', 'apoio_editorial'),
                           ('duvidas_visuais_mantidas', 'duvidas_visuais_preservadas')]:
            expected = decision[key]
            require(row[field] == ('; '.join(expected) if isinstance(expected, list) else expected),
                    'Decisão ou dúvida alterada na reconferência: ' + field)
        require(row['revisor'] == consolidated['revisor'], 'Autoria da reconferência divergente.')
        paths = [(review/name).relative_to(root).as_posix() for name in decision['decisoes']]
        require(row['evidencias_caminhos'] == '; '.join(paths), 'Caminhos de proveniência divergentes.')
        require(row['evidencias_sha256'] == '; '.join(hashlib.sha256((root/name).read_bytes()).hexdigest()
                                                    for name in paths), 'Hashes das decisões divergentes.')
    preview = (output/'comparacao_reproduzivel.html').read_text(encoding='utf-8')
    require(all(term in preview for term in ['Reconferência posterior', 'Requererão', 'Justissa', 'orgente']),
            'Reconferência ausente do HTML.')
    return {'registros_humanos': 17, 'linhas_com_duvidas_visuais_mantidas': [11, 19, 23, 24],
            'catalogo_promovido': False, 'alvos_alterados': False,
            'referencia_independente_da_edicao': False}


def verify_generated(root, output, version=DEFAULT_VERSION):
    delivery, _ = delivery_paths(version)
    config = VERSIONS[version]
    archived = root/delivery
    result = read(output/'resultado_notebook.json')
    original = read(archived/'resultado_notebook.json')
    for key in ['tipo', 'linhas', 'ressalvas', 'regioes', 'metricas',
                'arquivos_experimento_inalterados', 'novas_inferencias', 'treino', 'teste_reservado']:
        require(result[key] == original[key], 'Recálculo divergente: '+key)
    require(result['linhas'] == 24 and result['ressalvas'] == 8 and result['regioes'] == 5,
            'Linhas, ressalvas ou blocos divergentes.')
    require(result['novas_inferencias'] == 0 and not result['treino'] and not result['teste_reservado'],
            'Resultado promovido indevidamente ou nova inferência declarada.')
    historical = read(root/DELIVERY/'resultado_notebook.json')
    require(result['tipo'] == 'diagnostico_de_desenvolvimento' and result['metricas'] == historical['metricas'],
            'Diagnóstico ou métricas da referência congelada de 20/10 divergentes.')
    require(result['workspace_conferido'] is False and result['workspace_arquivos_inalterados'] is None,
            'A reprodução deve ocorrer sem workspace.')
    notebook, saved = read(output/'comparacao_reproduzivel.ipynb'), read(archived/'comparacao_reproduzivel.ipynb')
    require([(c['cell_type'], source(c)) for c in notebook['cells']] ==
            [(c['cell_type'], source(c)) for c in saved['cells']], 'Fontes do notebook foram alteradas.')
    cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
    require(len(cells) == config['cells'] and [c['execution_count'] for c in cells] == list(range(1, config['cells']+1)),
            'Notebook não executado integralmente.')
    require(all(o['output_type'] != 'error' for c in cells for o in c['outputs']), 'Erro em célula do notebook.')
    images = [o['data']['image/png'] for c in cells for o in c['outputs'] if 'image/png' in o.get('data', {})]
    require(len(images) == 2 and all(base64.b64decode(''.join(i) if isinstance(i, list) else i).startswith(b'\x89PNG')
                                  for i in images), 'Figuras incorporadas ausentes.')
    expected_csv = {p.name for p in (archived/'tabelas').glob('*.csv')}
    require(len(expected_csv) == config['tables'] and {p.name for p in (output/'tabelas').glob('*.csv')} == expected_csv,
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
    report = {'versao': version, 'linhas': 24, 'ressalvas': DOUBTS, 'regioes': 5, 'metricas': result['metricas'],
              'celulas_codigo_executadas': config['cells'], 'figuras_incorporadas': 2,
              'tabelas_identicas': config['tables'], 'figuras_png_svg': 4, 'novas_inferencias': 0}
    if version == '20261022':
        report['reconferencia'] = verify_reconference(root, output, archived)
    return report


def run(root, version=DEFAULT_VERSION):
    root = Path(root).resolve()
    delivery, output_path = delivery_paths(version)
    check_environment(root, version)
    before = snapshot(root)
    output = root/output_path
    output.mkdir(parents=True)
    report = {'resultado': 'em_execucao', 'tipo': 'diagnostico_de_desenvolvimento', 'versao': version, 'novas_inferencias': 0}
    env = dict(os.environ, PYTHONPATH=str(root/'src'), PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', MPLBACKEND='Agg')
    auditor = root/delivery/'verificar_entrega.py'
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
            subprocess.run([sys.executable, str(root/delivery/'executar_notebook.py')],
                           cwd=root, env=guarded, timeout=600, check=True)
        events = [json.loads(line) for line in (output/'protecao.jsonl').read_text(encoding='utf-8').splitlines()]
        require(not any(e['evento'] == 'bloqueado' for e in events), 'A execução tentou uma operação proibida.')
        require(any(e.get('kernel') for e in events) and any(e.get('kernel') is False for e in events),
                'Proteções não confirmadas no executor e no kernel.')
        report.update(verify_generated(root, output, version))
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
    parser.add_argument('--version', choices=VERSIONS, default=DEFAULT_VERSION, help='Versão congelada da entrega acadêmica.')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.root, args.version), ensure_ascii=True))
    except Exception as exc:
        print('CI acadêmica: '+str(exc), file=sys.stderr)
        raise SystemExit(2)
