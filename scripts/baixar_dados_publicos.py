"""Baixa os modelos e dados PÚBLICOS usados no ajuste fino e confere o MD5 publicado.

Uso, na raiz do projeto:
    python scripts/baixar_dados_publicos.py            # baixa o que falta e confere tudo
    python scripts/baixar_dados_publicos.py --conferir # só confere o que já existe

Todas as fontes estão no Zenodo, em CC BY 4.0, exceto o PP-OCRv6 (licença no registro).
Cada arquivo vai para uma pasta própria fora do Git. Do ZIP da Inquisição são extraídos
apenas XML e JPG, com conferência de caminho. Nada é executado a partir dos arquivos baixados.

As imagens do acervo de Jundiaí (SISMU) não entram aqui: veja a seção "Reproduzir o treino"
do README.
"""
import argparse
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INQUISICAO = "data/raw/externo/inquisicao_traprinq_zenodo13986218"

FONTES = [
    {"nome": "PP-OCRv6 medium (modelo-base)", "registro": "https://zenodo.org/records/21788410",
     "url": "https://zenodo.org/records/21788410/files/medium.safetensors?download=1",
     "destino": "models/kraken_ppocrv6_medium/medium.safetensors", "md5": "e3411a453ce3b9e9efae3f8631d85762",
     "bytes": 63779644},
    {"nome": "TraPrInq v1 (modelo Kraken de comparação)", "registro": "https://zenodo.org/records/14543904",
     "url": "https://zenodo.org/api/records/14543904/files/traprinq.mlmodel/content",
     "destino": "models/traprinq_v1_zenodo14543904/traprinq.mlmodel", "md5": "b7f84ede75a0665c275346d94fdc1b95",
     "bytes": 159961943},
    {"nome": "TraPrInq metadata.json", "registro": "https://zenodo.org/records/14543904",
     "url": "https://zenodo.org/api/records/14543904/files/metadata.json/content",
     "destino": "models/traprinq_v1_zenodo14543904/metadata.json", "md5": "b63121eb0a3102d53123ce62d4331948",
     "bytes": 3497},
    {"nome": "Portuguese Handwriting 16th-19th c. — critérios de transcrição", "registro": "https://zenodo.org/records/13986218",
     "url": "https://zenodo.org/api/records/13986218/files/Transcription%20Criteria.pdf/content",
     "destino": INQUISICAO + "/Transcription Criteria.pdf", "md5": "842164722de5da610d057b28935506c5",
     "bytes": 627601},
    {"nome": "Portuguese Handwriting 16th-19th c. — Validation_Set_FINAL.zip (505 páginas)",
     "registro": "https://zenodo.org/records/13986218",
     "url": "https://zenodo.org/api/records/13986218/files/Validation_Set_FINAL.zip/content",
     "destino": INQUISICAO + "/zip/Validation_Set_FINAL.zip", "md5": "e220fef22d0923b0e1d97b109ca6d7f7",
     "bytes": 502387028, "extrair_em": INQUISICAO + "/extraido"},
]


def md5(path):
    digest = hashlib.md5()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def baixar(url, destino, esperado_bytes):
    temporario = destino.with_name(destino.name + ".parcial")
    request = urllib.request.Request(url, headers={"User-Agent": "paleographia-reproducao"})
    with urllib.request.urlopen(request, timeout=120) as resposta, temporario.open("wb") as saida:
        recebidos = 0
        for bloco in iter(lambda: resposta.read(1 << 20), b""):
            saida.write(bloco)
            recebidos += len(bloco)
            print(f"\r  {recebidos / 1e6:7.1f} / {esperado_bytes / 1e6:.1f} MB", end="", flush=True)
    print()
    return temporario


def extrair_xml_jpg(zip_path, destino):
    """Extrai só .xml e .jpg, recusando caminhos absolutos ou com travessia."""
    destino = Path(destino).resolve()
    if destino.exists():
        return 0
    destino.mkdir(parents=True)
    total = 0
    with zipfile.ZipFile(zip_path) as arquivo:
        for info in arquivo.infolist():
            nome = info.filename
            if not nome.lower().endswith((".xml", ".jpg")) or nome.startswith("/") or ".." in nome.split("/"):
                continue
            alvo = (destino / nome).resolve()
            if not alvo.is_relative_to(destino):
                continue
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(arquivo.read(info))
            total += 1
    return total


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--conferir", action="store_true", help="não baixa; só confere o MD5 do que existe")
    args = parser.parse_args(argv)
    falhas = 0
    for fonte in FONTES:
        destino = ROOT / fonte["destino"]
        print(f"- {fonte['nome']}\n  {fonte['registro']}")
        if not destino.exists():
            if args.conferir:
                print("  AUSENTE")
                falhas += 1
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            temporario = baixar(fonte["url"], destino, fonte["bytes"])
            if md5(temporario) != fonte["md5"]:
                temporario.unlink()
                print("  MD5 DIVERGENTE: download descartado")
                falhas += 1
                continue
            temporario.replace(destino)
        if md5(destino) != fonte["md5"]:
            print("  MD5 DIVERGENTE no arquivo existente; não foi alterado")
            falhas += 1
            continue
        print("  MD5 confere")
        if fonte.get("extrair_em") and not args.conferir:
            extraidos = extrair_xml_jpg(destino, ROOT / fonte["extrair_em"])
            print(f"  extraídos {extraidos} XML/JPG" if extraidos else "  já extraído")
    print("Tudo conferido." if not falhas else f"{falhas} problema(s).")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
