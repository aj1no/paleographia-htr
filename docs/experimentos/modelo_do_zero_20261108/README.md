# Curiosidade: reconhecedor treinado do zero (07–08/11/2026)

Experimento paralelo, feito por curiosidade, fora do pipeline principal: outro ambiente Python,
nenhum código do pacote `paleographia` importado e **nenhum peso pré-treinado** (nem PP-OCRv6,
nem TraPrInq, nem ImageNet). Inclui um pré-treino **não supervisionado**, em que o modelo nunca vê
texto. Não substitui o PP-OCRv6 ajustado B, que continua sendo o resultado principal do projeto.

## Resultado

Mesma validação de 1795 do artigo (7 linhas, 345 caracteres, 67 palavras):

| Modelo | CER | WER |
| --- | ---: | ---: |
| PP-OCRv6 ajustado B (projeto principal) | 10,14% | 38,81% |
| PP-OCRv6 ajustado A (projeto principal) | 10,72% | 41,79% |
| PP-OCRv6 medium sem ajuste | 14,20% | 56,72% |
| **Do zero, pré-treino não supervisionado + todas as linhas** | **15,94%** | **50,75%** |
| Do zero, só supervisionado, todas as linhas | 16,23% | 53,73% |
| Do zero, pré-treino + 5% das linhas rotuladas | 28,12% | 71,64% |
| Do zero, só supervisionado, 5% das linhas rotuladas | 71,88% | 101,49% |

- Partir de um modelo grande pré-treinado continua valendo: o melhor modelo do zero fica cerca de
  20 caracteres atrás do B em 345.
- O pré-treino não supervisionado quase não muda o resultado com todas as linhas rotuladas, mas com
  só 5% delas (637 linhas) derruba o CER de 71,88% para 28,12% em 1795 e de 72,60% para 37,04% na
  validação interna da Inquisição.
- Sozinho ele não lê: com o encoder congelado e só a saída treinando, o CER fica acima de 90%.

Tabela completa, com a carta de 1767 e as linhas transcritas: [`RESULTADOS.md`](RESULTADOS.md).
Painéis de cada etapa e o print do fim da noite: [`figuras/`](figuras/).

## Dados (só fontes públicas)

| Parte | Linhas | Uso |
| --- | ---: | --- |
| Inquisição — *Portuguese Handwriting 16th–19th c.* (Baudry et al., Zenodo 13986218, CC BY 4.0), 241 documentos | 12.543 | Treino |
| Inquisição, outros 20 documentos (separados por documento, não por linha) | 953 | Validação interna: escolhe o checkpoint |
| Traslado de 1767 (AHMJ, uso sem fins comerciais): as mesmas 191 linhas do ajuste A | 191 (repetidas 3× por época) | Treino |
| Sessão de 1795 (7) e carta de 1767 (3), referências diplomáticas humanas | 10 | Medida final, uma única vez; nunca escolhe nada |

Diferente do ajuste do PP-OCRv6, aqui a validação de 1795 **não** escolheu o checkpoint: a escolha
foi feita na validação interna da Inquisição. O teste reservado (pagamento a Thomas Pardo) não
entra em nada, nem como imagem sem texto; o preparo e o treino recusam qualquer registro com esse
nome. Nenhuma imagem é versionada aqui; a figura de reconstrução mostra uma linha da Inquisição
(CC BY 4.0).

As linhas da Inquisição são recortadas da página pela linha de base do PAGE XML (altura tirada do
espaçamento entre linhas da página), em tons de cinza, altura 64 px. As abreviaturas com letras
sobrescritas da convenção do projeto (`Nˢᵃ`, `muⁱᵗᵒˢ`) não existem nas transcrições da Inquisição;
o modelo não tem como produzi-las.

## Modelo e treino

- **Reconhecedor** (`codigo/comum.py`): CRNN-CTC com 6,26 milhões de parâmetros. 7 convoluções
  com BatchNorm (altura 64 → 4, largura ÷ 4), projeção para 256, BiLSTM de 3 camadas (256 por
  direção), saída para 138 caracteres + branco. Aumento de dados: inclinação, pequena rotação,
  largura da letra, traço fino/grosso, desfoque, contraste e ruído. AdamW, OneCycle, fp32 (a GTX
  1650 gera NaN em meia precisão), decodificação gulosa. 25.000 passos, lote 24, cerca de 2h20.
- **Pré-treino não supervisionado** (`codigo/pretreino_ssl.py`): autoencoder mascarado sobre
  colunas. Cerca de 40% da linha é apagada em trechos de 8 a 32 px e o mesmo encoder CNN + BiLSTM
  reconstrói os pixels apagados. Só as imagens de treino, sem texto. 12.000 passos.
- **Medidas do pré-treino:** sonda linear (encoder congelado, contra um encoder aleatório
  congelado), poucos rótulos (5%) e ajuste completo, sempre contra o mesmo treino do zero.

GPU NVIDIA GTX 1650 (4 GB), PyTorch 2.14.1 (cu126); versões em
[`codigo/requisitos_congelados.txt`](codigo/requisitos_congelados.txt). Em `resultados/` ficam a
configuração, o log de validação e o resultado de cada etapa; pesos e logs completos ficaram fora
do Git. A última etapa terminou com o código 0xC0000409 do Windows ao fechar os processos de
leitura de dados, **depois** de gravar o `resultado.json`; nenhum número foi afetado.

## Rodar

Em uma pasta separada, com PyTorch instalado:

```
python codigo/preparar_dados.py CAMINHO/DO/PaleographIA
python codigo/rodar_noite.py      # sequência inteira, um treino por vez; retoma o que já terminou
```

Os passos de cada etapa ficam em `codigo/passos.json`.
