"""Proteções e comparação do recálculo; fixtures copiadas não são nova inferência."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('ci_academica', ROOT/'scripts/ci_academica.py')
CI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CI)


@pytest.fixture
def generated(tmp_path):
    output = tmp_path/'derivados'
    shutil.copytree(ROOT/CI.DELIVERY, output)
    receipt = CI.read(output/'resultado_notebook.json')
    receipt.update(workspace_conferido=False, workspace_arquivos_inalterados=None)
    (output/'resultado_notebook.json').write_text(json.dumps(receipt), encoding='utf-8')
    return output


def test_generated_accepts_identical_metrics_tables_and_eight_doubts(generated):
    result = CI.verify_generated(ROOT, generated)
    assert result['linhas'] == 24 and result['ressalvas'] == [11, 15, 16, 17, 19, 20, 23, 24]
    assert result['tabelas_identicas'] == 5 and result['novas_inferencias'] == 0


@pytest.mark.parametrize('change', ['metricas', 'ressalvas', 'inferencias', 'fonte', 'execucao', 'csv'])
def test_generated_rejects_changed_results_or_partial_execution(generated, change):
    if change in {'metricas', 'ressalvas', 'inferencias'}:
        path = generated/'resultado_notebook.json'
        value = CI.read(path)
        if change == 'metricas':
            value['metricas']['ppocrv6']['characters']['errors'] += 1
        elif change == 'ressalvas':
            value['ressalvas'] = 7
        else:
            value['novas_inferencias'] = 1
        path.write_text(json.dumps(value), encoding='utf-8')
    elif change in {'fonte', 'execucao'}:
        path = generated/'comparacao_reproduzivel.ipynb'
        value = CI.read(path)
        cell = next(c for c in value['cells'] if c['cell_type'] == 'code')
        if change == 'fonte':
            cell['source'] = ['print("alteração de teste")']
        else:
            cell['execution_count'] = None
        path.write_text(json.dumps(value), encoding='utf-8')
    else:
        path = generated/'tabelas/ressalvas.csv'
        rows = path.read_text(encoding='utf-8-sig').splitlines(keepends=True)
        path.write_text(''.join(rows[:-1]), encoding='utf-8-sig')
    with pytest.raises(ValueError):
        CI.verify_generated(ROOT, generated)


@pytest.mark.parametrize('directory', ['models', 'data/workspace', 'data/workspace_traslado_269r', str(CI.OUTPUT)])
def test_preflight_refuses_weights_workspaces_and_existing_outputs(tmp_path, directory):
    folder = tmp_path/directory
    folder.mkdir(parents=True)
    sentinel = folder/'preservado.txt'
    sentinel.write_bytes(b'nao sobrescrever')
    with pytest.raises(ValueError):
        CI.check_environment(tmp_path)
    assert sentinel.read_bytes() == b'nao sobrescrever'


def guarded(tmp_path, code):
    project, custom = tmp_path/'repo', tmp_path/'custom'
    project.mkdir()
    custom.mkdir()
    (project/'output').mkdir()
    (project/'src').mkdir()
    (project/'src/entrada.txt').write_bytes(b'original')
    shutil.copyfile(ROOT/'scripts/ci_academica_guard.py', custom/'sitecustomize.py')
    log = project/'output/protecao.jsonl'
    env = dict(os.environ, PYTHONPATH=str(custom), PYTHONDONTWRITEBYTECODE='1',
               PYTHONIOENCODING='utf-8', PALEOGRAPHIA_CI_ROOT=str(project), PALEOGRAPHIA_CI_LOG=str(log))
    process = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=project, env=env,
                             capture_output=True, text=True, encoding='utf-8', timeout=15)
    events = [json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
    assert any(e['evento'] == 'protecao_ativa' for e in events)
    assert (project/'src/entrada.txt').read_bytes() == b'original'
    return process, events


@pytest.mark.parametrize('code,reason', [
    ('import torch', 'importacao_de_inferencia'),
    ('import onnxruntime', 'importacao_de_inferencia'),
    ('import paleographia.recognition', 'importacao_de_inferencia'),
    ('import subprocess; subprocess.run(["docker", "--version"])', 'subprocesso_nao_autorizado'),
    ('import subprocess; subprocess.run(["uname", "-a"])', 'subprocesso_nao_autorizado'),
    ('import socket; socket.create_connection(("example.invalid", 443))', 'conexao_externa'),
    ('open("models/peso.safetensors", "rb")', 'acesso_a_pesos'),
    ('open("src/entrada.txt", "w").write("alterado")', 'escrita_em_entrada'),
])
def test_guard_blocks_inference_network_commands_and_input_changes(tmp_path, code, reason):
    process, events = guarded(tmp_path, code)
    assert process.returncode != 0
    assert any(e['evento'] == 'bloqueado' and e['motivo'] == reason for e in events)


def test_guard_allows_loopback_and_derived_outputs_without_unix_sockets(tmp_path):
    code = '''import socket
if hasattr(socket, "AF_UNIX"):
    del socket.AF_UNIX
server = socket.socket()
server.bind(("127.0.0.1", 0))
server.listen(1)
client = socket.create_connection(server.getsockname(), timeout=2)
accepted, _ = server.accept()
accepted.close()
client.close()
server.close()
open("output/derivado.txt", "w").write("permitido")
'''
    process, events = guarded(tmp_path, code)
    assert process.returncode == 0, process.stderr
    assert not any(e['evento'] == 'bloqueado' for e in events)


def test_guard_accepts_processor_metadata_probe_without_launching_it(tmp_path):
    code = 'import sys; sys.audit("subprocess.Popen", "uname", ["uname", "-p"], None, None)'
    process, events = guarded(tmp_path, code)
    assert process.returncode == 0, process.stderr
    assert not any(e['evento'] == 'bloqueado' for e in events)


@pytest.mark.skipif(os.name != 'nt', reason='O evento serializado é específico do Windows.')
def test_guard_accepts_serialized_windows_kernel_event_without_launching_it(tmp_path):
    code = '''import subprocess, sys
command = subprocess.list2cmdline([sys.executable, "-m", "ipykernel_launcher", "-f", "connection.json"])
sys.audit("subprocess.Popen", None, command, None, None)
'''
    process, events = guarded(tmp_path, code)
    assert process.returncode == 0, process.stderr
    assert not any(e['evento'] == 'bloqueado' for e in events)
