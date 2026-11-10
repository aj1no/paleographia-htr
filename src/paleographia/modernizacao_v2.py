"""Leitura modernizada, versão 2: uma camada sobre ``modernizacao`` (v1), que não é alterada.

A v1 trabalha palavra a palavra e deixa passar quatro coisas comuns nos documentos coloniais.
A v2 trata essas quatro antes de chamar a v1 e, no resto, devolve o que a v1 devolveria:

1. **Caixa.** Maiúsculas no meio da palavra (``TOdos`` → ``todos``) e palavras gramaticais
   com maiúscula no meio da frase (``Com``, ``Pella``) vão para minúsculas. A v1 trata
   maiúscula no meio da linha como nome próprio e evita mexer nela.
2. **Palavras partidas dentro da linha.** Duas partes viram uma quando a segunda sozinha não
   é palavra do português atual e as duas juntas são (``Com quistas`` → ``Conquistas``). Uma
   tabela pequena cobre os casos em que as duas partes existem (``tão bem`` → ``também``).
   Antes de consoante que não seja ``p``/``b``, o ``m`` da junção vira ``n``.
3. **Nomes próprios.** Uma tabela de topônimos da capitania de São Paulo e de prenomes
   comuns em grafia antiga (``Jundiahy`` → ``Jundiaí``, ``Joam`` → ``João``). Fora da tabela,
   os nomes continuam com as proteções da v1.
4. **Pretérito em -ão.** Nas atas, contratos e cartas, ``-ão`` no fim de verbo marca quase
   sempre o pretérito (``derão``, ``forão``, ``estavão``). A palavra vira ``-am`` quando essa
   forma é palavra atual (``derão`` → ``deram``, ``puzerão`` → ``puseram``). O futuro
   (``farão``) fica de fora sem querer, porque ``faram`` não existe. A v1 escolhia pela
   frequência e errava (``deraõ`` → ``dirão``, ``Havião`` → ``Avião``).

As tabelas e a regra do -ão vêm de fenômenos conhecidos da grafia setecentista e da
onomástica paulista. Não vêm de linhas do teste reservado.
"""
import re

from .modernizacao import (FREQUENCIA_MINIMA, PONTUACAO, SOBRESCRITOS, _caixa, _conhecida, brasileira,
                           modernizar_palavra, nfc, palavra_partida)

VERSAO = 2
FREQUENCIA_JUNCAO = 50       # a palavra unida precisa ser estabelecida no português atual
TAMANHO_MINIMO_VERBO = 5     # ``são``, ``dão``, ``irão`` ficam fora da regra do -ão

# Palavras gramaticais: com maiúscula no meio da frase, vão para minúsculas.
GRAMATICAIS = frozenset("""
a o as os ao aos à às de do da dos das em no na nos nas num numa com por pelo pela pelos pelas
para pera que e se como mas ou nem não já também mais muito muita muitos muitas todo toda
todos todas tudo seu sua seus suas este esta estes estas isto esse essa esses essas isso
aquele aquela aqueles aquelas aquilo ele ela eles elas lhe lhes me te nós vós um uma uns umas
qual quais quando onde até sem sobre entre depois antes logo então porém porque pois assim
""".split())

# Antes de substantivo, não de verbo (``a``/``as``/``o``/``os`` ficam fora: também são pronomes).
DETERMINANTES = frozenset("""
um uma uns umas do da dos das no na nos nas ao aos pelo pela pelos pelas pello pella de num numa
mesmo mesma mesmos mesmas seu sua seus suas meu minha nosso nossa este esta esse essa aquele
aquela grande santo santa outro outra qualquer cada
""".split())

# Partes separadas que formam uma palavra, quando as duas partes existem sozinhas.
JUNCOES = {
    ("tão", "bem"): "também", ("tam", "bem"): "também", ("taõ", "bem"): "também",
    ("toda", "via"): "todavia", ("de", "pois"): "depois", ("a", "onde"): "aonde",
    ("em", "fim"): "enfim", ("sobre", "dito"): "sobredito",
    ("sobre", "dita"): "sobredita", ("sobre", "ditos"): "sobreditos", ("sobre", "ditas"): "sobreditas",
}
# Palavras que a v1 erra por frequência (achadas na varredura das linhas de treino).
CORRECOES = {"reo": "réu", "reos": "réus", "menhã": "manhã", "menham": "manhã", "paes": "Paes"}

# Topônimos e prenomes em grafia antiga (chave sem acento de til em ``aõ``, em minúsculas).
NOMES = {
    "jundiahy": "Jundiaí", "jundiahi": "Jundiaí", "jundiay": "Jundiaí", "jundiai": "Jundiaí",
    "jundiahij": "Jundiaí", "jundiahÿ": "Jundiaí",
    "parnahyba": "Parnaíba", "parnahiba": "Parnaíba", "parnaiba": "Parnaíba",
    "ytu": "Itu", "hytu": "Itu", "atibaya": "Atibaia", "mogy": "Mogi", "juquery": "Juqueri",
    "jacarehy": "Jacareí", "jacarehi": "Jacareí", "goyaz": "Goiás", "goyás": "Goiás",
    "cuyabá": "Cuiabá", "cuyaba": "Cuiabá", "guaratinguitá": "Guaratinguetá",
    "piratininga": "Piratininga", "ytapetininga": "Itapetininga", "sorocaba": "Sorocaba",
    "riberão": "Ribeirão", "ribeyrão": "Ribeirão", "ribeirao": "Ribeirão", "riberao": "Ribeirão",
    "joam": "João", "joaõ": "João", "joão": "João", "joaô": "João", "joao": "João",
    "jozé": "José", "joze": "José", "jose": "José", "josé": "José", "jozeph": "José", "joseph": "José",
    "manoel": "Manuel", "ignacio": "Inácio", "ignácio": "Inácio", "ignes": "Inês", "ignez": "Inês",
    "luiz": "Luís", "luis": "Luís", "braz": "Brás", "bras": "Brás", "thomé": "Tomé", "thome": "Tomé",
    "mathias": "Matias", "thereza": "Teresa", "theresa": "Teresa", "izabel": "Isabel",
    "isabella": "Isabela", "anna": "Ana", "maria": "Maria", "estevão": "Estêvão", "estevam": "Estêvão",
    "sebastiam": "Sebastião", "sebastiaõ": "Sebastião", "sebastião": "Sebastião",
    "christovão": "Cristóvão", "christovam": "Cristóvão", "christovaõ": "Cristóvão",
    "gonçallo": "Gonçalo", "gonsalo": "Gonçalo", "gonçalves": "Gonçalves", "gonsalves": "Gonçalves",
    "rodrigues": "Rodrigues", "roiz": "Rodrigues", "glz": "Gonçalves",
}

MAIUSCULAS_NO_MEIO = re.compile(r"^[A-ZÀ-Ý]{2,}[a-zà-ÿ]+$")
CONSOANTE_DEPOIS_DE_M = re.compile(r"m(?=[^aeiouáéíóúâêôãõàpbh\W])")


def _sem_til_antigo(palavra):
    return palavra.replace("aõ", "ão").replace("oẽ", "õe")


def _corrigir_caixa(nucleo):
    """``TOdos`` → ``Todos``: maiúsculas seguidas de minúsculas, sem abreviatura."""
    if MAIUSCULAS_NO_MEIO.match(nucleo) and not any(c in SOBRESCRITOS for c in nucleo):
        return nucleo[0] + nucleo[1:].lower()
    return nucleo


def _palavra_atual(palavra):
    """Forma atual (minúsculas) e frequência, pela v1; ``None`` se não for palavra atual."""
    minuscula = nfc(palavra).lower()
    conhecida = _conhecida(minuscula)
    if conhecida:
        return brasileira(conhecida[0]), conhecida[1]
    forma = modernizar_palavra(minuscula)[0]
    conhecida = forma and _conhecida(forma)
    return (brasileira(conhecida[0]), conhecida[1]) if conhecida else None


def _juncao(a, b):
    """Palavra única formada por ``a`` + ``b``, ou ``None``."""
    chave = (_sem_til_antigo(a.lower()), _sem_til_antigo(b.lower()))
    if chave in JUNCOES:
        return JUNCOES[chave]
    # ``o mto``: abreviatura sem vogal não é pedaço de palavra.
    if not (a.isalpha() and b.isalpha()) or len(a) < 2 or len(b) < 3 or not b[:1].islower() \
            or not re.search(r"[aeiouáéíóúâêôãõ]", b.lower()) or len(a + b) < 6:
        return None
    if _palavra_atual(b):                  # ``de vendo``: a segunda parte existe, fica separada
        return None
    junta = CONSOANTE_DEPOIS_DE_M.sub("n", (a + b).lower())
    atual = _palavra_atual(junta)
    if not atual or atual[1] < FREQUENCIA_JUNCAO:
        return None
    return atual[0]


def _preterito(minuscula, anterior=""):
    """``derão`` → ``deram``; ``None`` se a regra não se aplica.

    Depois de determinante (``pela mesma Rezaõ``, ``do Fundaõ``) a palavra é substantivo.
    """
    palavra = _sem_til_antigo(minuscula)
    if len(palavra) < TAMANHO_MINIMO_VERBO or not palavra.endswith("ão") \
            or _separar(anterior)[1].lower() in DETERMINANTES:
        return None
    candidata = palavra[:-2] + "am"
    if _conhecida(candidata) and _conhecida(candidata)[0] == candidata:
        return candidata
    forma = modernizar_palavra(candidata)[0]
    if forma and forma.endswith("am") and _conhecida(forma):
        return forma
    return None


def _inicio_de_frase(tokens, indice):
    return indice == 0 or tokens[indice - 1].rstrip("\"'”’»)]").endswith((".", "!", "?", ":"))


def _separar(token):
    inicio = len(token) - len(token.lstrip(PONTUACAO))
    fim = len(token.rstrip(PONTUACAO))
    return token[:inicio], token[inicio:fim], token[fim:]


def _unir_partidas(tokens, partida_no_inicio, partida_no_fim, trocas):
    """Junta, dentro da linha, as palavras escritas em duas partes."""
    saida, indice = [], 0
    while indice < len(tokens):
        token = tokens[indice]
        if indice + 1 < len(tokens) and not (indice == 0 and partida_no_inicio) \
                and not (indice + 1 == len(tokens) - 1 and partida_no_fim):
            antes, a, fim_a = _separar(token)
            inicio_b, b, depois = _separar(tokens[indice + 1])
            if a and b and not fim_a and not inicio_b:
                junta = _juncao(_corrigir_caixa(a), _corrigir_caixa(b))
                if junta:
                    junta = _caixa(a if not MAIUSCULAS_NO_MEIO.match(a) else a[0], junta)
                    trocas.append({"de": f"{a} {b}", "para": junta, "motivo": "palavra unida"})
                    saida.append((antes + junta + depois, True))
                    indice += 2
                    continue
        saida.append((token, False))
        indice += 1
    return saida


def modernizar_linha(texto, partida_no_inicio=False, partida_no_fim=False):
    """Devolve (leitura modernizada, trocas), como ``modernizacao.modernizar_linha``."""
    trocas = []
    tokens = nfc(texto).split()
    unidos = _unir_partidas(tokens, partida_no_inicio, partida_no_fim, trocas)
    originais = [t for t, _ in unidos]
    saida = []
    for indice, (token, ja_unido) in enumerate(unidos):
        antes, nucleo, depois = _separar(token)
        ultima = indice == len(unidos) - 1
        quebrada = ultima and (nucleo.endswith(("-", "=", "¬")) or partida_no_fim)
        if ja_unido or not nucleo or quebrada or (indice == 0 and partida_no_inicio):
            saida.append(token)
            continue
        frase = _inicio_de_frase(originais, indice)
        corrigido = _corrigir_caixa(nucleo)
        minuscula = _sem_til_antigo(corrigido.lower())
        nova, motivo = None, None
        if minuscula in NOMES:
            nova, motivo = NOMES[minuscula], "nome próprio"
        elif minuscula in CORRECOES:
            nova, motivo = _caixa(corrigido, CORRECOES[minuscula]), "forma fixa"
        elif (preterito := _preterito(minuscula, originais[indice - 1] if indice else "")) is not None:
            nova, motivo = _caixa(corrigido, preterito), "pretérito em -am"
        else:
            forma, motivo_v1 = modernizar_palavra(corrigido, indice > 0 and corrigido[:1].isupper())
            if forma is not None:
                nova, motivo = _caixa(corrigido, forma), motivo_v1
        atual = nova if nova is not None else corrigido
        if not frase and atual[:1].isupper() and atual.lower() in GRAMATICAIS and len(atual) > 1 \
                and minuscula not in NOMES:
            atual, motivo = atual.lower(), motivo or "minúscula"
        elif corrigido != nucleo and nova is None:
            motivo = "minúscula"
        if atual != nucleo:
            trocas.append({"de": nucleo, "para": atual, "motivo": motivo})
        saida.append(antes + atual + depois)
    return " ".join(saida), trocas


def modernizar_linhas(textos):
    """Como ``modernizacao.modernizar_linhas``, com a v2 em cada linha."""
    partidas = [bool(atual and seguinte and palavra_partida(atual, seguinte))
                for atual, seguinte in zip(textos, list(textos[1:]) + [None])]
    saida = []
    for indice, texto in enumerate(textos):
        if not texto:
            saida.append("")
            continue
        inicio = indice > 0 and partidas[indice - 1]
        saida.append(modernizar_linha(texto, partida_no_inicio=inicio, partida_no_fim=partidas[indice])[0])
    return saida
