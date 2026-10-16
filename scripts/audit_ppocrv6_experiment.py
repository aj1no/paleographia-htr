"""Audit the PP-OCRv6 development run offline; does not load any recognizer."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from paleographia.evaluation import evaluate
from paleographia.frozen_experiment import check_control, restore_support, verify_files
from paleographia.io import read_jsonl, safe_path, sha256


def audit(root, bundle, output):
    root, bundle, output = Path(root), Path(bundle), Path(output)
    inventory=verify_files(root,bundle)
    frozen=json.loads((bundle/'frozen_inputs_v2.json').read_bytes())
    for row in frozen['files']:
        if sha256(safe_path(root,row['path'])) != row['sha256']:
            raise ValueError('Entrada congelada divergente: '+row['path'])
    lines=read_jsonl(safe_path(root,frozen['reference']))
    pages=read_jsonl(safe_path(root,frozen['pages']))
    predictions=read_jsonl(bundle/'predictions.jsonl')
    check_control(lines,predictions)
    if len(lines)!=5 or frozen['dataset_role']!='development':
        raise ValueError('Escopo de desenvolvimento divergente.')
    for ref,crop,prediction in zip(lines,frozen['crops'],predictions):
        if ref['line_id']!=crop['line_id'] or sha256(safe_path(root,crop['crop_image']))!=crop['sha256']:
            raise ValueError('Recorte congelado divergente.')
        with Image.open(safe_path(root,ref['source_image'])) as source, Image.open(safe_path(root,ref['crop_image'])) as image:
            pixels=image.convert('RGB').tobytes()
            if source.convert('RGB').crop(ref['bbox_xyxy']).tobytes()!=pixels:
                raise ValueError('Pixels do recorte diferem da fonte.')
            if hashlib.sha256(pixels).hexdigest()!=crop['pixel_sha256']:
                raise ValueError('Pixels diferem do recibo anterior à inferência.')
        if prediction['status']=='ok' and prediction['preprocessing']['pixel_sha256']!=crop['pixel_sha256']:
            raise ValueError('Worker recebeu pixels diferentes.')
    result=evaluate(lines,predictions,output,root,pages)
    if result != json.loads((bundle/'evaluation/metrics.json').read_bytes()):
        raise ValueError('Métricas recalculadas divergentes.')
    for filename in ['regions.jsonl','lines.jsonl']:
        if read_jsonl(output/filename)!=read_jsonl(bundle/'evaluation'/filename):
            raise ValueError('Detalhes da avaliação divergentes.')
    integration=json.loads((bundle/'app_smoke.json').read_bytes())
    app_predictions=read_jsonl(bundle/'app_predictions.jsonl')
    check_control(lines,app_predictions)
    if ([p['text_raw'] for p in app_predictions] != [p['text_raw'] for p in predictions]
            or not integration['human_lines_unchanged'] or not integration['pages_unchanged']):
        raise ValueError('Integração diverge do controle.')
    return {'verified_files':len(inventory['files']),'dataset_role':'development','metrics':result['metrics']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',default='docs/experimentos/traslado_269r_ppocrv6_20261016')
    parser.add_argument('--output',required=True)
    parser.add_argument('--restore-support',action='store_true')
    args=parser.parse_args()
    if args.restore_support:
        restore_support(Path.cwd(),'docs/experimentos/traslado_269r_20261016')
    print(json.dumps(audit(Path.cwd(),args.bundle,args.output),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
