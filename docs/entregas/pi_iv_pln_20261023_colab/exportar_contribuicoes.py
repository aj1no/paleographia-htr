"""Pacote de contribuições de um participante, sem autenticar ou publicar relatos."""
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED
import json


def criar_pacote_contribuicoes(raiz, participante):
    if participante not in {'caio', 'guilherme', 'tiago', 'rodolfo'}:
        raise ValueError('Selecione um integrante da equipe.')
    raiz = Path(raiz).resolve()
    pasta = (raiz / 'output/participacao_equipe_20261023').resolve()
    if not pasta.is_relative_to(raiz / 'output'):
        raise ValueError('Pasta de registros fora de output/.')
    arquivos = []
    for caminho in sorted(pasta.glob(participante + '_*.json')):
        if not caminho.resolve().is_relative_to(pasta):
            raise ValueError('Registro resolveu para fora da pasta de contribuições.')
        registro = json.loads(caminho.read_bytes())
        if registro.get('participante_id') != participante:
            raise ValueError('O participante do registro não corresponde ao nome do arquivo.')
        arquivos.append(caminho)
    if not arquivos:
        return None
    saida = (raiz / 'output/equipe_colab_20261023').resolve()
    if not saida.is_relative_to(raiz / 'output'):
        raise ValueError('Pasta de download fora de output/.')
    saida.mkdir(parents=True, exist_ok=True)
    agora = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    destino = saida / ('contribuicoes_' + participante + '_' + agora + '_' + uuid4().hex[:8] + '.zip')
    with ZipFile(destino, 'x', compression=ZIP_DEFLATED) as pacote:
        for caminho in arquivos:
            pacote.write(caminho, arcname=caminho.name)
        pacote.writestr('LEIA-ME.txt',
            'Contribuições autodeclaradas de ' + participante + '.\n'
            'Os JSONs preservam autoria informada, data, relato, evidências e uso de IA.\n'
            'Múltiplos arquivos podem representar versões sucessivas.\n'
            'A coordenação e o participante devem conferir os relatos; não há validação automática.\n')
    return destino
