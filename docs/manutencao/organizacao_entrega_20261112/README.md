# Organização do repositório para a entrega final, 12/11/2026

Revisão final antes da entrega (versão 1.0.0). O objetivo foi que um clone novo funcione, que o
repositório contenha só o que o projeto usa e que nada pessoal ou sem permissão de redistribuição
fique público. **O código e os registros datados não mudaram de conteúdo**, exceto o que está listado aqui.

## O que um clone novo não fazia

| Problema | Correção |
| --- | --- |
| No Windows, o `git clone` falhava: três nomes em `data/raw/transcriptions` tinham mais de 190 caracteres e estouravam o limite de 260 do caminho | Nomes encurtados, com a tabela de equivalência em [`data/raw/transcriptions/README.md`](../../../data/raw/transcriptions/README.md). O caminho mais longo agora tem 139 caracteres |
| O README mandava abrir o modo leitura, mas o clone começa sem workspace e a tela ficava vazia | O README traz o `import-catalog` do Traslado 269r (24 linhas, com imagens), testado num clone limpo |
| `iniciar_editor.bat` usava `>/dev/null`, que o `cmd` não entende: o aviso de Docker aparecia sempre | Trocado por `>nul` |
| O peso do modelo da entrega só existia na máquina da equipe | Publicado no Release v1.0.0; `configs/editor_folios.toml` passa a usar o D1 |
| `client` era um submódulo (gitlink) sem `.gitmodules`, que gerava erro de `git` na CI | Removido; a interface é servida pelo próprio pacote |

## O que saiu do repositório

| Item | Motivo |
| --- | --- |
| `data/raw/Photos-*.zip` (4 arquivos, cerca de 40 MB) | Fotos pessoais, sem relação com o projeto, versionadas por engano no primeiro commit |
| `data/raw/Transcrições.rar` (27 MB) | Pacote enviado pelo Arquivo Histórico para uso da equipe; a autorização cobre o uso acadêmico, não a redistribuição. As transcrições usadas nas avaliações continuam em `data/raw/transcriptions/` com crédito |
| Dez avisos `1_…py` a `9_…py` na raiz | Só imprimiam "script desativado". O código histórico segue em [`legacy/`](../../../legacy/README.md) e o [catálogo de 20/10](../scripts_numerados_20261020/README.md) continua conferido por `tests/test_legacy_entrypoints.py` |
| `.claude/skills/` e `skills-lock.json` | Configuração local de ferramenta de IA, não do projeto |

Os arquivos seguem na máquina da equipe e ficam fora do Git pelo `.gitignore`.

## Reescrita do histórico

Os arquivos das duas primeiras linhas da tabela acima estavam no primeiro commit. Para que deixem de
ser baixados por quem clona o repositório, eles foram retirados de **todo o histórico** com
`git filter-repo`. As árvores de arquivos de cada commit continuam iguais, sem esses cinco arquivos;
as mensagens, autores e datas não mudaram. Como o código de um commit depende do conteúdo, **todos os
commits ganharam código novo**. A correspondência antigo → novo está em
[`mapa_commits.tsv`](mapa_commits.tsv), como na [reescrita de 09/11](../reescrita_historico_20261109/README.md).

- Os registros datados (READMEs de entregas e experimentos, `git_commit` em JSONs de avaliação)
  continuam citando os códigos antigos, porque são o registro da época. Use a tabela para achar o novo.
- Três referências que o código executa foram atualizadas para os códigos novos: a base do histórico
  do Traslado (`scripts/traslado_history.py`), o commit anterior dos scripts numerados
  (`tests/test_legacy_entrypoints.py`) e o fechamento de 23/10 conferido pela CI (`.github/workflows/ci.yml`).
- Quem já tinha um clone precisa cloná-lo de novo.
- Commits antigos podem continuar acessíveis no GitHub por um tempo pelo código direto, até a
  limpeza do próprio GitHub.

## Outras mudanças

- `README.md`: estado de 12/11, instalação testada num clone limpo, sugestões do modelo, como citar.
- `CITATION.cff` novo; `pyproject.toml` na versão 1.0.0, com autores, licença e endereços.
- [`docs/README.md`](../../README.md): a entrada passa a ser a entrega final; as entregas de outubro
  ficam como histórico preservado.
- `iniciar_apresentacao.bat`: abre a demonstração local, os slides e a pasta da apresentação.
