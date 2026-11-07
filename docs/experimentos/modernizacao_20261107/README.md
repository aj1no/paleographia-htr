# Leitura modernizada automática (07/11/2026)

Terceira camada de texto, para quem só quer ler ou buscar o documento:

| Camada | Quem faz | Para quê |
| --- | --- | --- |
| Imagem | Arquivo Histórico | Original |
| Transcrição paleográfica (diplomática) | Modelo sugere, humano valida | Pesquisa, gabarito, CER/WER |
| **Leitura modernizada** | Edição do Arquivo, quando registrada na linha; senão, sugestão automática | Leitura e busca |

A leitura modernizada **nunca substitui nem altera a diplomática**. A sugestão automática é feita
só sobre a leitura humana, nunca sobre a sugestão do modelo. Ela aparece em "Texto do fólio" →
"Mostrar leitura modernizada", com a origem de cada linha (edição ou automática).

## Como funciona

[`src/paleographia/modernizacao.py`](../../../src/paleographia/modernizacao.py) trabalha palavra a palavra:

- **Formas fixas e abreviaturas comuns:** `he` → `é`, `hum`/`huã` → `um`/`uma`, `q̄` → `que`, `Snr` → `senhor`.
- **Abreviaturas com letras sobrescritas**, na convenção das transcrições do projeto: as letras
  escritas devem aparecer em ordem na palavra plena, que termina pelas sobrescritas
  (`Nˢᵃ` → `Nossa`, `muⁱᵗᵒˢ` → `muitos`). Se nada servir, a abreviatura fica como está.
- **Regras de grafia histórica → atual**, em até 3 pontos da palavra: `y`→`i`, consoantes
  dobradas, `ph`, `th`, `-aõ`, `-ão`/`-am`, `-aes`/`-ais`, `-eo`/`-eu`, `h` inicial, `u`/`v`, `i`/`j`,
  `ç`/`ss`, `s`/`z`, til de abreviatura (`ē` → `em`) e outras. Também restaura acentos.
- **Escolha pela frequência no português atual:** vence a variante mais frequente, penalizada
  por um fator 10 a cada troca. Uma palavra que já existe só muda se a variante for 10 vezes
  mais comum. Dicionário: lista de frequência pública do pacote
  [`pyspellchecker`](https://pypi.org/project/pyspellchecker/) 0.8.3 (`language="pt"`).
- **Cuidados:** palavras com menos de 3 letras só mudam pelas tabelas. Palavras com maiúscula
  no meio da linha (nomes próprios, mas também `Camara`, `Capitam`) recebem as regras que
  mantêm as letras e só aceitam as demais se o resultado for palavra muito frequente. Palavras
  divididas na quebra de linha (`cumpri` | `mento`) ficam como estão. Agudo antes de `m`/`n` +
  vogal vira circunflexo (`António` → `Antônio`), porque a lista mistura a norma europeia.
- **Não faz:** pontuação atual, maiúsculas de nomes e escolhas de sentido (`reis` × `réis`).

As regras vêm das normas de edição modernizada do AHMJ (Novo Acordo Ortográfico, abreviaturas
desenvolvidas) e das mudanças conhecidas da grafia do português. Os limiares e as proteções
foram ajustados durante o desenvolvimento, olhando a varredura e as 10 linhas descritas abaixo.

## Avaliação de desenvolvimento

[`scripts/avaliar_modernizacao.py`](../../../scripts/avaliar_modernizacao.py) compara a sugestão com a edição
modernizada do AHMJ, que mantém a quebra de linha do original. São 10 linhas com transcrição
diplomática validada: 7 da sessão de 1795 e as linhas 1, 3 e 4 da carta de 1767
([pares](pares_avaliacao.json), [resultado](resultado_avaliacao.json)). A comparação é em minúsculas e sem pontuação,
porque a edição atualiza a pontuação e as maiúsculas e o modernizador não.

| Texto comparado com a edição | CER | WER |
| --- | ---: | ---: |
| Transcrição diplomática, sem modernizar | 6,61% | 14,89% |
| Leitura modernizada automática | 1,28% | 2,13% |

Foram 12 palavras trocadas, todas iguais à edição, e nenhuma troca errada. Restaram `jundiahy`
(nome de lugar fora do dicionário; a edição traz `Jundiaí`) e `por não`, em que a edição
acrescenta `que`.

**Ressalvas.** São só 94 palavras, e essas 10 linhas foram vistas durante o desenvolvimento, por
isso o número é otimista. Uma varredura nas 741 linhas de treino (Traslado e Inquisição, 5.904
palavras, sem edição para comparar) serviu para achar trocas erradas. Ela levou às proteções
para nomes e palavras curtas e à preferência pela grafia brasileira. Erros que ainda aparecem
nessa varredura: `Paes` → `Pais`, `Reo` → `Rio` (seria `Réu`), `deraõ` → `dirão` (seria
`deram`), `Havião` → `Avião`, `menhã` → `minha`.

**Próxima avaliação.** Quando a equipe validar novas linhas de documentos com edição (posturas
de 1831, contratos de 1763), elas servem de avaliação nova, sem mudar o código. No pagamento
a Thomas Pardo a comparação também poderá ser feita, com uma ressalva: durante o
desenvolvimento o autor (Claude) viu a edição desse documento, embora não a transcrição
diplomática, que ainda não existe. O código avaliado tem SHA-256
`cc00fbfb1b4000abe29583267e7e80302ea9754a7c097a0fab90c86fe3cca6e5` (com fim de linha LF, como no repositório).

## Créditos

Edições modernizadas do Arquivo Histórico Municipal de Jundiaí: sessão de 1795, transcrição e
edição de Gilson Santos Lino; carta de 1767, Júlia Munhoz e Matheus Bellodi; revisão de
Isabella Ferraro. Uso sem fins comerciais, com crédito.
