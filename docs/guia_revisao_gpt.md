# Estado do projeto para revisão

**Atualização mais recente — PP-OCRv6:** o [novo reconhecedor e sua integração](experimentos/traslado_269r_ppocrv6_20261016/README.md)
foram executados nas mesmas cinco linhas: CER **30/242 = 12,40%**, WER
**23/45 = 51,11%**, sem falhas. A proposta recupera as frases, com erros de
letras, espaços e grafia; foi liberada experimentalmente no editor do Traslado,
sem alterar a referência humana. TrOCR está bloqueado nos fluxos de execução;
o histórico continua auditável. O runtime Linux/CPU usa Docker/WSL2 e preserva
o ambiente da aplicação. Essa amostra permanece desenvolvimento, sem treino
ou teste reservado. As notas abaixo registram etapas anteriores.

**Estado mais recente — 16/10/2026:** o usuário concluiu a conferência das cinco
linhas do corpo do Traslado 269r, com texto, geometria, correspondência de página
e cobertura completa somente do bloco. A [entrega experimental](experimentos/traslado_269r_20261016/README.md)
publica essa referência, confirmações, snapshot, configuração, saídas, métricas
e hashes das duas execuções. TrOCR: CER/WER 80,58%/100%; PP-OCRv5 latino:
57,02%/95,56%. Ainda não há leitura automática aproveitável, treino ou teste
reservado. As cinco linhas são desenvolvimento; o catálogo de 1831 permanece
pendente. Os parágrafos seguintes registram etapas anteriores da preparação.

Preparação do Traslado concluída em 16/10/2026: cinco linhas candidatas do
269r podem ser abertas em workspace próprio no editor, com apoio publicado
de somente leitura e texto humano vazio. As confirmações parciais foram
preservadas. O [bloco concreto para revisão](revisao_humana/traslado_269r/conferencia_bloco.md)
e a [entrega com verificações](revisao_humana/traslado_269r/entrega.md) descrevem
os comandos e limites. Foram executados 53 testes Python e 18 testes de DOM;
nenhuma linha completa foi validada. A integridade dos oito blobs legados foi
registrada separadamente de seus identificadores CRLF, e os novos snapshots
têm contrato determinístico UTF-8/LF.

Atualização de 16/10/2026: foi inventariada a pasta de transcrições indicada
pelo usuário; os 15 arquivos correspondem por hash à importação existente.
O [levantamento do acervo](mineracao_acervo_jundiai.md) registra vínculos e
proposta de mineração. A [revisão do Traslado, fólio 269 reto](revisao_humana/traslado_269r/comparacao.md)
reúne 24 linhas candidatas da edição, imagens publicadas e confirmações
parciais de leitura. `Dias` e `da dita Hera nesta povoação` foram confirmados;
a dificuldade anterior com `Hera` foi resolvida ao consultar a página inteira.
O caderno mantém o histórico e as pendências de sinais, geometria e cobertura.
Nenhuma linha completa foi validada ou incorporada ao catálogo experimental.

Preparação humana iniciada em 15/10/2026: cinco linhas consecutivas, 17–21 do
100 reto, com recortes ampliados e identificação do revisor. «Leu se» recebeu
confirmação parcial; a abreviatura final permanece aberta, com sinais superiores
aparentemente «es» segundo o revisor. Nenhuma linha completa foi validada.
O [caderno da sessão e ponto de retomada](revisao_humana/100r_17_21/conferencia.md)
separa decisões atuais, hipóteses e histórico; as seis confirmações anteriores
do repertório foram preservadas em seu catálogo original.

Atualização de 15/10/2026, após a revisão de `756492c`: foram corrigidas a
validação global da partição, a preservação das múltiplas regiões e a perda de
rascunhos. Consulte [correcoes_pos_revisao.md](correcoes_pos_revisao.md) para
implementação, 46 testes Python, 16 testes em DOM simulado e conferência em
navegador real com dados sintéticos. Os números de HTR abaixo são históricos;
esta atualização não acrescenta reconhecimento real nem referências humanas.

Esta entrega organiza o piloto que estava distribuído em scripts e acrescenta
uma revisão local com proveniência, histórico e um repertório paleográfico.
O objetivo da análise é verificar se esse caminho sustenta transcrições
conferíveis e uma futura comparação experimental, sem confundir funcionamento
do programa com qualidade de reconhecimento.

## O que existe

- Pacote em `src/paleographia`: dados, segmentação, reconhecimento, revisão,
  avaliação, experimentos, preparação de treino e API.
- Interface de revisão em `/` e repertório ampliável em `/repertorio`.
- Três fólios candidatos, 94 recortes e zero linhas integralmente validadas.
- Repertório com 13 exemplos nas linhas editoriais 17–19 e 23 do 100r, apoiados
  pela página 3 de uma edição **modernizada**. A edição não cobre as cinco
  primeiras linhas físicas que começamos a ler.
- Seis confirmações parciais recebidas do usuário: a sequência a–r–t em dois
  exemplos de “Artigo”; as leituras de “projecto”, “posturas”, “ofensivas” e
  “defensivas”. O usuário identificou **somente um f** em “ofensivas”, corrigindo
  a hipótese inicial. “Hum” continua provável. Caixa, sinais e linhas completas
  não foram formalmente validados.
- Histórico do repertório em `data/manifests/repertorio_revisions/`, separado das
  revisões de linhas. Nenhum nome de revisor foi inventado.

## Resultados e limites efetivos

O modelo TrOCR atual foi executado em três recortes de diagnóstico e nos 32
recortes do 100r. Não houve falhas de processamento, mas as leituras foram
inadequadas. A comparação qualitativa com três linhas já editadas também
falhou. O registro técnico correspondente está em
`docs/diagnostico_reconhecimento.json`, com as saídas brutas preservadas.

A apresentação em português oculta a sugestão inadequada e informa sua
indisponibilidade. **Não é detecção de idioma, tradução, melhoria dos pesos ou
prova de leitura correta.** A liberação de sugestões continua desligada em
`configs/pilot.toml` até uma avaliação apropriada do reconhecedor.

CER/WER não foram calculados; não houve ajuste fino. O catálogo experimental
de 1831 contém uma única sessão, insuficiente para criar grupos independentes apenas
separando seus fólios. Kraken tem um adaptador, mas sua execução real permanece
pendente por ambiente/pesos, conforme `environment.md`.

## Pontos para a análise

1. A distinção entre edição modernizada, leitura assistida, confirmação parcial
   e referência paleográfica validada está clara no esquema e nas telas?
2. Fonte, hash, caixa, ordem e recorte permanecem associados corretamente? Os
   recortes reconstruídos preservam os pixels e as confirmações existentes?
3. O cálculo de erros por região conta linhas omitidas e espúrias? A separação
   por documento e derivação evita vazamento entre treino e avaliação?
4. O carregamento do reconhecedor é explícito, serializado e rastreável? As
   falhas e resultados inadequados continuam visíveis no diagnóstico?
5. As notas de comparação de letras correspondem aos recortes? Generalizações
   paleográficas não confirmadas devem ser identificadas como hipóteses.
6. A camada de apresentação em português deixa suficientemente claro que o
   reconhecedor ainda precisa ser adaptado ou substituído?
7. Quais problemas impedem uma revisão confiável agora e quais são melhorias
   posteriores? Para cada problema, indicar arquivo, trecho, efeito e evidência.

## Reprodução e evidência visual

Instalar o pacote e executar os testes conforme `README.pt-br.md`. O
`docs/runbook.md` explica a extração dos arquivos originais, a reconstrução dos
94 recortes e a reconstrução do repertório **sem reescrever seu catálogo**.
Pesos, ambientes, arquivos temporários e o workspace mutável não são versionados.

Uma cópia dos 13 recortes do repertório está em `docs/repertorio/`, junto de
um quadro de exemplos. São derivados da imagem fonte já preservada no arquivo
original do repositório; coordenadas e hashes estão no catálogo. Consulte
`repertorio_100r.md` para os limites das leituras e os créditos da edição.

## Base da entrega

A branch de trabalho parte de `master`, onde estavam os scripts e os arquivos
originais usados no piloto. `main` tem uma história separada e não contém o
mesmo conjunto de fontes. A revisão proposta usa `master` como base, sem
reescrever ou mesclar automaticamente as duas histórias.

O cliente legado continua como um ponteiro Git sem configuração recuperada de
submódulo. A interface integrada ao pacote é a parte implementada nesta entrega.
