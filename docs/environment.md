# Ambientes e modelos — 20/10/2026

Instale a versão da `main`, branch principal e padrão. Para obter ou atualizar
o checkout, siga o [guia de execução](runbook.md). Os registros de ambientes e
execuções anteriores conservam as branches, versões e hashes de sua época.

## Aplicação local

Python **3.11 ou 3.12**, conforme `pyproject.toml`. O ambiente básico oferece
catálogo, editor e auditorias, sem PyTorch, GPU ou pesos.

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[test]"
```

Em Linux, use `python3.12 -m venv .venv` e `.venv/bin/python`. As dependências
diretas estão fixadas no `pyproject.toml`; `requirements.txt` instala o pacote
local. A CI verifica Windows/Ubuntu, Python 3.11/3.12; a entrega local usou
Windows/Python 3.12.14.

| Finalidade | Dependências e estado |
| --- | --- |
| Revisão, API e auditorias | Pacote básico; `[test]` para pytest/httpx |
| Extração PDF/RAR | `[pdf]`; RAR também exige extrator externo compatível no PATH |
| PP-OCRv5 latino | `[ocr]` e pesos ONNX; experimento separado do editor |
| PP-OCRv6 medium | Docker Linux, Kraken 7.1 e pesos; separado da aplicação |
| Notebook e figuras | Ambiente acadêmico Python 3.12, com requisitos próprios |
| Extra `[htr]` | Histórico TrOCR; não habilita o reconhecedor bloqueado nem treino atual |

## Reconhecimento atual

PP-OCRv6/Kraken 7.1 usa worker persistente Linux/CPU/float32, com Python 3.12.15
e PyTorch 2.9.1+cpu. Recebe pixels dos recortes; não monta edição ou referência
humana. Pesos, imagem Docker e worker têm identidades verificadas.

O [guia do runtime](../runtime/kraken_ppocrv6/README.md) explica construção,
download explícito, hashes e transferência da imagem. Uma imagem reconstruída
pode ter ID diferente: exige configuração candidata e avaliação antes de
liberar sugestões, sem alterar a configuração aprovada.

O [diagnóstico de 24 linhas](experimentos/traslado_269r_reconhecedores_24_20261020/README.md)
compara esse componente com PP-OCRv5/ONNX. Implementações e pré-processamentos
diferem; o resultado não isola somente a versão. A [execução inicial em cinco linhas](experimentos/traslado_269r_ppocrv6_20261016/README.md)
é um registro anterior.

## Notebook

A [entrega acadêmica](entregas/pi_iv_pln_20261020/README.md) fornece ambiente
opcional, versões observadas, executor e auditor. Recalcular métricas não exige
pesos, Docker ou nova inferência. A instalação inicial exige rede; o recálculo
usa arquivos locais. O freeze observado não é lock universal.

## Histórico e rotas secundárias

TrOCR: `configs/trocr-download.toml`, extra `[htr]` e código antigo permanecem
para compatibilidade e rastreabilidade. Pontos públicos de carga, download e
reconhecimento estão bloqueados. Não use essa configuração para preparar o
ambiente atual. As [predições antigas](experimentos/traslado_269r_20261016/README.md)
continuam auditáveis sem carregar o modelo.

`neural_worker.py` e `[neural]` referem-se ao segmentador Kraken 6, separado do
reconhecedor Kraken 7.1. Essa rota não foi medida neste corpus; a tentativa de
instalação e limitações estão no [relatório histórico](execution_report.md).
Não é necessária para a comparação atual. Treino Kraken não está implementado.
