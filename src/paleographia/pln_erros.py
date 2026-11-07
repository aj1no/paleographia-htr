"""PLN depois do reconhecimento: análise linguística dos erros e pós-correção lexical.

Tudo em Python puro, sobre predições e referências já salvas: nenhum reconhecedor roda aqui.

- ``alinhar``: alinhamento de caracteres por distância de edição (Levenshtein) com rastreio.
- ``classificar``: tipo linguístico de cada operação de edição (espaço, pontuação, maiúscula,
  acento/til, grafia histórica, abreviatura, nome próprio, forma da letra).
- ``Vocabulario`` e ``corrigir_linha``: pós-correção de palavras fora do vocabulário histórico por
  dois métodos, (A) Levenshtein e (B) TF-IDF de n-gramas de caracteres com cosseno.

A correção é sempre uma sugestão, guardada à parte da saída bruta e da transcrição humana.
Os limiares abaixo foram fixados antes de olhar o resultado na validação e não são ajustados nela.
"""
import math
import re
import unicodedata
from collections import Counter

# Limiares fixados a priori (não ajustados na validação).
TAMANHO_MINIMO = 3          # palavras menores não são corrigidas: risco alto, ganho pequeno
COSSENO_MINIMO = 0.5        # método B
NGRAMAS = (2, 3)            # método B, com marcadores de borda


def distancia_maxima(tamanho):
    """Método A: até 1 edição em palavras de até 5 letras, até 2 nas maiores."""
    return 1 if tamanho <= 5 else 2


# Pares de letras que alternam na escrita dos séculos XVII-XIX (comparados sem caixa e sem acento).
GRAFIAS_HISTORICAS = {frozenset(p) for p in [("i", "j"), ("u", "v"), ("i", "y"), ("s", "z"), ("c", "s"),
                                             ("ç", "s"), ("ç", "c"), ("s", "x"), ("e", "i"), ("o", "u")]}
SOBRESCRITOS = set("ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ")
TIPOS = ["espaço (palavras coladas ou separadas)", "pontuação", "abreviatura", "maiúscula/minúscula",
         "acento ou til", "grafia histórica", "nome próprio", "forma da letra"]


def normalizar(texto):
    """NFC e espaços simples; preserva caixa, acentos, pontuação e grafia."""
    return " ".join(unicodedata.normalize("NFC", texto or "").split())


def sem_acento(c):
    return "".join(x for x in unicodedata.normalize("NFD", c) if not unicodedata.combining(x))


def alinhar(ref, hyp):
    """Lista de operações (op, char_ref, char_hyp, posição_ref) com custo mínimo de edição.

    op é "=" (acerto), "S" (substituição), "D" (apagado: está na referência, falta na predição)
    ou "I" (inserido: aparece só na predição). O número de S+D+I é a distância usada no CER.
    """
    n, m = len(ref), len(hyp)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]))
    ops, i, j = [], n, m
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            ops.append(("=" if ref[i - 1] == hyp[j - 1] else "S", ref[i - 1], hyp[j - 1], i - 1))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            ops.append(("D", ref[i - 1], "", i - 1))
            i -= 1
        else:
            ops.append(("I", "", hyp[j - 1], i))
            j -= 1
    return ops[::-1]


def _palavra_em(ref, pos):
    """Palavra da referência que contém a posição (ou a palavra seguinte, para inserções)."""
    pos = min(max(pos, 0), max(len(ref) - 1, 0))
    if not ref:
        return "", False
    ini = ref.rfind(" ", 0, pos + 1) + 1
    fim = ref.find(" ", pos)
    palavra = ref[ini:fim if fim >= 0 else len(ref)]
    return palavra.strip(".,;:!?()[]-"), ini == 0


def classificar(op, a, b, ref, pos):
    """Tipo linguístico de uma operação de edição (a = caractere da referência, b = da predição)."""
    if " " in (a, b):
        return TIPOS[0]
    if (a and unicodedata.category(a).startswith("P")) or (b and unicodedata.category(b).startswith("P")):
        return TIPOS[1]
    palavra, inicio_de_linha = _palavra_em(ref, pos)
    if any(c in SOBRESCRITOS for c in palavra) or palavra.endswith("."):
        return TIPOS[2]
    if op == "S":
        if a.lower() == b.lower():
            return TIPOS[3]
        if sem_acento(a) == sem_acento(b):
            return TIPOS[4]
        if sem_acento(a.lower()) == sem_acento(b.lower()):
            return TIPOS[3]
        if frozenset((sem_acento(a.lower()), sem_acento(b.lower()))) in GRAFIAS_HISTORICAS:
            return TIPOS[5]
    if palavra[:1].isupper() and not inicio_de_linha:
        return TIPOS[6]
    return TIPOS[7]


def analisar(pares):
    """pares: lista de (referência, predição). Devolve contagens por tipo e confusões de caracteres."""
    por_tipo, confusoes, total_ref = Counter(), Counter(), 0
    for ref, hyp in pares:
        ref, hyp = normalizar(ref), normalizar(hyp)
        total_ref += len(ref)
        for op, a, b, pos in alinhar(ref, hyp):
            if op == "=":
                continue
            por_tipo[classificar(op, a, b, ref, pos)] += 1
            confusoes[(a or "∅", b or "∅")] += 1
    erros = sum(por_tipo.values())
    return {"caracteres_referencia": total_ref, "erros": erros, "cer": erros / total_ref if total_ref else 0.0,
            "por_tipo": {t: {"erros": por_tipo[t], "parcela_dos_erros": por_tipo[t] / erros if erros else 0.0,
                             "pontos_de_cer": por_tipo[t] / total_ref if total_ref else 0.0} for t in TIPOS},
            "confusoes": confusoes}


# ---------------------------------------------------------------- pós-correção lexical

PALAVRA = re.compile(r"^(\W*)(.*?)(\W*)$", re.UNICODE)


def palavras(texto):
    return [p.lower() for p in re.findall(r"[^\W\d_]+", normalizar(texto))]


def levenshtein(a, b):
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + (ca != cb)))
        anterior = atual
    return anterior[-1]


def _ngramas(palavra):
    marcada = f"<{palavra}>"
    return Counter(marcada[i:i + n] for n in NGRAMAS for i in range(len(marcada) - n + 1))


class Vocabulario:
    """Formas atestadas (em minúsculas) com frequência, e o índice TF-IDF de n-gramas do método B."""

    def __init__(self, textos):
        self.frequencia = Counter(p for t in textos for p in palavras(t))
        formas = list(self.frequencia)
        df = Counter(g for f in formas for g in _ngramas(f))
        self.idf = {g: math.log((1 + len(formas)) / (1 + n)) + 1 for g, n in df.items()}
        self.vetores = {f: self._vetor(f) for f in formas}
        self.por_ngrama = {}
        for f, v in self.vetores.items():
            for g in v:
                self.por_ngrama.setdefault(g, set()).add(f)

    def _vetor(self, palavra):
        v = {g: c * self.idf.get(g, 0.0) for g, c in _ngramas(palavra).items()}
        norma = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {g: x / norma for g, x in v.items() if x}

    def __contains__(self, palavra):
        return palavra.lower() in self.frequencia

    def candidato_levenshtein(self, palavra):
        p = palavra.lower()
        limite = distancia_maxima(len(p))
        melhores = [(levenshtein(p, f), -n, f) for f, n in self.frequencia.items() if abs(len(f) - len(p)) <= limite]
        melhores = [m for m in melhores if m[0] <= limite]
        return min(melhores)[2] if melhores else None

    def candidato_tfidf(self, palavra):
        v = self._vetor(palavra.lower())
        vizinhos = set().union(*(self.por_ngrama.get(g, set()) for g in v)) if v else set()
        pontos = [(sum(x * self.vetores[f].get(g, 0.0) for g, x in v.items()), self.frequencia[f], f) for f in vizinhos]
        pontos = sorted(p for p in pontos if p[0] >= COSSENO_MINIMO)  # ordem fixa para empates
        return max(pontos, key=lambda p: (round(p[0], 9), p[1]))[2] if pontos else None


def _caixa(modelo, forma):
    if len(modelo) > 1 and modelo.isupper():
        return forma.upper()
    return forma[:1].upper() + forma[1:] if modelo[:1].isupper() else forma


def corrigir_linha(texto, vocabulario, metodo):
    """Sugestão de correção da linha (texto bruto intacto) e a lista de trocas feitas."""
    trocas, saida = [], []
    for token in normalizar(texto).split(" "):
        antes, nucleo, depois = PALAVRA.match(token).groups()
        if (len(nucleo) < TAMANHO_MINIMO or not nucleo.isalpha() or nucleo in vocabulario):
            saida.append(token)
            continue
        forma = (vocabulario.candidato_levenshtein if metodo == "A" else vocabulario.candidato_tfidf)(nucleo)
        if forma is None or forma == nucleo.lower():
            saida.append(token)
            continue
        nova = _caixa(nucleo, forma)
        trocas.append({"de": nucleo, "para": nova})
        saida.append(antes + nova + depois)
    return " ".join(saida), trocas
