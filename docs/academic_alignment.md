# Enquadramento acadêmico — pendente de confirmação

Produto: protótipo local de transcrição assistida de manuscritos delimitados de Jundiaí.

**Fechamento de 23/10/2026:** o [ponto de entrada atual](entregas/pi_iv_pln_20261023_fechamento/README.md)
liga o artigo ao notebook baseline já disponível no Colab, com recálculo de
predições congeladas, sem nova inferência ou treino. O link para “Link Notebook 1”
está preparado para o grupo 4, célula F11 da planilha consultada; nada foi inserido
ou submetido. Revisão dos autores, relatos individuais, planilha original de uso
de IA e enquadramento de PI IV continuam pendentes. As datas de presença relatadas
não foram convertidas em prazos de entrega. A rodada dos oito candidatos de 1795
está preparada, sem novas validações; o experimento científico segue bloqueado.

O [notebook executado e o primeiro rascunho do artigo](entregas/pi_iv_pln_20261020/README.md)
foram preparados com as 24 linhas e oito ressalvas preservadas, sem novas
inferências ou funções no sistema. A entrega inclui autoria informada, fontes
iniciais e afiliação à FATEC Jundiaí, curso de Ciência de Dados, 5º semestre,
Jundiaí – SP. Modelos e rubricas continuam pendentes.
A revisão bibliográfica inicial não substitui a revisão sistemática de PI IV.

**Participação da equipe — adição de 23/10/2026:** o [notebook colaborativo](entregas/pi_iv_pln_20261023_equipe/README.md)
retoma as responsabilidades previstas no primeiro artigo, com atividades por
integrante e registro de relatos. O solicitante informou discussão coletiva
e execução prática concentrada nele; tarefas previstas não foram convertidas
em realizações individuais. Os colegas podem documentar contribuições concretas
às discussões e às análises, com data, evidência e uso de IA. A demonstração
foi executada por Codex com quatro formulários vazios. O artigo e os notebooks
históricos permanecem preservados até a consolidação dos relatos pela equipe.

**Preparação editorial posterior de 23/10/2026:** o [artigo em PDF e Word](entregas/pi_iv_pln_20261023_entrega/README.md)
foi revisado integralmente e diagramado em três páginas, com referências,
abstract e seção Comentários identificando ferramenta de IA e utilização.
Os modelos PLN2026/PLN2025 e as duas cópias dos slides de PI IV foram
efetivamente consultados nesta etapa. A [nota de adequação](entregas/pi_iv_pln_20261023_entrega/revisao_e_adequacao.md)
localiza as orientações por documento/página e distingue requisitos verificados
dos relatados anteriormente. Essa consulta sucede as pendências documentais
históricas abaixo, sem afirmar aprovação docente, revisão sistemática concluída
ou submissão no Classroom.

**Atualização de 23/10/2026:** a [bibliografia comentada revista](bibliografia/referencias_comentadas_20261023.md)
integra paleografia, corpus, reconhecimento e documentação de dados, com
[fichamentos parciais e campos pendentes](bibliografia/fichamentos_parciais_20261023.md).
O [ensaio técnico de ajuste fino PP-OCRv6](dataset_expansion_20261023/README.md)
foi executado com dois passos de otimização e recarga do peso. É uma demonstração
técnica sobre desenvolvimento conhecido; avaliação científica, revisão
sistemática e adequação à rubrica continuam pendentes. Os pacotes acadêmicos
anteriores conservam os conteúdos e estados de sua data.

**Progresso posterior de 23/10/2026:** os [fichamentos integrais de T1/T4](bibliografia/leitura_t1_t4_20261023/README.md)
estão concluídos por IA e fundamentam uma [nova versão do artigo](entregas/pi_iv_pln_20261023_fundamentacao/README.md).
Resultados, referência assistida e oito ressalvas do diagnóstico permanecem.
A revisão dos autores, a inclusão final na revisão sistemática e as demais
exigências acadêmicas continuam pendentes.

**Atualização de 21/10/2026:** o [protocolo bibliográfico](literature_review.md)
define PB1–PB3, buscas por componentes e por avaliação de reconhecimento histórico,
critérios de seleção, extração e síntese para PP-OCRv5 × PP-OCRv6. A
[coleta B01/B02 no arXiv](bibliografia/arxiv_b01_b02_20261021/README.md) recuperou
cinco registros e seus históricos de versões, com um vínculo a fonte anterior.
As demais buscas, a triagem formal e os fichamentos continuam pendentes. O protocolo
anterior foi preservado; as oito ressalvas e o diagnóstico de desenvolvimento
continuam válidos, sem presumir confirmação docente ou revisão concluída.

O [diagnóstico assistido nos 24 recortes](experimentos/traslado_269r_reconhecedores_24_20261020/README.md)
foi executado em 20/10/2026: PP-OCRv5 × PP-OCRv6, com resultados e ressalvas
preservados. A execução demonstra a comparação técnica de dois reconhecedores;
não representa aprovação da rubrica pelos professores nem avaliação reservada.

**Atualização de 20/10/2026:** o usuário esclareceu: “PLN exige comparar dois
reconhecedores.” A proposta principal para PLN passa a ser **PP-OCRv5 latino ×
PP-OCRv6 medium**, usando os mesmos recortes humanos e os componentes já
existentes. O PP-OCRv5 local foi carregado em CPU e os hashes dos dois modelos
foram conferidos, sem nova inferência ou métrica. O editor continua PP-OCRv6.
A proposta e os pré-requisitos estão na
[minuta do experimento](revisao_humana/traslado_269r/referencia_assistida_20261020/proposta_experimento.md).

O plano anterior e suas RQ1–RQ3 em `evaluation_protocol.md` comparavam
**segmentação**, com reconhecedor fixo. Esse plano sozinho não atende ao
requisito agora esclarecido para PLN e fica secundário, sem iniciar outra frente.

A especificação recebida relata que PI IV menciona “primeiro modelo de classificação” e deep learning, mas também admite outros temas. **O professor ainda precisa confirmar o enquadramento segmentação/HTR**. Não foi criado classificador artificial para cumprir terminologia. Isso não impede catálogo, editor ou piloto.

PLN: o requisito de dois reconhecedores foi informado diretamente pelo usuário
em 20/10/2026. Artigo de até cinco páginas e apresentação continuam requisitos
relatados na especificação; a rubrica e a aceitação do desenho específico ainda
precisam ser confirmadas. O segundo reconhecedor já existe no projeto como
componente experimental ONNX; não houve novo motor ou ativação de TrOCR.

PI IV: preservar sua própria orientação de revisão sistemática, artigo/notebook e dados públicos. A dispensa relatada para PLN não elimina o requisito de PI. Os PDFs das disciplinas não estavam nas entradas do projeto; requisitos foram registrados como **informação da especificação**, não leitura direta desses slides nem aprovação obtida.

Entregas propostas para confirmação: ferramenta local; corpus delimitado com política/proveniência/revisão; comparação reproduzível; análise de erros e limitações; artigo e apresentação; registro de uso de IA. Melhorias e economia de tempo não são resultados presumidos.
