"""Audit actual saved outputs offline; never run a fake recognizer as HTR evidence."""
import json
import shutil
from pathlib import Path

import pytest

from paleographia.frozen_experiment import restore_support
from paleographia.io import read_jsonl, sha256, write_jsonl
from scripts.audit_ppocrv6_experiment import audit

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=Path('docs/experimentos/traslado_269r_ppocrv6_20261016')
OLD=Path('docs/experimentos/traslado_269r_20261016')


@pytest.fixture
def frozen_checkout(tmp_path):
    paths=set()
    for bundle in (BUNDLE,OLD):
        inventory=json.loads((ROOT/bundle/'inventory.json').read_bytes())
        paths.update(row['path'] for row in inventory['files'])
        paths.add((bundle/'inventory.json').as_posix())
    for path in paths:
        target=tmp_path/path
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/path,target)
    restore_support(tmp_path,tmp_path/OLD)
    return tmp_path,tmp_path/BUNDLE


def test_actual_ppocrv6_saved_outputs_reproduce_without_docker(frozen_checkout):
    root,bundle=frozen_checkout
    result=audit(root,bundle,root/'audit')
    assert result['dataset_role']=='development'
    assert result['metrics']['characters']['errors']==30
    assert result['metrics']['characters']['reference_length']==242
    assert result['metrics']['words']['errors']==23
    assert result['metrics']['words']['reference_length']==45


def test_changed_transport_pixels_are_rejected_even_with_updated_file_hash(frozen_checkout):
    root,bundle=frozen_checkout
    path=bundle/'predictions.jsonl'
    rows=read_jsonl(path)
    rows[0]['preprocessing']['pixel_sha256']='0'*64
    write_jsonl(path,rows)
    inventory=json.loads((bundle/'inventory.json').read_bytes())
    for row in inventory['files']:
        if row['path']==path.relative_to(root).as_posix():
            row['sha256']=sha256(path)
    (bundle/'inventory.json').write_text(json.dumps(inventory),encoding='utf8')
    with pytest.raises(ValueError,match='Worker recebeu pixels diferentes'):
        audit(root,bundle,root/'audit')
