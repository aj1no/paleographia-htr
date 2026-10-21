# CI acadêmica — 21/10/2026

A tarefa `academic` de `.github/workflows/ci.yml` audita a entrega de PI IV e PLN
e reexecuta o notebook a cada push ou pull request. Roda em Ubuntu/Python 3.12,
separadamente da matriz leve Windows/Ubuntu × Python 3.11/3.12. Usa o pacote
básico e os requisitos opcionais já publicados; não instala extras de OCR/HTR,
pesos ou Docker e não reconhece novamente o manuscrito.

## O que é conferido

1. O auditor original confere os 24 arquivos da entrega arquivada e o experimento
   de origem, antes da execução.
2. O executor original reexecuta as nove células de código, em kernel próprio.
   As fontes do notebook congelado não são editadas.
3. O recibo gerado deve manter o diagnóstico de desenvolvimento: 24 linhas,
   cinco blocos, oito ressalvas, zero inferências novas, sem treino ou teste reservado.
4. As contagens e taxas CER/WER devem coincidir com as publicadas, e os cinco
   CSVs devem conservar todas as linhas e campos. As ressalvas continuam nas
   linhas 11, 15, 16, 17, 19, 20, 23 e 24.
5. O notebook deve estar integralmente executado, sem erros, com duas figuras
   incorporadas. Também são conferidos HTML, dois PNGs e dois SVGs. Não se exige
   igualdade de bytes das novas imagens entre sistemas; fontes e renderização
   podem variar. Os números, textos e tabelas são comparados exatamente.
6. O auditor original é executado novamente, e os hashes de todos os arquivos
   versionados devem permanecer iguais. Nenhum workspace é criado.

Os pacotes de `docs/entregas/`, `docs/experimentos/` e `docs/revisao_humana/`
permanecem byte a byte como publicados, inclusive inventários, versões e oito
ressalvas. Os avisos anteriores de ausência da CI são registros datados;
esta nota e os guias atuais descrevem a situação posterior.

## Proteções da execução

`scripts/ci_academica.py` exige checkout sem pesos, workspaces e saída anterior.
Cria os derivados somente em `output/entrega_academica_269r24_20261020/` e usa
`tmp/` para o kernel e configurações temporárias.

`scripts/ci_academica_guard.py` é instalado temporariamente como `sitecustomize`
no executor e no kernel. Bloqueia importações de reconhecedores e bibliotecas
de inferência, acesso a `models/`, conexões externas e escrita nas entradas.
Permite comunicação em loopback e sockets locais para o Jupyter. Só permite
iniciar o kernel previsto e os utilitários de consulta de fontes `fc-list` e
`fc-match`. Tentativas proibidas são registradas e reprovam a execução mesmo
que alguma biblioteca capture a exceção.

As proteções são testadas com dados sintéticos identificados, sem modelos ou
contato com serviços externos. A reexecução real utiliza somente as predições
salvas do diagnóstico, sem alterar o significado acadêmico da referência assistida.

## Artefatos da CI

A tarefa publica notebook executado, HTML, tabelas, figuras, `resultado_notebook.json`,
`ci_academica.json` e `protecao.jsonl` como artefato `ci-academica-COMMIT-TENTATIVA`,
retido por 14 dias. Em falha, publica os derivados parciais disponíveis para
diagnóstico; o estado do job e o recibo devem ser consultados antes de usá-los.
Esses arquivos não são enviados à branch nem substituem as evidências canônicas
versionadas. O token do job possui apenas `contents: read`.

## Reproduzir localmente

Use um novo checkout, sem remover dados ou revisões do checkout de trabalho.
No Windows, a opção de caminhos longos atende aos nomes históricos já existentes:

```powershell
git -c core.longpaths=true clone --branch main https://github.com/aj1no/paleographia-htr.git paleographia-ci
cd paleographia-ci
py -3.12 -m venv .venv-academico
.venv-academico/Scripts/python.exe -m pip install -e . -r docs/entregas/pi_iv_pln_20261020/requirements-notebook.txt
.venv-academico/Scripts/python.exe scripts/ci_academica.py
```

Em Linux, use `python3.12 -m venv .venv-academico` e `.venv-academico/bin/python`.
A instalação inicial exige rede; o recálculo não consulta serviços externos.
Uma saída já existente é recusada; para repetir sem sobrescrita, use outro
checkout. `--root` permite indicar um checkout limpo a partir de um ambiente
acadêmico instalado, usando as fontes desse checkout.

## Validação desta entrega

O [recibo de manutenção](validacao.json) registra testes, auditorias, reexecução
em cópia sem modelos/workspace e preservação dos originais. As validações locais
não são apresentadas como resultado da execução remota do novo commit.

Configuração de artefatos e permissões conferida nas fontes oficiais:
[upload-artifact v4](https://github.com/actions/upload-artifact/tree/v4) e
[permissões do GITHUB_TOKEN](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).
