# Entrega atual do PaleographIA para PI IV e PLN

Pacote preparado em 23/10/2026, a partir de `dbcd8ce100147ba066233d9b4d6078b7159dcec9`.
**Artigo e notebook apresentam o diagnóstico dos mesmos 24 recortes do 269r.**
O notebook recalcula resultados das predições arquivadas de 20/10; não executa
novamente os reconhecedores nem realiza treinamento. A revisão final dos quatro
autores e o enquadramento docente de PI IV continuam pendentes.

| Material a entregar | Acesso |
| --- | --- |
| Notebook baseline indicado | [Arquivo `.ipynb` fixado](https://github.com/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb) |
| Artigo correspondente | [PDF](artigo.pdf), [Word editável](artigo.docx) e [Markdown](artigo.md) |
| Revisão ainda necessária | [Pontos dos autores e rodada dos oito recortes](revisao_pendente.md) |
| Evidências desta preparação | [Recibo do fechamento](fechamento.json) e [verificador](verificar_fechamento.py) |

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb)

## Executar e interpretar

No Colab, salve uma cópia no Drive, conecte ao ambiente padrão de CPU e use
**Executar tudo**. A primeira célula busca dados públicos na revisão `c8a3e9a`
completa registrada no notebook e prepara as bibliotecas necessárias. O notebook
não monta o Drive. Os formulários ficam vazios na demonstração; cada integrante
deve preencher sua própria seção e baixar o ZIP dos relatos antes de encerrar
a sessão. O [guia do Colab](../pi_iv_pln_20261023_colab/README.md) detalha esses passos.

O Colab é uma opção. Para executar localmente, use Python **3.11 ou 3.12**,
Git e um ambiente isolado. A partir de uma pasta de trabalho nova:

```powershell
git clone https://github.com/aj1no/paleographia-htr.git
cd paleographia-htr
python -m venv .venv-academico
.venv-academico/Scripts/python.exe -m pip install -e . -r docs/entregas/pi_iv_pln_20261022/requirements-notebook.txt
.venv-academico/Scripts/python.exe docs/entregas/pi_iv_pln_20261023_colab/validar_colab.py --saida output/equipe_colab_20261023/validacao_local
```

Em Linux/macOS, substitua `.venv-academico/Scripts/python.exe` por
`.venv-academico/bin/python`. O executor usa kernel novo e grava uma **cópia de
validação** em `output/equipe_colab_20261023/validacao_local/execucao_validacao.ipynb`;
não abra essa cópia para respostas pessoais, pois nova validação a recria.
Salve suas respostas em outro nome, por exemplo `minha_contribuicao.ipynb`.

Ver o arquivo no GitHub não executa as células. Baixar somente o `.ipynb` permite
o início automático pelo Colab; a execução local requer o checkout e as
dependências acima. Não há credenciais, caminho privado, pesos ou Docker no
recálculo. As versões são mostradas pela execução e registradas no recibo.

São **24 linhas**, cinco blocos, 1.112 caracteres e 203 palavras, com oito
ressalvas e 17 registros humanos históricos preservados. CER/WER esperados
para conferir a reprodução: PP-OCRv5 **58,45%/94,58%**, PP-OCRv6
**15,11%/60,10%**. NFC e colapso de espaços, com grafia, caixa e diacríticos
preservados. São taxas de erro contra referência assistida, não acurácia.
Não há partições de treino/validação/teste neste baseline: o conjunto inteiro
é desenvolvimento. O cálculo não usa sorteio; não há semente a fixar nesta etapa.

As 48 inferências históricas, hashes dos pesos, CPU/float32, pré-processamentos
e comandos para repeti-las estão no [experimento de 20/10](../../experimentos/traslado_269r_reconhecedores_24_20261020/README.md).
Essa reprodução de inferência é opcional e exige os dois runtimes e pesos
identificados ali; não integra o comando de recálculo acima.

## Dados e condições de uso

O recálculo lê os alvos assistidos, saídas, inventários e recortes versionados,
com a edição identificada separadamente. A autoria da conferência é de Rodolfo;
a edição de apoio é de Ana Caroline Carvalho Miranda, com revisão de Thiago
Paschoal conforme o PDF consultado. As oito dúvidas não viram leitura humana
independente pela execução automática.

Os créditos e as condições de consulta/redistribuição das fontes documentais
estão em [Fontes e condições de uso](../../sources.md). A licença MIT é do
código; não concede licença aos manuscritos, edições ou PDFs. Os 15 originais
do corpus ampliado não são pré-requisito do baseline. Para curadoria integral,
obtenha o ZIP v0.2 pela origem autorizada e confira o SHA-256
`62e1c3da154b4dcc9bdf63715c01eba788d7a2f6f5cce7a973938755772e25bd`.
O comando de restauração verifica os arquivos e recusa sobrescritas divergentes:

```powershell
python -m paleographia restore-corpus --archive CAMINHO_DO_ZIP_V02
```

Os [catálogos do corpus](../../../data/manifests/corpus_expandido_v02/) informam
origens e hashes. Permissões individuais de redistribuição continuam a conferir;
não é necessário obter esse ZIP para reproduzir as métricas publicadas.

## Links prontos para a planilha

A planilha **Grupos_PI_Jundiai_2026**, aba **Página1** (`gid=0`), foi consultada
em 23/10, sem edição. PaleographIA é o **grupo 4**, nas linhas **11–14**,
com os quatro nomes conferidos. **Link Notebook 1** é a célula mesclada
**F11:F14**, cuja célula inicial é **F11**; estava vazia na consulta.
O link de artigo já existente em **E11:E14** aponta para o planejamento inicial.

- [Ir à célula F11 na planilha](https://docs.google.com/spreadsheets/d/1QlHVMDzOaElIdInD9BIDEun_v5TgPhD36OWzQlFH8EQ/edit#gid=0&range=F11).
- **Valor preparado para Link Notebook 1:** [URL do notebook baseline](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb).
- **Artigo atual para eventual atualização da coluna Link Artigo:** [PDF no GitHub](https://github.com/aj1no/paleographia-htr/blob/main/docs/entregas/pi_iv_pln_20261023_fechamento/artigo.pdf).

Texto curto preparado para acompanhar os links:

> PaleographIA — diagnóstico de dois reconhecedores nas mesmas 24 linhas do
> fólio 269r. O notebook executa a auditoria e o recálculo de CER/WER a partir
> das predições arquivadas, com oito ressalvas preservadas. Não realiza novo
> reconhecimento ou treinamento. Artigo e instruções de acesso acompanham o link.

**Nenhuma célula foi alterada; nada foi submetido no Classroom e nenhum professor
ou colega foi contatado.** A equipe deve conferir os materiais e fazer a inserção
e a submissão. As datas 17/10, 24/10 e 31/10 foram relatadas como dias atendidos
pela atividade; não foram interpretadas como três prazos ou data-limite.

Descrição para o grupo consultar o professor de PI IV: o projeto compara dois
reconhecedores pré-treinados, apresenta dataset assistido e métricas de edição,
com revisão bibliográfica dirigida e ensaio técnico de ajuste fino separado.
Falta confirmar o enquadramento nas exigências de PI IV e completar a revisão
sistemática. Não há classificador adicional, teste reservado ou aprovação docente.

## Próximo avanço do dataset

| Unidade | Quantidade e condição atual |
| --- | --- |
| Fontes originais | 15 arquivos: oito PDFs e sete JPEGs |
| Páginas de PDF | 59; não são pares supervisionados |
| Ocorrências de manuscrito | 28; incluem cópias/reproduções e abertura com dois fólios |
| Grupos/documentos candidatos | Sete grupos e sete IDs; independência ainda pendente, sem total definitivo de documentos físicos independentes |
| Núcleo histórico do 269r | 24 linhas de desenvolvimento: 16 validadas e oito ressalvadas |
| Novos candidatos de 1795 | Oito recortes, zero novos pares validados/aptos |
| Partições científicas atuais | Zero pares aptos atribuídos a treino, validação ou teste; nenhum teste documental constituído |
| Ensaio técnico anterior | Duas linhas em treino e uma em validação técnica do mesmo documento; dois passos, sem teste |

A [rodada humana preparada](revisao_pendente.md#rodada-de-curadoria-dos-oito-recortes)
reutiliza os recortes e o editor existentes. Texto, geometria, correspondência
e cobertura têm decisões próprias. O catálogo de 1831 e todo o Traslado,
incluindo reto/verso/cópias, já são desenvolvimento e não podem virar novo teste.

A [configuração científica candidata](../../../configs/training_ppocrv6_scientific.toml)
continua bloqueada pela independência documental e pela falta de referências
revisadas. Não se força 80/10/10. Após a curadoria, será preciso congelar grupos,
política, manifests e orçamento, selecionar o checkpoint somente com validação
e comparar base/ajustado no mesmo teste. PP-OCRv5 × PP-OCRv6 continua a comparação
de PLN. Não houve novo treino neste fechamento; o pico próximo de 4 GiB no ensaio
anterior exige conferir recursos antes de ampliar o orçamento.

O ensaio usou altura de entrada de 96 pixels; a ficha do checkpoint-base
descreve 128 pixels. Antes da comparação futura, conferir e registrar uma
condição comum de pré-processamento/altura para base e ajustado, ou explicitar
o efeito das configurações diferentes. Mudança simultânea de entrada e de pesos
não permite atribuir toda a diferença ao ajuste fino. O teste reservado não
deve orientar codec, limites de entrada, taxa, épocas ou escolha de checkpoint.

## Uso de IA e revisão final

A [declaração atual de ferramentas](../../ai_comments.md) registra Codex e o
uso inicial de Antigravity informado no material recebido, sem inventar prompts,
modelos, datas de atividade ou autoria dos colegas. A planilha
`PaleographIA_Documentacao_Uso_IA.xlsx` não foi localizada no projeto nem nas
pastas de Downloads consultadas. Ela precisa ser disponibilizada para atualização
no próprio modelo; não foi criada planilha substituta nem foram confirmadas
as seis entradas pendentes dos colegas. A solicitação administrativa de
atualização anterior não foi acrescentada a um XLSX.

As [revisões dos quatro autores](revisao_pendente.md) estão preparadas, sem
aprovação atribuída. As versões de 20/10, 22/10, fundamentação, artigo anterior,
notebook colaborativo e Colab foram preservadas; esta pasta contém apenas o
novo artigo, orientações de fechamento e evidências necessárias.

## Conferências realizadas neste fechamento

O artigo tem **três páginas e nove referências**, incluindo a identificação
institucional de Antigravity. Foram conferidos os 76 blocos/células de conteúdo
entre Markdown, Word e PDF, os 13 links e todas as páginas renderizadas a 150 dpi.
O Word 16.0 exportou o PDF a partir do DOCX aberto somente para leitura.
O helper de documentos não encontrou LibreOffice no Windows; sua rasterização
foi reaproveitada sobre o PDF do Word, com Poppler, e as três páginas foram
inspecionadas. Não houve redução de fonte para ajustar a paginação.

A execução protegida terminou com **18 células, seis tabelas reproduzidas,
zero contribuições individuais novas e nenhuma operação bloqueada**. Foram
reutilizados o ambiente acadêmico isolado e o bloqueio existente de inferência,
pesos, conexões externas e escrita nas entradas. A primeira tentativa concluiu
os cálculos, mas falhou na limpeza de um cache do Windows; a rotina passou a
preservar o cache em `tmp/`, e a reexecução final terminou com código zero.
Não há teste de nova sessão hospedada ou de download do navegador nesta etapa;
a conferência dos formulários no Colab e a execução em Linux limpo estão
registradas na versão anterior, preservada.

Os **192 testes passaram**. A auditoria da expansão conferiu 126 arquivos e
os artefatos grandes locais, incluindo o peso final. O dry-run científico
retornou `not_executed`, bloqueado pela independência documental, sem criar
plano, comando Docker ou dados de treino. O [recibo](fechamento.json) registra
ambientes, comandos, hashes, preservação dos pacotes e pendências.

Para repetir a execução protegida, escolha uma saída nova:

```powershell
python docs/entregas/pi_iv_pln_20261023_fechamento/reexecutar_baseline.py --saida output/fechamento_20261023/NOVA_RODADA
```

Para conferir o pacote publicado sem executar o notebook ou os modelos, instale
o extra PDF no ambiente isolado e rode o verificador:

```powershell
python -m pip install -e ".[pdf]"
python docs/entregas/pi_iv_pln_20261023_fechamento/verificar_fechamento.py
```

Para regenerar o Word, use `gerar_artigo.py` com `python-docx`; para o PDF, use
o exportador preservado `../pi_iv_pln_20261023_entrega/exportar_pdf.ps1`, passando
os caminhos desta versão em `-Documento` e `-Pdf`. Confira novamente texto,
links e renderização após qualquer alteração; os hashes deste fechamento
identificam apenas os arquivos publicados nesta rodada.
