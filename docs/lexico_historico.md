# Consulta lexical histórica

Entrega de 19/10/2026, versão **2026-10-19.1**, na branch
`codex/refatoracao-piloto`. A consulta auxilia uma decisão humana: não executa
HTR, não faz pós-correção automática e não integra LLM.

## Uso no editor

1. Abra uma linha e expanda **Vocabulário histórico e fontes**.
2. Selecione uma palavra ou trecho na transcrição diplomática, ou digite a
   consulta no campo do painel. É possível digitar uma palavra da saída bruta
   exibida no editor. A seleção da transcrição tem precedência sobre o campo.
3. Escolha o repertório e clique em **Consultar vocabulário histórico**.
4. Confira forma, fonte, localizador, período, evidência e condições de uso.
   Uma atestação do acervo não contém necessariamente uma definição.
5. Aplique somente se a imagem sustentar a leitura. A aplicação afeta o trecho
   selecionado ou sua única ocorrência literal na linha. Em texto vazio, o
   botão permite inserir somente o candidato consultado. Havendo ocorrências
   repetidas, selecione explicitamente uma delas e consulte novamente.
6. Confira o rascunho e salve pelo fluxo normal. A alteração desmarca a
   conferência do texto; não aprova geometria, cobertura ou referência.

Consultas não salvam nada. Aplicações ficam no rascunho, inclusive ao navegar
entre linhas e páginas. Texto alterado depois da consulta exige nova consulta.
Respostas de outra linha e resultados antigos não podem substituir o texto.
Conflitos 409, erros de validação e falhas de rede conservam o rascunho para
reconciliação. O histórico anterior não é substituído.

O salvamento registra `lexical_assistance` como eventos anexados à linha:
versão e SHA-256 do léxico, IDs de candidato e entradas, consulta, repertório,
critério, distância, trecho anterior/posterior, posições Unicode e horário do
servidor. O servidor revalida cada nova aplicação; versões divergentes exigem
nova consulta. Eventos já salvos permanecem preservados mesmo se o léxico
ficar indisponível. A revisão manual continua funcionando sem a base.

## Conjunto documental e cobertura

[Catálogo](../data/lexicon/sources.json), [entradas](../data/lexicon/entries.jsonl)
e [relatório de cobertura e consultas reproduzíveis](../data/lexicon/coverage.json)
são arquivos separados. São **21 registros: três de dicionário e 18 atestações
do acervo**. Não há entrada indígena importada nesta versão.

| Fonte | Conferência realizada | Limites |
| --- | --- | --- |
| [Bluteau, vol. 1, 1712](https://digital.bbm.usp.br/handle/bbm/5446) | `ANNO`, p. impressa 385, PDF físico 493 | Um verbete, conferido no fac-símile |
| [Bluteau, vol. 4, 1713](https://digital.bbm.usp.br/handle/bbm/5445) | `FREGUEZ` e `FREGUEZIA`, p. impressa 206, PDF físico 222 | Dois verbetes, conferidos no fac-símile |
| [Morais 1789, A–K](https://digital.bbm.usp.br/handle/bbm/5412) e [L–Z](https://digital.bbm.usp.br/handle/bbm/5413) | Catálogo e volumes localizados | Nenhum verbete conferido/importado; publicação posterior a 1656 e 1767 |
| [Leite, 2013](https://tupi.fflch.usp.br/sites/tupi.fflch.usp.br/files/A%20lingua%20geral%20paulista.pdf) | Resumo, páginas vii–viii (PDF 7–8), para delimitação linguística | Vocabulário publicado em 1936 com fontes heterogêneas, em parte LGP oitocentista; nenhuma entrada importada |
| [VLB, ficha CEDOCH](https://cedoch.fflch.usp.br/ficha004) | Identificação bibliográfica, datas e condições do banco | Português–tupi, edição Ayrosa 1938; datas/autoria discutidas na fonte. Sem importação de verbetes ou PDFs |
| [Revisão humana 269r](revisao_humana/traslado_269r/sessao_20261016/README.md) | 18 formas literais das linhas 1–10 validadas | Proveniência por linha/revisor/revisão; sem novas validações humanas |

Os dois [fac-símiles publicados](lexico_evidencias/) têm hashes individuais
nas entradas. O hash do PDF original é outro campo; os PDFs integrais não são
incluídos. Os registros BBM indicam domínio público para as obras de Bluteau.
As notas de significado são breves paráfrases próprias, não transcrições
extensas de obras modernas. Créditos e alcance das condições de cada fonte
estão no catálogo. A licença MIT do código não licencia materiais externos.

As atestações do acervo são `Anno`, `do`, `Nacimento`, `Jezus`, `sincoenta`,
`annos`, `Hera`, `Freguezia`, `Jundiahy`, `Tabelião`, `Capitão`, `mõr`,
`ouvidor`, `Capitania`, `Sam viçente`, `Miguel de Cabedo`, `vasconçellos` e
`Hum`. Mantêm a grafia, o revisor e a data registrados na sessão original.
Nomes sem identificação etimológica permanecem com idioma não determinado.
A extração documental do agente não constitui nova revisão paleográfica humana.

`Anno` e `Freguezia` têm correspondentes de dicionário com caixa diferente.
`Nacimento`, `Jezus`, `Jundiahy`, `sincoenta` e `mõr` estão atestados no acervo,
mas continuam **sem conferência nos dicionários**. `Sundiahy` não foi localizado
no lote curado; pode receber `Jundiahy` por distância 1. Isso não representa
uma busca exaustiva nem prova ausência na língua. Repertórios indígenas
continuam aguardando exame individual de fontes e atribuições.

Português histórico, vocabulário do acervo e repertórios indígenas têm
identidades separadas. Os rótulos internos não são códigos ISO. O ato descrito
como 1656, o cabeçalho da cópia indicando 1767 (ainda sem validação integral),
a publicação de um dicionário e a revisão de 2026 são datas distintas.

## Regras determinísticas

Consulta explícita de 1–80 caracteres, até oito candidatos, nesta ordem:
forma exata em NFC, diferença de caixa, índice sem acentos, distância de edição
e separação de palavras. A forma armazenada nunca é normalizada para grafia
moderna. Diferenças de caixa/acentos são explicadas na interface.

A distância de Levenshtein usa comparação sem distinção de caixa. Para busca
aproximada, a consulta precisa de quatro caracteres; admite uma edição até
sete caracteres e duas a partir de oito, com razão máxima de 25% do maior
comprimento. Distância ordena candidatos; não é probabilidade ou confiança.
Empates são ordenados por forma e ID. Não há substituições globais de
`f/s`, `u/v` ou `i/j`.

A separação explícita aceita consultas sem espaços de até 40 caracteres,
duas ou três palavras atestadas, cada uma com pelo menos dois caracteres;
gera no máximo oito propostas. Sua distância exibida conta os espaços
inseridos; diferenças de caixa conservam as formas das entradas. Por exemplo,
no repertório do acervo `Annodo` produz `Anno do`; `Sundiahy` produz `Jundiahy`.
Não existem exceções codificadas para esses exemplos. Nenhuma regra recompõe
automaticamente `ca / torze`, `Deste / rro` ou `abai / xo` entre linhas físicas.

Entradas pendentes não participam da consulta. Entradas com origem, página,
localizador, data ou hash obrigatório inválido tornam a base indisponível,
com mensagem em português e edição manual preservada. Expansões de
abreviaturas, quando documentadas, são apenas anotações; a aplicação conserva
a forma atestada. Esta versão não contém expansões novas.

## Manutenção e experimento

Uma ampliação exige página conferida, condições de uso, temporalidade,
responsável/data e versão nova do léxico. `source_file`/`source_sha256` ligam
arquivos locais quando disponíveis; `evidence_file`/`evidence_sha256` ligam
fac-símiles publicados. O fingerprint é SHA-256 de `sources.json`, byte nulo,
`entries.jsonl`, em UTF-8/LF. `coverage.json` documenta o lote, sem alterar sua
identidade de consulta. Mantenha as regras de LF no Git.

O [protocolo de comparação](protocolo_apoio_lexical.md) trata a avaliação
automática como etapa futura. Nenhuma métrica lexical foi calculada. As cinco
linhas do diagnóstico e as linhas 6–10 já foram usadas com assistência;
as 18 atestações do acervo têm papel de desenvolvimento e pertencem ao mesmo
grupo documental. Não podem constituir informação independente para avaliar
a generalização nesse grupo.
