"""Glossário histórico: notas numeradas (¹²³) para palavras antigas da leitura modernizada.

Os verbetes ficam em ``docs/glossario/glossario.json``, editável pela equipe. Cada palavra da
leitura modernizada cujas formas batem com um verbete (sem diferença de acento ou maiúscula)
recebe o número da nota; a mesma palavra repetida no fólio usa o mesmo número. O arquivo é relido
quando muda, então uma nota nova aparece na aba Textos sem reiniciar o app.
"""
import json
from pathlib import Path

from .duvidas import PALAVRA
from .modernizacao import nfc, sem_acento

ARQUIVO = Path(__file__).resolve().parents[2] / "docs/glossario/glossario.json"
SITUACOES = {"hipotese", "rascunho", "conferida"}
_cache = {}


def chave(palavra):
    return sem_acento(nfc(palavra).lower())


def verbetes(arquivo=ARQUIVO):
    """Verbetes indexados pelas formas: ``{forma: verbete}``. Arquivo ausente: glossário vazio."""
    arquivo = Path(arquivo)
    try:
        marca = arquivo.stat().st_mtime_ns
    except OSError:
        return {}
    if _cache.get(arquivo, (None,))[0] != marca:
        indice = {}
        for verbete in json.loads(arquivo.read_text(encoding="utf-8")).get("verbetes", []):
            if verbete.get("situacao") not in SITUACOES:
                raise ValueError(f"situação inválida no verbete {verbete.get('termo')!r}")
            for forma in verbete["formas"]:
                indice[chave(forma)] = verbete
        _cache[arquivo] = (marca, indice)
    return _cache[arquivo][1]


class Notas:
    """Numera as notas de um fólio na ordem em que os termos aparecem."""

    def __init__(self, indice):
        self.indice, self.numeros, self.lista = indice, {}, []

    def marcar(self, texto):
        """Trechos ``[início, fim, número]`` das palavras de ``texto`` que estão no glossário."""
        saida = []
        for achada in PALAVRA.finditer(texto or ""):
            verbete = self.indice.get(chave(achada.group()))
            if verbete is None:
                continue
            termo = verbete["termo"]
            if termo not in self.numeros:
                self.numeros[termo] = len(self.lista) + 1
                self.lista.append({"numero": self.numeros[termo], "termo": termo, "nota": verbete["nota"],
                                   "fontes": verbete.get("fontes", []), "situacao": verbete["situacao"]})
            saida.append([achada.start(), achada.end(), self.numeros[termo]])
        return saida

    def conferida(self, palavra):
        verbete = self.indice.get(chave(palavra))
        return bool(verbete and verbete["situacao"] == "conferida")
