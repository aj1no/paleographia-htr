"""Confere a versão aditiva, a referência histórica e as decisões posteriores."""
import base64
import csv
import hashlib
import json
import runpy
from pathlib import Path

import nbformat

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OLD = ROOT / 'docs/entregas/pi_iv_pln_20261020'
REVIEW = ROOT / 'docs/revisao_humana/traslado_269r/reconferencia_ressalvas_20261021'
DOUBTS = [11, 15, 16, 17, 19, 20, 23, 24]


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def verificar():
    manifest = read(BASE / 'manifesto_entrega.json')
    files = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*')
             if p.is_file() and p.name != 'manifesto_entrega.json' and '__pycache__' not in p.parts}
    require(files == set(manifest), 'Arquivos ausentes ou inesperados na nova entrega.')
    for name, expected in manifest.items():
        path = (BASE / name).resolve()
        require(path.is_relative_to(BASE) and sha(path) == expected, 'Hash divergente: ' + name)
    provenance = read(BASE / 'proveniencia_entrega.json')
    for key in ['pacote_20261020', 'pacotes_de_origem']:
        for name, expected in provenance[key].items():
            require(sha(ROOT / name) == expected, 'Origem histórica alterada: ' + name)
    require(provenance['novas_inferencias'] == 0 and not provenance['alvos_alterados']
            and not provenance['catalogo_promovido']
            and not provenance['leitura_humana_independente_da_edicao'], 'Proveniência promovida indevidamente.')
    old_audit = runpy.run_path(str(OLD / 'verificar_entrega.py'))['verificar']()
    require(old_audit['resultado'] == 'aprovado', 'Entrega de 20/10 reprovada.')
    inventory = read(REVIEW / 'inventario.json')
    require({p.name for p in REVIEW.iterdir() if p.is_file()} == set(inventory) | {'inventario.json'},
            'Arquivos da reconferência ausentes ou inesperados.')
    for name, expected in inventory.items():
        require(sha(REVIEW / name) == expected, 'Reconferência alterada: ' + name)
    review = read(REVIEW / 'consolidacao.json')
    require(not review['duvidas_foram_zeradas'] and not review['referencia_humana_independente_da_edicao']
            and review['novo_total_de_linhas_validadas_no_catalogo'] is None, 'Dúvidas promovidas indevidamente.')
    notebook = nbformat.read(BASE / 'comparacao_reproduzivel.ipynb', as_version=4)
    nbformat.validate(notebook)
    cells = [c for c in notebook.cells if c.cell_type == 'code']
    require(len(cells) == 10 and [c.execution_count for c in cells] == list(range(1, 11)),
            'Notebook não executado integralmente.')
    require(all(o.output_type != 'error' for c in cells for o in c.outputs), 'Erro no notebook.')
    embedded = [o.data['image/png'] for c in cells for o in c.outputs if 'image/png' in o.get('data', {})]
    require(len(embedded) == 2 and all(base64.b64decode(p).startswith(b'\x89PNG') for p in embedded),
            'Figuras incorporadas ausentes.')
    result = read(BASE / 'resultado_notebook.json')
    old_result = read(OLD / 'resultado_notebook.json')
    for key in ['tipo', 'linhas', 'ressalvas', 'regioes', 'metricas', 'novas_inferencias', 'treino', 'teste_reservado']:
        require(result[key] == old_result[key], 'Resultado histórico divergente: ' + key)
    require(result['linhas'] == 24 and result['ressalvas'] == 8 and result['novas_inferencias'] == 0,
            'Escopo ou execução indevidos.')
    r = result['reconferencia']
    require(r['linhas'] == DOUBTS and r['registros_humanos'] == 17
            and r['pacote_20261020_preservado'] and not r['catalogo_promovido']
            and not r['alvos_alterados'] and not r['leitura_independente_da_edicao']
            and r['inventario_sha256'] == sha(REVIEW / 'inventario.json'), 'Recibo da reconferência divergente.')
    old_tables = list((OLD / 'tabelas').glob('*.csv'))
    require(len(old_tables) == 5, 'Conjunto histórico de tabelas divergente.')
    for table in old_tables:
        require(sha(table) == sha(BASE / 'tabelas' / table.name), 'Tabela histórica divergente: ' + table.name)
    new_rows = rows(BASE / 'tabelas/reconferencia_ressalvas.csv')
    require([int(row['linha']) for row in new_rows] == DOUBTS, 'Oito ressalvas históricas ausentes.')
    original_rows = {int(row['linha']): row for row in rows(OLD / 'tabelas/ressalvas.csv')}
    for row, decision in zip(new_rows, review['resultados_por_linha']):
        require(row['alvo_congelado_20261020'] == decision['texto_adotado_na_referencia_congelada']
                == original_rows[decision['linha']]['alvo_adotado'], 'Alvo alterado na tabela de reconferência.')
        require(row['ressalva_original_20261020'] == original_rows[decision['linha']]['ressalva_preservada'],
                'Ressalva original apagada.')
        for field, source in [('decisao_reconferencia_20261021', 'trecho_adotado'),
                              ('confirmacoes_visuais_pontuais', 'confirmacoes_visuais_novas'),
                              ('apoio_editorial', 'apoio_editorial'),
                              ('duvidas_visuais_mantidas', 'duvidas_visuais_preservadas')]:
            expected = decision[source]
            require(row[field] == ('; '.join(expected) if isinstance(expected, list) else expected),
                    'Decisão ou dúvida divergente: ' + field)
        require(row['revisor'] == review['revisor'], 'Autoria da revisão divergente.')
        paths = row['evidencias_caminhos'].split('; ')
        hashes = row['evidencias_sha256'].split('; ')
        require(paths == [(REVIEW / name).relative_to(ROOT).as_posix() for name in decision['decisoes']],
                'Vínculos de proveniência divergentes.')
        require(hashes == [sha(ROOT / name) for name in paths], 'Hashes das decisões divergentes.')
    require(review['linhas_com_duvidas_visuais_expressamente_mantidas'] == [11, 19, 23, 24]
            and review['novas_confirmacoes_pontuais_de_ressalvas'] == [15, 16, 20], 'Escopo das confirmações divergente.')
    preview = (BASE / 'comparacao_reproduzivel.html').read_text(encoding='utf-8')
    require('<script src=' not in preview and preview.count('data:image/png;base64,') == 2,
            'HTML incompleto ou dependente de script externo.')
    require(all(term in preview for term in ['Reconferência posterior', 'Requererão', 'Justissa', 'orgente']),
            'Reconferência ausente do HTML.')
    article = (BASE / 'artigo_rascunho.md').read_text(encoding='utf-8')
    require(all(term in article for term in ['diagnóstico de desenvolvimento', 'oito ressalvas',
            '58,45%', '94,58%', '15,11%', '60,10%', 'Reconferência posterior', 'Dois s continuam duvidosos',
            'Pontuação final em aberto', 'Inicial o/e permanece visualmente duvidosa']), 'Ressalvas ou métricas ausentes do artigo.')
    authors = read(BASE / 'autoria.json')
    require(all(a['nome'] in article and a['email'] in article for a in authors['autores']), 'Autoria ausente.')
    events = [json.loads(line) for line in (BASE / 'protecao_execucao.jsonl').read_text(encoding='utf-8').splitlines()]
    require(not any(e['evento'] == 'bloqueado' for e in events)
            and any(e.get('kernel') for e in events) and any(e.get('kernel') is False for e in events),
            'Proteções não confirmadas no executor e kernel.')
    return {'resultado': 'aprovado', 'arquivos_entrega': len(manifest), 'linhas': 24,
            'ressalvas_historicas': DOUBTS, 'registros_humanos': 17,
            'celulas_codigo_executadas': 10, 'figuras_incorporadas': 2,
            'tabelas_historicas_identicas': 5, 'tabela_nova_reconferencia': 8,
            'pacote_20261020_preservado': True, 'metricas_identicas_ao_experimento': True,
            'novas_inferencias': 0, 'protecao_executor_e_kernel': True}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
