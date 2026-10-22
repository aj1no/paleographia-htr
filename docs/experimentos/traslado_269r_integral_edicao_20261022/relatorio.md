# Fólio 269 reto inteiro — comparação automática com a edição

**Diagnóstico de desenvolvimento.** Referência editorial publicada, sem nova
conferência humana do texto, treinamento ou teste reservado. Reconhecedor:
**PP-OCRv6 medium/Kraken**, com os pesos, a imagem Docker e a configuração já existentes.

## Resultado principal

| Área | CER | Erros/caracteres | WER | Erros/palavras |
| --- | ---: | ---: | ---: | ---: |
| Página completa | 26,97% | 391/1450 | 60,31% | 158/262 |
| Cabeçalho e foliação | 35,29% | 12/34 | 71,43% | 5/7 |
| Título | 47,06% | 24/51 | 88,89% | 8/9 |
| Resumo | 79,25% | 191/241 | 90,70% | 39/43 |
| Corpo | 14,63% | 164/1121 | 52,22% | 106/203 |

A página completa é uma única sequência para o cálculo principal. As áreas
são diagnósticos separados; suas taxas não foram usadas para fazer média.
O teste gerou **35 recortes automáticos**, comparados a
**36 unidades da edição**: três elementos do cabeçalho/foliação, duas linhas do
título, sete do resumo e 24 do corpo. Essas 36 unidades não equivalem a 36 linhas
físicas do manuscrito: os três elementos do cabeçalho compartilham a faixa superior.

Houve **0 falhas técnicas** e **3 saídas vazias**, nas ordens
0, 4, 34 (ordens iniciadas em zero). As faixas 0 e 34 são bordas
da imagem; a ordem 4 contém a primeira linha do resumo e também retornou vazia.
Esses recortes não foram removidos ou reconhecidos novamente.

## Principais erros e diferenças de representação

- **Resumo:** seis recortes automáticos para sete linhas da edição, com extensa
  perda de conteúdo. A caixa `[70, 473, 1096, 550]` reúne as duas últimas linhas
  visíveis desse bloco. A primeira linha do resumo retornou vazia. As causas
  de cada omissão não foram isoladas entre recorte, escala e reconhecimento.
- **Título e cabeçalho:** palavras omitidas e abreviadas pela saída automática;
  `Villa` desaparece no cabeçalho. As margens fixas de 70 pixels à esquerda e
  70 à direita limitam os recortes; não foram ajustadas para melhorar a taxa.
- **Corpo:** junções e separações de palavras, trocas de letras, caixa, acentos
  e pontuação. Exemplos incluem `Anno do`/`Annodo`, `Jundiahy`/`Sundialg` e
  `deligençias`/`de Ligencias`.
- **Edição e abreviaturas:** o alvo final é `Magestade`, conforme a edição;
  a forma abreviada `Magᵈᵉ` permanece na revisão humana anterior. O erro medido
  inclui essa diferença de convenção. Grafias, espaços e quebras editoriais,
  como `Se / nhora`, também fazem parte deste alvo.

## Exemplos completos

| Local | Edição oficial | Saída bruta |
| --- | --- | --- |
| Cabeçalho completo | Villa de Jundiahy Anno de 1767 269 | De Jundiarly node 1767 269 |
| Título, primeira linha | Traslado de Auto e Criação desta | Tdo u Cacõ desa |
| Corpo, linha 1 | Anno do Nacimento de Nosso Senhor Jezus christo | Annodo Nacimento de Nosso Senhor Iezuschritto |
| Corpo, linha 14 | Senhora do DesTerro de Jundiahy onde Heram | senhora dlo des Terro de Sundialg on de heram |
| Corpo, linha 18 | tissa fazer deligençias por ser Longe devendo | isca fazer de Ligencias por ser Longe deuendo |
| Corpo, linha 24 | lhes Requerião da parte de Deos e de Sua Magestade | lhes Requiriaõ da parte de deos e de sua Ragd.s |

Os exemplos do corpo têm correspondência geométrica inspecionada pelo assistente
para apresentação, sem alterar as previsões ou promover uma leitura a validada.
A versão normalizada usada nas contas aplica somente NFC e colapso de espaços;
o JSON e o texto bruto conservam os caracteres realmente emitidos.

## Cobertura e protocolo

Foram selecionados os trechos do reto nas páginas 1 e 2 do PDF, encerrando antes
de `269/Verso.`. Metadados e créditos da edição foram excluídos por não fazerem
parte da imagem manuscrita. A fonte foi extraída e renderizada para conferir
a cobertura. A ordem espacial do cabeçalho foi fixada antes da inferência:
`Villa de Jundiahy`, `Anno de 1767`, `269`; o PDF dispõe esses campos em outra
sequência vertical. Nenhuma palavra foi substituída por interpretação posterior.

O detector OpenCV por projeção recebeu a imagem inteira, com os parâmetros já
existentes. Não foram usados os 24 recortes humanos nem as cinco regiões
revisadas. Todos os recortes foram enviados ao PP-OCRv6, apenas como imagem,
sem os textos da edição. Falhas e saídas vazias permanecem na comparação.
As áreas diagnósticas foram delimitadas antes da execução por faixas verticais
e associadas pelo centro das caixas; limites cruzados ficam registrados no JSON.

CER/WER usam NFC, colapso de espaços, caixa e diacríticos preservados; somam
substituições, deleções e inserções contra 1.450 caracteres e 262 palavras no
reto completo. Essas taxas não são porcentagens simples de acerto.

## Preservação e interpretação

O reconhecimento bruto, os recortes, os alvos editoriais e os parâmetros ficam
arquivados nesta pasta. Os workspaces e os arquivos anteriores foram conferidos
por hash antes e depois da execução, sem alterações. Permanecem os pacotes
de 20/10 e 22/10, as oito ressalvas históricas e as confirmações humanas anteriores.
Nenhum peso foi alterado, nenhum treinamento foi executado e nenhum estado
humano foi promovido.

Este teste **mede o fluxo de segmentação e reconhecimento contra a edição**.
Difere do experimento de 24 recortes humanos com referência assistida e
agregação em cinco blocos; a diferença de CER/WER não demonstra isoladamente
melhora ou piora do reconhecedor. O 269r já é documento de desenvolvimento;
o resultado não mede generalização para outro documento.

## Arquivos para conferir

- [Saída bruta completa](transcricao_bruta.txt), [JSON original](ppocrv6/predictions.jsonl).
- [Texto da edição adotado](texto_oficial.txt), [proveniência de cada unidade](alvos_editoriais.jsonl).
- [Imagem com os recortes automáticos](segmentacao/p_traslado_269r_overlay.png).
- [Métricas](comparacao.json), [tabela por área](por_area.csv), [alinhamentos de erros](erros_palavras.jsonl).
- [Protocolo congelado](protocolo.json), [identidade da execução](ppocrv6/proveniencia.json).
- [Auditoria](validacao.json), [preservação](preservacao_depois.json), [inventário](inventario.json).
