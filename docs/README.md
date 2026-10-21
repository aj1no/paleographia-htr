# Índice da documentação

Estado em 21/10/2026, na branch principal e padrão `main`.
O escopo permanece fechado para novas funções.

Use a `main` para consultar a versão atual e iniciar novas contribuições.
As branches anteriores e suas referências de publicação foram preservadas;
veja a [nota da adoção da main](manutencao/main_20261020/README.md).

## Para começar

- [Apresentação e resultados atuais](../README.md).
- [Execução e revisão local](runbook.md), [ambientes e modelos](environment.md).
- [Guia para revisar o projeto](guia_revisao_gpt.md).
- [Revisão do repositório e candidatos a organização](revisao_repositorio_20261020.md).

## Entrega atual de PI IV e PLN

| Material | Situação |
| --- | --- |
| [Referência assistida do 269r](revisao_humana/traslado_269r/referencia_assistida_20261020/README.md) | 24 linhas, cinco coberturas; 16 validadas e oito ressalvas |
| [Comparação de reconhecedores](experimentos/traslado_269r_reconhecedores_24_20261020/README.md) | PP-OCRv5 × PP-OCRv6, desenvolvimento |
| [Notebook, artigo e evidências](entregas/pi_iv_pln_20261020/README.md) | Notebook executado; artigo em primeiro rascunho |
| [CI acadêmica](manutencao/ci_academica_20261021/README.md) | Auditoria e reexecução do notebook, sem inferência; métricas, tabelas e oito ressalvas conferidas |
| [Adequação acadêmica](entregas/pi_iv_pln_20261020/adequacao_academica.md) | Rubricas, revisão bibliográfica e revisão dos autores pendentes |
| [Enquadramento das disciplinas](academic_alignment.md) | Dois reconhecedores em PLN; enquadramento PI IV a confirmar |
| [Protocolo bibliográfico de PI IV](literature_review.md) | Perguntas, buscas e critérios definidos para PP-OCRv5 × PP-OCRv6; seleção ainda não executada |

O [protocolo de avaliação](evaluation_protocol.md) registra a mudança do plano
de segmentação para o diagnóstico de reconhecedores. O [protocolo bibliográfico](literature_review.md)
foi atualizado em 21/10/2026 para PP-OCRv5 × PP-OCRv6. As buscas, a seleção e os
fichamentos ainda precisam ser executados; não é revisão sistemática concluída.
Os [registros de busca](bibliografia/registro_buscas.md) e os
[modelos de triagem/fichamento](bibliografia/triagem_e_fichamento.md) estão sem
resultados preenchidos; o protocolo anterior foi preservado como histórico.

## Uso e dados

- [Esquema e estados](data_schema.md), [política de transcrição](transcription_policy.md).
- [Consulta lexical](lexico_historico.md), [entrega lexical](lexico_entrega_20261019.md).
- [Teste lexical em cópia](testes/lexico_copia_20261019/README.md): não é revisão original.
- [Repertório do 100r](repertorio_100r.md): confirmações parciais.
- [Acervo e inventário](mineracao_acervo_jundiai.md).
- [Fontes e condições de uso](sources.md), [uso de IA](ai_comments.md).
- [Runtime do reconhecedor](../runtime/kraken_ppocrv6/README.md).

## Histórico preservado

Contagens, comandos e disponibilidade de modelos nestes registros devem ser
interpretados na data de cada etapa. Pacotes com hashes não devem ser editados
para atualizar a narrativa.

Menções a `codex/refatoracao-piloto`, a `master` ou à situação antiga da `main`
registram a origem e as condições da época. Inclusive os pacotes de entregas e
manutenção mantêm esses campos; isso não muda a branch principal atual.

- [Auditoria inicial de 15/10](audit.md), [relatório inicial](execution_report.md),
  [inventário legado](legacy_inventory.json).
- [Caderno do 269r](revisao_humana/traslado_269r/comparacao.md),
  [preparação das primeiras cinco linhas](revisao_humana/traslado_269r/conferencia_bloco.md).
- [TrOCR e PP-OCRv5 nas cinco linhas](experimentos/traslado_269r_20261016/README.md).
- [Integração inicial de PP-OCRv6](experimentos/traslado_269r_ppocrv6_20261016/README.md).
- [Sessão humana de 16/10](revisao_humana/traslado_269r/sessao_20261016/README.md)
  e [sessão de 19/10](revisao_humana/traslado_269r/sessao_20261019/README.md).
- [Integridade dos snapshots](revisao_humana/traslado_269r/integridade.md).
- [Código legado](../legacy/README.md), [execuções locais](../experiments/README.md).
- [Seis auxiliares arquivados, caminhos e hashes](../legacy/auxiliares_20261020/README.md).
- [Scripts numerados: caminhos de compatibilidade e avisos](manutencao/scripts_numerados_20261020/README.md).

A comparação de segmentadores e o [protocolo lexical futuro](protocolo_apoio_lexical.md)
permanecem fora da entrega atual; não foram executados como novos experimentos.
