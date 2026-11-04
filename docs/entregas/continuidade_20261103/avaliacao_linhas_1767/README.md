# Avaliação por linha da carta de 1767

**[Notebook executado para apresentação](PaleographIA_Notebook_2_Carta_1767.ipynb).** Abra no Colab ou no Jupyter e execute todas as células para recalcular CER e WER a partir das previsões incorporadas. Para testar os dois reconhecedores ao vivo, abra o notebook no Jupyter local a partir do checkout preparado e mude `EXECUTAR_INFERENCIA_LOCAL` para `True`. A última seção reúne a evidência do ajuste fino técnico e o plano para avaliar base e ajustado em documentos reservados.

Diagnóstico exploratório de reconhecimento manuscrito no fólio **4r**. A seleção congela as linhas físicas **1, 3 e 4**, com recortes e transcrições diplomáticas aprovados. As linhas **2, 5 e 6** têm geometria aprovada e referência diplomática pendente. A região das seis linhas mantém `complete=false`. A partição científica está pendente. [Histórico da curadoria](../../../revisao_humana/carta_jose_gomes_1767/sessao_20261103/anotacao_superior_leitura_de_trabalho.md).

| Arquivo | Conteúdo |
| --- | --- |
| [Referências](referencias.jsonl) | Três transcrições diplomáticas e suas respectivas imagens |
| [Recortes para reconhecimento](recortes.jsonl) | Os mesmos três PNGs na mesma ordem, com o texto de referência separado |
| [Exclusões](exclusoes.jsonl) | Linhas 2, 5 e 6 e os motivos de cada exclusão |
| [Página e cobertura](paginas.jsonl) | Identificação do fólio, limites e cobertura textual incompleta |
| [Protocolo](protocolo.json) | Seleção, regras de cálculo, identidades dos modelos e hashes das entradas |

Os modelos são **latin PP-OCRv5 mobile via ONNX** e **PP-OCRv6 medium via Kraken 7.1**, as configurações usadas no Notebook 1. Cada um recebeu os mesmos recortes e usou seu pré-processamento nativo. Os pesos locais, a imagem Docker e o worker Kraken foram conferidos. As referências foram congeladas antes da inferência.

## Resultados de 04/11/2026

Os dois reconhecedores processaram as três imagens sem falhas de execução. A tabela agrega **128 caracteres** e **26 palavras** de referência. [Métricas agregadas](execucao_01/metricas/comparacao.json) e [métricas por linha](execucao_01/metricas/por_linha.jsonl).

| Modelo | CER | WER |
| --- | ---: | ---: |
| PP-OCRv5 | 79,69% (102/128) | 100,00% (26/26) |
| PP-OCRv6 | 25,78% (33/128) | 65,38% (17/26) |

O **PP-OCRv5** teve 86 deleções de caracteres. Na linha 3, produziu `n lmn r.do Ee` para uma referência de oito palavras. Na linha 4, produziu apenas `d`. [Previsões brutas](execucao_01/ppocrv5/predictions.jsonl).

O **PP-OCRv6** errou formas como `Paquem` por `Paguem`, `Snr.` por `Srsˢ` e `Deseu` por `Desco-`, com perda do hífen. Na linha 4, produziu `lampo vorde` por `campo verde`, `m.tos` por `muⁱᵗᵒˢ` e `estao` por `estão`. [Previsões brutas](execucao_01/ppocrv6/predictions.jsonl).

Os arquivos da execução foram arquivados byte a byte, com os recibos de carregamento e a proveniência de cada modelo. [Inventário SHA-256](execucao_01/inventario.json).

## Execução na raiz do repositório

Use a `.venv` do projeto, os pesos locais e a imagem Docker fixada no protocolo. As fontes brutas e os recortes são lidos pelos caminhos registrados nos manifestos. Em outro checkout, restaure os arquivos de origem do corpus v0.2 e o runtime Kraken. [Restauração das fontes](../../../dataset_expansion_20261023/README.md) e [runtime Kraken](../../../../runtime/kraken_ppocrv6/README.md).

```powershell
$pacote = 'docs/entregas/continuidade_20261103/avaliacao_linhas_1767'
$saida = 'output/avaliacao_linhas_1767/execucao_01'
$python = '.venv/Scripts/python.exe'

& $python "$pacote/avaliar.py"
& $python scripts/recognize_latin.py --lines "$pacote/recortes.jsonl" --output "$saida/ppocrv5/predictions.jsonl"
& $python -m paleographia recognize --config configs/traslado_269r.toml --lines "$pacote/recortes.jsonl" --output "$saida/ppocrv6/predictions.jsonl"
& $python "$pacote/avaliar.py" --ppocrv5 "$saida/ppocrv5/predictions.jsonl" --ppocrv6 "$saida/ppocrv6/predictions.jsonl" --output-dir "$saida/metricas"
```

O avaliador confere a identidade dos modelos, os recortes, os IDs e a ordem. Em seguida, grava `por_linha.jsonl` com referência, previsão bruta e CER/WER de cada linha, além de `comparacao.json` com as microcontagens dos dois modelos. O total divide a soma das operações de edição pela soma dos denominadores. Uma falha de reconhecimento registrada conta como previsão vazia. Linhas ausentes, duplicadas ou com metadados divergentes impedem o cálculo.

A normalização usa Unicode NFC e redução de espaços, preservando caixa, diacríticos, pontuação e grafia. Os resultados medem reconhecimento em três recortes fixos de um único documento. A qualidade da segmentação, a generalização entre documentos e o ganho de ajuste fino ficam fora do escopo desta comparação. [Política de transcrição](../../../transcription_policy.md).
