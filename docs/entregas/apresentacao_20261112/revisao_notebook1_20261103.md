# Conferência das mudanças da primeira entrega

Revisão realizada por Codex em **03/11/2026**, a pedido do solicitante. Base local anterior: `e8e96b3`. GitHub consultado por `git fetch origin`. Versão conferida: `6b213fceb455f5a91f87178f7516800235a20a3a`, incorporada à cópia local por fast-forward, preservando o planejamento da apresentação.

## Mudanças encontradas

Dois commits adicionaram três arquivos em [notebook_1_offline](../notebook_1_offline/README.md):

- `1831003`: pacote ZIP e instruções para execução offline.
- `6b213fc`: notebook detalhado já executado e link para consulta no GitHub.

O ZIP contém notebook offline, script de recálculo, instruções, artigo em PDF e notebook detalhado para consulta. Os commits não alteram os reconhecedores, o editor, as referências congeladas ou os resultados científicos.

## Verificações realizadas

| Verificação | Resultado |
| --- | --- |
| Integridade do ZIP | CRC conferido e SHA-256 igual ao informado no README: `a32d3edc7ceef7f65dadc1acc3e988ac4f0a49765663363de1e8a745db6462ed` |
| Extração | Cinco arquivos extraídos em pasta temporária nova, com destinos conferidos dentro dessa pasta |
| Dados incorporados | Alvos e predições dos dois modelos iguais às entradas canônicas, lidas como UTF-8 |
| Script `recalcular.py` | Executado com sucesso em Python 3.12.14, modo isolado e sem carregamento de site-packages (`-I -S`), com criação de conexões via socket bloqueada |
| Notebook offline | Todas as três células de código executadas sequencialmente nas mesmas condições, em namespace separado do script |
| Resultado dos dois caminhos | PP-OCRv5: CER 650/1.112 e WER 192/203. PP-OCRv6: CER 168/1.112 e WER 122/203 |
| Cobertura | 24 linhas, cinco blocos e oito ressalvas preservados |
| Notebook detalhado publicado | 44 células totais, 18 de código com contagens de execução de 1 a 18 e nenhuma saída de erro salva |
| Notebook publicado versus cópia no ZIP | Conteúdo JSON integral idêntico, incluindo células, saídas e metadados. Há diferença de serialização dos arquivos, sem diferença de conteúdo JSON |
| Artigo no ZIP | Bytes idênticos ao PDF de `pi_iv_pln_20261023_fechamento/artigo.pdf` |

O recibo da execução está na pasta temporária local `tmp/revisao_notebook1_20261103_99r2lvq4/verificacao.json`. Essa pasta não integra a entrega.

## Conclusão da conferência

**Nenhum problema bloqueante encontrado nas mudanças examinadas.** O pacote melhora o acesso à primeira entrega: oferece consulta das saídas salvas e reprodução numérica com biblioteca padrão do Python, sem exigir o repositório completo.

A revisão executou o script e as células do notebook reduzido. Não reexecutou o notebook detalhado, não abriu o arquivo em um cliente Jupyter e não realizou novas inferências. A verificação do PDF foi por identidade com o artigo existente, sem nova revisão editorial ou visual.

Os formulários individuais continuam vazios. As novas sínteses técnicas se identificam como preparadas com apoio de IA e não comprovam participação individual. A conferência técnica também não comprova submissão, aprovação docente ou atendimento integral das rubricas.

## Continuidade para 12/11

Usar o [pacote offline](../notebook_1_offline/README.md) como opção de recálculo na apresentação. O notebook detalhado fornece tabelas, gráficos e exemplos para consulta. A demonstração do editor continua sendo uma preparação própria, com cópia de workspace e ensaio no equipamento escolhido.

A narrativa e as métricas dos slides permanecem as mesmas: comparação de configurações pré-treinadas em um documento de desenvolvimento, com referência assistida e oito ressalvas. A ampliação do corpus e o ajuste fino continuam em etapa separada.
