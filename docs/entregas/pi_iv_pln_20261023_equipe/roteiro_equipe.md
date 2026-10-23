# Participação da equipe e cronograma de consolidação

Versão de 23/10/2026, preparada por Codex (IA) a pedido do solicitante.
Base: `D:/Downloads/PaleographIA_Artigo_Entrega_Objetivos_Planejamento.docx`,
seção **Planejamento inicial**. O arquivo recebido é fonte de responsabilidades
previstas, não comprovação de execução. As propostas antigas de comparar
segmentadores foram adaptadas ao diagnóstico atual de dois reconhecedores.

## Situação conhecida

O solicitante informou que a equipe conversou sobre o projeto, mas a execução
está concentrada nele. O relato permite registrar **discussão coletiva**, sem
determinar a fala, a decisão ou a tarefa realizada por cada colega. Não foram
informadas datas dessas conversas nem evidências individuais novas.

O projeto já registra a revisão humana do manuscrito por Rodolfo e a execução
de várias atividades por Codex. O notebook preserva esse histórico e identifica
a execução de demonstração desta versão como feita por IA. A lista de autores
não significa que cada autor executou todas as células.

## Responsabilidades e pontos de entrada no notebook

| Integrante | Responsabilidade no artigo inicial | Participação proposta no estágio atual | Produto que pode demonstrar participação |
| --- | --- | --- | --- |
| Caio Augusto de Souza Soares | Bibliografia; colaboração na frente neural com Guilherme | Conferir fontes T1/T4, relação com a fundamentação e limites da comparação | Relato próprio com páginas e uma sugestão ou concordância justificada sobre o artigo |
| Guilherme Rodrigues Veiga | Modelos/dependências; pré-processamento com Rodolfo; segmentação tradicional com Tiago e neural com Caio | Conferir as duas configurações, proveniência e reprodução das métricas | Checagem técnica e interpretação própria, com arquivos/versões identificados |
| Tiago Galhardo Avelar | Inventário e associações com Rodolfo; frente tradicional com Guilherme | Inspecionar três recortes e sua correspondência com IDs, alvos e erros | Observações próprias sobre imagem, associação e tipos de divergência |
| Rodolfo Vinicius Cima Takemoto | Inventário, associações e pré-processamento; entregas em equipe | Coordenar a rodada e consolidar relatos, dados e documentos | Registro da implementação/coordenação efetivamente realizada e consolidação conferida |
| Equipe | Revisão do piloto, métricas, análise, artigo, notebook e apresentação | Discutir os achados e revisar as contribuições antes de apresentá-las | Registro coletivo com participantes e decisões que cada pessoa possa confirmar |

As frentes da coluna “proposta” estão **a realizar ou a detalhar**, não marcadas
como concluídas. Se alguém já contribuiu pela discussão, pode registrar essa
contribuição intelectual; não precisa afirmar que programou ou executou modelos.

## Cronograma por rodadas

O artigo inicial enumera tarefas e dependências, mas não fixa datas individuais
nessa seção. Este cronograma usa sequência e condições de conclusão, sem criar
datas passadas ou prazos de disciplina.

| Rodada | Atividade | Responsabilidade proposta | Dependência | Evidência de conclusão | Estado inicial |
| --- | --- | --- | --- | --- | --- |
| R1 | Disponibilizar o notebook, o artigo e a divisão de trabalho | Coordenação | Arquivos atuais disponíveis | Materiais acessíveis e frentes conhecidas pelo grupo | Materiais preparados; ciência dos colegas ainda não registrada |
| R2 | Fazer ou relatar a análise de cada frente | Caio, Guilherme, Tiago e Rodolfo | R1 | Formulário individual com relato, data real e evidência | A preencher |
| R3 | Conferir relatos e discutir divergências | Caio ↔ Guilherme; Tiago ↔ Rodolfo, como proposta | R2 | Concordâncias/correções identificadas pelos participantes | Não realizada por esta preparação |
| R4 | Consolidar a contribuição dos autores e a apresentação | Coordenação e equipe | R3 | Declaração factual, com referências aos registros conferidos | Pendente |

## Como preencher

1. Abra o [notebook colaborativo](colaboracao_equipe.ipynb) em uma cópia de
   trabalho e execute a parte comum. O checkout completo é necessário.
2. Localize a seção com seu nome, consulte os materiais e faça a análise.
   Uma contribuição de discussão pode ser descrita com o que você propôs,
   questionou, explicou ou ajudou a decidir.
3. Preencha `preenchido_por`, `data_atividade`, `relato`, `evidencias` e
   `uso_de_ia`. Não use a data de geração do notebook como se fosse a data
   de uma reunião anterior. Se não conhece a data, apure-a antes de exportar.
4. Em `evidencias`, informe caminho de arquivo do projeto, URL ou uma entrada
   iniciada por `relato:` com a descrição identificável da discussão. Relato
   de discussão é autodeclaração; não é auditoria ou autenticação de presença.
5. Execute sua célula e envie o JSON gerado à coordenação pelos canais que o
   grupo já utiliza. Esta preparação não envia mensagens nem atribui contas.

Os JSONs ficam em `output/participacao_equipe_20261023/`. Cada gravação cria
um arquivo novo, sem sobrescrever o anterior. Formulários vazios não gravam
participação. Os campos de confirmação de identidade, validação de linha e
alteração do experimento continuam falsos. Links informados não são auditados
automaticamente. Quem registra o relato de outra pessoa aparece em
`preenchido_por`, e o participante ainda deve conferir.

## Declaração de contribuições para consolidar depois da rodada

Preencher com ações realmente relatadas e conferidas, sem distribuir autoria
retrospectiva pela tabela de planejamento:

| Integrante | O que efetivamente discutiu, analisou, implementou ou revisou | Data da atividade | Registro/evidência | Conferência do participante |
| --- | --- | --- | --- | --- |
| Caio | A individualizar | A informar | A informar | Pendente |
| Guilherme | A individualizar | A informar | A informar | Pendente |
| Tiago | A individualizar | A informar | A informar | Pendente |
| Rodolfo | Revisão humana histórica documentada; detalhar implementação e coordenação atuais | 21/10 para a reconferência; demais datas a informar | [17 registros históricos](../../revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/consolidacao.md); demais evidências a indicar | Nova consolidação pendente |
| Equipe | Discussão coletiva relatada pelo solicitante; conteúdo e participação individual ainda não detalhados | Não informada | Relato do solicitante neste chat, registrado em 23/10 | A confirmar pelos participantes |

O artigo preparado em PDF/Word permanece preservado. Uma seção factual de
contribuição dos autores poderá ser acrescentada em nova versão depois de
consolidar os registros. Este roteiro não declara aprovações ou participação
individual nova apenas pela execução automática do notebook.
