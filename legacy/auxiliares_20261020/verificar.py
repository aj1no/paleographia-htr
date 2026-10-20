"""Confere os seis auxiliares arquivados contra seus blobs Git de origem."""
import hashlib
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PREFIX = Path('legacy/auxiliares_20261020')
SOURCE_COMMIT = '398aafafce895c104a6f16d69167453213cdc50d'
EXPECTED = {
    'test_encoding.py': 'test_encoding.py.txt',
    'downloads_list.txt': 'downloads_list.txt',
    'downloads_utf8.txt': 'downloads_utf8.txt',
    'train_log.txt': 'train_log.txt',
    'server/Texto importantes.txt': 'server/Texto importantes.txt',
    'index.html': 'index.html',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def verificar(base=BASE):
    base = Path(base).resolve()
    inventory = json.loads((base/'inventario.json').read_bytes())
    require(inventory['commit_origem'] == SOURCE_COMMIT, 'Commit de origem divergente.')
    rows = inventory['arquivos']
    require(len(rows) == 6 and {r['caminho_original'] for r in rows} == set(EXPECTED),
            'O inventário deve conter exatamente os seis auxiliares autorizados.')
    for row in rows:
        original = row['caminho_original']
        expected_path = (PREFIX/EXPECTED[original]).as_posix()
        require(row['caminho_arquivado'] == expected_path, 'Destino divergente: '+original)
        path = (base/EXPECTED[original]).resolve()
        require(path.is_relative_to(base) and path.is_file(), 'Arquivo ausente: '+expected_path)
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        require(len(content) == row['bytes'] and digest == row['sha256'], 'Hash/tamanho divergente: '+expected_path)
        blob = git('show', SOURCE_COMMIT+':'+original)
        require(content == blob, 'Bytes divergem do blob de origem: '+original)
        oid = git('rev-parse', SOURCE_COMMIT+':'+original).decode().strip()
        require(oid == row['git_blob_original'], 'Identificador do blob divergente: '+original)
        local = blob.replace(b'\n', b'\r\n') if row['diferenca_checkout_somente_crlf'] else blob
        require(len(local) == row['bytes_checkout_antes'] and
                hashlib.sha256(local).hexdigest() == row['sha256_checkout_antes'],
                'Registro de conversão do checkout divergente: '+original)
        require(not (ROOT/original).exists(), 'Caminho antigo foi recriado: '+original)
    return {'resultado': 'aprovado', 'arquivos': 6,
            'bytes_identicos_aos_blobs_originais': True, 'caminhos_anteriores_ausentes': True,
            'conversoes_checkout_registradas': sum(r['diferenca_checkout_somente_crlf'] for r in rows),
            'novas_inferencias': 0}


if __name__ == '__main__':
    print(json.dumps(verificar(), ensure_ascii=True))
