"""Auditoria offline do diagnóstico assistido; não carrega pesos nem altera o editor."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image
from paleographia.evaluation import aggregate, counts, normalize
from paleographia.io import read_jsonl, sha256

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def read(name):
    return json.loads((BASE / name).read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def distance(reference, prediction):
    """Levenshtein independente para conferir o número total de operações."""
    previous = list(range(len(prediction) + 1))
    for i, a in enumerate(reference, 1):
        current = [i]
        for j, b in enumerate(prediction, 1):
            current.append(min(previous[j] + 1, current[-1] + 1, previous[j-1] + (a != b)))
        previous = current
    return previous[-1]


def verificar():
    inventory = read('inventario.json')
    files = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*')
             if p.is_file() and p.name != 'inventario.json' and '__pycache__' not in p.parts}
    require(files == set(inventory), 'Inventário incompleto.')
    for name, expected in inventory.items():
        path = (BASE / name).resolve()
        require(path.is_relative_to(BASE) and sha256(path) == expected, 'Arquivo divergente: ' + name)
    for name, expected in read('entradas_congeladas.json')['arquivos'].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT) and sha256(path) == expected, 'Entrada congelada divergente: ' + name)
    targets = read_jsonl(BASE / 'alvos_assistidos.jsonl')
    original = read_jsonl(BASE / 'catalogo_origem.jsonl')
    inference = read_jsonl(BASE / 'recortes_reconhecimento.jsonl')
    crops = read('recortes_congelados.json')
    protocol = read('protocolo.json')
    require(not protocol['referencia_humana_independente'] and not protocol['teste_reservado'], 'Escopo promovido indevidamente.')
    require(len(targets) == len(original) == len(inference) == len(crops) == 24, 'Contagem divergente.')
    require([t['reading_order'] for t in targets] == list(range(24)), 'Ordem divergente.')
    require([t['linha'] for t in targets if t['estado_visual_original'] != 'validated'] == [11, 15, 16, 17, 19, 20, 23, 24], 'Ressalvas perdidas.')
    groups = defaultdict(list)
    for target, source, crop, infer in zip(targets, original, crops, inference):
        require(target['texto_alvo'] == source['text_diplomatic'], 'Alvo alterado após a conferência.')
        require(target['estado_visual_original'] == source['review_status'], 'Validação visual promovida.')
        require(target['duvidas_preservadas'] == source.get('human_review', {}).get('duvidas_preservadas', []), 'Dúvida perdida.')
        require(infer['text_diplomatic'] is None and infer['reference_kind'] == 'unknown', 'Texto humano incluído no manifesto de inferência.')
        require(sha256(ROOT / crop['crop_image']) == crop['sha256'], 'Recorte divergente.')
        with Image.open(ROOT / crop['crop_image']) as opened, Image.open(ROOT / source['source_image']) as src:
            image = opened.convert('RGB')
            require(hashlib.sha256(image.tobytes()).hexdigest() == crop['pixel_sha256'], 'Pixels divergentes.')
            require(src.convert('RGB').crop(tuple(source['bbox_xyxy'])).tobytes() == image.tobytes(), 'Recorte não corresponde à fonte.')
        groups[target['region_id']].append(target)
    require(len(groups) == 5, 'Número de blocos divergente.')
    region_rows = read_jsonl(BASE / 'regioes.jsonl')
    by_line = read_jsonl(BASE / 'por_linha.jsonl')
    summary = read('comparacao.json')
    recomputed = {}
    for model in ['ppocrv5', 'ppocrv6']:
        predictions = read_jsonl(BASE / model / 'predictions.jsonl')
        require([p['line_id'] for p in predictions] == [t['line_id'] for t in targets], 'Predições ausentes, extras ou fora de ordem.')
        require(len(predictions) == len({p['line_id'] for p in predictions}) == 24, 'Predição duplicada.')
        index = {p['line_id']: p for p in predictions}
        for prediction, infer, crop in zip(predictions, inference, crops):
            require(all(prediction[k] == infer[k] for k in ['region_id', 'reading_order', 'bbox_xyxy', 'crop_image', 'source_sha256']), 'Predição de outro recorte.')
            expected_model = 'models/latin_PP-OCRv5_mobile_rec/model.onnx' if model == 'ppocrv5' else 'models/kraken_ppocrv6_medium/medium.safetensors'
            require(prediction['model']['sha256'] == read('entradas_congeladas.json')['pesos'][expected_model], 'Outro modelo foi utilizado.')
            if model == 'ppocrv6' and prediction['status'] == 'ok':
                require(prediction['preprocessing']['pixel_sha256'] == crop['pixel_sha256'], 'Worker recebeu outros pixels.')
        results = []
        for region, refs in groups.items():
            ref = ' '.join(t['texto_alvo'] for t in refs)
            pred = ' '.join(index[t['line_id']]['text_raw'] if index[t['line_id']]['status'] == 'ok' else '' for t in refs)
            metrics = counts(ref, pred)
            require(metrics['characters']['errors'] == distance(normalize(ref), normalize(pred)), 'CER diverge do cálculo independente.')
            require(metrics['words']['errors'] == distance(normalize(ref).split(), normalize(pred).split()), 'WER diverge do cálculo independente.')
            saved = next(r for r in region_rows if r['modelo'] == model and r['region_id'] == region)
            require(saved['metrics'] == metrics and saved['referencia'] == ref and saved['predicao'] == pred, 'Resultado regional divergente.')
            results.append(metrics)
        recomputed[model] = aggregate(results)
        require(recomputed[model] == summary['modelos'][model]['metrics'], 'Microagregação divergente.')
        require(summary['modelos'][model]['falhas'] == sum(p['status'] != 'ok' for p in predictions), 'Falha omitida.')
        for target in targets:
            pred = index[target['line_id']]
            text = pred['text_raw'] if pred['status'] == 'ok' else ''
            saved = next(r for r in by_line if r['modelo'] == model and r['linha'] == target['linha'])
            require(saved['metrics'] == counts(target['texto_alvo'], text), 'Diagnóstico por linha divergente.')
    return {'resultado': 'aprovado', 'arquivos_conferidos': len(inventory), 'linhas': 24,
            'ressalvas_preservadas': 8, 'blocos': 5, 'metricas_recalculadas': recomputed,
            'distancias_conferidas_por_algoritmo_independente': True}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
