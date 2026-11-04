"""Materializa apenas imagens para o ensaio técnico VGSL."""
import json
import sys
from pathlib import Path

from PIL import Image
from paleographia.io import read_jsonl, sha256, write_json


BASE = Path('output/curadoria_contrato_livro13_1763/piloto_pagina_05')
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True)
manifests = [
    Path(f'docs/experimentos/traslado_{side}_integral_edicao_20261022/segmentacao/lines.jsonl')
    for side in ('269r', '269v')
]
train = [
    (row, path, Path(row['crop_image']))
    for path in manifests
    for row in sorted(read_jsonl(path), key=lambda row: row['reading_order'])[1:-1]
]
pilot = Path('docs/revisao_humana/contrato_livro13_1763/preparacao_20261104/piloto_pagina_05.json')
validation = [
    (
        row, pilot,
        BASE / 'diagnostico_linha_a_retificada_01/complemento_textura/antitrama_inteira.png'
        if row['pilot_label'] == 'A'
        else BASE / 'diagnostico_linhas_bcd_01' / f"{row['pilot_label']}_antitrama_inteira.png",
    )
    for row in json.loads(pilot.read_bytes())['rows']
]
expected_documents = {'train': 'tt_pbr_0004_026_traslado_1767', 'validation': 'contrato_livro13_1763'}
seen = set()
evidence = []
for split, records in [('train', train), ('validation', validation)]:
    directory = out / split
    directory.mkdir()
    paths = []
    for row, manifest, source in records:
        assert row['document_id'] == expected_documents[split] and row.get('split') is None
        assert not row.get('text_diplomatic') and not row.get('text_modernized')
        destination = directory / f"{row['line_id']}.png"
        with Image.open(source) as image:
            gray = image.convert('L')
            gray.info.clear()
            gray.save(destination)
        digest = sha256(destination)
        if digest in seen:
            raise ValueError(f'Imagem duplicada: {source}')
        seen.add(digest)
        # Kraken 7.1 path compiler needs an existing sidecar even for an empty line.
        destination.with_suffix('.gt.txt').touch(exist_ok=False)
        paths.append('/input/' + destination.relative_to(out).as_posix())
        evidence.append({
            'role': split, 'line_id': row['line_id'], 'document_id': row['document_id'],
            'manifest': manifest.as_posix(), 'source': source.as_posix(),
            'source_sha256': sha256(source), 'input_sha256': digest,
        })
    (out / f'{split}.lst').write_text('\n'.join(paths) + '\n', encoding='utf-8', newline='\n')
write_json(out / 'inventory.json', {
    'mode': 'technical_pretraining', 'test_used': False, 'transcribed_labels': 0,
    'source_manifests': {p.as_posix(): sha256(p) for p in [*manifests, pilot]},
    'records': evidence,
})
print(f'{len(train)} imagens para treino e {len(validation)} para validação técnica.')
