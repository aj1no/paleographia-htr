# Protocolo futuro: PP-OCRv6 bruto versus apoio lexical

Preparado em 19/10/2026. **Protocolo, sem execução automática lexical.**
A consulta interativa do editor retorna candidatos para decisão humana;
aplicações humanas não são predições de um segundo reconhecedor ou modelo
treinado. Confirmar o enquadramento acadêmico com os professores.

## Antes de avaliar

1. Reservar novos grupos documentais antes da seleção de regras ou limiares.
   Registrar IDs, grupos, referência, caixas, ordem, hashes e partições.
   Conferir referência humana, geometria e cobertura pelo fluxo normal.
2. Congelar predições brutas já preservadas. Não repetir HTR para esta
   comparação. Usar o mesmo conjunto de linhas e o mesmo protocolo NFC com
   redução de espaços da avaliação existente.
3. Congelar versão/fingerprint do léxico e lista explícita de entradas
   elegíveis. Excluir toda atestação derivada do grupo avaliado, mesmo que
   `split` esteja nulo ou rotulado como desenvolvimento. A API interna
   `Lexicon.query(..., exclude_groups=...)` permite filtrar grupos, mas não
   substitui a verificação de linhagem do lote experimental.
4. Rejeitar entradas de acervo com origem desconhecida e verificar vínculos
   entre documentos aparentados. Não passar referência humana, edição ou
   respostas de revisão ao algoritmo. Não calibrar regras no teste reservado.
5. Implementar separadamente o algoritmo de aceitação. Pré-especificar regras
   e limiares com dados de desenvolvimento, tratamento de empates, ausência de
   candidato, caixa, acentos, nomes, abreviaturas e espaços. Proximidade gráfica
   isolada não é autorização para substituir nomes próprios. Não há algoritmo
   de aceitação automática nesta entrega; os limites de busca do editor não
   devem ser apresentados como tais regras.

## Execução e relatório futuros

Gerar arquivo derivado novo, preservando IDs, ordem e caixas. Nunca substituir
o bruto nem os experimentos existentes. Registrar ambiente, código, configuração,
léxico elegível, hashes de entrada/saída, cada proposta e o motivo da aceitação
ou recusa. Só após gerar as saídas independentes abrir a referência para medir
CER/WER bruto e derivado, com numeradores e denominadores e o mesmo protocolo.

Publicar também palavras corretas preservadas, erros corrigidos e erros
introduzidos. Declarar o alinhamento usado para comparar alterações de palavras;
segmentações ambíguas exigem inspeção humana identificada, separada da decisão
automática. Não selecionar apenas exemplos favoráveis. Relatar regressões,
falhas, tempo, cobertura lexical e casos sem candidato.

## Dados atuais e limites

As cinco primeiras linhas do 269r são desenvolvimento. PP-OCRv6 bruto tem CER
**30/242 = 12,40%**, WER **23/45 = 51,11%** apenas nelas, conforme o
[experimento congelado](experimentos/traslado_269r_ppocrv6_20261016/README.md).
Esses números não medem o painel lexical, as dez linhas ou generalização.
As linhas 6–10 também tiveram assistência; não são referência produzida às cegas.

As 18 atestações do acervo da versão 2026-10-19.1 vêm das dez linhas humanas
do mesmo grupo `tt_pbr_0004_026_traslado_1767`. Usá-las para corrigir essas
linhas e medir melhora gera circularidade. Uma futura exploração nesse grupo
precisa declarar esse uso e excluir tais entradas da execução independente.
Os três verbetes externos de Bluteau não usam a transcrição do grupo como
definição, mas sua seleção temática já foi informada por esta amostra.

Nenhuma predição automática lexical, CER/WER novo, treino, resegmentação,
integração LLM ou alegação de generalização acompanha este protocolo.
