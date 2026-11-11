# Experimento da noite de 10 para 11/11/2026: o treino nas Posturas ajuda a ler as Posturas?

As 7 linhas de 1795 que validam o A, o B e o C são de outro documento, e por isso não mostram o
que o C ganhou nas Posturas de 1831. Para medir isso, o fólio **101r** (31 linhas, 1.414 caracteres)
saiu do treino e entrou na validação, junto com 1795 (`scripts/treino_noturno.py`):

- **treino:** 191 linhas do Traslado + 63 linhas das Posturas (100r e 100v), com 1 variante aumentada cada;
- **validação** (dev, 38 linhas): 101r + 1795 ([pares](pares_dev.json)). A parada antecipada e a escolha
  do checkpoint olham para essas 38 linhas;
- **hiperparâmetros:** os do C (taxa 2e-5, lote 2, acumula 4, BatchNorm congelada), com teto de 6 épocas.

Os rótulos do 101r têm as leituras erradas apontadas pela edição do AHMJ (ver o README do treino C).
Por isso, o CER no 101r mede a concordância com o que a equipe validou, e não com o texto certo.

## O que aconteceu

A fila está em [fila_noturna.log](fila_noturna.log):

- 21h55: as linhas de base foram avaliadas.
- 21h58: o D1 começou.
- **01h51:** o Windows reiniciou o computador sozinho para instalar uma atualização planejada (evento 1074 do
  TrustedInstaller). O D1 estava na 6ª e última época (passo 336, 228 min) e não exportou o peso. O D2
  (2 variantes aumentadas) não chegou a começar.

Os checkpoints do D1 ficaram no disco. O melhor deles, `checkpoint_03-0.8695.ckpt`, foi convertido à
mão para pesos com `ketos convert`, na mesma imagem Docker do treino. É o primeiro ponto com 86,95%, no
passo 239 da 4ª época; o passo 303 empatou depois. O peso convertido tem SHA-256
`13a1fa98d4dae668fbded047be73503dca2705a378a88fbc674ea4378558bdf7`. Como
o treino não terminou, as validações que faltavam (cerca de 2) não foram vistas. A seleção pode ser
diferente da que o `ketos` faria, mas só se uma delas passasse 86,95% + 0,1 ponto.

## Validações do D1 (acerto do `ketos`, 38 linhas)

Começou em 85,66% (passo 15), subiu devagar e chegou a **86,95%** nos passos 239 e 303. O histórico
completo está em [D1/validation_history.json](D1/validation_history.json) e no [console](D1/console.log).

## CER e WER em NFC (métrica do projeto)

Medidos com `scripts/avaliar_validacao.py`, o mesmo worker de inferência do editor ([linhas](avaliacao_dev_nfc.json)):

| Modelo | 101r: CER | 101r: WER | 1795: CER | 1795: WER |
|---|---|---|---|---|
| PP-OCRv6 base | 19,09% | 62,65% | 14,20% | 56,72% |
| Ajustado A | 17,54% | 56,03% | 10,72% | 41,79% |
| Ajustado B (na aplicação) | 17,11% | **54,86%** | 10,14% | 38,81% |
| **D1** (Traslado + 100r/100v) | **15,70%** | 56,42% | **9,86%** | **38,81%** |

O C não entra nesta tabela, porque treinou no 101r.

- **No 101r**, o D1 erra cerca de 20 caracteres a menos que o B (1,4 ponto de CER), mas acerta 1 ou 2
  palavras a menos (WER). O treino nas Posturas ajuda a ler as Posturas no nível dos caracteres. O
  ganho é pequeno, e o WER, mais sensível a palavra juntada ou partida, não acompanha.
- **Em 1795**, o D1 empata com o B em palavras e erra 1 caractere a menos. Treinar nas Posturas não
  piorou a leitura de outro documento.

## O que falta

- **D2** (2 variantes aumentadas): não rodou.
- **Teste reservado:** com o aval do usuário, rodou uma vez no D1, em 11/11. Resultado: CER total de 55,4%,
  contra 60,9% do B; a diferença pareada vai de −8,1 a −3,3 pontos (IC 95%), e o WER empata. O D1
  passou a ser o modelo da aplicação. Os detalhes estão no [README do teste reservado](../../../revisao_humana/teste_reservado_congelado_20261109/README.md).
  O peso fica em `models/ppocrv6_ajustado_D1_20261110/medium_ajustado_D1.safetensors`, fora do Git.
