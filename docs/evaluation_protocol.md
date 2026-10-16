# Protocolo experimental proposto

Atualização posterior: o [PP-OCRv6 medium](experimentos/traslado_269r_ppocrv6_20261016/README.md)
atingiu CER 30/242 = 12,40% e WER 23/45 = 51,11% na mesma referência e nos mesmos
cinco recortes, com leitura aproveitável como rascunho assistido e correção humana
obrigatória. O backend foi integrado experimentalmente ao Traslado; TrOCR ficou
desativado para novas execuções. A região permanece desenvolvimento, sem treino
ou teste reservado. A comparação de segmentadores não foi executada.

Atualização de 16/10/2026: o Traslado 269r tem **cinco linhas integralmente
conferidas**, com cobertura completa somente de `body_first5`. A
[comparação controlada de reconhecedores](experimentos/traslado_269r_20261016/README.md)
congela os mesmos textos e recortes: CER/WER de 80,58%/100% (TrOCR) e
57,02%/95,56% (PP-OCRv5 latino). É uma etapa de diagnóstico do reconhecedor,
anterior à comparação de segmentadores proposta abaixo. As cinco linhas são
**desenvolvimento** (valor canônico `exploratory`); não constituem teste reservado.
Reservar outros trechos/grupos ao ampliar o corpus, antes de escolher modelos
e configurações com eles. A aprovação do bloco não se estende à página inteira.

Objetivo: medir o efeito da segmentação na transcrição assistida, mantendo **o mesmo reconhecedor aprovado e sua configuração**. O candidato atual é PP-OCRv6/Kraken 7.1; não reutilizar o TrOCR rejeitado. Métodos: OpenCV (contornos ou perfil horizontal pré-especificado) e Kraken 6.0.0 (linhas/baselines, bbox derivada de polígono). Controle: recortes humanos revisados. O controle não é outro modelo treinado.

Perguntas: RQ1, como os métodos localizam/separam linhas? RQ2, qual o efeito em CER, WER e tempos mantendo o reconhecedor fixo? RQ3, quais características de documento/segmentação aparecem nos erros? Melhoria é hipótese, inclusive resultados negativos devem permanecer.

Antes da comparação de segmentadores: identificar documento/fólios, fixar política textual, ampliar a seleção para 30–50 linhas em regiões integralmente revisadas e registrar exclusões. As cinco linhas do Traslado permitem o diagnóstico de desenvolvimento acima; o orçamento não prova suficiência estatística ou para treino. O catálogo de 1831 ainda não tem linhas aptas e reúne três fólios de uma sessão candidata, sem comprovação de escriba comum.

`split` persiste semente, atribuições e contagens; não refaz a divisão em cada treino. O padrão é documento, juntando todos os seus fólios, fontes repetidas e derivados. Exige ao menos três grupos para treino/validação/teste e verifica vazamento também por fonte, fólio e `derived_from`. Não forçar 80/10/10. Com um documento use `--exploratory`: tudo permanece no conjunto exploratório, **sem treino** e sem alegação de generalização. Divisão por fólio de um documento não está habilitada por padrão; exige protocolo adicional explícito.

Ajuste segmentação e hiperparâmetros apenas no desenvolvimento. Congele TOML e hashes antes do teste reservado; não usar teste em demonstrações, adaptação ou escolha de hiperparâmetros. O CLI usa o split definido em `[experiment]`. Augmentations não são geradas pelo MVP; quando acrescentadas, somente de treino e com grupo/linhagem preservados.

Geometria: correspondência 1:1 por IoU bbox >= 0,5, ordenação determinística por IoU decrescente. É greedy, não otimização global. Interseção/menor área >= 0,2 identifica relações de divisão/fusão: referência sobreposta a múltiplas detecções = linha dividida; detecção sobreposta a múltiplas referências = fusão. Omitida/espúria = sem aresta de sobreposição; `unmatched_*` também registra caixas sem correspondência pelo limiar IoU. Contagens de divisão/fusão não são categorias mutuamente exclusivas. Critérios são fixados antes do teste.

Texto: avaliação principal concatena todas as referências e saídas em ordem por região de cobertura completa. Linhas omitidas causam deleções e linhas espúrias na região causam inserções; falhas de processamento contam como saída vazia. Predições fora de cobertura conhecida são listadas com motivo, não penalizadas como se houvesse referência. Não avaliar a parte anterior à cobertura editorial do 100r.

CER = (S+D+I)/caracteres da referência; WER usa palavras. Microagregar contagens das regiões, nunca média simples das taxas. Referência vazia: registrar inserções e taxa nula (denominador zero). Referência não vazia e saída vazia: todas deleções. Não limitar taxas a 1. Métricas por linha usam correspondência geométrica válida e são diagnósticas; espúrias não pareadas entram na métrica principal de região.

Relatórios guardam configuração, versões, commit + estado dirty, dispositivo/precisão, snapshot/hashes dos pesos, manifests/hashes, falhas, predições brutas, tempos, exclusões, overlays e recortes. Kraken roda em subprocesso; seu tempo externo inclui inicialização do processo e o carregamento neural é reportado separadamente. O reconhecedor selecionado é reutilizado entre os métodos na comparação. Não confundir tempo total com tempo de inferência, nem inferir economia humana por CER. Para esforço humano, usar sessões realmente cronometradas e protocolo separado.
