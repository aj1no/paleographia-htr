# Estado do projeto para revisão

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

CER/WER não foram calculados; não houve ajuste fino. Há uma única sessão
documental candidata, insuficiente para criar grupos independentes apenas
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
