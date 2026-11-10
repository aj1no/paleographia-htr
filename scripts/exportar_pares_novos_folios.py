"""Monta os pares de treino do ajustado C: os do A (Traslado) + linhas validadas dos fólios novos.

Uso, na raiz do projeto:  python scripts/exportar_pares_novos_folios.py [--gravar]

Sem ``--gravar`` só mostra as contagens. Com ``--gravar`` escreve
``docs/experimentos/ppocrv6_ajustado_C/dados/pares_C.json``.

Desde 10/11 os fólios em curadoria moram na aplicação oficial (a da apresentação,
``data/demo_apresentacao``); a lista deles está em ``data/demo_apresentacao/curadoria.json``.
Entram só linhas desses fólios com ``review_status = validated``, revisor
identificado, texto diplomático e sem motivo de exclusão (espaços duplos viram um só). Sai toda linha do contrato do livro 13
que tenha 6 palavras seguidas em comum com a referência congelada do contrato do livro 12 (teste
reservado). A validação continua sendo as 7 linhas de 1795, as mesmas do A e do B.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WORKSPACE = RAIZ / "data/demo_apresentacao/workspace"
CURADORIA = RAIZ / "data/demo_apresentacao/curadoria.json"
PARES_A = RAIZ / "docs/experimentos/ppocrv6_ajuste_fino_20261105/dados/pares_filtrados.json"
REFERENCIA_TESTE = RAIZ / "docs/revisao_humana/teste_reservado_congelado_20261109/referencia.jsonl"
SAIDA = RAIZ / "docs/experimentos/ppocrv6_ajustado_C/dados/pares_C.json"
PROIBIDOS = {"pagamento_thomas_pardo", "contrato_livro12_1763", "sessao_1795"}
N = 6


def palavras(texto):
    return re.findall(r"[a-zà-ÿ]+", unicodedata.normalize("NFC", texto or "").lower())


def ngramas(texto):
    p = palavras(texto)
    return {tuple(p[i:i + N]) for i in range(len(p) - N + 1)}


def linhas_validadas():
    atual = json.loads((WORKSPACE / "current.json").read_text(encoding="utf-8"))["revision"]
    estado = json.loads((WORKSPACE / "revisions" / f"{atual}.json").read_text(encoding="utf-8"))
    em_curadoria = set(json.loads(CURADORIA.read_text(encoding="utf-8"))["page_ids"])
    paginas = {p["page_id"]: p for p in estado["pages"]}
    return atual, [(l, paginas[l["page_id"]]) for l in estado["lines"]
                   if l["page_id"] in em_curadoria and l["review_status"] == "validated" and (l.get("reviewer") or "").strip()
                   and (l.get("text_diplomatic") or "").strip() and not l.get("exclusion_reason")]


def main(gravar=False):
    teste = set()
    for linha in REFERENCIA_TESTE.read_text(encoding="utf-8").splitlines():
        registro = json.loads(linha)
        if registro["document_id"] == "contrato_livro12_1763":
            teste |= ngramas(registro["text_diplomatic"])
    revisao, validadas = linhas_validadas()
    novos, retiradas = [], []
    for linha, pagina in validadas:
        assert linha["document_id"] not in PROIBIDOS, linha["line_id"]
        texto = " ".join(unicodedata.normalize("NFC", linha["text_diplomatic"]).split())  # junta espaços duplos
        if linha["document_id"] == "contrato_livro13_1763" and ngramas(texto) & teste:
            retiradas.append(texto)
            continue
        novos.append({"crop_image": linha["crop_image"], "text": texto, "document_id": linha["document_id"],
                      "folio": pagina["folio_id"], "split": "train", "label_source": "human_diplomatic_assisted",
                      "reviewer": linha["reviewer"], "line_id": linha["line_id"], "augment": 1})
    pares = json.loads(PARES_A.read_text(encoding="utf-8")) + novos
    por_documento = {}
    for par in novos:
        por_documento[par["document_id"]] = por_documento.get(par["document_id"], 0) + 1
    print(f"revisão {revisao}: {len(novos)} linhas novas {por_documento}; {len(retiradas)} retiradas por repetir o livro 12")
    print(f"total: {sum(p['split'] == 'train' for p in pares)} de treino, {sum(p['split'] == 'validation' for p in pares)} de validação")
    if gravar:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(pares, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("gravado:", SAIDA.relative_to(RAIZ))
    return pares


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--gravar" in sys.argv)
