# Participação da equipe no Google Colab

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/main/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb)

Versão do [notebook colaborativo anterior](../pi_iv_pln_20261023_equipe/README.md)
preparada para preencher no navegador. Os notebooks históricos são preservados.
O cronograma inicial orienta as tarefas propostas; não comprova participação realizada.

1. Abra o botão e escolha **Arquivo → Salvar uma cópia no Drive**; coloque seu nome no título.
2. Conecte ao ambiente padrão de **CPU**. Use **Ambiente de execução → Executar tudo** e aguarde.
3. Leia a atividade da seção com seu nome. Preencha os cinco campos e execute novamente sua célula.
4. Na última seção, **Baixar minha contribuição**, selecione seu nome, marque `baixar_contribuicoes`
   e execute a célula. Envie o ZIP baixado ao grupo para a coordenação conferir.
5. Salve sua cópia do notebook. Se corrigir o relato, execute o formulário e baixe um novo ZIP.

Os menus podem variar conforme o idioma do Colab. Ao executar código do GitHub,
o Colab pode exibir seu aviso padrão; confira a origem `aj1no/paleographia-htr`.

| Integrante | Atividade proposta |
| --- | --- |
| Caio | Conferir T1/T4, identificar afirmação sustentada, limite e sugestão para o artigo |
| Guilherme | Conferir modelos, configurações, proveniência e reprodução das métricas |
| Tiago | Inspecionar recortes, vínculos imagem–texto e erros das linhas 1, 17 e 24 |
| Rodolfo | Registrar sua execução/coordenação e reunir os relatos para conferência |

Os campos são: quem preenche; data real em `AAAA-MM-DD`; contribuição concreta;
evidências (caminho, URL ou `relato: descrição`, separadas por ponto e vírgula);
uso de IA, ou declaração de não utilização. Registre apenas o que efetivamente
fez ou trouxe à discussão. Formulários vazios não criam registros. Um relato
preenchido é autodeclarado e fica pendente de conferência; não autentica identidade
nem valida uma linha do manuscrito. Reexecutar o formulário cria outra versão.

**Baixe o ZIP antes de encerrar a sessão.** Os JSONs em
`output/participacao_equipe_20261023/` ficam no ambiente temporário do Colab.
Salvar o notebook no Drive não salva esses arquivos. O ZIP inclui apenas os
JSONs do integrante selecionado e um LEIA-ME; envie separadamente evidências
externas ou outros arquivos produzidos. A equipe recebe o ZIP manualmente e
confere os relatos antes de incorporá-los ao projeto. Não há publicação automática.

A preparação usa internet e Git público, busca somente as pastas necessárias
na revisão `c8a3e9a7f1cc55b66d630c510eff17ff95dfdece` e instala bibliotecas ausentes
ou incompatíveis com o notebook. Mantém bibliotecas compatíveis do ambiente.
Não precisa de token GitHub, instalação local, montagem do Drive ou GPU.
São recalculadas métricas das saídas arquivadas; não há nova inferência ou treino.
O catálogo, as 17 revisões humanas e as oito ressalvas anteriores são preservados.

`gerar_colab.py` cria o notebook com a preparação e o exportador incorporados,
para funcionar mesmo antes de existir um checkout. `preparar_colab.py` verifica
origem e revisão antes de reutilizar uma pasta existente. Fora do Colab, a célula
usa o checkout local e não instala pacotes nem acessa a rede. Resultados derivados
ficam em `output/equipe_colab_20261023/`.

A implementação usa o [botão oficial para notebooks GitHub](https://github.com/googlecolab/colabtools/blob/main/notebooks/colab-github-demo.ipynb),
os [formulários do Colab](https://colab.research.google.com/notebooks/forms.ipynb)
e [`google.colab.files.download`](https://github.com/googlecolab/colabtools/blob/main/google/colab/files.py).
O [FAQ oficial](https://research.google.com/colaboratory/faq.html) explica a
persistência dos notebooks e a natureza temporária das máquinas de execução.
Os ambientes do serviço podem mudar.

## Validação em 23/10/2026

As 18 células foram executadas em [Windows/Python 3.12.14](validacao_local.json)
e em [Linux limpo/Python 3.12.15](validacao_linux.json). No Linux, a primeira célula
buscou a revisão pública e instalou as dependências. Foram reproduzidas as seis
tabelas de 22/10, com os mesmos CER/WER, as oito ressalvas e os 17 registros
humanos históricos. Não foram gerados relatos individuais ou ZIPs vazios.
Os 192 testes do projeto passaram, incluindo seis novos testes de preparação,
formulários, preservação dos cálculos e separação dos relatos no download.

O teste Linux usa `Dockerfile.validacao` e `validar_colab.py --checkout-remoto`.
Explicita o ramo de preparação Colab em um kernel comum, sem simular a interface
hospedada. **A sessão autenticada do Colab e o download pelo navegador não foram
testados nesta validação.** A criação do ZIP e a preservação dos JSONs foram
testadas automaticamente; o acionamento do download usa a API oficial do Colab.

Para reproduzir localmente, com as dependências de notebook disponíveis:

```powershell
python docs/entregas/pi_iv_pln_20261023_colab/validar_colab.py --saida output/equipe_colab_20261023/validacao_local
```

Para conferir a preparação remota em Linux com Docker, a partir da raiz do projeto:

```powershell
docker build -f docs/entregas/pi_iv_pln_20261023_colab/Dockerfile.validacao -t paleographia-colab-validacao:20261023 docs/entregas/pi_iv_pln_20261023_colab
$colabWorkspace = (Get-Location).Path
$colabResults = New-Item -ItemType Directory -Force output/equipe_colab_20261023/validacao_linux
docker run --rm --cpus 2 --memory 2g --mount "type=bind,source=$colabWorkspace,target=/entrada,readonly" --mount "type=bind,source=$($colabResults.FullName),target=/resultados" paleographia-colab-validacao:20261023 python /entrada/docs/entregas/pi_iv_pln_20261023_colab/validar_colab.py --raiz /work/dados --saida /resultados --checkout-remoto
```

Preparação do notebook e testes por Codex (IA). Formulários entregues vazios;
nenhuma resposta foi escrita em nome dos alunos.
