# Ambiente e modelos

Testado localmente no Windows com **Python 3.12.14**, Pillow 11.3.0, NumPy 2.2.6, OpenCV headless 4.12.0.88, FastAPI 0.116.1, Pydantic 2.11.7, JiWER 4.0.0. Inferência: PyTorch 2.7.1+cpu, torchvision 0.22.1, Transformers 4.57.1, sentencepiece 0.2.1 e accelerate 1.10.1. O ambiente `.venv` foi criado com o Python 3.12 do runtime local; o Python padrão do usuário é 3.14 e não deve ser usado neste ambiente. Python 3.11/3.12 são alvos da CI; somente 3.12/Windows foi executado localmente.

As dependências diretas estão fixadas em `pyproject.toml`; `requirements-tested-windows-py312.txt` registra o freeze da execução, não é lock universal para outros sistemas. Instalação leve: `python -m pip install -e ".[test]"`. Extras: `[htr]` para inferência/treino e `[pdf]` para extração de texto/RAR. RAR exige extrator compatível; esta máquina tinha `C:\Program Files\WinRAR\UnRAR.exe`. A extração feita na auditoria selecionou esse executável explicitamente via `rarfile.UNRAR_TOOL`; em outra máquina, instale/configure o extrator no PATH. Nenhum script move o único original de Downloads.

## TrOCR

`prepare-weights --config configs/trocr-download.toml --output-dir models/trocr-small-handwritten` é a operação explícita de download. A revisão fixada é `b4648cfa171985a6745f37ddd637e98c0da958ac`. O download usa diretório de staging e arquivos regulares, evitando privilégio de symlink no Windows. `provenance.json` inclui hash dos arquivos e snapshot. Checkpoint deve conter configuração, pré-processador, tokenizador e pesos (e todos os shards quando aplicável). A API de carregamento também verifica arquitetura/compatibilidade. Não existe fallback silencioso.

O TOML do piloto aponta para esse diretório local, usa CPU/float32, `local_files_only=true`, processador lento explicitamente fixado e geração determinística com limite configurável. O checkpoint small é pré-treinado e não foi ajustado ao português histórico. Greedy seleciona tokens prováveis e não garante fidelidade. As saídas reais de diagnóstico foram inadequadas; não são referência histórica.

A preparação inicialmente falhou porque o requests não confiava no certificado da rede; resolveu-se fornecendo um bundle com certificados públicos confiáveis do Windows (`REQUESTS_CA_BUNDLE`), mantendo verificação HTTPS. Não se desabilitou TLS. A primeira tentativa pelo cache encontrou limitação de symlinks, corrigida no código com download em `local_dir`. Se a preparação falhar, registre o erro e use diretório novo para nova tentativa; não trate uma pasta parcial como modelo.

## Kraken separado

Foi conferido o contrato real de [blla.segment na versão 6.0.0](https://raw.githubusercontent.com/mittagessen/kraken/6.0.0/kraken/blla.py): retorna `Segmentation.lines`, com `boundary` e `baseline`. O worker verifica a versão, tipo do modelo e polígonos, e preserva geometria nativa junto da bbox. O mesmo TrOCR permanece no processo principal.

Kraken 6.0.0 exige Python >=3.9,<3.13, NumPy ~=2.0.0, SciPy ~=1.13.0, coremltools ~=8.1 e torch >=2.4,<2.8. Por isso não foi adicionado ao ambiente principal (OpenCV 4.12 requer NumPy >=2.0,<2.3, e o projeto fixa 2.2.6). A checagem real `pip install --dry-run --only-binary=:all: kraken==6.0.0` no Windows falhou: **não há distribuição binária compatível de coremltools ~=8.1 no índice consultado**. Isso não prova impossibilidade de compilação manual, mas essa rota não foi testada. A segmentação neural permanece não executada, sem métricas inventadas.

Preparação sugerida em ambiente Linux/macOS compatível (ainda não executada nesta entrega):

```bash
python3.12 -m venv .venv-kraken
.venv-kraken/bin/python -m pip install 'kraken==6.0.0' 'torch==2.7.1' 'torchvision==0.22.1'
.venv-kraken/bin/python -c "from importlib.resources import files; from pathlib import Path; import shutil; p=Path('models/kraken/segmentation.mlmodel'); p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(files('kraken').joinpath('blla.mlmodel'),p)"
```

Os pesos acima são o segmentador genérico distribuído com o pacote, não um modelo adaptado a estes fólios. O worker calcula SHA-256 e registra versões em cada execução. Configure `[neural].python` com o caminho desse executável e `[neural].weights` com o arquivo preparado; são necessários os caminhos no mesmo sistema em que o CLI roda. Em Windows, não apontar diretamente para um executável Linux/WSL como se fosse `.exe`; executar o projeto no ambiente compatível ou fornecer um launcher explícito próprio. O padrão do adaptador busca `.venv-kraken/Scripts/python.exe`; em Linux configure `.venv-kraken/bin/python`.

```bash
python -m paleographia segment --pages data/manifests/pages.jsonl --method kraken --output-dir data/processed/kraken_NEW
```

Esse comando falha claramente se pesos ou runtime estiverem ausentes. Antes do experimento, conferir que o peso é de segmentação, que sua entrada aceita RGB e que o modelo é adequado ao domínio; o worker não binariza silenciosamente um modelo que só aceita entrada binária. Uma execução real do worker ainda é requisito para encerrar a validação dessa rota.
