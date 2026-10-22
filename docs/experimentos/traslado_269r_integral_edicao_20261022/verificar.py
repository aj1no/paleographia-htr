"""Auditoria offline do diagnóstico integral; não carrega modelos."""
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from paleographia.config import load_config
from paleographia.evaluation import counts, normalize
from paleographia.segmentation import opencv_boxes

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
AREAS = [('cabecalho', 0, 130), ('titulo', 130, 240), ('resumo', 240, 550), ('corpo', 550, 1873)]


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def distance(a, b):
    previous = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(previous[j]+1, current[-1]+1, previous[j-1]+(x != y)))
        previous = current
    return previous[-1]


def verificar():
    inventory = read(BASE/'inventario.json')
    actual = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()
              and p.name != 'inventario.json' and '__pycache__' not in p.parts}
    require(actual == set(inventory), 'Arquivos ausentes ou inesperados no pacote.')
    for name, expected in inventory.items():
        path = (BASE/name).resolve()
        require(path.is_relative_to(BASE) and sha(path) == expected, 'Hash divergente: '+name)
    frozen = read(BASE/'entradas_congeladas.json')
    for name, expected in frozen['arquivos'].items():
        require(sha(ROOT/name) == expected, 'Entrada congelada divergente: '+name)
    protocol = read(BASE/'protocolo.json')
    require(protocol['tipo'] == 'diagnostico_de_desenvolvimento_contra_edicao_publicada'
            and not protocol['treinamento'] and not protocol['teste_reservado']
            and not protocol['referencia_humana_independente']
            and not protocol['promocao_de_estados_humanos']
            and not protocol['recortes_humanos_usados_na_medicao_principal'], 'Experimento promovido indevidamente.')
    require(protocol['ressalvas_historicas_preservadas'] == [11, 15, 16, 17, 19, 20, 23, 24],
            'Ressalvas históricas perdidas.')
    extraction = read(BASE/'edicao_extraida.json')
    require(sha(ROOT/extraction['fonte']) == extraction['sha256'], 'Edição divergente.')
    pdf = PdfReader(ROOT/extraction['fonte'])
    for page in extraction['paginas']:
        require(pdf.pages[page['pagina_pdf']-1].extract_text() == page['texto_extraido'], 'Extração da edição divergente.')
    target = rows(BASE/'alvos_editoriais.jsonl')
    require(len(target) == 36, 'Cobertura editorial incompleta.')
    expected_sizes = {'cabecalho': 3, 'titulo': 2, 'resumo': 7, 'corpo': 24}
    require({area: sum(t['area'] == area for t in target) for area, _, _ in AREAS} == expected_sizes,
            'Partes editoriais ausentes ou duplicadas.')
    for item in target:
        page = extraction['paginas'][item['pagina_pdf']-1]
        raw = page['linhas_sem_vazias'][item['indice_linha_extraida_sem_vazias']]
        require(raw == item['texto_extraido_original'] and raw.strip() == item['texto_alvo']
                and item['validacao_humana_nova'] is False, 'Texto editorial alterado ou promovido.')
    require([t['texto_alvo'] for t in target[:3]] == ['Villa de Jundiahy', 'Anno de 1767', '269'],
            'Ordem do cabeçalho divergente.')
    require((BASE/'texto_oficial.txt').read_text(encoding='utf-8') == '\n'.join(t['texto_alvo'] for t in target)+'\n',
            'Texto oficial divergente.')
    lines = rows(BASE/'segmentacao/lines.jsonl')
    predictions = rows(BASE/'ppocrv6/predictions.jsonl')
    require([p['line_id'] for p in predictions] == [line['line_id'] for line in lines]
            and len({p['line_id'] for p in predictions}) == len(lines), 'Predições ausentes ou duplicadas.')
    require([line['reading_order'] for line in lines] == list(range(len(lines))), 'Ordem automática divergente.')
    page = rows(BASE/'pagina_reconhecimento.jsonl')[0]
    require(not page['transcribed_coverage'], 'Regiões humanas inseridas na segmentação.')
    with Image.open(ROOT/page['source_image']) as opened:
        image = opened.convert('RGB')
        generated = opencv_boxes(image, load_config(BASE/'config.toml')['segmentation'])
        require(generated == [line['bbox_xyxy'] for line in lines], 'Caixas automáticas alteradas.')
        crop_hashes = read(BASE/'ppocrv6/entradas_recortes.json')
        for line, pred in zip(lines, predictions):
            require(line['text_diplomatic'] is None and line['reference_kind'] == 'unknown'
                    and line['review_status'] == 'pending_review', 'Texto da referência apresentado como entrada.')
            require(all(pred[k] == line[k] for k in ['bbox_xyxy', 'reading_order', 'region_id', 'source_sha256', 'crop_image']),
                    'Entrada e predição não correspondem.')
            with Image.open(ROOT/line['crop_image']) as crop:
                pixels = crop.convert('RGB').tobytes()
            require(image.crop(line['bbox_xyxy']).tobytes() == pixels, 'Pixels do recorte alterados.')
            require(crop_hashes[line['line_id']]['sha256'] == sha(ROOT/line['crop_image'])
                    and crop_hashes[line['line_id']]['pixel_sha256'] == hashlib.sha256(pixels).hexdigest(),
                    'Recorte diverge do congelamento anterior à inferência.')
            require(pred['status'] in {'ok', 'failed'} and isinstance(pred['text_raw'], str), 'Estado bruto inválido.')
            if pred['status'] == 'ok':
                require(pred['preprocessing']['pixel_sha256'] == hashlib.sha256(pixels).hexdigest(), 'Pixels recebidos divergentes.')
                require(pred['model']['sha256'] == next(iter(frozen['pesos'].values()))
                        and pred['model']['docker_image_id'] == frozen['imagem_docker'], 'Modelo divergente.')
    ref = ' '.join(t['texto_alvo'] for t in target)
    hyp = ' '.join(p['text_raw'] if p['status'] == 'ok' else '' for p in predictions)
    saved = read(BASE/'comparacao.json')
    measured = counts(ref, hyp)
    require(saved['metrics'] == measured and saved['recortes_automaticos'] == len(predictions), 'Métricas divergentes.')
    require(measured['characters']['errors'] == distance(normalize(ref), normalize(hyp))
            and measured['words']['errors'] == distance(normalize(ref).split(), normalize(hyp).split()),
            'Distância de edição independente divergente.')
    require(saved['falhas'] == sum(p['status'] != 'ok' for p in predictions)
            and not saved['treinamento'] and not saved['teste_reservado']
            and not saved['referencia_humana_independente']
            and not saved['promocao_de_estados_humanos'], 'Resultado promovido indevidamente.')
    require((BASE/'transcricao_bruta.txt').read_text(encoding='utf-8') == '\n'.join(
        p['text_raw'] if p['status'] == 'ok' else '' for p in predictions)+'\n', 'Bruto textual alterado.')
    groups = rows(BASE/'por_area.jsonl')
    require([g['area'] for g in groups] == [area for area, _, _ in AREAS], 'Área ausente.')
    for group, (area, y0, y1) in zip(groups, AREAS):
        selected = [p for p in predictions if y0 <= (p['bbox_xyxy'][1]+p['bbox_xyxy'][3])/2 < y1]
        group_ref = ' '.join(t['texto_alvo'] for t in target if t['area'] == area)
        group_hyp = ' '.join(p['text_raw'] if p['status'] == 'ok' else '' for p in selected)
        require(group['referencia'] == group_ref and group['predicao_bruta'] == group_hyp
                and group['metrics'] == counts(group_ref, group_hyp) and group['recortes'] == len(selected),
                'Diagnóstico por área divergente.')
    with (BASE/'por_area.csv').open(encoding='utf-8-sig', newline='') as stream:
        table = list(csv.DictReader(stream))
    require([r['area'] for r in table] == ['pagina_inteira', *[a for a, _, _ in AREAS]], 'Tabela incompleta.')
    for row, metrics in zip(table, [measured, *[g['metrics'] for g in groups]]):
        require(float(row['CER']) == metrics['characters']['rate'] and float(row['WER']) == metrics['words']['rate'],
                'CSV numérico divergente.')
    infer = read(BASE/'ppocrv6/proveniencia.json')
    require(datetime.fromisoformat(frozen['criado_em']) <= datetime.fromisoformat(infer['inicio']), 'Referência congelada após a inferência.')
    require(infer['inferencias'] == len(predictions), 'Número de inferências divergente.')
    before, after = read(BASE/'preservacao_antes.json'), read(BASE/'preservacao_depois.json')
    prefixes = ['docs/entregas/pi_iv_pln_20261020/', 'docs/entregas/pi_iv_pln_20261022/',
                'docs/revisao_humana/traslado_269r/referencia_assistida_20261020/',
                'docs/revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/',
                'docs/experimentos/traslado_269r_reconhecedores_24_20261020/']
    preserved = {name: h for name, h in before['versionados'].items() if any(name.startswith(p) for p in prefixes)}
    require(all(sha(ROOT/name) == h for name, h in preserved.items()), 'Pacote histórico alterado.')
    require(after['arquivos_versionados_inalterados'] == len(before['versionados'])
            and after['arquivos_workspace_inalterados'] == len(before['workspaces'])
            and not after['editor_alterado'] and after['estados_humanos_promovidos'] == 0, 'Recibo de preservação inválido.')
    return {'resultado': 'aprovado', 'arquivos_conferidos': len(inventory), 'recortes_automaticos': len(lines),
            'unidades_editoriais': 36, 'pacotes_historicos_arquivos_conferidos': len(preserved),
            'editor_alterado': False, 'treinamento': False, 'referencia_independente': False,
            'metrics': measured, 'distancias_conferidas_independentemente': True}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
