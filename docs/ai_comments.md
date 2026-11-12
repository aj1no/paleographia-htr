# Uso de ferramentas de IA — revisão dos autores pendente

Atualização: 23/10/2026. Codex auxiliou a refatoração Python, CLI, API/editor,
validação, adaptadores, testes, documentação e inspeção de imagens/PDFs.
Também apoiou a organização da referência assistida, experimentos, notebook,
figuras e primeiro rascunho do artigo. Os registros datados identificam as
operações executadas; a responsabilidade pela revisão final é dos autores.

As etapas de 23/10 incluem expansão/inventário do corpus, ensaio técnico de
ajuste fino, fichamentos de T1/T4, revisão e diagramação do artigo, notebook
colaborativo, preparação para Colab e fechamento acadêmico. Os relatos dos
colegas não foram preenchidos pela IA. Execução automática não autentica
participação nem confirma leitura paleográfica.

O documento de fechamento encaminhado pelo solicitante e autorizado em 23/10
informa uso de **Antigravity no desenvolvimento inicial**. A anotação histórica
em `legacy/auxiliares_20261020/server/Texto importantes.txt` menciona Antigravity,
mas não individualiza quais arquivos foram gerados. Versão, modelo, prompts,
datas da atividade e alterações específicas ainda não foram recuperados.
Uma síntese não deve ser apresentada como prompt literal. A anotação
“Antigravity Kit” não comprova que esse Kit seja um produto do Google; caminhos
privados dessa anotação não são reproduzidos no material de apresentação.

A [apresentação institucional do Google Antigravity Team, de 20/11/2025](https://developers.googleblog.com/en/build-with-google-antigravity-our-new-agentic-development-platform/)
foi consultada em 23/10/2026 e identifica a ferramenta. Ela não comprova usos
ou autoria de arquivos neste projeto. A nova declaração do [artigo atual](entregas/pi_iv_pln_20261023_fechamento/artigo.md#comentários)
mantém esse limite; declarações dos pacotes congelados permanecem intactas.

A planilha `PaleographIA_Documentacao_Uso_IA.xlsx` não foi localizada no projeto
nem nas pastas de Downloads consultadas. A estrutura, os 15 registros anteriores
e as seis entradas pendentes descritas no documento recebido **não foram
conferidos no arquivo**. É preciso disponibilizar a planilha original antes
de atualizá-la. Não foi criada substituta, não foram confirmados usos dos colegas
e não foi acrescentada a interação administrativa cuja exclusão foi solicitada.

O editor experimental do Traslado usa **PP-OCRv6 medium/Kraken**. A comparação
publicada usa **latin PP-OCRv5 mobile/ONNX e PP-OCRv6 medium/Kraken**. TrOCR foi
usado anteriormente e está bloqueado para novas execuções. Suas predições
históricas estão arquivadas, sem serem apresentadas como saídas atuais.

O [diagnóstico de 24 linhas](experimentos/traslado_269r_reconhecedores_24_20261020/README.md)
utiliza referência assistida pela edição e preserva oito ressalvas. Decisões
humanas têm autoria e histórico; apoio editorial não equivale a certeza visual.
Testes sintéticos são identificados e não contam como resultados acadêmicos.

A declaração da [entrega acadêmica](entregas/pi_iv_pln_20261020/adequacao_academica.md)
deve ser revisada conforme a rubrica. Não foram presumidas ferramentas usadas
anteriormente, coautorias, aprovações ou revisão sistemática concluída. Créditos,
fontes, texto e interpretações precisam da conferência final do grupo.

## Atualização de 09/11/2026: Claude Code

De 05/11 a 09/11, o Claude Code (Claude Opus 5.5, Anthropic) apoiou, a pedido de Rodolfo Takemoto:
o pipeline de ajuste fino do PP-OCRv6 e os treinos gravados, a análise linguística dos erros e a
pós-correção (Notebook 3), o reconhecedor treinado do zero, a aplicação web (modo leitura, aba Textos,
conferência às cegas, PAGE XML, tema noturno), a curadoria às cegas e o congelamento do teste
reservado, a avaliação final única, o notebook comparativo, a redação e a revisão do artigo de PLN e
deste README. Os prompts e os resultados estão na planilha de documentação do uso de IA da equipe.

Os commits desse período foram feitos pelo Claude Code em nome do autor e, a pedido do autor, as mensagens
não trazem a linha de coautoria; o uso de IA fica declarado aqui, na planilha e nos comentários dos
notebooks e do artigo. Nenhuma ferramenta de IA validou leituras: as transcrições de referência da
validação e do teste foram feitas por integrantes da equipe.

## Atualização de 12/11/2026: Claude Code, de 10 a 12/11

De 10 a 12/11, o Claude Code (Claude Opus 5.5 e, a partir do fim da manhã de 12/11, Claude Fable 5.2, Anthropic)
apoiou, a pedido de Rodolfo Takemoto:

- **Leitura modernizada:** as palavras a conferir (sublinhadas), o glossário histórico com notas
  numeradas e a versão 3 das regras, avaliada contra a edição do Arquivo nas Posturas de 1831.
- **Treinos C, D1 e D2:** a preparação dos pares, a fila de treinos, a recuperação do checkpoint do D1
  depois que o Windows reiniciou o computador, as avaliações na validação e a avaliação única do D1 no
  teste reservado, autorizada pelo autor. A decisão de trocar o modelo da aplicação foi do autor.
- **Documentação:** os registros dos treinos, a página [Os treinos, época por época](treinos/README.md),
  o resumo e roteiro da apresentação, a atualização do artigo de PLN com o D1 e o rascunho do e-mail de
  retorno ao Arquivo Histórico, que o autor revisou e enviou.
- **Organização do repositório para a entrega** (12/11): correção do clone no Windows, `CITATION.cff`,
  retirada de arquivos pessoais e do pacote do Arquivo, com reescrita do histórico decidida pelo autor
  ([registro](manutencao/organizacao_entrega_20261112/README.md)), e preparação do Release v1.0.0,
  que o autor publicou.
- **Demonstração:** o fólio pré-processado e os atalhos para abrir a aplicação na apresentação.

Como antes, as leituras e validações das linhas das Posturas de 1831 foram feitas pela equipe na
aplicação; a IA apontou possíveis erros de digitação e divergências com a edição, e a decisão de
corrigir ou manter foi dos revisores. Os commits continuam sem a linha de coautoria, a pedido do autor.
Os prompts e os resultados desse período devem entrar na planilha de documentação do uso de IA da equipe.
