# Fólio 269 verso inteiro — comparação com a edição

**Diagnóstico de desenvolvimento, 22/10/2026.** PP-OCRv6 medium/Kraken com os mesmos
pesos, imagem Docker e parâmetros de segmentação e reconhecimento do reto integral.
Nenhum treinamento ou adaptação foi feito. A referência segue literalmente a edição
publicada; não é uma nova transcrição humana validada.

## Resultado

| Fólio completo | CER | Operações/caracteres | WER | Operações/palavras |
| --- | ---: | ---: | ---: | ---: |
| 269 reto (rodada anterior) | 26,97% | 391/1450 | 60,31% | 158/262 |
| 269 verso (esta rodada) | 16,48% | 237/1438 | 56,25% | 153/272 |

No verso: **237 operações em 1438 caracteres**
(172 substituições, 50 deleções e 15 inserções)
e **153 operações em 272 palavras**
(124 substituições, 25 deleções e 4 inserções).
CER/WER são distâncias de edição normalizadas, não porcentagens simples de acerto.

Foram processados **36 recortes automáticos**, com **0 falhas técnicas**.
Há 2 saídas vazias (ordens 0, 35, iniciadas em zero),
correspondentes às bordas superior e inferior. Todas as saídas, inclusive vazias,
foram mantidas. Os 34 recortes intermediários acompanham as 34 linhas editoriais;
a correspondência foi inspecionada pelo assistente de IA, sem nova validação humana.

O resultado menor no verso não demonstra melhora do modelo: os pesos são idênticos
e o conteúdo é diferente. O reto inclui cabeçalho, título e resumo, que não formam
blocos separados neste verso. Ambos pertencem ao mesmo documento usado no
desenvolvimento; não constituem avaliação reservada nem teste entre documentos.

## Principais erros observados

- **Letras e grafia:** `formasse` sai como `fosmasse`, `Levantando` como
  `Leuantando` e `pelourinho` como `peLoarinho`. Há trocas de caracteres e caixa.
- **Espaçamento:** a saída divide `Resposta` em `Res posta` e junta `por Sua`
  em `porsua`. Na linha 3, `Com o Liado Em toda ella` aparece como
  `Comalsada emta da ella`, com trocas e perda de conteúdo.
- **Nomes próprios:** `João` aparece como `doaõ` e `Ioaõ`; `Machado` como
  `Tacha do`, e `Antonio Luis da penha` como `Antonio Liu daponha`.
- **Acentos, caixa e pontuação:** diferenças como `Estácio`/`Estacio` e
  `Senhor`/`senhor` também contam. O til em saída decomposta é preservado no bruto;
  NFC unifica formas Unicode equivalentes, mas não corrige til na vogal errada.
- **Convenções da edição:** mantidos `Com o Liado`, `Prepetuo`, `Lemeda`, os
  sinais `=`, os espaços e as quebras editoriais, como `Cap / pitão` e `Cas / Cais`.
  A avaliação inclui diferenças de representação editorial e não isola erros
  paleográficos do reconhecedor. Não houve harmonização para reduzir as taxas.

## Exemplos completos

Linhas numeradas de 1 a 34 dentro do verso; não são as linhas 1–24 do reto.
Os exemplos são ilustrativos, sem média de taxas por linha.

| Linha do verso | Edição oficial | Saída bruta |
| --- | --- | --- |
| 3 | nia e ouvidor Com o Liado Em toda ella | nia e ouvidor Comalsada emta da ella |
| 4 | lhe formasse villa Levantando pelourinho | lhe fosmasse villa Leuantando peLoarinho |
| 14 | requerimentos mandou a mim Tabelião | Requrimentos mandaa amim Tobaliaõ |
| 20 | e a Resposta dos ditos officiais della e que | e a Res posta dos ditos offeciais della e que |
| 25 | signados e Eu Francisco Novo de Mandonssa | signados e heTraneyco Nauo de Mendonsa |
| 33 | João Leme do Prado = João Pais Mello = Mathias | doaõ Leme da Prado = Ioaõ Pais malho = Malhias |
| 34 | Machado Castello Branco = Antonio Luis da penha | Tacha do Castello Brenco = Antonio Liu daponha |

## Fonte, cobertura e procedimento

A imagem é o JPEG original embutido na página 2 do fac-símile, extraído sem
filtros ou reamostragem: 1195 × 1883 pixels. A edição cobre o verso em **10 linhas
na página PDF 2 e 24 na página PDF 3**, após `269/Verso.` e antes do marcador `270`.
Esses marcadores são editoriais e não aparecem como texto deste verso na imagem;
foram excluídos, juntamente com o final do reto e o conteúdo do fólio seguinte.
As páginas da edição e o manuscrito foram inspecionados visualmente pelo assistente.

O OpenCV por projeção recebeu a imagem inteira; nenhum recorte humano foi usado.
Os parâmetros não foram ajustados para este fólio. A margem horizontal automática
foi de 72 pixels em cada lado, pela mesma razão 0,06 usada no reto. Limites apertados
podem afetar a leitura; sua contribuição não foi isolada. Nenhuma caixa foi retocada.

O modelo recebeu apenas imagens. Os alvos foram extraídos e congelados antes da
inferência. A configuração copiada do reto é idêntica byte a byte, inclusive os
caminhos históricos do TOML; a execução usa explicitamente os manifestos e saídas
desta nova pasta, sem invocar o editor ou escrever no workspace do reto.
Pesos PP-OCRv6 medium SHA-256:
`15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9`.
Docker: `paleographia-kraken:7.1.0-cpu`, identidade fixada no protocolo;
CPU/float32, sem rede e com pesos montados somente para leitura.

O cálculo principal concatena todas as linhas editoriais e todas as saídas na ordem,
com espaço entre elas. Aplica somente NFC e colapso de espaços nos dois lados;
preserva caixa, grafia, acentos, pontuação e desenvolvimentos da edição. Não foi
aplicada correção lexical, pós-processamento editorial ou seleção de melhores saídas.
O alinhamento de palavras é uma solução de distância mínima e não uma atribuição
causal de cada erro; exemplos devem ser lidos com seu contexto.

## Preservação e auditoria

Comparados por hash antes e depois: **789 arquivos
versionados e 82 arquivos de workspaces, todos inalterados**.
As revisões, o reconhecimento bruto anterior, os pacotes de 20/10 e 22/10 e as oito
ressalvas do reto (11, 15, 16, 17, 19, 20, 23 e 24) continuam preservados.
Nenhum estado humano foi promovido. A inspeção da cobertura não resolve dúvidas
paleográficas nem substitui a conferência humana.

O auditor offline confere hashes, extração do PDF, bytes da imagem original,
configuração idêntica ao reto, geometria e pixels de todos os recortes, identidade
do modelo, integridade do bruto e CER/WER com uma segunda implementação de
distância de edição. Não executa nova inferência, não carrega pesos e não usa rede.
O recibo de preservação documenta esta execução; não exige congelar o editor vivo.
Os testes e o resultado detalhado estão em [validacao.json](validacao.json).
Esta nova pasta ainda não integra automaticamente as matrizes da CI acadêmica.

## Evidências

- [Saída bruta](transcricao_bruta.txt) e [JSON das predições](ppocrv6/predictions.jsonl).
- [Texto oficial](texto_oficial.txt), [alvos com páginas e posições](alvos_editoriais.jsonl)
  e [extração integral das páginas da edição](edicao_extraida.json).
- [Manuscrito original](manuscrito_269v_original.jpg),
  [sobreposição dos recortes](segmentacao/p_traslado_269v_overlay.png),
  [página 2 da edição](edicao_pagina_2.png) e [página 3](edicao_pagina_3.png).
- [Métricas](comparacao.json), [CSV](por_area.csv) e [alinhamento de erros](erros_palavras.jsonl).
- [Protocolo](protocolo.json), [entradas congeladas](entradas_congeladas.json),
  [execução e runtime](ppocrv6/proveniencia.json), [preservação](preservacao_depois.json)
  e [inventário](inventario.json).
