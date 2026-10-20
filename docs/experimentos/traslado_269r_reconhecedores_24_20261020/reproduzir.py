"""Experimento documental: alvos assistidos, componentes existentes, sem alterar o editor.

Execute da raiz do repositório. O avaliador humano estrito permanece inalterado;
o experimento usa suas funções counts/aggregate com alvos explicitamente assistidos.
"""
import argparse
import copy
import csv
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path

import jiwer
from PIL import Image

from paleographia.config import load_config
from paleographia.data import Line, validate
from paleographia.evaluation import aggregate, counts, normalize
from paleographia.experiments import provenance
from paleographia.io import now, read_jsonl, sha256, write_json, write_jsonl

ROOT = Path.cwd()
SOURCE = ROOT / 'docs/revisao_humana/traslado_269r/referencia_assistida_20261020'
DEFAULT_OUTPUT = 'docs/experimentos/traslado_269r_reconhecedores_24_20261020'
REQUEST = 'Vamos preparar esse conjunto de avaliação assistida, usando a edição nas dúvidas e preservando as ressalvas. Depois pode rodar a comparação nos 24 recortes e me mostrar o CER/WER e os principais erros dos dois.'


def read(path):
    return json.loads(path.read_bytes())


def relative(path):
    return path.relative_to(ROOT).as_posix()


def check_inputs(out, weights=False):
    frozen = read(out / 'entradas_congeladas.json')
    for name, expected in frozen['arquivos'].items():
        assert sha256(ROOT / name) == expected, 'Entrada alterada: ' + name
    if weights:
        for name, expected in frozen['pesos'].items():
            assert sha256(ROOT / name) == expected, 'Pesos alterados: ' + name
    return frozen


def inventory(out):
    write_json(out / 'inventario.json', {p.relative_to(out).as_posix(): sha256(p)
               for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'inventario.json'
               and '__pycache__' not in p.parts})


def prepare(out):
    assert not out.exists(), 'Use diretório novo; não sobrescrever experimento.'
    source_manifest = read(SOURCE / 'inventario.json')
    assert all(sha256(SOURCE / p) == h for p, h in source_manifest.items())
    original_lines = read_jsonl(SOURCE / 'linhas_congeladas.jsonl')
    pages = read_jsonl(SOURCE / 'paginas_congeladas.jsonl')
    assert len(original_lines) == 24
    assert [r['reading_order'] for r in original_lines] == list(range(24))
    assert validate(original_lines, ROOT, 'catalog', pages)['valid']
    assert not validate(original_lines, ROOT, 'evaluation', pages)['valid']
    previous_provenance = provenance({}, [SOURCE / 'linhas_congeladas.jsonl'])
    config = load_config('configs/traslado_269r.toml')
    weights = {'models/latin_PP-OCRv5_mobile_rec/model.onnx': 'b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a',
               config['recognition']['model']: config['recognition']['sha256']}
    assert all(sha256(ROOT / p) == h for p, h in weights.items())
    image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', config['recognition']['docker_image']], text=True).strip()
    assert image_id == config['recognition']['docker_image_id']
    out.mkdir(parents=True)
    shutil.copyfile(Path(__file__), out / 'reproduzir.py')
    shutil.copyfile(SOURCE / 'linhas_congeladas.jsonl', out / 'catalogo_origem.jsonl')
    shutil.copyfile(SOURCE / 'paginas_congeladas.jsonl', out / 'paginas.jsonl')
    shutil.copyfile(SOURCE / 'politica_textual.json', out / 'politica_textual_origem.json')
    shutil.copyfile(ROOT / 'configs/traslado_269r.toml', out / 'config_ppocrv6.toml')
    adopted = (SOURCE / 'texto_adotado.txt').read_text(encoding='utf-8').splitlines()
    assert adopted == [r['text_diplomatic'] for r in original_lines]
    targets, inference, crops = [], [], []
    fields = {'line_id', 'page_id', 'document_id', 'folio_id', 'region_id', 'reading_order',
              'source_image', 'crop_image', 'bbox_xyxy', 'source_width', 'source_height',
              'source_sha256', 'transform_id', 'split_group', 'geometry_status', 'reviewer', 'reviewed_at'}
    for n, row in enumerate(original_lines, 1):
        assert row['geometry_status'] == 'validated'
        with Image.open(ROOT / row['source_image']) as source, Image.open(ROOT / row['crop_image']) as crop:
            image = crop.convert('RGB')
            assert source.convert('RGB').crop(tuple(row['bbox_xyxy'])).tobytes() == image.tobytes()
            pixel_sha = hashlib.sha256(image.tobytes()).hexdigest()
        crops.append({'linha': n, 'line_id': row['line_id'], 'crop_image': row['crop_image'],
                      'sha256': sha256(ROOT / row['crop_image']), 'pixel_sha256': pixel_sha})
        targets.append({'linha': n, 'line_id': row['line_id'], 'page_id': row['page_id'],
                        'region_id': row['region_id'], 'reading_order': row['reading_order'],
                        'texto_alvo': row['text_diplomatic'], 'tipo_referencia': 'assistida_por_edicao_publicada',
                        'estado_visual_original': row['review_status'],
                        'duvidas_preservadas': row.get('human_review', {}).get('duvidas_preservadas', []),
                        'revisor': row['reviewer'], 'origem_da_decisao': row.get('human_review'),
                        'edicao_publicada': row['published_reference']['text'],
                        'reference_source': row['reference_source'], 'reference_pages': row['reference_pages']})
        infer = Line(**{k: copy.deepcopy(v) for k, v in row.items() if k in fields}, split='exploratory').model_dump()
        assert infer['text_diplomatic'] is None and infer['reference_kind'] == 'unknown'
        inference.append(infer)
    assert len([t for t in targets if t['estado_visual_original'] != 'validated']) == 8
    assert validate(inference, ROOT, 'catalog', pages)['valid']
    write_jsonl(out / 'alvos_assistidos.jsonl', targets)
    write_jsonl(out / 'recortes_reconhecimento.jsonl', inference)
    protocol = {
        'tipo': 'comparacao_assistida_de_desenvolvimento', 'data_congelamento': now(),
        'autorizacao_do_usuario': REQUEST, 'revisor': 'Rodolfo Vinícius Cima Takemoto',
        'folio': '269r', 'linhas': 24, 'regioes_completas': 5,
        'papel_do_documento': 'desenvolvimento_exploratorio', 'teste_reservado': False,
        'referencia_humana_independente': False, 'treino': False,
        'politica': 'Usar leituras adotadas na conferência; edição nas dúvidas; preservar ressalvas e diferenças confirmadas.',
        'abreviatura_final': 'Magᵈᵉ literal no alvo; Magestade somente no campo editorial.',
        'alvo_congelado_antes_das_novas_inferencias': True,
        'alteracao_dos_estados_no_editor': False, 'promocao_de_pendencias_a_validacao_visual': False,
        'normalizacao': 'Unicode NFC e colapso de espaços; preservar caixa, diacríticos e grafia histórica.',
        'unidade_principal': 'Contagens por bloco completo e microagregação dos cinco blocos; não média de taxas por linha.',
        'tratamento_de_falhas': 'Saída vazia, contando deleções; sem excluir linhas ou execuções malsucedidas.',
        'metricas': ['CER=(S+D+I)/caracteres de referência', 'WER=(S+D+I)/palavras de referência'],
        'modelos': ['latin PP-OCRv5 mobile/ONNX', 'PP-OCRv6 medium/Kraken'],
        'recortes': 'Os mesmos 24 PNGs, na mesma ordem; nenhum detector ou pós-correção.',
        'pre_processamento': 'Nativo de cada reconhecedor, documentado nas saídas; ambos CPU/float32.',
        'tempos': 'Uma execução sequencial por modelo, sem inferência de superioridade temporal ou economia humana.',
        'avaliador': 'Funções counts/aggregate existentes; os alvos assistidos não são apresentados ao validador como human_diplomatic validado.',
        'linhas_com_ressalvas': [t['linha'] for t in targets if t['estado_visual_original'] != 'validated'],
    }
    write_json(out / 'protocolo.json', protocol)
    write_json(out / 'recortes_congelados.json', crops)
    write_json(out / 'proveniencia_preparacao.json', previous_provenance)
    workspace = ROOT / 'data/workspace_traslado_269r'
    write_json(out / 'preservacao_workspace_antes.json', {relative(p): sha256(p) for p in sorted(workspace.rglob('*')) if p.is_file()})
    paths = [SOURCE / 'inventario.json', *[SOURCE / p for p in source_manifest],
             ROOT / 'src/paleographia/evaluation.py', ROOT / 'src/paleographia/recognition.py',
             ROOT / 'src/paleographia/latin_ocr.py', ROOT / 'src/paleographia/kraken_recognition.py',
             ROOT / 'src/paleographia/kraken_recognition_worker.py']
    paths += [p for p in out.iterdir() if p.is_file()]
    paths += [ROOT / r['crop_image'] for r in inference]
    paths += [ROOT / r['source_image'] for r in inference]
    paths += [ROOT / t['reference_source'] for t in targets]
    write_json(out / 'entradas_congeladas.json', {'arquivos': {relative(p): sha256(p) for p in sorted(set(paths))},
               'pesos': weights, 'imagem_docker': image_id,
               'versao_jiwer': importlib.metadata.version('jiwer')})
    print(json.dumps({'preparado': True, 'linhas': 24, 'ressalvas_preservadas': 8, 'editor_alterado': False}))


def recognize(out, model):
    check_inputs(out, weights=True)
    directory = out / model
    assert not directory.exists(), 'Execução existente: não sobrescrever.'
    directory.mkdir()
    from paleographia.recognition import recognize_lines
    config = load_config(out / 'config_ppocrv6.toml')
    if model == 'ppocrv5':
        from paleographia.latin_ocr import LatinONNXRecognizer
        recognizer = LatinONNXRecognizer(ROOT / 'models/latin_PP-OCRv5_mobile_rec/model.onnx')
    else:
        from paleographia.backends import create_recognizer
        recognizer = create_recognizer(config, ROOT)
    started, stamp = time.perf_counter(), now()
    try:
        predictions = recognize_lines(read_jsonl(out / 'recortes_reconhecimento.jsonl'), recognizer, directory / 'predictions.jsonl', ROOT)
        status = recognizer.status()
    finally:
        close = getattr(recognizer, 'close', None)
        if close:
            close()
    record = provenance(config if model == 'ppocrv6' else {}, [out / 'recortes_reconhecimento.jsonl', out / 'entradas_congeladas.json'])
    record.update(inicio=stamp, termino=now(), tempo_externo_segundos=time.perf_counter()-started,
                  identidade=status, inferencias=24,
                  falhas=sum(p['status'] != 'ok' for p in predictions))
    write_json(directory / 'provenance.json', record)
    check_inputs(out)
    print(json.dumps({'modelo': model, 'linhas': len(predictions), 'falhas': record['falhas'],
                      'segundos_externos': record['tempo_externo_segundos']}, ensure_ascii=True))


def alignments(ref, pred, characters=False):
    result = (jiwer.process_characters if characters else jiwer.process_words)(normalize(ref), normalize(pred))
    r, p = result.references[0], result.hypotheses[0]
    joiner = '' if characters else ' '
    return [{'operacao': chunk.type, 'referencia': joiner.join(r[chunk.ref_start_idx:chunk.ref_end_idx]),
             'predicao': joiner.join(p[chunk.hyp_start_idx:chunk.hyp_end_idx])}
            for chunk in result.alignments[0] if chunk.type != 'equal']


def evaluate_assisted(out):
    check_inputs(out)
    assert not (out / 'comparacao.json').exists(), 'Avaliação existente: não sobrescrever.'
    targets = read_jsonl(out / 'alvos_assistidos.jsonl')
    infer = read_jsonl(out / 'recortes_reconhecimento.jsonl')
    source = read_jsonl(out / 'catalogo_origem.jsonl')
    crop_info = {r['line_id']: r for r in read(out / 'recortes_congelados.json')}
    groups = defaultdict(list)
    for target in targets:
        groups[target['region_id']].append(target)
    summaries, rows, word_errors, char_errors, region_rows = {}, [], [], [], []
    for model in ['ppocrv5', 'ppocrv6']:
        predictions = read_jsonl(out / model / 'predictions.jsonl')
        assert [p['line_id'] for p in predictions] == [t['line_id'] for t in targets]
        assert len(predictions) == 24 and len({p['line_id'] for p in predictions}) == 24
        indexed = {p['line_id']: p for p in predictions}
        for p, entry in zip(predictions, infer):
            assert all(p[k] == entry[k] for k in ['bbox_xyxy', 'reading_order', 'region_id', 'crop_image', 'source_sha256'])
            if model == 'ppocrv6' and p['status'] == 'ok':
                assert p['preprocessing']['pixel_sha256'] == crop_info[p['line_id']]['pixel_sha256']
        region_metrics = []
        for region, refs in groups.items():
            reference = ' '.join(t['texto_alvo'] for t in refs)
            prediction = ' '.join(indexed[t['line_id']]['text_raw'] if indexed[t['line_id']]['status'] == 'ok' else '' for t in refs)
            metrics = counts(reference, prediction)
            region_metrics.append(metrics)
            region_rows.append({'modelo': model, 'region_id': region, 'linhas': [t['linha'] for t in refs],
                                'referencia': reference, 'predicao': prediction, 'metrics': metrics})
        summaries[model] = {'metrics': aggregate(region_metrics), 'linhas': 24, 'blocos': 5,
                            'falhas': sum(p['status'] != 'ok' for p in predictions),
                            'tempo_externo_segundos': read(out / model / 'provenance.json')['tempo_externo_segundos'],
                            'soma_tempos_inferencia_segundos': sum(p.get('recognition_seconds', 0) for p in predictions)}
        for target in targets:
            pred = indexed[target['line_id']]
            text = pred['text_raw'] if pred['status'] == 'ok' else ''
            metrics = counts(target['texto_alvo'], text)
            rows.append({'modelo': model, 'linha': target['linha'], 'line_id': target['line_id'],
                         'referencia': target['texto_alvo'], 'predicao_bruta': text,
                         'estado_visual_original': target['estado_visual_original'],
                         'duvidas_preservadas': target['duvidas_preservadas'], 'metrics': metrics})
            for chars, destination in [(False, word_errors), (True, char_errors)]:
                destination.extend(dict(item, modelo=model, linha=target['linha'],
                                        alvo_com_ressalva=target['estado_visual_original'] != 'validated')
                                   for item in alignments(target['texto_alvo'], text, chars))
    result = {'tipo': 'diagnostico_de_desenvolvimento_com_referencia_assistida',
              'normalizacao': read(out / 'protocolo.json')['normalizacao'],
              'agregacao': 'microcontagens_por_cinco_regioes_completas',
              'linhas': 24, 'linhas_com_ressalvas': 8, 'teste_reservado': False,
              'modelos': summaries, 'metricas_por_linha_somente_diagnosticas': True}
    write_json(out / 'comparacao.json', result)
    write_jsonl(out / 'regioes.jsonl', region_rows)
    write_jsonl(out / 'por_linha.jsonl', rows)
    write_jsonl(out / 'erros_palavras.jsonl', word_errors)
    write_jsonl(out / 'erros_caracteres.jsonl', char_errors)
    with (out / 'por_linha.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['modelo', 'linha', 'alvo', 'predicao_bruta', 'estado_visual', 'CER', 'WER',
                         'erros_caracteres', 'caracteres_referencia', 'erros_palavras', 'palavras_referencia'])
        for row in rows:
            c, w = row['metrics']['characters'], row['metrics']['words']
            writer.writerow([row['modelo'], row['linha'], row['referencia'], row['predicao_bruta'], row['estado_visual_original'],
                             c['rate'], w['rate'], c['errors'], c['reference_length'], w['errors'], w['reference_length']])
    before = read(out / 'preservacao_workspace_antes.json')
    assert all(sha256(ROOT / p) == h for p, h in before.items()), 'Workspace alterado.'
    assert all(t['texto_alvo'] == r['text_diplomatic'] and t['estado_visual_original'] == r['review_status']
               for t, r in zip(targets, source))
    write_json(out / 'preservacao_depois.json', {'workspace_arquivos_conferidos': len(before), 'todos_inalterados': True,
               'referencia_publicada_inalterada': True, 'linhas_pendentes_no_editor_promovidas': 0})
    inventory(out)
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('etapa', choices=['preparar', 'ppocrv5', 'ppocrv6', 'avaliar'])
    parser.add_argument('--output-root', default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = ROOT / args.output_root
    assert output.resolve().is_relative_to(ROOT.resolve())
    if args.etapa == 'preparar':
        prepare(output)
    elif args.etapa in ['ppocrv5', 'ppocrv6']:
        recognize(output, args.etapa)
    else:
        evaluate_assisted(output)
