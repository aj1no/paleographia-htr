# Triagem e fichamento — modelos sem estudos preenchidos

Seguir o [protocolo de PI IV](../literature_review.md) e vincular cada ocorrência
ao [registro de buscas](registro_buscas.md). Nenhuma tabela abaixo contém estudos
triados ou fichados. As fontes já conhecidas devem manter essa origem e o escopo
real de leitura; não herdam aprovação para inclusão.

## Ocorrências, registros canônicos e seleção

Uma ocorrência conserva sua base/consulta ou origem complementar. Um registro
canônico reúne ocorrências e versões do mesmo trabalho, sem apagar os originais.

| ID da ocorrência | Execução/origem | DOI/arXiv/URL e versão | Título/autores/ano | ID canônico | Relação: único/duplicata/preprint/artigo | Evidência da identificação |
| --- | --- | --- | --- | --- | --- | --- |

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
