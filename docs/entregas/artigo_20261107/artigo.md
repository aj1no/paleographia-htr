# Ajuste fino do PP-OCRv6 e análise linguística de erros em manuscritos históricos de Jundiaí

Caio Augusto de Souza Soares; Guilherme Rodrigues Veiga; Rodolfo Vinicius Cima Takemoto; Tiago Galhardo Avelar

caio.soares01@aluno.cps.sp.gov.br; guilherme.veiga1@aluno.cps.sp.gov.br; rodolfo.takemoto@aluno.cps.sp.gov.br; tiago.avelar@aluno.cps.sp.gov.br

Faculdade de Tecnologia de Jundiaí — Ciência de Dados — 5º semestre

Jundiaí — SP

## Resumo

A leitura de manuscritos históricos em português dos séculos XVII a XIX exige tempo e formação paleográfica, recursos escassos em arquivos municipais. O PaleographIA é uma ferramenta aberta que sugere a leitura de cada linha para revisão humana rastreável. Este trabalho adapta o reconhecedor PP-OCRv6 medium a documentos do Arquivo Histórico de Jundiaí e acrescenta uma etapa de Processamento de Linguagem Natural depois do reconhecimento. O ajuste fino usou 191 linhas do Traslado do Auto de Criação da Vila, rotuladas pelo alinhamento automático com a transcrição paleográfica publicada, e, em outras configurações, 550 linhas públicas de processos da Inquisição (B) ou 63 linhas das Posturas Municipais de 1831 validadas pela equipe (D1). Em sete linhas de validação de outra mão (1795), o CER caiu de 14,20% para 10,72% (A), 10,14% (B) e 9,86% (D1). A análise linguística dos erros mostra que o ajuste reduziu sobretudo a forma das letras e as palavras coladas; o que resta é, em boa parte, convenção de escrita. A pós-correção lexical por distância de Levenshtein e por TF-IDF de n-gramas de caracteres piorou o CER, porque o vocabulário de treino não cobre palavras corretas da validação. No teste reservado, transcrito às cegas pela equipe e avaliado uma única vez (49 linhas de duas outras mãos), o CER foi de 64,0% no base, 60,5% e 60,9% em A e B e 55,4% no D1, cuja diferença pareada para o B vai de −8,1 a −3,3 pontos. O ganho veio do contrato de escrita densa (74% → 66%); no pagamento, de letra regular, o erro fica perto de 28–29%. Dados do próprio acervo ajudaram mais que dados de fora, mas a generalização para outras mãos ainda é limitada. Uma leitura modernizada por regras e frequência, feita sobre o texto validado, reduziu o WER contra a edição modernizada do Arquivo de 44,7% para 30,5% no contrato.

**Palavras-chave:** reconhecimento de manuscritos; português histórico; ajuste fino; análise de erros; pós-correção lexical.

## Abstract

Reading handwritten historical Portuguese from the 17th to 19th centuries requires time and paleographic training, which municipal archives often lack. PaleographIA is an open tool that suggests a reading for each line, followed by traceable human review. This work adapts the PP-OCRv6 medium recognizer to documents from the Historical Archive of Jundiaí and adds a Natural Language Processing stage after recognition. Fine-tuning used 191 lines of a 1767 certified copy, labeled by automatic alignment with a published paleographic transcription, and, in other configurations, 550 public lines from Inquisition trials (B) or 63 lines of the 1831 municipal ordinances validated by the team (D1). On seven validation lines by another hand (1795), CER dropped from 14.20% to 10.72% (A), 10.14% (B) and 9.86% (D1). Linguistic error analysis shows that fine-tuning mainly reduced letter-shape errors and merged words; most remaining errors concern writing conventions. Lexical post-correction by Levenshtein distance and by TF-IDF character n-grams increased CER, because the training vocabulary does not cover correct validation words. On the reserved test set, transcribed blind by the team and evaluated only once (49 lines by two other hands), CER was 64.0% for the base model, 60.5% and 60.9% for A and B, and 55.4% for D1, whose paired difference to B ranges from −8.1 to −3.3 points. The gain came from the densely written contract (74% → 66%); on a payment record in a regular hand, error stays near 28–29%. Data from the archive itself helped more than external data, but generalization to other hands is still limited. A rule- and frequency-based modernized reading of the validated text reduced WER against the Archive's modernized edition from 44.7% to 30.5% on the contract.

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

Treino: o Traslado do Auto de Criação da Vila de Jundiaí, cópia de 1767 de um auto de 1656 (Jundiaí, s.d.), com a transcrição paleográfica publicada por Miranda (s.d.). Validação: sete linhas da sessão da Câmara de 25/06/1795, de outra mão, com referência diplomática validada pela equipe (345 caracteres). Teste reservado, recusado pelo código de treino: o registro de um pagamento a Thomas Pardo (livro 0146, fólios 113v e 114r, 1759) e, porque as linhas finais do pagamento se mostraram ilegíveis, um contrato de 1763 (Cartório Olgado, livro 12), escolhido só pela legibilidade, antes de qualquer modelo rodar. Dois integrantes transcreveram as linhas às cegas, com o reconhecedor desligado; a referência (49 linhas, 1.644 caracteres) foi congelada, com hashes, antes da avaliação. Para a configuração D1 entram as Posturas Municipais de 1831 (fólios 100r, 100v e 101r, 94 linhas lidas e validadas pela equipe): o 101r (31 linhas) fica fora do treino e soma-se a 1795 na validação. As imagens do Arquivo Histórico de Jundiaí, públicas no Acervo Digital da prefeitura, são usadas com autorização do arquivo, para fins não comerciais e com crédito ao acervo.

### Dados de treino

As linhas foram segmentadas pelo modelo blla do Kraken. Como a edição preserva a quebra de linha, um alinhamento monotônico por programação dinâmica, guiado pela leitura do modelo base, associou 277 linhas da edição aos recortes. A edição expande abreviaturas ("Ant." vira "Antonio"); treinar com isso ensinaria o modelo a expandir. Por isso foram retirados 102 pares com abreviatura, colchete editorial ou leitura-guia muito distante, restando 175, mais 16 linhas humanas do 269r. A configuração A usa essas 191 linhas, cada uma com uma variante de imagem (rotação, escala e contraste leves). A configuração B soma 550 linhas da Inquisição, até duas por página, sem variantes. A D1 soma às 191 linhas do Traslado as 63 linhas das Posturas dos fólios 100r e 100v, com uma variante cada.

### Ajuste fino

Todas partem do checkpoint PP-OCRv6 medium, treinado com ketos (Kraken 7.1) numa GPU GTX 1650 de 4 GB: lote de 2 linhas com acumulação de 4, AdamW com taxa de 2×10⁻⁵, aquecimento e decaimento cosseno, rótulos em NFD e parada após oito validações sem melhora. Com lotes tão pequenos, as estatísticas de normalização em lote se degradavam e derrubavam o acerto; elas foram congeladas nos valores do checkpoint. Os treinos foram gravados, com registro de cada lote, das validações e do uso da GPU. Ao todo houve cinco (A, B, C, D1 e D2), somando 19 h 33 min de GPU; C e D2 testaram variações descritas no repositório. Com só sete linhas, a validação de 1795 escolhia checkpoints quase iniciais; por isso o D1 escolhe o seu nas 38 linhas do 101r mais 1795.

### Avaliação, análise de erros e pós-correção

Todos os modelos leem os mesmos recortes de validação. O CER e o WER são calculados em NFC, com espaços simplificados e preservando caixa, acentos, pontuação e grafia. Para a análise de erros, cada linha é alinhada à referência por Levenshtein com rastreio, e cada operação recebe um tipo, por prioridade: espaço, pontuação, abreviatura, maiúscula, acento ou til, grafia histórica (i/j, u/v, i/y, s/z, c/s e outras alternâncias da época), nome próprio e forma da letra.

Na pós-correção, cada palavra com pelo menos três letras e fora do vocabulário recebe uma sugestão. O método A escolhe a forma de menor distância de Levenshtein (até 1 edição em palavras de até cinco letras e até 2 nas maiores). O método B representa as palavras por bigramas e trigramas de caracteres ponderados por TF-IDF e escolhe a de maior cosseno, com mínimo de 0,5. O vocabulário (2.188 formas) vem só das transcrições de treino e do léxico histórico do projeto; os limiares foram fixados antes de olhar a validação.

## Resultados e discussão

**Tabela 1 — Validação de 1795 (7 linhas)**

| Modelo | CER | WER |
| --- | ---: | ---: |
| PP-OCRv6 base | 14,20% | 56,72% |
| Ajustado A (Traslado) | 10,72% | 41,79% |
| Ajustado B (Traslado + Inquisição) | 10,14% | 38,81% |
| Ajustado D1 (Traslado + Posturas) | 9,86% | 38,81% |

Fonte: treinos de 06/11 (A), 07/11 (B) e 10/11 (D1). Números de desenvolvimento.

O ajuste fino reduziu o erro em uma mão que não estava no treino. Em "ando sobre o bem commum do povo", o base leu "lando sobre obem commûm dopovo" e o B, "lando sobre o bem commum do povo". A diferença entre A e B, cerca de 2 caracteres em 345, não permite dizer que os dados da Inquisição ajudam: um treino anterior de A, com a mesma configuração, chegou a 12,17%, e o treino na GPU não é determinístico. A acurácia de caracteres correspondente fica perto de 90%, mas o WER mostra que ainda cerca de duas em cada cinco palavras têm algum erro. No fólio 101r das Posturas, fora do treino, o CER do D1 foi de 15,70%, contra 17,11% do B e 19,09% do base: aprender um segundo documento de Jundiaí ajuda a ler esse documento.

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

### Teste reservado

**Tabela 4 — Teste reservado, avaliação única (CER)**

| Modelo | Total | Pagamento | Contrato |
| --- | ---: | ---: | ---: |
| PP-OCRv6 base | 64,0% | 31,1% | 77,1% |
| Ajustado A | 60,5% | 27,9% | 73,5% |
| Ajustado B | 60,9% | 28,3% | 73,8% |
| Ajustado D1 | 55,4% | 29,0% | 65,9% |

Fonte: avaliação de 09/11 (base, A, B) e 11/11 (D1), uma vez por modelo; 49 linhas (14 do pagamento, 35 do contrato).

Os dois ajustados erram menos que o base nas mesmas linhas (diferença pareada de 1,4 a 5,6 pontos, IC 95% por bootstrap de linhas), e A e B continuam indistinguíveis: o IC 95% do CER total vai de 54% a 68% em ambos, e o WER fica em 94–95% nos três modelos. A distância para a validação, porém, é grande. No pagamento, de letra grande e regular, o B leu "do Concelho NNicolaõ Guedes" onde a referência tem "do conselho Nicolal Guedes": o erro é sobretudo de convenção. No contrato, de cursiva densa e com a tinta do verso aparecendo, a saída é quase sempre ilegível, e em nove pedaços curtos de margem, com uma ou duas palavras, nenhum modelo leu nada. O D1, escolhido antes no 101r, erra menos que o B: diferença pareada de −8,1 a −3,3 pontos, toda vinda do contrato; no pagamento, os dois empatam, e o WER não muda. Depois do resultado, notamos que uma linha do contrato foi validada com uma nota do revisor no lugar da leitura e que algumas seguem a grafia da edição; a referência congelada não foi alterada.

### Leitura modernizada

Além da transcrição diplomática, o PaleographIA oferece uma leitura modernizada, para quem só quer ler ou buscar o documento. Ela é feita só sobre linhas validadas e nunca altera a diplomática. É uma normalização ortográfica do português histórico por regras. As abreviaturas são desenvolvidas, e regras de grafia antiga para atual (y→i, consoantes dobradas, ph→f, -aõ→-ão, h inicial e outras) geram variantes de cada palavra. Vence a variante mais frequente no português atual, penalizada pelo número de trocas, numa lista pública de frequência (pyspellchecker). Uma segunda versão acrescenta quatro tratamentos: caixa ("Com TOdos" → "com todos"), palavras partidas dentro da linha ("Com quistas" → "Conquistas"), nomes próprios em grafia antiga ("Jundiahy" → "Jundiaí") e o pretérito em -ão ("derão" → "deram"), que a primeira confundia com o futuro.

**Tabela 5 — Leitura modernizada contra a edição do Arquivo (WER)**

| Texto | Desenv. | Contrato |
| --- | ---: | ---: |
| Diplomática, sem modernizar | 14,89% | 44,67% |
| Versão 1 | 2,13% | 34,01% |
| Versão 2 | 1,06% | 30,46% |

Fonte: comparação em minúsculas e sem pontuação. Desenvolvimento: 10 linhas da sessão de 1795 e da carta de 1767. Contrato de 1763: 24 linhas da referência congelada do teste reservado, avaliadas uma vez, sem ajuste depois.

No contrato, a segunda versão acerta 25 trocas, contra 20 da primeira. A avaliação não é cega, porque os casos que motivaram a versão 2 foram vistos nessas linhas. O erro que resta é quase todo de leitura: a referência e a edição divergem em trechos ("le no ta veio" × "é notório"), e nenhuma normalização resolve isso. Uma terceira versão, feita sobre as Posturas de 1831 (artigos, réis, futuro em -rão, palavras grudadas e hífen de quebra), reduziu o WER nessas 75 linhas de 28,3% (versão 2) para 21,2%; como elas guiaram a versão 3, o número é de desenvolvimento. A interface também sublinha as palavras fora do dicionário atual e numera notas de um glossário histórico ("magotes", "rocio").

### Curiosidade: um reconhecedor treinado do zero

Para ver quanto pesa partir de um modelo pré-treinado, um reconhecedor CRNN-CTC (convoluções e BiLSTM, 6,3 milhões de parâmetros) foi treinado sem nenhum peso prévio, em uma noite na mesma GPU, com 12.543 linhas públicas da Inquisição e as 191 do Traslado. Numa segunda versão, o codificador passou antes por um pré-treino não supervisionado: trechos de cada linha eram apagados e o modelo reconstruía os pixels, sem ver texto algum. O checkpoint foi escolhido numa validação separada da Inquisição (953 linhas de 20 documentos); a validação de 1795 foi lida uma única vez, no fim.

**Tabela 6 — Modelos treinados do zero, validação de 1795**

| Modelo | CER | WER |
| --- | ---: | ---: |
| Do zero, todas as linhas | 16,23% | 53,73% |
| Pré-treino + todas as linhas | 15,94% | 50,75% |
| Do zero, 5% das linhas | 71,88% | 101,49% |
| Pré-treino + 5% das linhas | 28,12% | 71,64% |

Fonte: treinos de 07 e 08/11, fora do pipeline principal. Números exploratórios.

O melhor modelo do zero fica perto do PP-OCRv6 sem ajuste (14,20%) e atrás dos ajustados: com poucos dados rotulados, partir de um modelo pré-treinado continua valendo. O pré-treino não supervisionado quase não muda o resultado quando todas as linhas têm texto, mas, com só 5% delas (637 linhas), derruba o CER de 71,88% para 28,12%. Como o acervo tem muito mais imagens do que transcrições, isso sugere um caminho para reduzir o custo de rotulação.

## Limitações

A validação tem sete linhas de uma única mão e foi usada para escolher o checkpoint, o que torna os números otimistas e sujeitos a variação de uma ou duas linhas. O treino na GPU não é determinístico, e a comparação entre A e B fica dentro dessa variação. Os rótulos do Traslado vêm da edição, não de leitura diplomática independente. O teste reservado é pequeno (49 linhas, duas mãos) e cada documento foi lido por um só integrante, sem dupla conferência; o contrato entrou depois que o pagamento se mostrou difícil de ler, e sua referência tem problemas notados só após o resultado. A pós-correção lexical não foi aplicada no teste. O teste já foi usado por quatro modelos, uma vez cada; o D1 foi escolhido antes, no 101r, mas a comparação entre os quatro não é mais totalmente cega. Parte dos rótulos das Posturas tem leituras que a edição do Arquivo aponta como erradas, e eles entraram no treino como estavam.

## Conclusões

O ajuste fino do PP-OCRv6 com 191 linhas de um documento de Jundiaí reduziu o CER de 14,20% para cerca de 10–11% e o WER de 57% para 39–42% numa mão diferente, com custo de duas a quatro horas numa GPU de notebook. A análise linguística mostra que o modelo aprendeu a forma das letras e a separação das palavras, e que o erro restante se concentra em convenções de escrita, o que pede políticas de transcrição explícitas. A pós-correção lexical, nas condições testadas, não ajuda. No teste reservado, o ganho do ajuste se manteve, mas o erro subiu para 28% numa letra regular e 74% numa escrita densa. Somar 63 linhas de um segundo documento do acervo (D1) baixou o teste de 60,9% para 55,4%, enquanto 550 linhas de fora (B) não mudaram nada: mais documentos de Jundiaí rotulados são o próximo passo. A leitura modernizada, feita sobre o texto validado, aproxima a transcrição da edição do Arquivo (WER de 44,7% para 30,5% no contrato) sem tocar na diplomática. O resultado reforça o desenho do PaleographIA: o modelo sugere, e o humano valida.

## Disponibilidade dos materiais

Código, dados de treino sem imagens, provas e prints dos treinos (docs/treinos), o Notebook 3 e o experimento do zero estão no [repositório público](https://github.com/aj1no/paleographia-htr); o peso do D1 está no Release v1.0.0. A licença MIT cobre o código; documentos e edições têm condições próprias.

## Comentários

Ferramentas de IA: Codex (OpenAI), Antigravity, ChatGPT (OpenAI) e Claude Code (Anthropic). Codex apoiou a programação, a organização dos artefatos e a versão de 23/10 deste artigo. Claude Code apoiou o pipeline de ajuste fino e os treinos C, D1 e D2, a análise de erros, a pós-correção, a leitura modernizada, o Notebook 3, o experimento do zero e a revisão deste texto. O uso de Antigravity e ChatGPT, e os detalhes de cada integrante, estão na planilha de documentação do uso de IA. Nenhuma ferramenta de IA validou leituras: as referências humanas são da equipe.

## Referências bibliográficas

BAUDRY, Hervé et al. Portuguese Handwriting 16th-19th c. Zenodo, 2024. [Registro 13986218](https://zenodo.org/records/13986218). Licença CC BY 4.0.

JUNDIAÍ. Acervo Digital. Traslado do Auto de Criação da Vila de Jundiaí no Ano de 1656, a 14 Dezembro. Ficha PT/TT/PBR/0004/026, s.d. [Fonte institucional](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

KIESSLING, Benjamin. A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition. arXiv:2609.20064v1, 2026a. Preprint. [Versão consultada](https://arxiv.org/abs/2609.20064v1).

KIESSLING, Benjamin. PP-OCRv6 (medium) multilingual handwritten and printed text recognition model. Zenodo, v1, 2026b. [DOI: 10.5281/zenodo.21788410](https://doi.org/10.5281/zenodo.21788410).

MIRANDA, Ana Caroline Carvalho. Transcrição paleográfica do Traslado do Auto de Criação da Vila de Jundiaí. Revisão de Thiago Paschoal. Memorabilia Paleografia e Diplomática, s.d. [Ficha institucional](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

MUEHLBERGER, Guenter et al. Transforming scholarship in the archives through handwritten text recognition: Transkribus as a case study. Journal of Documentation, v. 75, n. 5, p. 954–976, 2019. [DOI: 10.1108/JD-07-2018-0114](https://doi.org/10.1108/JD-07-2018-0114).

OLIVEIRA, Weslley. TraPrInq: transcription model to recognize Portuguese handwritten texts from the 16th to 19th centuries. Zenodo, v1, 2024. [Registro 14543904](https://zenodo.org/records/14543904). Licença CC BY 4.0.
