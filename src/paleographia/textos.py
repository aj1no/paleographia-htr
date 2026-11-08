"""Texto validado de um fólio para leitura: diplomático e modernizado, em texto corrido.

Só entram linhas validadas por um revisor; linhas pendentes, rascunhos humanos e sugestões
do modelo nunca aparecem (viram lacunas marcadas). As linhas validadas consecutivas são
unidas em texto corrido, juntando a palavra partida na quebra de linha (``aos ca`` |
``torze`` → ``aos catorze``) com o mesmo detector do modernizador, e a leitura modernizada
é feita sobre o texto já unido. O módulo ``modernizacao`` é só usado, não alterado.
Não há pós-correção lexical aqui: a linha validada já é a correção humana.
"""
from .modernizacao import modernizar_linha, modernizar_linhas, nfc, palavra_partida

QUEBRA = ("-", "=", "¬")


def juntar(linhas):
    """Une linhas diplomáticas consecutivas em texto corrido, juntando palavras partidas."""
    corrido = ""
    for indice, linha in enumerate(linhas):
        atual = nfc(linha).strip()
        if not corrido:
            corrido = atual
        elif palavra_partida(linhas[indice - 1], linha):
            anterior = corrido.rstrip()
            corrido = (anterior[:-1] if anterior.endswith(QUEBRA) else anterior) + atual
        else:
            corrido = f"{corrido} {atual}"
    return corrido


def _bloco(linhas, posicao):
    textos = [nfc(l["text_diplomatic"]).strip() for l in linhas]
    automaticas = modernizar_linhas(textos)
    corrido = juntar(textos)
    return {"tipo": "texto", "regiao": linhas[0]["region_id"],
            "linhas": [{"line_id": l["line_id"], "numero": posicao[l["line_id"]], "diplomatica": t,
                        "modernizada": (l.get("text_modernized") or "").strip() or a,
                        "fonte_moderna": "edicao" if (l.get("text_modernized") or "").strip() else "automatica",
                        "revisor": l.get("reviewer")}
                       for l, t, a in zip(linhas, textos, automaticas)],
            "diplomatica": corrido, "modernizada": modernizar_linha(corrido)[0]}


def textos_validados(page, lines):
    linhas = sorted((l for l in lines if l["page_id"] == page["page_id"] and l["review_status"] != "rejected"),
                    key=lambda l: (l["reading_order"], str(l["region_id"])))
    posicao = {l["line_id"]: i + 1 for i, l in enumerate(linhas)}
    validada = lambda l: l["review_status"] == "validated" and (l.get("text_diplomatic") or "").strip()  # noqa: E731
    partes = {"corpo": [], "margem": []}
    for nome, grupo in (("corpo", [l for l in linhas if l["region_id"] != "margem"]),
                        ("margem", [l for l in linhas if l["region_id"] == "margem"])):
        corrente = []
        for linha in grupo:
            if validada(linha):
                corrente.append(linha)
                continue
            if corrente:
                partes[nome].append(_bloco(corrente, posicao))
                corrente = []
            if partes[nome] and partes[nome][-1]["tipo"] == "lacuna":
                partes[nome][-1]["numeros"].append(posicao[linha["line_id"]])
            else:
                partes[nome].append({"tipo": "lacuna", "numeros": [posicao[linha["line_id"]]]})
        if corrente:
            partes[nome].append(_bloco(corrente, posicao))
    return {"page_id": page["page_id"], "folio": page.get("folio_id"), "documento": page.get("document_id"),
            "imagem": page.get("original_name"), "creditos": page.get("credits"), "fonte": page.get("source_url"),
            "total": len(linhas), "validadas": sum(1 for l in linhas if validada(l)),
            "corpo": partes["corpo"], "margem": partes["margem"]}
