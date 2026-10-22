"""Auditoria aditiva v2 do 269v: PDF externo ou conferência parcial explícita."""
import argparse
import importlib.util
import sys
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

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'docs/experimentos/traslado_269v_integral_edicao_20261022'
FACSIMILE = 'data/raw/import_20261015/6e82cef18b04_5b58a915f024a80e.pdf'
PDF_SHA = 'e1c779a4713340adbf5e6102b0c3edc716c12612d18597e9d22228676ab9b3e0'
BASE_GIT = '4d429c9c1a51d616b84452269895e4951f4464c4'
AUDITOR_HISTORICO_SHA = 'f846eee77db4ca7cfee7a7d494baee1a93e00bee2c0af2ccd86c919813cad88d'
COMANDO = 'python docs/manutencao/reprodutibilidade_269v_20261022/verificar.py'
AREAS = [('corpo', 0, 1883)]


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def sha(path):
    require(path.is_file(), 'Arquivo necessário ausente: '+str(path))
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


def fonte_original(facsimile):
    path = Path(facsimile).expanduser().resolve() if facsimile is not None else ROOT/FACSIMILE
    instruction = (' SHA-256 obrigatório: '+PDF_SHA+'. Próximo comando: '+COMANDO+
                   ' --facsimile "CAMINHO/74780.pdf". Para conferir apenas os artefatos, use '+
                   COMANDO+' --modo artefatos (resultado parcial; não compara o PDF original). '+
                   'Recuperação pelo RAR versionado e download: docs/manutencao/reprodutibilidade_269v_20261022/README.md.')
    require(path.is_file(), 'PDF original ausente: '+str(path)+'.'+instruction)
    actual = sha(path)
    require(actual == PDF_SHA, 'PDF original incorreto: '+str(path)+'. SHA-256 encontrado: '+actual+'.'+instruction)
    return path


def verificar(facsimile=None, modo='completo'):
    require(modo in {'completo', 'artefatos'}, 'Modo de auditoria inválido.')
    require(modo != 'artefatos' or facsimile is None,
            'Use --facsimile somente no modo completo; artefatos não verifica o PDF original.')
    source = fonte_original(facsimile) if modo == 'completo' else None
    require(sha(BASE/'verificar.py') == AUDITOR_HISTORICO_SHA, 'Verificador histórico divergente da versão-base.')
    inventory = read(BASE/'inventario.json')
    actual = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()
              and p.name != 'inventario.json' and '__pycache__' not in p.parts}
    require(actual == set(inventory), 'Arquivos ausentes ou inesperados no pacote.')
    for name, expected in inventory.items():
        path = (BASE/name).resolve()
        require(path.is_relative_to(BASE) and sha(path) == expected, 'Hash divergente: '+name)
    frozen = read(BASE/'entradas_congeladas.json')
    require(frozen['arquivos'][FACSIMILE] == PDF_SHA, 'Identidade histórica do PDF divergente.')
    for name, expected in frozen['arquivos'].items():
        if name == FACSIMILE:
            if source is not None:
                require(sha(source) == expected, 'Fonte externa diverge da entrada congelada.')
            continue
        require(sha(ROOT/name) == expected, 'Entrada congelada divergente: '+name)
    protocol = read(BASE/'protocolo.json')
    require(protocol['tipo'] == 'diagnostico_de_desenvolvimento_contra_edicao_publicada'
            and not protocol['treinamento'] and not protocol['teste_reservado']
            and not protocol['referencia_humana_independente']
            and not protocol['promocao_de_estados_humanos']
            and not protocol['recortes_humanos_usados_na_medicao_principal'], 'Experimento promovido indevidamente.')
    require(protocol['ressalvas_historicas_do_reto_preservadas'] == [11, 15, 16, 17, 19, 20, 23, 24],
            'Ressalvas históricas perdidas.')
    extraction = read(BASE/'edicao_extraida.json')
    require(sha(ROOT/extraction['fonte']) == extraction['sha256'], 'Edição divergente.')
    pdf = PdfReader(ROOT/extraction['fonte'])
    for page in extraction['paginas']:
        require(pdf.pages[page['pagina_pdf']-1].extract_text() == page['texto_extraido'], 'Extração da edição divergente.')
    target = rows(BASE/'alvos_editoriais.jsonl')
    require(len(target) == 34 and all(t['area'] == 'corpo' for t in target), 'Cobertura editorial incompleta.')
    pages = {p['pagina_pdf']: p for p in extraction['paginas']}
    a, b = pages[2]['linhas_sem_vazias'], pages[3]['linhas_sem_vazias']
    positions = [(2, i) for i in range(a.index('269/Verso.')+1, len(a))]
    positions += [(3, i) for i in range(b.index('270'))]
    require(len(positions) == 34 and sum(p == 2 for p, _ in positions) == 10,
            'Limites da fonte editorial divergentes.')
    require([(t['pagina_pdf'], t['indice_linha_extraida_sem_vazias']) for t in target] == positions,
            'Ordem ou seleção editorial divergente.')
    require([t['ordem_na_area'] for t in target] == list(range(34)), 'Ordem dos alvos divergente.')
    for item in target:
        raw = pages[item['pagina_pdf']]['linhas_sem_vazias'][item['indice_linha_extraida_sem_vazias']]
        require(raw == item['texto_extraido_original'] and raw.strip() == item['texto_alvo']
                and item['validacao_humana_nova'] is False
                and item['tipo_referencia'] == 'edicao_publicada_sem_nova_revisao_humana',
                'Texto editorial alterado ou promovido.')
    image_source = read(BASE/'imagem_extraida.json')
    require(image_source['fonte'] == FACSIMILE and image_source['fonte_sha256'] == PDF_SHA,
            'Proveniência histórica do fac-símile divergente.')
    if source is not None:
        require(sha(source) == image_source['fonte_sha256'], 'Fac-símile divergente.')
        embedded = PdfReader(source).pages[1].images[0]
        require(embedded.data == (BASE/'manuscrito_269v_original.jpg').read_bytes()
                and embedded.image.size == (1195, 1883), 'Imagem não corresponde ao original embutido.')
    require((BASE/'config.toml').read_bytes() ==
            (ROOT/'docs/experimentos/traslado_269r_integral_edicao_20261022/config.toml').read_bytes()
            and protocol['parametros_identicos_ao_reto'], 'Parâmetros divergentes do reto.')
    require((BASE/'texto_oficial.txt').read_text(encoding='utf-8') == '\n'.join(t['texto_alvo'] for t in target)+'\n',
            'Texto oficial divergente.')
    lines = rows(BASE/'segmentacao/lines.jsonl')
    predictions = rows(BASE/'ppocrv6/predictions.jsonl')
    require([p['line_id'] for p in predictions] == [line['line_id'] for line in lines]
            and len({p['line_id'] for p in predictions}) == len(lines), 'Predições ausentes ou duplicadas.')
    require(len(lines) == 36, 'Número de recortes divergente.')
    require([line['reading_order'] for line in lines] == list(range(len(lines))), 'Ordem automática divergente.')
    page = rows(BASE/'pagina_reconhecimento.jsonl')[0]
    require(page['page_id'] == 'p_traslado_269v' and page['correspondence_status'] == 'pending_review'
            and page['reviewer'] is None and not page['transcribed_coverage'], 'Regiões humanas inseridas na segmentação.')
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
                        and pred['model']['docker_image_id'] == frozen['imagem_docker']
                        and pred['model']['worker_sha256'] == load_config(BASE/'config.toml')['presentation']['evaluated_worker_sha256'], 'Modelo divergente.')
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
    spec = importlib.util.spec_from_file_location('reproducao_historica_269v', BASE/'reproduzir.py')
    historical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(historical)
    word_errors = historical.word_errors
    require(rows(BASE/'erros_palavras.jsonl') == word_errors(ref, hyp), 'Alinhamentos de erros divergentes.')
    infer = read(BASE/'ppocrv6/proveniencia.json')
    require(infer['config'] == load_config(BASE/'config.toml'), 'Configuração da execução divergente.')
    require([p['reading_order'] for p in predictions if not p['text_raw'].strip()] == [0, 35],
            'Saídas vazias diferentes das arquivadas.')
    require(datetime.fromisoformat(frozen['criado_em']) <= datetime.fromisoformat(infer['inicio']), 'Referência congelada após a inferência.')
    require(infer['inferencias'] == len(predictions), 'Número de inferências divergente.')
    before, after = read(BASE/'preservacao_antes.json'), read(BASE/'preservacao_depois.json')
    prefixes = ['docs/entregas/pi_iv_pln_20261020/', 'docs/entregas/pi_iv_pln_20261022/',
                'docs/revisao_humana/traslado_269r/referencia_assistida_20261020/',
                'docs/revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/',
                'docs/experimentos/traslado_269r_reconhecedores_24_20261020/',
                'docs/experimentos/traslado_269r_integral_edicao_20261022/']
    preserved = {name: h for name, h in before['versionados'].items() if any(name.startswith(p) for p in prefixes)}
    require(all(sha(ROOT/name) == h for name, h in preserved.items()), 'Pacote histórico alterado.')
    require(after['arquivos_versionados_inalterados'] == len(before['versionados'])
            and after['arquivos_workspace_inalterados'] == len(before['workspaces'])
            and not after['editor_alterado'] and after['estados_humanos_promovidos'] == 0, 'Recibo de preservação inválido.')
    return {'resultado': 'aprovado' if source is not None else 'conferencia_parcial_aprovada',
            'versao_auditoria': 2, 'base_git_historica': BASE_GIT, 'modo': modo,
            'auditoria_completa': source is not None,
            'hash_pdf_original_verificado': source is not None,
            'comparacao_bytes_imagem_embutida_executada': source is not None,
            'facsimile_fornecido': str(source) if source is not None else None,
            'caminho_original_preservado': FACSIMILE, 'sha256_pdf_esperado': PDF_SHA,
            'checagens_nao_executadas': [] if source is not None else
                ['Hash dos bytes do PDF original', 'Comparação do JPEG publicado com a imagem embutida no PDF original'],
            'novas_inferencias': 0, 'tipo': saved['tipo'],
            'arquivos_conferidos': len(inventory), 'recortes_automaticos': len(lines),
            'unidades_editoriais': 34, 'pacotes_historicos_arquivos_conferidos': len(preserved),
            'editor_alterado': False, 'treinamento': False, 'referencia_independente': False,
            'metrics': measured, 'distancias_conferidas_independentemente': True}


class Argumentos(argparse.ArgumentParser):
    def format_usage(self):
        return super().format_usage().replace('usage:', 'uso:', 1)

    def format_help(self):
        return super().format_help().replace('usage:', 'uso:', 1)

    def error(self, message):
        self.exit(2, 'Argumentos inválidos. Consulte '+COMANDO+' --help.\n')


def main():
    parser = Argumentos(description=__doc__, add_help=False,
                        usage='%(prog)s [--modo {completo,artefatos}] [--facsimile CAMINHO]')
    parser._optionals.title = 'opções'
    parser.add_argument('-h', '--help', action='help', help='mostrar esta ajuda e sair')
    parser.add_argument('--modo', choices=['completo', 'artefatos'], default='completo',
                        help='completo exige o PDF original; artefatos aprova somente a conferência parcial')
    parser.add_argument('--facsimile', metavar='CAMINHO', help='PDF original externo, com SHA-256 obrigatório')
    args = parser.parse_args()
    try:
        result = verificar(args.facsimile, args.modo)
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({'resultado': 'reprovado', 'modo': args.modo,
                          'auditoria_completa': False, 'erro': str(error),
                          'novas_inferencias': 0}, ensure_ascii=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
