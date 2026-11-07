# Notebook 3 — PLN depois do reconhecimento

[`PaleographIA_Notebook_3_PLN.ipynb`](PaleographIA_Notebook_3_PLN.ipynb) reúne as duas comparações
da entrega de PLN, sobre predições já salvas (sem GPU nem Docker; no Colab ele baixa o repositório público):

1. **Modelos:** PP-OCRv6 base × ajustado A (Traslado) × ajustado B (Traslado + Inquisição), CER e WER
   em NFC nas 7 linhas de validação de 1795.
2. **Análise linguística dos erros:** alinhamento por distância de edição e classificação de cada erro
   (espaço, pontuação, abreviatura, maiúscula, acento, grafia histórica, nome próprio, forma da letra).
3. **Pós-correção lexical:** método A (Levenshtein) × método B (TF-IDF de n-gramas de caracteres), com
   vocabulário só de transcrições de treino e de `data/lexicon`.

| Modelo | Bruto (CER / WER) | Pós-correção A | Pós-correção B |
|---|---|---|---|
| PP-OCRv6 base | 14,20% / 56,72% | 16,52% / 50,75% | 20,00% / 53,73% |
| Ajustado A | 10,72% / 41,79% | 13,91% / 38,81% | 14,78% / 43,28% |
| Ajustado B | **10,14% / 38,81%** | 12,75% / 35,82% | 16,23% / 41,79% |

A pós-correção piora o CER: o vocabulário de treino (2.188 formas) não contém 14 das 51 palavras da
validação, que acabam "corrigidas" para vizinhas erradas. Fica como sugestão ao revisor, nunca
automática. Números de desenvolvimento; o teste reservado ainda não foi usado.

Código: `src/paleographia/pln_erros.py` (testes em `tests/test_pln_erros.py`) e
`scripts/analise_pln.py`, que grava [`resultados_pln.json`](resultados_pln.json).
