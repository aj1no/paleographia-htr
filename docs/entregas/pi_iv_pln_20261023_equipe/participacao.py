"""Registro de contribuições autodeclaradas; não autentica autoria ou valida linhas."""
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4
import json

PARTICIPANTES = {
    'caio': 'Caio Augusto de Souza Soares',
    'guilherme': 'Guilherme Rodrigues Veiga',
    'rodolfo': 'Rodolfo Vinicius Cima Takemoto',
    'tiago': 'Tiago Galhardo Avelar',
}
CAMPOS = ('preenchido_por', 'data_atividade', 'relato', 'evidencias', 'uso_de_ia')


def formulario_vazio():
    return dict(preenchido_por='', data_atividade='', relato='', evidencias=[], uso_de_ia='')


def registrar(raiz, participante, respostas):
    """Só grava formulários preenchidos, em novo arquivo dentro de output/."""
    if participante not in PARTICIPANTES:
        raise ValueError('Participante desconhecido.')
    if set(respostas) != set(CAMPOS):
        raise ValueError('Use os campos do formulário, sem acrescentar aprovação ou validação.')
    if not any(respostas.values()):
        return dict(salvo=False, participante=participante, estado='pendente',
                    motivo='Nenhuma contribuição individual preenchida; nenhum registro criado.')
    for campo in CAMPOS:
        if campo == 'evidencias':
            if not isinstance(respostas[campo], list) or not respostas[campo]:
                raise ValueError('Informe ao menos uma evidência ou um relato de discussão identificado.')
        elif not isinstance(respostas[campo], str) or not respostas[campo].strip():
            raise ValueError('Preencha: ' + campo)
    try:
        date.fromisoformat(respostas['data_atividade'])
    except ValueError as exc:
        raise ValueError('Use a data real da atividade no formato AAAA-MM-DD.') from exc

    raiz = Path(raiz).resolve()
    evidencias = []
    for valor in respostas['evidencias']:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError('Evidência vazia ou inválida.')
        valor = valor.strip()
        if valor.startswith('relato:'):
            if not valor.removeprefix('relato:').strip():
                raise ValueError('Descreva a discussão depois de relato:.')
            evidencias.append(dict(tipo='relato_autodeclarado', descricao=valor[7:].strip()))
        elif valor.startswith(('https://', 'http://')):
            evidencias.append(dict(tipo='url_informada_nao_auditada', url=valor))
        else:
            caminho = (raiz / valor).resolve()
            if not caminho.is_relative_to(raiz) or not caminho.is_file():
                raise ValueError('O arquivo de evidência deve existir dentro do checkout: ' + valor)
            evidencias.append(dict(tipo='arquivo_local_informado', caminho=caminho.relative_to(raiz).as_posix()))

    saida = (raiz / 'output/participacao_equipe_20261023').resolve()
    if not saida.is_relative_to(raiz / 'output'):
        raise ValueError('A saída resolveu para fora de output/.')
    saida.mkdir(parents=True, exist_ok=True)
    agora = datetime.now(timezone.utc)
    registro = dict(
        participante=PARTICIPANTES[participante], participante_id=participante,
        preenchido_por=respostas['preenchido_por'].strip(),
        data_atividade=respostas['data_atividade'], registrado_em=agora.isoformat(),
        relato=respostas['relato'].strip(), evidencias=evidencias,
        uso_de_ia=respostas['uso_de_ia'].strip(),
        estado='autodeclarado_pendente_conferencia', identidade_autenticada=False,
        confirma_participacao_de_outros=False, valida_linha_do_catalogo=False,
        altera_experimento=False,
    )
    nome = participante + '_' + agora.strftime('%Y%m%dT%H%M%S') + '_' + uuid4().hex[:8] + '.json'
    destino = saida / nome
    with destino.open('x', encoding='utf-8', newline='\n') as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False, indent=2) + '\n')
    return dict(salvo=True, participante=participante, estado=registro['estado'],
                arquivo=destino.relative_to(raiz).as_posix())


def registros(raiz):
    pasta = Path(raiz).resolve() / 'output/participacao_equipe_20261023'
    return [json.loads(p.read_bytes()) for p in sorted(pasta.glob('*.json'))] if pasta.is_dir() else []
