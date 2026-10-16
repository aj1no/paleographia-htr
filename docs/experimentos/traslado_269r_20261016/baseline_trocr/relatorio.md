# Primeiro diagnóstico exploratório do bloco 269r

Referência conferida por **Rodolfo Vinicius Cima Takemoto**, conforme identificação
salva no editor. Cinco linhas com texto e geometria validados, correspondência
do fólio confirmada e cobertura completa somente da região `body_first5`.
As outras 19 linhas candidatas e o restante do fólio não foram validados por
consequência. Revisão de origem: `20261016T172615_7ca3ab1c`.

As correções explícitas das linhas 2 e 3 e a limpeza do motivo de exclusão foram
aplicadas com histórico preservado antes de congelar a referência. As confirmações
de página e cobertura foram registradas a partir das respostas do usuário.

## Resultado

| Medida | Resultado |
|---|---|
| Linhas processadas | 5, sem falhas |
| Erro por caracteres (CER) | 195 edições / 242 caracteres = **80,58%** |
| Erro por palavras (WER) | 45 edições / 45 palavras = **100%** |
| Truncamento sinalizado | 0 |

Taxas de erro: menor é melhor; não são apresentadas como acurácia. Avaliação
principal da região, com Unicode NFC e redução de espaços, preservando caixa,
acentos, grafia, sinais e quebras de palavras representadas nas linhas.

O TrOCR gerou frases em inglês sem correspondência útil ao texto aprovado.
Isso confirma a inadequação do checkpoint nesta pequena amostra; não estima
seu desempenho em todo o acervo. A referência humana não foi substituída
pelas predições.

## Leituras aprovadas e saídas brutas

| Linha | Referência humana | Predição bruta do TrOCR |
|---|---|---|
| 1 | Anno do Nacimento de Nosso Senhor Jezus christo | What is the most of a successful half of the federal research was in |
| 2 | de mil seis centos sincoenta e seis annos, aos ca | selects the self of elementary management . |
| 3 | torze Dias do mes de Dezembro da dita Hera nesta | is also a successful scientific health health to |
| 4 | povoação e Freguezia de Nossa senhora do Deste | was a successful field for the |
| 5 | rro de Jundiahy, aonde Eu Publico Tabelião ao di | What is the first man made the first relationship was |

## Condições e limites

Checkpoint local `microsoft/trocr-small-handwritten`, snapshot
`b4648cfa171985a6745f37ddd637e98c0da958ac`; CPU/float32; máximo de 128 tokens novos,
um beam, sem amostragem e penalidade de repetição 1.0. Não houve treinamento ou
download novo. As sugestões automáticas da interface permanecem desativadas.
O carregamento registrou chaves ausentes do pooler do encoder; o aviso e a
identificação/hash dos pesos estão preservados na execução.

A referência foi congelada antes das predições, com hashes das fontes, manifests
e configuração. Todos os recortes pertencem a um único grupo exploratório.
Os limites das caixas são os conferidos pelo usuário; não houve nova segmentação.
Correspondências geométricas perfeitas resultam de reutilizar as mesmas caixas
como controle e não demonstram qualidade de um detector.

`diagnostico.json` registra tempos, métricas e hashes. Os arquivos de predição,
proveniência, configuração e avaliação ficam nesta pasta. O catálogo exportado e
as confirmações ficam em `data/processed/traslado_269r_revisoes/20261016T172615_7ca3ab1c/`.
Esta execução e a exportação são locais; não foram enviadas ao GitHub nesta etapa.
