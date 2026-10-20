"""Verificação por leitura do retrato documental; não altera o editor."""
import hashlib
import json
from pathlib import Path

from PIL import Image
from paleographia.data import validate

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]


def read(name):
    return json.loads((BASE / name).read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verificar():
    manifest = read('inventario.json')
    actual = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.name != 'inventario.json'}
    require(actual == set(manifest), 'Inventário incompleto ou arquivos inesperados.')
    for name, expected in manifest.items():
        path = (BASE / name).resolve()
        require(path.is_relative_to(BASE) and sha(path) == expected, 'Hash divergente: ' + name)
    old = read('editor_anterior.json')
    first = read('editor_consolidado_inicial.json')
    state = read('editor_consolidado.json')
    require(first['parent_revision'] == old['revision'] and state['parent_revision'] == first['revision'], 'Histórico interrompido.')
    require(read('ponteiro_consolidado.json')['revision'] == state['revision'], 'Ponteiro congelado divergente.')
    require(len(state['lines']) == len(state['predictions']) == 24, 'Contagem de linhas/predições divergente.')
    require(state['lines'][:10] == old['lines'][:10], 'Linhas 1–10 alteradas.')
    require(state['predictions'][:15] == old['predictions'], 'Predições anteriores alteradas.')
    require([l['reading_order'] for l in state['lines']] == list(range(24)), 'Ordem divergente.')
    require(len({l['line_id'] for l in state['lines']}) == 24, 'IDs duplicados.')
    require(all(l['geometry_status'] == 'validated' for l in state['lines']), 'Geometria pendente.')
    pending = [i for i, l in enumerate(state['lines'], 1) if l['review_status'] != 'validated']
    require(pending == [11, 15, 16, 17, 19, 20, 23, 24], 'Dúvidas visuais perdidas ou alteradas.')
    require(state['lines'][13]['text_diplomatic'].endswith('onde Eram'), 'Eram confirmado perdido.')
    require(old['lines'][13]['text_diplomatic'].endswith('onde Heram'), 'Snapshot anterior alterado.')
    require(state['lines'][21]['text_diplomatic'].endswith('outros que mais'), 'Espaçamento adotado divergente.')
    require(state['lines'][23]['text_diplomatic'].endswith('Magᵈᵉ'), 'Abreviatura literal substituída.')
    require(state['lines'][23]['published_reference']['text'].endswith('Magestade'), 'Desenvolvimento editorial perdido.')
    for before, after in zip(old['lines'][10:15], state['lines'][10:15]):
        observations = before.get('published_reference', {}).get('human_observations', [])
        require(after['published_reference']['human_observations'][:len(observations)] == observations,
                'Observações humanas anteriores perdidas.')
    page = state['pages'][0]
    require(sha(ROOT / page['source_image']) == page['source_sha256'], 'Fonte do manuscrito divergente.')
    policy = read('politica_textual.json')
    require(sha(ROOT / policy['fonte_editorial_publicada']) == policy['sha256_fonte_editorial'], 'Fonte editorial divergente.')
    regions = page['transcribed_coverage']
    require(len(regions) == 5 and all(r['complete'] and r['review_status'] == 'validated' for r in regions), 'Cobertura incompleta.')
    with Image.open(ROOT / page['source_image']) as opened:
        image = opened.convert('RGB')
    for n, line in enumerate(state['lines'], 1):
        with Image.open(BASE / 'recortes' / f'linha_{n:02d}.png') as opened:
            cut = opened.convert('RGB')
        expected = image.crop(tuple(line['bbox_xyxy']))
        require(cut.size == expected.size and cut.tobytes() == expected.tobytes(), 'Recorte divergente: ' + str(n))
    mappings = read('mapeamento_predicoes.json')
    for mapping, projected in zip(mappings, state['predictions'][15:]):
        path = ROOT / mapping['arquivo_original']
        require(sha(path) == mapping['sha256_original'], 'Predição original divergente.')
        raw = json.loads(path.read_text(encoding='utf-8').strip())
        restored = {k: v for k, v in projected.items() if k != 'import_provenance'}
        restored.update(region_id=mapping['region_id_original'], crop_image=mapping['crop_image_original'])
        require(restored == raw, 'Campo bruto alterado na projeção do editor.')
    lines = [json.loads(s) for s in (BASE / 'linhas_congeladas.jsonl').read_text(encoding='utf-8').splitlines()]
    for frozen, editor in zip(lines, state['lines']):
        restored = dict(frozen)
        restored['crop_image'] = restored.pop('crop_image_no_editor')
        restored['reference_source'] = restored.pop('reference_source_no_editor')
        require(restored == editor, 'Catálogo congelado difere do editor.')
    require((BASE / 'texto_adotado.txt').read_text(encoding='utf-8').splitlines() ==
            [l['text_diplomatic'] for l in lines], 'Texto adotado divergente.')
    pages = [json.loads(s) for s in (BASE / 'paginas_congeladas.jsonl').read_text(encoding='utf-8').splitlines()]
    require(len(lines) == 24 and len(pages) == len(state['pages']), 'Exportação congelada incompleta.')
    for frozen_page, editor_page in zip(pages, state['pages']):
        restored_page = json.loads(json.dumps(frozen_page))
        for coverage in restored_page['transcribed_coverage']:
            coverage['reference_source'] = coverage.pop('reference_source_no_editor')
        require(restored_page == editor_page, 'Página congelada difere do editor.')
    catalog = validate(lines, ROOT, 'catalog', pages)
    evaluation = validate(lines, ROOT, 'evaluation', pages)
    require(catalog['valid'] and not evaluation['valid'], 'Elegibilidade indevida.')
    return {'arquivos_conferidos': len(manifest), 'linhas': 24, 'recortes_identicos': 24,
            'linhas_validadas': 16, 'pendencias_visuais': pending,
            'historico_e_bruto_preservados': True, 'catalogo_valido': True,
            'avaliacao_integral_apta': False}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
