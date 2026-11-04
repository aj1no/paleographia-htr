"""Executa o ketos pretrain 7.1 com texto vazio em Arrow."""
from importlib.metadata import version
from pathlib import Path
import sys

import pyarrow as pa
from kraken.ketos import cli
from kraken.lib.dataset.recognition import ArrowIPCRecognitionDataset


if version("kraken") != "7.1" or "pretrain" not in sys.argv:
    raise RuntimeError("Este ensaio é restrito ao pré-treinamento do Kraken 7.1.")
for split, expected_count in (("train", 67), ("validation", 4)):
    with pa.memory_map(str(Path("/work") / f"{split}.arrow"), "r") as source:
        table = pa.ipc.open_file(source).read_all()
        if len(table) != expected_count or any(
            text != "" for text in pa.compute.struct_field(table["lines"], "text").to_pylist()
        ):
            raise ValueError(f"Inventário de imagens sem texto inválido em {split}.")
    print(f"{split}: {expected_count} imagens com texto vazio", flush=True)

original_transform = ArrowIPCRecognitionDataset._apply_text_transform


def allow_empty_pretraining_text(self, text):
    if text == "" and not self.skip_empty_lines:
        return text
    return original_transform(self, text)


ArrowIPCRecognitionDataset._apply_text_transform = allow_empty_pretraining_text
cli()
