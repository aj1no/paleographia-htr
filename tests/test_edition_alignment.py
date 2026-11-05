"""Synthetic checks for edition-to-crop alignment and blla crop helpers (no Docker)."""
from PIL import Image

from paleographia.blla_segmentation import ordered_lines, polygon_crop
from paleographia.edition_alignment import align, cer, split_by_folio


def test_split_by_folio_uses_recto_and_verso_markers():
    text = ["Cabeçalho", "269", "linha a", "linha b", "269/Verso.", "linha c", "", "270", "linha d"]
    folios = split_by_folio(text)
    assert folios == {"_antes": ["Cabeçalho"], "269r": ["linha a", "linha b"],
                      "269v": ["linha c"], "270r": ["linha d"]}


def test_alignment_skips_margins_and_missing_lines_and_keeps_edition_label():
    edition = ["Aos vinte e cinco dias do mes", "de junho de mil sete centos", "noventa e cinco annos"]
    guide = ["4000", "Aos vinte ecenco dia domes", "de Iunho demil sette centos", "rubrica", "noventa ainco annos"]
    pairs = align(edition, guide)
    assert [(i, j) for i, j, _ in pairs] == [(1, 0), (2, 1), (4, 2)]
    assert all(c <= 0.45 for _, _, c in pairs)


def test_alignment_drops_pairs_whose_guide_is_too_far():
    pairs = align(["Senhora do Desterro de Jundiahy"], ["xxxxxxxxxxxxqqqqqqqq"])
    assert pairs == []
    assert cer("abc", "abc") == 0


def test_ordered_lines_follows_kraken_order_and_polygon_crop_masks_outside():
    lines = [{"id": "b", "baseline": [[0, 40], [10, 40]], "boundary": [[0, 30], [10, 30], [10, 50], [0, 50]]},
             {"id": "a", "baseline": [[0, 10], [10, 10]], "boundary": [[0, 0], [10, 0], [10, 20], [0, 20]]}]
    assert [l["id"] for l in ordered_lines({"lines": lines, "line_orders": [["a", "b"]]})] == ["a", "b"]
    assert [l["id"] for l in ordered_lines({"lines": lines})] == ["a", "b"]
    image = Image.new("RGB", (100, 60), (240, 230, 210))
    image.paste((0, 0, 0), (20, 20, 30, 30))   # ink inside the polygon
    image.paste((0, 0, 0), (80, 20, 90, 30))   # ink outside the polygon
    box, crop = polygon_crop(image, [(10, 10), (50, 10), (50, 40), (10, 40)], pad=40, grow=0)
    assert box[0] == 0 and box[2] == 91
    assert crop.getpixel((25 - box[0], 25 - box[1])) == (0, 0, 0)
    assert crop.getpixel((85 - box[0], 25 - box[1])) == (240, 230, 210)


def test_page_xml_import_reads_lines_and_skips_unusable(tmp_path):
    from paleographia.page_xml_import import import_pairs, read_page_xml
    ns = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    def line(i, y, text, custom=""):
        return (f'<TextLine id="l{i}" custom="{custom}"><Coords points="10,{y} 190,{y} 190,{y+20} 10,{y+20}"/>'
                f'<TextEquiv><Unicode>{text}</Unicode></TextEquiv></TextLine>')
    body = line(1, 10, "q̄ cre ensina") + line(2, 40, "palavra??") + line(3, 70, "") + line(4, 100, "texto", "unclear {offset:0;}")
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages/p.xml").write_text(f'<PcGts xmlns="{ns}"><Page imageFilename="p.jpg" imageWidth="200" '
                                          f'imageHeight="140"><TextRegion id="r">{body}</TextRegion></Page></PcGts>', encoding="utf-8")
    Image.new("RGB", (200, 140), (230, 220, 200)).save(tmp_path / "pages/p.jpg")
    name, lines = read_page_xml(tmp_path / "pages/p.xml")
    assert name == "p.jpg" and [t for _, _, t, _ in lines][0] == "q̄ cre ensina"
    pairs, skipped = import_pairs(tmp_path / "pages", tmp_path / "pages", tmp_path / "out", tmp_path, per_page=5)
    assert [p["text"] for p in pairs] == ["q̄ cre ensina"]
    assert skipped == {"duvida_marcada": 1, "vazia": 1, "unclear": 1}
    import unicodedata
    no_macron = set(unicodedata.normalize("NFD", "q cre ensina"))
    _, skipped = import_pairs(tmp_path / "pages", tmp_path / "pages", tmp_path / "out2", tmp_path, alphabet=no_macron)
    assert skipped["caractere_fora_do_alfabeto"] == 1
