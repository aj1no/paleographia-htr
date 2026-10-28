# Índice da documentação

Estado em 28/10/2026, na branch principal e padrão `main`.
A expansão de fontes e o ajuste fino passaram a integrar a etapa acadêmica.

Use a `main` para consultar a versão atual e iniciar novas contribuições.
As branches anteriores e suas referências de publicação foram preservadas;
veja a [nota da adoção da main](manutencao/main_20261020/README.md).

## Para começar

- [Apresentação e resultados atuais](../README.md).
- [Execução e revisão local](runbook.md), [ambientes e modelos](environment.md).
- [Guia para revisar o projeto](guia_revisao_gpt.md).
- [Bibliografia comentada, fontes e fichamentos integrais de T1/T4](bibliografia/README.md).
- [Revisão do repositório e candidatos a organização](revisao_repositorio_20261020.md).

## Entrega atual de PI IV e PLN

| Material | Situação |
| --- | --- |
| [Ponto de entrada da entrega atual](entregas/pi_iv_pln_20261023_fechamento/README.md) | Artigo atualizado e notebook indicado; links prontos para o grupo 4, célula F11; rodada humana preparada; submissão e confirmações pendentes |
| [Abrir e preencher no Google Colab](entregas/pi_iv_pln_20261023_colab/README.md) | Botão direto, preparação do ambiente, formulários por aluno e download do ZIP de relatos para conferência |
| [Notebook colaborativo e cronograma da equipe](entregas/pi_iv_pln_20261023_equipe/README.md) | Atividades por integrante e registro de discussão/análise; 16 células executadas por IA, formulários individuais vazios; núcleo numérico preservado |
| [Versão editorial anterior — PDF e Word](entregas/pi_iv_pln_20261023_entrega/README.md) | Três páginas preservadas; sucedida pelo ponto de entrada atual, com vínculo ao Colab e declaração de Antigravity |
| [Artigo com fundamentação ampliada — 23/10](entregas/pi_iv_pln_20261023_fundamentacao/README.md) | T1/T4 lidos integralmente por IA; fundamentos e discussão atualizados; métricas preservadas; revisão dos autores pendente |
| [Expansão do corpus e ajuste fino](dataset_expansion_20261023/README.md) | 15 fontes, oito novos recortes candidatos, núcleo 16/8 preservado; ensaio PP-OCRv6 com dois passos reais; avaliação científica pendente de revisão |
| [Referência assistida do 269r](revisao_humana/traslado_269r/referencia_assistida_20261020/README.md) | 24 linhas, cinco coberturas; 16 validadas e oito ressalvas |
| [Reconferência das oito ressalvas](revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/consolidacao.md) | Rodada concluída com dúvidas e apoio editorial preservados; registro aditivo, sem alterar a referência ou as métricas congeladas |
| [Comparação de reconhecedores](experimentos/traslado_269r_reconhecedores_24_20261020/README.md) | PP-OCRv5 × PP-OCRv6, desenvolvimento |
| [269 reto inteiro contra a edição](experimentos/traslado_269r_integral_edicao_20261022/README.md) | Diagnóstico separado: segmentação automática + PP-OCRv6; CER 26,97%, WER 60,31%; bruto e revisões preservados |
| [269 verso inteiro contra a edição](experimentos/traslado_269v_integral_edicao_20261022/README.md) | Diagnóstico de desenvolvimento do mesmo documento, com pesos e parâmetros do reto; CER 16,48%, WER 56,25%; bruto, revisões e dúvidas preservados; sem treinamento ou teste reservado |
| [Correção de reprodução do verso e orientação da CI](manutencao/reprodutibilidade_269v_20261022/README.md) | Auditoria v2 aditiva: fonte exata no RAR versionado ou PDF externo com hash; completo e parcial distintos; quatro ambientes leves e duas entregas acadêmicas na CI, sem diagnósticos integrais |
| [Notebook, artigo e evidências — versão de 22/10](entregas/pi_iv_pln_20261022/README.md) | Reconferência posterior incorporada; oito ressalvas históricas e métricas de 20/10 preservadas |
| [Entrega acadêmica congelada de 20/10](entregas/pi_iv_pln_20261020/README.md) | Pacote original preservado; referência das métricas; verificado junto à versão de 22/10 |
| [CI acadêmica das duas versões](manutencao/ci_academica_duas_versoes_20261022/README.md) | Auditoria e reexecução de 20/10 e 22/10, sem inferência; saídas e artefatos separados; oito ressalvas e reconferência preservadas |
| [Adequação acadêmica](entregas/pi_iv_pln_20261022/adequacao_academica.md) | Rubricas, demais buscas, triagem/leitura bibliográfica e revisão dos autores pendentes |
| [Enquadramento das disciplinas](academic_alignment.md) | Dois reconhecedores em PLN; enquadramento PI IV a confirmar |
| [Protocolo bibliográfico de PI IV](literature_review.md) | PP-OCRv5 × PP-OCRv6; B01/B02 executadas no arXiv, demais buscas e seleção pendentes |
| [Primeira coleta bibliográfica](bibliografia/arxiv_b01_b02_20261021/README.md) | B01: 3 registros; B02: 2; cinco IDs distintos, todos v1; um já conhecido; sem inclusão definitiva |

O [protocolo de avaliação](evaluation_protocol.md) registra a mudança do plano
de segmentação para o diagnóstico de reconhecedores. O [protocolo bibliográfico](literature_review.md)
foi atualizado em 21/10/2026 para PP-OCRv5 × PP-OCRv6. B01 e B02 já foram
executadas no arXiv; T1/T4 têm fichamentos integrais por IA. Outras buscas e
leituras, conferência humana e seleção final continuam pendentes.
Não é revisão sistemática concluída.
Os [registros de busca](bibliografia/registro_buscas.md) e os
[modelos de triagem/fichamento](bibliografia/triagem_e_fichamento.md) distinguem
recuperação, fonte já conhecida e leitura pendente. O protocolo anterior foi
preservado como histórico.

## Uso e dados

- [Esquema e estados](data_schema.md), [política de transcrição](transcription_policy.md).
- [Curadoria de 1795 — consolidação de 28/10](revisao_humana/sessao_1795/consolidacao_20261028/README.md): oito geometrias validadas, textos pendentes e quarta linha parcial; zero pares elegíveis para treino.
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
