"""Texto validado de um fólio para leitura: diplomático e modernizado, em texto corrido.

Só entram linhas validadas por um revisor; linhas pendentes, rascunhos humanos e sugestões
do modelo nunca aparecem (viram lacunas marcadas). As linhas validadas consecutivas são
unidas em texto corrido, juntando a palavra partida na quebra de linha (``aos ca`` |
``torze`` → ``aos catorze``) com o mesmo detector do modernizador, e a leitura modernizada
é feita sobre o texto já unido, com a versão 3 (``modernizacao_v3``). O módulo ``modernizacao``
é só usado, não alterado.
Não há pós-correção lexical aqui: a linha validada já é a correção humana. As palavras da
leitura modernizada que ficam fora do dicionário atual vêm marcadas (``duvidas``) para conferência,
e as que estão no glossário histórico recebem o número da nota (``notas``), listada no fim do fólio.
"""
from .duvidas import duvidas, duvidas_por_linha, localizar
from .glossario import Notas, verbetes
from .modernizacao import nfc
from .modernizacao_v3 import limpar_hifen, modernizar_linha, modernizar_linhas, palavra_partida

QUEBRA = ("-", "=", "¬")


def juntar(linhas):
    """Une linhas diplomáticas consecutivas em texto corrido, juntando palavras partidas.

    Hífen de enchimento (``de -`` | ``multa``) e hífen antes de maiúscula (``de-`` | ``Paz``) somem.
    """
    corrido = ""
    for indice, linha in enumerate(linhas):
        atual = nfc(linha).strip()
        if not corrido:
            corrido = atual
        elif palavra_partida(linhas[indice - 1], linha):
            anterior = corrido.rstrip()
            corrido = (anterior[:-1].rstrip() if anterior.endswith(QUEBRA) else anterior) + atual
        else:
            corrido = f"{limpar_hifen(corrido, linha)} {atual}"
    return corrido


def _sem_conferidas(marcas, texto, notas):
    """Palavra com verbete conferido no glossário deixa de ser dúvida: já está explicada."""
    return [m for m in marcas if not notas.conferida(texto[m[0]:m[1]])]


def _bloco(linhas, posicao, notas):
    textos = [nfc(l["text_diplomatic"]).strip() for l in linhas]
    automaticas = modernizar_linhas(textos)
    modernas = [(l.get("text_modernized") or "").strip() or a for l, a in zip(linhas, automaticas)]
    corrido = juntar(textos)
    moderno = modernizar_linha(corrido)[0]
    notas_do_texto = notas.marcar(moderno)  # numera na ordem da leitura corrida
    return {"tipo": "texto", "regiao": linhas[0]["region_id"],
            "linhas": [{"line_id": l["line_id"], "numero": posicao[l["line_id"]], "diplomatica": t,
                        "modernizada": m, "duvidas": _sem_conferidas(d, m, notas), "notas": notas.marcar(m),
                        "fonte_moderna": "edicao" if (l.get("text_modernized") or "").strip() else "automatica",
                        "revisor": l.get("reviewer")}
                       for l, t, m, d in zip(linhas, textos, modernas, duvidas_por_linha(textos, modernas))],
            "diplomatica": corrido, "modernizada": moderno, "notas": notas_do_texto,
            "duvidas": localizar(_sem_conferidas(duvidas(moderno), moderno, notas), moderno,
                                 [(posicao[l["line_id"]], m) for l, m in zip(linhas, modernas)])}


def textos_validados(page, lines, glossario=None):
    linhas = sorted((l for l in lines if l["page_id"] == page["page_id"] and l["review_status"] != "rejected"),
                    key=lambda l: (l["reading_order"], str(l["region_id"])))
    posicao = {l["line_id"]: i + 1 for i, l in enumerate(linhas)}
    validada = lambda l: l["review_status"] == "validated" and (l.get("text_diplomatic") or "").strip()  # noqa: E731
    partes = {"corpo": [], "margem": []}
    notas = Notas(verbetes() if glossario is None else glossario)
    for nome, grupo in (("corpo", [l for l in linhas if l["region_id"] != "margem"]),
                        ("margem", [l for l in linhas if l["region_id"] == "margem"])):
        corrente = []
        for linha in grupo:
            if validada(linha):
                corrente.append(linha)
                continue
            if corrente:
                partes[nome].append(_bloco(corrente, posicao, notas))
                corrente = []
            if partes[nome] and partes[nome][-1]["tipo"] == "lacuna":
                partes[nome][-1]["numeros"].append(posicao[linha["line_id"]])
            else:
                partes[nome].append({"tipo": "lacuna", "numeros": [posicao[linha["line_id"]]]})
        if corrente:
            partes[nome].append(_bloco(corrente, posicao, notas))
    return {"page_id": page["page_id"], "folio": page.get("folio_id"), "documento": page.get("document_id"),
            "imagem": page.get("original_name"), "creditos": page.get("credits"), "fonte": page.get("source_url"),
            "total": len(linhas), "validadas": sum(1 for l in linhas if validada(l)),
            "corpo": partes["corpo"], "margem": partes["margem"], "notas": notas.lista}
