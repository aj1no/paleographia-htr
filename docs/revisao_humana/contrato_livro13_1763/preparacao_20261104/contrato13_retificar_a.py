from pathlib import Path
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from paleographia.io import sha256, write_json


prep = Path('docs/revisao_humana/contrato_livro13_1763/preparacao_20261104')
pilot = json.loads((prep / 'piloto_pagina_05.json').read_bytes())
row = next(row for row in pilot['rows'] if row['pilot_label'] == 'A')
source = Path(row['source_image'])
assert sha256(source) == row['source_sha256']
assert sha256(row['crop_image']) == row['crop_sha256']
with Image.open(source) as image:
    original = np.asarray(image.convert('RGB'))

# Guideline picked on the image. Coordinates refer to the complete reproduction.
anchors = [(200, 899), (300, 884), (400, 867), (500, 852), (625, 842), (750, 835),
           (900, 832), (1100, 828), (1300, 828), (1450, 825), (1610, 831),
           (1800, 830), (1969, 830)]
left, right, above, below = 200, 1970, 52, 47
x = np.arange(left, right, dtype=np.float32)
line_y = np.interp(x, [p[0] for p in anchors], [p[1] for p in anchors]).astype(np.float32)
map_x = np.broadcast_to(x, (above + below, len(x))).copy()
map_y = line_y[None, :] + np.arange(-above, below, dtype=np.float32)[:, None]
assert 0 <= map_y.min() and map_y.max() < original.shape[0]
rectified = cv2.remap(original, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
gray = cv2.cvtColor(rectified, cv2.COLOR_RGB2GRAY)


def levels(image, low=0.5, high=99.5):
    lo, hi = np.percentile(image, [low, high])
    normalized = np.clip((image.astype(np.float64) - lo) / (hi - lo), 0, 1)
    return np.rint(10 + 235 * normalized).astype(np.uint8), [float(lo), float(hi)]


adjusted, limits = levels(gray)
clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(12, 2)).apply(gray)
smooth = cv2.GaussianBlur(gray, (0, 0), sigmaX=1.15, sigmaY=1.15)
background = cv2.GaussianBlur(smooth, (0, 0), sigmaX=16, sigmaY=12)
balanced = cv2.addWeighted(smooth, 1, background, -1, 185)
balanced_levels, balanced_limits = levels(balanced)
binary = cv2.adaptiveThreshold(balanced_levels, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 29, 13)

out = Path('output/curadoria_contrato_livro13_1763/piloto_pagina_05/diagnostico_linha_a_retificada_01')
out.mkdir(exist_ok=False)
entries = [
    ('retificada_rgb', 'Linha alinhada · cor', rectified, {}),
    ('retificada_niveis', 'Linha alinhada · níveis em cinza', adjusted, {'levels': limits, 'percentiles': [0.5, 99.5]}),
    ('retificada_clahe', 'Linha alinhada · CLAHE', clahe, {'clip_limit': 1.8, 'tile_grid': [12, 2]}),
    ('retificada_fundo', 'Linha alinhada · fundo compensado', balanced_levels,
     {'smooth_sigma': 1.15, 'background_sigma_xy': [16, 12], 'background_offset': 185, 'levels': balanced_limits, 'percentiles': [0.5, 99.5]}),
    ('retificada_binaria', 'Linha alinhada · limiar adaptativo', binary, {'source_variant': 'retificada_fundo', 'block': 29, 'c': 13}),
]
variants = []
for key, _, array, parameters in entries:
    path = out / f'{key}.png'
    Image.fromarray(array).save(path)
    with Image.open(path) as saved:
        assert np.array_equal(np.asarray(saved), array)
    variants.append({'name': key, 'path': path.as_posix(), 'sha256': sha256(path),
                     'size': [right - left, above + below], 'parameters': parameters})

font_path = 'C:/Windows/Fonts/segoeui.ttf'
panel = Image.new('RGB', (1810, 70 + 189 + len(entries) * 131), '#f5f2eb')
draw = ImageDraw.Draw(panel)
draw.text((20, 10), 'Livro 13 · página 5 · linha A', font=ImageFont.truetype(font_path, 28), fill='#171813')
draw.text((20, 46), 'Comparação de alinhamento e tratamento da imagem', font=ImageFont.truetype(font_path, 18), fill='#45443c')
font = ImageFont.truetype(font_path, 21)
draw.text((20, 71), 'Recorte original', font=font, fill='#183d35')
with Image.open(row['crop_image']) as image:
    panel.paste(image.convert('RGB'), (20, 100))
for i, ((_, label, _, _), view) in enumerate(zip(entries, variants, strict=True)):
    top = 263 + 131 * i
    draw.text((20, top), label, font=font, fill='#183d35')
    with Image.open(view['path']) as image:
        panel.paste(image.convert('RGB'), (20, top + 28))
panel_path = out / 'comparacao_retificacao.png'
panel.save(panel_path)
write_json(out / 'tratamentos.json', {
    'document_id': row['document_id'], 'line_id': row['line_id'], 'page_id': row['page_id'],
    'source_image': source.as_posix(), 'source_sha256': row['source_sha256'],
    'original_crop_image': row['crop_image'], 'original_crop_sha256': row['crop_sha256'],
    'original_bbox_xyxy': row['bbox_xyxy'], 'baseline_guideline_xy': anchors,
    'horizontal_range': [left, right], 'vertical_margin': {'above': above, 'below': below},
    'remap_method': 'Interpolação linear entre pontos da linha de guia; cv2.remap com interpolação bilinear.',
    'variants': variants, 'comparison': {'path': panel_path.as_posix(), 'sha256': sha256(panel_path)},
    'use': 'Derivados para diagnóstico, com geometria retificada. A caixa original identifica a fonte e não descreve os pixels retificados.',
})
assert sha256(source) == row['source_sha256'] and sha256(row['crop_image']) == row['crop_sha256']
print(panel_path)
