# PaleographIA — entrega do Notebook 1

**[Ver o Notebook 1 já executado](PaleographIA_Notebook_1_Entrega.ipynb)** — consulte o código, os gráficos e as tabelas com as saídas salvas diretamente no GitHub.

**[Baixar o pacote completo (ZIP)](https://raw.githubusercontent.com/aj1no/paleographia-htr/main/docs/entregas/notebook_1_offline/PaleographIA_Entrega_Offline.zip)**

1. Baixe o ZIP e escolha **Extrair tudo**. Abra os arquivos na pasta extraída.
2. Para reproduzir os resultados, escolha uma das opções abaixo.
3. Para ler o artigo, abra `PaleographIA_Artigo.pdf`. Os gráficos e as tabelas detalhadas já executados estão no notebook da pasta `consulta`.

### Com Jupyter

Abra `PaleographIA_Notebook_1_Offline.ipynb`, selecione um kernel Python e execute todas as células em ordem (**Run All / Executar tudo**).

### Sem Jupyter

Com o Python instalado, abra um terminal na pasta extraída e execute:

```text
python recalcular.py
```

No Windows, se `python` não for reconhecido, tente `py -3 recalcular.py`. Em Linux ou macOS, use `python3 recalcular.py` se esse for o comando disponível.

Os dados estão incorporados. O recálculo não usa internet, Git, Docker ou pacotes adicionais. Foi testado com Python 3.12 após extrair o ZIP em uma pasta nova, com conexões de rede bloqueadas e sem acesso a pacotes adicionais. O notebook da pasta `consulta` tem saídas salvas; para executar, use o notebook offline na raiz.

### Resultado esperado

| Reconhecedor | CER | WER |
| --- | ---: | ---: |
| PP-OCRv5 | 58,45% | 94,58% |
| PP-OCRv6 | 15,11% | 60,10% |

O cálculo usa predições arquivadas de 24 linhas do fólio 269r. Ele reproduz as métricas, sem rodar os reconhecedores novamente.

SHA-256 do ZIP: `a32d3edc7ceef7f65dadc1acc3e988ac4f0a49765663363de1e8a745db6462ed`.
