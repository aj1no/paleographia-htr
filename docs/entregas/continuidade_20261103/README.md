# Continuidade após a primeira entrega

**Pausa em 03/11/2026:** consulte o [ponto exato de retomada](RETOMADA.md) e o [salvamento do editor](salvamento_20261103/README.md). A carta de 1767 avançou até a terceira linha; a próxima conferência é a quarta linha.

Retomada em **03/11/2026**. O solicitante identifica o Notebook 1 como sua primeira entrega e pede continuidade do desenvolvimento. Esse nome não foi convertido na numeração oficial de PI IV: a entrega 1 dos slides de PI IV é uma apresentação pessoal.

## Requisitos recuperados dos arquivos originais

Fontes localizadas em `D:/Downloads/Faculdade/`, após reorganização dos caminhos antigos de Downloads. Arquivos consultados, páginas e hashes estão em [fontes_requisitos.json](fontes_requisitos.json).

| Disciplina | Fonte | Exigência localizada |
| --- | --- | --- |
| PI IV | Apresentação da disciplina, p. 12–13 | Etapa 4: conjunto de dados tratado e descrição das transformações. Etapa 5: primeiro modelo de classificação e análise. Etapa 6: deep learning com comparação. Etapa 7: apresentação. Etapa 8: artigo e notebook Colab |
| PI IV | Apresentação da disciplina, p. 9 | Calendário ilustrado associa dados a 10/10, primeiro modelo a 17–24/10, deep learning a 31/10–07/11 e apresentação a 14/11. Uma versão o identifica como proposta sujeita a alteração. Datas posteriores do solicitante prevalecem para o nosso planejamento |
| PI IV | Apresentação da disciplina, p. 10 e 16–17 | Declarar ferramenta/função de IA nos Comentários do próprio arquivo e usar dataset público |
| PLN | `05_The Transformer Revolution.pdf`, p. 45 | Decisão relatada da turma: notebook de implementação comparando dois modelos, artigo de até cinco páginas sem modelo obrigatório, apresentação de até dez minutos e cinco minutos de perguntas. Revisão sistemática dispensada nessa orientação de PLN |
| PLN | `01_Processamento de Linguagem Natural.pdf`, p. 6 | Referências e ferramentas citadas, declaração de IA dentro do próprio notebook e link no local indicado da planilha |

**Apresentação informada pelo solicitante: 12/11, até 15 minutos.** Preparar dez minutos de exposição e cinco de perguntas atende ao total informado e à orientação localizada de PLN. O calendário antigo de PI IV não substitui a data informada. Não foi localizada uma instrução que nomeie o próximo arquivo do projeto como “Notebook 2” ou fixe um novo prazo específico para ele.

A dispensa explícita de revisão sistemática foi localizada para PLN. Os slides consultados de PI IV não especificam esse requisito; registros históricos do projeto o mencionam, mas a conferência atual não demonstra uma exigência docente vigente de revisão sistemática para PI IV.

## Situação e avanço necessário

| Frente | Situação conferida | Trabalho de continuidade |
| --- | --- | --- |
| Primeira entrega | Notebook 1, pacote offline e comparação PP-OCRv5 × PP-OCRv6 conferidos | Preservar como referência e reutilizar suas métricas com identificação |
| Dados e transformações | Inventário, proveniência e oito recortes atuais de 1795 disponíveis | Consolidar o conjunto atual, as transformações já realizadas e as pendências em notebook próprio |
| Referências de 1795 | Oito geometrias validadas, sete referências por linha validadas, linha 8 provável/pendente; associação e cobertura parcial confirmadas | Conferir os pontos textuais que faltam e a identificação/cobertura documental. As aprovações localizadas já registradas permanecem válidas |
| Primeiro modelo | Dois reconhecedores pré-treinados comparados no Notebook 1 | O termo “classificação” de PI IV não foi confirmado como equivalente ao HTR. Documentar a tarefa real e obter o enquadramento docente, sem inventar um novo classificador |
| Deep learning com comparação | Ensaio técnico de ajuste fino com dois passos e pesos recarregados | Preparar avaliação científica apenas após pares aptos, separação de documentos e protocolo de avaliação |
| Artigo e apresentação | Artigo de fechamento e roteiro inicial disponíveis | Incorporar o avanço efetivamente realizado e preparar exposição em dez minutos |

## Trabalho iniciado nesta retomada

O [notebook de continuidade dos dados](continuidade_dataset.ipynb) executa uma conferência do snapshot de 1795 após a observação 038. Ele lê os dados locais, verifica fontes/recortes e hashes, apresenta os rascunhos e explica as transformações registradas. Também mostra os grupos candidatos e por que ainda não há partições científicas prontas. Não depende de novas bibliotecas, não executa modelos e não altera o editor.

O notebook é uma **base técnica para a etapa de dados**, não uma afirmação de atendimento integral da etapa 4 ou de submissão. Requer este checkout completo e os arquivos locais das fontes. As saídas salvas permitem consultar a execução realizada nesta máquina. Seu relatório derivado fica em `output/continuidade_20261103/prontidao_dataset.json`.

A auditoria existente foi executada com `--local-artifacts` nesta retomada: 126 arquivos conferidos, pesos grandes íntegros, dois passos de otimização, 318 tensores treináveis alterados e recarga para inferência registrada. Isso confirma o ensaio técnico histórico, sem nova execução de treinamento.

## Sequência de execução

1. **Dados:** retomar a conferência das oito transcrições de 1795 com os recortes atuais, mantendo a edição separada. Revisar identificação e cobertura. Exportar uma nova versão somente com decisões realmente recebidas.
2. **Protocolo:** identificar documentos independentes e definir treino, validação e teste antes da seleção do modelo. O Traslado e o piloto de 1831 continuam desenvolvimento. Os grupos já inspecionados nesta curadoria devem ser tratados como conhecidos no desenho da avaliação.
3. **Experimento:** comparar modelo-base e modelo ajustado nas mesmas entradas reservadas, sob a mesma política textual e métricas. Um pequeno bloco revisado sozinho não garante dados suficientes para as três partições.
4. **Entrega:** produzir novo notebook com resultados executados, atualizar artigo e preparar slides. Resultados que não puderem ser obtidos até 12/11 devem aparecer com seu estado real e suas limitações.

## Dados revisados e próxima etapa

As observações 037 e 038 consolidam sete transcrições integrais, a associação ao fólio 91r da sessão de 25/06/1795 e a descrição da cobertura parcial de oito linhas. A oitava linha mantém abriu provável, alternativa abrio e exclusão explícita como alvo aprovado. As aprovações já recebidas não precisam ser solicitadas novamente.

O [pacote de dados revisados de 1795](dataset_revisado_1795/README.md) contém sete referências selecionadas, a oitava linha excluída em arquivo próprio, a página/cobertura e as validações de prontidão. Os sete pares passam na validação estrutural de referência por linha. A região de oito linhas não tem referência integral completa; não foram calculadas novas métricas regionais.

O notebook foi reexecutado sobre a [exportação após 038](../../revisao_humana/sessao_1795/sessao_20261103/exportacao_apos_observacao_038/lines.jsonl), com cinco células de código e 16 vínculos fonte/recorte íntegros. O [fechamento da curadoria](../../revisao_humana/sessao_1795/sessao_20261103/fechamento_curadoria_038.md) preserva o histórico e descreve os limites.

O seletor de treinamento científico continua recusando o protocolo antes de Docker/modelos, por independência documental e partições pendentes. O pacote contém um grupo documental; não foi feito sorteio de linhas entre treino, validação e teste. Condições de uso das fontes ainda precisam ser esclarecidas.

Na carta de José Gomes de Gouveia de 1767, foram confirmados o fólio **4r** e a cobertura parcial de seis linhas da anotação superior à esquerda. Os seis recortes têm geometria aprovada. As linhas **1, 3 e 4** passaram na validação de referência para avaliação por linha, e as linhas **2, 5 e 6** seguem com texto diplomático pendente. A referência da região está incompleta, e as partições científicas continuam pendentes. [Curadoria da carta de 1767](../../revisao_humana/carta_jose_gomes_1767/preparacao_20261103/README.md).

Na avaliação exploratória dessas três linhas, o PP-OCRv5 teve CER de **79,69%** e WER de **100,00%**, e o PP-OCRv6 teve CER de **25,78%** e WER de **65,38%**. O pacote registra as exclusões, as entradas congeladas, as previsões brutas, as métricas por linha e os comandos para reprodução. [Avaliação por linha de 1767](avaliacao_linhas_1767/README.md).
