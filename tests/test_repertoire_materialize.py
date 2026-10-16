import hashlib
import importlib.util
import io
import json
from pathlib import Path

import pytest
from PIL import Image


def test_rebuild_repertoire_preserves_confirmation_and_refuses_divergence(tmp_path):
    spec = importlib.util.spec_from_file_location("repertoire_builder", Path(__file__).parents[1]/"scripts/build_repertoire.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = Image.new("RGB", (100, 70), "white")
    source.save(tmp_path/"source.png")
    (tmp_path/"edition.pdf").write_bytes(b"fixture de referencia")
    stream = io.BytesIO()
    source.crop((10, 10, 80, 60)).save(stream, format="PNG")
    expected = stream.getvalue()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    catalog = {"fonte": "source.png", "fonte_sha256": digest(tmp_path/"source.png"),
               "edicao": "edition.pdf", "edicao_sha256": digest(tmp_path/"edition.pdf"),
               "itens": [{"id": "exemplo", "bbox_xyxy": [10, 10, 80, 60],
                          "imagem": "crops/exemplo.png", "imagem_sha256": hashlib.sha256(expected).hexdigest(),
                          "confirmacao_parcial": {"palavra_confirmada": "exemplo"}}]}
    path = tmp_path/"catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    original = path.read_bytes()
    assert module.materialize_repertoire(path, tmp_path)["criados"] == 1
    assert (tmp_path/"crops/exemplo.png").read_bytes() == expected
    assert module.materialize_repertoire(path, tmp_path)["existentes_preservados"] == 1
    assert path.read_bytes() == original
    (tmp_path/"crops/exemplo.png").write_bytes(b"nao substituir")
    with pytest.raises(ValueError, match="não foi sobrescrito"):
        module.materialize_repertoire(path, tmp_path)
    assert (tmp_path/"crops/exemplo.png").read_bytes() == b"nao substituir"
    assert path.read_bytes() == original
