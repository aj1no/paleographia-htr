# Notebook e primeiro rascunho — PI IV e PLN

Entrega de 20/10/2026, baseada exclusivamente no diagnóstico publicado de
**24 linhas do fólio 269r**, com **oito ressalvas preservadas**. Não é teste
reservado nem referência humana independente da edição. Nenhuma função foi
adicionada ao sistema; o editor e os dados históricos permanecem inalterados.

## Ler os resultados

- [Notebook executado](comparacao_reproduzivel.ipynb): nove células de código,
  cálculos, tabelas e duas figuras, sem erros de execução.
- [Versão HTML do notebook](comparacao_reproduzivel.html): leitura sem Jupyter.
- [Primeiro rascunho do artigo](artigo_rascunho.md): base comum a PI IV e PLN;
  precisa de revisão dos autores e ajuste ao modelo de cada disciplina.
- [Adequação e pendências acadêmicas](adequacao_academica.md).
- [Fontes e escopo de consulta](fontes_consultadas.json).
- [Autoria e contatos informados](autoria.json).

| Reconhecedor | CER | WER |
| --- | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 94,58% |
| PP-OCRv6 medium / Kraken | 15,11% | 60,10% |

Os resultados foram recalculados a partir do bruto e dos alvos congelados,
com microcontagens dos cinco blocos completos: 1.112 caracteres e 203 palavras.
O notebook mantém as ressalvas das linhas 11, 15, 16, 17, 19, 20, 23 e 24,
sem filtrar linhas difíceis. O auditor independente do experimento também é
executado. O processo padrão não carrega pesos, não usa Docker e não realiza
novas inferências ou consultas a serviços externos.

## Reexecutar em ambiente separado

Requer um checkout completo do repositório e Python 3.12. Na raiz, em PowerShell:

```powershell
py -3.12 -m venv .venv-academico
.venv-academico/Scripts/python.exe -m pip install -e . -r docs/entregas/pi_iv_pln_20261020/requirements-notebook.txt
.venv-academico/Scripts/python.exe docs/entregas/pi_iv_pln_20261020/executar_notebook.py
```

A instalação inicial das dependências exige acesso ao registro de pacotes.
A auditoria e o recálculo, depois disso, usam apenas arquivos locais. As
dependências acadêmicas são opcionais e não foram incluídas no `pyproject.toml`.
O script usa o próprio interpretador do ambiente para o kernel e não instala
um kernel global. A lista completa do ambiente testado está em
[requirements-ambiente-testado.txt](requirements-ambiente-testado.txt).

O comando gera arquivos derivados em `output/entrega_academica_269r24_20261020/`:
notebook executado, HTML, figuras PNG/SVG, cinco CSVs e recibo numérico.
Reexecutar pode recriar esses derivados; não sobrescreve o notebook arquivado
nesta pasta, o experimento publicado ou o workspace. As cópias de figuras e
tabelas desta entrega correspondem à execução documentada.

A reexecução passou também em um checkout separado, sem pesos e sem workspace:
as cinco tabelas e as quatro figuras PNG/SVG ficaram idênticas byte a byte.
O recibo está em [validacao_checkout_limpo.json](validacao_checkout_limpo.json).

Para conferir a entrega arquivada:

```powershell
.venv-academico/Scripts/python.exe docs/entregas/pi_iv_pln_20261020/verificar_entrega.py
```

## Arquivos derivados e limites

As figuras [CER/WER](figuras/cer_wer.png) e [CER por bloco](figuras/cer_blocos.png)
também estão em SVG. Os CSVs ficam em `tabelas/`, incluindo todas as 48
combinações de linha e modelo. [resultado_notebook.json](resultado_notebook.json)
registra o recálculo e a preservação; [validacao_execucao.json](validacao_execucao.json)
documenta as verificações desta entrega.

Instituição e curso informados: Faculdade de Tecnologia de Jundiaí (FATEC Jundiaí),
Ciência de Dados, 5º semestre, Jundiaí – SP. Modelo, limite de páginas e rubricas finais
continuam pendentes. O professor foi registrado em campo separado da autoria dos quatro
alunos, sem presumir coautoria. A revisão bibliográfica inicial não substitui
a revisão sistemática de PI IV; não foram inventadas buscas, contagens de
seleção ou aprovações acadêmicas. A entrega é mantida na branch
`codex/refatoracao-piloto`, identificada como diagnóstico de desenvolvimento.
