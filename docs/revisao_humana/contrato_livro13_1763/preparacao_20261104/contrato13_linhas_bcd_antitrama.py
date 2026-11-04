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
pilot_path = Path('docs/revisao_humana/contrato_livro13_1763/preparacao_20261104/piloto_pagina_05.json')
pilot = json.loads(pilot_path.read_bytes())
base = Path('output/curadoria_contrato_livro13_1763/piloto_pagina_05')
geometry_path = base / 'diagnostico_linha_a_retificada_01/tratamentos.json'
texture_path = geometry_path.parent / 'complemento_textura/tratamento.json'
geometry = json.loads(geometry_path.read_bytes())
texture = json.loads(texture_path.read_bytes())
source_path = Path(geometry['source_image'])
assert sha256(source_path) == geometry['source_sha256'] == texture['source_sha256']
out = base / 'diagnostico_linhas_bcd_01'
out.mkdir(exist_ok=False)


def remove_periodic_texture(gray):
    pad = 32
    padded = np.pad(gray.astype(np.float64), pad, mode='reflect')
    fx = np.fft.fftfreq(padded.shape[1])[None, :]
    fy = np.fft.fftfreq(padded.shape[0])[:, None]
    response = np.ones(padded.shape)
    sigma = texture['sigma_cycles_per_pixel']
    for cx, cy in texture['peak_xy_cycles_per_128_pixels']:
        for sign in (-1, 1):
            radius = ((fx - sign * cx / 128) / sigma) ** 2 + ((fy - sign * cy / 128) / sigma) ** 2
            response *= 1 - texture['depth'] * np.exp(-radius / 2)
    return np.fft.ifft2(np.fft.fft2(padded) * response).real[pad:-pad, pad:-pad].astype(np.float32)


left, right = geometry['horizontal_range']
above, below = (geometry['vertical_margin'][key] for key in ('above', 'below'))
x = np.arange(left, right, dtype=np.float32)
guide = np.array(geometry['baseline_guideline_xy'])
line_a_y = pilot['rows'][0]['pilot_guide_y_in_original']
params, entries, panel_images = [], [], []
with Image.open(source_path) as source:
    for row in pilot['rows'][1:]:
        label = row['pilot_label']
        assert sha256(row['crop_image']) == row['crop_sha256']
        offset = row['pilot_guide_y_in_original'] - line_a_y
        line_y = np.interp(x, guide[:, 0], guide[:, 1] + offset).astype(np.float32)
        top, bottom = int(line_y.min()) - above - 20, int(line_y.max()) + below + 20
        gray = cv2.cvtColor(np.asarray(source.crop((left, top, right, bottom)).convert('RGB')), cv2.COLOR_RGB2GRAY)
        filtered = remove_periodic_texture(gray)
        map_x = np.broadcast_to(x - left, (above + below, len(x))).copy()
        map_y = line_y[None, :] - top + np.arange(-above, below, dtype=np.float32)[:, None]
        strip = cv2.remap(filtered, map_x, map_y, cv2.INTER_LINEAR)
        lo, hi = np.percentile(strip, texture['levels_percentiles'])
        strip = np.rint(10 + 235 * np.clip((strip - lo) / (hi - lo), 0, 1)).astype(np.uint8)
        params.append({'line': label, 'guide_offset_y': offset, 'guide_xy': (guide + [0, offset]).tolist(),
                       'working_crop_xyxy': [left, top, right, bottom], 'input_levels': [float(lo), float(hi)]})
        panel_images.append((label, Image.fromarray(strip)))
        variants = [('original', Path(row['crop_image']), None)]
        for reference in texture['inputs']:
            name = reference['diagnostic_variant']
            start, end = reference['x_range_in_rectified_line']
            path = out / f'{label}_{name}.png'
            Image.fromarray(strip[:, start:end]).save(path)
            variants.append((name, path, [start, end]))
        for name, path, span in variants:
            entries.append({'line_id': row['line_id'] + '_' + name, 'original_line_id': row['line_id'],
                            'pilot_label': label, 'page_id': row['page_id'],
                            'region_id': 'contrato13_p05_bcd_diagnostico_textura',
                            'reading_order': len(entries), 'bbox_xyxy': row['bbox_xyxy'],
                            'crop_image': path.as_posix(), 'source_sha256': row['source_sha256'],
                            'input_sha256': sha256(path), 'diagnostic_variant': name,
                            'x_range_in_rectified_line': span})

panel = Image.new('L', (len(x), 125 * len(panel_images)), 255)
draw = ImageDraw.Draw(panel)
for index, (label, strip) in enumerate(panel_images):
    draw.text((8, 125 * index + 4), label, fill=0)
    panel.paste(strip, (0, 125 * index + 21))
panel.save(out / 'linhas_bcd_tratadas.png')
write_json(out / 'tratamento.json', {
    'source': source_path.as_posix(), 'source_sha256': geometry['source_sha256'],
    'pilot': pilot_path.as_posix(), 'pilot_sha256': sha256(pilot_path),
    'line_a_geometry': geometry_path.as_posix(), 'line_a_geometry_sha256': sha256(geometry_path),
    'line_a_texture': texture_path.as_posix(), 'line_a_texture_sha256': sha256(texture_path),
    'geometry_selection': 'Guideline from A translated by the existing pilot y offsets and checked visually on the page before inference.',
    'working_margin_y': 20, 'fft_reflect_padding': 32, 'output_levels': [10, 245],
    'line_parameters': params,
})
write_jsonl(out / 'entradas.jsonl', entries)
recognizer = create_recognizer(load_config('configs/traslado_269r.toml'), root)
try:
    results = recognize_lines(entries, recognizer, out / 'predictions.jsonl', root)
finally:
    recognizer.close()
for entry, result in zip(entries, results, strict=True):
    assert result['line_id'] == entry['line_id']
    print(entry['pilot_label'], entry['diagnostic_variant'], result['status'], repr(result['text_raw']))
