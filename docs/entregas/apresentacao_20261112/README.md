# Preparação da apresentação de 12/11/2026

Plano iniciado em **03/11/2026**, com prazo de apresentação informado pelo solicitante. Meta interna proposta: material fechado em **11/11**, com ensaio e cópia de segurança. O prazo de 12/11 não foi estendido automaticamente ao artigo ou a outras entregas das disciplinas.

Este documento reúne o diagnóstico de retomada, o cronograma proposto e um roteiro inicial. **Os slides finais ainda não foram produzidos.** O solicitante confirmou em 03/11 o limite de **até 15 minutos**. A orientação original de PLN, recuperada depois, especifica até dez minutos de exposição e cinco de perguntas. O roteiro passa a mirar 9min30 de exposição, com 30 segundos de margem e cinco minutos de perguntas. A [continuidade do projeto](../continuidade_20261103/README.md) prioriza as próximas etapas de dados e avaliação antes de fechar os slides.

## Ponto de partida conferido em 03/11

| Frente | Evidência atual | Uso na apresentação |
| --- | --- | --- |
| Produto | [Editor e instruções locais](../../runbook.md), com revisão, proveniência e consulta lexical | Demonstrar o fluxo de conferência humana |
| Artigo | [Versão de fechamento de 23/10](../pi_iv_pln_20261023_fechamento/artigo.md), também em PDF e Word | Base do argumento, método e discussão. Revisão dos autores ainda pendente nos registros |
| Notebook | [Primeira entrega com pacote offline e notebook executado](../notebook_1_offline/README.md), além do [guia do Colab](../pi_iv_pln_20261023_colab/README.md) | Script e notebook reduzido conferidos em 03/11 sem rede e sem pacotes adicionais. Recalculam resultados arquivados |
| Comparação principal | [Experimento de 24 linhas](../../experimentos/traslado_269r_reconhecedores_24_20261020/README.md) | Resultado central, com as configurações e limitações visíveis |
| Referência | [24 linhas, 16 validadas e oito ressalvas](../../revisao_humana/traslado_269r/referencia_assistida_20261020/README.md) | Explicar a referência assistida pela edição e as dúvidas preservadas |
| Expansão de 1795 | [Estado mais recente de 28/10](../../revisao_humana/sessao_1795/README.md) | Oito geometrias validadas, oito transcrições pendentes e zero pares elegíveis para treino |
| Ajuste fino | [Ensaio técnico de dois passos](../../dataset_expansion_20261023/README.md) | Evidência técnica separada. Ganho científico em documentos reservados ainda não demonstrado |
| Bibliografia | [Protocolo e leituras](../../bibliografia/README.md) | Fundamentação disponível. Revisão sistemática ainda em andamento |
| Equipe | [Responsabilidades e relatos](../pi_iv_pln_20261023_equipe/roteiro_equipe.md) | Divisão oral e relatos precisam refletir contribuições conferidas pelos participantes |

As auditorias locais de referência e comparação foram reexecutadas em 03/11, sem modelos ou nova inferência. A primeira conferiu 58 arquivos e os 24 recortes, preservando 16 linhas validadas e as oito ressalvas. A segunda aprovou 29 arquivos e recalculou CER/WER por algoritmo independente. A avaliação integral como referência visualmente validada continua inapta, conforme o próprio auditor.

**Atualização da primeira entrega em 03/11:** os commits `1831003` e `6b213fc` publicaram o pacote offline e o notebook detalhado executado. A [conferência local](revisao_notebook1_20261103.md) reproduziu os cálculos pelos dois caminhos offline e confirmou a correspondência do artigo e das entradas. Usar esse pacote como opção sem internet na apresentação. A demonstração do editor e o teste no equipamento final ainda precisam ser preparados.

### Resultado que sustenta a apresentação

| Configuração | CER | WER |
| --- | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 94,58% |
| PP-OCRv6 medium / Kraken 7.1 | 15,11% | 60,10% |

Mesmos 24 recortes do corpo do fólio 269r, cinco blocos, 1.112 caracteres e 203 palavras na referência. Diagnóstico de desenvolvimento de um documento, com referência assistida e oito ressalvas. As diferenças entre variantes, pesos, implementações e pré-processamentos limitam a atribuição causal à versão do modelo. CER e WER medem operações de edição sobre o alvo adotado.

## Cronograma proposto

Datas abaixo são metas internas de preparação, não novos prazos oficiais. Nenhuma tarefa da equipe está atribuída ou marcada como realizada por este plano.

| Data | Trabalho prioritário | Critério para encerrar a etapa |
| --- | --- | --- |
| 03/11 | Retomar o estado real e organizar a narrativa | Diagnóstico e roteiro inicial disponíveis. Limite de 15 minutos confirmado; demais exigências a confirmar |
| 04/11 | Revisar artigo e enquadramento das disciplinas com a equipe | Lista objetiva de ajustes e exigências. Identificar o que depende do professor |
| 05/11 | Preparar os slides de problema, objetivo, dados e método | Primeira metade com fontes, exemplos legíveis e falas curtas |
| 06/11 | Preparar resultados, erros, limites e conclusão | Primeira versão completa dos slides, coerente com o artigo |
| 07/11 | Preparar demonstração em cópia do workspace | Fluxo ensaiado, imagens de apoio e procedimento de abertura documentados |
| 08/11 | Conferir referências, uso de IA e relatos da equipe | Fontes e contribuições conferidas. Registrar requisitos acadêmicos ainda pendentes |
| 09/11 | Fazer primeiro ensaio completo e cronometrado | Identificar cortes, dúvidas e falhas de demonstração |
| 10/11 | Corrigir conteúdo e realizar segundo ensaio | Falas distribuídas, transições claras e duração dentro do limite confirmado |
| 11/11 | Fechar os arquivos e verificar no equipamento de apresentação | Versão final acessível, cópia de segurança e alternativa à demonstração ao vivo |
| 12/11 | Apresentar | Usar a versão ensaiada e as evidências conferidas |

### Prioridades até a entrega

1. Fechar a história que os resultados atuais sustentam, com artigo, slides e demonstração coerentes.
2. Resolver as orientações de PI IV/PLN e a revisão dos autores em paralelo à preparação dos slides. A pendência de revisão sistemática precisa de encaminhamento específico se continuar exigida.
3. Continuar a curadoria quando houver disponibilidade humana. Uma nova avaliação exige pares aptos, documentos independentes e protocolo próprio antes da execução.

A conclusão da apresentação não depende de prometer novos resultados de treinamento. Se a orientação docente exigir uma etapa adicional, revisar o cronograma assim que a exigência for conhecida.

## Roteiro inicial de 12 slides

Limite total informado: **15 minutos**. Conforme a orientação de PLN recuperada na p. 45 de `05_The Transformer Revolution.pdf`, reservar **dez minutos de exposição e cinco de perguntas**. Tempo de fala planejado: **9min30**, incluindo 1min30 de demonstração no slide 4, com 30 segundos de margem. Cada slide terá notas com fontes locais e créditos dos materiais utilizados.

| Slide | Título | Conteúdo e evidência visual | Tempo |
| --- | --- | --- | ---: |
| 1 | PaleographIA | Subtítulo: Transcrição assistida de manuscritos históricos de Jundiaí. Equipe, curso e data | 0:15 |
| 2 | Leitura de manuscritos históricos | Recorte original com dificuldades concretas de grafia, espaços e abreviaturas. Explicar a necessidade de conferência | 0:45 |
| 3 | Objetivo e escopo | Apoiar revisão humana e comparar dois reconhecedores nas mesmas entradas. Delimitar o estudo ao documento analisado | 0:30 |
| 4 | Revisão no PaleographIA | Fluxo de imagem, previsão, consulta de apoio e revisão salva com autoria. Demonstração em cópia | 1:30 |
| 5 | Documento e referência assistida | Corpo do 269r, 24 linhas, cinco blocos, 16 validadas e oito ressalvas. Distinguir traslado de 1767 e acontecimento de 1656, conforme artigo | 1:00 |
| 6 | Comparação dos reconhecedores | PP-OCRv5 mobile/ONNX e PP-OCRv6 medium/Kraken. Mesmos recortes, ordem fixa e pesos registrados | 0:50 |
| 7 | CER e WER | Explicação simples de substituições, deleções e inserções. Mostrar os denominadores e a agregação em blocos | 0:45 |
| 8 | Resultados nos 24 recortes | Tabela com CER/WER. Gráfico editável opcional com eixo partindo de zero. Rodapé com desenvolvimento, referência assistida e oito ressalvas | 1:00 |
| 9 | Erros e revisão humana | Exemplo de perda de conteúdo no PP-OCRv5 e de junção/separação de palavras no PP-OCRv6. Imagem e textos lado a lado | 1:00 |
| 10 | Expansão do corpus e ajuste fino | Oito geometrias validadas em 1795, textos pendentes, zero pares elegíveis. Ensaio de dois passos descrito separadamente | 0:35 |
| 11 | Limitações e próximos passos | Um documento de desenvolvimento, referência assistida e configurações diferentes. Próxima avaliação com novos pares revisados e separação documental | 0:40 |
| 12 | Conclusão e materiais | Achado limitado às configurações e entradas estudadas. Contribuição do fluxo auditável. Artigo, notebook, referências e declaração de IA acessíveis | 0:40 |

### Falas de apoio

**Abertura:** “O PaleographIA é um protótipo de apoio à leitura de manuscritos históricos de Jundiaí. Ele permite comparar a imagem com sugestões de reconhecimento e registrar decisões humanas com histórico.”

**Problema:** “A grafia histórica, as abreviaturas e a qualidade da imagem dificultam a leitura. Uma sugestão automática precisa ser conferida no documento. O projeto organiza essa conferência e preserva as dúvidas.”

**Método:** “Comparamos duas configurações pré-treinadas nos mesmos 24 recortes. Mantivemos separados o texto automático, a edição de apoio e as decisões humanas. A referência tem 16 linhas validadas e oito com ressalvas, incluídas nos cálculos.”

**Métricas:** “CER conta operações de edição em caracteres. WER faz o mesmo em palavras. Valores menores indicam menos divergência em relação à referência adotada. Aqui, somamos as operações dos cinco blocos antes de dividir pelos totais.”

**Resultados:** “Neste conjunto, o PP-OCRv6 medium teve CER de 15,11%, contra 58,45% no PP-OCRv5 mobile. O WER de 60,10% no PP-OCRv6 mostra que a correspondência de palavras ainda exige atenção. O resultado descreve essas configurações neste documento.”

**Expansão:** “O projeto também iniciou a ampliação do corpus e executou um ensaio técnico de ajuste fino. A revisão dos novos textos ainda está pendente. Por isso, a comparação apresentada usa os resultados congelados dos reconhecedores pré-treinados.”

**Fechamento:** “A contribuição é reunir uma comparação reproduzível e um fluxo de revisão que mantém a origem dos textos e as dúvidas. A próxima avaliação depende de novos pares revisados e documentos separados do desenvolvimento.”

## Demonstração proposta

Preparar em cópia separada do workspace, preservando as revisões reais. A preparação da cópia, a captura de telas e o teste de abertura ainda estão pendentes.

1. Abrir uma linha já escolhida e mostrar a imagem do manuscrito.
2. Exibir a previsão arquivada, identificando sua configuração e origem.
3. Mostrar uma divergência concreta e a edição de apoio separada.
4. Mostrar autoria, observação e histórico de uma revisão. Se houver gravação durante a apresentação, usar a cópia de demonstração e identificar a alteração como demonstração.
5. Encerrar com a tabela de métricas ou o notebook detalhado já executado da primeira entrega. Para demonstrar o recálculo sem internet, usar `recalcular.py` ou o notebook reduzido do pacote offline, dentro do tempo reservado.

Usar imagens ou vídeo previamente conferidos se a demonstração local falhar. Inferência ao vivo só deve entrar no roteiro depois de runtime, pesos e tempo de execução conferidos no equipamento usado.

## Perguntas para ensaiar

| Pergunta provável | Resposta sustentada pelas evidências |
| --- | --- |
| Vocês treinaram os modelos dessa comparação? | A comparação de 20/10 usa reconhecedores pré-treinados. O ensaio posterior de dois passos é uma etapa técnica separada |
| O PP-OCRv6 é melhor em qualquer manuscrito? | O menor erro foi observado nesta configuração e neste documento. A avaliação entre documentos ainda está pendente |
| Por que o WER é alto se o CER é menor? | Pequenas diferenças de letra e de espaço podem comprometer palavras inteiras. Os exemplos do artigo permitem mostrar os casos concretos |
| Quem produziu a referência? | O revisor identificado realizou conferência assistida pela edição. O protocolo preserva oito ressalvas e a origem das decisões |
| Por que há apenas 24 linhas? | O diagnóstico delimita o corpo do 269r. A expansão tem candidatos em revisão e ainda exige elegibilidade textual e documental |
| Qual foi o papel da IA? | Apoio a código, documentação, auditorias e preparação textual, conforme os registros. Atribuir a leitura humana ao revisor e conferir a declaração com os autores |
| Quanto tempo de trabalho o sistema economiza? | O experimento não mediu esforço humano. Uma futura medição exige desenho e registro específicos |
| A revisão sistemática está concluída? | Os registros mostram protocolo, buscas e leituras, com etapas ainda pendentes. A equipe precisa concluir o que a orientação docente exigir |

## Próximas decisões

- Quantidade de apresentadores e divisão das falas no formato de dez minutos mais cinco de perguntas.
- Exigência de slides, demonstração e artigo para 12/11, além de eventual entrega anterior.
- Orientação atual dos professores sobre enquadramento de PI IV e revisão sistemática.
- Destino dos slides e eventual modelo institucional.
- Disponibilidade da equipe para revisão, curadoria e ensaios.

## Pronto para apresentar

- [ ] Slides finais com fontes, imagens legíveis e resultados conferidos.
- [ ] Artigo revisado pelos autores e coerente com os slides.
- [ ] Notebook executável no ambiente escolhido, com o recálculo identificado.
- [ ] Demonstração e alternativa em imagens/vídeo verificadas.
- [ ] Créditos das fontes e declaração de uso de IA conferidos.
- [ ] Falas e contribuições da equipe confirmadas pelos participantes.
- [ ] Requisitos docentes atendidos ou pendências explicitamente encaminhadas.
- [ ] Ensaio dentro do tempo e cópia de segurança acessível.
