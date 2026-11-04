import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from paleographia.backends import create_recognizer
from paleographia.config import load_config
from paleographia.io import sha256, write_json, write_jsonl
from paleographia.recognition import recognize_lines


root = Path.cwd()
previous = Path('output/curadoria_contrato_livro13_1763/piloto_pagina_05/diagnostico_linha_a_retificada_01')
record = json.loads((previous / 'tratamentos.json').read_bytes())
assert sha256(record['source_image']) == record['source_sha256']
left, right = record['horizontal_range']
above, below = (record['vertical_margin'][key] for key in ('above', 'below'))
x = np.arange(left, right, dtype=np.float32)
anchors = record['baseline_guideline_xy']
line_y = np.interp(x, [a[0] for a in anchors], [a[1] for a in anchors]).astype(np.float32)
top, bottom = int(line_y.min()) - above - 20, int(line_y.max()) + below + 20
with Image.open(record['source_image']) as image:
    gray = cv2.cvtColor(np.asarray(image.crop((left, top, right, bottom)).convert('RGB')), cv2.COLOR_RGB2GRAY)

# Suppress the symmetric peaks seen in the reproduction's repeating texture.
centers = [(10.5, 9.5), (20.5, 19.0), (38.5, 38.5), (38.5, -38.0)]
pad = 32
padded = np.pad(gray.astype(np.float64), pad, mode='reflect')
fx = np.fft.fftfreq(padded.shape[1])[None, :]
fy = np.fft.fftfreq(padded.shape[0])[:, None]
response = np.ones(padded.shape)
sigma = 1.8 / 128
for cx, cy in centers:
    for sign in (-1, 1):
        radius = ((fx - sign * cx / 128) / sigma) ** 2 + ((fy - sign * cy / 128) / sigma) ** 2
        response *= 1 - 0.88 * np.exp(-radius / 2)
filtered = np.fft.ifft2(np.fft.fft2(padded) * response).real[pad:-pad, pad:-pad].astype(np.float32)
map_x = np.broadcast_to(x - left, (above + below, len(x))).copy()
map_y = line_y[None, :] - top + np.arange(-above, below, dtype=np.float32)[:, None]
rectified = cv2.remap(filtered, map_x, map_y, cv2.INTER_LINEAR)
lo, hi = np.percentile(rectified, [0.5, 99.5])
image = np.rint(10 + 235 * np.clip((rectified - lo) / (hi - lo), 0, 1)).astype(np.uint8)

out = previous / 'complemento_textura'
out.mkdir(exist_ok=False)
inputs = []
for index, (name, start, end) in enumerate((('antitrama_inteira', 0, len(x)), ('antitrama_esquerda', 0, 1000), ('antitrama_direita', 770, len(x)))):
    path = out / f'{name}.png'
    Image.fromarray(image[:, start:end]).save(path)
    inputs.append({'line_id': record['line_id'] + '_' + name, 'page_id': record['page_id'],
                   'region_id': 'contrato13_p05_a_diagnostico_textura', 'reading_order': index,
                   'bbox_xyxy': record['original_bbox_xyxy'], 'crop_image': path.as_posix(),
                   'source_sha256': record['source_sha256'], 'input_sha256': sha256(path),
                   'diagnostic_variant': name, 'x_range_in_rectified_line': [start, end]})
write_json(out / 'tratamento.json', {'source': record['source_image'], 'source_sha256': record['source_sha256'],
                                  'filter': 'Supressão localizada de picos periódicos na transformada de Fourier, antes de alinhar a linha.',
                                  'peak_xy_cycles_per_128_pixels': centers, 'sigma_cycles_per_pixel': sigma, 'depth': 0.88,
                                  'levels_percentiles': [0.5, 99.5], 'input_levels': [float(lo), float(hi)],
                                  'geometry_record': (previous / 'tratamentos.json').as_posix(), 'inputs': inputs})
write_jsonl(out / 'entradas.jsonl', inputs)
recognizer = create_recognizer(load_config('configs/traslado_269r.toml'), root)
try:
    results = recognize_lines(inputs, recognizer, out / 'predictions.jsonl', root)
finally:
    recognizer.close()
for entry, result in zip(inputs, results, strict=True):
    assert result['line_id'] == entry['line_id']
    print(entry['diagnostic_variant'], result['status'], repr(result['text_raw']))
