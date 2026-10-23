"""Confere o pacote de entrega sem executar modelos, treinar ou escrever arquivos."""
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZipFile
import hashlib
import json
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET

from pypdf import PdfReader

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ler(path):
    return json.loads(Path(path).read_bytes())


def linhas(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]


def normal(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFC', text).replace('\xad', ''))


def objetos_git_do_trabalho(prefixo):
    nomes = subprocess.check_output(['git', 'ls-files', '-z', '--', prefixo], cwd=ROOT).decode('utf-8').split('\0')
    nomes = [n for n in nomes if n]
    # Aplica os mesmos filtros de fim de linha do Git, sem gravar objetos.
    # Os arquivos antigos continuam com os bytes locais preservados; o recibo
    # precisa identificar o mesmo conteúdo em checkouts Windows e Linux.
    proc = subprocess.run(['git', 'hash-object', '--stdin-paths'], cwd=ROOT,
        input='\n'.join(nomes)+'\n', capture_output=True, text=True, check=True)
    objetos = proc.stdout.splitlines()
    assert len(objetos) == len(nomes)
    return dict(zip(nomes, objetos, strict=True))


def conferir_artigo():
    md = (BASE / 'artigo.md').read_text(encoding='utf-8')
    anterior = (BASE.parent / 'pi_iv_pln_20261023_entrega/artigo.md').read_text(encoding='utf-8')
    assert md.split('## Disponibilidade dos materiais')[0] == anterior.split('## Disponibilidade dos materiais')[0]
    body, refs = md.split('## Referências bibliográficas\n\n')
    records = ler(BASE / 'citacoes.json')['references']
    entries = refs.strip().split('\n\n')
    assert len(entries) == len(records) == 9
    for entry, record in zip(entries, records, strict=True):
        assert entry.startswith(record['author']), record['key']
        assert re.search(record['pattern'], body), record['key']
        if 'local_source' in record:
            assert sha(ROOT / record['local_source']) == record['source_sha256']
    anteriores = ler(BASE.parent / 'pi_iv_pln_20261023_entrega/citacoes.json')['references']
    assert all(r in records for r in anteriores), 'Escopo das oito consultas anteriores foi alterado.'
    pdf = PdfReader(BASE / 'artigo.pdf')
    assert len(pdf.pages) == 3
    pdftext = '\n'.join(p.extract_text() for p in pdf.pages)
    pdftext = re.sub(r'\b00[123]\s*\|\s*Página\s*', '', pdftext)
    with ZipFile(BASE / 'artigo.docx') as pacote:
        doc = ET.fromstring(pacote.read('word/document.xml'))
        rels = ET.fromstring(pacote.read('word/_rels/document.xml.rels'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    doctext = ''.join(e.text or '' for e in doc.findall('.//w:t', ns))
    cobertura = 0
    for block in md.strip().split('\n\n'):
        if block.startswith('|'):
            # Cada célula da tabela deve existir nos dois formatos.
            blocks = [v.strip() for line in block.splitlines() if not re.match(r'^\|\s*:?-', line)
                      for v in line.strip('|').split('|')]
        else:
            blocks = [re.sub(r'^#+\s*', '', re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', block)).replace('**', '')]
        for plain in blocks:
            assert normal(plain) in normal(doctext), 'Texto ausente no Word: ' + plain[:70]
            assert normal(plain) in normal(pdftext), 'Texto ausente no PDF: ' + plain[:70]
            cobertura += 1
    expected = {unquote(u).rstrip('/') for u in re.findall(r'\]\((https?://[^)]+)\)', md)}
    doclinks = {unquote(r.attrib['Target']).rstrip('/') for r in rels if r.attrib.get('Type', '').endswith('/hyperlink')}
    pdflinks = set()
    for page in pdf.pages:
        for annotation in page.get('/Annots', []):
            action = annotation.get_object().get('/A', {})
            if action.get('/URI'):
                pdflinks.add(unquote(str(action['/URI'])).rstrip('/'))
    assert expected <= doclinks and expected <= pdflinks, 'Link ausente nos formatos finais.'
    assert normal('Magᵈᵉ') in normal(pdftext)
    assert all(value in pdftext for value in ['58,45%', '94,58%', '15,11%', '60,10%', '650/1.112', '168/1.112'])
    return dict(paginas=3, referencias=9, blocos_e_celulas_conferidos=cobertura,
                links_conferidos=len(expected), texto_markdown_docx_pdf_correspondente=True)


def conferir_dataset():
    catalogo = ROOT / 'data/manifests/corpus_expandido_v02'
    grupos = ler(catalogo / 'partitions.json')['groups']
    core = linhas(catalogo / 'core_lines.jsonl')
    candidatos = linhas(ROOT / 'docs/dataset_expansion_20261023/curation_sessao_1795_bloco01/lines.jsonl')
    assert len(core) == 24 and sum(r['review_status'] == 'validated' for r in core) == 16
    assert len(candidatos) == 8
    assert all(r['text_diplomatic'] is None and r['review_status'] == 'pending_review'
               and r['geometry_status'] == 'pending_review' and r['split'] is None for r in candidatos)
    assert len(grupos) == len({g['document_id'] for g in grupos}) == 7
    assert all(g['independence_status'] == 'pending_review' and g['scientific_split'] is None for g in grupos)
    assert sum(g['eligible_new_pairs'] for g in grupos) == 0
    fontes = linhas(catalogo / 'sources.jsonl')
    paginas = linhas(catalogo / 'pdf_pages.jsonl')
    ocorrencias = linhas(catalogo / 'image_occurrences.jsonl')
    assert len(fontes) == 15 and len(paginas) == 59 and len(ocorrencias) == 28
    return dict(fontes=15, paginas_pdf=59, ocorrencias_manuscrito=28, grupos_candidatos=7,
                grupos_com_independencia_confirmada=0, linhas_historicas=24,
                linhas_historicas_validadas=16, ressalvas=8, novos_candidatos=8,
                novos_pares_aptos=0, particoes_cientificas=dict(train=0, validation=0, test=0))


def conferir_recibo():
    caminho = BASE / 'fechamento.json'
    if not caminho.exists():
        return {'recibo': 'ainda_nao_gerado'}
    recibo = ler(caminho)
    for name, digest in recibo['arquivos'].items():
        assert sha(BASE / name) == digest, 'Arquivo do pacote divergente: ' + name
    for group in recibo['preservacao']['pacotes']:
        hashes = objetos_git_do_trabalho(group['prefixo'])
        observed = hashlib.sha256(json.dumps(hashes, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        assert len(hashes) == group['quantidade_arquivos']
        assert observed == group['sha256_do_conjunto'], 'Pacote histórico divergente: ' + group['prefixo']
    baseline = recibo['baseline']
    observado = objetos_git_do_trabalho(baseline['notebook'])[baseline['notebook']]
    assert observado == baseline['notebook_git_blob'], 'Fonte do notebook difere do objeto Git executado.'
    publicado = subprocess.check_output(['git', 'cat-file', 'blob', observado], cwd=ROOT)
    assert hashlib.sha256(publicado).hexdigest() == baseline['notebook_publicado_sha256']
    assert recibo['baseline']['resultado'] == 'aprovado'
    assert recibo['baseline']['novos_registros_individuais'] == 0
    assert recibo['submissao']['executada'] is False and recibo['revisao_humana']['novas_validacoes'] == 0
    return {'arquivos_do_pacote': len(recibo['arquivos']), 'pacotes_historicos': len(recibo['preservacao']['pacotes'])}


if __name__ == '__main__':
    print(json.dumps(dict(resultado='aprovado', artigo=conferir_artigo(), dataset=conferir_dataset(),
                         integridade=conferir_recibo()), ensure_ascii=False, indent=2))
