# Fichamentos parciais — 23/10/2026

Consulta dirigida por Codex, assistente de IA. Conferência humana, triagem formal
e inclusão final na revisão sistemática: **pendentes**. Este arquivo registra
consultas parciais reais, sem declarar leitura integral dos dois trabalhos.
Os identificadores seguem a [seleção comentada](referencias_comentadas_20261023.md)
e o [registro estruturado](referencias_20261023.json).

## T1 — Muehlberger et al. (2019)

ID canônico: `DOI-10.1108/JD-07-2018-0114`. Origem: seleção complementar recebida;
consulta ao [registro e resumo da Universidade de Edimburgo](https://www.research.ed.ac.uk/en/publications/transforming-scholarship-in-the-archives-through-handwritten-text/).
O acesso direto ao PDF retornou bloqueio nesta conferência. Metadados e resumo
foram consultados; método experimental e texto integral não foram conferidos.

| Campo comparável | Extração parcial / estado |
| --- | --- |
| Natureza | Artigo, Journal of Documentation 75(5), 954–976, 2019 |
| Objetivo | Examinar aplicação e impacto de HTR em arquivos pelo caso Transkribus |
| Corpus e quantidades | Não verificado no texto integral |
| Modelo/checkpoint e ajuste | Não verificado |
| Partições e independência | Não verificado |
| Referência e convenções | Não verificado |
| CER/WER e resultados numéricos | Não extraídos; não usar como comparação quantitativa |
| Relação proposta com PaleographIA | Contexto arquivístico e integração de reconhecimento ao trabalho humano |
| Próxima leitura | Localizar dados, condições e limites dos casos antes de síntese empírica |

PB potencial: PB3, como contexto; a adequação à síntese empírica depende da
leitura. Não afirmar que a ausência de extração significa ausência de método
ou métricas no artigo.

## T4 — Kiessling (2026)

ID canônico: `ARXIV-2609.20064`; versão consultada: **v1**.
Ocorrência anterior: `B02-ARXIV-001`; nova consulta vinculada ao mesmo estudo.
[Registro arXiv](https://arxiv.org/abs/2609.20064v1) e
[PDF](https://arxiv.org/pdf/2609.20064v1).
Escopo desta conferência: metadados, primeira página e trechos das seções 4.2–4.4,
incluindo a tabela 5; leitura integral e exame de todos os desenhos experimentais
continuam pendentes. Campos editoriais provisórios do PDF não definem publicação final.

| Campo comparável | Extração parcial / estado |
| --- | --- |
| Natureza | Preprint, submetido em 17/09/2026; revisão por pares não comprovada |
| Condições | Reconhecimento histórico; comparação entre pré-treino, treino e ajuste |
| Modelos | PP-OCRv6 e baseline CRNN; variantes e configurações precisam de extração completa |
| Corpus/dimensões e partições | Inventário e independência ainda não conferidos integralmente |
| Política textual / denominadores | Não verificado para todos os experimentos |
| Resultado localizado | Tabela 5, p. 9: PP-OCRv6 medium, MAKHZAN, CER macro 17,99% zero-shot e 18,82% após ajuste |
| Interpretação limitada | Nesse cenário, o ajuste aumenta o CER; não garante melhora universal |
| Relação proposta com PaleographIA | Fundamentar a análise de transferência e a aceitação de resultados negativos |

PB potencial: PB1/PB3. A taxa publicada pertence ao experimento dos autores;
não é resultado local nem previsão de erro para português/Jundiaí. Não comparar
diretamente essa macroagregação com a microagregação histórica do PaleographIA.

## Campos necessários para fechar a síntese

Completar corpus e quantidades, checkpoint, preparação das entradas, orçamento,
unidade de divisão, política da referência, normalização, agregação, falhas e
limitações. Cada resultado precisa de página/seção/tabela e conferência humana.
Usar os [modelos existentes](triagem_e_fichamento.md) para a decisão final;
estes registros parciais não a substituem.
