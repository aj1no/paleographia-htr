# Consolidação da curadoria de 1795 — 28/10/2026

Aplicação autorizada pelo solicitante das orientações recebidas após a análise do commit `bf1db30a93fee10808b1509054524ae572fe1864`. O parecer foi preservado [integralmente e sem alteração de bytes](parecer_recebido_chatgpt.md), identificado como análise assistida por IA, sem nova validação paleográfica independente.

**Resultado: oito geometrias validadas, oito transcrições pendentes e zero pares elegíveis para treinamento.** Os textos foram preservados literalmente. A quarta linha tem leitura parcial e motivo de exclusão explícito na linha e na exportação.

| Item | Antes | Depois |
| --- | --- | --- |
| Revisão do editor | `20261028T145912_c649c938` | `20261028T160355_969eab97` |
| Geometria | 8 `pending_review` | 8 `validated` |
| Transcrição | 8 `pending_review` | 8 `pending_review` |
| Sequência | Ordem 0–7 confirmada na observação 019 | Valores e associação preservados e conferidos |
| Linha 4 | Parcialidade registrada nas observações | `exclusion_reason` explicita parcialidade e continuação incerta |
| Correspondência documental | `pending_review` | `pending_review` |
| Cobertura | Bloco de oito linhas; `complete=false`, pendente | Preservada; página inteira não declarada completa |
| Elegibilidade para treino | 0 | 0 |

## O que foi aplicado no editor

As confirmações humanas de limites foram associadas por ID, fonte, hash do recorte e caixa. A atribuição retrospectiva das observações 001–005 foi conferida pelos hashes da observação 006. As oito marcações e ordens de leitura coincidem com a observação 019. O [preflight](preflight.json) registra essas verificações e o estado publicado de referência.

As oito atualizações foram realizadas pelo fluxo existente da API, com verificação da revisão esperada em cada chamada. O [plano](plano_consolidacao.json) e o [registro de consolidação](registro_consolidacao.json) vinculam as confirmações e datas humanas às novas revisões derivadas. Rodolfo Vinicius Cima Takemoto permanece como revisor das decisões geométricas; Codex é o agente que aplicou as decisões anteriores sob autorização do solicitante. Nenhuma nova declaração paleográfica foi atribuída ao revisor.

O campo compartilhado `reviewed_at` foi preenchido pelo serviço ao validar a geometria. Nesta rodada ele registra a aplicação geométrica, não aprovação textual. As datas das declarações humanas permanecem nas observações e nos recibos de revisão. Os metadados auxiliares herdados da preparação candidata foram preservados; o estado formal atual da geometria é dado por `geometry_status`.

Os valores existentes de `reading_order` já eram corretos; o esquema não possui um estado separado de aprovação da sequência. A correspondência foi consolidada pelo vínculo documental à observação 019 e pelas oito geometrias, sem criar novos campos ou alterar as ordens. A confirmação do bloco não foi convertida em aprovação da identificação documental, lado ou cobertura textual.

## Quarta linha e alternativas

O texto adotado continua **“de São Paulo, em casas de morada de Luiz”**, como rascunho humano parcial. As observações 009 → 016 → 017 preservam, respectivamente, a leitura inicial assistida, a releitura parcial e a segurança declarada para Luiz, com dúvida sobre a continuação. A leitura do trecho seguinte como possível sobrenome é interpretação do revisor.

A edição modernizada traz “de São Paulo em casas de morada do Juiz Presidente”. O parecer recebido favorece provisoriamente essa alternativa como hipótese visual assistida por IA. A [comparação das reproduções locais](inspecao_reproducoes_por_ia.json) também registra compatibilidade visual com essa hipótese, sem resolver cada grafema ou adotar uma correção.

Foi usado o campo existente `exclusion_reason`, conforme a [política de transcrição](../../../transcription_policy.md), para indicar que há continuação visível no recorte e que o texto atual não é um alvo completo. Essa informação acompanha a linha na exportação nativa e bloqueia sua elegibilidade. O texto não recebeu reticências ou marcadores editoriais novos. A linha não foi rejeitada, removida ou omitida do bloco.

## Preservação e exportação

- [Catálogo anterior](catalogo_antes.json) e [catálogo posterior](catalogo_depois.json).
- [Exportação nativa do editor em ZIP](exportacao_editor.zip) e [manifests extraídos](exportacao_editor/).
- [Linhas exportadas](exportacao_editor/lines.jsonl), [páginas](exportacao_editor/pages.jsonl) e [proveniência](exportacao_editor/provenance.json).
- [Conferência textual objetiva pendente](conferencia_textual_pendente.md).
- [Ampliações de estudo e sua proveniência](estudo_visual/proveniencia.json).
- [Validação e integridade desta consolidação](verificacao_consolidacao.json).

Textos, caixas, fontes, recortes, referências editoriais, divisão física **trat- / ando**, páginas, predições e revisões anteriores foram preservados. A página continua com fólio/lado declarados de origem, sem validação documental. Os estados de cobertura permanecem pendentes e `complete=false`. Os pequenos cruzamentos verticais entre caixas não motivaram mudança de geometria.

O índice da sessão foi atualizado para apontar esta rodada; os snapshots e as observações históricos permanecem íntegros. O histórico completo continua no workspace local; os oito recibos `revisao_01.json` a `revisao_08.json` registram a cadeia criada nesta aplicação.

## Próxima conferência e elegibilidade

O roteiro prioriza de/do, L/J e a continuação da quarta linha; possíveis abreviaturas nas linhas 1, 2 e 8; caixa, til, commum e pontuação. As duas reproduções já disponíveis foram comparadas. A análise assistida não estabeleceu vantagem suficiente para encerrar a disputa; ampliar pixels não recupera informação ausente. Nenhuma nova aquisição foi solicitada e nenhuma confirmação de limites ou hífen foi repetida.

Os validadores existentes verificam o catálogo e mantêm treino/avaliação bloqueados. Texto aprovado, identificação documental e cobertura ainda faltam; a linha 4 possui adicionalmente exclusão por transcrição parcial. As outras sete linhas não foram declaradas aptas. Condições de uso das fontes e partição por documento também seguem para conferência; nenhum novo split foi atribuído.

Não houve execução de reconhecedor, treinamento, cálculo de CER/WER, instalação, mudança de esquema ou nova funcionalidade nesta etapa.

A [auditoria existente do corpus](auditoria_corpus_existente.json) passou com 126 arquivos conferidos e zero novos pares validados. Os registros de treinamento apresentados nessa auditoria são evidências históricas de 23/10, não uma nova execução nesta consolidação.

Os atributos Git da pasta de curadoria preservam os bytes literais dos pareceres, observações, exportações e snapshots em Windows/Linux, mantendo os hashes de proveniência.
