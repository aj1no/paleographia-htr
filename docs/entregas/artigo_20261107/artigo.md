# Ajuste fino do PP-OCRv6 e análise linguística de erros em manuscritos históricos de Jundiaí

Caio Augusto de Souza Soares; Guilherme Rodrigues Veiga; Rodolfo Vinicius Cima Takemoto; Tiago Galhardo Avelar

caio.soares01@aluno.cps.sp.gov.br; guilherme.veiga1@aluno.cps.sp.gov.br; rodolfo.takemoto@aluno.cps.sp.gov.br; tiago.avelar@aluno.cps.sp.gov.br

Faculdade de Tecnologia de Jundiaí — Ciência de Dados — 5º semestre

Jundiaí — SP

## Resumo

A leitura de manuscritos históricos em português dos séculos XVII a XIX exige tempo e formação paleográfica, recursos escassos em arquivos municipais. O PaleographIA é uma ferramenta aberta que sugere a leitura de cada linha para revisão humana rastreável. Este trabalho adapta o reconhecedor PP-OCRv6 medium a documentos do Arquivo Histórico de Jundiaí e acrescenta uma etapa de Processamento de Linguagem Natural depois do reconhecimento. O ajuste fino usou 191 linhas do Traslado do Auto de Criação da Vila, rotuladas pelo alinhamento automático com a transcrição paleográfica publicada, e, numa segunda configuração, 550 linhas públicas de processos da Inquisição. Em sete linhas de validação de outra mão (1795), o CER caiu de 14,20% para 10,72% e 10,14%, e o WER de 56,72% para 41,79% e 38,81%. A análise linguística dos erros mostra que o ajuste reduziu sobretudo a forma das letras e as palavras coladas; o que resta é, em boa parte, convenção de escrita. A pós-correção lexical por distância de Levenshtein e por TF-IDF de n-gramas de caracteres piorou o CER, porque o vocabulário de treino não cobre palavras corretas da validação. Os números são de desenvolvimento; o teste reservado ainda não foi usado.

**Palavras-chave:** reconhecimento de manuscritos; português histórico; ajuste fino; análise de erros; pós-correção lexical.

## Abstract

Reading handwritten historical Portuguese from the 17th to 19th centuries requires time and paleographic training, which municipal archives often lack. PaleographIA is an open tool that suggests a reading for each line, followed by traceable human review. This work adapts the PP-OCRv6 medium recognizer to documents from the Historical Archive of Jundiaí and adds a Natural Language Processing stage after recognition. Fine-tuning used 191 lines of a 1767 certified copy, labeled by automatic alignment with a published paleographic transcription, and, in a second configuration, 550 public lines from Inquisition trials. On seven validation lines by another hand (1795), CER dropped from 14.20% to 10.72% and 10.14%, and WER from 56.72% to 41.79% and 38.81%. Linguistic error analysis shows that fine-tuning mainly reduced letter-shape errors and merged words; most remaining errors concern writing conventions. Lexical post-correction by Levenshtein distance and by TF-IDF character n-grams increased CER, because the training vocabulary does not cover correct validation words. Results are from development; the reserved test set has not been used.

**Keywords:** handwritten text recognition; historical Portuguese; fine-tuning; error analysis; lexical post-correction.

## Introdução

O Arquivo Histórico de Jundiaí disponibiliza digitalmente atas, autos e registros dos séculos XVII a XIX, mas a maior parte desse material não tem transcrição. Ler essas páginas exige conhecer abreviaturas, grafias e formas de letra da época. O PaleographIA propõe um fluxo de apoio: a imagem é segmentada em linhas, um modelo sugere a leitura de cada linha e um humano confere, corrige e valida. A saída automática, a sugestão e a transcrição humana ficam sempre separadas, com autoria e histórico.

Num diagnóstico anterior do projeto, sobre 24 linhas do fólio 269r do Traslado, o PP-OCRv6 medium teve CER de 15,11% e WER de 60,10%, contra 58,45% e 94,58% do latin PP-OCRv5 mobile. Este trabalho parte do melhor dos dois e pergunta: (1) quanto o ajuste fino com documentos de Jundiaí reduz o erro em outra mão; (2) que tipos de erro sobram; e (3) se uma pós-correção lexical com o vocabulário histórico corrige o que o reconhecedor erra. As duas comparações pedidas pela disciplina são o modelo base contra os ajustados e o método de pós-correção A contra o B.

## Fundamentação teórica

O reconhecimento de texto manuscrito, ou HTR, integra fluxos de digitalização, segmentação, preparação de referência e uso do texto (Muehlberger et al., 2019). Ele pode ser visto como uma tarefa de sequência para sequência: a entrada é a imagem de uma linha e a saída, uma sequência de caracteres. O PP-OCRv6 combina um extrator convolucional (LCNetV4), um codificador LightSVTR e uma saída CTC; o vocabulário é de caracteres, sem tokenização em palavras, o que permite produzir grafias e abreviaturas fora de qualquer dicionário (Kiessling, 2026a). Kiessling (2026a; 2026b) mostra que o modelo pré-treinado em várias línguas pode ser adaptado a coleções históricas com poucos dados, mas com ganhos que variam conforme o acervo.

Esse ajuste é uma adaptação de domínio, a mesma ideia de modelos como LEGAL-BERT e BioMistral: partir de um modelo geral e continuar o treino em textos do domínio. Para o português histórico há poucos dados públicos rotulados; o conjunto Portuguese Handwriting 16th–19th c., com processos da Inquisição transcritos de forma conservadora (Baudry et al., 2024), e o modelo TraPrInq, treinado sobre ele (Oliveira, 2024), são exceções de licença aberta.

As métricas são o CER e o WER: a distância de edição (substituições, apagamentos e inserções) entre a predição e a referência, dividida pelo número de caracteres ou de palavras da referência. Elas cumprem para o HTR o papel de BLEU e ROUGE na geração de texto e dependem da normalização adotada (Unicode, espaços, caixa). Por fim, corrigir uma palavra reconhecida procurando a forma mais parecida num vocabulário é um problema de recuperação lexical, aparentado à busca por TF-IDF e BM25 usada em sistemas de geração aumentada por recuperação.

## Materiais e métodos

### Documentos e partições

Treino: o Traslado do Auto de Criação da Vila de Jundiaí, cópia de 1767 de um auto de 1656 (Jundiaí, s.d.), com a transcrição paleográfica publicada por Miranda (s.d.). Validação: sete linhas da sessão da Câmara de 25/06/1795, de outra mão, com referência diplomática validada pela equipe (345 caracteres). Teste reservado: o registro de um pagamento a Thomas Pardo (livro 0146, fólios 113v e 114r), recusado pelo código de treino e ainda sem uso. As imagens do Arquivo Histórico de Jundiaí, públicas no Acervo Digital da prefeitura, são usadas com autorização do arquivo, para fins não comerciais e com crédito ao acervo.

### Dados de treino

As linhas foram segmentadas pelo modelo blla do Kraken. Como a edição preserva a quebra de linha, um alinhamento monotônico por programação dinâmica, guiado pela leitura do modelo base, associou 277 linhas da edição aos recortes. A edição expande abreviaturas ("Ant." vira "Antonio"); treinar com isso ensinaria o modelo a expandir. Por isso foram retirados 102 pares com abreviatura, colchete editorial ou leitura-guia muito distante, restando 175, mais 16 linhas humanas do 269r. A configuração A usa essas 191 linhas, cada uma com uma variante de imagem (rotação, escala e contraste leves). A configuração B soma 550 linhas da Inquisição, até duas por página, sem variantes.

### Ajuste fino

Ambas partem do checkpoint PP-OCRv6 medium, treinado com ketos (Kraken 7.1) numa GPU GTX 1650 de 4 GB: lote de 2 linhas com acumulação de 4, AdamW com taxa de 2×10⁻⁵, aquecimento e decaimento cosseno, rótulos em NFD e parada após oito validações sem melhora. Com lotes tão pequenos, as estatísticas de normalização em lote se degradavam e derrubavam o acerto; elas foram congeladas nos valores do checkpoint. Os dois treinos foram gravados em vídeo, com registro de cada lote, das validações e do uso da GPU.

### Avaliação, análise de erros e pós-correção

Os três modelos leem os mesmos recortes de validação. O CER e o WER são calculados em NFC, com espaços simplificados e preservando caixa, acentos, pontuação e grafia. Para a análise de erros, cada linha é alinhada à referência por Levenshtein com rastreio, e cada operação recebe um tipo, por prioridade: espaço, pontuação, abreviatura, maiúscula, acento ou til, grafia histórica (i/j, u/v, i/y, s/z, c/s e outras alternâncias da época), nome próprio e forma da letra.

Na pós-correção, cada palavra com pelo menos três letras e fora do vocabulário recebe uma sugestão. O método A escolhe a forma de menor distância de Levenshtein (até 1 edição em palavras de até cinco letras e até 2 nas maiores). O método B representa as palavras por bigramas e trigramas de caracteres ponderados por TF-IDF e escolhe a de maior cosseno, com mínimo de 0,5. O vocabulário (2.188 formas) vem só das transcrições de treino e do léxico histórico do projeto; os limiares foram fixados antes de olhar a validação.

## Resultados e discussão

**Tabela 1 — Validação de 1795 (7 linhas)**

| Modelo | CER | WER |
| --- | ---: | ---: |
| PP-OCRv6 base | 14,20% | 56,72% |
| Ajustado A (Traslado) | 10,72% | 41,79% |
| Ajustado B (Traslado + Inquisição) | 10,14% | 38,81% |

Fonte: treinos gravados em 06/11 (A) e 07/11 (B). Números de desenvolvimento.

O ajuste fino reduziu o erro em uma mão que não estava no treino. Em "ando sobre o bem commum do povo", o base leu "lando sobre obem commûm dopovo" e o B, "lando sobre o bem commum do povo". A diferença entre A e B, cerca de 2 caracteres em 345, não permite dizer que os dados da Inquisição ajudam: um treino anterior de A, com a mesma configuração, chegou a 12,17%, e o treino na GPU não é determinístico. A acurácia de caracteres correspondente fica perto de 90%, mas o WER mostra que ainda cerca de duas em cada cinco palavras têm algum erro.

**Tabela 2 — Erros por tipo (de 49 e 35 erros)**

| Tipo de erro | Base | Ajustado B |
| --- | ---: | ---: |
| Forma da letra | 14 | 7 |
| Grafia histórica | 11 | 9 |
| Espaço (palavras coladas) | 7 | 3 |
| Maiúscula/minúscula | 5 | 5 |
| Acento ou til | 5 | 4 |
| Abreviatura | 4 | 4 |
| Pontuação e nome próprio | 3 | 3 |

Do base para o B, os erros de forma da letra caíram pela metade e os de espaço, de 7 para 3. O restante é, em boa parte, convenção de escrita: maiúsculas onde a referência diplomática registra minúsculas ("Comarca da Cidade"), s/z ("Cazas", "Prezidente"), i/j ("Iuis" por "Juiz") e a abreviatura "Nˢᵃ", que o modelo expande em "Nossa". Depois dos espaços, as confusões mais frequentes no B são c/C, s/z e j/I. Isso indica que parte do CER mede diferenças de convenção, não de leitura, e que a política de transcrição pesa tanto quanto o modelo.

**Tabela 3 — Pós-correção no modelo B (CER / WER)**

| Saída | CER | WER |
| --- | ---: | ---: |
| Bruta | 10,14% | 38,81% |
| Método A: Levenshtein | 12,75% | 35,82% |
| Método B: TF-IDF de n-gramas | 16,23% | 41,79% |

A pós-correção piorou o CER nos três modelos, com os dois métodos. O método A melhorou o WER nos três; o B, só no modelo base. As correções certas existem ("Selvador" → "Salvador", "ainco" → "cinco"), mas 14 das 51 palavras distintas da validação não estão no vocabulário, entre elas "noventa", "morada" e "comarca", e são trocadas por vizinhas erradas ("noventa" → "corenta"). O método B, mais permissivo, faz trocas piores ("Iundiahi" → "Ahi"). Com um vocabulário pequeno, a correção automática erra mais do que acerta; ela só serve como sugestão para o revisor. O uso de um grande modelo de linguagem fica para trabalho futuro, pelo risco de modernizar a grafia ou inventar palavras.

### Curiosidade: um reconhecedor treinado do zero

Para ver quanto pesa partir de um modelo pré-treinado, um reconhecedor CRNN-CTC (convoluções e BiLSTM, 6,3 milhões de parâmetros) foi treinado sem nenhum peso prévio, em uma noite na mesma GPU, com 12.543 linhas públicas da Inquisição e as 191 do Traslado. Numa segunda versão, o codificador passou antes por um pré-treino não supervisionado: trechos de cada linha eram apagados e o modelo reconstruía os pixels, sem ver texto algum. O checkpoint foi escolhido numa validação separada da Inquisição (953 linhas de 20 documentos); a validação de 1795 foi lida uma única vez, no fim.

**Tabela 4 — Modelos treinados do zero, validação de 1795**

| Modelo | CER | WER |
| --- | ---: | ---: |
| Do zero, todas as linhas | 16,23% | 53,73% |
| Pré-treino + todas as linhas | 15,94% | 50,75% |
| Do zero, 5% das linhas | 71,88% | 101,49% |
| Pré-treino + 5% das linhas | 28,12% | 71,64% |

Fonte: treinos de 07 e 08/11, fora do pipeline principal. Números exploratórios.

O melhor modelo do zero fica perto do PP-OCRv6 sem ajuste (14,20%) e atrás dos ajustados: com poucos dados rotulados, partir de um modelo pré-treinado continua valendo. O pré-treino não supervisionado quase não muda o resultado quando todas as linhas têm texto, mas, com só 5% delas (637 linhas), derruba o CER de 71,88% para 28,12%. Como o acervo tem muito mais imagens do que transcrições, isso sugere um caminho para reduzir o custo de rotulação.

## Limitações

A validação tem sete linhas de uma única mão e foi usada para escolher o checkpoint, o que torna os números otimistas e sujeitos a variação de uma ou duas linhas. O treino na GPU não é determinístico, e a comparação entre A e B fica dentro dessa variação. Os rótulos do Traslado vêm da edição, não de leitura diplomática independente. O teste reservado ainda espera a transcrição às cegas da equipe; só depois todos os modelos serão avaliados nele, uma única vez.

## Conclusões

O ajuste fino do PP-OCRv6 com 191 linhas de um documento de Jundiaí reduziu o CER de 14,20% para cerca de 10–11% e o WER de 57% para 39–42% numa mão diferente, com custo de duas a quatro horas numa GPU de notebook. A análise linguística mostra que o modelo aprendeu a forma das letras e a separação das palavras, e que o erro restante se concentra em convenções de escrita, o que pede políticas de transcrição explícitas. A pós-correção lexical, nas condições testadas, não ajuda. O resultado reforça o desenho do PaleographIA: o modelo sugere, e o humano valida.

## Disponibilidade dos materiais

Código, dados de treino sem imagens, provas dos treinos gravados, o Notebook 3 e o experimento do zero estão no [repositório público](https://github.com/aj1no/paleographia-htr). A licença MIT cobre o código; documentos e edições têm condições próprias.

## Comentários

Ferramentas de IA: Codex (OpenAI), Antigravity, ChatGPT (OpenAI) e Claude Code (Anthropic). Codex apoiou a programação, a organização dos artefatos e a versão de 23/10 deste artigo. Claude Code apoiou o pipeline de ajuste fino, a análise de erros, a pós-correção, o Notebook 3, o experimento do zero e a revisão deste texto. O uso de Antigravity e ChatGPT, e os detalhes de cada integrante, estão na planilha de documentação do uso de IA. Nenhuma ferramenta de IA validou leituras: as referências humanas são da equipe.

## Referências bibliográficas

BAUDRY, Hervé et al. Portuguese Handwriting 16th-19th c. Zenodo, 2024. [Registro 13986218](https://zenodo.org/records/13986218). Licença CC BY 4.0.

JUNDIAÍ. Acervo Digital. Traslado do Auto de Criação da Vila de Jundiaí no Ano de 1656, a 14 Dezembro. Ficha PT/TT/PBR/0004/026, s.d. [Fonte institucional](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

KIESSLING, Benjamin. A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition. arXiv:2609.20064v1, 2026a. Preprint. [Versão consultada](https://arxiv.org/abs/2609.20064v1).

KIESSLING, Benjamin. PP-OCRv6 (medium) multilingual handwritten and printed text recognition model. Zenodo, v1, 2026b. [DOI: 10.5281/zenodo.21788410](https://doi.org/10.5281/zenodo.21788410).

MIRANDA, Ana Caroline Carvalho. Transcrição paleográfica do Traslado do Auto de Criação da Vila de Jundiaí. Revisão de Thiago Paschoal. Memorabilia Paleografia e Diplomática, s.d. [Ficha institucional](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

MUEHLBERGER, Guenter et al. Transforming scholarship in the archives through handwritten text recognition: Transkribus as a case study. Journal of Documentation, v. 75, n. 5, p. 954–976, 2019. [DOI: 10.1108/JD-07-2018-0114](https://doi.org/10.1108/JD-07-2018-0114).

OLIVEIRA, Weslley. TraPrInq: transcription model to recognize Portuguese handwritten texts from the 16th to 19th centuries. Zenodo, v1, 2024. [Registro 14543904](https://zenodo.org/records/14543904). Licença CC BY 4.0.
