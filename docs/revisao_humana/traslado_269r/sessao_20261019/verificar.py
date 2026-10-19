"""Confere somente por leitura o pacote da sessão humana de 19/10/2026."""
import hashlib
import json
from pathlib import Path
import zipfile

from PIL import Image

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[3]


def exigir(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ler(name):
    return json.loads((BASE / name).read_bytes())


def verificar():
    inventory = ler('inventario.json')
    files = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*')
             if p.is_file() and '__pycache__' not in p.parts
             and p.relative_to(BASE).as_posix() != 'inventario.json'}
    exigir(files == set(inventory), 'Arquivos ausentes ou inesperados no pacote.')
    for name, expected in inventory.items():
        path = (BASE / name).resolve()
        exigir(path.is_relative_to(BASE), 'Caminho fora do pacote.')
        exigir(sha(path.read_bytes()) == expected, 'Hash divergente: ' + name)
    notes = ler('conferencia.json')
    provenance = ler('proveniencia.json')
    exigir(not notes['gravado_no_editor'] and not notes['apta_para_treino']
           and not notes['apta_para_avaliacao'], 'Notas promovidas indevidamente a referência.')
    exigir([r['linha'] for r in notes['linhas']] == list(range(11, 22)), 'Sequência de notas divergente.')
    exigir(all(r['geometria_nesta_conferencia'] == 'nao_validada'
               and r['cobertura_nesta_conferencia'] == 'nao_confirmada'
               for r in notes['linhas']), 'Geometria/cobertura ampliadas indevidamente.')
    last = notes['linhas'][-1]
    exigir(last['texto_proposto_na_conversa'] is None
           and any(s['texto'] == 'Pesueem' and s['estado'] == 'hipotese_do_usuario'
                   for s in last['segmentos']), 'Pendência da linha 21 perdida.')
    pointer = ler('editor/ponteiro.json')
    saved = ler('editor/revisao_salva.json')
    exigir(pointer['revision'] == saved['revision'] == notes['revisao_editor_preservada'],
           'Revisão salva divergente.')
    exigir(len(saved['lines']) == 15 and len(saved['predictions']) == 15,
           'Catálogo original divergente.')
    exigir(all(l['review_status'] == 'validated' for l in saved['lines']),
           'Estados originais não preservados.')
    exigir({r['region_id'] for r in saved['pages'][0]['transcribed_coverage'] if r['complete']}
           == {'body_first5', 'body_06_10'}, 'Cobertura original divergente.')
    zip_inventory = ler('editor/arquivos_workspace.json')
    with zipfile.ZipFile(BASE / 'editor/workspace.zip') as archive:
        exigir(set(archive.namelist()) == set(zip_inventory), 'Conteúdo do ZIP divergente.')
        for name, expected in zip_inventory.items():
            path = Path(name)
            exigir(not path.is_absolute() and '..' not in path.parts
                   and name.startswith('data/workspace_traslado_269r/'), 'Caminho inseguro no ZIP.')
            exigir(sha(archive.read(name)) == expected, 'Bytes divergentes no ZIP: ' + name)
        prefix = 'data/workspace_traslado_269r/'
        exigir(archive.read(prefix + 'current.json') == (BASE / 'editor/ponteiro.json').read_bytes(),
               'Ponteiro publicado diverge do ZIP.')
        exigir(archive.read(prefix + 'revisions/' + saved['revision'] + '.json')
               == (BASE / 'editor/revisao_salva.json').read_bytes(), 'Snapshot diverge do ZIP.')
        revisions = [name for name in archive.namelist() if name.startswith(prefix + 'revisions/')
                     and name.endswith('.json')]
        for name in revisions:
            state = json.loads(archive.read(name))
            parent = state.get('parent_revision')
            exigir(not parent or prefix + 'revisions/' + parent + '.json' in zip_inventory,
                   'Pai ausente no histórico: ' + name)
    source = REPO / provenance['manuscrito']
    exigir(sha(source.read_bytes()) == provenance['source_sha256'], 'Fonte manuscrita divergente.')
    with Image.open(source) as raw:
        original = raw.convert('RGB')
    runs = notes['reconhecimentos_novos']
    exigir([r['linha'] for r in runs] == list(range(16, 22)), 'Execuções divergentes.')
    for run in runs:
        folder = BASE / run['pasta']
        entries = (folder / 'predictions.jsonl').read_text(encoding='utf-8').splitlines()
        exigir(len(entries) == 1, 'Quantidade de predições divergente.')
        prediction = json.loads(entries[0])
        exigir(prediction['text_raw'] == run['texto_bruto']
               and prediction['execution_id'] == run['execution_id']
               and prediction['status'] == 'ok', 'Saída bruta alterada.')
        exigir(prediction['source_sha256'] == provenance['source_sha256']
               and prediction['model']['sha256'] == '15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9',
               'Identidade da execução divergente.')
        with Image.open(folder / 'recorte.png') as raw:
            crop = raw.convert('RGB')
        expected = original.crop(tuple(run['bbox_xyxy']))
        exigir(crop.size == expected.size and crop.tobytes() == expected.tobytes(),
               'Recorte não corresponde aos pixels da fonte.')
        exigir(prediction['preprocessing']['pixel_sha256'] == sha(crop.tobytes()),
               'Reconhecedor recebeu pixels diferentes.')
        with Image.open(folder / 'ampliado_3x.png') as raw:
            enlarged = raw.convert('RGB')
        expected_enlarged = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.NEAREST)
        exigir(enlarged.size == expected_enlarged.size and enlarged.tobytes() == expected_enlarged.tobytes(),
               'Ampliação divergente.')
        receipt = json.loads((folder / 'preservacao.json').read_bytes())
        exigir(receipt['before'] == receipt['after'], 'Execução alterou os arquivos monitorados do editor.')
    preservation = ler('preservacao.json')
    exigir(preservation['quantidade'] == len(preservation['arquivos'])
           and preservation['todos_inalterados'], 'Recibo de preservação inválido.')
    return {'resultado': 'aprovado', 'arquivos_do_pacote': len(inventory),
            'arquivos_no_zip': len(zip_inventory), 'revisoes_no_zip': len(revisions),
            'reconhecimentos_conferidos': len(runs),
            'linhas_com_notas': len(notes['linhas']),
            'linha_de_retomada': 21, 'pendencia_preservada': 'Pesueem / pessuhem'}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True, indent=2))
