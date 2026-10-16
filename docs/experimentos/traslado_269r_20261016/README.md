# 269r: referência congelada e comparação de reconhecedores

Em 16/10/2026, as cinco primeiras linhas do corpo do Traslado foram conferidas
por **Rodolfo Vinicius Cima Takemoto**, conforme o nome salvo no editor. Texto,
geometria, correspondência entre imagem/documento/269r e cobertura completa
**somente do bloco `body_first5`** foram confirmados. As outras 19 linhas
candidatas e o restante do fólio continuam fora desta aprovação.

## Resultado controlado

| Reconhecedor | CER por região | WER por região | Falhas |
|---|---:|---:|---:|
| TrOCR small handwritten | 195/242 = **80,58%** | 45/45 = **100%** | 0/5 |
| PP-OCRv5 latino, conversão ONNX RapidAI | 138/242 = **57,02%** | 43/45 = **95,56%** | 0/5 |

O CER caiu 23,55 pontos percentuais, mas a segunda saída ainda contém muitas
omissões e palavras deformadas. **Não obtivemos leitura automática aproveitável.**
Dois reconhecedores insuficientes neste bloco não demonstram impossibilidade
de HTR no acervo. As sugestões automáticas continuam desativadas no editor.

A unidade principal é a região completa, com linhas concatenadas na ordem,
separadas por um espaço. Aplicamos apenas Unicode NFC e redução de espaços,
preservando caixa, acentos e pontuação. `ca / torze`, `Deste / rro` e o `di`
final permanecem nas referências; não recompomos palavras nem modernizamos.
Os denominadores são 242 caracteres e 45 palavras, incluindo a união das linhas.

| Linha | Referência humana | TrOCR: saída bruta | PP-OCRv5: saída bruta |
|---|---|---|---|
| 1 | Anno do Nacimento de Nosso Senhor Jezus christo | What is the most of a successful half of the federal research was in | Amodo Nacei momo de Nofo enen Ieucerike |
| 2 | de mil seis centos sincoenta e seis annos, aos ca | selects the self of elementary management . | demid diCumo cnaoriy amo ay |
| 3 | torze Dias do mes de Dezembro da dita Hera nesta | is also a successful scientific health health to | tonzey o mey  Deror de dialednea |
| 4 | povoação e Freguezia de Nossa senhora do Deste | was a successful field for the | panraeaegariooga inorse |
| 5 | rro de Jundiahy, aonde Eu Publico Tabelião ao di | What is the first man made the first relationship was | mro ce moaky condeeli abrig ad |

O espaço duplo na saída bruta da linha 3 está preservado no JSONL; a métrica
reduz espaços igualmente nas referências e predições. As contagens completas
de substituições, deleções, inserções e acertos estão em [comparison.json](comparison.json).

## O que foi mantido e o que mudou

São os mesmos arquivos de imagem e recortes, caixas, IDs, ordem, textos humanos,
cobertura e código de avaliação nas duas execuções. Só mudou o reconhecedor,
incluindo seu pré-processamento e decodificação próprios. O adaptador ONNX
recebe uma linha, usa BGR, altura 48, largura proporcional de pelo menos 320,
interpolação linear, normalização `(pixel/255 - 0.5)/0.5` e preenchimento zero à
direita; decodifica CTC por argmax, colapsando repetições antes de remover blank.
Não usa detector, orientação, correção textual ou descarte por confiança.

A escolha do segundo candidato se baseou no suporte declarado a português
pela [documentação oficial do PaddleOCR](https://www.paddleocr.ai/v3.3.0/en/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.html)
e na viabilidade de execução local. Isso não comprova adaptação à caligrafia
histórica deste fólio. A [ficha do TrOCR](https://huggingface.co/microsoft/trocr-small-handwritten)
informa ajuste no IAM; a diferença de domínio é uma hipótese explicativa,
sem isolar causalmente a razão dos erros observados.

Ambos rodaram em CPU/float32. O TrOCR usa snapshot
`b4648cfa171985a6745f37ddd637e98c0da958ac`, seed 1831, um beam, máximo 128 tokens,
sem amostragem. Os avisos do pooler estão preservados. O ONNX tem SHA-256
`b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a`, ONNX Runtime
1.23.2, um thread por operador/sessão e execução sequencial. O
[registro RapidAI fixado por commit](https://github.com/RapidAI/RapidOCR/blob/7cfd3d9ef786a2e538ca30df700325e72e85b5f5/python/rapidocr/default_models.yaml)
identifica a conversão. Os pesos permanecem fora do Git.

Os tempos medidos de carregamento são cerca de 32,95 s (TrOCR) e 0,65 s (ONNX).
São observações locais, com inicializações e bibliotecas diferentes, sem
benchmark de velocidade ou estimativa de esforço humano.

## Artefatos e proveniência

- [reference/catalogo/](reference/catalogo/): exportação humana original da
  revisão `20261016T172615_7ca3ab1c`, com páginas, linhas, autoria e horários.
- [reference/linhas_exploratorias.jsonl](reference/linhas_exploratorias.jsonl):
  os mesmos textos com atribuição exploratória persistida. `Dias` tem D
  maiúsculo e a linha 2 preserva `seis centos`, `aos ca` e exclusão vazia.
- [Clarificações](reference/clarificacoes.json), [confirmação de página e cobertura](reference/confirmacao_pagina_cobertura.json)
  e [snapshot imutável](reference/snapshots/): decisões e estado final.
- [baseline_trocr/](baseline_trocr/): cópia literal da execução inicial,
  incluindo configuração congelada, predições/tokens, métricas, logs e hashes.
  O relatório interno diz que a execução era local porque foi escrito antes
  desta publicação; seus bytes e caminhos históricos foram mantidos.
- [latin_ppocrv5/](latin_ppocrv5/): predições/tokens, estado do modelo, versões,
  avaliação e origem dos pesos. A configuração estava codificada no adaptador
  antes da inferência; `configuration.json` é uma descrição posterior extraída
  dos metadados emitidos, explicitamente identificada como tal.
- [inventory.json](inventory.json): hashes dos arquivos publicados, código
  usado, imagem e recortes compartilhados; mapeamento de caminhos originais
  para cópias publicadas. Os caminhos nos recibos originais não foram reescritos.
  O Git registra o próprio inventário; ele não inclui seu próprio hash.

As notas de preparação dentro dos manifests/snapshots são históricas e ainda
descrevem propostas pendentes. Os campos `validated`, revisor, horários e os
recibos documentam a aprovação posterior deste bloco. A edição é apoio; a
referência resulta da conferência humana assistida. A data do ato de 1656 e o
ano 1767 no cabeçalho permanecem distintos; a confirmação destas cinco linhas
não valida integralmente o cabeçalho.

## Auditoria offline em outro checkout

Execute na raiz desta revisão do repositório, com Python 3.11 ou 3.12:

```powershell
python -m pip install -e ".[test]"
python scripts/audit_traslado_experiment.py --restore-support --output output/auditoria_269r_NEW
```

O comando verifica hashes, recibos congelados, snapshot, igualdade exata dos
pixels dos recortes com as caixas na fonte e invariância dos controles nas duas
predições. Recalcula todas as métricas por região e linha em saída nova e exige
igualdade com os resultados publicados. Não baixa modelos nem executa inferência.
O PDF de apoio é uma cópia de 177.383 bytes do membro já existente no arquivo
original; `--restore-support` o recupera offline no caminho histórico ignorado
quando ausente, recusando substituir conteúdo divergente. As condições próprias
da edição e os créditos permanecem no catálogo; a licença MIT cobre o código.

O inventário fixa também os bytes do código e dos logs. Para auditá-lo após
mudanças futuras de implementação, use um checkout desta revisão.

## Repetir inferência explicitamente

As saídas devem ser novas. Primeiro execute a auditoria acima. Para TrOCR:

```powershell
python -m pip install -e ".[htr]"
python -m paleographia prepare-weights --config configs/trocr-download.toml --output-dir models/trocr-small-handwritten
python -m paleographia recognize --lines docs/experimentos/traslado_269r_20261016/reference/linhas_exploratorias.jsonl --config docs/experimentos/traslado_269r_20261016/baseline_reproduce.toml --output experiments/traslado_trocr_NEW/predictions.jsonl
```

Pule `prepare-weights` se os pesos corretos já existirem; o comando recusa
sobrescrita. `baseline_reproduce.toml` apenas substitui os dois caminhos de
manifests pelos publicados; a configuração original permanece preservada.
Para o reconhecedor latino:

```powershell
python -m pip install -e ".[ocr]"
python scripts/recognize_latin.py --download
python scripts/recognize_latin.py --lines docs/experimentos/traslado_269r_20261016/reference/linhas_exploratorias.jsonl --output experiments/traslado_latin_NEW/predictions.jsonl
python -m paleographia evaluate --reference docs/experimentos/traslado_269r_20261016/reference/linhas_exploratorias.jsonl --pages docs/experimentos/traslado_269r_20261016/reference/catalogo/pages.jsonl --predictions experiments/traslado_latin_NEW/predictions.jsonl --output-dir experiments/traslado_latin_NEW/evaluation
```

Apenas os comandos explícitos de preparação/download acessam a rede. Timestamps
e tempos das novas execuções variam; não esperamos igualdade de hash dos arquivos
com novos metadados. A auditoria reproduz os cálculos das saídas históricas.

## Papel da amostra e próxima etapa

Estas cinco linhas são **desenvolvimento** (`split="exploratory"` no esquema
atual), de um documento, sem treino ou teste reservado. Não estimam desempenho
do acervo. Ao ampliar a referência, reservar outros trechos e grupos documentais
antes de usá-los para escolher modelos/configurações. Buscar um reconhecedor
adaptado a manuscritos históricos em português é a próxima investigação; não
trocar referência ou recortes para favorecer este candidato.

A geometria foi reutilizada como controle. IoU=1 e as contagens de sobreposição
split/merge dos retângulos são efeitos dessas caixas, não avaliação de um
segmentador. A comparação OpenCV/Kraken permanece posterior à obtenção de um
reconhecedor aproveitável e de referência maior.
