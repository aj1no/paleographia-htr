# Reescrita do histórico em 09/11/2026: mensagens sem linha de coautoria

A pedido do autor, as mensagens de 41 commits feitos com o Claude Code (de `f37e3a1`, em 05/11, a
`fe3e79e`, em 09/11) perderam a linha `Co-Authored-By: Claude ...`. **Só as mensagens mudaram:** a
árvore de arquivos de cada commit, o título, o autor e as datas são os mesmos. Como o código (hash) de
um commit depende da mensagem, esses commits e os seguintes ganharam códigos novos.

[`mapa_commits.tsv`](mapa_commits.tsv) liga cada commit antigo ao novo, com a árvore (igual nos dois)
e o título. Para conferir um par: `git rev-parse <commit_novo>^{tree}` deve dar a árvore da tabela. A
mesma árvore no commit antigo pode ser conferida pelo backup.

- Commits anteriores a 05/11 (inclusive os citados nas entregas de outubro, como `69e98a78` e
  `c8a3e9a`) **não mudaram**.
- O congelamento do teste reservado, citado como `1797998`, hoje é `472f9f6`, com a mesma árvore
  (`2d1ddd6c…`) e a mesma data. O `git_commit` gravado em `avaliacao_final.json` continua com o
  código antigo, porque o arquivo é o registro original da avaliação.
- Links para commits antigos podem continuar abrindo no GitHub com o aviso de que o commit não
  pertence a nenhum branch. Use a tabela para trocar pelo código novo.
- O uso de IA continua declarado em [`docs/ai_comments.md`](../../ai_comments.md), na planilha de
  uso de IA da equipe e nos comentários dos notebooks e do artigo.
