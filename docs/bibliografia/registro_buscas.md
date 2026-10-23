# Registro de buscas bibliográficas — PI IV

Protocolo: [versão de 21/10/2026](../literature_review.md).
Estado: **coleta parcial iniciada: B01/B02 concluídas no arXiv; seleção
complementar recebida e conferida em 23/10; T1/T4 com leitura integral por IA
concluída; demais buscas e leituras, conferência humana e triagem formal
pendentes**. Não há estudos incluídos por decisão final nem
total global apurado da revisão.

## Identificação antes da primeira execução

- Versão/commit do protocolo usado neste lote: `1faf5c214ed7248f7f0b9ea5c33e020e94d8431a`.
- Responsável pela coleta: Codex, assistente de IA, em execução autorizada pelo usuário.
- Início: 21/10/2026, 11:40:34, São Paulo (UTC−03). Leitura humana não atribuída.
- Conferente e orientação docente: não registrados.
- Corte temporal: 21/10/2026; idiomas de leitura: português, inglês e espanhol.
- Cobertura planejada: B01–B08 em ACM, IEEE e arXiv; G01–G08 no Scholar;
  fontes conhecidas e uma rodada de rastreamento, identificadas separadamente.

## Execuções

Uma linha por base/consulta/versão;
desdobramentos recebem sufixo. Incluir buscas sem achados e tentativas bloqueadas.
Campo ainda não medido deve dizer **não apurado**; não usar zero como marcador.

| ID da execução | Base/coleção e modo | Consulta ID e expressão literal aceita/campos | Versão do protocolo | Data/hora e fuso | Responsável | Período, filtros e ordenação | Limite/posições previstas e vistas | Estado: concluída/parcial/bloqueada | Total da interface e se estimado | Registros realmente recuperados | Exportação/evidência e SHA-256 | Bloqueio/desvio e providência |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARXIV-B01-20261021 | arXiv / formulário avançado, HTTP GET | B01: `"PP-OCRv5" OR "PP OCR v5" OR "PPOCRv5"`; seis cláusulas OR em título/resumo, parâmetros literais no plano | `1faf5c2` | 21/10/2026 11:40:34 UTC−03 | Codex (IA) | Primeira submissão 2000-01-01–2026-10-21; todas as categorias, cross-list e versões anteriores; sem filtro de idioma; `-announced_date_first` | Sem cota; página de 50; posições 1–3 de 3 vistas | concluída para recuperação | 3, não estimado | 3 | [Pacote, plano, HTML e hashes](arxiv_b01_b02_20261021/README.md) | Sem bloqueio; triagem e leitura pendentes |
| ARXIV-B02-20261021 | arXiv / formulário avançado, HTTP GET | B02: `"PP-OCRv6" OR "PP OCR v6" OR "PPOCRv6"`; seis cláusulas OR em título/resumo, parâmetros literais no plano | `1faf5c2` | 21/10/2026 11:40:37 UTC−03 | Codex (IA) | Primeira submissão 2000-01-01–2026-10-21; todas as categorias, cross-list e versões anteriores; sem filtro de idioma; `-announced_date_first` | Sem cota; página de 50; posições 1–2 de 2 vistas | concluída para recuperação | 2, não estimado | 2 | [Pacote, plano, HTML e hashes](arxiv_b01_b02_20261021/README.md) | Sem bloqueio; triagem e leitura pendentes |

O plano foi salvo antes da coleta. A primeira validação da interface preservou
as expressões lógicas, desdobrando cada frase nos campos título e resumo; não
mudou período, critérios ou escopo. As seis cláusulas de termo/campo/operador
e os filtros aceitos foram conferidos no HTML retornado. Uma página por consulta
foi suficiente para recuperar os totais exibidos.

Guardar as exportações e evidências em uma pasta datada por execução, sem
sobrescrever arquivos existentes. Anotar formato, nome, hash, consulta e lote;
quando não houver exportação, registrar manualmente IDs/URLs e posições vistas.
O caminho neste registro deve permitir localizar a evidência. Não arquivar
credenciais nem redistribuir texto integral sem condição de uso conhecida.

Uma tentativa bloqueada não tem total zero. Uma coleta parcial deve informar
os lotes/posições faltantes. No Scholar, o limite de 100 inclui duplicatas;
registrar separadamente o total estimado na tela e as posições de fato vistas.

## Origens complementares

A origem anterior abaixo é vinculada ao mesmo registro recuperado em B01;
não constitui um sexto artigo nem uma busca complementar já concluída. Não
atribuir à busca nova um artigo que já era conhecido.

| ID da ocorrência | Origem: fonte conhecida/referência/citação | ID do estudo-semente ou arquivo anterior | Data e responsável | URL/DOI/versão | Posição e ordenação quando aplicável | Evidência e registro canônico vinculado |
| --- | --- | --- | --- | --- | --- | --- |
| CONHECIDA-cui2025 | Fonte conhecida antes do protocolo; vinculada a B01-ARXIV-003 | `docs/entregas/pi_iv_pln_20261020/fontes_consultadas.json`, ID `cui2025` | Consulta anterior registrada em 20/10/2026; vínculo conferido por Codex em 21/10/2026 | https://arxiv.org/abs/2507.05595v1 | Não aplicável; origem anterior à coleta | `ARXIV-2507.05595`; seção 2.1 e resumo previamente consultados, sem leitura integral declarada |

## Contagens para reconciliar após a coleta e seleção

Totais globais continuam **não apurados**. Há somente a recuperação local de
cinco ocorrências B01/B02 no arXiv, com cinco IDs distintos, nenhuma repetição
de ID entre as duas consultas e um vínculo a fonte anterior. A independência
entre estudos e suas versões conceituais depende da leitura; não foi apurada.
A tabela não representa um fluxograma preenchido da revisão completa.
Reconstruir os valores a partir das ocorrências e decisões, por origem e no
total deduplicado; distinguir retirada de duplicata de exclusão por conteúdo.

| Etapa | Contagem | Evidência que permitirá apurar |
| --- | --- | --- |
| Ocorrências recuperadas nas bases principais | parcial: 5 no lote arXiv B01/B02; total global não apurado | Duas respostas HTML completas; ver `resultados.json` do lote |
| Ocorrências complementares: Scholar, fontes conhecidas e rastreamento | não apurada | Registros por origem e posição |
| Duplicatas/versões agrupadas | não apurada | Mapeamento de ocorrências ao registro canônico |
| Registros únicos triados por título/resumo | não apurada | Decisões de triagem |
| Excluídos por título/resumo | não apurada | Motivos registrados por estudo |
| Textos integrais buscados, obtidos e não obtidos | não apurada | Tentativas de acesso e decisões |
| Excluídos após leitura integral, por motivo | não apurada | Motivo principal, página/seção e conferência |
| Estudos primários incluídos na síntese empírica | não apurada | Fichamentos e decisões finais |
| Fontes técnicas/contextuais de apoio | não apurada | Classificação separada da síntese empírica |

## Emendas posteriores à versão de 21/10/2026

Não houve alteração de consultas, corte temporal ou critérios em 23/10. O registro
complementar abaixo é aditivo; não substitui uma busca planejada nem uma decisão
de inclusão. Preencher emendas de protocolo quando necessárias, sem apagar
consultas ou decisões anteriores.

| ID/data | Responsável | Regra anterior | Regra nova e motivo | Resultados já vistos ao decidir | Execuções/decisões afetadas e necessidade de repetição |
| --- | --- | --- | --- | --- | --- |

## Seleção complementar de 23/10/2026

Origem: Markdown bibliográfico recebido do usuário, atualizado após conferência
dirigida de registros institucionais e trechos de fontes. Responsável pela
organização/consulta: Codex (IA); conferência humana e seleção final pendentes.
[Original e recibo](README.md), [referências revistas](referencias_comentadas_20261023.md)
e [registro estruturado das 14 entradas](referencias_20261023.json).
As 12 entradas P1–P6/T1–T6 e duas fontes documentais não são 14 estudos empíricos
incluídos. Não atualizar totais globais com essa contagem de entradas.

| Ocorrência complementar | Identidade / vínculo anterior | Consulta e tratamento |
| --- | --- | --- |
| COMP-20261023-T3 | `ARXIV-2507.05595`; `B01-ARXIV-003`; fonte conhecida `cui2025` | Mesmo trabalho; preservar origem e contagem anterior |
| COMP-20261023-T4 | `ARXIV-2609.20064`; `B02-ARXIV-001` | Mesma v1; metadados/trechos conferidos; ficha parcial, sem inclusão final |
| COMP-20261023-P6 | `ACL-L06-1222`; fonte conhecida `sousa2006` | Mesmo artigo já citado em `fontes_consultadas.json`; não presumir novidade |
| Demais COMP-20261023-P*/T*/D* | Identificadores e fontes no JSON complementar | Origem complementar; consulta e leitura descritas por entrada; independência científica não apurada |

O artigo T4 difere da ficha de modelo Zenodo denominada `kiessling2026` nos
pacotes acadêmicos. T5 reúne a publicação CACM e a versão arXiv como versões
relacionadas, sem contá-las automaticamente como dois estudos.
Os [fichamentos parciais de T1/T4](fichamentos_parciais_20261023.md) localizam
o escopo da consulta inicial; foram sucedidos pela leitura registrada abaixo.

## Leitura integral posterior de T1/T4 — 23/10/2026

Codex (IA) leu integralmente T1 (23 páginas, UCL) e T4 v1 (14 páginas, arXiv),
incluindo notas e referências, e preencheu os [fichamentos e a avaliação de qualidade](leitura_t1_t4_20261023/README.md).
T1 foi obtido por URL institucional alternativa após o bloqueio em Edimburgo.
O [manifesto](leitura_t1_t4_20261023/manifesto.json) fixa URLs, versões, hashes,
licença e páginas lidas. As fontes externas citadas pelos artigos não foram
automaticamente consideradas lidas.

Contagem desta etapa: **dois textos integrais lidos por IA, 37 páginas, dois
fichamentos concluídos**. São os mesmos IDs já registrados: não acrescentam
ocorrências B01/B02 nem alteram o total de 14 entradas complementares.
Conferência humana e inclusão final permanecem pendentes. As consultas, o
corte de 21/10 e a cobertura do protocolo não foram alterados; a data desta
leitura é posterior, e os dois trabalhos já existiam no corte previsto.
