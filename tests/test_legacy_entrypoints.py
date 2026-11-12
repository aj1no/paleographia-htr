"""Scripts numerados antigos: o código histórico continua em legacy/ e os comandos indicados existem.

Os dez avisos de compatibilidade que ficavam na raiz (``1_organizar_arquivos.py`` etc.) saíram na
organização da entrega de 12/11/2026 (docs/manutencao/organizacao_entrega_20261112). Eles ainda
estão no histórico do Git; o catálogo de 20/10 e as cópias em legacy/ seguem conferidos aqui.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from paleographia.__main__ import parser

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT/'docs/manutencao/scripts_numerados_20261020/inventario.json'
INVENTORY = json.loads(CATALOG.read_bytes())
ROWS = INVENTORY['scripts']


def test_avisos_sairam_da_raiz():
    assert not list(ROOT.glob('[0-9]_*.py'))


def test_catalogo_preserva_historico_hashes_e_comandos_indicados():
    assert len(ROWS) == 10
    assert INVENTORY['commit_anterior'] == '951363bdb588268dd973de6ead96d7d36c538df6'
    for row in ROWS:
        assert row['saida_esperada'] == 1
        assert hashlib.sha256((ROOT/row['original_historico']).read_bytes()).hexdigest() == row['sha256_original_historico']
        try:
            old = subprocess.check_output(['git', 'show', INVENTORY['commit_anterior']+':'+row['caminho']], cwd=ROOT,
                                          stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip('histórico do Git indisponível (clone raso ou sem git)')
        assert hashlib.sha256(old).hexdigest() == row['sha256_aviso_anterior']
        args = row['orientacao_cli'].split()[3:]
        if args[-1:] == ['--help']:
            with pytest.raises(SystemExit) as stopped:
                parser().parse_args(args)
            assert stopped.value.code == 0
        else:
            assert parser().parse_args(args).command == args[0]
