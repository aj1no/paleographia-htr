# PI IV e PLN — versão com reconferência posterior

Versão de **22/10/2026**, aditiva ao [pacote de 20/10](../pi_iv_pln_20261020/README.md).
Mantém **24 linhas, cinco blocos e oito ressalvas históricas**, sob a identificação
**diagnóstico de desenvolvimento**. O pacote anterior, o editor, os alvos e as
saídas brutas permanecem preservados.

- [Notebook executado](comparacao_reproduzivel.ipynb): dez células de código,
  duas figuras incorporadas e uma seção adicional de reconferência.
- [Notebook em HTML](comparacao_reproduzivel.html): leitura sem Jupyter.
- [Artigo revisado](artigo_rascunho.md): ainda rascunho, com seção 3.1 e limites explícitos.
- [Reconferência em CSV](tabelas/reconferencia_ressalvas.csv): oito linhas com
  alvo e ressalva originais, decisão posterior, confirmação pontual, apoio
  editorial, dúvida mantida, revisor, caminhos e hashes das evidências.
- [Proveniência](proveniencia_entrega.json), [verificações](validacao_execucao.json)
  e [inventário](manifesto_entrega.json).
- [Reprodução em cópia limpa](validacao_checkout_limpo.json) e
  [testes de alterações indevidas em cópia](testes_auditoria.json).
- [Adequação e pendências acadêmicas](adequacao_academica.md).

## O que a reconferência acrescenta

A [consolidação de 21/10](../../revisao_humana/traslado_269r/reconferencia_ressalvas_20261021/consolidacao.md)
registra 17 respostas/decisões de **Rodolfo Vinícius Cima Takemoto**. Há novas
confirmações pontuais nas linhas 15, 16 e 20; a linha 17 combina confirmação
visual e adoção editorial de `ministros`. Permanecem dúvidas visuais nas linhas
11, 19, 23 e 24, incluindo o sinal de `Requererão`, a inicial de `orgente`, os
dois s de `Justissa`, a base provável `Mag` e a pontuação final.

Esses registros são posteriores ao experimento. As oito ressalvas históricas
continuam presentes, sem nova contagem de linhas validadas ou promoção a
referência independente da edição. `Magᵈᵉ`, as quebras físicas e os alvos de
20/10 permanecem na avaliação. A consulta ao PDF por IA é distinta da leitura humana.

## Métricas conferidas

| Reconhecedor | CER | Operações/caracteres | WER | Operações/palavras |
| --- | ---: | ---: | ---: | ---: |
| latin PP-OCRv5 mobile / ONNX | 58,45% | 650/1.112 | 94,58% | 192/203 |
| PP-OCRv6 medium / Kraken | 15,11% | 168/1.112 | 60,10% | 122/203 |

São as mesmas taxas e microcontagens do experimento, reproduzidas a partir do
bruto e dos alvos congelados de 20/10. Usa-se NFC e colapso de espaços, mantendo
caixa, diacríticos e grafia, com agregação dos cinco blocos completos. As cinco
tabelas históricas permanecem idênticas byte a byte; o novo CSV é documental.
Nenhuma nova inferência, treinamento, pós-correção ou avaliação de nova referência
faz parte desta entrega.

Uma segunda execução em cópia isolada dos arquivos, sem pesos, workspace ou
diretório `.git`, reproduziu os seis CSVs e as quatro figuras byte a byte.
Três testes em cópias separadas, com manifestos recalculados, confirmaram que
o auditor rejeita alvo alterado, dúvida apagada e promoção indevida do catálogo.
As entradas e os registros humanos originais permaneceram intactos.

## Reprodução

Na raiz do repositório, com Python 3.12 e as dependências acadêmicas instaladas:

```powershell
py -3.12 -m venv .venv-academico
.venv-academico/Scripts/python.exe -m pip install -e . -r docs/entregas/pi_iv_pln_20261022/requirements-notebook.txt
.venv-academico/Scripts/python.exe docs/entregas/pi_iv_pln_20261022/reexecutar_protegido.py
.venv-academico/Scripts/python.exe docs/entregas/pi_iv_pln_20261022/verificar_entrega.py
```

Em Linux, use `.venv-academico/bin/python`. O executor utiliza seu próprio
interpretador para o kernel, sem instalar um kernel global. A instalação
inicial pode acessar o registro de pacotes; depois, o notebook lê somente
arquivos locais e grava derivados em `output/entrega_academica_269r24_20261022/`.
O executor não sobrescreve esta entrega nem o pacote de 20/10. O auditor confere
a entrega arquivada, incluindo seus recibos e o pacote anterior; não importa os
derivados locais automaticamente.

A reexecução protegida utiliza as proteções existentes de
`scripts/ci_academica_guard.py` no executor e no kernel: bloqueio de módulos de
inferência, acesso a pesos, conexões externas e escrita nas entradas. O log
da execução arquivada está em [protecao_execucao.jsonl](protecao_execucao.jsonl).
O comando de reprodução grava seu próprio log em `output/`.
As versões do ambiente
efetivamente executado constam em `resultado_notebook.json`; a lista completa
de dependências foi mantida como origem do ambiente já usado em 20/10.

A CI existente continua apontando para a entrega congelada de 20/10. Esta nova
versão foi reexecutada e auditada localmente; sua inclusão na execução automática
da CI é uma etapa separada.

## Limites acadêmicos

O fólio 269r continua sendo desenvolvimento, assistido pela edição. Não há teste
reservado, nova aprovação dos professores ou inferência de generalização. Modelo
de artigo, limite de páginas e rubricas precisam de confirmação; os autores devem
revisar texto, créditos e interpretações. B01/B02 têm cinco IDs recuperados com
triagem e leitura pendentes, sem alegação de revisão sistemática concluída.
Nenhuma função foi acrescentada ao sistema.
