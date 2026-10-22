"""Diagnóstico integral do 269v contra a edição, com componentes existentes."""
import argparse
import copy
import csv
import hashlib
import json
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path

import jiwer
from PIL import Image
from pypdf import PdfReader

from paleographia.config import load_config
from paleographia.data import validate
from paleographia.evaluation import counts, normalize
from paleographia.experiments import provenance
from paleographia.io import now, read_jsonl, sha256, write_json, write_jsonl

ROOT = Path.cwd().resolve()
DEFAULT = 'docs/experimentos/traslado_269v_integral_edicao_20261022'
PDF = 'docs/experimentos/traslado_269r_20261016/support/edition.pdf'
FACSIMILE = 'data/raw/import_20261015/6e82cef18b04_5b58a915f024a80e.pdf'
PREVIOUS = 'docs/experimentos/traslado_269r_integral_edicao_20261022'
PDF_SHA = '3fa01bf328add9393c8a79896f94d39db292fe51543c49ea679b33a3ec069b65'
IMAGE_SHA = '63e18446dc3e31f8c0b444679650b2220035ef3ef602956d4659e762b3107251'
FACSIMILE_SHA = 'e1c779a4713340adbf5e6102b0c3edc716c12612d18597e9d22228676ab9b3e0'
AREAS = [('corpo', 0, 1883)]


def read(path):
    return json.loads(Path(path).read_bytes())


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def tree(folder):
    return {relative(p): sha256(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def preservation():
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    return {'versionados': {name: sha256(ROOT/name) for name in tracked if name and (ROOT/name).is_file()},
            'workspaces': {relative(p): sha256(p) for folder in (ROOT/'data').glob('workspace*')
                           if folder.is_dir() for p in sorted(folder.rglob('*')) if p.is_file()}}


def check_preservation(out):
    old = read(out/'preservacao_antes.json')
    assert preservation() == old, 'Arquivos versionados ou workspaces foram alterados.'
    return {'arquivos_versionados_inalterados': len(old['versionados']),
            'arquivos_workspace_inalterados': len(old['workspaces']),
            'editor_alterado': False, 'estados_humanos_promovidos': 0}


def inputs(out, weights=False):
    frozen = read(out/'entradas_congeladas.json')
    for name, expected in frozen['arquivos'].items():
        assert sha256(ROOT/name) == expected, 'Entrada divergente: ' + name
    if weights:
        for name, expected in frozen['pesos'].items():
            assert sha256(ROOT/name) == expected, 'Pesos divergentes: ' + name
        cfg = load_config(out/'config.toml')
        image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}',
                                            cfg['recognition']['docker_image']], text=True).strip()
        assert image_id == frozen['imagem_docker']
    return frozen


def prepare(out):
    assert not out.exists(), 'Escolha uma pasta nova.'
    assert sha256(ROOT/PDF) == PDF_SHA and sha256(ROOT/FACSIMILE) == FACSIMILE_SHA
    before = preservation()
    baseline = ROOT/PREVIOUS
    cfg = load_config(baseline/'config.toml')
    assert cfg == load_config(ROOT/'configs/traslado_269r.toml')
    assert sha256(ROOT/cfg['recognition']['model']) == cfg['recognition']['sha256']
    image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}',
                                        cfg['recognition']['docker_image']], text=True).strip()
    assert image_id == cfg['recognition']['docker_image_id']
    embedded = PdfReader(ROOT/FACSIMILE).pages[1].images[0]
    assert hashlib.sha256(embedded.data).hexdigest() == IMAGE_SHA
    assert embedded.image.size == (1195, 1883)
    reader = PdfReader(ROOT/PDF)
    text = [reader.pages[i].extract_text() for i in [1, 2]]
    lines = [[line for line in t.splitlines() if line.strip()] for t in text]
    a, b = lines
    start, stop = a.index('269/Verso.')+1, b.index('270')
    assert len(a[start:]) == 10 and stop == 24
    assert a[start].startswith('Magestade Huã e muitas vezes Como Cap')
    assert b[stop-1] == 'Machado Castello Branco = Antonio Luis da penha'
    positions = [(0, i) for i in range(start, len(a))] + [(1, i) for i in range(stop)]
    targets = [{'area': 'corpo', 'ordem_na_area': order, 'pagina_pdf': page+2,
                'indice_linha_extraida_sem_vazias': line, 'texto_extraido_original': lines[page][line],
                'texto_alvo': lines[page][line].strip(),
                'tipo_referencia': 'edicao_publicada_sem_nova_revisao_humana',
                'validacao_humana_nova': False} for order, (page, line) in enumerate(positions)]
    assert len(targets) == 34
    out.mkdir(parents=True)
    shutil.copyfile(Path(__file__), out/'reproduzir.py')
    shutil.copyfile(baseline/'config.toml', out/'config.toml')
    image_path = out/'manuscrito_269v_original.jpg'
    image_path.write_bytes(embedded.data)
    write_json(out/'imagem_extraida.json', {'fonte': FACSIMILE, 'fonte_sha256': FACSIMILE_SHA,
               'pagina_pdf': 2, 'indice_imagem': 0, 'nome_imagem_embutida': embedded.name,
               'imagem': relative(image_path), 'imagem_sha256': IMAGE_SHA, 'dimensoes': [1195, 1883],
               'metodo': 'Bytes JPEG embutidos extraídos por pypdf, sem renderização, filtros ou reamostragem.',
               'correspondencia_inspecionada_por': 'Codex, assistente de IA; sem nova validação humana.'})
    page = copy.deepcopy(read_jsonl(ROOT/'data/manifests/traslado_269r/pages.jsonl')[0])
    page.update(page_id='p_traslado_269v', folio_id='269v', side='verso', source_image=relative(image_path),
                original_name='manuscrito_269v_original.jpg', width=1195, height=1883, source_sha256=IMAGE_SHA,
                transcribed_coverage=[], correspondence_status='pending_review', reviewer=None, reviewed_at=None)
    page['nota_experimento'] = '269 verso: imagem inteira extraída da página 2 do fac-símile; sem recortes humanos.'
    page.pop('comparison_source', None)
    page.pop('geometry_notes', None)
    page.pop('identification_basis', None)
    write_jsonl(out/'pagina_reconhecimento.jsonl', [page])
    write_json(out/'edicao_extraida.json', {'fonte': PDF, 'sha256': PDF_SHA, 'paginas': [
        {'pagina_pdf': i+2, 'texto_extraido': t, 'linhas_sem_vazias': lines[i]} for i, t in enumerate(text)]})
    write_jsonl(out/'alvos_editoriais.jsonl', targets)
    (out/'texto_oficial.txt').write_text('\n'.join(t['texto_alvo'] for t in targets)+'\n', encoding='utf-8')
    protocol = {
        'criado_em': now(), 'tipo': 'diagnostico_de_desenvolvimento_contra_edicao_publicada',
        'pedido': 'Testar o 269 verso contra a transcrição oficial com os mesmos pesos e parâmetros, preservando bruto e revisões.',
        'folio': '269v', 'unidades_editoriais': 34, 'modelo': 'PP-OCRv6 medium/Kraken',
        'segmentacao': 'OpenCV/projeção na imagem inteira, sem ajuste de parâmetros.',
        'configuracao_do_reto_sha256': sha256(baseline/'config.toml'),
        'parametros_identicos_ao_reto': True, 'recortes_humanos_usados_na_medicao_principal': False,
        'referencia': 'Trechos literais da edição nas páginas PDF 2 e 3, após 269/Verso. e antes de 270.',
        'exclusoes_editoriais': ['Marcador editorial 269/Verso. ausente da imagem manuscrita',
                                'Final do 269 reto e conteúdo do 270 e seguintes', 'Metadados e créditos editoriais'],
        'normalizacao': 'NFC e colapso de espaços igualmente nos dois lados; preservar caixa, grafia, acentos, pontuação e desenvolvimentos editoriais.',
        'metrica_principal': 'Uma sequência do verso completo: concatenar todas as unidades editoriais e todas as saídas automáticas em ordem com espaço, sem excluir recortes ou falhas; CER/WER por distância de edição.',
        'areas_y': [{'area': 'corpo', 'inicio_inclusivo': 0, 'fim_exclusivo': 1883}],
        'falhas': 'Saída vazia, contando omissões; nenhum recorte difícil removido.',
        'convencoes_editoriais': 'Mantidos os sinais =, as grafias dos nomes, os espaços e as quebras editoriais. Expansões como Magestade permanecem como na edição.',
        'fonte_nao_fornecida_ao_reconhecedor': True, 'treinamento': False, 'teste_reservado': False,
        'referencia_humana_independente': False, 'promocao_de_estados_humanos': False,
        'ressalvas_historicas_do_reto_preservadas': [11, 15, 16, 17, 19, 20, 23, 24],
        'comparabilidade': 'Mesmo pipeline e parâmetros do reto integral, em conteúdo diferente do mesmo documento; comparação descritiva, sem alegação de generalização entre documentos.'}
    write_json(out/'protocolo.json', protocol)
    write_json(out/'preservacao_antes.json', before)
    paths = [ROOT/PDF, ROOT/FACSIMILE, baseline/'config.toml', baseline/'comparacao.json',
             *[p for p in out.iterdir() if p.is_file()],
             ROOT/'src/paleographia/segmentation.py', ROOT/'src/paleographia/recognition.py',
             ROOT/'src/paleographia/kraken_recognition.py', ROOT/'src/paleographia/kraken_recognition_worker.py',
             ROOT/'src/paleographia/evaluation.py']
    write_json(out/'entradas_congeladas.json', {'criado_em': now(), 'arquivos': {relative(p): sha256(p) for p in paths},
               'pesos': {cfg['recognition']['model']: cfg['recognition']['sha256']}, 'imagem_docker': image_id,
               'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})
    print(json.dumps({'etapa': 'preparado', 'unidades_editoriais': len(targets), 'inferencias': 0}))


def segment(out):
    from paleographia.segmentation import segment_pages
    inputs(out)
    cfg = load_config(out/'config.toml')
    lines, timings = segment_pages(read_jsonl(out/'pagina_reconhecimento.jsonl'), 'opencv', cfg, out/'segmentacao', ROOT)
    assert all(line['text_diplomatic'] is None and line['reference_kind'] == 'unknown' for line in lines)
    assert validate(lines, ROOT, 'catalog', read_jsonl(out/'pagina_reconhecimento.jsonl'))['valid']
    write_json(out/'segmentacao'/'proveniencia.json', provenance(cfg, [out/'pagina_reconhecimento.jsonl', out/'entradas_congeladas.json']))
    print(json.dumps({'etapa': 'segmentado', 'recortes_automaticos': len(lines)}))


def recognize(out):
    from paleographia.backends import create_recognizer
    from paleographia.recognition import recognize_lines
    inputs(out, weights=True)
    lines = read_jsonl(out/'segmentacao/lines.jsonl')
    assert all(line['text_diplomatic'] is None for line in lines)
    cfg = load_config(out/'config.toml')
    directory = out/'ppocrv6'
    assert not directory.exists(), 'Saída bruta existente; não sobrescrever.'
    directory.mkdir()
    write_json(directory/'entradas_recortes.json', {r['line_id']: {'sha256': sha256(ROOT/r['crop_image']),
               'pixel_sha256': hashlib.sha256(Image.open(ROOT/r['crop_image']).convert('RGB').tobytes()).hexdigest()}
               for r in lines})
    recognizer = create_recognizer(cfg, ROOT)
    start, stamp = time.perf_counter(), now()
    try:
        predictions = recognize_lines(lines, recognizer, directory/'predictions.jsonl', ROOT)
        status = recognizer.status()
    finally:
        recognizer.close()
    record = provenance(cfg, [out/'segmentacao/lines.jsonl', out/'entradas_congeladas.json'])
    record.update(inicio=stamp, fim=now(), inferencias=len(lines), falhas=sum(p['status'] != 'ok' for p in predictions),
                  tempo_externo_segundos=time.perf_counter()-start, identidade=status)
    write_json(directory/'proveniencia.json', record)
    print(json.dumps({'etapa': 'reconhecido', 'inferencias': len(lines), 'falhas': record['falhas']}, ensure_ascii=True))


def area_for(row):
    y = (row['bbox_xyxy'][1]+row['bbox_xyxy'][3])/2
    return next(name for name, y0, y1 in AREAS if y0 <= y < y1)


def word_errors(reference, prediction):
    aligned = jiwer.process_words(normalize(reference), normalize(prediction))
    ref, hyp = aligned.references[0], aligned.hypotheses[0]
    return [{'operacao': c.type, 'referencia': ' '.join(ref[c.ref_start_idx:c.ref_end_idx]),
             'predicao': ' '.join(hyp[c.hyp_start_idx:c.hyp_end_idx]),
             'intervalo_referencia': [c.ref_start_idx, c.ref_end_idx],
             'intervalo_predicao': [c.hyp_start_idx, c.hyp_end_idx],
             'contexto_anterior_referencia': ' '.join(ref[max(0, c.ref_start_idx-4):c.ref_start_idx]),
             'contexto_posterior_referencia': ' '.join(ref[c.ref_end_idx:c.ref_end_idx+4])}
            for c in aligned.alignments[0] if c.type != 'equal']


def evaluate(out):
    inputs(out)
    assert not (out/'comparacao.json').exists(), 'Avaliação existente; não sobrescrever.'
    targets = read_jsonl(out/'alvos_editoriais.jsonl')
    predictions = read_jsonl(out/'ppocrv6/predictions.jsonl')
    crops = read_jsonl(out/'segmentacao/lines.jsonl')
    assert [p['line_id'] for p in predictions] == [r['line_id'] for r in crops]
    assert [r['reading_order'] for r in crops] == list(range(len(crops)))
    reference = ' '.join(t['texto_alvo'] for t in targets)
    raw = ' '.join(p['text_raw'] if p['status'] == 'ok' else '' for p in predictions)
    metrics = counts(reference, raw)
    groups = []
    for name, y0, y1 in AREAS:
        selected = [p for p in predictions if area_for(p) == name]
        ref = ' '.join(t['texto_alvo'] for t in targets if t['area'] == name)
        hyp = ' '.join(p['text_raw'] if p['status'] == 'ok' else '' for p in selected)
        groups.append({'area': name, 'referencia': ref, 'predicao_bruta': hyp, 'recortes': len(selected),
                       'unidades_editoriais': sum(t['area'] == name for t in targets), 'metrics': counts(ref, hyp),
                       'caixas_cruzando_limite': [p['line_id'] for p in selected
                                                 if p['bbox_xyxy'][1] < y0 or p['bbox_xyxy'][3] > y1]})
    (out/'transcricao_bruta.txt').write_text('\n'.join(p['text_raw'] if p['status'] == 'ok' else '' for p in predictions)+'\n', encoding='utf-8')
    result = {'tipo': 'diagnostico_de_desenvolvimento_contra_edicao_publicada', 'folio': '269v',
              'escopo': '269 verso completo, incluindo texto e nomes/assinaturas constantes da edição; sem 269 reto ou 270.',
              'modelo': 'PP-OCRv6 medium/Kraken', 'recortes_automaticos': len(predictions),
              'unidades_editoriais': len(targets), 'falhas': sum(p['status'] != 'ok' for p in predictions),
              'metrics': metrics, 'normalizacao': read(out/'protocolo.json')['normalizacao'],
              'treinamento': False, 'teste_reservado': False, 'referencia_humana_independente': False,
              'promocao_de_estados_humanos': False, 'restricao': 'Diagnóstico em outra página do mesmo documento; não é teste reservado nem demonstra generalização entre documentos.'}
    write_json(out/'comparacao.json', result)
    write_jsonl(out/'por_area.jsonl', groups)
    write_jsonl(out/'erros_palavras.jsonl', word_errors(reference, raw))
    with (out/'por_area.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['area', 'recortes_automaticos', 'unidades_editoriais', 'CER', 'WER', 'erros_caracteres', 'caracteres_referencia', 'erros_palavras', 'palavras_referencia'])
        for row in [{'area': 'pagina_inteira', 'recortes': len(predictions), 'unidades_editoriais': len(targets), 'metrics': metrics}, *groups]:
            c, w = row['metrics']['characters'], row['metrics']['words']
            writer.writerow([row['area'], row['recortes'], row['unidades_editoriais'], c['rate'], w['rate'], c['errors'], c['reference_length'], w['errors'], w['reference_length']])
    write_json(out/'preservacao_depois.json', check_preservation(out))
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('etapa', choices=['preparar', 'segmentar', 'reconhecer', 'avaliar'])
    parser.add_argument('--output-root', default=DEFAULT)
    args = parser.parse_args()
    out = (ROOT/args.output_root).resolve()
    assert out.is_relative_to(ROOT) and out != ROOT
    {'preparar': prepare, 'segmentar': segment, 'reconhecer': recognize, 'avaliar': evaluate}[args.etapa](out)
