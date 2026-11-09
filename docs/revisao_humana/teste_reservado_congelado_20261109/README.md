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
