# Índice da documentação

Estado em 12/11/2026, na branch `main` (versão 1.0.0, a da entrega final). O
[README principal](../README.md) resume o projeto, os resultados e como instalar.

## Entrega final (novembro de 2026)

| Material | O que traz |
| --- | --- |
| [Artigo de PLN](entregas/artigo_20261107/README.md) | Ajuste fino, análise de erros, pós-correção e teste reservado |
| [Notebook comparativo, 09/11 (Entrega 06 do PI IV)](entregas/notebook_comparativo_20261109/README.md) | Base × ajustados A e B na validação e no teste reservado, com intervalos e tipos de erro |
| [Notebook 3 de PLN](entregas/notebook_3_pln/README.md) | Análise linguística dos erros e pós-correção Levenshtein × TF-IDF |
| [Resumo e roteiro da apresentação de 19/11](entregas/apresentacao_20261119/PaleographIA_resumo_e_roteiro.pdf) | Como o programa funciona, números, fala de cada integrante e perguntas prováveis ([roteiro em Markdown](entregas/apresentacao_20261119/ROTEIRO.md)) |
| [Teste reservado congelado](revisao_humana/teste_reservado_congelado_20261109/README.md) | 49 linhas lidas às cegas; avaliação única de base, A, B e D1, com intervalos |
| [Ajustados C e D1: Posturas de 1831](experimentos/ppocrv6_ajustado_C/noturno_20261110/README.md) | O D1, modelo da entrega, escolhido no fólio 101r fora do treino; o D2 empatou ([treino C gravado](experimentos/ppocrv6_ajustado_C/gravacao_20261110/treino_C/README.md)) |
| [Ajuste fino A e B](experimentos/ppocrv6_ajuste_fino_20261105/README.md) | Treinos gravados de 06/11 e 07/11 |
| [Leitura modernizada v1 a v3](experimentos/modernizacao_20261107/README.md) | Regras de grafia avaliadas contra a edição do Arquivo; palavras a conferir e [glossário](glossario/README.md) |
| [Curadoria dos fólios novos](revisao_humana/novos_folios_20261110/README.md) | Posturas de 1831 validadas pela equipe; carta de 1767 e contrato do livro 13 em andamento |
| [Organização da entrega, 12/11](manutencao/organizacao_entrega_20261112/README.md) | O que saiu do repositório e por quê, nomes encurtados e reescrita do histórico |

## Para usar e conferir

- [Execução e revisão local](runbook.md), [ambientes e modelos](environment.md), [runtime do reconhecedor](../runtime/kraken_ppocrv6/README.md).
- [Protocolo de avaliação](evaluation_protocol.md), [esquema dos dados](data_schema.md), [política de transcrição](transcription_policy.md).
- [Fontes e condições de uso](sources.md), [declaração de uso de IA](ai_comments.md).
- [Bibliografia comentada e fichamentos](bibliografia/README.md).
- [Contexto completo do projeto](CONTEXTO_COMPLETO_PROJETO.md) (retrato de 05/11) e [guia para revisar o projeto](guia_revisao_gpt.md).

## Entregas de outubro (PI IV e PLN), preservadas

| Material | Situação |
| --- | --- |
| [Continuidade após o Notebook 1](entregas/continuidade_20261103/README.md) | Requisitos originais recuperados em 03/11; sequência das próximas etapas e notebook de conferência dos dados executado |
| [Notebook 1: pacote offline e versão executada](entregas/notebook_1_offline/README.md) | Publicado em 03/11; script e notebook reduzido reproduzem as métricas com dados incorporados; versão detalhada disponível para consulta |
| [Ponto de entrada da entrega atual](entregas/pi_iv_pln_20261023_fechamento/README.md) | Artigo atualizado e notebook indicado; links prontos para o grupo 4, célula F11; rodada humana preparada; submissão e confirmações pendentes |
| [Abrir e preencher no Google Colab](entregas/pi_iv_pln_20261023_colab/README.md) | Botão direto, preparação do ambiente, formulários por aluno e download do ZIP de relatos para conferência |
| [Notebook colaborativo e cronograma da equipe](entregas/pi_iv_pln_20261023_equipe/README.md) | Atividades por integrante e registro de discussão/análise; 16 células executadas por IA, formulários individuais vazios; núcleo numérico preservado |
| [Versão editorial anterior — PDF e Word](entregas/pi_iv_pln_20261023_entrega/README.md) | Três páginas preservadas; sucedida pelo ponto de entrada atual, com vínculo ao Colab e declaração de Antigravity |
| [Artigo com fundamentação ampliada — 23/10](entregas/pi_iv_pln_20261023_fundamentacao/README.md) | T1/T4 lidos integralmente por IA; fundamentos e discussão atualizados; métricas preservadas; revisão dos autores pendente |
| [Expansão do corpus e ajuste fino](dataset_expansion_20261023/README.md) | 15 fontes, oito novos recortes candidatos, núcleo 16/8 preservado; ensaio PP-OCRv6 com dois passos reais; avaliação científica pendente de revisão |
| [Referência assistida do 269r](revisao_humana/traslado_269r/referencia_assistida_20261020/README.md) | 24 linhas, cinco coberturas; 16 validadas e oito ressalvas |
| [Reconferência das oito ressalvas](revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/consolidacao.md) | Rodada concluída com dúvidas e apoio editorial preservados; registro aditivo, sem alterar a referência ou as métricas congeladas |
| [Curiosidade: reconhecedor treinado do zero](experimentos/modelo_do_zero_20261108/README.md) | CRNN-CTC sem pesos prévios + pré-treino não supervisionado; 1795: CER 15,94% (B: 10,14%); com 5% dos rótulos o pré-treino leva o CER de 71,88% a 28,12% |
| [Comparação de reconhecedores](experimentos/traslado_269r_reconhecedores_24_20261020/README.md) | PP-OCRv5 × PP-OCRv6, desenvolvimento |
| [269 reto inteiro contra a edição](experimentos/traslado_269r_integral_edicao_20261022/README.md) | Diagnóstico separado: segmentação automática + PP-OCRv6; CER 26,97%, WER 60,31%; bruto e revisões preservados |
| [269 verso inteiro contra a edição](experimentos/traslado_269v_integral_edicao_20261022/README.md) | Diagnóstico de desenvolvimento do mesmo documento, com pesos e parâmetros do reto; CER 16,48%, WER 56,25%; bruto, revisões e dúvidas preservados; sem treinamento ou teste reservado |
| [Correção de reprodução do verso e orientação da CI](manutencao/reprodutibilidade_269v_20261022/README.md) | Auditoria v2 aditiva: fonte exata no RAR (fora do repositório desde 12/11) ou PDF externo com hash; completo e parcial distintos; quatro ambientes leves e duas entregas acadêmicas na CI, sem diagnósticos integrais |
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

- [Grupo de teste reservado — pagamento a Thomas Pardo, 05/11](revisao_humana/pagamento_thomas_pardo_teste/README.md): decisão, partição proposta, ressalvas e protocolo de curadoria sem sugestões de modelo.
- [Segundo documento do teste — contrato do livro 12, 1763, 09/11](revisao_humana/contrato_livro12_teste/README.md): entra somado ao pagamento, escolhido só pela legibilidade, antes de qualquer modelo rodar no teste.
- [Teste reservado congelado, 09/11](revisao_humana/teste_reservado_congelado_20261109/README.md): 49 linhas e 1.644 caracteres em dois documentos, lidos às cegas; referência fixa antes da avaliação única.
- [Notebook comparativo, 09/11 (Entrega 06 do PI IV)](entregas/notebook_comparativo_20261109/README.md): baseline PP-OCRv6 × ajustados A e B na validação e no teste reservado, com intervalos, comparação pareada e tipos de erro.
- [Reescrita do histórico, 09/11](manutencao/reescrita_historico_20261109/README.md): mensagens de 41 commits sem a linha de coautoria; tabela commit antigo → novo, com árvores idênticas.
- [Esquema e estados](data_schema.md), [política de transcrição](transcription_policy.md).
- [Curadoria de 1795 — fechamento após 038 em 03/11](revisao_humana/sessao_1795/sessao_20261103/fechamento_curadoria_038.md): sete referências por linha validadas, oitava provável/excluída, identificação e cobertura parcial confirmadas; treino científico ainda sem partições prontas.
- [Próxima curadoria: carta de José Gomes de Gouveia de 1767](revisao_humana/carta_jose_gomes_1767/preparacao_20261103/README.md): primeiro recorte proposto, sem aprovação humana ou transcrição diplomática.
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

- [Retomadas de 03/11 e 05/11](entregas/continuidade_20261103/RETOMADA_20261105.md), [preparação inicial da apresentação](entregas/apresentacao_20261112/README.md), [revisão do repositório de 20/10](revisao_repositorio_20261020.md).
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
