# Teste reservado congelado (09/11/2026)

Referência fixa do teste final. Depois deste registro ela não muda. Cada configuração final do
PP-OCRv6 roda **uma única vez** nela, com [`scripts/avaliar_teste_final.py`](../../../scripts/avaliar_teste_final.py).
Esse script foi escrito e commitado junto com o congelamento, **antes** de qualquer modelo rodar
nestas imagens.

| Documento | Linhas | Caracteres | Revisor (leitura às cegas) |
| --- | ---: | ---: | --- |
| [Pagamento a Thomas Pardo](../pagamento_thomas_pardo_teste/README.md), livro 0146, 113v e 114r | 14 | 467 | Rodolfo Takemoto |
| [Contrato do livro 12, 1763](../contrato_livro12_teste/README.md), página 9 do PDF da edição | 35 | 1.177 | Tiago Avelar |
| **Total** | **49** | **1.644** | |

- **Às cegas:** as duas curadorias rodaram com o reconhecedor desligado. No congelamento, nenhuma
  tinha predição de modelo (`model_predictions_before_freeze: 0`).
- **Só linhas validadas:** transcrição diplomática humana, com revisor identificado e sem motivo de
  exclusão. As linhas ilegíveis ou não lidas ficaram de fora: 47 no pagamento e 104 no contrato
  (páginas 10 a 12 do PDF, não transcritas).
- **Recortes:** são os mesmos que os revisores leram no modo leitura. Ler a linha inteira no recorte
  e validá-la conta como conferência do recorte (o modo leitura não tem a caixa separada de
  geometria). No contrato, os pedaços que o blla cortou já tinham sido juntados antes da leitura
  nas páginas 10 a 12. Na página 9, alguns pedaços curtos foram lidos e validados como linhas
  próprias.
- **Cobertura do 113v:** as seis primeiras linhas validadas ficam no topo da página. Pela reserva de
  05/11, ali há outro recibo, assinado por Caetano Antonio Rangel. Para medir o reconhecimento isso
  não muda nada (é a mesma imagem, sem uso anterior), mas essas linhas não correspondem à edição
  do pagamento. A confirmação cabe ao revisor.
- **Edição:** os revisores podiam consultar a edição modernizada para tirar dúvidas, depois de ler a
  imagem, como no 269r. A referência registra o que está no manuscrito.

## Arquivos

- [`referencia.jsonl`](referencia.jsonl): uma linha por recorte, com o texto diplomático, o revisor,
  a geometria, o SHA-256 da imagem de origem e o SHA-256 do recorte.
- [`congelamento.json`](congelamento.json): data, SHA-256 da referência
  (`2d0fb78e021f72a971a2ae8ccacbc72544b560a5c7e57b1366cf2fe273a6fee0`), contagens e as revisões dos
  workspaces congelados.
- Os recortes ficam na pasta local `data/teste_reservado_congelado_20261109/recortes/`, fora do Git
  (imagens do acervo). O script de avaliação confere o hash de cada um antes de rodar.
- Script do congelamento: [`scripts/congelar_teste_reservado.py`](../../../scripts/congelar_teste_reservado.py).
  Ele se recusa a rodar de novo.

## Avaliação prevista

PP-OCRv6 base, ajustado A e ajustado B, com os mesmos pesos (conferidos pelo SHA-256) e o mesmo
worker de inferência da validação de 1795: Docker `paleographia-kraken:7.1.0-cpu`, CPU, float32. As
métricas são CER e WER em NFC, com espaços simplificados, por linha, por documento e no total. O
resultado vai para `avaliacao_final.json` nesta pasta. Um modelo que já tem resultado gravado não
roda de novo.

## Resultado da avaliação única (09/11/2026)

Cada modelo rodou **uma vez**, no commit do congelamento (`1797998`; depois da [reescrita das mensagens em 09/11](../../manutencao/reescrita_historico_20261109/README.md), `472f9f6`, com a mesma árvore), com os hashes da referência,
dos recortes e dos pesos conferidos. Os dados estão em [`avaliacao_final.json`](avaliacao_final.json),
com a leitura de cada linha. Os intervalos foram calculados depois, a partir das mesmas predições,
sem rodar nenhum modelo de novo ([`analise_intervalos.json`](analise_intervalos.json),
[`scripts/analisar_teste_final.py`](../../../scripts/analisar_teste_final.py)).

CER em NFC, com IC 95% por bootstrap de linhas:

| Modelo | Total (49 linhas) | Pagamento (14) | Contrato (35) | WER total |
| --- | ---: | ---: | ---: | ---: |
| PP-OCRv6 base | 64,0% (57,1–71,4) | 31,1% (24,2–38,4) | 77,1% (72,9–81,6) | 95,3% |
| PP-OCRv6 ajustado A | 60,5% (53,5–67,8) | 27,9% (21,8–33,9) | 73,5% (69,5–77,8) | 93,7% |
| PP-OCRv6 ajustado B | 60,9% (54,0–68,0) | 28,3% (22,8–33,9) | 73,8% (69,6–78,3) | 94,4% |

- **O ajuste fino ajuda, mas pouco fora do domínio.** A e B ficam abaixo do base nas mesmas linhas.
  A diferença pareada de CER é de −1,5 a −5,6 pontos para o A e de −1,4 a −4,9 para o B (IC 95%).
  **A e B não se distinguem** entre si.
- **A distância para a validação é grande.** Em 1795, o B teve 10,1% de CER. No teste, foi 28% no
  pagamento (letra grande e regular) e 74% no contrato. No contrato, a saída é quase sempre ilegível:
  letra cursiva densa, tinta do verso aparecendo e imagem tirada de dentro do PDF da edição.
- **Pedaços curtos.** Em 9 linhas os três modelos não leram nada. Todas são pedaços de margem com 1
  ou 2 palavras ("ou", "na", "Com"…). Sem os 12 pedaços de margem (análise post hoc, 37 linhas), o
  CER do B fica em 59,4% (51,7–66,5).
- **Qualidade da referência do contrato (observação posterior ao resultado).** Uma linha validada
  tem como texto uma nota do revisor ("não e possivele ler"), e não uma leitura. Algumas linhas
  parecem seguir a grafia da edição ("Manuel", "Francisco" por extenso), e não a do manuscrito.
  Pelo protocolo, a referência congelada **não foi alterada** e os números acima valem como estão.
  Uma auditoria do revisor pode produzir uma referência corrigida. Ela só pode ser aplicada às
  **mesmas predições gravadas** e precisa ser identificada como análise posterior.

## Ajustado D1 (11/11/2026)

O D1 é um modelo novo, treinado depois do congelamento: Traslado + Posturas de 1831, fólios 100r e
100v. O checkpoint foi escolhido no dev 101r + 1795, sem olhar o teste
([registro](../../experimentos/ppocrv6_ajustado_C/noturno_20261110/README.md)). Ele foi o único
candidato novo levado ao teste e rodou **uma vez**, pelo mesmo script, com a referência, os
recortes e os pesos conferidos (SHA-256 `13a1fa98…`). Os modelos já avaliados não rodaram de novo,
e os números deles não mudaram.

| Modelo | Total (49 linhas) | Pagamento (14) | Contrato (35) | WER total |
| --- | ---: | ---: | ---: | ---: |
| PP-OCRv6 ajustado B | 60,9% (54,0–68,0) | 28,3% (22,8–33,9) | 73,8% (69,6–78,3) | 94,4% |
| **PP-OCRv6 ajustado D1** | **55,4% (49,5–61,9)** | 29,0% (23,5–35,0) | **65,9% (62,1–70,3)** | 94,4% |

Diferença pareada de CER entre o D1 e o B (bootstrap de linhas, 2.000 reamostragens, semente 7):

| Recorte | D1 − B | IC 95% |
| --- | ---: | ---: |
| Total | −5,4 pontos | −8,1 a −3,3 |
| Contrato | −7,8 pontos | −11,0 a −5,4 |
| Pagamento | +0,6 ponto | −2,1 a +3,4 |

- **O D1 erra menos que o B**, e o intervalo não cruza o zero. Toda a melhora vem do contrato do
  livro 12: no pagamento, os dois empatam. Linha a linha, o D1 melhora 25 linhas, piora 5 e empata 19.
- **Em palavras, nada muda** (WER de 94,4% nos dois). A melhora é de caracteres soltos dentro de
  palavras que continuam erradas.
- **Por isso, o D1 substituiu o B na aplicação** (`configs/demo_apresentacao.toml`, 11/11).
- **Ressalva:** o teste já foi usado para 4 modelos. Cada um rodou uma vez, mas a comparação entre
  eles não é mais totalmente cega. A escolha do D1 foi feita antes, no dev, e não no teste.
