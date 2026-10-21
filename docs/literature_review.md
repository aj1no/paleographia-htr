# Protocolo bibliográfico de PI IV — PP-OCRv5 × PP-OCRv6

Versão de **21/10/2026**. Estado: **planejamento definido; buscas de estudos,
triagem e fichamentos ainda não executados sob este protocolo**. A adequação
à rubrica de PI IV continua sem confirmação docente. Este documento define
o trabalho a realizar; não apresenta resultados de revisão sistemática.

## 1. Objetivo, contexto e limites

Organizar a revisão que fundamentará a comparação de **latin PP-OCRv5
mobile/ONNX × PP-OCRv6 medium/Kraken** na transcrição de manuscritos históricos.
Buscar evidência sobre comparação de reconhecedores pré-treinados, avaliação
reproduzível por CER/WER e influência das convenções da referência.

O [diagnóstico já publicado](experimentos/traslado_269r_reconhecedores_24_20261020/README.md)
usa os mesmos 24 recortes do corpo do fólio 269r, em cinco blocos, com referência
assistida pela edição. O fólio permanece **desenvolvimento**, sem teste reservado,
treinamento ou estimativa de generalização. Diferenças de variante, pré-treino,
implementação e pré-processamento impedem atribuir o resultado apenas à versão.

As **oito ressalvas** das linhas **11, 15, 16, 17, 19, 20, 23 e 24** permanecem
registradas. Incluem Requererão e seus sinais, trechos das linhas 15/16/20,
ministros/menistros, orgente/ergente, Justissa e a abreviatura Magᵈᵉ.
Ver a [tabela congelada de ressalvas](entregas/pi_iv_pln_20261020/tabelas/ressalvas.csv).
A literatura não confirma essas leituras pela imagem nem promove o alvo
assistido a referência humana independente. Mantêm-se também as decisões
Eram, Com, Como, que mais e a separação entre Magᵈᵉ e seu desenvolvimento editorial.

Este protocolo é posterior ao diagnóstico e à consulta inicial de fontes.
Não é pré-registro das inferências nem seleção bibliográfica feita sem conhecer
os resultados locais. As buscas devem acolher achados favoráveis, negativos e
inconclusivos, sem selecionar estudos pela concordância com o diagnóstico.

## 2. Perguntas da revisão

Os identificadores **PB1–PB3** são próprios desta revisão e não substituem
retroativamente as RQ1–RQ3 do planejamento histórico de segmentação.

| ID | Pergunta | Elementos a extrair |
| --- | --- | --- |
| PB1 | Como estudos primários comparam reconhecedores pré-treinados em manuscritos históricos, especialmente em português ou escrita latina? | Modelos e checkpoints; corpus e idioma; mesmos recortes ou detecção própria; adaptação; pré-processamento; unidade documental; separação desenvolvimento/teste |
| PB2 | Como referências e protocolos de CER/WER tratam grafia histórica, caixa, diacríticos, abreviaturas, espaços e incertezas? | Origem e independência da referência; revisores; normalização; denominadores; agregação; tratamento de falhas e ambiguidades |
| PB3 | Quais erros e limitações são relatados, e em que condições podem ajudar a interpretar este diagnóstico? | Omissões, letras, espaços, sinais e abreviaturas; deslocamento de domínio; diferenças de configuração; riscos de vazamento e limites de generalização |

Não se exige que um estudo mencione ambos os PP-OCR para responder às perguntas.
A busca direta verifica fontes específicas dos componentes; a busca temática
fundamenta método e análise. Não se presume a existência de comparação publicada
PP-OCRv5 × PP-OCRv6 nem sua ausência antes de executar a busca.

## 3. Cobertura e fontes

- **Período principal:** 01/01/2000 a 21/10/2026, inclusive. O intervalo amplo
  permite recuperar avaliação e representação de corpora anteriores aos modelos
  atuais. Registrar publicação e primeira versão pública; material posterior
  ao corte exige emenda, sem substituição silenciosa.
- **Idiomas de leitura:** português, inglês e espanhol. Não aplicar filtro de
  idioma na recuperação; identificar textos em outros idiomas na triagem e
  registrar a limitação de leitura, sem inferir irrelevância pelo título.
- **Bases principais:** ACM Digital Library, IEEE Xplore e arXiv. O arXiv é
  tratado como fonte de preprints; registrar o estado de revisão por pares de
  cada trabalho, sem equipará-lo automaticamente a artigo publicado.
- **Busca complementar:** Google Scholar e uma rodada de referências/citações
  dos estudos incluídos, além das fontes conhecidas antes deste protocolo.
- **Fontes técnicas separadas:** documentação oficial, relatórios dos autores,
  fichas dos checkpoints, código e acervo/edição. Podem fundamentar componentes
  ou proveniência, mas documentação sem estudo empírico não integra a síntese
  de estudos de desempenho.

Nas bases principais, examinar todos os registros recuperados e acessíveis de
cada consulta, sem cota por resultado favorável. Limites de exportação devem ser
tratados por lotes/paginação. Se uma base impedir completar a recuperação,
registrar a interrupção, sem alegar cobertura integral dessa base.

No Google Scholar, examinar **as primeiras 100 posições por consulta, ou todas
se houver menos**, ordenadas por relevância. Duplicatas também ocupam posições;
não continuar além de 100 para compensá-las. É um limite operacional exclusivo
da busca complementar, com viés de ordenação explicitado na síntese. Registrar
data, ordenação, posições efetivamente vistas e eventuais bloqueios. O total
estimado na tela não é o número de registros exportados ou triados.

## 4. Consultas planejadas

Executar **B01–B08 em cada uma das três bases principais**. As expressões abaixo
são a especificação lógica; a tradução para cada interface deve conservar os
conceitos e ficar registrada antes da execução. Não são consultas já testadas.
Se a interface exigir desdobrar OR ou limitar campos, atribuir sufixos às
subconsultas e preservar todas as versões, com justificativa.

| ID | Expressão lógica | Finalidade |
| --- | --- | --- |
| B01 | `"PP-OCRv5" OR "PP OCR v5" OR "PPOCRv5"` | Fontes e avaliações específicas do primeiro componente |
| B02 | `"PP-OCRv6" OR "PP OCR v6" OR "PPOCRv6"` | Fontes e avaliações específicas do segundo componente |
| B03 | `("handwritten text recognition" OR "handwriting recognition") AND (historical OR manuscript) AND (comparison OR evaluation OR benchmark)` | Comparações de reconhecimento histórico |
| B04 | `("handwritten text recognition" OR "handwriting recognition") AND (Portuguese OR "Latin script" OR "Latin-script")` | Idioma e sistema de escrita próximos do corpus |
| B05 | `("handwritten text recognition" OR "handwriting recognition") AND ("character error rate" OR "word error rate" OR CER OR WER) AND (transcription OR normalization OR abbreviation OR spacing)` | Política textual e avaliação |
| B06 | `("handwritten text recognition" OR "handwriting recognition") AND ("pre-trained" OR pretrained OR "domain adaptation" OR "cross-domain" OR "zero-shot") AND (historical OR manuscript)` | Transferência e diferenças de domínio |
| B07 | `("reconhecimento de manuscritos" OR "reconhecimento de texto manuscrito") AND (histórico OR históricos OR português) AND (avaliação OR comparação)` | Literatura em português |
| B08 | `("reconocimiento de manuscritos" OR "reconocimiento de texto manuscrito") AND (histórico OR históricos OR portugués) AND (evaluación OR comparación)` | Literatura em espanhol |

Nas B01/B02, não exigir manuscrito ou avaliação no primeiro filtro: a fonte
original de um componente pode ter outro domínio. Na seleção, distinguir a
descrição técnica de um checkpoint de evidência empírica aplicável ao manuscrito.

Adaptação prevista, a validar na execução:

| Fonte | Campo e execução planejados | Registro obrigatório |
| --- | --- | --- |
| ACM Digital Library | Busca avançada em título, resumo e palavras-chave/metadados; combinar campos por OR e conceitos por AND. Usar o Guide to Computing Literature quando disponível. | Coleção escolhida, campos, expressão aceita, período e eventuais desdobramentos; não confundir busca em metadados com texto integral |
| IEEE Xplore | Busca de metadados em Basic/Command Search, com operadores em maiúsculas; não presumir suporte a expressões completas dentro de cada campo da busca avançada. | Modo, campos/expressão efetivamente aceitos e filtros |
| arXiv | Busca avançada em título/resumo, com conceitos distribuídos nos campos; registrar separadamente a versão selecionada e a data usada no filtro. | Campos, conectores, data de submissão/versão e expressão ou formulário reproduzível |

Para o Google Scholar, usar estas consultas curtas, sem presumir equivalência
com a álgebra booleana das demais bases, no mesmo intervalo temporal:

| ID | Consulta literal |
| --- | --- |
| G01 | `"PP-OCRv5"` |
| G02 | `"PP-OCRv6"` |
| G03 | `"handwritten text recognition" historical evaluation` |
| G04 | `"handwritten text recognition" Portuguese` |
| G05 | `"handwritten text recognition" "character error rate" transcription` |
| G06 | `"handwritten text recognition" "domain adaptation" historical` |
| G07 | `"reconhecimento de manuscritos" avaliação` |
| G08 | `"reconocimiento de manuscritos" evaluación` |

Não filtrar apenas acesso aberto na busca. Antes de declarar texto indisponível,
verificar a página editorial, DOI, repositório dos autores e versões públicas.
Sem acesso à leitura integral, manter a limitação registrada; não declarar
leitura ou extração de resultados que não ocorreu.

## 5. Elegibilidade e critérios de exclusão

Incluir na **síntese empírica** estudos primários com texto integral legível,
identificação de método e corpus, e avaliação verificável que responda a pelo
menos uma PB. Isso abrange reconhecimento histórico/latino e estudos de avaliação
textual transferíveis à pergunta, mesmo sem PP-OCR ou comparação de dois modelos.
Não exigir melhora de CER/WER, código aberto, dados públicos ou um valor mínimo
de desempenho. A falta desses itens entra na avaliação de qualidade.

Incluir em **apoio técnico/contextual**, com essa classificação, fontes primárias
de modelos, convenções, corpus e edição. Revisões secundárias podem orientar
termos e rastreamento, mas não contam como estudos primários na síntese empírica.

| Código | Motivo e tratamento |
| --- | --- |
| D01 | Mesmo trabalho/versão duplicada: vincular ao registro canônico, preservar todas as origens e contar separadamente da exclusão por conteúdo |
| E01 | Fora do escopo: sem relação justificável com reconhecimento histórico, referência, avaliação textual ou componentes efetivos |
| E02 | Material secundário, publicidade ou opinião sem estudo primário: retirar da síntese empírica; manter como apoio quando pertinente |
| E03 | Texto integral não obtido após as tentativas documentadas: excluir da síntese empírica por indisponibilidade, sem presumir baixa qualidade |
| E04 | Método, dados ou evidência insuficientes para responder às PB após leitura: registrar o elemento ausente e a página/seção examinada |
| E05 | Fora do período: registrar data e eventual exceção fundacional prevista abaixo |
| E06 | Idioma fora de português/inglês/espanhol sem leitura verificável pelo grupo: registrar limitação e possibilidade de tradução futura |

OCR de impressos pode entrar como fonte técnica do modelo ou estudo de avaliação
textual pertinente. Seu desempenho não deve ser transportado para manuscritos.
Não excluir todo OCR impresso pelo título nem usá-lo como evidência direta de HTR.

Na dúvida por título/resumo, manter para leitura integral. Registrar um motivo
principal por exclusão de conteúdo, seguindo E01–E06 quando houver vários, e
anotar os demais sem duplicar a contagem. Retratação ou correção conhecida deve
ser registrada e avaliada; não citar um resultado invalidado como evidência válida.

## 6. Seleção, duplicatas e rastreamento

1. Registrar base, consulta aceita, filtros, data/hora, responsável e estado da
   execução. Salvar exportação e evidência de busca permitidas pela interface.
2. Atribuir IDs estáveis; deduplicar por DOI, arXiv e, depois, título/autores/ano,
   com conferência manual. Conservar vínculo entre todas as ocorrências.
3. Agrupar preprint, relatório e artigo do mesmo estudo. Preferir a versão
   publicada mais completa disponível até o corte; manter diferenças relevantes,
   identificadores e versões. Não contar o mesmo experimento como estudos distintos.
4. Triar título/resumo, depois ler o texto integral. Registrar responsável,
   decisão e motivo; metadados/resumo consultados não equivalem à leitura integral.
5. Fazer **uma rodada** de referências e citações dos estudos incluídos.
   Para citações no Scholar, examinar até as primeiras 100 posições por estudo,
   com o mesmo corte temporal e registro de truncamento. Examinar todas as
   referências listadas acessíveis. Novos incluídos dessa rodada não geram
   outra rodada automática.
6. Textos anteriores a 2000 podem entrar por essa rodada se forem fundacionais
   para uma PB. Registrar origem, justificativa e data como exceção, sem alterar
   o período das buscas principais.
7. Submeter inclusões, exclusões por leitura integral e agrupamentos duvidosos
   à conferência de outro integrante identificado. Resolver divergências com
   justificativa; se houver somente um leitor, declarar a limitação e a falta
   de conferência, sem inventar dupla revisão ou concordância.

As [fontes já consultadas](entregas/pi_iv_pln_20261020/fontes_consultadas.json)
entram por uma origem separada, **conhecidas antes do protocolo**. Passam pelos
mesmos critérios; não são resultados das novas buscas por retroatribuição.
O escopo real da leitura anterior permanece válido, inclusive consultas apenas
a resumo ou seções. Não há número mínimo artificial de estudos a incluir.

## 7. Extração, qualidade e síntese

Usar o [registro de triagem e fichamento](bibliografia/triagem_e_fichamento.md).
Extrair referência/DOI/versão, tipo de fonte e revisão por pares, PB atendidas,
páginas lidas, corpus/idioma/escribas/documentos, modelo/checkpoint, adaptação,
pré-processamento, recortes/segmentação, referência/revisores, normalização,
separação por documento, métricas/denominadores/agregação, falhas/exclusões,
resultados nas condições do estudo e limitações para o piloto.

Avaliar, com evidência de página/seção, se cada estudo informa: dados e tamanho;
identidade dos modelos; preparação das entradas; origem e incertezas dos alvos;
protocolo de métricas; independência entre desenvolvimento e teste; falhas e
exclusões; disponibilidade para reprodução; e limites das conclusões.
Usar **informado, parcialmente informado, não informado ou não aplicável**,
sem nota numérica ou exclusão automática criada depois de conhecer resultados.

Fazer síntese narrativa por PB e tabela de condições/limitações. Separar
estudos empíricos, fontes técnicas e contexto documental; também separar
preprints de publicações com revisão por pares. Não combinar taxas de corpora,
normalizações, unidades ou configurações diferentes em um ranking comum ou
média de desempenho. Ausência de relato não significa ausência do procedimento.
Ausência de achado nesta cobertura não prova inexistência na literatura.

Relacionar os achados ao diagnóstico local como interpretação, mantendo as
oito ressalvas, a referência assistida e a identificação **diagnóstico de
desenvolvimento**. Não alterar alvos, normalização ou conclusões empíricas
congeladas para aproximá-los de outro estudo. Qualquer experimento novo exigiria
protocolo próprio e está fora desta atualização.

## 8. Registros e condição de conclusão

O [registro de buscas](bibliografia/registro_buscas.md) começa sem execuções,
totais ou seleção preenchidos. Campo desconhecido é **não apurado**, nunca zero.
Só registrar zero depois de executar a operação correspondente. Distinguir
total informado pela interface, recuperados, duplicatas, triados, textos
solicitados/obtidos, excluídos e incluídos. Guardar contagens por consulta e
união deduplicada; não somar resultados sobrepostos como estudos únicos.

Para declarar a revisão concluída, devem existir: execução ou indisponibilidade
justificada de cada consulta/base, exportações/registros identificáveis, triagem
e leitura documentadas, fichamentos, contagens reconciliadas por origem/etapa,
síntese por PB e relato das limitações. Não preencher fluxograma com estimativas.
Registrar separadamente a revisão dos autores e eventual aprovação docente.

Alterações futuras de consultas, corte, bases, idiomas, critérios ou limites
devem gerar emenda datada no registro, com motivo e impacto nas buscas já feitas.
Se houver necessidade de repetir uma busca, manter a anterior e sua relação
com a nova. Não reescrever os registros para simular decisões prévias.

## 9. Histórico e consulta operacional

O [protocolo anterior de segmentação/TrOCR](bibliografia/protocolo_anterior_20261021.md)
foi preservado literalmente antes desta atualização. SHA-256:
`9a8725deb73c250b3953db89ad66c9d28a772f3845279cff54e1d947f3b9d014`.
As consultas antigas e fontes técnicas continuam históricas; não foram executadas
como parte desta revisão. Notebook, artigo, referências assistidas, saídas brutas
e pacotes com inventários permanecem intactos.

Em 21/10/2026 foram consultadas apenas orientações operacionais para elaborar
este protocolo, sem executar B01–B08/G01–G08 nem selecionar estudos:

- [Guia oficial da ACM Digital Library](https://libraries.acm.org/binaries/content/assets/libraries/new_acm-digital-library-user-guide.pdf): campos, coleções e operadores; a interface concreta deve ser registrada na execução.
- [Mecanismo de busca do IEEE Xplore](https://ieeexplore.ieee.org/Xplorehelp/searching-ieee-xplore/search-engine): modos, campos e operadores.
- [Ajuda oficial do Google Scholar](https://scholar.google.com/intl/en/scholar/help.html): ordenação, busca avançada, versões e exportação; a coleta complementar será manual, sem raspagem em massa.

A sintaxe operacional do arXiv ainda precisa ser validada na interface ao
registrar a primeira execução. Estas consultas de documentação não são estudos
incluídos, revisão sistemática realizada ou aprovação dos professores.
