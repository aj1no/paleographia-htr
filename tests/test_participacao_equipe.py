"""Contribuição preenchida não deve virar aprovação, identidade ou revisão humana."""
from pathlib import Path
import json
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = runpy.run_path(str(ROOT / 'docs/entregas/pi_iv_pln_20261023_equipe/participacao.py'))


def resposta():
    return dict(preenchido_por='Participante de teste', data_atividade='2026-10-23',
                relato='Registro fictício exclusivo do teste automatizado, sem contribuição real.',
                evidencias=['relato: cenário sintético para testar o registro, não é reunião real.'],
                uso_de_ia='Dado sintético de teste.')


def test_rodar_formulario_vazio_nao_atribui_participacao(tmp_path):
    result = HELPER['registrar'](tmp_path, 'caio', HELPER['formulario_vazio']())
    assert result['estado'] == 'pendente' and not result['salvo']
    assert not (tmp_path / 'output').exists()


def test_registros_nao_sobrescrevem_nem_validam_humanamente(tmp_path):
    first = HELPER['registrar'](tmp_path, 'tiago', resposta())
    second = HELPER['registrar'](tmp_path, 'tiago', resposta())
    assert first['arquivo'] != second['arquivo']
    records = HELPER['registros'](tmp_path)
    assert len(records) == 2
    assert all(r['estado'] == 'autodeclarado_pendente_conferencia' for r in records)
    assert all(not r['identidade_autenticada'] and not r['valida_linha_do_catalogo']
               and not r['altera_experimento'] and not r['confirma_participacao_de_outros'] for r in records)
    assert len(list(tmp_path.rglob('*.json'))) == 2


def test_rejeita_formulario_parcial_e_campo_de_aprovacao(tmp_path):
    partial = HELPER['formulario_vazio']()
    partial['preenchido_por'] = 'Pessoa de teste'
    with pytest.raises(ValueError):
        HELPER['registrar'](tmp_path, 'guilherme', partial)
    invalid = resposta() | {'aprovado': True}
    with pytest.raises(ValueError):
        HELPER['registrar'](tmp_path, 'guilherme', invalid)
    assert not (tmp_path / 'output').exists()


def test_rejeita_evidencia_fora_do_checkout_e_data_invalida(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + '_fora.txt')
    outside.write_text('Fixture sintética.', encoding='utf-8')
    with pytest.raises(ValueError):
        HELPER['registrar'](tmp_path, 'rodolfo', resposta() | {'evidencias': [str(outside)]})
    with pytest.raises(ValueError):
        HELPER['registrar'](tmp_path, 'rodolfo', resposta() | {'data_atividade': 'dia da reunião'})
    assert not (tmp_path / 'output').exists()
