# Fólio inteiro e ajuste fino do PP-OCRv6 — 05/11/2026

Registro aditivo do trabalho de 05/11. Não altera pacotes congelados. Pesos, checkpoints,
recortes e imagens ficam em `output/` e `models/` (fora do Git); aqui ficam os dados de
seleção, as decisões e os números.

## Objetivo

Produzir uma pré-versão do texto do fólio inteiro, o mais próxima possível da escrita,
e comparar o PP-OCRv6 base com versões ajustadas (PI IV, etapa 6; PLN, comparação de modelos).

## Fase 1 — fólio inteiro: segmentação neural + PP-OCRv6 base

- Novo `src/paleographia/blla_segmentation.py`: segmentação de linhas com o modelo `blla`
  do Kraken, já presente na imagem `paleographia-kraken:7.1.0-cpu`, sem rede. Cada linha
  vira o recorte do seu polígono, com cor de papel fora dele.
- `configs/editor_folios.toml` usa esse método no botão **Detectar linhas**.
- Nova vista **Texto do fólio** (`/folio-texto`, `src/paleographia/web/folio_texto.html`,
  rota `GET /api/pages/{id}/text`): texto em ordem de leitura, leitura humana quando existe,
  senão a sugestão do modelo, com origem marcada; copiar e baixar `.txt`.

Diagnóstico no fac-símile do Traslado (desenvolvimento, não teste), PP-OCRv6 base,
CER da página inteira contra a transcrição paleográfica publicada
([relatório](fase1_relatorio_traslado.html), [números](dados/diagnostico_paginas.json)):

| Fólio | Linhas blla | Pareadas | CER da página |
| --- | ---: | ---: | ---: |
| 269r | 37 | 33 | 19,2% |
| 269v | 34 | 34 | 18,9% |
| 270r | 36 | 35 | 18,6% |
| 270v | 36 | 34 | 22,6% |
| 271r | 38 | 29 | 33,5% |
| 271v | 35 | 34 | 26,8% |
| 272r | 40 | 35 | 28,1% |
| 272v | 38 | 32 | 28,1% |
| 273r | 17 | 11 | 38,9% |

## Fase 2 — dados de treino

- `src/paleographia/edition_alignment.py`: alinhamento monotônico das linhas da transcrição
  paleográfica do Traslado (que preserva a quebra de linha) aos recortes, guiado pela leitura
  do modelo base. O rótulo vem sempre da edição: **277 pares** em 9 fólios.
- **Filtro** ([regra e contagens](dados/filtro.json)): a edição expande abreviaturas
  ("Ant." → "Antonio"); treinar com isso ensinaria a expandir. Foram retirados 92 pares com
  abreviatura na leitura-guia, 3 com colchetes editoriais e 7 com CER-guia acima de 0,35.
  Ficaram **175 pares alinhados** (`edition_aligned_paleographic`), que não são validação humana.
- Mais **16 linhas humanas** do 269r (referência assistida de 20/10) no treino.
- **Validação:** 7 linhas humanas da sessão de 1795 (outra mão). **Teste reservado:** pagamento a
  Thomas Pardo, recusado no código de treino (`RESERVED_TEST_DOCUMENTS`).
- **Dados públicos externos** ([pares](dados/pares_traslado_mais_inquisicao.json)):
  - [Portuguese Handwriting 16th–19th c.](https://zenodo.org/records/13986218), CC BY 4.0,
    processos da Inquisição (Torre do Tombo, 1536–1821), transcrição "maximamente conservadora"
    com abreviaturas mantidas. Baixado só o `Validation_Set_FINAL.zip` (MD5
    `e220fef22d0923b0e1d97b109ca6d7f7`); extraídos apenas XML e JPG.
  - `src/paleographia/page_xml_import.py` converteu **1.007 linhas de 504 páginas** (até 2 por
    página; descartadas 41 "unclear" e 2 com "??"; todas no alfabeto do PP-OCRv6). O treino B usa 550.
  - Modelo [TraPrInq](https://zenodo.org/records/14543904) (Kraken, CC BY 4.0, MD5
    `b7f84ede75a0665c275346d94fdc1b95`) usado só como comparação.

## Fase 3 — ajuste fino

Novo pipeline (`ppocrv6_finetune.py` + `ppocrv6_finetune_worker.py`); os arquivos do ensaio de
23/10 ficam intactos por terem bytes fixados. Configuração em `configs/finetune_ppocrv6.toml`.

Treino em GPU com a imagem `runtime/kraken_ppocrv6_gpu` (mesma base e mesmo Kraken 7.1, torch
CUDA 12.6; ID `sha256:b5e275eb694b25aeac0b159181953b8c3824e777ed9c8d49996db5347b6a0c1a`).
A inferência continua na imagem de CPU avaliada.

Problemas encontrados e decisões:

| Tentativa | Resultado | Decisão |
| --- | --- | --- |
| CPU, lote 4 | Contêiner morto por memória | Lote menor |
| CPU, lote 1 | ~18 s por linha, >100 h | GPU |
| GPU FP32 | ~6 s por linha | Mantido |
| GPU 16-mixed | Perda NaN (CTC) | Descartado |
| Taxa 1e-4 | Validação caiu de 86,8% para 45,1% | Taxa 2e-5 |
| Taxa 2e-5 | Caiu para 0,3% em 11 passos | Causa não era a taxa |
| **BatchNorm congelada** | **90,2% em 11 passos** | Mantido: com lotes de 1–2 linhas as estatísticas desandavam |

Validação (acerto de caracteres do `ketos`, 7 linhas e 348 caracteres de 1795):

| Modelo | Caracteres | Palavras |
| --- | ---: | ---: |
| TraPrInq (Kraken, Inquisição) | 75,0% | 32,8% |
| PP-OCRv6 base | 86,8% | 46,3% |
| PP-OCRv6 ajustado A (Traslado), melhor checkpoint | 90,2% | 62,7% |
| PP-OCRv6 ajustado B (Traslado + Inquisição) | em andamento | — |

Limitações: validação muito pequena (diferenças de 1–2 pontos podem ser ruído); três sinais
da validação (ᵃ, ˢ, -) não aparecem no treino; o TraPrInq recebeu recortes retangulares, embora
treinado com linhas extraídas pela linha de base. **Nenhum modelo foi avaliado no teste reservado.**
