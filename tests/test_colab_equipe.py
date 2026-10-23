"""Preparação e download no Colab sem atribuir contribuição pela execução."""
from pathlib import Path
from zipfile import ZipFile
import json
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/entregas/pi_iv_pln_20261023_colab'
BOOT = runpy.run_path(str(BASE / 'preparar_colab.py'))
EXPORT = runpy.run_path(str(BASE / 'exportar_contribuicoes.py'))
PART = runpy.run_path(str(ROOT / 'docs/entregas/pi_iv_pln_20261023_equipe/participacao.py'))


def test_exportacao_sem_registros_nao_cria_zip(tmp_path):
    assert EXPORT['criar_pacote_contribuicoes'](tmp_path, 'caio') is None
    assert not (tmp_path / 'output').exists()


def test_zip_preserva_bytes_e_separa_participantes(tmp_path):
    # Registros sintéticos só no diretório temporário do teste.
    pasta = tmp_path / 'output/participacao_equipe_20261023'
    pasta.mkdir(parents=True)
    original = b'{"participante_id":"caio","estado":"autodeclarado_pendente_conferencia"}\n'
    (pasta / 'caio_teste.json').write_bytes(original)
    (pasta / 'tiago_teste.json').write_text('{"participante_id":"tiago"}', encoding='utf-8')
    first = EXPORT['criar_pacote_contribuicoes'](tmp_path, 'caio')
    second = EXPORT['criar_pacote_contribuicoes'](tmp_path, 'caio')
    assert first != second
    with ZipFile(first) as pacote:
        assert set(pacote.namelist()) == {'caio_teste.json', 'LEIA-ME.txt'}
        assert pacote.read('caio_teste.json') == original
    assert (pasta / 'caio_teste.json').read_bytes() == original


def test_zip_rejeita_participante_divergente(tmp_path):
    pasta = tmp_path / 'output/participacao_equipe_20261023'
    pasta.mkdir(parents=True)
    (pasta / 'caio_teste.json').write_text('{"participante_id":"tiago"}', encoding='utf-8')
    with pytest.raises(ValueError):
        EXPORT['criar_pacote_contribuicoes'](tmp_path, 'caio')
    with pytest.raises(ValueError):
        EXPORT['criar_pacote_contribuicoes'](tmp_path, '../outro')
    assert not list(tmp_path.rglob('*.zip'))


def test_checkout_existente_diferente_nao_e_sobrescrito(tmp_path, monkeypatch):
    (tmp_path / '.git').mkdir()
    arquivo = tmp_path / 'trabalho.txt'
    arquivo.write_text('Preservar', encoding='utf-8')
    chamadas = []

    def git(args, cwd):
        chamadas.append(args)
        return BOOT['REPOSITORIO_COLAB'] if args[0] == 'remote' else 'revisao_diferente'

    monkeypatch.setitem(BOOT['preparar_checkout'].__globals__, 'executar_git', git)
    with pytest.raises(RuntimeError, match='nenhuma alteração'):
        BOOT['preparar_checkout'](tmp_path)
    assert chamadas == [['remote', 'get-url', 'origin'], ['rev-parse', 'HEAD']]
    assert arquivo.read_text(encoding='utf-8') == 'Preservar'


def test_notebook_prepara_antes_das_dependencias_e_inicia_vazio(tmp_path):
    nb = json.loads((BASE / 'colaboracao_colab.ipynb').read_bytes())
    codigo = [c for c in nb['cells'] if c['cell_type'] == 'code']
    assert codigo[0]['id'] == 'colab-preparacao'
    assert 'preparar_ambiente_colab()' in ''.join(codigo[0]['source'])
    assert all(not c['outputs'] and c['execution_count'] is None for c in codigo)
    for pid in ['caio', 'guilherme', 'tiago', 'rodolfo']:
        cell = next(c for c in codigo if c['id'] == 'equipe-' + pid + '-formulario')
        source = ''.join(cell['source'])
        # O parser de formulários do Colab exige JSON válido, inclusive quando
        # a dica contém dois-pontos ("relato: descrição").
        configuracoes = [line.split('# @param ', 1)[1] for line in source.splitlines() if '# @param {' in line]
        assert len(configuracoes) == 5
        assert all(json.loads(config)['type'] == 'string' for config in configuracoes)
        # Avalia somente o formulário, sem o material automático de consulta.
        form = source[source.index('preenchido_por_' + pid + ' ='):]
        env = {'RAIZ': tmp_path, 'registrar_participacao': PART['registrar']}
        exec(form, env)
        assert env['resultado_' + pid]['estado'] == 'pendente'
        assert not env['resultado_' + pid]['salvo']
    assert not (tmp_path / 'output').exists()
    assert 'baixar_contribuicoes = False' in ''.join(codigo[-1]['source'])


def test_calculos_originais_preservados():
    original = json.loads((ROOT / 'docs/entregas/pi_iv_pln_20261022/comparacao_reproduzivel.ipynb').read_bytes())
    colab = json.loads((BASE / 'colaboracao_colab.ipynb').read_bytes())
    cells = {c['id']: c for c in colab['cells']}
    for cell in original['cells']:
        if cell['cell_type'] != 'code':
            continue
        esperado = ''.join(cell['source']).replace('output/entrega_academica_269r24_20261022',
                                                  'output/equipe_colab_20261023/calculos')
        assert ''.join(cells[cell['id']]['source']) == esperado
