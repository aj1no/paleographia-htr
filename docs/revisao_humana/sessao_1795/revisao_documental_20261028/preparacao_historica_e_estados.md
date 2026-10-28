# Preparação de 23/10 e estado atual da revisão

O [índice candidato de 23/10](../../../dataset_expansion_20261023/curation_sessao_1795_bloco01/README.md) é um retrato da preparação original: alvos vazios e estados pendentes. Suas descrições e manifests são históricos. Os comandos de importação ali apresentados destinam-se à criação de um workspace vazio, e não à recuperação do editor atual.

O estado atual está na [retificação humana para Juiz](../retificacao_juiz_20261028/README.md) e no [catálogo posterior da retificação](../retificacao_juiz_20261028/catalogo_depois.json). A revisão é `20261028T162318_8769604b`: oito geometrias validadas, oito textos pendentes e quarta linha parcial com `exclusion_reason`. A ordem 0–7 e o hífen de trat- já estão confirmados.

O README candidato integra o inventário congelado `docs/dataset_expansion_20261023/inventory.json`, com SHA-256 `188880fcfe80c5659a6d3c3264789f784a6c4dc833dcb1ed9c72262ea7138142`. Acrescentar uma nota naquele arquivo mudaria seus bytes e faria falhar a auditoria existente. Este guia é a contextualização aditiva; o README e o inventário originais foram preservados.

## Metadados de preparação e estados formais

`segmentation_method=manual_candidate_not_human_approved` e `alignment_status=candidate_pending_human_confirmation` vieram da preparação. São metadados herdados de proveniência. A geometria atual é dada por `geometry_status=validated`; os textos permanecem com `review_status=pending_review` e `reference_kind=unknown`. Os metadados de origem não foram reescritos para uniformizar sua aparência.

`reviewed_at` é compartilhado entre texto e geometria. Os carimbos da consolidação registram a aplicação das confirmações geométricas anteriores. O carimbo posterior da quarta linha, na retificação, não representa nova confirmação dos limites nem aprovação textual. Sua interpretação depende dos estados formais, da ação e do histórico. As datas das declarações humanas continuam nas observações e recibos.

## Interpretação dos validadores

Os relatórios de catálogo válido e bloqueio de avaliação/treinamento continuam sendo os da rodada publicada. No [validador existente](../../../../src/paleographia/data.py), a correspondência documental é verificada antes dos requisitos textuais; o primeiro erro pode encerrar as verificações daquela linha. Os erros publicados, portanto, não são uma lista exaustiva de todas as pendências.

Resolver a correspondência documental, isoladamente, não libera as oito linhas. Texto completo e aprovado, tipo de referência apropriado, proveniência, exclusões, cobertura exigida e partições documentais continuam sujeitos às verificações do protocolo. Depois de uma decisão futura mudar os dados, os validadores devem ser executados novamente para revelar os bloqueios seguintes. Nesta etapa somente documental, foram verificadas referências, links, integridade e a ausência de alteração do editor.
