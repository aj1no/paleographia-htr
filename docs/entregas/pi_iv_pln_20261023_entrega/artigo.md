# Diagnóstico de reconhecimento de 24 linhas do fólio 269r de Jundiaí

Caio Augusto de Souza Soares; Guilherme Rodrigues Veiga; Rodolfo Vinicius Cima Takemoto; Tiago Galhardo Avelar

caio.soares01@aluno.cps.sp.gov.br; guilherme.veiga1@aluno.cps.sp.gov.br; rodolfo.takemoto@aluno.cps.sp.gov.br; tiago.avelar@aluno.cps.sp.gov.br

Faculdade de Tecnologia de Jundiaí — Ciência de Dados — 5º semestre

Jundiaí — SP

## Resumo

Este trabalho compara dois reconhecedores pré-treinados em 24 linhas do fólio 269r do Traslado do Auto de Criação da Vila de Jundiaí. Avaliam-se latin PP-OCRv5 mobile, em ONNX, e PP-OCRv6 medium, em Kraken, com recortes idênticos e referência assistida por edição publicada. Mantêm-se dezesseis linhas validadas e oito com ressalvas, sem confirmação independente das dúvidas. A avaliação aplica Unicode NFC e colapso de espaços, preservando grafia, caixa e diacríticos, e agrega contagens de cinco blocos. O PP-OCRv5 apresentou CER de 58,45% e WER de 94,58%; o PP-OCRv6, CER de 15,11% e WER de 60,10%. As divergências incluem perda de conteúdo, espaçamento, letras e acentuação. A análise relaciona política textual, reconhecimento histórico e limites de transferência. Os resultados caracterizam as configurações neste documento de desenvolvimento; não estimam generalização, economia de revisão humana ou ganho de ajuste fino.

**Palavras-chave:** reconhecimento de manuscritos; português histórico; referência assistida; CER; WER.

## Abstract

This study compares two pretrained recognizers on 24 lines from folio 269r of the certified copy of the founding record of the town of Jundiaí. We evaluate latin PP-OCRv5 mobile, running in ONNX, and PP-OCRv6 medium, running in Kraken, using identical crops and a reference assisted by a published edition. Sixteen validated lines and eight lines with reading reservations are retained, without independent confirmation of unresolved readings. Evaluation applies Unicode NFC and whitespace collapsing while preserving spelling, case, and diacritics, and aggregates edit counts across five blocks. PP-OCRv5 achieved a CER of 58.45% and a WER of 94.58%; PP-OCRv6 achieved a CER of 15.11% and a WER of 60.10%. Differences include content loss, spacing, letters, and accents. The analysis connects transcription policy, historical recognition, and transfer limitations. The results characterize the configurations on this development document; they do not estimate generalization, savings in human revision effort, or gains from fine-tuning.

**Keywords:** handwritten text recognition; historical Portuguese; assisted reference; CER; WER.

## Introdução

A conversão de manuscritos em texto pesquisável exige definir como grafias, abreviaturas, espaços e sinais serão representados. Sousa e Trippel (2006) descrevem a reestruturação de um corpus de português histórico com padronização da marcação e uso de padrões abertos. Essa perspectiva relaciona a organização dos dados à possibilidade de reutilização: a avaliação de um reconhecedor depende tanto das imagens quanto da referência textual escolhida.

O PaleographIA é um protótipo local de transcrição assistida de manuscritos de Jundiaí, com inspeção de recortes e registro de revisões. Neste estudo, a pergunta é: como latin PP-OCRv5 mobile e PP-OCRv6 medium se comportam sobre os mesmos 24 recortes do fólio 269r, sob uma política de referência assistida que conserva dúvidas de leitura? O objetivo é comparar essas configurações, quantificar divergências e interpretar seus limites. A contribuição consiste em um diagnóstico com alvos, saídas e contagens rastreáveis, acompanhado de análise dos erros.

As próximas seções apresentam a fundamentação, o trabalho proposto, o método, os resultados e as limitações. O experimento é de 20/10/2026; a reconferência e a revisão bibliográfica posteriores preservam os alvos avaliados.

## Fundamentação teórica

Muehlberger et al. (2019, p. 958–963) descrevem o reconhecimento de texto manuscrito, ou HTR, como parte de um fluxo de imagens, segmentação, preparação de referência e uso do texto. No estudo do Transkribus, a consistência das transcrições abrange grafias, símbolos e abreviaturas, com convenções escolhidas conforme a finalidade. Os casos arquivísticos apresentados têm condições diferentes e não formam um benchmark uniforme. Para o PaleographIA, essa discussão fundamenta a explicitação da política textual e a separação entre saída automática, edição de apoio e revisão humana. A consistência computacional da referência não resolve uma dúvida paleográfica.

Cui et al. (2025) apresentam PP-OCRv5 no relatório PaddleOCR 3.0 como solução de reconhecimento multilíngue. A documentação RapidOCR descreve modelos convertidos para diferentes ambientes, incluindo ONNX (RapidAI, s.d.). Essas fontes caracterizam os componentes; seus resultados publicados não substituem a avaliação do checkpoint latino mobile utilizado neste trabalho.

Kiessling (2026a, p. 3–6) investiga a adaptação de PP-OCRv6 ao reconhecimento histórico e sua comparação com uma rede convolucional recorrente, ou CRNN. A configuração estudada combina LCNetV4, LightSVTR e saída CTC; o decodificador autorregressivo auxiliar é usado no treino e descartado na inferência. O estudo distingue treino do zero, pré-treino generalista e ajuste fino, com ganhos dependentes dos dados e do orçamento. Trata-se de preprint v1, sem revisão por pares comprovada nesta consulta.

O artigo experimental e a ficha do modelo local são fontes distintas. O preprint descreve entradas históricas com altura de 96 pixels e pré-treino real em 37 línguas; a ficha do checkpoint medium informa altura de 128 pixels e cobertura de 44 línguas (Kiessling, 2026a, p. 4–5; 2026b). Portanto, não se atribuem automaticamente ao peso local todas as condições experimentais do preprint. A ficha também informa mistura de convenções de transcrição, capaz de afetar abreviaturas e grafias na saída.

CER e WER dependem do protocolo de representação e agregação. Kiessling (2026a, p. 6) usa Unicode NFD e conversão de caracteres de espaço para U+0020; este trabalho usa NFC e colapso de espaços. Além disso, médias macro por língua não equivalem à microagregação local. As taxas externas não são, assim, um benchmark direto para Jundiaí. A literatura foi selecionada de forma dirigida para interpretar o diagnóstico; não se apresenta uma revisão sistemática concluída.

## O trabalho proposto

O diagnóstico reúne recortes preparados no PaleographIA, dois reconhecedores e um protocolo comum de comparação textual. A geometria e a ordem dos recortes foram fixadas antes do reconhecimento. Mantêm-se separados os textos automáticos, a edição de apoio e as decisões humanas. A hipótese operacional é que as configurações podem apresentar padrões diferentes de divergência na mesma entrada; o estudo descreve esses padrões, sem isolar o efeito causal da versão da arquitetura.

## Materiais e métodos

### Documento e referência assistida

A ficha do acervo identifica o documento pelo código PT/TT/PBR/0004/026 e descreve um traslado produzido em 1767, relativo à criação da vila em 1656 (Jundiaí, s.d.). O recorte contém as 24 linhas do corpo do fólio 269 reto, sem cabeçalho, resumo ou verso. A data do acontecimento não é tratada como data de produção da cópia.

A edição de apoio é atribuída a Ana Caroline Carvalho Miranda; Thiago Paschoal consta como revisor no PDF consultado (Miranda, s.d.). Rodolfo Vinicius Cima Takemoto realizou a conferência humana registrada no projeto. Nas dúvidas, adotaram-se leituras da edição com proveniência. Na referência congelada de 20/10, dezesseis linhas têm estado validado e oito preservam ressalvas; todas entram na avaliação.

As ressalvas correspondem às linhas 11, 15, 16, 17, 19, 20, 23 e 24. Incluem sinais e pontuação, trechos das linhas 15/16/20, ministros/menistros, orgente/ergente, os dois s de Justissa e a abreviatura final. Preservaram-se grafias e quebras físicas, como Capi/tão, Par/nahiba e Jus/tissa. A forma Magᵈᵉ permanece no alvo; seu desenvolvimento editorial, Magestade, é informação separada.

Em 21/10, o mesmo revisor reconferiu os oito casos com imagem e edição, gerando 17 registros. Houve confirmações pontuais, especialmente nas linhas 15, 16 e 20, mas permaneceram ambiguidades e adoções editoriais. A reconferência não é segunda leitura independente e não altera os alvos ou o total validado. A tabela completa das decisões integra o notebook complementar.

### Configurações e execução

Cada reconhecedor recebeu os mesmos 24 PNGs, na mesma ordem, por um manifesto sem texto humano. Foram executadas 24 inferências por configuração, totalizando 48, sem falhas. Ambos operaram em CPU e float32, com pesos identificados por SHA-256. O latin PP-OCRv5 mobile utilizou ONNX Runtime; o PP-OCRv6 medium utilizou Kraken 7.1 em contêiner local com imagem fixada. Cada configuração manteve seu pré-processamento nativo, registrado nas evidências.

Não houve detecção automática de linhas, treinamento, ajuste fino ou pós-correção no experimento de 20/10. As diferenças de variante, pré-treino, implementação e preparação das entradas impedem atribuir o resultado apenas à versão da arquitetura. O ensaio técnico posterior de ajuste fino do projeto possui registro separado e não produz os resultados desta comparação.

### Métricas e auditoria

Aplicaram-se Unicode NFC e colapso de espaços aos alvos e às saídas, preservando caixa, diacríticos e grafia. As linhas foram concatenadas em cinco blocos completos: 1–5, 6–10, 11–15, 16–20 e 21–24. Somaram-se as operações dos blocos antes da divisão, em vez de calcular uma média simples das taxas por linha.

CER = (S + D + I) / Ncar; WER = (S + D + I) / Npal.

S, D e I indicam substituições, deleções e inserções; Ncar e Npal são os totais de caracteres e palavras da referência. As taxas são apresentadas em porcentagem. Os denominadores são 1.112 caracteres e 203 palavras. Espaços internos aos blocos entram em Ncar; os quatro limites entre blocos não acrescentam caracteres. Uma falha seria contada como saída vazia, preservando a cobertura da avaliação.

O notebook recalcula as métricas a partir das saídas congeladas, sem carregar modelos. Os auditores verificam hashes, pixels, IDs e ressalvas e conferem as distâncias por uma implementação independente de Levenshtein. A reexecução de 22/10 reproduziu os cálculos da referência de 20/10; as decisões posteriores não foram usadas para selecionar linhas ou mudar o protocolo.

## Resultados e discussão

A Tabela 1 apresenta as taxas microagregadas. O PP-OCRv6 medium teve menos divergências nos dois níveis. As diferenças são 43,35 pontos percentuais em CER e 34,48 em WER, calculadas a partir das contagens antes do arredondamento. Esses valores descrevem as configurações neste alvo e não são porcentagens simples de acerto.

**Tabela 1 — Divergências nos mesmos 24 recortes**

| Configuração | CER | WER |
| --- | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 94,58% |
| PP-OCRv6 medium / Kraken | 15,11% | 60,10% |

Fonte: experimento do PaleographIA de 20/10/2026. Referência assistida; oito ressalvas preservadas.

Em caracteres, os totais são 650/1.112 operações para PP-OCRv5 e 168/1.112 para PP-OCRv6. O primeiro acumulou 200 substituições, 444 deleções e seis inserções; o segundo, 96 substituições, 54 deleções e 18 inserções. Em palavras, são 192/203 e 122/203 operações, com contagens S/D/I de 108/84/0 e 95/22/5, respectivamente. O bloco 21–24 apresentou o maior CER nos dois reconhecedores: 71,20% e 21,74%.

A perda de conteúdo domina a saída do PP-OCRv5. Na linha 22, o alvo por titullos de Sismaria as Lavrão outros que mais resultou em tiay cm es uhy g. O exemplo mostra a necessidade de verificar a configuração no manuscrito concreto. No PP-OCRv6, aparecem junções como Anno do → Annodo e separações como Cabedo → Cabe do e onde → on de. Há também Jundiahy → Sundiahy, Sismaria → Sismario e titullos → titllos. Capitão → Capitao. combina diferenças de acento e pontuação. Pequenas alterações podem impedir a correspondência de palavras inteiras, ajudando a interpretar o WER de 60,10%.

Os resultados não resolvem ministros/menistros, orgente/ergente, Justissa ou sinais finais. Essas leituras coincidem com ressalvas da referência. Magᵈᵉ → Magi envolve também a representação da abreviatura com letras elevadas. As operações medem divergência em relação ao alvo adotado, sem transformar a previsão do reconhecedor em decisão paleográfica.

Muehlberger et al. (2019, p. 963) mostram que uma saída imperfeita pode servir à localização de conteúdo. Entretanto, este diagnóstico não mediu recuperação de informação nem esforço de revisão. Kiessling (2026a, p. 8–9) relata ganhos não uniformes após adaptação. No MAKHZAN, o medium passa de CER macro de 17,99% para 18,82% após ajuste, enquanto o WER macro diminui de 59,06% para 58,37%. O exemplo reforça a necessidade de interpretar as métricas em conjunto, sem transportar suas taxas ou sua causa para o experimento local.

## Limitações

O estudo usa 24 linhas de um documento empregado no desenvolvimento e em consultas lexicais anteriores. As linhas não são amostras documentais independentes, e o fólio não constitui teste reservado. Não foram estimadas generalização, incerteza estatística, desempenho entre escribas ou qualidade de tarefas posteriores de PLN.

A referência é assistida pela edição, com oito ressalvas e sem segunda leitura humana independente. Parte das divergências pode decorrer das decisões de representação. Não foi auditada eventual sobreposição com corpora externos de pré-treino. Diferenças de configuração impedem inferência causal de superioridade arquitetural; os tempos disponíveis também não sustentam comparação de velocidade ou economia de trabalho humano.

A separação documental merece atenção inclusive na literatura: Kiessling (2026a, p. 5) avalia poucos exemplos com treino e teste na mesma página e explicita a restrição de MAKHZAN quanto à independência entre documentos. A ampliação local requer reservar documentos antes de usá-los na seleção de modelos ou parâmetros. A bibliografia dirigida não substitui a revisão sistemática em andamento.

## Conclusões

Nos mesmos 24 recortes e sob a política textual adotada, o PP-OCRv6 medium apresentou menos divergências que o latin PP-OCRv5 mobile. A análise identifica perda de conteúdo no PP-OCRv5 e dificuldades de espaços, letras e sinais no PP-OCRv6. O WER observado e as dúvidas da referência mantêm a revisão humana como componente necessário do fluxo estudado.

A contribuição é um diagnóstico auditável que relaciona resultados, política textual e limites de domínio. Sua conclusão se restringe ao documento de desenvolvimento e às configurações executadas. Uma avaliação mais ampla requer novos pares revisados, separação documental e protocolo próprio; o treinamento posterior do projeto não é evidência de ganho nesta comparação.

## Disponibilidade dos materiais

Alvos, saídas, hashes, scripts e auditorias estão no [experimento congelado](https://github.com/aj1no/paleographia-htr/tree/7c9a1b7942fec4f5c7809ccc23e6f96ce44f665b/docs/experimentos/traslado_269r_reconhecedores_24_20261020). O [notebook e a reconferência de 22/10](https://github.com/aj1no/paleographia-htr/tree/7f048a34ab9f406e42d22241e98146b85b81bf51/docs/entregas/pi_iv_pln_20261022) permitem auditar os cálculos. As licenças e condições das fontes documentais são próprias; a licença MIT refere-se ao código.

## Comentários

Ferramenta: Codex, da OpenAI. Utilização: apoio à programação, organização dos artefatos, verificações de reprodução, leitura e fichamento de Muehlberger et al. (2019) e Kiessling (2026a), revisão textual e preparação deste artigo. PP-OCRv5 e PP-OCRv6 produziram as saídas avaliadas. A leitura humana permanece atribuída ao revisor identificado; o uso de IA não é validação paleográfica independente.

## Referências bibliográficas

CUI, Cheng et al. PaddleOCR 3.0 Technical Report. arXiv:2507.05595v1, 2025. [DOI: 10.48550/arXiv.2507.05595](https://doi.org/10.48550/arXiv.2507.05595).

JUNDIAÍ. Acervo Digital. Traslado do Auto de Criação da Vila de Jundiaí no Ano de 1656, a 14 Dezembro. Ficha PT/TT/PBR/0004/026, s.d. [Fonte institucional](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro). Acesso em: 23 out. 2026.

KIESSLING, Benjamin. A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition. arXiv:2609.20064v1, 17 set. 2026a. Preprint. [Versão consultada](https://arxiv.org/abs/2609.20064v1).

KIESSLING, Benjamin. PP-OCRv6 (medium) multilingual handwritten and printed text recognition model. Zenodo, v1, 2026b. [DOI: 10.5281/zenodo.21788410](https://doi.org/10.5281/zenodo.21788410).

MIRANDA, Ana Caroline Carvalho. Transcrição paleográfica do Traslado do Auto de Criação da Vila de Jundiaí. Revisão de Thiago Paschoal, conforme PDF consultado. Memorabilia Paleografia e Diplomática, s.d. [Ficha institucional](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro). Acesso em: 23 out. 2026.

MUEHLBERGER, Guenter et al. Transforming scholarship in the archives through handwritten text recognition: Transkribus as a case study. Journal of Documentation, v. 75, n. 5, p. 954–976, 2019. [DOI: 10.1108/JD-07-2018-0114](https://doi.org/10.1108/JD-07-2018-0114).

RAPIDAI. RapidOCR Model List. Documentação técnica, s.d. [Fonte](https://rapidai.github.io/RapidOCRDocs/main/en/model_list/). Acesso em: 23 out. 2026.

SOUSA, Maria Clara Paixão de; TRIPPEL, Thorsten. Building a historical corpus for Classical Portuguese: some technological aspects. In: Proceedings of the Fifth International Conference on Language Resources and Evaluation. Genoa: ELRA, 2006. [Registro e resumo](https://aclanthology.org/L06-1222/).
