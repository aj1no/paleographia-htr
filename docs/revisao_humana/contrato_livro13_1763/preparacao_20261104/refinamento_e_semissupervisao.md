# Piloto de refinamento e aprendizagem semissupervisionada

O piloto usou as quatro linhas exploratórias da reprodução da página 5 do contrato do livro 13. O PP-OCRv6 base recebeu cinco variações de cada faixa já tratada. A hipótese da rodada anterior foi incluída na votação. Os pesos e o decodificador permaneceram fixos.

| Linha | Seleção automática | Votos exatos em 6 | Edições de caracteres para a edição modernizada, anterior → seleção |
| --- | --- | ---: | ---: |
| A | Fundo uniforme | 1 | — |
| B | Nitidez | 1 | 17 → 18 |
| C | Nitidez | 1 | 7 → 8 |
| D | Faixa anterior | 2 | 23 → 23 |

O consenso escolhe a hipótese do OCR com menor soma de distâncias de edição às outras hipóteses. A transcrição editorial só entra na análise depois de gravada a seleção. As contagens para B, C e D usam NFC, espaços normalizados e comparação sem diferença entre maiúsculas e minúsculas. A linha A tem uma quebra de palavra e um trecho editorial ilegível, por isso a tabela não atribui uma contagem a ela. A melhor variante observada depois da consulta à edição exigiu 15 edições na B, 7 na C e 21 na D. Essa escolha retrospectiva não estima o desempenho de um seletor automático.

Para uma linha se tornar candidata a revisão como pseudorrótulo, o piloto exige a mesma linha inteira em pelo menos quatro das seis previsões. O limiar é exploratório. Variantes do mesmo modelo compartilham erros e os votos não são uma confiança calibrada. Nenhuma das quatro linhas atingiu o limiar. Os pesos permanecem iguais aos do PP-OCRv6 base.

## Integração proposta

1. **Estabelecer o ajuste supervisionado.** Usar as linhas diplomáticas validadas e confirmar a divisão por documento. As 19 linhas de treino e 7 de validação ainda são propostas. O teste final precisa de um grupo independente. Fixar a normalização de treino após a verificação do codec e usar a mesma política para avaliar todos os modelos.
2. **Gerar pseudorrótulos só em documentos de desenvolvimento.** Usar o checkpoint supervisionado para prever linhas sem rótulo em variantes da mesma imagem. Medir a qualidade do filtro em referências diplomáticas do desenvolvimento antes de fixar o limiar. Manter um manifesto separado com checkpoint, versão do tratamento, saídas brutas e decisão de revisão. Os pseudorrótulos ficam separados das transcrições validadas.
3. **Medir o efeito dos pseudorrótulos.** Comparar o PP-OCRv6 base, o ajuste supervisionado e o mesmo ajuste com os pseudorrótulos. Selecionar checkpoints na validação e avaliar os três no mesmo teste independente, com CER, WER e exemplos de erros. Manter as variantes de uma linha no mesmo grupo de origem.

O pré-treinamento autossupervisionado do Kraken aprende com imagens de linhas sem transcrição. Na imagem Docker do projeto, o comando 'ketos pretrain' usa a arquitetura VGSL, enquanto o reconhecedor deste piloto é PP-OCRv6. O pré-treinamento disponível pode formar um experimento separado de VGSL. A rota semissupervisionada com pseudorrótulos aproveita o ajuste fino PP-OCRv6 existente. [Documentação de treinamento do Kraken](https://kraken.re/main/user_guide/training_recognition.html#pretraining) e [experimento de aprendizagem incremental em manuscritos](https://arxiv.org/abs/1811.07768).

Os scripts locais [gerar variantes](gerar_variantes_refinamento.py) e [selecionar hipóteses](selecionar_hipoteses_refinamento.py) são executados a partir da raiz do projeto com o ambiente do PaleographIA e as faixas tratadas da rodada anterior. O gerador exige uma pasta nova. O [registro do piloto](diagnostico_ppocrv6_refinamento.json) conserva as 24 hipóteses e os hashes das entradas.
