"""Prepara as linhas para o modelo do zero, só com fontes públicas.

- Inquisição (Portuguese Handwriting 16th-19th c., Zenodo 13986218, CC BY 4.0): todas as linhas
  transcritas do PAGE XML, recortadas pelo polígono da linha com margem. Uma parte dos
  documentos (não das linhas) fica separada como validação interna, usada para escolher o
  checkpoint.
- Traslado de 1767 (Arquivo Histórico de Jundiaí, imagens públicas no Acervo Digital, uso sem fins
  comerciais com crédito): linhas de treino já recortadas no projeto principal.
- Validação de Jundiaí (sessão de 1795, 7 linhas; carta de 1767, 3 linhas): só para medir no fim,
  nunca para escolher checkpoint ou parâmetro.
- O teste reservado (pagamento a Thomas Pardo) não entra em nada, nem como imagem sem texto.

Uso: python preparar_dados.py CAMINHO_DO_PROJETO_PRINCIPAL
"""
import hashlib
import json
import random
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "dados"
ALTURA = 64
LARGURA_MAX = 1600
FRACAO_VAL_INQ = 0.07
SEMENTE = 20261107
PROIBIDO = ("pagamento", "thomas_pardo", "teste_pagamento")

NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}


def nfc(texto):
    return unicodedata.normalize("NFC", " ".join(texto.split()))


def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def documento_inquisicao(nome):
    """Agrupa páginas do mesmo processo para a validação interna não vazar por documento."""
    m = re.search(r"docId_(\d+)", nome)
    if m:
        return "docId_" + m.group(1)
    m = re.search(r"IL-(\d+)-(\d+)", nome)  # PT-TT-TSO-IL-028-00067 e IL-28-67 são o mesmo processo
    if m:
        return f"IL_{int(m.group(1))}_{int(m.group(2))}"
    m = re.search(r"IL_(\d+)", nome)
    if m:
        return f"IL_{int(m.group(1))}"
    return re.split(r"_[mc]\d", re.sub(r"^\d+_", "", nome))[0]


def salvar_linha(img, destino):
    img = img.convert("L")
    w, h = img.size
    nova_w = max(16, min(LARGURA_MAX, round(w * ALTURA / h)))
    img.resize((nova_w, ALTURA), Image.Resampling.LANCZOS).save(destino)
    return nova_w


def inquisicao(projeto, so_paginas=None):
    base = next((projeto / "data/raw/externo/inquisicao_traprinq_zenodo13986218/extraido").rglob("page"))
    pasta_img = base.parent
    saida = SAIDA / "linhas" / "inq"
    saida.mkdir(parents=True, exist_ok=True)
    registros = []
    for xml in sorted(base.glob("*.xml"))[slice(None) if so_paginas is None else so_paginas]:
        imagem = pasta_img / (xml.stem + ".jpg")
        if not imagem.exists():
            continue
        doc = documento_inquisicao(xml.stem)
        pagina = Image.open(imagem)
        W, H = pagina.size
        linhas = []
        for linha in ET.parse(xml).getroot().iter(f"{{{NS['p']}}}TextLine"):
            uni = linha.find("p:TextEquiv/p:Unicode", NS)
            base_l = linha.find("p:Baseline", NS)
            if uni is None or base_l is None or not (uni.text or "").strip():
                continue
            pts = [tuple(map(int, p.split(","))) for p in base_l.get("points").split()]
            linhas.append((linha, nfc(uni.text), pts))
        # Os polígonos do PAGE variam muito de altura entre documentos; a linha de base é estável.
        # A altura do recorte sai do espaçamento entre linhas de base da página.
        medias = sorted(sum(y for _, y in pts) / len(pts) for _, _, pts in linhas)
        difs = sorted(b - a for a, b in zip(medias, medias[1:]) if b - a > 10)
        espaco = min(150, max(25, difs[len(difs) // 2] if difs else 50))
        for linha, texto, pts in linhas:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            caixa = (max(0, x0 - 10), max(0, int(y0 - 0.8 * espaco)), min(W, x1 + 10), min(H, int(y1 + 0.35 * espaco)))
            if caixa[2] - caixa[0] < 24 or caixa[3] - caixa[1] < 12:
                continue
            ident = "inq_" + hashlib.sha1(f"{xml.name}|{linha.get('id')}".encode()).hexdigest()[:16]
            destino = saida / f"{ident}.png"
            largura = salvar_linha(pagina.crop(caixa), destino)
            registros.append({"id": ident, "img": str(destino.relative_to(AQUI)), "texto": texto, "largura": largura,
                              "fonte": "inquisicao_zenodo13986218_cc_by_4_0", "documento": doc,
                              "pagina": xml.stem, "linha_xml": linha.get("id")})
    docs = sorted({r["documento"] for r in registros})
    random.Random(SEMENTE).shuffle(docs)
    alvo = FRACAO_VAL_INQ * len(registros)
    val, n = set(), 0
    for d in docs:
        if n >= alvo:
            break
        val.add(d)
        n += sum(r["documento"] == d for r in registros)
    for r in registros:
        r["split"] = "val_inq" if r["documento"] in val else "treino"
    return registros


def jundiai(projeto):
    saida = SAIDA / "linhas" / "jdi"
    saida.mkdir(parents=True, exist_ok=True)
    pares = json.loads((projeto / "docs/experimentos/ppocrv6_ajuste_fino_20261105/dados/pares_traslado_mais_inquisicao.json")
                       .read_text(encoding="utf-8"))
    fontes = []
    for p in pares:
        if p["document_id"].startswith("externo"):
            continue  # a Inquisição vem inteira do PAGE XML, recortada aqui
        split = "treino" if p["split"] == "train" else "val_jundiai"
        fontes.append((p["crop_image"], p["text"], p["document_id"], split, p["label_source"]))
    carta = projeto / "docs/entregas/continuidade_20261103/avaliacao_linhas_1767/referencias.jsonl"
    for linha in carta.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        if r.get("text_diplomatic"):
            fontes.append((r["crop_image"], r["text_diplomatic"], r["document_id"], "val_jundiai", "human_diplomatic"))
    registros = []
    for img, texto, doc, split, origem in fontes:
        if any(x in (img + doc).lower() for x in PROIBIDO):
            raise SystemExit(f"recusado: {doc} {img} é do teste reservado")
        caminho = projeto / img
        ident = "jdi_" + hashlib.sha1(img.encode()).hexdigest()[:16]
        destino = saida / f"{ident}.png"
        largura = salvar_linha(Image.open(caminho), destino)
        registros.append({"id": ident, "img": str(destino.relative_to(AQUI)), "texto": nfc(texto), "largura": largura,
                          "fonte": "jundiai_ahmj_uso_nao_comercial", "documento": doc, "split": split,
                          "rotulo": origem, "sha256_recorte": sha256(caminho)})
    return registros


def main():
    projeto = Path(sys.argv[1]).resolve()
    registros = inquisicao(projeto) + jundiai(projeto)
    assert not any(any(x in json.dumps(r).lower() for x in PROIBIDO) for r in registros)
    treino = [r for r in registros if r["split"] == "treino"]
    alfabeto = sorted({c for r in treino for c in r["texto"]})
    with (SAIDA / "manifesto.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (SAIDA / "alfabeto.json").write_text(json.dumps(alfabeto, ensure_ascii=False), encoding="utf-8")
    resumo = {}
    for r in registros:
        chave = f"{r['split']}/{r['fonte']}"
        resumo[chave] = resumo.get(chave, 0) + 1
    resumo["alfabeto"] = len(alfabeto)
    resumo["documentos_val_inq"] = len({r["documento"] for r in registros if r["split"] == "val_inq"})
    (SAIDA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
