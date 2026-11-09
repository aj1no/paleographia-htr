# Notebook comparativo: baseline × modelos ajustados (Entrega 06 do PI IV)

[`PaleographIA_Notebook_Comparativo.ipynb`](PaleographIA_Notebook_Comparativo.ipynb) compara o
**PP-OCRv6 medium sem ajuste (baseline)** com os dois modelos ajustados, A (Traslado) e B (Traslado
mais Inquisição). Usa os dados do próprio projeto: a validação de 1795 (7 linhas) e o
[teste reservado congelado](../../revisao_humana/teste_reservado_congelado_20261109/README.md), com
49 linhas lidas às cegas pela equipe e avaliadas uma única vez.

| Conjunto | Baseline | Ajustado A | Ajustado B |
| --- | ---: | ---: | ---: |
| Validação 1795 (CER / WER) | 14,2% / 56,7% | 10,7% / 41,8% | 10,1% / 38,8% |
| Teste, total (CER / WER) | 64,0% / 95,3% | 60,5% / 93,7% | 60,9% / 94,4% |
| Teste, pagamento (CER) | 31,1% | 27,9% | 28,3% |
| Teste, contrato (CER) | 77,1% | 73,5% | 73,8% |

O notebook também traz intervalos de confiança por bootstrap, a comparação pareada com o baseline,
a contagem de linhas que melhoraram e pioraram, exemplos e os tipos de erro.

**Conclusão:** o ajuste fino melhora o baseline de forma consistente (diferença pareada toda abaixo
de zero), A e B empatam, e o erro fora da validação mostra que o modelo ainda não generaliza para
outras mãos.

**Reprodutibilidade:** Python 3.10 ou mais novo, `jiwer` e `matplotlib`. O notebook roda sobre as
leituras gravadas, sem GPU, sem Docker e sem as imagens, e no Colab clona o repositório sozinho. Antes
de usar o teste, confere o SHA-256 da referência congelada. Para gerar e executar o notebook de novo,
use `python docs/entregas/notebook_comparativo_20261109/montar_notebook.py`, com `nbformat` e
`nbclient`.
