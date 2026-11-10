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

## Versão 2 (10/11/2026)

A aba Modernizada ainda ficava muito parecida com a diplomática. A v2
([`modernizacao_v2.py`](../../../src/paleographia/modernizacao_v2.py)) é uma camada sobre a v1, que
continua intacta (o teste confere o SHA-256 acima). A v2 trata antes quatro coisas:

- **Caixa:** `Com TOdos` → `com todos`. Maiúscula no meio da palavra vira minúscula, e
  palavras gramaticais com maiúscula no meio da frase também.
- **Palavra partida dentro da linha:** `Com quistas` → `Conquistas`. A junção acontece quando a
  segunda parte sozinha não é palavra atual e a junção é. Há uma tabela pequena para quando as
  duas partes existem (`tão bem` → `também`, `toda via` → `todavia`).
- **Nomes próprios:** tabela de topônimos paulistas e prenomes em grafia antiga (`Jundiahy` →
  `Jundiaí`, `Joam` → `João`, `Riberão` → `Ribeirão`, `Manoel` → `Manuel`).
- **Pretérito em -ão:** `deraõ` → `deram`, `Havião` → `Haviam`, quando a forma em -am existe.
  A regra não se aplica depois de determinante (`pela mesma Razão`, `do Fundaõ`), porque aí a
  palavra é substantivo. Também entram três correções de erros da v1: `Reo` → `Réu`,
  `menhã` → `manhã`, `Paes` fica `Paes`.

| Texto comparado com a edição (10 linhas de desenvolvimento) | CER | WER |
| --- | ---: | ---: |
| Sem modernizar | 6,61% | 14,89% |
| v1 | 1,28% | 2,13% |
| v2 | 0,85% | 1,06% |

São 13 trocas, todas iguais à edição. Só resta `por não`, em que a edição acrescenta `que`
([resultado v2](resultado_avaliacao_v2.json)). **Esse ganho é otimista por construção:** `Jundiahy`
era o resíduo conhecido da v1 e está na tabela de nomes. Por isso a varredura das 741 linhas de
treino importa mais aqui. Nela, a v2 muda 110 linhas em relação à v1: 65 minúsculas, 26 nomes,
19 pretéritos, 11 formas fixas, 8 grafias. Ela serviu para achar e corrigir `o mto` → `unto`
(abreviatura sem vogal não entra na junção) e `do Fundaõ` → `Fundam` (bloqueio depois de
determinante). A ambiguidade que sobra é o futuro (`acharão` vira `acharam`), aceitável em texto
narrativo. Código avaliado: SHA-256
`bdd34ffe6c7311c3b562a6c9b7eef72d72e194320b261eb47ee554182b579ed8` (LF). A interface (`/leitura`,
Texto do fólio e aba Textos) usa a v2. Para comparar: `python scripts/avaliar_modernizacao.py --v1`.

### Avaliação nova: contrato do livro 12, 1763 (10/11/2026)

O código da v2 foi fechado antes desta avaliação (SHA-256 acima), e nada foi ajustado depois.
[`scripts/avaliar_modernizacao_contrato12.py`](../../../scripts/avaliar_modernizacao_contrato12.py)
compara três textos com o fl. 1 da edição modernizada do AHMJ: a diplomática das 24 linhas do
corpo da página 9 do PDF e as leituras da v1 e da v2 sobre ela. A diplomática vem da
[referência congelada de 09/11](../../revisao_humana/teste_reservado_congelado_20261109/README.md),
lida às cegas por Tiago Avelar. O script só lê a referência e confere o hash dela, então o
teste do HTR não muda. As 11 peças de margem ficam de fora
([pares](pares_contrato12.json), [resultado](resultado_contrato12.json)).

| Texto comparado com a edição (24 linhas, 197 palavras) | CER | WER |
| --- | ---: | ---: |
| Diplomática, sem modernizar | 14,23% | 44,67% |
| v1 | 11,68% | 34,01% |
| **v2** | **10,58%** | **30,46%** |

Se a linha da edição for usada inteira, sem o corte do trecho (217 palavras), a ordem não muda:
WER de 48,85% sem modernizar, 38,71% com a v1 e 35,48% com a v2. A v2 acerta 25 trocas e a v1
acerta 20. As duas têm cerca de 14 trocas que não batem com a edição.

**Ressalvas.**
- Os exemplos que motivaram a v2 (`Com quistas`, `Riberão`, `Com TOdos`) foram vistos em 09/11
  justamente nestas linhas, na aba Modernizada. As regras são gerais, mas esta avaliação não é
  totalmente cega.
- O erro que sobra é quase todo de leitura, não de modernização. A diplomática e a edição leem
  trechos de forma diferente (`le no ta veio` × `é notório`, `eles mas` × `e com as`), e o
  modernizador não tem como resolver isso.

**Erros da modernização vistos aqui, que ficam para uma próxima versão** (corrigir agora seria
ajustar no teste):
- `resolverao` sem til não entra na regra do pretérito;
- `tãobem` escrito junto não vira `também`;
- `des certam` não vira `deste sertão`;
- começos de palavra partida na quebra de linha, avaliados como linha solta: `rem` → `rim`,
  `uro` → `urro`, `eria` → `iria`. No texto corrido esses pedaços são unidos e ficam como estão.

## Créditos

Edições modernizadas do Arquivo Histórico Municipal de Jundiaí: sessão de 1795, transcrição e
edição de Gilson Santos Lino; carta de 1767, Júlia Munhoz e Matheus Bellodi; revisão de
Isabella Ferraro; contrato do livro 12 (1763), transcrição e edição de Gilson Santos, revisão de
Isabella Ferraro. Uso sem fins comerciais, com crédito.
