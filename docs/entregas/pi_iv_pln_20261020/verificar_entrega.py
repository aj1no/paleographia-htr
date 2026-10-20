"""Audita os artefatos acadêmicos sem executar inferências ou alterar o editor."""
import base64
import csv
import json
import runpy
from pathlib import Path

import nbformat
from PIL import Image
from paleographia.io import sha256

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
EXPERIMENT = ROOT / 'docs/experimentos/traslado_269r_reconhecedores_24_20261020'


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verificar():
    manifest = read(BASE / 'manifesto_entrega.json')
    files = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*')
             if p.is_file() and p.name != 'manifesto_entrega.json' and '__pycache__' not in p.parts}
    require(files == set(manifest), 'Arquivos ausentes ou inesperados na entrega.')
    for name, expected in manifest.items():
        path = (BASE / name).resolve()
        require(path.is_relative_to(BASE) and sha256(path) == expected, 'Hash divergente: ' + name)
    source = read(BASE / 'proveniencia_entrega.json')
    for name, digest in source['pacotes_de_origem'].items():
        require(sha256(ROOT / name) == digest, 'Pacote de origem divergente.')
    audit = runpy.run_path(str(EXPERIMENT / 'verificar.py'))['verificar']()
    require(audit['resultado'] == 'aprovado', 'Experimento de origem divergente.')
    notebook = nbformat.read(BASE / 'comparacao_reproduzivel.ipynb', as_version=4)
    nbformat.validate(notebook)
    code_cells = [c for c in notebook.cells if c.cell_type == 'code']
    require(len(code_cells) == 9 and [c.execution_count for c in code_cells] == list(range(1,10)), 'Notebook não executado integralmente.')
    require(all(o.output_type != 'error' for c in code_cells for o in c.outputs), 'Erro no notebook.')
    embedded = [o.data['image/png'] for c in code_cells for o in c.outputs if 'image/png' in o.get('data', {})]
    require(len(embedded) == 2 and all(base64.b64decode(p).startswith(b'\x89PNG') for p in embedded), 'Figuras não incorporadas ao notebook.')
    result = read(BASE / 'resultado_notebook.json')
    original = read(EXPERIMENT / 'comparacao.json')
    require(result['metricas'] == {m: v['metrics'] for m,v in original['modelos'].items()}, 'Métricas do notebook divergentes.')
    require(result['linhas'] == 24 and result['ressalvas'] == 8 and result['regioes'] == 5, 'Escopo ampliado ou ressalvas perdidas.')
    require(result['novas_inferencias'] == 0 and not result['treino'] and not result['teste_reservado'], 'Execução promovida indevidamente.')
    with (BASE / 'tabelas/ressalvas.csv').open(encoding='utf-8-sig', newline='') as stream:
        doubts = list(csv.DictReader(stream))
    require([int(r['linha']) for r in doubts] == [11, 15, 16, 17, 19, 20, 23, 24], 'CSV não preserva as oito ressalvas.')
    with (BASE / 'tabelas/24_linhas.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 48, 'Combinações de linha/modelo ausentes.')
    for model in ['ppocrv5', 'ppocrv6']:
        require([int(r['linha']) for r in rows if r['modelo'] == model] == list(range(1,25)), 'Linha excluída do CSV.')
    with (BASE / 'tabelas/resumo_metricas.csv').open(encoding='utf-8-sig', newline='') as stream:
        summary = list(csv.DictReader(stream))
    for row in summary:
        metrics = result['metricas'][row['modelo']]
        require(float(row['CER']) == metrics['characters']['rate'] and float(row['WER']) == metrics['words']['rate'], 'CSV de resumo divergente.')
    for name in ['cer_wer.png', 'cer_blocos.png']:
        with Image.open(BASE / 'figuras' / name) as image:
            require(image.width >= 1000 and image.height >= 600, 'Figura inadequada para exportação.')
    preview = (BASE / 'comparacao_reproduzivel.html').read_text(encoding='utf-8')
    require('Diagnóstico de desenvolvimento' in preview or 'diagnóstico de desenvolvimento' in preview, 'HTML sem identificação do diagnóstico.')
    require('<script src=' not in preview and preview.count('data:image/png;base64,') == 2, 'HTML depende de recurso externo ou perdeu figuras.')
    authors = read(BASE / 'autoria.json')
    require(len(authors['autores']) == 4 and authors['professor_informado']['nome'] == 'Leonardo de Lellis Rossi', 'Autoria divergente.')
    article = (BASE / 'artigo_rascunho.md').read_text(encoding='utf-8')
    require(all(a['nome'] in article and a['email'] in article for a in authors['autores']), 'Autoria ausente no rascunho.')
    require('oito ressalvas' in article and '58,45%' in article and '15,11%' in article and '94,58%' in article and '60,10%' in article, 'Resultados/ressalvas ausentes do artigo.')
    return {'resultado': 'aprovado', 'arquivos_entrega': len(manifest), 'celulas_codigo_executadas': 9,
            'figuras_embutidas': 2, 'linhas': 24, 'ressalvas': 8,
            'combinacoes_linha_modelo': len(rows), 'novas_inferencias': 0,
            'metricas_identicas_ao_experimento': True}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
