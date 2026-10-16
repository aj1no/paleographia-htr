"""Build a provisional visual repertoire from explicitly selected source boxes."""
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from paleographia.data import bbox_valid
from paleographia.io import safe_path, sha256


SOURCE = "data/raw/import_20261015/6e82cef18b04_198b675a9b65d183.jpg"
CHECKSUM = "413d1502555f62d45ef50cc9af5d0fb7df0ed55bf9652157f0fa874b2006a1ad"
REFERENCE = "data/raw/import_20261015/6e82cef18b04_094cbf86c7ec88ea.pdf"
# Boxes are selected by visual inspection in original image coordinates.
# Each record is an assisted reading hypothesis, not a validated training label.
EXAMPLES = [
    ("hum", 17, (240, 916, 333, 978), "hum", "um", "letra em palavra", ["h", "u", "m"],
     "Observe a haste inicial e a sequência de arcos. A edição moderniza a palavra para ‘um’; preserve ‘hum’ se essa grafia for confirmada na imagem."),
    ("projecto", 17, (330, 905, 485, 998), "Projecto", "Projeto", "letra em palavra", ["P", "r", "j", "t"],
     "Compare a inicial com o P de ‘Posturas’. A leitura ‘Projecto’, incluindo o c, continua em conferência; a edição traz ‘Projeto’."),
    ("posturas", 17, (505, 916, 665, 978), "Posturas", "Posturas", "letra em palavra", ["P", "s", "t", "r"],
     "Use a inicial alta e os traços internos de s e t como comparações. Uma forma pode variar conforme sua posição e ligação com a letra vizinha."),
    ("treze", 17, (730, 920, 829, 981), "treze", "treze", "letra em palavra", ["t", "r", "z", "e"],
     "Observe o traço alto inicial e compare o t com os exemplos em ‘Posturas’. Não identifique uma palavra apenas pelo traço transversal."),
    ("artigos", 17, (822, 920, 954, 993), "Artigos", "artigos", "letra em palavra", ["A", "r", "t", "g", "s"],
     "Compare a sequência inicial Art com as formas abreviadas de ‘Artigo’. Maiúscula inicial e pontuação permanecem em conferência."),
    ("seguintes", 17, (950, 902, 1087, 991), "seg…", "seguintes", "abreviatura a conferir", ["s", "e", "g"],
     "A edição desenvolve como ‘seguintes’. Há sinais acima da sequência principal; a forma completa da abreviatura e sua representação textual ainda não foram estabelecidas. ‘seg…’ é apenas um rótulo provisório."),
    ("artigo1", 18, (136, 974, 326, 1042), "Art. 1º", "Artigo 1º", "abreviatura", ["A", "r", "t"],
     "Abreviatura correspondente a ‘Artigo’, seguida do número 1. ‘Art. 1º’ é uma representação de trabalho; confira a caixa, o ponto e a forma do ordinal antes de validar."),
    ("ninguem", 18, (315, 945, 499, 1050), "Ninguem", "Ninguém", "letra em palavra", ["N", "g", "u", "m"],
     "Observe a inicial N e o traço descendente no corpo da palavra. O acento não foi fixado na leitura de trabalho; a edição usa a grafia atual."),
    ("offensivas", 18, (821, 965, 1066, 1040), "ofensivas", "ofensivas", "letra em palavra", ["f", "s", "v"],
     "Compare o traço alto de f com o exemplo em ‘defensivas’. A leitura de trabalho usa uma única consoante f; confira a palavra e a pontuação no original."),
    ("defensivas", 19, (190, 1015, 399, 1100), "defensivas", "defensivas", "letra em palavra", ["d", "f", "s", "v"],
     "Compare o f com o exemplo em ‘ofensivas’ e observe as mudanças de forma do s dentro e no final da palavra."),
    ("polvora", 19, (366, 1016, 548, 1093), "polvora", "pólvora", "letra em palavra", ["p", "l", "v", "r"],
     "Observe o p descendente e o l alto. A posição de acentos não foi estabelecida nesta leitura de trabalho."),
    ("chumbo", 19, (549, 1018, 696, 1085), "chumbo", "chumbo", "letra em palavra", ["c", "h", "u", "m", "b"],
     "Use como segundo contexto para h, u e m. As letras estão ligadas; os limites entre elas não foram anotados individualmente."),
    ("artigo2", 23, (137, 1224, 328, 1294), "Art. 2º", "Artigo 2º", "abreviatura", ["A", "r", "t"],
     "Segunda ocorrência da abreviatura de ‘Artigo’, agora seguida do número 2. Compare com o exemplo anterior antes de generalizar a forma."),
]


def materialize_repertoire(manifest_path, root):
    """Recreate missing pixels without changing any human reading or history."""
    root = Path(root).resolve()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    source_path = safe_path(root, manifest["fonte"])
    if sha256(source_path) != manifest["fonte_sha256"]:
        raise ValueError("A imagem fonte diverge do catálogo do repertório.")
    if sha256(safe_path(root, manifest["edicao"])) != manifest["edicao_sha256"]:
        raise ValueError("A edição diverge do catálogo do repertório.")
    planned, existing = [], 0
    with Image.open(source_path) as opened:
        source = opened.convert("RGB")
        for item in manifest["itens"]:
            if not bbox_valid(item["bbox_xyxy"], *source.size):
                raise ValueError("Recorte do repertório fora da imagem fonte.")
            target = safe_path(root, item["imagem"])
            crop = source.crop(item["bbox_xyxy"])
            crop.info.clear()
            stream = io.BytesIO()
            crop.save(stream, format="PNG")
            content = stream.getvalue()
            if hashlib.sha256(content).hexdigest() != item["imagem_sha256"]:
                raise ValueError("Os pixels reconstruídos divergem do recorte catalogado.")
            if target.exists():
                if sha256(target) != item["imagem_sha256"]:
                    raise ValueError("Um recorte existente diverge; ele não foi sobrescrito.")
                existing += 1
            else:
                planned.append((target, content))
    for target, content in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)
    return {"criados": len(planned), "existentes_preservados": existing}


def main():
    parser = argparse.ArgumentParser(description="Preparar os recortes do repertório preservando as confirmações.")
    parser.add_argument("--materialize", action="store_true", help="Reconstruir somente imagens ausentes a partir do catálogo existente.")
    args = parser.parse_args()
    root = Path.cwd()
    destination = root / "data/manifests/repertorio_100r.json"
    if args.materialize:
        result = materialize_repertoire(destination, root)
        entries = json.loads(destination.read_text(encoding="utf-8"))["itens"]
        render_sheet(entries, root, root / "data/processed/repertorio_100r/exemplos_iniciais.png")
        print(json.dumps(result, ensure_ascii=False))
        return
    if destination.exists():
        existing = json.loads(destination.read_text(encoding="utf-8"))
        if any(item.get("revisor") or item.get("validado_em") or item.get("confirmacao_parcial") or item.get("estado") != "aguarda conferência humana"
               for item in existing.get("itens", [])):
            raise ValueError("O repertório tem revisão humana; preserve-a e prepare uma nova versão.")
    if sha256(root / SOURCE) != CHECKSUM:
        raise ValueError("A imagem fonte diverge da fonte inspecionada.")
    out = root / "data/processed/repertorio_100r"
    out.mkdir(parents=True, exist_ok=True)
    pages = [json.loads(row) for row in (root / "data/manifests/edition_1831_pages.jsonl").read_text(encoding="utf-8").splitlines()]
    if pages[2]["source_sha256"] != sha256(root / REFERENCE):
        raise ValueError("A edição de apoio diverge da fonte inspecionada.")
    pointer = json.loads((root / "data/workspace/current.json").read_text())
    state = json.loads((root / "data/workspace/revisions" / (pointer["revision"] + ".json")).read_text(encoding="utf-8"))
    source = Image.open(root / SOURCE).convert("RGB")
    entries = []
    for identifier, order, box, reading, modern, kind, letters, note in EXAMPLES:
        line = next(line for line in state["lines"] if line["page_id"] == "p_1c30bfae3576f7d2" and line["reading_order"] == order)
        crop = source.crop(box)
        crop.info.clear()
        target = out / (identifier + ".png")
        crop.save(target)
        entries.append({"id": identifier, "tipo": kind, "letras": letters,
                        "leitura_provisoria": reading, "forma_na_edicao": modern,
                        "nota": note, "linha_editorial": order, "line_id": line["line_id"],
                        "page_id": line["page_id"], "bbox_xyxy": list(box),
                        "imagem": target.relative_to(root).as_posix(), "imagem_sha256": sha256(target),
                        "contexto": line["crop_image"], "estado": "aguarda conferência humana",
                        "revisor": None, "validado_em": None})
    manifest = {"titulo": "Repertório de letras e abreviaturas · Fólio 100 reto", "versao": 1,
                "aviso": "Leituras assistidas pela edição modernizada. Todos os exemplos aguardam conferência humana e não são referências de treinamento.",
                "metodo": "Recortes dos pixels originais, sem reconstrução ou alteração dos traços. A ampliação na tela apenas facilita a visualização.",
                "fonte": SOURCE, "fonte_sha256": CHECKSUM,
                "edicao": REFERENCE, "edicao_sha256": sha256(root / REFERENCE), "pagina_edicao": 3,
                "creditos_edicao": "Transcrição e edição: Paulo Vicentini (AHMJ). Revisão: Isabella Ferraro e Gilson Santos (AHMJ).",
                "itens": entries}
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_sheet(entries, root, out / "exemplos_iniciais.png")
    print(json.dumps({"exemplos": len(entries), "catalogo": destination.relative_to(root).as_posix()}, ensure_ascii=False))


def render_sheet(entries, root, destination):
    # A small visual sheet for discussion; pixels remain unchanged apart from scale.
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 23) if font_path.exists() else ImageFont.load_default(size=23)
    small = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default(size=18)
    sheet = Image.new("RGB", (1200, 770), "#f5f3ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((22, 14), "Fólio 100 reto · Repertório em conferência", font=font, fill="#173d35")
    draw.text((22, 48), "Leitura apoiada pela edição; grafia e sinais ainda em revisão humana.", font=small, fill="#45534d")
    for i, identifier in enumerate(["hum", "posturas", "offensivas", "defensivas", "artigo1", "seguintes"]):
        entry = next(e for e in entries if e["id"] == identifier)
        x, y = 20 + (i % 2) * 595, 90 + (i // 2) * 223
        draw.rounded_rectangle((x, y, x + 575, y + 207), radius=8, fill="white", outline="#cdd5ce")
        label = entry["leitura_provisoria"] + " · linha " + str(entry["linha_editorial"])
        if entry.get("confirmacao_parcial"):
            label += " · confirmação parcial"
        draw.text((x + 12, y + 10), label, font=font, fill="#173d35")
        pic = Image.open(root / entry["imagem"])
        pic.thumbnail((549, 122), Image.Resampling.LANCZOS) if pic.width > 549 else None
        factor = min(549 / pic.width, 122 / pic.height)
        pic = pic.resize((round(pic.width * factor), round(pic.height * factor)), Image.Resampling.LANCZOS)
        sheet.paste(pic, (x + 12, y + 47))
        draw.text((x + 12, y + 175), "Na edição: " + entry["forma_na_edicao"], font=small, fill="#45534d")
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination)


if __name__ == "__main__":
    main()
