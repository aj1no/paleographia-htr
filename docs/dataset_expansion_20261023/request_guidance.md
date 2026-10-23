# PaleographIA — ampliar o dataset e preparar treinamento real

## Prioridade e autorização
Em 23/10/2026, o usuário pediu ampliar o dataset com as transcrições já fornecidas
e informou que o professor quer ver o treinamento do modelo. Tratar isso como
uma atualização explícita do plano acadêmico: a etapa indispensável de
treinamento passa a ser necessária. O restante do escopo continua fechado.

Trabalhar a partir da main atual, respeitando AGENTS.md e alterações locais.
A base conferida foi 75b7b24aa2f03aa906aedf2c6d3dfecfa89cb627.
Não iniciar executável, novo editor, LLM, RAG, outro reconhecedor ou correção
automática como parte desta tarefa. Não reativar o TrOCR rejeitado.

## O que já foi preparado
O pacote de corpus v0.2 reúne:
- Todos os 15 arquivos do inventário de transcrições de 16/10, com hashes.
- Sete grupos documentais candidatos.
- Oito PDFs e extração bruta por suas 59 páginas, incluindo páginas vazias.
- Sete JPEGs avulsos e nove imagens embutidas do fac-símile.
- Núcleo anterior de 24 linhas, preservado com estados 16/8.
- Inventários e fila de curadoria por grupo.

As páginas extraídas não são rótulos. Não contar a quantidade de linhas
retornadas pelo extrator PDF como número de pares de treinamento.
Inspecionar os PDFs combinados para localizar reproduções ainda não indexadas
como JPEG avulso. Não concluir que falta imagem somente pela contagem de JPEGs.

## Etapa 1 — incorporar e conferir o corpus
Conferir o pacote recebido, sua origem e as versões. Preparar uma organização
reproduzível em pasta nova, mantendo os originais e catálogos históricos.
Os caminhos devem ser relativos a uma raiz documentada. Registrar:
documento/grupo candidato, fonte, página PDF, fólio/lado quando conhecidos,
imagem, edição, autor/créditos, tipo de transcrição e hashes.

A v0.2 é um corpus de fontes para curadoria, não uma versão ampliada de linhas
validadas. A incorporação não autoriza modificar estados humanos anteriores.

## Etapa 2 — transformar as fontes em pares supervisionados
Primeiro conferir os documentos e seus vínculos. Depois preparar blocos
concretos para revisão, com imagem contextual, recortes candidatos e texto
editorial separado. Avançar documento por documento, sem exigir revisar todo
o acervo antes de preparar um primeiro conjunto útil.

Para cada linha:
- Manter ID estável, documento, fólio, ordem e coordenadas.
- Conservar a transcrição publicada em campo próprio.
- Registrar o texto-alvo adotado e sua política.
- Diferenciar texto modernizado, referência assistida e confirmação visual.
- Registrar a geometria e a cobertura separadamente da revisão textual.
- Preservar autoria, data, dúvida, expansão editorial e proveniência.
- Não completar letras com saída do reconhecedor ou plausibilidade contextual.

Manter a política paleográfica existente: grafia histórica, caixa, sinais,
abreviaturas e quebras físicas. Uma edição oficial modernizada pode apoiar
a revisão, mas não valida automaticamente a forma visível em cada recorte.
Não mudar silenciosamente o objetivo para modernização textual.

As 24 linhas do 269r já são desenvolvimento. As oito pendências históricas
continuam documentadas; a reconferência de 21/10 permanece aditiva.
Não repetir aprovações já dadas nem pedir novamente para decidir se a edição
pode ser apoio: essa escolha já existe. Pedir somente as decisões humanas
específicas que ainda faltam, sobre recortes e trechos concretos.

## Etapa 3 — registrar partições antes do treino
Conferir quais grupos são documentos independentes. A mesma fonte pode ter
reproduções em imagem e PDF. Todos os fólios, cópias e derivados do mesmo
documento ficam no mesmo grupo.

Preparar conjuntos explícitos de treino, validação e teste de acordo com o
contrato do projeto. Não usar a partição aleatória automática do Kraken.
Não forçar 80/10/10 quando os documentos disponíveis não sustentarem a divisão.

O teste permanece reservado. Seus textos não podem orientar criação de codec,
limites de comprimento, vocabulário, épocas ou seleção de checkpoint.
Qualquer verificação de elegibilidade no teste deve seguir critérios fixados,
sem usar seu conteúdo para escolher hiperparâmetros.

Se ainda faltarem grupos aptos, continuar a anotação e registrar a limitação.
Um ensaio técnico de poucos passos pode ser separado da avaliação científica,
com essa identificação, sem apresentar seu resultado como generalização.

## Etapa 4 — preparar ajuste fino do PP-OCRv6 existente
O código atual training.py tem um bloqueio explícito para treinar o backend
kraken_ppocrv6. A existência do comando train ou de dry-run não significa
que o PP-OCRv6 já esteja sendo treinado.

A documentação oficial do Kraken 7.1 oferece:
https://kraken.re/7.1/user_guide/training_recognition.html

Verificar as opções no ambiente fixado usando a ajuda instalada. O objetivo
é ajuste fino do checkpoint já existente, não treinamento do zero e nem troca
para o TrOCR. O modelo-base deve permanecer somente para leitura, identificado
pelo SHA-256 existente.

Preparar o treinamento como experimento separado, usando ketos e os recursos
nativos compatíveis da versão fixada. Não atualizar pacotes ou a imagem Docker
do editor silenciosamente. Um ambiente de treino diferente deve ter identidade,
dependências e configuração próprias.

Verificar o formato de entrada suportado: recorte de linha e texto correspondente,
ou um formato nativo de anotação. Se usar arquivos de texto ao lado das imagens,
documentar nomes e codificação. Não introduzir novo editor de anotação para isso.

Definir um orçamento limitado depois de verificar hardware, memória e uma
execução curta. Não prometer duração ou melhora sem medir. Não baixar pesos,
atualizar o Docker ou usar serviço externo sem seguir as instruções vigentes
da sessão. Não modificar o reconhecedor ativo como efeito de preparar o treino.

## Etapa 5 — demonstrar aprendizado real e avaliar
Uma execução de treino deve registrar:
- Hash dos dados, partições e checkpoint inicial.
- Código, versões, hardware, dispositivo e precisão.
- Configuração: semente, taxa de aprendizado, lote e épocas/passos.
- Perda de treinamento por passo/época e medidas de validação.
- Checkpoints gerados e identidade do peso final.
- Critério de seleção usando somente a validação.
- Falhas ou interrupções, sem marcar dry-run como treino executado.

O teste técnico deve provar que houve passos de otimização e atualização de
pesos, e que o checkpoint produzido pode ser recarregado para inferência.
Uma mudança de hash sozinha não prova aprendizado: serialização diferente
também pode mudar os bytes. Conferir passos do otimizador e tensores treináveis
alterados, preservando os pesos iniciais.

Depois de fixado o modelo, comparar PP-OCRv6 base e ajustado sobre os mesmos
dados reservados, com CER/WER e protocolo textual iguais. Manter a comparação
PP-OCRv5 × PP-OCRv6 já publicada como diagnóstico histórico. Se a entrega exigir
os dois reconhecedores no novo teste, avaliar ambos no mesmo conjunto, sem
atribuir a diferença somente à versão da arquitetura.

Resultados negativos são válidos. Não mostrar exemplos memorizados do treino
como demonstração de qualidade em documentos desconhecidos.

## Entrega de continuidade
Informar:
1. Fontes incorporadas e imagens efetivamente disponíveis.
2. Novos pares revisados, estados e pendências concretas.
3. Grupos aptos e partições registradas.
4. Situação real do treinamento: não preparado, pronto para ensaio, ensaio
   executado ou experimento concluído, com evidências.
5. Próximo bloco que depende de revisão humana.
6. Explicação atualizada para o professor, separando corpus de fontes,
   dataset supervisionado, inferência e ajuste fino.

Não aguardar confirmação genérica para organizar dados ou investigar suporte.
Avançar no trabalho reversível já autorizado; solicitar somente a decisão
humana indispensável à leitura ou uma informação de ambiente realmente ausente.
Não executar treino científico com referências apenas presumidas para acelerar.
