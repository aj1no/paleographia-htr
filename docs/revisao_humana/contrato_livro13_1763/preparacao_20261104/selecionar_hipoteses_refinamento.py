"""Seleciona uma hipótese do OCR e separa candidatos a pseudorrótulo.

Execute a partir da raiz do projeto, após gerar as variantes e rodar o OCR.
O texto da edição só é carregado após a seleção visual.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

from paleographia.io import read_jsonl, sha256, write_json
from paleographia.lexicon import distance, nfc


PREP = Path("docs/revisao_humana/contrato_livro13_1763/preparacao_20261104")
PILOT = Path("output/curadoria_contrato_livro13_1763/piloto_pagina_05")
REFINEMENT = PILOT / "diagnostico_refinamento_01"
VARIANT_COUNT = 6
MIN_EXACT_VOTES = 4


def hypotheses(folder):
    entries = read_jsonl(folder / "entradas.jsonl")
    predictions = read_jsonl(folder / "predictions.jsonl")
    for entry, prediction in zip(entries, predictions, strict=True):
        if entry["line_id"] != prediction["line_id"] or entry["crop_image"] != prediction["crop_image"]:
            raise ValueError("A previsão diverge da entrada registrada.")
        if prediction["status"] != "ok" or prediction["possible_truncation"]:
            raise ValueError("Execução incompleta. Verifique as previsões antes de comparar.")
        if entry["input_sha256"] != sha256(entry["crop_image"]):
            raise ValueError("Imagem de entrada alterada.")
        yield {
            "line": entry.get("pilot_label", "A"),
            "variant": entry["diagnostic_variant"],
            "image": entry["crop_image"],
            "image_sha256": entry["input_sha256"],
            "source_sha256": entry["source_sha256"],
            "execution_id": prediction["execution_id"],
            "model_sha256": prediction["model"]["sha256"],
            "docker_image_id": prediction["model"]["docker_image_id"],
            "text_raw": prediction["text_raw"],
        }


def normalized(text):
    return " ".join(nfc(text).split())


def select(variants):
    texts = [normalized(variant["text_raw"]) for variant in variants]
    if len(texts) != VARIANT_COUNT or len({variant["variant"] for variant in variants}) != VARIANT_COUNT:
        raise ValueError("Cada linha deve conter a saída anterior e as cinco novas variantes.")
    # Empates preservam a ordem de entrada, com a leitura anterior em primeiro lugar.
    selected = min(
        (index for index, text in enumerate(texts) if text),
        key=lambda index: sum(distance(texts[index], other) for other in texts),
        default=None,
    )
    votes = Counter(text for text in texts if text)
    exact_votes = votes[texts[selected]] if selected is not None else 0
    return {
        "hypotheses": variants,
        "selected_variant": variants[selected]["variant"] if selected is not None else None,
        "selected_text_raw": variants[selected]["text_raw"] if selected is not None else None,
        "exact_votes": exact_votes,
        "pseudolabel_candidate_for_review": exact_votes >= MIN_EXACT_VOTES,
    }


def run():
    folders = [
        PILOT / "diagnostico_linha_a_retificada_01/complemento_textura",
        PILOT / "diagnostico_linhas_bcd_01",
        REFINEMENT,
    ]
    by_line = defaultdict(list)
    for folder in folders:
        for hypothesis in hypotheses(folder):
            if folder == REFINEMENT or hypothesis["variant"] == "antitrama_inteira":
                by_line[hypothesis["line"]].append(hypothesis)
    if set(by_line) != set("ABCD"):
        raise ValueError("Esperadas exatamente as quatro linhas do piloto.")
    lines = {label: select(variants) for label, variants in by_line.items()}
    identities = {
        (h["model_sha256"], h["docker_image_id"], h["source_sha256"])
        for variants in by_line.values() for h in variants
    }
    if len(identities) != 1:
        raise ValueError("A comparação exige os mesmos pesos, ambiente e imagem de origem.")
    visual_path = REFINEMENT / "selecao_visual.json"
    write_json(visual_path, lines)

    # Somente a análise posterior tem acesso à transcrição modernizada.
    editorial = json.loads((PREP / "diagnostico_ppocrv6_linhas_bcd.json").read_bytes())
    for label, prior in editorial["lines"].items():
        reference = prior["editorial_excerpt"]
        lines[label]["editorial_excerpt"] = reference
        reference_key = normalized(reference).casefold()
        lines[label]["editorial_character_edits"] = {
            h["variant"]: distance(normalized(h["text_raw"]).casefold(), reference_key)
            for h in lines[label]["hypotheses"]
        }
    write_json(PREP / "diagnostico_ppocrv6_refinamento.json", {
        "document_id": editorial["document_id"],
        "pdf_page": editorial["pdf_page"],
        "model": editorial["model"],
        "method": "Menor soma de distâncias de edição entre hipóteses. Empates preservam a ordem, começando pela variante anterior. A saída escolhida é mantida na forma bruta.",
        "min_exact_votes": MIN_EXACT_VOTES,
        "variants_per_line": VARIANT_COUNT,
        "selection_before_editorial_comparison": visual_path.as_posix(),
        "selection_sha256": sha256(visual_path),
        "input_artifacts": {
            path.as_posix(): sha256(path)
            for folder in folders
            for path in (folder / "entradas.jsonl", folder / "predictions.jsonl", folder / "tratamentos.json")
            if path.is_file()
        },
        "editorial_note": "Distância exploratória à edição modernizada apenas para B, C e D. A linha A tem palavra dividida na quebra da linha física e trecho editorial ilegível. Nenhuma distância constitui CER diplomático.",
        "lines": lines,
        "training_executed": False,
        "scientific_split": None,
    })
    for label, line in lines.items():
        print(label, line["selected_variant"], line["exact_votes"],
              repr(line["selected_text_raw"]), line.get("editorial_character_edits"))


if __name__ == "__main__":
    run()
