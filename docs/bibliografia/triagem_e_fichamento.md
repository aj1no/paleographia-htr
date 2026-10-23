# Ocorrências recuperadas e modelos de triagem/fichamento

Seguir o [protocolo de PI IV](../literature_review.md) e vincular cada ocorrência
ao [registro de buscas](registro_buscas.md). A tabela de ocorrências registra
somente a recuperação B01/B02 no arXiv. **Triagem formal, leitura integral e
fichamentos deste lote estão pendentes.** As fontes já conhecidas mantêm origem e escopo
real de leitura; não herdam aprovação para inclusão.

**Adição de 23/10/2026:** a [seleção comentada](referencias_comentadas_20261023.md)
e os [fichamentos parciais](fichamentos_parciais_20261023.md) acrescentam consultas
dirigidas e pendências explícitas. A tabela histórica abaixo continua como
recuperação de 21/10; ver os vínculos canônicos no [registro complementar](registro_buscas.md#seleção-complementar-de-23102026).
Nenhuma decisão final de triagem ou leitura integral foi atribuída a essa adição.

## Ocorrências, registros canônicos e seleção

Uma ocorrência conserva sua base/consulta ou origem complementar. Um registro
canônico reúne ocorrências e versões do mesmo trabalho, sem apagar os originais.

| ID da ocorrência | Execução/origem | DOI/arXiv/URL e versão | Título/autores/ano | ID canônico | Relação: único/duplicata/preprint/artigo | Evidência da identificação |
| --- | --- | --- | --- | --- | --- | --- |
| B01-ARXIV-001 | ARXIV-B01-20261021 | 2609.24058v1 | All-in-One Multilingual Scene Text Recognition with Script-aware Mixture-of-Experts; Ye et al.; 2026 | ARXIV-2609.24058 | ID distinto no lote; somente v1 exibida; possível relação com outros estudos ainda não avaliada | [Ficha e histórico arquivados](arxiv_b01_b02_20261021/arxiv_2609_24058_ficha.html) |
| B01-ARXIV-002 | ARXIV-B01-20261021 | 2603.24373v1 | PP-OCRv5: A Specialized 5M-Parameter Model Rivaling Billion-Parameter Vision-Language Models on OCR Tasks; Cui et al.; 2026 | ARXIV-2603.24373 | ID distinto no lote; somente v1 exibida; sobreposição com relatório de 2025 a verificar | [Ficha e histórico arquivados](arxiv_b01_b02_20261021/arxiv_2603_24373_ficha.html) |
| B01-ARXIV-003 | ARXIV-B01-20261021; fonte anterior `cui2025` | 2507.05595v1 | PaddleOCR 3.0 Technical Report; Cui et al.; 2025 | ARXIV-2507.05595 | Mesmo ID da fonte conhecida; não é novo artigo; somente v1 exibida | [Ficha e histórico arquivados](arxiv_b01_b02_20261021/arxiv_2507_05595_ficha.html) |
| B02-ARXIV-001 | ARXIV-B02-20261021 | 2609.20064v1 | A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition; Kiessling; 2026 | ARXIV-2609.20064 | ID distinto no lote; somente v1 exibida; preprint, revisão por pares não verificada | [Ficha e histórico arquivados](arxiv_b01_b02_20261021/arxiv_2609_20064_ficha.html) |
| B02-ARXIV-002 | ARXIV-B02-20261021 | 2606.13108v1 | PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks; Zhang et al.; 2026 | ARXIV-2606.13108 | ID distinto no lote; somente v1 exibida; relação com checkpoint local a verificar | [Ficha e histórico arquivados](arxiv_b01_b02_20261021/arxiv_2606_13108_ficha.html) |

Autores completos, URLs, datas UTC e proveniência estão em
[resultados.json](arxiv_b01_b02_20261021/resultados.json). IDs canônicos agrupam
ocorrências do mesmo identificador; não afirmam independência entre experimentos.
O resumo e a seção 2.1 do relatório de 2025 já haviam sido consultados antes;
nenhuma leitura integral foi atribuída a esta coleta. As tabelas seguintes
continuam sem decisões de seleção ou fichamentos de artigos.

Registrar decisões por etapa e por adição. A leitura integral é distinta da
consulta ao resumo. Não usar ausência de resumo como exclusão automática.

| ID canônico | Etapa | Leitor e data | Decisão: manter/excluir/incluir/pendente | PB atendida e justificativa | Código e motivo principal | Página/seção ou tentativas de acesso | Classe: empírico/apoio técnico/contexto | Conferente e decisão final |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Ficha a copiar somente quando houver estudo real

- ID canônico, ocorrências e origem:
- Referência completa, DOI/URL, versões relacionadas e versão lida:
- Data de publicação/primeira versão e eventual exceção temporal:
- Tipo de publicação; revisão por pares informada ou não verificada:
- Leitor, data, idioma e páginas/seções efetivamente lidas:
- Pergunta/objetivo do estudo e PB1/PB2/PB3 atendidas:
- Corpus, idioma/escrita, número de documentos/escribas/páginas/linhas:
- Modelo, checkpoint, pré-treino e adaptação/treinamento realizados:
- Entradas, recortes, segmentação e pré-processamento de cada condição:
- Origem da referência, revisores, independência, convenções e dúvidas:
- Desenvolvimento/validação/teste, unidade de divisão e risco de sobreposição:
- CER/WER ou outras métricas, normalização, denominadores e agregação:
- Falhas, exclusões, configuração, dispositivo e definição dos tempos:
- Resultados nas condições do estudo, com tabela/página/seção de origem:
- Disponibilidade de dados/código/pesos e condições de uso:
- Limitações declaradas pelos autores:
- Limitações identificadas pelo leitor, separadas das declarações dos autores:
- Relação concreta com o diagnóstico de 24 linhas, sem extrapolar suas taxas:
- Trecho a citar ou paráfrase, com localização e conferência no original:
- Conferente, divergências e resolução; revisão única se não houver conferência:

Campo ausente na fonte deve ser marcado **não informado**; campo ainda não lido
é **não verificado**. Ambos diferem de zero e de não aplicável. Leitura auxiliada
por IA ou tradução deve ser registrada e conferida no original pelo responsável.

## Avaliação de qualidade, sem pontuação inventada

Para cada critério, preencher: informado, parcialmente informado, não informado
ou não aplicável; sempre localizar evidência e justificar não aplicável.

| Critério | Estado | Evidência/página/seção | Implicação para a interpretação |
| --- | --- | --- | --- |
| Corpus e tamanho | a verificar | a preencher | a preencher |
| Identificação dos modelos/configurações | a verificar | a preencher | a preencher |
| Preparação das entradas e comparação | a verificar | a preencher | a preencher |
| Referência, política textual e incertezas | a verificar | a preencher | a preencher |
| Métricas, denominadores e agregação | a verificar | a preencher | a preencher |
| Independência entre desenvolvimento e teste | a verificar | a preencher | a preencher |
| Falhas e exclusões | a verificar | a preencher | a preencher |
| Condições para reprodução | a verificar | a preencher | a preencher |
| Limites das conclusões | a verificar | a preencher | a preencher |

## Matriz de síntese a preencher após a leitura

| ID canônico | Classe e estado editorial | PB | Corpus/unidade de divisão | Modelo e adaptação | Referência/normalização | Métricas e condições dos resultados | Limitações/qualidade | Relação com o piloto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Não somar taxas heterogêneas nem ordenar modelos por resultados de conjuntos
diferentes. A síntese local mantém **diagnóstico de desenvolvimento**, referência
assistida e as oito ressalvas das linhas **11, 15, 16, 17, 19, 20, 23 e 24**.
Estes modelos não modificam o notebook, o artigo ou os alvos congelados.
