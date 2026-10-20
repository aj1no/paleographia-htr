# Guia de Contribuição

O escopo desta entrega está fechado para novas funções. Priorize correções,
clareza da documentação e consolidação das entregas já autorizadas. Consulte o
[README](README.md) e o [índice da documentação](docs/README.md).

## Conventional Commits

Use mensagens claras em português. Conventional Commits pode ser usado sem
reescrever o histórico existente para padronizá-lo.

Estrutura recomendada:
`tipo(escopo): descrição sucinta`

Tipos comuns:
- `feat`: Uma nova funcionalidade
- `fix`: Uma correção de bug
- `docs`: Alterações na documentação
- `style`: Alterações que não afetam o significado do código (espaço em branco, formatação, etc.)
- `refactor`: Uma alteração de código que não corrige um bug nem adiciona uma funcionalidade
- `test`: Adicionar ou corrigir testes existentes
- `chore`: Atualizações de build, dependências ou tarefas administrativas

## Fluxo de Trabalho

1. Mantenha esta entrega em `codex/refatoracao-piloto`, sem mesclar com `main`
   ou `master`. Para outra tarefa, confirme a base adequada; não presuma que
   branches distintas tenham as mesmas fontes. Use prefixo `codex/` quando aplicável.
2. Preserve originais, autoria, revisões e resultados congelados, inclusive
   resultados negativos. Não reformate pacotes com hashes para atualizar narrativa.
3. Execute verificações pertinentes: `python -m pytest -q`,
   `node --test tests/web_review.test.cjs` e auditorias dos artefatos afetados.
   Use Python 3.11/3.12; a CI usa Node 22. O notebook tem ambiente separado,
   documentado na [entrega acadêmica](docs/entregas/pi_iv_pln_20261020/README.md).
4. Descreva problema, mudança, verificação e limitações. Mudanças apenas
   documentais podem ser conferidas por links, comandos e integridade, sem nova
   inferência nem testes que apenas reproduzam o texto.
5. Não inclua ambientes, pesos ou workspaces mutáveis por acidente. Publicações
   devem ter escopo e proveniência explícitos. Antes de remover código arquivado,
   confira os auditores e as referências que dependem dele.
