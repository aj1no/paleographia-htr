"""Preparação autocontida do notebook Colab; incorporada à primeira célula."""
from pathlib import Path
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys

REPOSITORIO_COLAB = 'https://github.com/aj1no/paleographia-htr.git'
REVISAO_DADOS_COLAB = 'c8a3e9a7f1cc55b66d630c510eff17ff95dfdece'
PASTAS_COLAB = [
    'src',
    'docs/experimentos/traslado_269r_20261016/support',
    'docs/experimentos/traslado_269r_reconhecedores_24_20261020',
    'docs/revisao_humana/traslado_269r/images',
    'docs/revisao_humana/traslado_269r/referencia_assistida_20261020',
    'docs/revisao_humana/traslado_269r/reconferencia_ressalvas_20261021',
    'docs/entregas/pi_iv_pln_20261020',
    'docs/entregas/pi_iv_pln_20261022',
    'docs/entregas/pi_iv_pln_20261023_entrega',
    'docs/entregas/pi_iv_pln_20261023_equipe',
    'docs/bibliografia/leitura_t1_t4_20261023',
]
# O notebook usa os módulos de métricas diretamente de src/. Não instala a
# aplicação, seus extras de OCR ou versões de NumPy/Matplotlib sobre as do Colab.
REQUISITOS_COLAB = [
    'jiwer==4.0.0', 'Pillow>=10,<13', 'pydantic>=2.11.7,<3',
    'numpy>=1.26,<3', 'matplotlib>=3.8,<4', 'nbformat>=5.10,<6', 'nbclient>=0.10,<1',
]


def esta_no_colab():
    if 'google.colab' in sys.modules:
        return True
    try:
        return importlib.util.find_spec('google.colab') is not None
    except (ModuleNotFoundError, ValueError):
        return False


def executar_git(argumentos, cwd=None):
    result = subprocess.run(['git', *argumentos], cwd=cwd, check=True,
                            capture_output=True, text=True,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT='0'))
    return result.stdout.strip()


def preparar_checkout(destino):
    destino = Path(destino).resolve()
    if destino.exists():
        if not (destino / '.git').is_dir():
            raise RuntimeError('A pasta escolhida já existe e não é o checkout preparado. Use outra pasta.')
        remoto = executar_git(['remote', 'get-url', 'origin'], destino)
        revisao = executar_git(['rev-parse', 'HEAD'], destino)
        if remoto != REPOSITORIO_COLAB or revisao != REVISAO_DADOS_COLAB:
            raise RuntimeError('Checkout existente diferente do esperado; nenhuma alteração foi feita.')
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    executar_git(['clone', '--depth', '1', '--filter=blob:none', '--no-checkout',
                  '--branch', 'main', REPOSITORIO_COLAB, str(destino)])
    executar_git(['sparse-checkout', 'init', '--cone'], destino)
    executar_git(['sparse-checkout', 'set', *PASTAS_COLAB], destino)
    executar_git(['fetch', '--depth', '1', '--filter=blob:none', 'origin', REVISAO_DADOS_COLAB], destino)
    executar_git(['checkout', '--detach', REVISAO_DADOS_COLAB], destino)
    if executar_git(['rev-parse', 'HEAD'], destino) != REVISAO_DADOS_COLAB:
        raise RuntimeError('Não foi possível conferir a revisão dos dados.')
    return destino


def instalar_dependencias():
    from packaging.requirements import Requirement
    pendentes = []
    for expressao in REQUISITOS_COLAB:
        requisito = Requirement(expressao)
        try:
            versao = importlib.metadata.version(requisito.name)
        except importlib.metadata.PackageNotFoundError:
            pendentes.append(expressao)
            continue
        if versao not in requisito.specifier:
            pendentes.append(expressao)
    if pendentes:
        print('Preparando bibliotecas do notebook:', ', '.join(pendentes))
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', *pendentes], check=True)
        importlib.invalidate_caches()
    return pendentes


def preparar_ambiente_colab(colab=None, destino=None, instalar=True):
    no_colab = esta_no_colab() if colab is None else colab
    if no_colab:
        raiz = preparar_checkout(destino or Path('/content/PaleographIA_equipe_c8a3e9a'))
        instalados = instalar_dependencias() if instalar else []
    else:
        inicio = Path.cwd().resolve()
        raiz = next((p for p in (inicio, *inicio.parents)
                     if (p / 'pyproject.toml').is_file() and (p / 'src/paleographia').is_dir()), None)
        if raiz is None:
            raise RuntimeError('Abra pelo botão do Colab ou execute dentro do checkout do PaleographIA.')
        instalados = []
    sys.dont_write_bytecode = True
    os.chdir(raiz)
    if str(raiz / 'src') not in sys.path:
        sys.path.insert(0, str(raiz / 'src'))
    saida = raiz / 'output/equipe_colab_20261023'
    saida.mkdir(parents=True, exist_ok=True)
    registro = dict(colab=no_colab, revisao_dados=REVISAO_DADOS_COLAB if no_colab else 'checkout_local',
                    bibliotecas_instaladas=instalados, python=sys.version,
                    novas_inferencias=0, montagem_drive=False)
    (saida / 'preparacao.json').write_text(json.dumps(registro, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Ambiente preparado. Execute as próximas células; use a seção com seu nome.')
    return raiz
