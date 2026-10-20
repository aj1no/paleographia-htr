# Diagnóstico de PP-OCRv5 e PP-OCRv6 na transcrição assistida de 24 linhas do fólio 269r

**Primeiro rascunho — PI IV e PLN — 20 de outubro de 2026**

Caio Augusto de Souza Soares · Guilherme Rodrigues Veiga · Rodolfo Vinicius Cima Takemoto · Tiago Galhardo Avelar

caio.soares01@aluno.cps.sp.gov.br · guilherme.veiga1@aluno.cps.sp.gov.br · rodolfo.takemoto@aluno.cps.sp.gov.br · tiago.avelar@aluno.cps.sp.gov.br

**Professor informado:** Leonardo de Lellis Rossi — leoboralelis@gmail.com  
**Faculdade de Tecnologia de Jundiaí (FATEC Jundiaí)**  
Ciência de Dados — 5º semestre  
Jundiaí – SP  
**Modelo e limite de páginas:** a confirmar em cada disciplina.

## Resumo

Este trabalho apresenta um diagnóstico de desenvolvimento de dois reconhecedores
pré-treinados aplicados a 24 linhas consecutivas de um manuscrito histórico em
português. Comparam-se latin PP-OCRv5 mobile, em ONNX, e PP-OCRv6 medium, em
Kraken, usando os mesmos recortes do fólio 269r do Traslado do Auto de Criação da
Vila de Jundiaí. Os alvos combinam conferência humana e apoio de edição publicada,
mantendo oito ressalvas visuais. O protocolo preserva grafia, caixa e diacríticos
e agrega contagens de cinco blocos completos. O PP-OCRv5 apresentou CER de
58,45% e WER de 94,58%; o PP-OCRv6, CER de 15,11% e WER de 60,10%. A análise
aponta perda de conteúdo no primeiro e problemas de espaçamento, letras e
acentuação no segundo. Os arquivos congelados e o notebook permitem auditar
os cálculos. O estudo permanece restrito a um documento usado no desenvolvimento,
sem teste reservado ou inferência de generalização.

**Palavras-chave:** reconhecimento de manuscritos; português histórico; referência assistida; CER; WER; reprodutibilidade.

## 1. Introdução

A conversão de documentos históricos em texto pesquisável depende de escolhas
que ultrapassam a identificação de letras. Grafias, abreviaturas, espaços e
sinais de pontuação precisam de representação explícita para que a avaliação
automática seja interpretável. No contexto do português histórico, a organização
de corpora e de suas representações já foi discutida por Sousa e Trippel (2006),
que relacionam a padronização da marcação ao aproveitamento e à preservação dos
recursos documentais. [Sousa e Trippel, 2006](https://aclanthology.org/L06-1222/).

O projeto PaleographIA dispõe de um fluxo local de reconhecimento e revisão
assistida. Nesta etapa, seu escopo foi mantido: não foram acrescentadas funções
ao sistema, novos reconhecedores ou mecanismos de pós-correção. O objetivo foi
organizar uma comparação verificável entre duas configurações já disponíveis.
A pergunta deste diagnóstico é: **como latin PP-OCRv5 mobile e PP-OCRv6 medium
se comportam sobre os mesmos 24 recortes, sob uma política de referência assistida
que preserva as dúvidas de leitura?**

A contribuição é um estudo piloto com alvos e saídas rastreáveis, contagens
reproduzíveis e análise de divergências. A comparação não constitui treinamento
de um novo modelo nem avaliação representativa de todo o acervo.

## 2. Referencial técnico inicial

O relatório PaddleOCR 3.0 apresenta PP-OCRv5 no contexto de reconhecimento
multilíngue e distingue configurações de implantação. Seus resultados publicados
não são transportados para este estudo: aqui se avalia um checkpoint latino
mobile convertido para ONNX e identificado por hash. A documentação do RapidOCR
registra as rotas de conversão e reconhecimento utilizadas como apoio técnico.
[Cui et al., 2025](https://arxiv.org/html/2507.05595v1);
[RapidAI, documentação de modelos](https://rapidai.github.io/RapidOCRDocs/main/en/model_list/).

O segundo checkpoint é o PP-OCRv6 medium distribuído por Kiessling para Kraken.
Sua ficha explicita a diversidade das convenções de transcrição no pré-treino.
Assim, diferenças de saída podem envolver convenções além da identificação
visual de caracteres. [Kiessling, 2026](https://zenodo.org/records/21788410).

Essas fontes formam um referencial inicial, selecionado para descrever o corpus
e os componentes efetivamente utilizados. Não foi realizada revisão sistemática
com estratégias, triagem e contagens de seleção. A revisão exigida em PI IV
permanece uma atividade própria, conforme o protocolo bibliográfico do projeto.

## 3. Corpus e construção dos alvos assistidos

O objeto está identificado no acervo municipal pelo código PT/TT/PBR/0004/026.
A ficha institucional descreve um traslado produzido em 1767, relativo ao ato
de criação da vila em 1656. Essa distinção impede tratar a data do acontecimento
como data direta da cópia analisada. O recorte experimental contém somente as
24 linhas do corpo do fólio 269 reto, sem cabeçalho, resumo ou verso.
[Acervo Digital de Jundiaí, ficha do traslado](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

A edição de apoio é atribuída a Ana Caroline Carvalho Miranda no catálogo;
o PDF consultado registra Thiago Paschoal como revisor. Rodolfo Vinícius Cima
Takemoto realizou a conferência humana registrada no projeto. A edição foi
adotada nas dúvidas, com manutenção das decisões e ressalvas no histórico.
[Ficha da transcrição paleográfica](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

Os limites, a ordem e a cobertura foram confirmados em cinco blocos: 1–5, 6–10,
11–15, 16–20 e 21–24. Dezesseis linhas têm validação visual; oito preservam
ressalvas. Todas as 24 foram incluídas. O conjunto de avaliação separado contém
`texto_alvo`, estado visual original e observações, sem alterar o catálogo humano
ou promover as pendências a validação independente.

| Linha | Ressalva mantida no alvo assistido |
| --- | --- |
| 11 | Requererão; sinal superior/final e pontuação |
| 15 | , e ficaram |
| 16 | , e da villa de |
| 17 | ministros, primeira vogal e segmentos intermediários/de Jus |
| 19 | orgente, inicial e pontuação |
| 20 | muito Grande detrimento de to |
| 23 | Justissa, especialmente os dois s |
| 24 | Base Mag e pontuação; de elevado confirmado |

Preservaram-se `Eram`, `Com` e `Como`, confirmados na conferência, e `que mais`
separado conforme a edição, com nota sobre a escrita ligada. A linha final
mantém `Magᵈᵉ`; `Magestade` é o desenvolvimento editorial registrado em campo
separado. As quebras físicas também foram conservadas, inclusive fragmentos
como `Capi/tão`, `Par/nahiba` e `Jus/tissa`.

## 4. Método

### 4.1. Condições da comparação

Os alvos foram congelados antes das duas novas execuções. Cada reconhecedor
recebeu os mesmos 24 PNGs, na mesma ordem, por meio de um manifesto sem texto
humano. Ambos operaram em CPU e float32, com pesos identificados por SHA-256.
O PP-OCRv5 utilizou ONNX Runtime; o PP-OCRv6, Kraken 7.1 em contêiner local com
imagem fixada. Cada configuração manteve seu pré-processamento nativo,
documentado nas saídas brutas.

Não foram executados detector de linhas, treinamento, ajuste fino ou pós-correção.
Logo, o experimento controla os recortes de entrada e compara as configurações
completas de reconhecimento; não isola o efeito causal de mudar apenas a versão
da arquitetura. Há diferenças de variante, pré-treino e implementação.

### 4.2. Métricas e unidade de agregação

Aplicaram-se Unicode NFC e colapso de espaços à referência e às saídas,
preservando caixa, diacríticos e grafia. Para cada bloco completo, concatenaram-se
as linhas em ordem com um espaço. Somaram-se as operações dos cinco blocos antes
da divisão, sem média simples de taxas por linha:

**CER = (S + D + I) / Ncar**  
**WER = (S + D + I) / Npal**

S representa substituições, D deleções e I inserções; Ncar e Npal são os totais
de caracteres e palavras da referência. Uma falha seria contada como saída
vazia, sem excluir a linha. As 48 inferências terminaram sem falhas.
Os denominadores microagregados foram 1.112 caracteres e 203 palavras. Os
espaços internos aos blocos entram em Ncar; os quatro limites entre blocos não
acrescentam caracteres. Taxas por linha foram usadas somente no diagnóstico.

### 4.3. Rastreabilidade e reprodução

As funções existentes `counts` e `aggregate` calcularam o diagnóstico assistido.
O validador estrito de referência humana permaneceu inalterado. A auditoria
verifica hashes, pixels, correspondência de IDs e preservação das ressalvas,
além de conferir as distâncias por uma implementação independente de Levenshtein.
Os casos de alteração de alvo, saída bruta e promoção indevida de ressalva foram
rejeitados em cópia de teste. O notebook recalcula os resultados sem carregar
modelos, e as duas inferências podem ser repetidas separadamente em nova pasta.

## 5. Resultados

| Reconhecedor | CER | Operações / caracteres | WER | Operações / palavras |
| --- | ---: | ---: | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 650 / 1.112 | 94,58% | 192 / 203 |
| PP-OCRv6 medium / Kraken | 15,11% | 168 / 1.112 | 60,10% | 122 / 203 |

O PP-OCRv6 apresentou menos divergências em ambos os níveis, com diferenças de
43,35 pontos percentuais em CER e 34,48 em WER. Esses valores descrevem apenas
o alvo e as condições deste diagnóstico. Não são porcentagens simples de acerto
nem evidência de superioridade geral em documentos desconhecidos.

![Figura 1 — CER e WER nos 24 recortes.](figuras/cer_wer.png)

**Figura 1.** Taxas microagregadas dos cinco blocos. Referência assistida pela
edição; oito ressalvas preservadas. Sem estimativa de intervalo de confiança.

Em caracteres, o PP-OCRv5 acumulou 200 substituições, 444 deleções e seis
inserções; o PP-OCRv6, 96 substituições, 54 deleções e 18 inserções. Em palavras,
os totais foram, respectivamente, 108/84/0 e 95/22/5. O bloco 21–24 apresentou
o maior CER em ambos os reconhecedores: 71,20% e 21,74%.

## 6. Discussão e análise de divergências

No PP-OCRv5, a perda de conteúdo domina o alinhamento. Na linha 22, o alvo
`por titullos de Sismaria as Lavrão outros que mais` resultou em `tiay cm es uhy g`.
O exemplo mostra por que uma configuração de OCR disponível não pode ser
considerada suficiente para este manuscrito sem avaliação local.

O PP-OCRv6 conserva mais conteúdo, mas junta palavras, como `Anno do → Annodo`,
e as separa indevidamente, como `Cabedo → Cabe do` e `onde → on de`. Há trocas
como `Jundiahy → Sundiahy`, `Sismaria → Sismario` e perda de letra em
`titullos → titllos`. `Capitão → Capitao.` combina divergência de acento e
pontuação. Essas diferenças ajudam a interpretar o WER ainda elevado: a
correspondência de palavras inteiras é afetada mesmo por diferenças pequenas.

Não se devem tratar todas as divergências como decisões paleográficas resolvidas.
`ministros/menistros`, `orgente/ergente`, `Justissa` e os sinais finais coincidem
com dúvidas registradas na referência. Na última linha, `Magᵈᵉ → Magi` envolve
também a convenção de representar uma abreviatura com caracteres elevados.
As operações são computadas contra o alvo escolhido, sem decidir a leitura
histórica somente pelo resultado do reconhecedor.

## 7. Limitações e ameaças à validade

O estudo contém um documento e 24 linhas; as linhas não constituem amostras
documentais independentes. O fólio foi usado no desenvolvimento e em consultas
lexicais anteriores, portanto não é conjunto reservado. Não se realizou teste
estatístico, estimativa de generalização ou avaliação de escribas diferentes.

A referência utiliza a edição nas dúvidas e mantém oito ressalvas. Parte do erro
pode refletir essas escolhas de representação. As diferenças entre corpora de
pré-treino, variantes e ambientes também impedem atribuir a diferença somente
ao número da versão. Eventual sobreposição entre o documento e os corpora de
pré-treino externos não foi auditada. Os tempos de uma única execução, com
implementações e limites de CPU distintos, não sustentam conclusão de velocidade.
Não foram medidas economia de esforço humano ou qualidade de tarefas posteriores
de PLN, como busca ou extração de entidades.

Para uma ampliação, deve-se reservar outros documentos antes de usá-los em
seleção de configurações. A meta de 30–50 linhas é operacional, não garantia
de representatividade. A revisão sistemática e a adequação às rubricas de
PI IV e PLN permanecem pendentes; não se presume aprovação acadêmica deste desenho.

## 8. Conclusão

Nos mesmos 24 recortes e sob a política textual explicitada, o PP-OCRv6 medium
apresentou menos divergências que o latin PP-OCRv5 mobile. O WER de 60,10%
mantém a revisão humana como componente necessário do fluxo observado.
O principal resultado desta etapa é um diagnóstico auditável, com saídas brutas,
alvos assistidos e dúvidas preservadas. A conclusão limita-se a esse documento
de desenvolvimento; sua extensão exige avaliação em novos documentos.

## Disponibilidade e uso de ferramentas de IA

O [experimento congelado](https://github.com/aj1no/paleographia-htr/tree/7c9a1b7942fec4f5c7809ccc23e6f96ce44f665b/docs/experimentos/traslado_269r_reconhecedores_24_20261020)
reúne alvos, saídas, configuração, hashes e auditores. O notebook desta entrega
recalcula as métricas, gera tabelas e figuras e verifica a preservação dos arquivos.
As condições de uso da edição e das imagens são próprias; a licença MIT refere-se
ao código do projeto.

Codex auxiliou a organização dos artefatos, a redação deste rascunho e a execução
das verificações. As decisões humanas de leitura e os respectivos escopos estão
no histórico, separadas das saídas de reconhecimento. Os autores devem revisar
o texto, as referências, os créditos e as interpretações antes da entrega.

## Referências iniciais

SOUSA, Maria Clara Paixão de; TRIPPEL, Thorsten. *Building a historical corpus for Classical Portuguese: some technological aspects*. LREC, 2006. [Registro e resumo](https://aclanthology.org/L06-1222/).

CUI, Cheng et al. *PaddleOCR 3.0 Technical Report*. arXiv:2507.05595, 2025. DOI: [10.48550/arXiv.2507.05595](https://doi.org/10.48550/arXiv.2507.05595).

KIESSLING, Benjamin. *PP-OCRv6 (medium) multilingual handwritten and printed text recognition model*. Versão v1. Zenodo, 2026. DOI: [10.5281/zenodo.21788410](https://doi.org/10.5281/zenodo.21788410).

RAPIDAI. *RapidOCR: lista de modelos*. Documentação técnica. [Fonte](https://rapidai.github.io/RapidOCRDocs/main/en/model_list/). Consulta em 20 out. 2026.

JUNDIAÍ. Acervo Digital. *Traslado do Auto de Criação da Vila de Jundiaí*. Ficha PT/TT/PBR/0004/026. [Fonte institucional](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro). Consulta em 20 out. 2026.

MIRANDA, Ana Caroline Carvalho. *Transcrição paleográfica do Traslado do Auto de Criação da Vila de Jundiaí*. Revisão de Thiago Paschoal, conforme PDF consultado. Memorabilia Paleografia e Diplomática, [s.d.]. [Ficha institucional](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro). Consulta em 20 out. 2026.
