"""Palavras a conferir na leitura modernizada: as que não estão no dicionário do português atual.

O modernizador só atualiza palavras que reconhece. Uma palavra que continua fora do dicionário
depois da modernização é erro de leitura (``batecins``), palavra antiga que caiu de uso
(``magotes``) ou nome próprio (``Pentiado``). A aba Textos sublinha essas palavras para o
pesquisador localizar os trechos a conferir na imagem. Nada é corrigido aqui: é só uma marca.

Tipos: ``nome`` para a palavra com inicial maiúscula (provável nome próprio) e ``duvida`` para
as demais. Usa o mesmo dicionário do modernizador (``pyspellchecker``, lista ``pt``), sem
alterá-lo; acentos não contam, porque a dúvida é sobre a palavra, não sobre a acentuação.
"""
import re

from .modernizacao import dicionario, nfc, palavra_partida, sem_acento
from .modernizacao_v2 import NOMES

PALAVRA = re.compile(r"[^\W\d_]+")
CONHECIDAS = frozenset({"art", "arts", "pra", "pras", "pro", "pros"})  # abreviatura de artigo e formas orais comuns
ROMANOS = re.compile(r"^[IVXLCDM]+$")


def conhecida(palavra):
    minuscula = palavra.lower()
    if len(minuscula) < 2 or minuscula in CONHECIDAS or ROMANOS.match(palavra):
        return True
    frequencia, acentuadas, _ = dicionario()
    return minuscula in frequencia or sem_acento(minuscula) in acentuadas


NOMES_MODERNIZADOS = frozenset(sem_acento(n.lower()) for n in NOMES.values())


def duvidas(texto, ignorar_primeira=False, ignorar_ultima=False):
    """Trechos ``[início, fim, tipo]`` de ``texto`` (NFC) fora do dicionário atual.

    ``ignorar_primeira``/``ignorar_ultima`` deixam de fora o pedaço de palavra partida na quebra
    de linha (``ra`` | ``zão``), que só faz sentido unido à linha vizinha.
    """
    texto = nfc(texto)
    achadas = list(PALAVRA.finditer(texto))
    saida = []
    for indice, achada in enumerate(achadas):
        if (ignorar_primeira and indice == 0) or (ignorar_ultima and indice == len(achadas) - 1):
            continue
        palavra = achada.group()
        if conhecida(palavra) or sem_acento(palavra.lower()) in NOMES_MODERNIZADOS:
            continue
        saida.append([achada.start(), achada.end(), "nome" if palavra[0].isupper() else "duvida"])
    return saida


def duvidas_por_linha(diplomaticas, modernizadas):
    """Dúvidas de cada linha modernizada, sem marcar os pedaços de palavra partida na quebra."""
    partidas = [bool(atual and seguinte and palavra_partida(atual, seguinte))
                for atual, seguinte in zip(diplomaticas, list(diplomaticas[1:]) + [None])]
    return [duvidas(moderna, ignorar_primeira=indice > 0 and partidas[indice - 1], ignorar_ultima=partidas[indice])
            for indice, moderna in enumerate(modernizadas)]


def localizar(duvidas_do_texto, texto, linhas):
    """Acrescenta a cada dúvida do texto corrido o número da linha de onde ela veio.

    ``linhas`` são pares ``(numero, modernizada)`` em ordem de leitura. A busca anda para a frente:
    primeiro a linha que contém a palavra inteira; senão, a linha cujo fim começa a palavra partida
    na quebra (``me`` + ``lativamenete``). Sem achar, fica a última linha encontrada.
    """
    partes = [[sem_acento(p.lower()) for p in PALAVRA.findall(moderna)] for _, moderna in linhas]
    saida, atual = [], 0
    for inicio, fim, tipo in duvidas_do_texto:
        palavra = sem_acento(texto[inicio:fim].lower())
        inteira = (i for i in range(atual, len(linhas)) if palavra in partes[i])
        partida = (i for i in range(atual, len(linhas)) if partes[i] and len(partes[i][-1]) >= 2
                   and palavra.startswith(partes[i][-1]))
        atual = next(inteira, None) or next(partida, None) or atual
        saida.append([inicio, fim, tipo, linhas[atual][0] if linhas else None])
    return saida
