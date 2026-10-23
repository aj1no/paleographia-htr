# Notebook colaborativo e participação dos alunos

Esta versão acrescenta às análises reproduzíveis uma atividade para cada
integrante, recuperando as responsabilidades do primeiro artigo e adaptando-as
ao estágio atual. O solicitante informou que a execução prática se concentra
nele, embora tenha havido discussão coletiva. Os relatos individuais ainda
precisam ser descritos e conferidos pelos participantes.

- [Notebook com atividades e formulários](colaboracao_equipe.ipynb).
- [Leitura em HTML](colaboracao_equipe.html), com a execução de demonstração.
- [Divisão de trabalho, rodadas e declaração a consolidar](roteiro_equipe.md).
- [Proveniência e verificações](manifesto.json).
- [Registro dos formulários](participacao.py), [gerador](gerar_notebook.py),
  [executor](executar_notebook.py) e [reexecução protegida](reexecutar_protegido.py).

## O que cada aluno encontra

Caio tem uma atividade de bibliografia e interpretação de T1/T4; Guilherme,
de modelos, ambiente e condições de comparação; Tiago, de inspeção de recortes,
associações e erros; Rodolfo, de coordenação e consolidação. Cada seção tem
material de apoio gerado automaticamente e um formulário inicialmente vazio.
Uma participação já ocorrida na discussão também pode ser documentada pelo
colega, com sua contribuição concreta e a data real.

A execução de demonstração por **Codex (IA)** deixa os quatro formulários
vazios, não cria novos registros de participação e não atribui as células aos
alunos pelo título da seção. O registro de Rodolfo na reconferência de 21/10
permanece com sua autoria original. Nenhum aluno é apresentado como autor de
uma decisão humana ou implementação feita por outra pessoa.

## Executar e contribuir

Na raiz do checkout, use o ambiente acadêmico já documentado:

```powershell
python -m pip install -e . -r docs/entregas/pi_iv_pln_20261022/requirements-notebook.txt
python docs/entregas/pi_iv_pln_20261023_equipe/reexecutar_protegido.py
```

A execução gera a cópia de trabalho em
`output/equipe_20261023/colaboracao_equipe.ipynb`, o HTML e os cálculos derivados.
Antes de preencher no Jupyter, salve uma cópia com nome individual, por exemplo
`output/equipe_20261023/caio.ipynb`. O executor regenera o arquivo chamado
`colaboracao_equipe.ipynb`; as respostas devem ficar na cópia individual.
Não é necessário editar o exemplar publicado. Os relatos preenchidos são
exportados separadamente para `output/participacao_equipe_20261023/`, com novo
arquivo a cada gravação. O projeto não publica ou autentica esses relatos
automaticamente; a coordenação e os participantes os conferem antes de usar
uma declaração de contribuições na entrega.

Não é necessário instalar modelos, Docker ou novos reconhecedores. A parte
numérica mantém as dez células de código do [notebook de 22/10](../pi_iv_pln_20261022/README.md),
mudando somente a pasta de saída. A reexecução continua protegida contra
inferência, rede externa e escrita nas entradas. As atividades não alteram o
catálogo, os alvos, as oito ressalvas ou as métricas históricas.

O [artigo preparado](../pi_iv_pln_20261023_entrega/README.md), os notebooks de
20/10 e 22/10 e seus manifestos permanecem preservados. As fontes integrais
de T1/T4 e a expansão do corpus são acessíveis pelos links do notebook.
