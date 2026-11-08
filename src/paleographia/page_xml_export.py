"""Exporta um fólio em PAGE XML (2019), o formato de eScriptorium e Transkribus.

Cada região do fólio vira um TextRegion e cada linha não rejeitada, um TextLine com as
coordenadas do recorte (polígono quando existir, senão o retângulo) e a transcrição
paleográfica em TextEquiv. O estado da revisão vai no atributo ``custom``, para que
quem importar saiba o que já foi validado. A saída é lida por ``page_xml_import``.
"""
import xml.etree.ElementTree as ET

from .io import now

NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
SCHEMA = NS + " https://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"


def _points(line):
    polygon = line.get("polygon")
    if polygon:
        return " ".join(f"{int(x)},{int(y)}" for x, y in polygon)
    x1, y1, x2, y2 = line["bbox_xyxy"]
    return f"{x1},{y1} {x2},{y1} {x2},{y2} {x1},{y2}"


def _custom_value(value):
    # PAGE custom: "chave {prop:valor;}"; ponto e vírgula e chaves quebrariam a sintaxe.
    return str(value).replace(";", ",").replace("{", "(").replace("}", ")")


def page_xml(page, lines):
    ET.register_namespace("", NS)
    q = lambda tag: f"{{{NS}}}{tag}"  # noqa: E731
    root = ET.Element(q("PcGts"), {"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": SCHEMA})
    meta = ET.SubElement(root, q("Metadata"))
    ET.SubElement(meta, q("Creator")).text = "PaleographIA"
    stamp = now()
    ET.SubElement(meta, q("Created")).text = stamp
    ET.SubElement(meta, q("LastChange")).text = stamp
    ET.SubElement(meta, q("Comments")).text = ("Transcrição paleográfica (diplomática) da equipe; "
                                                "linhas pendentes não são referência validada.")
    node = ET.SubElement(root, q("Page"), {"imageFilename": page["original_name"],
                                           "imageWidth": str(page["width"]), "imageHeight": str(page["height"])})
    kept = sorted((l for l in lines if l["page_id"] == page["page_id"] and l["review_status"] != "rejected"),
                  key=lambda l: (l["reading_order"], str(l["region_id"])))
    regions = []
    for line in kept:
        if line["region_id"] not in regions:
            regions.append(line["region_id"])
    order = ET.SubElement(ET.SubElement(node, q("ReadingOrder")), q("OrderedGroup"), {"id": "ordem"})
    for index, region in enumerate(regions):
        ET.SubElement(order, q("RegionRefIndexed"), {"index": str(index), "regionRef": f"r_{region}"})
    for index, region in enumerate(regions):
        members = [l for l in kept if l["region_id"] == region]
        box = [min(l["bbox_xyxy"][0] for l in members), min(l["bbox_xyxy"][1] for l in members),
               max(l["bbox_xyxy"][2] for l in members), max(l["bbox_xyxy"][3] for l in members)]
        element = ET.SubElement(node, q("TextRegion"), {"id": f"r_{region}", "custom": f"readingOrder {{index:{index};}}"})
        ET.SubElement(element, q("Coords"), {"points": _points({"bbox_xyxy": box})})
        for position, line in enumerate(members):
            status = f"paleographia {{status:{line['review_status']};"
            if line.get("reviewer"):
                status += f"reviewer:{_custom_value(line['reviewer'])};"
            status += "}"
            text_line = ET.SubElement(element, q("TextLine"), {"id": line["line_id"],
                                                              "custom": f"readingOrder {{index:{position};}} {status}"})
            ET.SubElement(text_line, q("Coords"), {"points": _points(line)})
            equiv = ET.SubElement(text_line, q("TextEquiv"))
            ET.SubElement(equiv, q("Unicode")).text = line.get("text_diplomatic") or ""
        region_equiv = ET.SubElement(element, q("TextEquiv"))
        ET.SubElement(region_equiv, q("Unicode")).text = "\n".join(l.get("text_diplomatic") or "" for l in members)
    ET.indent(root)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")
