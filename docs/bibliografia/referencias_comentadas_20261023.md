# PaleographIA — referências bibliográficas comentadas

Pesquisa dirigida realizada em 23 de outubro de 2026, para apoiar PI IV e PLN.

Versão revista em 23/10/2026, após a conferência bibliográfica e o ensaio técnico
do projeto. [Cópia versionada no PaleographIA](https://github.com/aj1no/paleographia-htr/blob/main/docs/bibliografia/referencias_comentadas_20261023.md).
O original recebido foi preservado separadamente, com hash no registro de atualização.

## 1. Para que serve esta seleção

O projeto articula leitura de manuscritos, construção de um corpus e reconhecimento automático. A contribuição acadêmica proposta é organizar e documentar os dados disponíveis, estabelecer uma política de transcrição e avaliar o reconhecimento, incluindo o ajuste de um modelo quando houver dados adequados e execução real de treinamento.

**Estado atual:** foi executado um ensaio técnico de ajuste fino do PP-OCRv6,
com dois passos de AdamW, alterações em 318 tensores treináveis e recarga do peso
exportado para inferência. Foram usadas duas linhas históricas para treino e uma
para validação técnica, todas do documento de desenvolvimento já conhecido.
Isso comprova otimização e recarga, sem demonstrar melhora ou generalização.
A avaliação científica em documentos independentes permanece pendente de
curadoria e de partições aptas. [Relatório e evidências do projeto](https://github.com/aj1no/paleographia-htr/blob/main/docs/dataset_expansion_20261023/README.md).

Esta seleção reúne fontes primárias de pesquisa, um livro, normas, documentação técnica e fontes documentais do acervo. Foram conferidos metadados em páginas de autores, editoras, periódicos, repositórios e instituições. As indicações temáticas se apoiam nos resumos, descrições e trechos consultados; **não constituem fichamento integral de todos os trabalhos nem revisão sistemática concluída**. O livro foi identificado no catálogo da editora, sem leitura integral.

As referências abaixo estão em formato bibliográfico de trabalho, próximo ao autor-data. Ajustar a apresentação final ao manual da instituição. Não acrescentar páginas de citações diretas sem conferir o texto completo.

## 2. Paleografia, transcrição e corpus histórico

### P1 — Manual introdutório de paleografia

BERWANGER, Ana Regina; LEAL, João Eurípedes Franklin. **Noções de Paleografia e de Diplomática**. 5. ed. Santa Maria: Editora UFSM, 2015. ISBN 9788573912241.

- Fonte verificada: [catálogo da Editora UFSM](https://editoraufsm.com.br/catalog/product/view/id/280/s/nocoes-de-paleografia-e-de-diplomatica/category/80/).
- Acesso: catálogo público; livro comercial, a consultar também na biblioteca da faculdade.
- Uso no projeto: fundamentar conceitos de paleografia, dificuldades da leitura e convenções de transcrição. O sumário inclui esses temas.
- Onde citar: introdução e fundamentação teórica. Conferir os capítulos antes de atribuir uma definição específica aos autores.

### P2 — Exemplo brasileiro de análise paleográfica

ANDRADE, Elias Alves de. **Aspectos paleográficos em manuscritos dos séculos XVIII e XIX**. Filologia e Linguística Portuguesa, n. 10–11, p. 149–172, 2009. DOI: [10.11606/issn.2176-9419.v0i10-11p149-172](https://doi.org/10.11606/issn.2176-9419.v0i10-11p149-172).

- [Página do artigo e PDF gratuito](https://revistas.usp.br/flp/article/view/59820).
- Uso no projeto: observar uma análise de manuscritos brasileiros apoiada em edições fac-similar e semidiplomática.
- Onde citar: características da escrita e explicação das modalidades de edição.
- Limite: os documentos estudados são de outros lugares e períodos; as leituras do artigo não validam automaticamente as do acervo de Jundiaí.

### P3 — Paleografia aplicada em uma instituição arquivística

OLIVEIRA, Carolina de. **A Paleografia em prática no Arquivo Nacional: a leitura da escrita antiga na contemporaneidade**. LaborHistórico, v. 5, n. 2, p. 213–230, 2019. DOI: [10.24206/lh.v5i2.26450](https://doi.org/10.24206/lh.v5i2.26450).

- [Artigo e PDF gratuito](https://revistas.ufrj.br/index.php/lh/article/view/26450).
- Paginação conferida no [sumário do periódico](https://revistas.ufrj.br/index.php/lh/issue/view/1225).
- Uso no projeto: contextualizar a transcrição como atividade especializada de acesso à documentação e relacioná-la à digitalização e preservação.
- Onde citar: justificativa social e institucional do PaleographIA.
- Limite: a experiência descrita não é uma avaliação dos reconhecedores do projeto.

### P4 — Organização de corpora históricos brasileiros

LACERDA, Mariana Fagundes de Oliveira; LOSE, Alícia Duhá; CARNEIRO, Zenaide de Oliveira Novais. **O português no Brasil colonial: reflexões sobre edições de manuscritos históricos brasileiros**. Working Papers em Linguística, v. 26, 2025. DOI: [10.5007/1984-8420.2025.e100380](https://doi.org/10.5007/1984-8420.2025.e100380).

- [Artigo e PDF/A gratuito](https://periodicos.ufsc.br/index.php/workingpapers/article/view/100380).
- Uso no projeto: fundamentar o diálogo entre paleografia, filologia e linguística histórica na organização de corpora. O artigo apresenta o trabalho do CE-DOHS e sua articulação com o grupo Modus Scribendi.
- Onde citar: construção do corpus e política editorial.
- Limite: um corpus histórico para pesquisa linguística e um dataset supervisionado de reconhecimento têm finalidades próprias. A adaptação para pares imagem–texto deve ser explicada pelo projeto.

### P5 — Normas de transcrição: referência para decisões explícitas

ARQUIVO NACIONAL. **Normas técnicas para transcrição e edição de documentos manuscritos**. [S. l.]: Arquivo Nacional, [s. d.]. Cópia disponibilizada pelo Laboratório de Estudos Filológicos da UFRJ; documento com indicação de última atualização em 10 out. 2000.

- [PDF institucional gratuito, três páginas](https://labefil.letras.ufrj.br/wp-content/uploads/2020/05/NORMAS_TRANSCRI%C3%87%C3%83O_Casa-Civil.pdf).
- Uso no projeto: discutir convenções de grafia, abreviaturas, dúvidas, identificação documental e apresentação.
- Atenção: o item 1.8 recomenda desenvolver abreviaturas não correntes, assinalando os acréscimos; o item 1.1 trata da separação e união de palavras/sílabas. O projeto preserva certos sinais e quebras físicas para reconhecimento. Portanto, deve declarar quais regras aproveita e quais adapta. Não afirmar adesão integral sem comparação.
- Data: 2000 é a atualização indicada na cópia, não uma data de edição comprovada. Não confundir as datas dos encontros de normatização com a publicação desta versão.

Comparação explícita com a política do projeto, sem declarar adesão integral:

| Regra da norma | Tratamento no PaleographIA | Justificativa |
| --- | --- | --- |
| 1.1: regularizar separação/união | Sem correção lexical automática; decisões de representação registradas | Manter auditável a relação imagem–alvo |
| 1.8–1.9: desenvolver ou manter abreviaturas conforme o caso | Preservar a forma visível; expansão em campo editorial ou nota | Separar sinal observado e desenvolvimento |
| 1.10: desdobrar sinais especiais | Preservar sinal representável; convenção humana quando necessária | Evitar alvos inferidos |
| 2.1: reconstituir ilegíveis pelo sentido | Reconstrução contextual fica no apoio editorial; não valida leitura visual | Distinguir interpretação e evidência |
| 1.14–1.17: conservar aspectos gráficos | Preservar acentos, pontuação, caixa e grafia | Reconhecimento de forma histórica |
| 7.1: admitir linhas ou texto corrido | Cada par supervisionado corresponde a uma linha física | Identificar recorte, ordem e cobertura |

Essas decisões explicitam a [política textual existente](https://github.com/aj1no/paleographia-htr/blob/main/docs/transcription_policy.md).
Referência assistida por edição, confirmação visual e transcrição modernizada
permanecem classificações distintas; a tabela não promove estados de revisão.

### P6 — Ponte entre português histórico e tecnologia

PAIXÃO DE SOUSA, Maria Clara; TRIPPEL, Thorsten. **Building a historical corpus for Classical Portuguese: some technological aspects**. In: Proceedings of the Fifth International Conference on Language Resources and Evaluation (LREC’06). Genoa: European Language Resources Association, 2006.

- [Registro oficial na ACL Anthology e PDF gratuito](https://aclanthology.org/L06-1222/).
- Uso no projeto: organização tecnológica de um corpus de português histórico, tratamento de material existente, marcação e padrões abertos para acesso duradouro.
- Onde citar: metodologia de organização e preservação do corpus.
- Limite: não é um experimento de treinamento dos modelos PP-OCR. A relação com o formato específico do nosso dataset é uma aplicação metodológica proposta por nós.

## 3. Reconhecimento automático, aprendizagem e documentação dos dados

### T1 — HTR no trabalho com arquivos históricos

MUEHLBERGER, Guenter et al. **Transforming scholarship in the archives through handwritten text recognition: Transkribus as a case study**. Journal of Documentation, v. 75, n. 5, p. 954–976, 2019. DOI: [10.1108/JD-07-2018-0114](https://doi.org/10.1108/JD-07-2018-0114).

- [Artigo na editora, acesso aberto](https://doi.org/10.1108/JD-07-2018-0114).
- [PDF em repositório universitário](https://www.research.ed.ac.uk/files/191649573/MuehlbergerEtalJD2019TransformingScholarshipInTheArchives.pdf).
- Uso no projeto: apresentar reconhecimento de manuscritos em contexto arquivístico e um caso de integração com pesquisa e acesso ao patrimônio escrito.
- Onde citar: trabalhos relacionados e justificativa da abordagem assistida.
- Limite: citar esse estudo não exige adotar Transkribus; seus resultados não são resultados do PaleographIA.

### T2 — Fundamento do alinhamento entre imagem e sequência textual

GRAVES, Alex; FERNÁNDEZ, Santiago; GOMEZ, Faustino; SCHMIDHUBER, Jürgen. **Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks**. In: Proceedings of the 23rd International Conference on Machine Learning (ICML). 2006. p. 369–376.

- [PDF gratuito mantido pelo autor](https://www.cs.toronto.edu/~graves/icml_2006.pdf).
- [Página do autor com dados bibliográficos](https://www.cs.toronto.edu/~graves/).
- Uso no projeto: explicar a função CTC, que permite aprender sequências sem fornecer o alinhamento individual de cada símbolo. Isso ajuda a entender o uso de imagem de linha acompanhada de sua transcrição.
- Limite: o artigo original trabalha com redes recorrentes. CTC é uma função/forma de treinamento, não sinônimo de uma arquitetura recorrente específica. Confirmar a arquitetura e a perda do checkpoint efetivamente usado no experimento.
- No ensaio local, os registros distinguem perdas CTC e GTC e sua soma.
  T2 fundamenta CTC; a configuração completa deve ser descrita pelas evidências
  da implementação Kraken usada. [Componentes de perda efetivamente registrados](https://github.com/aj1no/paleographia-htr/blob/main/docs/dataset_expansion_20261023/training_ppocrv6_smoke/validation_history.json).
  A sigla GTC é mantida conforme os logs, sem atribuir ao artigo de 2006 a
  documentação desse componente adicional.

### T3 — Base tecnológica da família PP-OCRv5

CUI, Cheng et al. **PaddleOCR 3.0 Technical Report**. arXiv, 2025. arXiv:2507.05595v1. DOI: [10.48550/arXiv.2507.05595](https://doi.org/10.48550/arXiv.2507.05595).

- [Registro dos autores e PDF gratuito](https://arxiv.org/abs/2507.05595v1).
- Natureza: relatório técnico disponibilizado como preprint.
- Uso no projeto: contextualizar a família PP-OCRv5 e o ecossistema PaddleOCR.
- Onde citar: descrição do reconhecedor comparador.
- Limite: os resultados gerais do relatório não descrevem automaticamente a variante latin mobile exportada para ONNX que usamos. Registrar também origem, versão e hash dos pesos locais.

### T4 — Adaptação de PP-OCRv6 a reconhecimento histórico

KIESSLING, Benjamin. **A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition**. arXiv, 2026. arXiv:2609.20064v1. DOI: [10.48550/arXiv.2609.20064](https://doi.org/10.48550/arXiv.2609.20064).

- [Registro do autor e PDF gratuito](https://arxiv.org/abs/2609.20064v1).
- Natureza: preprint, submetido em 17 set. 2026. Não apresentar como artigo de periódico com revisão por pares comprovada.
- Uso no projeto: referência particularmente próxima do caminho atual; aborda adaptação de PP-OCRv6 a linhas históricas e compara condições de pré-treinamento e ajuste.
- Onde citar: seleção do método e planejamento do fine-tuning.
- Limite: resultados do artigo não garantem melhora no nosso corpus. O PDF indexado contém campos editoriais de modelo, como “Conference XXX” e DOI fictício; usar os metadados reais do arXiv acima.
- Conferência: autoria, título, versão e data foram reconferidos no registro
  arXiv; o rodapé da primeira página do PDF contém campos editoriais provisórios.
  Não usá-los como referência de publicação definitiva. O identificador
  verificável da versão consultada é **arXiv:2609.20064v1**.

### T5 — Documentação do dataset

GEBRU, Timnit et al. **Datasheets for datasets**. Communications of the ACM, v. 64, n. 12, p. 86–92, 2021. DOI: [10.1145/3458723](https://doi.org/10.1145/3458723).

- [Registro da publicação](https://dl.acm.org/doi/10.1145/3458723).
- [Versão gratuita dos autores, atualizada em 2021](https://arxiv.org/abs/1803.09010v8).
- Uso no projeto: orientar uma ficha do dataset com motivação, composição, coleta, usos e limitações.
- Onde citar: metodologia e apresentação do dataset ao professor.
- Aplicação proposta: documentar fontes, autores das transcrições, modalidades editoriais, estados de revisão e usos permitidos de cada parte. Os números do nosso corpus vêm do inventário do projeto, não deste artigo.

### T6 — Execução do treinamento e avaliação no Kraken

KRAKEN. **Recognition Model Training**. Documentação da versão 7.1. [S. d.]. Disponível em: <https://kraken.re/7.1/user_guide/training_recognition.html>. Acesso em: 23 out. 2026.

- Acesso: documentação técnica gratuita.
- Uso no projeto: formatos de pares imagem–texto, manifests de treino/validação, carregamento de pesos para ajuste, checkpoints e avaliação com CER/WER.
- Onde citar: detalhes de implementação e reprodução.
- Limite: documentação de software não equivale a artigo experimental. Ela demonstra suporte na ferramenta; não demonstra que o treinamento já foi implementado ou executado no PaleographIA. Registrar a versão realmente instalada ao reproduzir.
- Atualização local: a execução por ketos/Kraken 7.1 foi demonstrada pelo ensaio
  técnico, com configuração, hashes, perdas e checkpoints próprios. Essa
  comprovação vem dos artefatos locais, além da documentação de suporte.

## 4. Fontes documentais do corpus

Além da bibliografia teórica, identificar individualmente os manuscritos e as edições usadas. Para o traslado:

1. **Traslado do Auto de Criação da Vila de Jundiahy no Ano de 1656, a 14 de dezembro**. Traslado produzido em 1767, referente ao ato de 1656. Arquivo Nacional da Torre do Tombo, Papéis do Brasil, códice 4, fólios 269–273. Código PT/TT/PBR/0004/026. Cópia digital disponibilizada pelo acervo municipal de Jundiaí. [Registro institucional](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).
2. MIRANDA, Ana Caroline Carvalho. **Transcrição Paleográfica do Traslado do Auto de Criação da Vila de Jundiahy no Ano de 1656, a 14 de dezembro**. [S. d.]. Registro 02294 no acervo municipal. [Registro institucional com autoria e acesso ao PDF](https://jundiai.sismu.app/obra/100529/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro).

Conservar também os créditos de revisão presentes no PDF: Thiago Paschoal, conforme a edição usada no projeto. A data de vistoria do catálogo não deve ser tomada automaticamente como data de publicação da transcrição. Conferir a edição exata e seus créditos ao fechar a referência.

Para cada outro documento, repetir a identificação de instituição de guarda, cota, data, edição, transcritor, modalidade editorial e arquivo/hash usado. A publicação institucional de uma transcrição documenta sua origem; não resolve por si só todas as divergências entre texto editorial e sinais visíveis no manuscrito.

## 5. Como relacionar as referências às decisões do projeto

| Parte do trabalho | Referências prioritárias | O que cabe demonstrar com os dados do PaleographIA |
|---|---|---|
| Problema e relevância | P1, P3, T1 | Acervo selecionado e dificuldades observadas |
| Política de transcrição | P2, P4, P5 | Tratamento adotado para sinais, abreviaturas, espaços e quebras |
| Corpus e dataset | P4, P6, T5 | Inventário, pares imagem–texto, autoria e estados de revisão |
| Reconhecedores | T2, T3, T4 | Checkpoints, versões, pré-processamento e condições da comparação |
| Treinamento | T2, T4, T6 | Dados separados, configuração, otimização real, curvas e checkpoints |
| Avaliação | T6 e estudos experimentais lidos integralmente | Protocolo textual, contagens CER/WER, falhas e limites da amostra |

As ligações dessa tabela são orientações para o nosso desenho metodológico. Não atribuir a cada autor todas as decisões específicas do projeto.

## 6. Roteiro de leitura inicial

1. **P2 (Andrade)**: exemplo concreto, em português, de tratamento paleográfico de manuscritos.
2. **P5 (normas)**: leitura curta para discutir a política textual com exemplos do fólio.
3. **T5 (Gebru et al.)**: organizar a ficha do dataset que será mostrada ao professor.
4. **T1 (Muehlberger et al.)**: compreender a aplicação de HTR em arquivos.
5. **T4 (Kiessling)**: estudar o método próximo ao reconhecedor atual e interpretar o ensaio técnico já executado, preparando o experimento científico ainda pendente.

Depois, usar P4/P6 para aprofundar o corpus e T2/T3/T6 para a parte técnica. P1 é um apoio de formação, caso disponível na biblioteca.

## 7. Regras práticas para escrever o artigo

- Associar cada afirmação à fonte que a sustenta e conferir o trecho antes de citar. Uma referência pertinente não sustenta qualquer conclusão.
- Preferir paráfrases próprias com autor e ano. Citações diretas exigem transcrição fiel e localização conferida.
- Distinguir fundamentos da literatura, decisões metodológicas do grupo e resultados próprios.
- Distinguir o ensaio técnico de ajuste fino já executado da avaliação científica ainda planejada. Uso de pesos pré-treinados apenas para inferência não é treinamento realizado pelo grupo. Dois passos sobre desenvolvimento conhecido não comprovam generalização.
- Documentar a política textual usada no cálculo do erro. Expansão de abreviaturas e modernização podem alterar o alvo de reconhecimento.
- Manter o fólio já usado no desenvolvimento fora de um teste apresentado como reservado. O particionamento por documento é uma decisão do protocolo do projeto que precisa ser justificada.
- Registrar estes achados como pesquisa bibliográfica complementar. Não marcar buscas, triagens ou leituras integrais pendentes como concluídas no protocolo de revisão da literatura.

## 8. Buscas que podem ampliar a seleção

Termos em português: `paleografia transcrição semidiplomática manuscritos`, `corpus histórico português edição filológica`, `reconhecimento de manuscritos históricos português`.

Termos em inglês: `historical handwritten text recognition fine-tuning`, `ground truth transcription conventions HTR`, `historical HTR character error rate evaluation`, `PP-OCRv6 historical text recognition`.

Priorizar periódicos universitários, SciELO, BDTD e repositórios institucionais para paleografia; ACL Anthology, bibliotecas de editoras científicas e arXiv para tecnologia. O buscador ajuda a localizar; o registro do periódico, autor ou instituição fornece a versão a consultar e citar.

Este documento não altera código, dados, revisões humanas ou o escopo funcional do produto.

## 9. Da seleção comentada ao fichamento comparável

A tabela de pertinência da seção 5 não substitui a extração de método e resultados.
Os [fichamentos parciais de T1 e T4](https://github.com/aj1no/paleographia-htr/blob/main/docs/bibliografia/fichamentos_parciais_20261023.md)
registram o escopo real de consulta e os campos ainda não verificados. Antes de
uma síntese empírica final, extrair e conferir, por estudo:

- Corpus, idioma/escrita, documentos e quantidade de exemplos.
- Checkpoint inicial, pré-treino, adaptação e orçamento efetivamente usados.
- Unidade da partição, independência e possível sobreposição entre conjuntos.
- Origem da referência e tratamento de grafia, abreviaturas e incertezas.
- Métricas, normalização, denominadores, agregação e localização dos resultados.
- Resultados negativos e limitações, distinguindo declarações dos autores de
  interpretações do grupo.

Campo ainda não consultado deve ser registrado como **não verificado**, sem
receber zero ou conclusão de ausência. A leitura assistida por IA deve ser
identificada; a conferência humana e a decisão final de inclusão continuam pendentes.

Esta seleção entra como origem complementar no registro bibliográfico.
T3 e T4 se vinculam, respectivamente, aos registros canônicos
`ARXIV-2507.05595` e `ARXIV-2609.20064`, já recuperados em B01/B02. P6 também
era fonte conhecida (`sousa2006`). Esses vínculos não representam novos estudos
independentes nem alteram as contagens históricas de recuperação.
