# PP-OCRv5 × PP-OCRv6 — 24 linhas do 269r

**Diagnóstico de desenvolvimento, com referência assistida pela edição publicada.**
Data: 20/10/2026. Revisor: Rodolfo Vinícius Cima Takemoto.
Foram reconhecidos os mesmos 24 recortes do corpo, em ordem, com os dois
componentes existentes, sem detector, pós-correção, treino ou alteração do editor.

## Resultado principal

| Reconhecedor | CER | Erros / caracteres | WER | Erros / palavras | Falhas |
| --- | ---: | ---: | ---: | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 650 / 1112 | 94,58% | 192 / 203 | 0 / 24 |
| PP-OCRv6 medium / Kraken | 15,11% | 168 / 1112 | 60,10% | 122 / 203 | 0 / 24 |

O PP-OCRv6 apresenta menos divergências neste diagnóstico. A diferença é de
**43,35 pontos percentuais em CER** e **34,48 em WER**. O resultado não demonstra
generalização para outros documentos e não equivale a uma porcentagem simples
de acertos: inserções também entram no numerador dos erros.

Os denominadores são 1.112 caracteres e 203 palavras. As contagens são somadas
por **cinco blocos completos** antes da divisão, sem média de taxas por linha.
Há espaços entre linhas dentro de cada bloco; os quatro limites entre blocos
não acrescentam caracteres ao denominador. NFC e colapso de espaços são aplicados
igualmente aos alvos e saídas, preservando caixa, acentos e grafia histórica.

| Reconhecedor | Caracteres: substituições | Deleções | Inserções | Palavras: substituições | Deleções | Inserções |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PP-OCRv5 | 200 | 444 | 6 | 108 | 84 | 0 |
| PP-OCRv6 | 96 | 54 | 18 | 95 | 22 | 5 |

## Principais divergências

**PP-OCRv5:** predomina a perda de conteúdo: 444 deleções de caracteres e 84
deleções de palavras no alinhamento principal. As leituras se afastam fortemente
do conteúdo das linhas. Exemplo da linha 22:

- **Alvo assistido:** `por titullos de Sismaria as Lavrão outros que mais`
- **Saída bruta PP-OCRv5:** `tiay cm es uhy g`

**PP-OCRv6:** conserva muito mais conteúdo, mas ainda apresenta:

- Junção de palavras: `Anno do` → `Annodo`; `mui dis` → `muidis`.
- Separação indevida: `Cabedo` → `Cabe do`; `onde` → `on de`.
- Troca ou perda de letras: `Jundiahy` → `Sundiahy`; `titullos` → `titllos`;
  `Sismaria` → `Sismario`.
- Acentos e pontuação: `Capitão` → `Capitao.`. Em várias saídas o til combina
  com o `o`, formando `aõ` em lugar de `ão`; NFC não corrige a posição do acento.
- Caixa: `Paulo` → `PauLo`. Caixa e diacríticos são significativos no protocolo.

O WER continua elevado porque uma pequena diferença, ou uma junção/separação,
afeta a correspondência de palavras inteiras. Isso não é segmentação de linhas:
os dois modelos receberam os mesmos recortes humanos.

As divergências `ministros`/`menistros`, `orgente`/`ergente`, a leitura de
`Justissa` e os sinais finais **coincidem com ressalvas da referência**. São
contabilizadas contra o alvo adotado, mas não provam por si só a leitura exata
do manuscrito. Na linha 24, o alvo conserva `Magᵈᵉ`; o PP-OCRv6 retorna `Magi`.
Parte dessa divergência envolve a convenção de representação da abreviatura.

## Exemplos completos

| Linha | Alvo assistido | PP-OCRv5 bruto | PP-OCRv6 bruto |
| --- | --- | --- | --- |
| 1 | Anno do Nacimento de Nosso Senhor Jezus christo | Amodo Nacei momo de Nofo enen Ieucerike | Annodo Nacimento de Noso Senhor Iezuschritto |
| 6 | ante nomeado fui Em Companhia do Capitão | ante nomuiemlompanio  opitio | ante nomeado fui Em Companhia do Capitao. |
| 14 | Senhora do DesTerro de Jundiahy onde Eram | eado Gira Deelmdeay on de leram | senhora dlo des Terro de Sundiaho on de Eeram |
| 22 | por titullos de Sismaria as Lavrão outros que mais | tiay cm es uhy g | por titllos de Sismario os Lavraõ outros quemas |
| 23 | posses tem por falta de Justissa pello que | y fim pn aeo let yuomy | pose som po falso de datia pl oqem |
| 24 | lhes Requerião da parte de Deos e de Sua Magᵈᵉ | e beem de e  | lhis Requriaõ daporte ou deos e de Sua Magi |

As linhas 23 e 24 têm ressalvas preservadas; os exemplos não são novas
confirmações paleográficas. O quadro completo das 24 linhas está em
[linhas_comparadas.md](linhas_comparadas.md).

## Resultados por bloco

| Linhas | PP-OCRv5 CER | PP-OCRv5 WER | PP-OCRv6 CER | PP-OCRv6 WER |
| --- | ---: | ---: | ---: | ---: |
| 1–5 | 57,02% | 95,56% | 12,40% | 51,11% |
| 6–10 | 52,81% | 95,12% | 14,72% | 58,54% |
| 11–15 | 56,00% | 97,50% | 15,11% | 70,00% |
| 16–20 | 57,83% | 93,02% | 13,04% | 51,16% |
| 21–24 | 71,20% | 91,18% | 21,74% | 73,53% |

O bloco 21–24 é o de maior CER nos dois modelos. Os diagnósticos por linha
identificam a 23 como a de maior CER do PP-OCRv6 (40,48%); no PP-OCRv5, a 22
(82,00%). Essas taxas por linha não são a métrica principal.

## Referência e limites

Os alvos foram congelados **antes das novas inferências**, a partir da
[referência publicada](../../revisao_humana/traslado_269r/referencia_assistida_20261020/README.md).
O usuário autorizou explicitamente a avaliação assistida usando a edição nas
dúvidas. Não houve alteração retroativa dos alvos após observar os resultados.

- Mantidas todas as 24 linhas e as oito ressalvas das linhas 11, 15, 16, 17, 19,
  20, 23 e 24; nenhuma linha difícil foi excluída.
- Mantidos `Eram`, `Com` e `Como`, confirmados na conferência, e `que mais`
  separado conforme a edição. `Magestade` permanece desenvolvimento editorial,
  separado do alvo abreviado `Magᵈᵉ`.
- O conjunto é explicitamente **assistido pela edição**, com `texto_alvo`,
  `estado_visual_original` e `duvidas_preservadas`. Não há promoção artificial
  das oito linhas a `human_diplomatic` validado. O catálogo humano original
  continua com 16 validadas e oito pendentes.
- Os modelos recebem apenas as imagens. O manifesto de reconhecimento tem
  texto humano nulo e tipo de referência `unknown`; o conteúdo dos alvos não
  é fornecido aos reconhecedores.
- Foram usadas as funções existentes `counts` e `aggregate` para este protocolo
  assistido. O validador e o avaliador estrito de referência humana não foram
  modificados nem apresentados como aprovados para as 24 linhas.
- O fólio foi usado no desenvolvimento e em consultas lexicais anteriores.
  Este diagnóstico não é teste reservado. Reservar outros documentos para
  avaliação antes de usá-los em escolhas de configuração.
- A meta de 30–50 linhas ainda não foi atingida; ela não garante representatividade.
  O enquadramento específico de PI IV e a adequação do desenho à rubrica de
  PLN continuam dependentes do alinhamento acadêmico.
- Compararam-se variantes e implementações distintas, cada uma com seu
  pré-processamento nativo documentado. Não atribuir a diferença apenas ao
  número da versão, nem presumir economia de trabalho humano a partir de CER.

## Execução e reprodução

Foram feitas duas novas execuções sequenciais, com 24 recortes cada, sem falhas.
Os pesos e a imagem Docker foram conferidos por SHA-256; CPU/float32 em ambos.
O PP-OCRv5 usa ONNX Runtime com uma thread; o PP-OCRv6 usa o worker Kraken em
Docker limitado a duas CPUs. Os tempos e carregamentos estão nas proveniências;
uma única execução nessas condições não sustenta conclusão de velocidade.

- Pesos PP-OCRv5: `b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a`.
- Pesos PP-OCRv6: `15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9`.
- Fonte do código: commit `4c25b4f6a1dba2536fc5e055b11137d076ef61a5`; o estado local
  e os hashes dos componentes estão registrados nas proveniências.

Para auditar os resultados sem carregar modelos, na raiz do projeto:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/verificar.py
```

O verificador recalcula as métricas e compara o total de operações também com
uma implementação independente de Levenshtein. Confere os pixels, os IDs, a
ordem, o congelamento dos alvos e a preservação das ressalvas. Os pesos não são
necessários para a auditoria offline.

A auditoria também passou em uma cópia sem pesos nem workspace. Três casos
negativos foram rejeitados nessa cópia: alteração do alvo, alteração da saída
bruta e promoção indevida de uma ressalva a validação visual, mesmo refazendo
os hashes locais pertinentes. O recibo está em
[auditoria_copia.json](auditoria_copia.json). Nenhum original foi alterado nesses testes.

Para repetir a inferência, escolha **outra pasta**, preservando esta execução:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/reproduzir.py preparar --output-root output/repeticao_269r24
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/reproduzir.py ppocrv5 --output-root output/repeticao_269r24
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/reproduzir.py ppocrv6 --output-root output/repeticao_269r24
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/reproduzir.py avaliar --output-root output/repeticao_269r24
```

A repetição exige os pesos locais e a imagem Docker indicados. Os comandos não
baixam novos modelos, não alteram o editor e recusam sobrescrever execuções.

## Arquivos para análise

- [protocolo.json](protocolo.json) e [entradas_congeladas.json](entradas_congeladas.json):
  decisões, autorização, hashes e condições fixadas antes do reconhecimento.
- [alvos_assistidos.jsonl](alvos_assistidos.jsonl): as 24 linhas, autoria e ressalvas.
- [comparacao.json](comparacao.json): microcontagens e métricas principais.
- [regioes.jsonl](regioes.jsonl): composição e contagens dos cinco blocos.
- [por_linha.csv](por_linha.csv) e [por_linha.jsonl](por_linha.jsonl): diagnóstico completo.
- [erros_palavras.jsonl](erros_palavras.jsonl) e [erros_caracteres.jsonl](erros_caracteres.jsonl):
  alinhamentos por linha, sem atribuir automaticamente certeza às leituras duvidosas.
- [PP-OCRv5 bruto](ppocrv5/predictions.jsonl) e [PP-OCRv6 bruto](ppocrv6/predictions.jsonl):
  saídas imutáveis, tokens, identidades e pré-processamento.
- [preservacao_depois.json](preservacao_depois.json): 74 arquivos anteriores do
  workspace conferidos sem alteração, incluindo ponteiro e histórico.
- [inventario.json](inventario.json): SHA-256 dos arquivos deste experimento.

Os recortes e a edição são reutilizados dos pacotes publicados, sem duplicar nem
alterar seus bytes. O editor mantém PP-OCRv6 e os estados humanos anteriores.
Nenhuma função do produto foi adicionada. Este pacote é destinado à branch
`codex/refatoracao-piloto`, com histórico aditivo, saídas brutas e oito ressalvas
preservadas. Os resultados são diagnóstico de desenvolvimento com referência
assistida pela edição, sem teste reservado ou alegação de generalização.
