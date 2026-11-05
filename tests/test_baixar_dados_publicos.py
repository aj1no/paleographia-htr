"""Download script: MD5 gate, atomic replace and safe ZIP extraction (no network: file:// URLs)."""
import hashlib
import importlib.util
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts/baixar_dados_publicos.py"


def load(tmp_path):
    spec = importlib.util.spec_from_file_location("baixar", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = tmp_path
    return module


def test_download_verifies_md5_and_extracts_only_xml_and_jpg(tmp_path):
    source = tmp_path / "origem.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("a/page/p.xml", "<x/>")
        archive.writestr("a/p.jpg", b"jpg")
        archive.writestr("a/notas.docx", b"office")
        archive.writestr("/log.txt", b"absolute")
        archive.writestr("../fora.xml", "<x/>")
    module = load(tmp_path)
    module.FONTES = [{"nome": "teste", "registro": "local", "url": source.as_uri(), "destino": "dados/x.zip",
                      "md5": hashlib.md5(source.read_bytes()).hexdigest(), "bytes": source.stat().st_size,
                      "extrair_em": "dados/extraido"}]
    assert module.main([]) == 0
    extracted = sorted(p.relative_to(tmp_path / "dados/extraido").as_posix()
                       for p in (tmp_path / "dados/extraido").rglob("*") if p.is_file())
    assert extracted == ["a/p.jpg", "a/page/p.xml"]
    assert not (tmp_path / "fora.xml").exists() and not (tmp_path / "dados/fora.xml").exists()
    assert module.main(["--conferir"]) == 0


def test_wrong_md5_discards_download(tmp_path):
    source = tmp_path / "modelo.bin"
    source.write_bytes(b"conteudo")
    module = load(tmp_path)
    module.FONTES = [{"nome": "teste", "registro": "local", "url": source.as_uri(), "destino": "m/modelo.bin",
                      "md5": "0" * 32, "bytes": 8}]
    assert module.main([]) == 1
    assert not (tmp_path / "m/modelo.bin").exists()
    assert not list((tmp_path / "m").glob("*.parcial"))
