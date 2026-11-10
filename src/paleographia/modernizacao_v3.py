"""Leitura modernizada, versão 3: uma camada sobre a v2 (e a v1), que não são alteradas.

Feita em 10/11/2026 a partir dos erros da v2 nas Posturas de 1831, comparadas com a edição
modernizada do AHMJ (ver ``docs/experimentos/modernizacao_20261107/README.md``). Trata:

1. **Artigo e ordinal.** ``Art. 1°`` → ``Artigo 1º``; o sinal de grau depois de número vira o
   indicador ordinal (``artigo 4°`` → ``artigo 4º``).
2. **Réis.** ``mil reis`` → ``mil réis``: ``reis`` depois de numeral é a moeda, não o plural de rei.
3. **Futuro em -rão.** A v2 lê ``-ão`` como pretérito (``derão`` → ``deram``). Em texto
   normativo é futuro (``não construirão``). Quando há um futuro inequívoco por perto
   (``será``, ``terá``, ``poderá``…, até 30 palavras antes ou depois), a palavra fica no futuro.
4. **Palavra grudada e partida.** Palavra fora do dicionário que é ``e``/``a``/``o``/``de``… +
   palavra atual é separada (``eo`` → ``e o``, ``apena`` → ``a pena``); ``a`` + pedaço que
   sozinho não existe é unido quando a junção é palavra (``a lugador`` → ``alugador``).
5. **Palavra rara do dicionário.** Palavras na frequência mínima da lista (50) são quase
   sempre grafias sem acento ou cedilha; quando uma variante de uma troca é ao menos 2× mais
   comum, ela é usada (``acoites`` → ``açoites``, ``individuo`` → ``indivíduo``). Uma lista
   protege palavras raras legítimas (``paço``).
6. **Formas fixas** (``cincoenta`` → ``cinquenta``) e **minúscula** em substantivos comuns de
   papel social escritos com maiúscula no meio da frase (``o Contraventor``, ``seu Senhor``),
   fora de ``Nosso Senhor``/``Nossa Senhora``.
7. **Hífen de quebra.** ``paga -`` | ``rá`` é palavra partida só se a junção for palavra
   (``pagará``); ``de -`` | ``multa`` é hífen de enchimento e some. Hífen antes de maiúscula
   (``Juiz de-`` | ``Paz``) também some.
"""
import re

from . import modernizacao_v2 as v2
from .modernizacao import (PONTUACAO, _aplicacoes, _caixa, _conhecida, brasileira, dicionario, nfc,
                           palavra_partida as _partida_v1, sem_acento)

VERSAO = 3
FREQUENCIA_PISO = 50          # a menor frequência da lista do pyspellchecker
RAZAO_RARA = 2                # variante precisa ser 2× mais comum que a palavra rara
FREQUENCIA_SEPARACAO = 500    # a palavra que sobra na separação precisa ser comum
JANELA_FUTURO = 30            # palavras antes e depois em que se procura um futuro inequívoco
HIFENS = ("-", "=", "¬")

PROTEGIDAS = frozenset({"paço", "paços"})
FORMAS = {"cincoenta": "cinquenta", "cincoentas": "cinquentas", "aa": "à", "aas": "às"}
# Só depois destas palavras o papel social vai para minúscula (``o Contraventor``, ``seu Senhor``);
# ``o dito Senhor``, ``Paschoal Dias`` e ``Nossa Senhora`` ficam como estão.
ANTES_DE_PAPEL = frozenset("o a os as ao aos à às do da dos das no na nos nas pelo pela seu sua seus suas de em".split())
NUMERAIS = frozenset("""
um uma dois duas tres três quatro cinco seis sete oito nove dez onze doze treze catorze quatorze
quinze dezesseis dezasseis dezessete dezassete dezoito dezenove dezanove vinte trinta quarenta
cinquenta cincoenta sessenta setenta oitenta noventa cem cento duzentos trezentos quatrocentos
quinhentos seiscentos setecentos oitocentos novecentos mil
""".split())
# Futuros que não se confundem com outra forma (``sera``, ``tera`` sem acento não são palavras).
FUTUROS = frozenset("sera tera podera havera estara fara dara vera sabera".split())
FUTURO_ACENTUADO = re.compile(r"^[a-zà-ÿ]{2,}rá$")
SEPARAVEIS = ("e", "a", "o", "de", "da", "do", "em", "no", "na")
# Substantivos comuns que os escrivães escreviam com maiúscula.
PAPEIS = frozenset("""
senhor senhores senhora senhoras escravo escravos escrava escravas contraventor contraventores
negociante negociantes cadeia multa multas passaporte município fazendas roupas dias pessoa pessoas
""".split())
ARTIGO = re.compile(r"\bArt\.?\s*(\d+)\s*[°º]?", re.IGNORECASE)
ORDINAL = re.compile(r"(?<=\d)°")
ORDINAL_DE_ARTIGO = re.compile(r"^\d+º[.\-–]?$")  # depois de ``Artigo 4º`` começa a frase do artigo


def _frequencia(palavra):
    return dicionario()[0].get(palavra, 0)


def _rara_para_comum(minuscula):
    """Palavra na frequência mínima → variante de uma troca (ou com acento) 2× mais comum."""
    if minuscula in PROTEGIDAS or not minuscula.isalpha() or len(minuscula) < 4             or _frequencia(minuscula) > FREQUENCIA_PISO:
        return None
    _, acentuadas, _ = dicionario()
    candidatas = [acentuadas.get(sem_acento(minuscula))]
    candidatas += [_conhecida(v) for v in _aplicacoes(minuscula, (("c", "ç"), ("ss", "ç"), ("z", "s"), ("s", "z")))]
    melhor = max((c for c in candidatas if c and c[0] != minuscula), key=lambda c: c[1], default=None)
    return brasileira(melhor[0]) if melhor and melhor[1] >= RAZAO_RARA * FREQUENCIA_PISO else None


def _separar_grudada(minuscula):
    """``eo`` → ``e o``; ``apena`` → ``a pena``. ``None`` se não se aplica."""
    if v2._palavra_atual(minuscula):
        return None
    for prefixo in SEPARAVEIS:
        resto = minuscula[len(prefixo):]
        if not minuscula.startswith(prefixo) or not resto:
            continue
        if resto in v2.GRAMATICAIS and len(minuscula) <= 3:
            return f"{prefixo} {resto}"
        if len(resto) >= 4 and _frequencia(resto) >= FREQUENCIA_SEPARACAO:
            return f"{prefixo} {resto}"
    return None


def _juntar_a(b):
    """``a`` + ``lugador`` → ``alugador``, quando ``lugador`` sozinho não existe."""
    if not b.isalpha() or not b[:1].islower() or len(b) < 4 or v2._palavra_atual(b):
        return None
    atual = v2._palavra_atual("a" + b)
    return atual[0] if atual and atual[1] >= v2.FREQUENCIA_JUNCAO else None


def _futuro(nucleo):
    minuscula = nfc(nucleo).lower()
    return minuscula in FUTUROS or bool(FUTURO_ACENTUADO.match(minuscula))


def _juntavel(a, b):
    """Duas partes em volta de um hífen de quebra formam palavra atual?"""
    a, b = a.strip(PONTUACAO), b.strip(PONTUACAO)
    if not (a.isalpha() and b.isalpha()):
        return False
    atual = v2._palavra_atual(a + b) or v2._palavra_atual(v2._sem_til_antigo((a + b).lower()))
    return bool(atual and atual[1] >= v2.FREQUENCIA_JUNCAO)


def palavra_partida(linha, seguinte):
    """Como a da v1, com o hífen de enchimento (``de -`` | ``multa``) e o hífen antes de maiúscula."""
    fim, comeco = nfc(linha).split(), nfc(seguinte or "").split()
    if not fim or not comeco:
        return False
    if fim[-1] in HIFENS:                                   # hífen solto: só se a junção existe
        return len(fim) > 1 and comeco[0][:1].islower() and _juntavel(fim[-2], comeco[0])
    if fim[-1].endswith(HIFENS) and not comeco[0][:1].islower():
        return False
    return _partida_v1(linha, seguinte)


def limpar_hifen(linha, seguinte):
    """Tira da linha o hífen do fim que não parte palavra (enchimento ou antes de maiúscula)."""
    texto = nfc(linha).rstrip()
    if seguinte is not None and texto.endswith(HIFENS) and not palavra_partida(linha, seguinte):
        return texto[:-1].rstrip()
    return texto


def _preparar(texto):
    texto = ARTIGO.sub(lambda m: f"Artigo {m.group(1)}º", nfc(texto))
    texto = ORDINAL.sub("º", texto)
    # ``ja- Prada``: hífen no meio da linha antes de maiúscula não parte palavra.
    return re.sub(r"(?<=\w)[-=¬](?=\s+[A-ZÀ-Ý])", "", texto)


def _janela_futuro(tokens, contexto_antes, contexto_depois):
    """Para cada token, se há futuro inequívoco a até ``JANELA_FUTURO`` palavras."""
    antes, depois = nfc(contexto_antes).split(), nfc(contexto_depois).split()
    todos = antes + tokens + depois
    marcas = [i for i, t in enumerate(todos) if _futuro(v2._separar(t)[1])]
    return [any(abs(m - (len(antes) + i)) <= JANELA_FUTURO for m in marcas) for i in range(len(tokens))]


def _juntar_as(tokens, ultimo_livre, trocas):
    """``a lugador`` → ``alugador``, antes da junção da v2, que não junta partes de uma letra."""
    saida, i = [], 0
    while i < len(tokens):
        if tokens[i].lower() == "a" and i + 1 < ultimo_livre:
            antes_b, b, depois_b = v2._separar(tokens[i + 1])
            unida = None if antes_b else _juntar_a(b)
            if unida:
                saida.append(_caixa(tokens[i], unida) + depois_b)
                trocas.append({"de": f"{tokens[i]} {b}", "para": unida, "motivo": "palavra unida"})
                i += 2
                continue
        saida.append(tokens[i])
        i += 1
    return saida


def modernizar_linha(texto, partida_no_inicio=False, partida_no_fim=False, contexto_antes="", contexto_depois=""):
    """Devolve (leitura modernizada, trocas), como as versões anteriores.

    ``contexto_antes``/``contexto_depois``: linhas vizinhas. Servem para decidir futuro ×
    pretérito e se a primeira palavra começa frase; não entram na saída.
    """
    trocas = []
    tokens = _preparar(texto).split()
    hifen_solto = bool(tokens) and tokens[-1] in HIFENS          # ``paga -``
    partida = partida_no_fim or hifen_solto
    tokens = _juntar_as(tokens, len(tokens) - (2 if partida else 0), trocas)
    unidos = v2._unir_partidas(tokens, partida_no_inicio, partida and not hifen_solto, trocas)
    originais = [t for t, _ in unidos]
    partida_em = len(unidos) - (2 if hifen_solto else 1) if partida else None
    futuro = _janela_futuro(originais, contexto_antes, contexto_depois)
    continua = bool(contexto_antes.strip()) and not contexto_antes.rstrip().rstrip("\"'”’»)]").endswith((".", "!", "?", ":"))
    saida = []
    for indice, (token, ja_unido) in enumerate(unidos):
        antes, nucleo, depois = v2._separar(token)
        quebrada = indice == partida_em or (indice == len(unidos) - 1 and nucleo.endswith(HIFENS))
        if ja_unido or not nucleo or quebrada or nucleo in HIFENS or (indice == 0 and partida_no_inicio):
            saida.append(token)
            continue
        frase = v2._inicio_de_frase(originais, indice) \
            or (indice > 0 and ORDINAL_DE_ARTIGO.match(originais[indice - 1]) is not None)
        corrigido = v2._corrigir_caixa(nucleo)
        minuscula = v2._sem_til_antigo(corrigido.lower())
        anterior = v2._separar(originais[indice - 1])[1].lower() if indice else \
            (v2._separar(contexto_antes.split()[-1])[1].lower() if continua else "")
        nova = motivo = None
        if minuscula in PROTEGIDAS:
            nova = corrigido
        elif minuscula in v2.NOMES:
            nova, motivo = v2.NOMES[minuscula], "nome próprio"
        elif minuscula in v2.CORRECOES:
            nova, motivo = _caixa(corrigido, v2.CORRECOES[minuscula]), "forma fixa"
        elif minuscula in FORMAS:
            nova, motivo = _caixa(corrigido, FORMAS[minuscula]), "forma fixa"
        elif minuscula == "reis" and (anterior in NUMERAIS or anterior.isdigit()):
            nova, motivo = _caixa(corrigido, "réis"), "moeda"
        elif (preterito := v2._preterito(minuscula, originais[indice - 1] if indice else "")) is not None:
            if futuro[indice] and minuscula.endswith("rão"):
                atual = v2._palavra_atual(minuscula)
                nova, motivo = _caixa(corrigido, atual[0] if atual else minuscula), "futuro"
            else:
                nova, motivo = _caixa(corrigido, preterito), "pretérito em -am"
        else:
            nome = indice > 0 and corrigido[:1].isupper() and not frase
            forma, motivo_v1 = v2.modernizar_palavra(corrigido, nome)
            if forma is not None:
                nova, motivo = _caixa(corrigido, forma), motivo_v1
            elif corrigido.isalpha() and not nome:
                separada = None if corrigido[:1].isupper() else _separar_grudada(minuscula)
                rara = _rara_para_comum(minuscula)
                if separada:
                    nova, motivo = separada, "palavras separadas"
                elif rara:
                    nova, motivo = _caixa(corrigido, rara), "grafia atualizada"
        atual = nova if nova is not None else corrigido
        papel = atual.lower() in PAPEIS and anterior in ANTES_DE_PAPEL and (indice > 0 or continua)
        if atual[:1].isupper() and len(atual) > 1 and minuscula not in v2.NOMES and (
                (atual.lower() in v2.GRAMATICAIS and not frase) or papel):
            atual, motivo = atual.lower(), motivo or "minúscula"
        elif corrigido != nucleo and nova is None:
            motivo = "minúscula"
        if atual != nucleo:
            trocas.append({"de": nucleo, "para": atual, "motivo": motivo})
        saida.append(antes + atual + depois)
    return " ".join(saida), trocas


def modernizar_linhas(textos):
    """Como as versões anteriores: cada linha com as vizinhas como contexto do futuro."""
    partidas = [bool(atual and seguinte and palavra_partida(atual, seguinte))
                for atual, seguinte in zip(textos, list(textos[1:]) + [None])]
    saida = []
    for indice, texto in enumerate(textos):
        if not texto:
            saida.append("")
            continue
        inicio = indice > 0 and partidas[indice - 1]
        seguinte = textos[indice + 1] if indice + 1 < len(textos) else None
        limpo = limpar_hifen(texto, seguinte)
        saida.append(modernizar_linha(limpo, partida_no_inicio=inicio, partida_no_fim=partidas[indice],
                                      contexto_antes=" ".join(textos[max(0, indice - 3):indice]),
                                      contexto_depois=" ".join(textos[indice + 1:indice + 4]))[0])
    return saida
