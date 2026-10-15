# Protocolo experimental proposto

Objetivo: medir o efeito da segmentação na transcrição assistida, mantendo **o mesmo TrOCR** e a mesma geração. Métodos: OpenCV (contornos ou perfil horizontal pré-especificado) e Kraken 6.0.0 (linhas/baselines, bbox derivada de polígono). Controle: recortes humanos revisados. O controle não é outro modelo treinado.

Perguntas: RQ1, como os métodos localizam/separam linhas? RQ2, qual o efeito em CER, WER e tempos mantendo o reconhecedor fixo? RQ3, quais características de documento/segmentação aparecem nos erros? Melhoria é hipótese, inclusive resultados negativos devem permanecer.

Antes de gerar predições para avaliação: identificar documento/fólios, fixar política textual, selecionar 30–50 linhas em regiões integralmente revisadas e registrar exclusões. Ainda há **zero** linhas aptas. O orçamento não prova suficiência estatística ou para treino. O primeiro catálogo tem três fólios de uma sessão candidata de 1831, sem comprovação de escriba comum.

`split` persiste semente, atribuições e contagens; não refaz a divisão em cada treino. O padrão é documento, juntando todos os seus fólios, fontes repetidas e derivados. Exige ao menos três grupos para treino/validação/teste e verifica vazamento também por fonte, fólio e `derived_from`. Não forçar 80/10/10. Com um documento use `--exploratory`: tudo permanece no conjunto exploratório, **sem treino** e sem alegação de generalização. Divisão por fólio de um documento não está habilitada por padrão; exige protocolo adicional explícito.

Ajuste segmentação e hiperparâmetros apenas no desenvolvimento. Congele TOML e hashes antes do teste reservado; não usar teste em demonstrações, adaptação ou escolha de hiperparâmetros. O CLI usa o split definido em `[experiment]`. Augmentations não são geradas pelo MVP; quando acrescentadas, somente de treino e com grupo/linhagem preservados.

Geometria: correspondência 1:1 por IoU bbox >= 0,5, ordenação determinística por IoU decrescente. É greedy, não otimização global. Interseção/menor área >= 0,2 identifica relações de divisão/fusão: referência sobreposta a múltiplas detecções = linha dividida; detecção sobreposta a múltiplas referências = fusão. Omitida/espúria = sem aresta de sobreposição; `unmatched_*` também registra caixas sem correspondência pelo limiar IoU. Contagens de divisão/fusão não são categorias mutuamente exclusivas. Critérios são fixados antes do teste.

Texto: avaliação principal concatena todas as referências e saídas em ordem por região de cobertura completa. Linhas omitidas causam deleções e linhas espúrias na região causam inserções; falhas de processamento contam como saída vazia. Predições fora de cobertura conhecida são listadas com motivo, não penalizadas como se houvesse referência. Não avaliar a parte anterior à cobertura editorial do 100r.

CER = (S+D+I)/caracteres da referência; WER usa palavras. Microagregar contagens das regiões, nunca média simples das taxas. Referência vazia: registrar inserções e taxa nula (denominador zero). Referência não vazia e saída vazia: todas deleções. Não limitar taxas a 1. Métricas por linha usam correspondência geométrica válida e são diagnósticas; espúrias não pareadas entram na métrica principal de região.

Relatórios guardam configuração, versões, commit + estado dirty, dispositivo/precisão, snapshot/hashes dos pesos, manifests/hashes, falhas, predições brutas, tempos, exclusões, overlays e recortes. Kraken roda em subprocesso; seu tempo externo inclui inicialização do processo e o carregamento neural é reportado separadamente. TrOCR é compartilhado entre os métodos na comparação. Não confundir tempo total com tempo de inferência, nem inferir economia humana por CER. Para esforço humano, usar sessões realmente cronometradas e protocolo separado.
