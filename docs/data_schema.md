# Contrato canônico

`pages.jsonl` e `lines.jsonl` são UTF-8, um objeto JSON por linha. Os modelos `Page` e `Line` em `src/paleographia/data.py` são o esquema executável; tipos são estritos, campos adicionais de proveniência são preservados. Caminhos são relativos à raiz do projeto e usam `/`, incluindo espaços e acentos. Nunca interpretar um caminho de manifest relativo ao diretório do próprio manifest.

## Página

`page_id`, `document_id`, `folio_id`, `side` (`recto`, `verso`, `unknown`), `source_image`, `original_name`, `width`, `height`, `source_sha256`, `correspondence_status`, `reviewer`, `reviewed_at`, `source_url`, `credits`, `usage_conditions`, `transcribed_coverage`.

Inventário não infere documento, lado, data ou associação. `unassigned_*` é uma pendência de identificação, não um grupo científico. Cópias idênticas permanecem visíveis no inventário. Identifique reproduções não idênticas e derivados como pertencentes ao mesmo documento; hash de imagem sozinho não identifica reproduções em PDF.

Uma cobertura contém `region_id`, `bbox_xyxy`, `reference_source`, `reference_pages`, `review_status`, `complete`, `reviewer`, `reviewed_at`. Mesma página de PDF pode aparecer em múltiplas coberturas/fólios. `reference_candidates` guarda pistas sem validá-las. Não preencher caixas com coordenadas supostas para satisfazer o esquema.

## Linha

Edições paleográficas publicadas com intervenções editoriais podem usar
`reference_kind="unknown"`, mantendo `text_diplomatic` e `text_modernized`
nulos na preparação. O campo extra `published_reference` identifica a natureza
`published_paleographic_transcription`, texto publicado, fonte/hash/páginas,
proposta assistida e observações humanas parciais. O editor mostra esse apoio
em painel de somente leitura, sem copiá-lo ao campo humano. Salvar e exportar
preservam esses metadados. `planned_reviewer` identifica um responsável
previsto; não substitui `reviewer` ou `reviewed_at` de uma revisão efetiva.

IDs e vínculos: `line_id`, `page_id`, `document_id`, `folio_id`, `region_id`, `reading_order`. Imagem: `source_image`, `crop_image`, `bbox_xyxy`, `source_width`, `source_height`, `source_sha256`, `transform_id`. Texto: `text_diplomatic`, `text_modernized`, `reference_source`, `reference_pages`, `reference_kind`. Revisão: `review_status`, `geometry_status`, `reviewer`, `reviewed_at`, `exclusion_reason`. Protocolo: `split`, `split_group`, `derived_from`.

Caixas: pixels no original, canto superior esquerdo, `[x1,y1,x2,y2]`, limites finais exclusivos; `0 <= x1 < x2 <= width`, equivalente para y. Recortes são RGB da fonte, sem aplicar a binarização de detecção à entrada do reconhecedor. Coordenadas neurais poligonais/baselines são guardadas como metadados; a comparação atual usa a aproximação bbox declarada.

Pré-visualizações e recortes removem a orientação EXIF dos derivados para que o navegador mostre os mesmos pixels/coordenadas nativos que o segmentador. O arquivo original, com seus metadados, permanece intacto; não há rotação silenciosa das coordenadas.

`reading_order` começa em 0 no catálogo gerado e é única por página/região ativa. Não coincide necessariamente com numeração editorial. `line_id` automático deriva de página/região/ordem/geometria; no editor a identidade da anotação é mantida quando a caixa muda. Crop novo recebe caminho novo, e revisões anteriores preservam o anterior.

## Validação e persistência

Propósitos: catálogo aceita texto/caixa nulos em preparação, mas bloqueia caminhos inválidos, fontes alteradas, IDs repetidos e relações incoerentes. Avaliação exige texto e geometria humanos, crops existentes e correspondência revisada. Avaliação de região exige cobertura completa confirmada. Treino acrescenta três splits por grupos independentes. Falha da CLI retorna código 2; ausência de modelo é HTTP 503, upload inválido HTTP 400, edição inválida HTTP 422, conflito HTTP 409, ID ausente HTTP 404.

O editor usa snapshots JSON imutáveis em `data/workspace/revisions`, ponteiro atômico `current.json`, relação com revisão anterior e registros de predição append-only. Exportação produz os manifests e a revisão de origem. O ZIP de exportação contém metadados e texto; as imagens permanecem nos caminhos originais e devem ser preservadas juntamente com o projeto. Não é um pacote autossuficiente de imagens.
