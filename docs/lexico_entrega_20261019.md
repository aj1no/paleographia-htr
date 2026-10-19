# Entrega: base lexical histórica e consulta no editor

19/10/2026 · branch `codex/refatoracao-piloto` · base analisada
`3284e070285cac462bf38140618e053fe7161650`. Nenhuma mesclagem com `main` ou
`master`. Os commits posteriores existentes foram preservados.

## Implementação

- `src/paleographia/lexicon.py`: validação documental, consulta determinística,
  separação explícita de palavras e validação de eventos de aplicação.
- `api.py`, `services.py`, `web/index.html`, `web/review.js`: endpoint de consulta,
  painel em português, aplicação pontual ao rascunho e proveniência no histórico.
- `data/lexicon/{sources.json,entries.jsonl,coverage.json}`: catálogo, 21 registros
  reais e relatório de cobertura. Três verbetes de Bluteau, 18 atestações do
  acervo, nenhuma entrada indígena importada.
- `tests/test_lexicon.py`, `tests/web_review.test.cjs`: regressões da consulta,
  validação de fontes, proveniência, Unicode, rascunhos, navegação e conflitos.
- `frozen_experiment.py`, `tests/test_ppocrv6_audit.py` e
  `docs/experimentos/implementation_3284e07/`: resolução dos bytes históricos
  por hash, incluindo JavaScript. Quatro arquivos da implementação anterior
  foram arquivados literalmente do Git; inventários e experimentos anteriores
  permanecem intactos. A auditoria recusa um arquivo se seu hash não coincidir.
- `.gitattributes`: LF restrito aos novos arquivos de dados lexicais e
  preservação literal da nova cópia histórica, sem renormalizar o acervo.
- README, guia de revisão, runbook, [política lexical](lexico_historico.md) e
  [protocolo experimental futuro](protocolo_apoio_lexical.md) atualizados.

## Evidência de uso real e preservação

A consulta foi conferida no navegador com uma **cópia isolada** da sessão
269r. Nessa cópia, a linha 5 recebeu como rascunho a predição PP-OCRv6 já
preservada, `rro de Sundiahy, aonde Eu Publico TabaLiaõ aodi`.
A consulta real `Sundiahy` no repertório do acervo retornou `Jundiahy`, distância
1, com fonte e revisor originais. Aplicar alterou somente essa palavra no
rascunho e desmarcou a validação textual. Os outros erros permaneceram para
conferência. Trocar para a linha 6 e voltar preservou o rascunho e o evento.

O salvamento ocorreu somente na cópia isolada, sob identificação explícita
`Codex · teste de interface em cópia isolada`, e manteve a linha pendente.
As páginas/coberturas, todas as predições e o snapshot anterior dessa cópia
permaneceram iguais aos originais. A demonstração não é nova revisão humana,
nova inferência ou avaliação da correção. A consulta `Annodo` retornou `Anno do`
pelas entradas documentadas, com aplicação bloqueada onde o trecho não existia.

Veja o [rascunho antes de salvar](lexico_evidencias/rascunho_aplicado.png), a
[consulta documentada](lexico_evidencias/consulta.png) e o
[recibo completo de hashes e aplicação](lexico_evidencias/preservacao_e_interface.json).
O recibo compara **557 arquivos preexistentes**, todos preservados byte a byte,
incluindo dados locais, revisões humanas e experimentos. O ponteiro real
continua `20261016T191933_07d31bad`: 15 linhas, 1–10 validadas, 11–15 pendentes
com texto humano vazio; cobertura confirmada somente dos blocos 1–5 e 6–10.

## Verificações

| Verificação | Resultado |
| --- | --- |
| `python -m pytest -q` | 90 aprovados; um aviso de descontinuação AnyIO/Starlette |
| `node --test tests/web_review.test.cjs` | 29 aprovados |
| `python scripts/audit_ppocrv6_experiment.py --output <nova pasta>` | 60 arquivos; CER 30/242 e WER 23/45 reproduzidos das saídas salvas |
| `python scripts/audit_traslado_experiment.py --output <nova pasta>` | 55 arquivos; métricas históricas reproduzidas |
| `python -m compileall -q src scripts`, `python -m pip check`, `python -m paleographia --help` | Sem falhas |
| Navegador real | Consulta, aplicação, navegação e salvamento na cópia isolada |

Os testes sintéticos estão identificados como testes; a conferência dos
21 registros reais está separada. As páginas de Bluteau foram conferidas
visualmente e suas imagens/hashes estão publicados. O aviso de dependência
não foi suprimido nem motivou atualização de pacotes nesta entrega.

## Limites e continuação

Não há busca exaustiva: `Nacimento`, `Jezus`, `Jundiahy`, `sincoenta` e `mõr`
continuam sem conferência nos dicionários. `Sundiahy` não está atestado no lote;
ausência não prova erro. Morais e fontes indígenas foram apenas catalogados.
Não se atribuiu etimologia ou idioma a nomes pela aparência.

Não há novo CER/WER lexical ou das dez linhas, algoritmo de aceitação
automática, LLM, treino, resegmentação ou repetição de HTR. A consulta é apoio
humano. A próxima etapa é ampliar verbetes com páginas conferidas e continuar
a revisão das linhas pendentes, reservando outros grupos antes da futura
avaliação independente. A base atual do acervo vem do grupo de desenvolvimento
e exige controle de vazamento conforme o protocolo.
