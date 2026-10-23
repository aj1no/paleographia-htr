# Política de transcrição — proposta v1, a confirmar pelos revisores

Esta proposta deve ser fixada antes da revisão do piloto e registrada nas execuções. O responsável humano decide leituras; ferramentas não promovem texto inferido a referência validada.

1. **Predição bruta**: manter a saída original com tokens, modelo, revisão, precisão, geração, tempo e status. Uma correção não substitui essa saída.
2. **Referência paleográfica**: conferir no manuscrito; preservar grafia histórica, caixa, acentos e pontuação visíveis. Não modernizar nomes ou inserir pontuação inferida. Preservar abreviaturas como escritas; registrar expansões apenas na edição modernizada ou em nota de revisão. Sinais e abreviaturas sem representação Unicode inequívoca exigem convenção humana registrada antes de validar.
3. **Edição modernizada**: campo separado, com fonte e páginas contadas a partir de 1. Pode conter desenvolvimentos e inferências do editor; não é automaticamente referência diplomática.

Cada anotação corresponde à linha física, com ordem explícita dentro da região. Hífen ao final de linha permanece quando visível; não unir palavras através da quebra por padrão. Nas métricas de região, as linhas são concatenadas por espaço, sem modernização ou junção de hifenização. Colchetes editoriais devem ter seu significado registrado em notas de origem; não removê-los automaticamente.

Leitura incerta, dano ou cobertura parcial: manter pendente ou marcar `exclusion_reason`, antes de observar as predições do experimento. Não completar lacunas com palavras plausíveis. Trechos excluídos devem ficar em regiões separadas, com contagem de exclusões; uma região declarada completa não pode esconder linhas ausentes. Para o estudo principal, selecionar regiões cuja referência integral seja conhecida.

Cabeçalhos, créditos e números editoriais devem ser separados por **trechos identificados na fonte** e preservados na extração integral. Não há filtro por tamanho de palavra nem regra que elimine datas/valores. `extract-reference` guarda páginas completas como material de apoio e não cria alvos.

Estados: `pending_review`, `validated`, `rejected`. Validar texto exige `text_diplomatic`, `reference_kind=human_diplomatic`, revisor identificado e instante com fuso. Geometria tem estado próprio. Correspondência de página e cobertura de região também precisam de conferência. A interface oferece rascunho e confirmação explícita; simples edição não inclui automaticamente no experimento.

Normalização de avaliação: Unicode NFC e redução de espaços, igualmente na referência e hipótese. Caixa, acentos, grafia, números e sinais permanecem. Não aplicar stopwords, lowercase, stemming ou lematização. CER/WER são taxas de edição por contagens e podem exceder 100%; não são convertidas em “acurácia”.

## Fundamentação e adaptações documentadas — 23/10/2026

A [seleção bibliográfica comentada](bibliografia/referencias_comentadas_20261023.md#p5--normas-de-transcrição-referência-para-decisões-explícitas)
compara as normas de transcrição do Arquivo Nacional com esta política, item a
item. P2/P4/P6 contextualizam modalidades editoriais e corpus histórico; T5
orienta a documentação do dataset. Essas relações são aplicações metodológicas
do projeto, sem atribuir aos autores decisões específicas que não formularam.
O adendo explicita a fundamentação das regras existentes; não é confirmação
humana de texto, geometria, cobertura ou correspondência.
