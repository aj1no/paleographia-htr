# Integridade dos snapshots do Traslado

Os oito arquivos legados `revisions/comparacao_*.json` são preservados com seus
nomes e conteúdos. Os identificadores históricos usavam o prefixo SHA-256 de
uma serialização UTF-8 com **CRLF**. O Git publicou blobs com **LF**. Isso explica
a diferença de digest e não demonstra alteração semântica do JSON.

[integridade.json](integridade.json) registra o caminho e SHA-256 completo dos
bytes de cada blob publicado no commit
`632e8ff71eef2913f003cece810f834aa1ca4382`. Esses bytes são obtidos com
`git show COMMIT:CAMINHO` em subprocesso binário, sem normalização textual.
O registro guarda separadamente o digest CRLF que originou o nome legado.
O verificador compara também os blobs históricos com os de `HEAD`, e verifica
o conteúdo da cópia de trabalho permitindo somente LF/CRLF como diferença de
serialização. A comparação semântica de JSON é uma verificação distinta.

## Novos snapshots

`paleographia.io.write_snapshot` usa `deterministic_json_bytes`:

- UTF-8 sem BOM; `ensure_ascii=False`, `sort_keys=True`, `indent=2` e
  `allow_nan=False`;
- quebras LF e exatamente um LF final;
- SHA-256 completo dos mesmos bytes que são gravados;
- nome `snapshot_SHA256_COMPLETO.json`;
- escrita com o `atomic_write` existente, que define `newline="\n"`;
- arquivo existente idêntico é preservado; divergência causa recusa.

As funções `verify_digest` e `same_json_content` separam integridade de bytes
e igualdade semântica. Hash de blob publicado nunca é calculado a partir de
`read_text`, que poderia normalizar quebras. O registro de integridade legado
não é um selo de validação paleográfica.

```powershell
python scripts/traslado_history.py verify
python scripts/traslado_history.py snapshot --source docs/revisao_humana/traslado_269r/comparacao.json
```

O segundo comando cria um snapshot determinístico do registro atual, sem
reescrever a cadeia antiga. Repeti-lo com os mesmos dados reutiliza os mesmos
bytes e nome. O verificador também confere todos os novos `snapshot_*.json`.
`record` serve para reconstruir o registro de blobs legados e recusa divergência
com registro existente; requer o commit base disponível no histórico Git.

`.gitattributes` fixa LF no registro novo, nos novos nomes `snapshot_*`
e nos dois manifests JSONL da amostra. As configurações próprias e o registro
de evidências também fixam LF para manter seus checksums reproduzíveis nas
cópias de trabalho. Nenhuma renormalização geral foi feita; as regras não
atingem os oito nomes antigos. Com `core.autocrlf=true`, a cópia
de trabalho legada pode continuar CRLF e diferir do blob: ambos os digests são
apresentados com sua origem explícita. Clones rasos precisam buscar o commit
base para executar a verificação de blobs históricos.
