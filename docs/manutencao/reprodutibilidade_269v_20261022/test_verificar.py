"""Casos da auditoria v2 em checkout isolado, sem data/raw, pesos ou inferência."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = 'docs/manutencao/reprodutibilidade_269v_20261022/verificar.py'
BUNDLE = 'docs/experimentos/traslado_269v_integral_edicao_20261022'
PDF_SHA = 'e1c779a4713340adbf5e6102b0c3edc716c12612d18597e9d22228676ab9b3e0'
METRICS = json.loads((ROOT/BUNDLE/'comparacao.json').read_bytes())['metrics']


@pytest.fixture(scope='module')
def isolated(tmp_path_factory):
    folder = tmp_path_factory.mktemp('clone_sem_pdf_269v')
    data = subprocess.check_output(['git', 'archive', '--format=tar', 'HEAD'], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(folder, filter='data')
    (folder/SCRIPT).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/SCRIPT, folder/SCRIPT)
    assert not list((folder/'data/raw').rglob('*.pdf'))
    assert not list((folder/'models').rglob('*.safetensors'))
    assert not list((folder/'models').rglob('*.mlmodel'))
    return folder


@pytest.fixture(scope='module')
def pdf_externo(isolated, tmp_path_factory):
    from paleographia.preparation import ensure_archive_reference
    members = json.loads((isolated/'data/manifests/archive_members.json').read_bytes())
    entry = next(item for item in members if item['sha256'] == PDF_SHA)
    destination = 'output/fontes/traslado_269_273.pdf'
    ensure_archive_reference(isolated, entry, destination)
    external = tmp_path_factory.mktemp('fonte_externa_269v')/'facsimile.pdf'
    shutil.copyfile(isolated/destination, external)
    assert hashlib.sha256(external.read_bytes()).hexdigest() == PDF_SHA
    return external


def run(folder, *arguments):
    env = dict(os.environ, PYTHONPATH=str(folder/'src'), PYTHONDONTWRITEBYTECODE='1',
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    result = subprocess.run([sys.executable, str(folder/SCRIPT), *arguments], cwd=folder,
                            env=env, capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert 'Traceback' not in result.stderr, result.stderr
    return result, json.loads(result.stdout if result.returncode == 0 else result.stderr)


def test_fonte_ausente_informa_requisito_e_comando(isolated):
    process, result = run(isolated)
    assert process.returncode == 2
    assert result['resultado'] == 'reprovado' and not result['auditoria_completa']
    assert 'PDF original ausente' in result['erro']
    assert PDF_SHA in result['erro'] and '--facsimile' in result['erro'] and '--modo artefatos' in result['erro']


def test_fonte_incorreta_rejeita_edicao_textual(isolated):
    edition = isolated/'docs/experimentos/traslado_269r_20261016/support/edition.pdf'
    process, result = run(isolated, '--facsimile', str(edition))
    assert process.returncode == 2
    assert 'PDF original incorreto' in result['erro']
    assert hashlib.sha256(edition.read_bytes()).hexdigest() in result['erro']
    assert PDF_SHA in result['erro'] and not result['auditoria_completa']


def test_fonte_correta_externa_aprova_auditoria_completa(isolated, pdf_externo):
    source = pdf_externo
    assert hashlib.sha256(source.read_bytes()).hexdigest() == PDF_SHA
    assert not source.is_relative_to(isolated)
    process, result = run(isolated, '--facsimile', str(source))
    assert process.returncode == 0
    assert result['resultado'] == 'aprovado' and result['auditoria_completa']
    assert result['comparacao_bytes_imagem_embutida_executada'] and result['hash_pdf_original_verificado']
    assert result['checagens_nao_executadas'] == []
    assert result['metrics'] == METRICS and result['novas_inferencias'] == 0


def test_recuperacao_do_rar_versionado_confere_pdf_exato(isolated, pdf_externo):
    archive = isolated/'data/raw/Transcri\u00e7\u00f5es.rar'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == '6e82cef18b04d2aaf7a2cc1c1f88bf82d47347b8b123cae92394b153806f7a0d'
    assert hashlib.sha256(pdf_externo.read_bytes()).hexdigest() == PDF_SHA
    assert (isolated/'output/fontes/traslado_269_273.pdf').read_bytes() == pdf_externo.read_bytes()


def test_sem_pdf_modo_artefatos_declara_aprovacao_apenas_parcial(isolated):
    process, result = run(isolated, '--modo', 'artefatos')
    assert process.returncode == 0
    assert result['resultado'] == 'conferencia_parcial_aprovada'
    assert not result['auditoria_completa'] and not result['comparacao_bytes_imagem_embutida_executada']
    assert not result['hash_pdf_original_verificado'] and result['facsimile_fornecido'] is None
    assert len(result['checagens_nao_executadas']) == 2
    assert result['metrics'] == METRICS and result['arquivos_conferidos'] == 69


def test_modo_parcial_rejeita_artefato_publicado_adulterado(isolated):
    raw = isolated/BUNDLE/'transcricao_bruta.txt'
    original = raw.read_bytes()
    try:
        raw.write_bytes(original+b'adulterado\n')
        process, result = run(isolated, '--modo', 'artefatos')
        assert process.returncode == 2
        assert 'Hash divergente: transcricao_bruta.txt' in result['erro']
    finally:
        raw.write_bytes(original)
