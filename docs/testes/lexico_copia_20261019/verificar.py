"""Conferência de somente leitura do teste lexical em cópia isolada."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT/name).read_bytes())


def verify():
    manifest = read('evidencias/sha256.json')
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts
              and p.relative_to(ROOT).as_posix()!='evidencias/sha256.json'}
    require(actual==set(manifest), 'Arquivos ausentes ou inesperados no pacote.')
    for name, expected in manifest.items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT), 'Caminho fora da pasta de teste.')
        require(sha(path)==expected, f'Hash divergente: {name}')
    publication = read('publicacao.json')
    require(publication['artifact_type']=='teste_em_copia_isolada'
            and publication['human_reference'] is False, 'Natureza do artefato inválida.')
    for item in publication['original_to_publication']:
        require(sha(ROOT/item['path'])==item['published_sha256'], 'Origem/publicação divergentes.')
        if item['transformation'].startswith('Cópia literal'):
            require(item['source_sha256']==item['published_sha256'], 'Evidência literal alterada.')
    receipt = read('evidencias/verificacao.json')
    states = [read('evidencias/revisions/'+row['revision']+'.json') for row in receipt['history']]
    require(len(states)==3, 'Quantidade de snapshots divergente.')
    for row, state in zip(receipt['history'],states):
        require(sha(ROOT/'evidencias/revisions'/(state['revision']+'.json'))==row['sha256'], 'Snapshot divergente.')
    require(states[0]['revision']==publication['initial_revision']
            and states[-1]['revision']==publication['final_copy_revision'], 'Revisões divergentes.')
    for prior, later, expected_id in zip(states,states[1:],['l_traslado_269r_body_05','l_traslado_269r_body_01']):
        require(later['parent_revision']==prior['revision'], 'Histórico sem encadeamento.')
        require(prior['pages']==later['pages'] and prior['predictions']==later['predictions'], 'Página ou bruto alterado.')
        require(len(prior['lines'])==len(later['lines'])==15, 'Quantidade de linhas divergente.')
        require([b['line_id'] for a,b in zip(prior['lines'],later['lines']) if a!=b]==[expected_id], 'Linha inesperada alterada.')
        for a,b in zip(prior['lines'],later['lines']):
            require(all(a.get(k)==b.get(k) for k in ['bbox_xyxy','reading_order','crop_image','geometry_status','published_reference']), 'Geometria ou apoio alterado.')
    catalog_bytes = (ROOT/'evidencias/sources.json').read_bytes()
    entry_bytes = (ROOT/'evidencias/entries.jsonl').read_bytes()
    fingerprint = hashlib.sha256(catalog_bytes+b'\0'+entry_bytes).hexdigest()
    catalog = json.loads(catalog_bytes)
    # Defaults opcionais do modelo Entry, sem exigir Pydantic neste verificador.
    entries = {e['id']:{'evidence_file':None,'evidence_sha256':None,
                       'variant_of':None,'expansion':None,'corpus_origin':None,**e}
               for e in map(json.loads,entry_bytes.decode('utf-8').splitlines())}
    sources = {s['id']:s for s in catalog['sources']}
    checked_external = set()
    for row in receipt['lines']:
        line = next(l for l in states[-1]['lines'] if l['line_id']==row['line'])
        require(len(line['lexical_assistance'])==1, 'Quantidade de eventos divergente.')
        event = line['lexical_assistance'][0]
        require(event==row['event'] and event['version']==catalog['version']
                and event['fingerprint']==fingerprint, 'Proveniência lexical divergente.')
        require(line['review_status']=='pending_review'
                and line['reviewer']=='Codex · teste de salvamento em cópia isolada', 'Estado de teste divergente.')
        selected = [entries[id] for id in event['entry_ids']]
        require(' '.join(e['form'] for e in selected)==event['replacement'], 'Forma sem atestação.')
        resolved = [dict(e,source=sources[e['source_id']]) for e in selected]
        require(resolved==row['sources'], 'Fonte resolvida divergente.')
        candidate = hashlib.sha256(json.dumps([fingerprint,event['entry_ids'],event['match'],event['replacement']],ensure_ascii=False).encode()).hexdigest()[:24]
        require(candidate==event['candidate_id'], 'Identidade do candidato divergente.')
        require(event['before'][event['start']:event['end']]==event['query'], 'Trecho original divergente.')
        require(event['after']==event['before'][:event['start']]+event['replacement']+event['before'][event['end']:]
                and line['text_diplomatic']==event['after'], 'Substituição pontual divergente.')
        raw = next(p['text_raw'] for p in states[-1]['predictions'] if p['line_id']==row['line'])
        require(event['before']==raw, 'Entrada divergente da predição bruta preservada.')
        for entry in selected:
            path = REPO/entry['source_file']
            if path.is_file():
                require(sha(path)==entry['source_sha256'], 'Atestação de origem divergente.')
                checked_external.add(entry['source_file'])
    preservation = read('evidencias/preservacao_publicacao.json')
    require(preservation['all_unchanged'] and all(r['before']==r['after'] for r in preservation['files'].values()), 'Recibo de preservação divergente.')
    return {'natureza':'teste em cópia isolada','arquivos_conferidos':len(manifest),
            'snapshots':len(states),'eventos_lexicais':len(receipt['lines']),
            'bruto_paginas_e_outras_linhas_preservados':True,
            'arquivos_originais_registrados_na_publicacao':len(preservation['files']),
            'arquivos_de_fonte_conferidos_no_checkout':len(checked_external),
            'nota':'A fonte externa ao pacote foi conferida no checkout.' if checked_external else 'Fonte externa ao pacote indisponível; conferência adicional requer o checkout.'}


if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=True,indent=2))
