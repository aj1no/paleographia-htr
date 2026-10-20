# Adoção da main como branch principal — 20/10/2026

A `main` é a branch principal e padrão do repositório. O responsável incorporou
a etapa de refatoração à `main`; antes desta atualização documental, ela e a
`codex/refatoracao-piloto` apontavam para
`5879f8538146d36e78a996ac1f604deaec36ab83`. A descrição pública foi atualizada
para transcrição assistida, revisão humana rastreável e comparação de reconhecedores.

Esta manutenção atualiza somente a orientação de uso: README, contribuição,
índice, guia de revisão, execução, ambiente e consulta lexical. A entrega é
publicada diretamente na `main`, conforme autorização do responsável.
As outras branches não são excluídas, redefinidas ou sincronizadas à força.

## Fluxo atual

- Consulte a [main no GitHub](https://github.com/aj1no/paleographia-htr/tree/main).
- Use a `main` atualizada como base de novas tarefas; branches `codex/` podem
  isolar trabalho. Publique no destino autorizado para a tarefa.
- Siga o [guia de execução](../../runbook.md) e as [orientações de contribuição](../../../CONTRIBUTING.md).
- Preserve o escopo fechado para novas funções e a distinção entre programa,
  referência assistida, experimentos de desenvolvimento e entregas acadêmicas.

## Por que existem referências às branches antigas

Os documentos datados registram onde e como cada entrega foi produzida. As
referências a `codex/refatoracao-piloto` e `master`, os commits de origem e as
restrições de publicação então vigentes permanecem como fatos históricos.
Essas restrições antigas não substituem a orientação atual de trabalhar a partir
da `main`.

Foram preservados sem alteração os pacotes de `docs/revisao_humana/`,
`docs/experimentos/`, `docs/entregas/`, `docs/testes/`, os registros de manutenção
anteriores e `legacy/`. Isso inclui os campos de branch no notebook, nos
inventários e nos recibos. Não foi feita substituição global de nomes de branch.
As URLs fixadas por commit continuam apontando para as versões exatas usadas.

A [revisão do repositório](../../revisao_repositorio_20261020.md) descreve uma
configuração anterior do GitHub; suas constatações sobre branch padrão e
descrição devem ser lidas nesse contexto. Esta nota registra a situação posterior.

## Verificação e limites

O [recibo desta manutenção](validacao.json) documenta testes, auditorias, links
locais e preservação por hash dos arquivos fora da edição e dos workspaces.
O código da aplicação, os avisos numerados, as configurações dos modelos, os
originais e as revisões não são alterados. Não há nova inferência, treinamento
ou reexecução do notebook, nem mudança nas oito ressalvas da referência assistida.
