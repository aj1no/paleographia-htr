"""Leitura modernizada automática: normalização ortográfica do português histórico.

A transcrição diplomática (como está escrito) nunca é alterada; a leitura modernizada é uma
sugestão separada, para o público ler e buscar. Funciona palavra a palavra:

1. Palavras que já existem no português atual ficam como estão, a não ser que uma variante
   próxima seja muito mais comum (``RAZAO_MINIMA`` vezes, já descontado o custo das trocas).
2. Abreviaturas com letras sobrescritas (``Nˢᵃ``, ``muⁱᵗᵒˢ``) são desenvolvidas: as letras
   escritas devem aparecer, em ordem, na palavra plena, que termina pelas letras sobrescritas.
   Uma tabela pequena cobre abreviaturas comuns sem sobrescrito (``q``, ``Snr``) e formas
   fixas (``he`` → ``é``, ``huã`` → ``uma``).
3. As demais passam por regras de grafia histórica → atual (y→i, consoantes dobradas, ``ph``,
   ``-ão``/``-am``, ``-aes``/``-ais``, ``h`` inicial…), aplicadas em até ``MAX_TROCAS`` pontos,
   e pela restauração de acentos. Vence a variante mais frequente no português atual,
   penalizada pelo número de trocas; ela precisa ficar acima de ``FREQUENCIA_MINIMA`` mesmo
   depois da penalidade. Sem variante assim, a palavra fica como está.

Cuidados: palavras com menos de ``TAMANHO_MINIMO`` letras só mudam pelas tabelas; palavras com
maiúscula no meio da linha (``Camara``, ``Capitam``, mas também nomes próprios) recebem as
regras que não trocam a identidade das letras (``REGRAS_SEGURAS``) e acentos; as demais regras
só valem para elas se o resultado for palavra muito frequente (``PISO_NOME``). Acento agudo antes de ``m``/``n`` + vogal
vira circunflexo (``António`` → ``Antônio``), porque o dicionário mistura a norma europeia.

Dicionário do português atual: lista de frequência do pacote público ``pyspellchecker``
(``language="pt"``). As regras vêm das normas de edição modernizada do Arquivo Histórico de
Jundiaí (Novo Acordo Ortográfico) e das mudanças conhecidas da grafia do português.
Pontuação e maiúsculas ficam como no original.
"""
import math
import re
import unicodedata
from functools import lru_cache

MAX_TROCAS = 3
TAMANHO_MINIMO = 3
FREQUENCIA_MINIMA = 20          # forma atual precisa ser palavra estabelecida, não erro de digitação
RAZAO_MINIMA = 10               # para trocar uma palavra que já existe: variante 10× mais comum
CUSTO_TROCA = math.log(10)      # cada troca de grafia custa um fator 10 de frequência
PISO = 0.0                      # variante precisa ser mais de 10^trocas vezes frequente
PISO_NOME = math.log(100)       # com maiúscula no meio da linha, só palavra comum e muito frequente

# Regras que não mudam a identidade das letras: valem também para nomes próprios.
REGRAS_SEGURAS = (
    ("y", "i"), ("ph", "f"), ("th", "t"), ("chr", "cr"),
    ("ll", "l"), ("tt", "t"), ("mm", "m"), ("nn", "n"), ("pp", "p"), ("ff", "f"), ("cc", "c"),
    ("bb", "b"), ("dd", "d"), ("gg", "g"),
    ("aõ", "ão"), ("oẽ", "õe"), ("çe", "ce"), ("çi", "ci"),
)
# Regras de grafia histórica → atual, em minúsculas. ``^`` e ``$`` marcam início e fim da palavra.
REGRAS = REGRAS_SEGURAS + (
    ("ch", "qu"), ("rr", "r"), ("ss", "s"), ("s", "ss"), ("r", "rr"),
    ("ct", "t"), ("pt", "t"), ("gn", "n"), ("mn", "n"), ("sc", "c"),
    ("ão$", "am"), ("am$", "ão"), ("oens$", "ões"), ("aens$", "ães"),
    ("aes$", "ais"), ("oes$", "ões"), ("eo$", "eu"), ("ae$", "ai"), ("ao$", "ão"),
    ("^h", ""), ("^", "h"), ("z", "s"), ("s", "z"), ("x", "ch"), ("ch", "x"), ("x", "ss"),
    ("u", "v"), ("v", "u"), ("j", "i"), ("i", "j"), ("g", "j"),
    ("ç", "c"), ("c", "ç"), ("s", "c"), ("c", "s"), ("ç", "ss"), ("ss", "ç"),
    ("coa", "qua"), ("goa", "gua"), ("e", "i"), ("o", "u"),
    ("n$", "m"), ("nb", "mb"), ("np", "mp"),
    ("ā", "am"), ("ē", "em"), ("ī", "im"), ("ō", "om"), ("ū", "um"),
)

# Abreviaturas frequentes escritas sem sobrescrito (forma em minúsculas, sem ponto final).
ABREVIATURAS = {
    "q": "que", "qe": "que", "q̄": "que", "snr": "senhor", "sr": "senhor", "snra": "senhora",
    "sra": "senhora", "srs": "senhores", "snrs": "senhores", "pa": "para", "pr": "por",
    "dto": "dito", "dta": "dita", "vm": "vossa mercê", "vmce": "vossa mercê", "nsa": "nossa",
    "nso": "nosso",
}

# Formas históricas de palavras curtas, com til ou ``h`` antigo.
FORMAS_FIXAS = {
    "he": "é", "hé": "é", "hum": "um", "huma": "uma", "humas": "umas", "huns": "uns",
    "huã": "uma", "huā": "uma", "hũa": "uma", "hũ": "um", "huãs": "umas", "huas": "umas",
    "hūa": "uma", "ē": "em", "cō": "com", "cõ": "com", "bē": "bem", "hē": "em",
}

SOBRESCRITOS = dict(zip("ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻªº", "abcdefghijklmnoprstuvwxyzao"))  # não há q sobrescrito
PONTUACAO = "\"'“”‘’«»()[]{}.,;:!?…"
CIRCUNFLEXO = {"ó": "ô", "é": "ê"}


def nfc(texto):
    return unicodedata.normalize("NFC", texto or "")


def sem_acento(palavra):
    return "".join(c for c in unicodedata.normalize("NFD", palavra) if not unicodedata.combining(c))


def brasileira(palavra):
    """``antónio`` → ``antônio``: agudo antes de m/n seguido de vogal vira circunflexo."""
    return re.sub(r"[óé](?=[mn][aeiouáéíóúâêôãõ])", lambda m: CIRCUNFLEXO[m.group()], palavra)


@lru_cache(maxsize=1)
def dicionario():
    """Frequência das palavras do português atual (pacote pyspellchecker, lista ``pt``)."""
    from spellchecker import SpellChecker
    frequencia = dict(SpellChecker(language="pt").word_frequency.dictionary)
    acentuadas = {}
    for palavra, n in frequencia.items():
        chave = sem_acento(palavra)
        if n > acentuadas.get(chave, ("", 0))[1]:
            acentuadas[chave] = (palavra, n)
    por_inicial = {}
    for palavra, n in frequencia.items():
        if n >= FREQUENCIA_MINIMA and palavra.isalpha():
            por_inicial.setdefault(sem_acento(palavra[0]), []).append((palavra, n))
    return frequencia, acentuadas, por_inicial


def _aplicacoes(palavra, regras):
    """Todas as palavras obtidas aplicando uma regra em um único ponto."""
    saida = set()
    for de, para in regras:
        nucleo = de.strip("^$")
        if de.startswith("^"):
            if palavra.startswith(nucleo):
                saida.add(para + palavra[len(nucleo):])
        elif de.endswith("$"):
            if palavra.endswith(nucleo):
                saida.add(palavra[: len(palavra) - len(nucleo)] + para)
        else:
            inicio = palavra.find(nucleo)
            while inicio != -1:
                saida.add(palavra[:inicio] + para + palavra[inicio + len(nucleo):])
                inicio = palavra.find(nucleo, inicio + 1)
    saida.discard(palavra)
    return {p for p in saida if p}


def _variantes(palavra, regras):
    """Variantes a até ``MAX_TROCAS`` trocas, com o número mínimo de trocas de cada uma."""
    trocas, fronteira = {palavra: 0}, {palavra}
    for passo in range(1, MAX_TROCAS + 1):
        nova = set()
        for p in fronteira:
            for q in _aplicacoes(p, regras):
                if q not in trocas:
                    trocas[q] = passo
                    nova.add(q)
        fronteira = nova
        if len(trocas) > 20000:
            break
    return trocas


def _conhecida(palavra):
    """Forma atual (com acentos restaurados se preciso) e frequência; ``None`` se desconhecida."""
    frequencia, acentuadas, _ = dicionario()
    melhor = (palavra, frequencia.get(palavra, 0))
    acentuada = acentuadas.get(sem_acento(palavra))
    if acentuada and acentuada[1] > RAZAO_MINIMA * melhor[1]:   # ``ana`` não vira ``anã``
        melhor = acentuada
    return melhor if melhor[1] >= FREQUENCIA_MINIMA else None


def desenvolver_abreviatura(base, sobrescrito):
    """``N`` + ``sa`` → ``nossa``: letras em ordem, terminando pelas sobrescritas; a mais frequente."""
    letras = sem_acento((base + sobrescrito).lower())
    _, _, por_inicial = dicionario()
    melhor = None
    for palavra, n in por_inicial.get(letras[0], []):
        simples = sem_acento(palavra)
        if not simples.endswith(sem_acento(sobrescrito.lower())) or len(simples) > len(letras) + 8:
            continue
        posicao = 0
        for letra in letras:
            posicao = simples.find(letra, posicao) + 1
            if not posicao:
                break
        if posicao and (melhor is None or n > melhor[1]):
            melhor = (palavra, n)
    return brasileira(melhor[0]) if melhor else None


@lru_cache(maxsize=50000)
def modernizar_palavra(palavra, nome_proprio=False):
    """Devolve (forma modernizada em minúsculas ou ``None``, motivo) para uma palavra sem pontuação."""
    minuscula = nfc(palavra).lower()
    if minuscula in FORMAS_FIXAS:
        return FORMAS_FIXAS[minuscula], "forma fixa"
    if any(c in SOBRESCRITOS for c in minuscula):
        base = "".join(c for c in minuscula if c not in SOBRESCRITOS)
        sobrescrito = "".join(SOBRESCRITOS[c] for c in minuscula if c in SOBRESCRITOS)
        for forma in (base + sobrescrito, base):
            if forma in ABREVIATURAS:
                return ABREVIATURAS[forma], "abreviatura"
        plena = desenvolver_abreviatura(base, sobrescrito) if base.isalpha() else None
        return (plena, "abreviatura") if plena else (None, "abreviatura não resolvida")
    if minuscula in ABREVIATURAS:
        return ABREVIATURAS[minuscula], "abreviatura"
    if not minuscula.isalpha():
        return None, "não é palavra"
    if len(minuscula) < TAMANHO_MINIMO:
        return None, "curta demais"
    frequencia, _, _ = dicionario()
    original = frequencia.get(minuscula, 0)
    melhor, melhor_pontuacao = None, -math.inf
    seguras = _variantes(minuscula, REGRAS_SEGURAS)
    for variante, passos in _variantes(minuscula, REGRAS).items():
        conhecida = _conhecida(variante)
        if not conhecida:
            continue
        pontuacao = math.log(conhecida[1]) - passos * CUSTO_TROCA
        if nome_proprio and variante not in seguras and pontuacao < PISO_NOME:
            continue
        if pontuacao > melhor_pontuacao or (pontuacao == melhor_pontuacao and conhecida[0] < melhor[0]):
            melhor, melhor_pontuacao = conhecida, pontuacao
    if melhor is None or melhor_pontuacao < PISO:
        return None, "sem forma atual segura"
    forma = brasileira(melhor[0])
    if forma == minuscula:
        return None, "atual"
    if original >= FREQUENCIA_MINIMA and melhor_pontuacao < math.log(original) + math.log(RAZAO_MINIMA):
        return None, "atual"
    return forma, "grafia atualizada"


def _caixa(modelo, palavra):
    if modelo.isupper() and len(modelo) > 1:
        return palavra.upper()
    if modelo[:1].isupper():
        return palavra[:1].upper() + palavra[1:]
    return palavra


def modernizar_linha(texto, partida_no_inicio=False, partida_no_fim=False):
    """Devolve (leitura modernizada, trocas). Não altera o texto recebido.

    ``partida_no_inicio``/``partida_no_fim``: a primeira/última palavra é pedaço de palavra
    dividida na quebra de linha e fica como está (``cumpri`` | ``mento``).
    """
    saida, trocas = [], []
    tokens = nfc(texto).split()
    for indice, token in enumerate(tokens):
        inicio = len(token) - len(token.lstrip(PONTUACAO))
        fim = len(token.rstrip(PONTUACAO))
        antes, nucleo, depois = token[:inicio], token[inicio:fim], token[fim:]
        ultima = indice == len(tokens) - 1
        quebrada = ultima and (nucleo.endswith(("-", "=", "¬")) or partida_no_fim)
        if not nucleo or quebrada or (indice == 0 and partida_no_inicio):
            saida.append(token)
            continue
        nome_proprio = indice > 0 and nucleo[:1].isupper()
        nova, motivo = modernizar_palavra(nucleo, nome_proprio)
        if nova is None:
            saida.append(token)
            continue
        nova = _caixa(nucleo, nova)
        if nova != nucleo:
            trocas.append({"de": nucleo, "para": nova, "motivo": motivo})
        saida.append(antes + nova + depois)
    return " ".join(saida), trocas


def palavra_partida(linha, seguinte):
    """A última palavra de ``linha`` continua na primeira de ``seguinte``?

    Sim se houver hífen no fim ou se as duas partes juntas, depois de modernizadas, formarem
    palavra do português atual que nenhuma das duas é sozinha (``satisfa`` + ``ca``).
    """
    fim, comeco = nfc(linha).split(), nfc(seguinte).split()
    if not fim or not comeco or fim[-1][-1:] in ",;:.!?" or not comeco[0][:1].islower():
        return False
    if fim[-1].endswith(("-", "=", "¬")):
        return True
    a, b = fim[-1].strip(PONTUACAO), comeco[0].strip(PONTUACAO)
    if not (a.isalpha() and b.isalpha()):
        return False
    junta = (a + b).lower()
    frequencia, _, _ = dicionario()
    juntas = _conhecida(junta) or _conhecida(modernizar_palavra(junta)[0] or junta)
    if not juntas:
        return False
    separadas = min(frequencia.get(a.lower(), 0), frequencia.get(b.lower(), 0))
    return juntas[1] > separadas


def modernizar_linhas(textos):
    """Moderniza linhas em ordem de leitura, respeitando palavras divididas entre linhas.

    ``textos``: lista de linhas (``None`` ou vazia quando não há leitura). Devolve a lista de
    leituras modernizadas ("" quando não há leitura).
    """
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
