# Roteiro da apresentação (até 5 minutos + 5 de perguntas)

Para 19/11 (ou 12/11). Cobre PI IV e PLN numa só fala. Tempo total de exposição: 5 min.
Os números vêm do [artigo de 07/11](../artigo_20261107/artigo.md) e do
[Notebook 3](../notebook_3_pln/README.md). Quem fala cada parte: a equipe decide.

| # | Parte | Tempo | O que dizer | O que mostrar |
|---|---|---|---|---|
| 1 | Problema | 30 s | Ler manuscritos dos séculos XVII a XIX exige paleógrafos e tempo; arquivos de cidades pequenas não têm isso. O acervo de Jundiaí está digitalizado, mas quase nada está transcrito. | Uma página do Traslado (imagem do acervo, com crédito). |
| 2 | Solução | 45 s | O PaleographIA é uma ferramenta aberta e gratuita: o modelo sugere a leitura de cada linha e um humano confere e valida. Saída automática, sugestão e transcrição humana ficam separadas, com autoria e histórico. | Tela do editor com uma linha, a sugestão e o campo de revisão. |
| 3 | Como funciona | 1 min | Imagem → segmentação de linhas (blla) → reconhecimento (PP-OCRv6, sequência para sequência, vocabulário de caracteres) → revisão humana → métricas CER e WER. | Diagrama do fluxo; vista "Texto do fólio". |
| 4 | Resultados | 1 min | Comparação 1: PP-OCRv5 × PP-OCRv6 no 269r (CER 58% × 15%). Ajuste fino com o Traslado, como adaptação de domínio: na validação de 1795 (outra mão), CER de 14,2% para 10,1–10,7% e WER de 57% para 39–42%. Treinos gravados em vídeo. | Tabela 1 do artigo; um trecho do vídeo do treino ou o print com a validação. |
| 5 | Parte de PLN | 1 min | Análise dos erros: o ajuste reduziu a forma das letras e as palavras coladas; sobra convenção de escrita (maiúsculas, s/z, i/j, abreviaturas). Comparação 2: pós-correção por Levenshtein × TF-IDF de n-gramas. Piorou o CER porque o vocabulário é pequeno; fica como sugestão ao revisor. | Gráfico "De onde vem o CER" e a tabela da pós-correção do Notebook 3. |
| 6 | Limitações e próximos passos | 45 s | Validação de só 7 linhas; teste reservado (pagamento a Thomas Pardo) espera transcrição às cegas; ampliar o léxico histórico; avaliar nas outras mãos do acervo. | Lista curta. |

## Perguntas prováveis

- **Dá para confiar com tão poucas linhas validadas?** Não para o número exato: são números de
  desenvolvimento. O que é consistente é a direção (o ajuste melhora nas duas execuções). O teste
  reservado, usado uma única vez, dará o número final.
- **Por que o TrOCR foi abandonado?** Nos testes iniciais ele gerava sequências de caracteres sem
  sentido nessas páginas; o PP-OCRv6, pré-treinado em manuscritos históricos, partiu de 15% de CER.
- **Vocês podem usar as imagens do acervo?** Sim: são públicas no Acervo Digital da prefeitura e o
  Arquivo Histórico autorizou o uso sem fins comerciais, com crédito.
- **Qual o papel do humano?** Validar. Nenhuma sugestão vira transcrição sem conferência na imagem; a
  pós-correção também é só sugestão.
- **Por que CER e WER e não acurácia?** São as métricas padrão de texto gerado (como BLEU e ROUGE):
  contam substituições, apagamentos e inserções, inclusive texto inventado, o que a acurácia esconde.
  Acurácia de caracteres ≈ 100% − CER (cerca de 90%) só como comentário.
- **Os dados da Inquisição ajudaram?** Não dá para afirmar: B ficou 2 caracteres à frente de A, dentro
  da variação entre execuções.

## A confirmar com o professor

- Tempo: 5 ou 10 minutos (preparado para 5).
- Se o artigo precisa estar no modelo oficial (o gerador já usa o layout PLN2026).
