# Coleta B01 e B02 no arXiv — 21/10/2026

**Recuperação concluída para estas duas consultas no arXiv; revisão sistemática
ainda em andamento.** Foram consultadas listagens, metadados, resumos e históricos
de versões. Não houve leitura integral, triagem formal ou inclusão definitiva.
Os arquivos do diagnóstico de desenvolvimento e suas oito ressalvas não mudaram.

## Protocolo e execução

Protocolo-base: commit `1faf5c214ed7248f7f0b9ea5c33e020e94d8431a`,
arquivo `docs/literature_review.md`. O [plano de coleta](plano_coleta.json)
foi registrado antes das buscas e contém as URLs, parâmetros e cláusulas
literais. SHA-256 do plano:
`6d84af8dd2dd469b64994c9e1a509554a88725b65b9be2f0a5202fef2e9d4257`.

Responsável pela coleta: **Codex, assistente de IA, em execução autorizada pelo
usuário**. Nenhuma leitura foi atribuída aos alunos ou ao professor. Conferência
humana deste lote: não registrada. Não foi obtida aprovação docente da revisão.

| Execução | Início em São Paulo (UTC−03) | Total informado / recuperado | Estado |
| --- | --- | --- | --- |
| ARXIV-B01-20261021 | 21/10/2026 11:40:34 | 3 / 3 | Recuperação concluída |
| ARXIV-B02-20261021 | 21/10/2026 11:40:37 | 2 / 2 | Recuperação concluída |

Modo: formulário público de busca avançada, via HTTP GET, com seis cláusulas
por consulta. Para cada uma das três frases, título e resumo foram conectados
por OR, conservando a expressão lógica do protocolo:

- **B01:** `"PP-OCRv5" OR "PP OCR v5" OR "PPOCRv5"`.
- **B02:** `"PP-OCRv6" OR "PP OCR v6" OR "PPOCRv6"`.

O formulário retornado manteve as seis cláusulas, operadores, campos e filtros
solicitados. A reprodução exata usa as URLs e os pares de parâmetros de
`plano_coleta.json`, não uma interpretação livre das expressões acima.

Filtros efetivamente aceitos: primeira submissão entre **01/01/2000 e
21/10/2026**, todas as categorias, inclusão de cross-list e de versões anteriores,
resumos visíveis, sem filtro de idioma ou de acesso aberto. Ordenação:
`-announced_date_first`; tamanho de página: 50. As listagens informaram
literalmente `Showing 1–3 of 3 results` e `Showing 1–2 of 2 results`.
Todos os resultados estavam na primeira página, sem próxima página habilitada.

## Registros e versões encontrados

Os cinco IDs do arXiv são distintos. A independência dos experimentos entre
artigos ainda depende da leitura; **cinco IDs não significam cinco estudos
independentes incluídos**. Não há repetição do mesmo ID entre B01 e B02.

| Ocorrência | ID e versão exibida | Título original | Primeira submissão no histórico UTC | Origem anterior |
| --- | --- | --- | --- | --- |
| B01-ARXIV-001 | [2609.24058v1](https://arxiv.org/abs/2609.24058v1) | All-in-One Multilingual Scene Text Recognition with Script-aware Mixture-of-Experts | 21/09/2026 03:34:56 | Sem vínculo no catálogo anterior consultado |
| B01-ARXIV-002 | [2603.24373v1](https://arxiv.org/abs/2603.24373v1) | PP-OCRv5: A Specialized 5M-Parameter Model Rivaling Billion-Parameter Vision-Language Models on OCR Tasks | 25/03/2026 14:54:40 | Sem vínculo no catálogo anterior consultado |
| B01-ARXIV-003 | [2507.05595v1](https://arxiv.org/abs/2507.05595v1) | PaddleOCR 3.0 Technical Report | 08/07/2025 02:14:10 | Já conhecido: `cui2025` |
| B02-ARXIV-001 | [2609.20064v1](https://arxiv.org/abs/2609.20064v1) | A Free Lunch? Adapting PP-OCRv6 for Historical Text Recognition | 17/09/2026 11:15:07 | Sem vínculo no catálogo anterior consultado |
| B02-ARXIV-002 | [2606.13108v1](https://arxiv.org/abs/2606.13108v1) | PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks | 11/06/2026 09:35:16 | Sem vínculo no catálogo anterior consultado |

Cada ficha exibiu somente **v1** no histórico consultado. As cinco versões estão
dentro do corte; seus links explícitos foram registrados para a futura leitura.
A versão identificada não equivale a texto integral lido. O registro no arXiv
não comprova revisão por pares; esse estado continua **não verificado**.

O relatório `2507.05595` já constava de
[fontes_consultadas.json](../../entregas/pi_iv_pln_20261020/fontes_consultadas.json),
com consulta anterior ao resumo e à seção 2.1. A ocorrência de B01 preserva esse
vínculo; não é apresentada como descoberta inédita nem contada novamente como
outro artigo. O escopo anterior não foi promovido a leitura integral.

## Datas, interpretação e limites

Em `2609.24058`, a listagem exibe 20/09/2026, enquanto o histórico da ficha
registra 21/09/2026 03:34:56 UTC. Em `2507.05595`, a listagem exibe 07/07/2025,
e o histórico registra 08/07/2025 02:14:10 UTC. Ambas as representações foram
preservadas, sem atribuir uma causa não verificada. Para identificar a versão
e conferir o corte, foi usado o horário UTC explícito do histórico.

O resumo de Kiessling (`2609.20064`) trata explicitamente de reconhecimento
histórico, por isso é um candidato útil para começar a leitura. Isso é uma
indicação de pertinência pelo resumo, não decisão formal de inclusão. Os textos
específicos de PP-OCRv5/PP-OCRv6 podem fundamentar componentes, mas suas variantes
e condições precisam ser conferidas antes de relacioná-los ao checkpoint latino
mobile/ONNX ou ao medium/Kraken usados no projeto.

Não foram extraídas tabelas de desempenho, fichamentos completos ou conclusões
para o artigo. A possível sobreposição entre o relatório de 2025 e o artigo
PP-OCRv5 de 2026 ainda precisa ser verificada. Também não foi investigada nesta
coleta a relação exata entre os pesos do projeto e os modelos descritos nos textos.
DOIs exibidos nas fichas foram registrados sem validação externa de seu cadastro.

As outras consultas e bases do protocolo continuam pendentes. Esta coleta não
prova ausência de outros textos sobre os componentes nem cobre menções que
apareçam somente no corpo do artigo, fora de título/resumo indexados.

## Evidências e preservação

- [resultados.json](resultados.json): execuções, ocorrências, autores, versões,
  datas, proveniência anterior, contagens locais e limites de leitura.
- [B01 — resposta HTML](b01_pagina_0000.html) e
  [recibo HTTP](b01_pagina_0000_requisicao.json).
- [B02 — resposta HTML](b02_pagina_0000.html) e
  [recibo HTTP](b02_pagina_0000_requisicao.json).
- `arxiv_*_ficha.html`: cinco fichas originais, acompanhadas de recibos HTTP
  com URL, horário, status e SHA-256. Não foram baixados PDFs ou textos integrais.
- [inventario.json](inventario.json): hashes dos arquivos deste pacote,
  excluindo o próprio inventário.
- [validacao.json](validacao.json): verificações locais de consultas, contagens,
  versões, links e preservação dos arquivos anteriores.

A coleta não usa inferência, treinamento, pesos ou o editor. Mantêm-se **as oito
ressalvas das linhas 11, 15, 16, 17, 19, 20, 23 e 24**, os textos assistidos e a
identificação **diagnóstico de desenvolvimento**, sem alegação de generalização.
Os pacotes congelados de revisão humana, experimento e entrega acadêmica
permanecem byte a byte como estavam. O progresso é registrado nos documentos
ativos; o protocolo-base continua identificável no commit acima.
