# PaleographIA — transcrição assistida de manuscritos

Protótipo local de apoio à leitura de manuscritos históricos de Jundiaí. Permite
conferir recortes e ordem de leitura, consultar vocabulário com fontes e salvar
revisões humanas com autoria e histórico. Reconhecimento bruto, edição publicada
e texto humano permanecem separados. A interface é apresentada em português.

**Estado em 21/10/2026 — branch principal e padrão: `main`.** O escopo está
fechado para novas funções; a prioridade é consolidar a avaliação e as entregas
de PI IV e PLN. Não houve treinamento ou ajuste fino neste corpus.

A [versão principal no GitHub](https://github.com/aj1no/paleographia-htr/tree/main)
contém o programa, a documentação e as evidências publicadas. A branch
`codex/refatoracao-piloto` foi preservada como registro da etapa anterior.
Referências a ela nos pacotes datados indicam a origem das entregas; consulte
a [nota sobre a adoção da main](docs/manutencao/main_20261020/README.md).

## Referência e resultados atuais

O corpo selecionado do **fólio 269r do Traslado do Auto de Criação da Vila** tem
24 linhas com geometria e cobertura conferidas em cinco blocos. Há **16 linhas
validadas e oito com ressalvas visuais**. Nas dúvidas, a referência assistida
adota a edição com proveniência; isso não equivale a confirmação visual nem a
referência humana independente da edição.

Os mesmos 24 recortes foram usados para comparar dois reconhecedores:

| Reconhecedor e implementação | CER | WER |
| --- | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 94,58% |
| PP-OCRv6 medium / Kraken 7.1 | 15,11% | 60,10% |

**Diagnóstico de desenvolvimento**, com oito ressalvas preservadas: um documento,
sem teste reservado ou conclusão de generalização. As métricas microagregam os
cinco blocos completos: 1.112 caracteres e 203 palavras. Variantes, implementações
e pré-processamentos diferem; a diferença não pode ser atribuída somente à versão.

- [Referência assistida, decisões e dúvidas](docs/revisao_humana/traslado_269r/referencia_assistida_20261020/README.md).
- [Comparação dos 24 recortes, bruto e auditoria](docs/experimentos/traslado_269r_reconhecedores_24_20261020/README.md).
- [269 reto inteiro contra a edição](docs/experimentos/traslado_269r_integral_edicao_20261022/README.md):
  diagnóstico separado com segmentação automática e PP-OCRv6, incluindo cabeçalho, título e resumo.
- [Notebook, artigo e evidências com a reconferência de 21/10](docs/entregas/pi_iv_pln_20261022/README.md),
  preservando o [pacote original de 20/10](docs/entregas/pi_iv_pln_20261020/README.md).
- [Pendências de PI IV e PLN](docs/entregas/pi_iv_pln_20261022/adequacao_academica.md):
  rubricas, modelo de artigo, revisão bibliográfica e revisão final dos autores.

O catálogo anterior de **1831** continua separado: três fólios candidatos, 94
recortes pendentes e nenhuma linha completa validada. Seu repertório contém 13
exemplos e seis confirmações parciais; “hum” permanece provável. As métricas do
269r não avaliam esse catálogo.

## Instalar e abrir

Na raiz do repositório, use **Python 3.11 ou 3.12**. Exemplo no Windows:

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[test]"
.venv/Scripts/python.exe -m paleographia serve --config configs/traslado_269r.toml --host 127.0.0.1 --port 8011
```

Abra [o editor do Traslado](http://127.0.0.1:8011/). Em Linux, use
`.venv/bin/python` no lugar de `.venv/Scripts/python.exe`.

Um checkout novo começa sem workspace; iniciar o servidor não importa as revisões
salvas nesta máquina. O [guia de execução](docs/runbook.md) explica a importação
do catálogo congelado em workspace vazio, os históricos e o piloto de 1831.
Use um processo por workspace.

O **PP-OCRv6 é o reconhecedor experimental do editor do Traslado**. Inferência
exige pesos e [runtime Linux/Docker separados](runtime/kraken_ppocrv6/README.md),
com identidades conferidas. A instalação básica não os baixa; a revisão manual
continua disponível sem o reconhecedor. PP-OCRv5 é usado no experimento separado;
TrOCR está bloqueado para novas execuções. `start_safe.bat` abre o piloto de 1831
na porta 8000, onde a apresentação de sugestões permanece desativada.

## Conferir sem reconhecer novamente

```powershell
.venv/Scripts/python.exe -m pytest -q
node --test tests/web_review.test.cjs
.venv/Scripts/python.exe docs/revisao_humana/traslado_269r/referencia_assistida_20261020/verificar.py
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/verificar.py
```

Os testes usam dados sintéticos identificados e evidências congeladas; não
medem nova qualidade de reconhecimento. A CI executa a suíte e as auditorias
publicadas em Windows/Ubuntu, Python 3.11/3.12. A tarefa acadêmica separada usa
Ubuntu/Python 3.12 para auditar e reexecutar separadamente as entregas de 20/10
e 22/10, sem pesos ou nova inferência. Confere métricas, cinco ou seis tabelas e
as oito ressalvas, preservando os pacotes publicados e as decisões posteriores.
Veja a [CI acadêmica e seus artefatos](docs/manutencao/ci_academica_duas_versoes_20261022/README.md)
e a [entrega acadêmica original](docs/entregas/pi_iv_pln_20261020/README.md).

## Organização

| Caminho | Papel |
| --- | --- |
| `src/paleographia/` | Pacote atual: CLI, API, editor, revisão e avaliação |
| `configs/`, `runtime/` | Configurações e ambiente separado do reconhecedor |
| `data/manifests/`, `data/lexicon/` | Catálogos, repertório e base lexical |
| `docs/revisao_humana/`, `docs/experimentos/` | Revisões e experimentos publicados com hashes |
| `docs/entregas/` | Notebook, artigo e evidências acadêmicas |
| `tests/`, `.github/workflows/` | Testes e CI |
| `legacy/`, scripts numerados, `client` | Histórico e compatibilidade; consultar o inventário antes de remover |

[Índice da documentação](docs/README.md) · [Guia de revisão](docs/guia_revisao_gpt.md) ·
[Revisão do repositório](docs/revisao_repositorio_20261020.md) ·
[Consulta lexical](docs/lexico_historico.md) · [Política textual](docs/transcription_policy.md) ·
[Contribuição](CONTRIBUTING.md).

Código sob MIT. Imagens, manuscritos e edições têm créditos e condições de uso
próprios; a licença do código não concede automaticamente permissão para esses
materiais. Consulte [fontes](docs/sources.md) e [uso de IA](docs/ai_comments.md).
