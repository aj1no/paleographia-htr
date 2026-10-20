"""Entradas antigas continuam bloqueadas e não modificam dados ou iniciam modelos."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from paleographia.__main__ import parser

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT/'docs/manutencao/scripts_numerados_20261020/inventario.json'
INVENTORY = json.loads(CATALOG.read_bytes())
ROWS = INVENTORY['scripts']


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob('*') if p.is_file()}


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['caminho'])
def test_legacy_entrypoint_blocks_execution_and_import_is_inert(row, tmp_path):
    for relative in ['data/raw/original.txt', 'models/preservado.txt']:
        path = tmp_path/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'conteudo que deve permanecer intacto')
    before = snapshot(tmp_path)
    before_paths = {p.relative_to(tmp_path) for p in tmp_path.rglob('*')}
    script = ROOT/row['caminho']
    python = [sys.executable, '-I', '-S', '-X', 'utf8']
    for args in [[], ['--execute', '--output-dir', 'output/NAO_CRIAR']]:
        result = subprocess.run(python+[str(script), *args], cwd=tmp_path,
                                capture_output=True, text=True, encoding='utf-8', timeout=15)
        assert result.returncode == 1
        assert result.stdout == ''
        assert 'script antigo está desativado' in result.stderr
        assert 'Nenhuma operação foi executada.' in result.stderr
        assert row['orientacao_cli'] in result.stderr
        assert row['original_historico'] in result.stderr
        assert snapshot(tmp_path) == before
        assert {p.relative_to(tmp_path) for p in tmp_path.rglob('*')} == before_paths
    code = (f'import runpy,sys; runpy.run_path({str(script)!r}); '
            'assert not any(m == "paleographia" or m.startswith("paleographia.") '
            'or m in {"torch", "transformers"} for m in sys.modules)')
    imported = subprocess.run(python+['-c', code], cwd=tmp_path, capture_output=True, timeout=15)
    assert imported.returncode == 0 and imported.stdout == imported.stderr == b''
    assert snapshot(tmp_path) == before
    assert {p.relative_to(tmp_path) for p in tmp_path.rglob('*')} == before_paths
    if row['caminho'] in {'8_treinar_modelo.py', '9_treino_relampago.py'}:
        assert 'treinamento está indisponível' in result.stderr


def test_legacy_catalog_preserves_paths_history_hashes_and_valid_cli_hints():
    expected = {p.name for p in ROOT.glob('[0-9]*.py')}
    assert len(ROWS) == 10 and {r['caminho'] for r in ROWS} == expected
    assert INVENTORY['commit_anterior'] == '951363bdb588268dd973de6ead96d7d36c538df6'
    for row in ROWS:
        assert row['saida_esperada'] == 1
        assert hashlib.sha256((ROOT/row['caminho']).read_bytes()).hexdigest() == row['sha256_aviso_atual']
        assert hashlib.sha256((ROOT/row['original_historico']).read_bytes()).hexdigest() == row['sha256_original_historico']
        old = subprocess.check_output(['git', 'show', INVENTORY['commit_anterior']+':'+row['caminho']], cwd=ROOT)
        assert hashlib.sha256(old).hexdigest() == row['sha256_aviso_anterior']
        args = row['orientacao_cli'].split()[3:]
        if args[-1:] == ['--help']:
            with pytest.raises(SystemExit) as stopped:
                parser().parse_args(args)
            assert stopped.value.code == 0
        else:
            assert parser().parse_args(args).command == args[0]
