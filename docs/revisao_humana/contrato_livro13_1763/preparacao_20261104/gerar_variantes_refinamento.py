import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from paleographia.backends import create_recognizer
from paleographia.config import load_config
from paleographia.io import sha256, write_json, write_jsonl
from paleographia.recognition import recognize_lines


root = Path.cwd()
base = Path('output/curadoria_contrato_livro13_1763/piloto_pagina_05')
out = base / 'diagnostico_refinamento_01'
pilot_path = Path('docs/revisao_humana/contrato_livro13_1763/preparacao_20261104/piloto_pagina_05.json')
pilot = json.loads(pilot_path.read_bytes())
out.mkdir(exist_ok=False)
entries = []
settings = {
    'faixa_estreita': {'top': 9, 'bottom': 9},
    'tracos_nitidos': {'sigma': 1.05, 'amount': 0.65},
    'fundo_uniforme': {'closing_width': 35, 'closing_height': 25, 'weight': 0.65, 'percentiles': [0.5, 99.5]},
    'clahe_suave': {'clip_limit': 1.4, 'tile_grid': [16, 2]},
    'escrita_alargada': {'width_scale': 1.22},
}
for row in pilot['rows']:
    label = row['pilot_label']
    if label == 'A':
        source = base / 'diagnostico_linha_a_retificada_01/complemento_textura/antitrama_inteira.png'
    else:
        source = base / 'diagnostico_linhas_bcd_01' / f'{label}_antitrama_inteira.png'
    with Image.open(source) as image:
        pixels = np.array(image.convert('L'))
    values = pixels.astype(np.float32)
    background = cv2.morphologyEx(pixels, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 25)))
    uniform = values - 0.65 * background + 0.65 * np.median(background)
    low, high = np.percentile(uniform, [0.5, 99.5])
    uniform = 10 + 235 * np.clip((uniform - low) / (high - low), 0, 1)
    variants = {
        'faixa_estreita': pixels[9:-9, :],
        'tracos_nitidos': cv2.addWeighted(pixels, 1.65, cv2.GaussianBlur(pixels, (0, 0), 1.05), -0.65, 0),
        'fundo_uniforme': np.rint(uniform).astype(np.uint8),
        'clahe_suave': cv2.createCLAHE(clipLimit=1.4, tileGridSize=(16, 2)).apply(pixels),
        'escrita_alargada': cv2.resize(pixels, (round(pixels.shape[1] * 1.22), pixels.shape[0]), interpolation=cv2.INTER_CUBIC),
    }
    for name, pixels in variants.items():
        image_path = out / f'{label}_{name}.png'
        Image.fromarray(pixels).save(image_path)
        entries.append({'line_id': row['line_id'] + '_' + name, 'original_line_id': row['line_id'],
                        'pilot_label': label, 'page_id': row['page_id'], 'region_id': 'contrato13_p05_refinamento',
                        'reading_order': len(entries), 'bbox_xyxy': row['bbox_xyxy'],
                        'crop_image': image_path.as_posix(), 'source_sha256': row['source_sha256'],
                        'input_sha256': sha256(image_path), 'previous_treated_image': source.as_posix(),
                        'previous_treated_sha256': sha256(source), 'diagnostic_variant': name})

write_json(out / 'tratamentos.json', {'settings': settings, 'inputs_frozen_before_inference': True})
write_jsonl(out / 'entradas.jsonl', entries)
recognizer = create_recognizer(load_config('configs/traslado_269r.toml'), root)
try:
    results = recognize_lines(entries, recognizer, out / 'predictions.jsonl', root)
finally:
    recognizer.close()
for entry, result in zip(entries, results, strict=True):
    assert result['line_id'] == entry['line_id']
    print(entry['pilot_label'], entry['diagnostic_variant'], result['status'], repr(result['text_raw']))
