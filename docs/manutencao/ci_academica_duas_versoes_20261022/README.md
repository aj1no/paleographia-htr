# CI acadêmica das entregas de 20/10 e 22/10

A CI agora audita e reexecuta as duas versões de PI IV e PLN em tarefas
independentes, usando Ubuntu e Python 3.12. Continua sendo **diagnóstico de
desenvolvimento**, com referência assistida pela edição e oito ressalvas históricas.
Os pacotes de entrega e de reconferência não são editados por esta manutenção.
A [nota de 21/10](../ci_academica_20261021/README.md) conserva a implantação original.

| Versão | Células de código | CSVs | Pasta de derivados |
| --- | ---: | ---: | --- |
| 20261020 | 9 | 5 | `output/entrega_academica_269r24_20261020/` |
| 20261022 | 10 | 6 | `output/entrega_academica_269r24_20261022/` |

## Execução e preservação

`scripts/ci_academica.py --version DATA` aceita somente `20261020` e
`20261022`. Sem argumento, mantém a versão original de 20/10. `--root` continua
permitindo indicar um checkout limpo a partir de um ambiente acadêmico instalado.
A execução recusa pesos, workspaces e uma saída já existente da versão escolhida;
a saída da outra versão pode existir e é preservada.

Cada tarefa instala os requisitos acadêmicos do respectivo pacote, executa
seu auditor antes e depois do recálculo e confere os hashes de todos os arquivos
versionados. O executor e o kernel recebem as proteções existentes de
`scripts/ci_academica_guard.py`: bloqueio de inferência, acesso a pesos, conexões
externas e escrita nas entradas. Não são instalados extras de reconhecimento,
pesos ou Docker. A instalação inicial de dependências pode acessar o registro
de pacotes; a reprodução usa arquivos locais.

As duas versões devem reproduzir as mesmas métricas e microcontagens do
experimento congelado de 20/10: PP-OCRv5 com CER 58,45% e WER 94,58%; PP-OCRv6
com CER 15,11% e WER 60,10%. Também são conferidos fontes e execução integral
do notebook, os CSVs, o HTML, dois PNGs, dois SVGs e duas figuras incorporadas.
Imagens renderizadas em sistemas diferentes não precisam ter bytes idênticos;
os textos, números e tabelas são comparados exatamente.

## Reconferência posterior de 22/10

A sexta tabela preserva o alvo e a ressalva de 20/10 e acrescenta as decisões
de 21/10. São verificadas as oito linhas 11, 15, 16, 17, 19, 20, 23 e 24,
os 17 registros humanos e as dúvidas visuais mantidas nas linhas 11, 19, 23 e 24.
As confirmações pontuais de 15, 16 e 20 e a decisão mista de 17 não promovem
automaticamente o catálogo nem tornam a referência independente da edição.

Além de comparar o CSV gerado com o arquivado, a CI confere seus alvos, ressalvas,
confirmações, escolhas editoriais, dúvidas, autoria e caminhos/hashes contra
a consolidação publicada. A abreviatura, a pontuação em aberto, o histórico e
a autoria conservam seus escopos. A reconferência não altera os alvos das métricas.

## Artefatos separados

A matriz usa `fail-fast: false`, permitindo concluir o diagnóstico de ambas as
versões quando uma delas falha. Cada tarefa publica seus próprios derivados e
recibos como `ci-academica-VERSAO-COMMIT-TENTATIVA`, por 14 dias. Em caso de falha,
os arquivos parciais disponíveis são publicados para diagnóstico; consulte
o estado da tarefa e `ci_academica.json` antes de usá-los. O token continua com
`contents: read`. Os artefatos não substituem as evidências versionadas.

## Reproduzir

Use um checkout completo, sem pesos/workspace, e um ambiente Python 3.12 com
o projeto e os requisitos acadêmicos instalados. Por exemplo, em PowerShell:

```powershell
.venv-academico/Scripts/python.exe -m pip install -e . -r docs/entregas/pi_iv_pln_20261022/requirements-notebook.txt
.venv-academico/Scripts/python.exe scripts/ci_academica.py --version 20261020
.venv-academico/Scripts/python.exe scripts/ci_academica.py --version 20261022
```

Em Linux, use `.venv-academico/bin/python`. Os requisitos das duas versões são
idênticos nesta entrega. Os comandos acima podem ser executados sequencialmente
no mesmo checkout, pois as saídas são distintas. Uma segunda execução da mesma
versão é recusada para preservar os derivados; use outro checkout para repeti-la.

## Evidências desta manutenção

O [recibo de validação](validacao.json) registra testes, auditorias e reproduções
locais em cópia limpa, sem nova inferência. Os recibos de cada versão estão em
[20261020](execucao_20261020.json) e [20261022](execucao_20261022.json), com seus
logs de proteção. O [inventário](inventario.json) conserva os hashes das evidências.
As validações locais não são apresentadas como resultado de uma execução remota.
Os avisos de CI anterior nos pacotes de 20/10 e 22/10 são registros datados;
esta nota e os guias atuais descrevem a configuração posterior.
