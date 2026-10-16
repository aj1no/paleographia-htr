# Acervo de Jundiaí: inventário e proposta de mineração

Levantamento de 16/10/2026, a partir da pasta `Transcrições` indicada pelo usuário,
da página oficial e de consultas públicas ao SISMU. Este documento registra uma
avaliação de viabilidade; não representa coleta integral do acervo, treino ou
validação paleográfica. Critérios editoriais encontrados nos PDFs foram tratados
como informação sobre as fontes, sem substituir a política do projeto.

## Resultado da conferência local

A pasta contém **15 arquivos: sete JPEGs e oito PDFs**, organizados em cinco
pastas principais e sete conjuntos documentais candidatos. A comparação SHA-256
encontrou correspondência exata dos 15 arquivos com membros já registrados em
`data/manifests/archive_members.json`. Não há acréscimo de conteúdo binário em
relação à importação preservada; os caminhos legíveis ajudam a identificar as fontes.

O inventário desta consulta está em
[`data/manifests/transcricoes_20261016.json`](../data/manifests/transcricoes_20261016.json).
Ele inclui tamanho, hash, membro de origem, contagem de páginas PDF e vínculos
candidatos aos registros públicos. A equivalência por hash foi verificada entre
arquivos locais; **não foi feita comparação binária com os downloads atuais do SISMU**.

| Conjunto local | Arquivos disponíveis | Natureza da edição | Próxima conferência |
|---|---|---|---|
| Código de Posturas, 1831 | 3 JPEGs + PDF de 8 páginas | Modernizada | Continuar o piloto de 100r; conferir a cobertura parcial |
| Sessão de 25/06/1795 | 1 JPEG + PDF de 4 páginas | Modernizada | Vincular 91r à página 185 do livro digital |
| Pagamento a Thomas Pardo | 2 JPEGs + PDF de 4 páginas | Modernizada | Resolver divergência 1751/1759 no original |
| Carta de José Gomes de Gouveia | 1 JPEG + PDF de 5 páginas | Modernizada | Conferir cobertura de 4r e 4v; não deduzir cobertura pelo nome do JPEG |
| Contrato de Francisco Vieira da Costa e Manoel da Siqueira Gil, 1763 | PDF de 12 páginas | Modernizada, com imagens anexas | Separar texto editorial, transcrição e fac-símiles |
| Contrato de Francisco Vieira da Costa, 1763 | PDF de 6 páginas | Modernizada, com imagens anexas | Separar texto editorial, transcrição e fac-símiles |
| Traslado do Auto de Criação da Vila | Transcrição de 11 páginas + fac-símile de 9 páginas | Identificada como paleográfica | Conferir convenções, autoria, correspondência e cobertura |

As seis edições modernizadas declaram critérios que atualizam grafia e pontuação,
desenvolvem abreviaturas e omitem rasuras. A extração foi conferida nas páginas
de critérios; páginas selecionadas também foram renderizadas e inspecionadas.
A edição paleográfica tem aparência e critérios distintos: não aplicar a ela
automaticamente as regras das outras seis.

Ter sete conjuntos não demonstra sete escribas ou sete grupos independentes.
Os dois contratos compartilham contexto e data; os dois autos pertencem ao mesmo
livro. Dependências precisam ser investigadas antes de definir treino e teste.

## Vínculos encontrados no catálogo

| Registro da edição | Fonte e localização declaradas pelo SISMU |
|---|---|
| [101300 — Código de Posturas](https://jundiai.sismu.app/obra/101300/codigo-de-posturas-de-jundiai-de-1831-que-define-juridicamente-a-repressao-contra-movimentos-de-insurreicoes-de-pessoas-escravizadas) | Sessão de 11/07/1831; edição parcial; registro 02314. Livro de Atas 1829–1833, registro 0010; fólios 100r, 100v, 101r; páginas 203–205 do PDF |
| [101813 — Sessão de 1795](https://jundiai.sismu.app/obra/101813/nomeacao-de-cinco-capitaes-de-mato-transcricao-da-sessao-da-camara-municipal-de-jundiai-do-25-de-junho-de-1795) | Registro 02332; livro de Atas 1787–1795, registro 0006; 91r; página 185 do PDF |
| [102151 — Pagamento](https://jundiai.sismu.app/obra/102151/pagamento-realizado-ao-capitao-do-mato-thomas-pardo-por-ter-posto-a-cabeca-de-um-negro-quilombola-na-estrada-real-que-vai-para-sao-paulo-27-de-novembro-de-1751) | Registro 02398; Autos de Diligências e Mandados 1742–1783, registro 0146; 113v e 114r; páginas 317–318 do PDF |
| [102967 — Carta](https://jundiai.sismu.app/obra/102967/registro-oficial-da-carta-enviada-por-jose-gomes-de-gouveia-nos-anais-da-camara-com-sugestoes-e-metodos-para-eliminar-movimentos-de-resistencia-pela-liberdade-de-africanos-afro-brasileiros-e-povos-originarios-em-1767) | Registro 02415; carta de 23/12/1767; livro 0146; 4r e 4v; páginas 11–12 do PDF |
| [101489 — Contrato com Siqueira Gil](https://jundiai.sismu.app/obra/101489/contrato-para-exploracao-de-minas-auriferas-em-territorios-jundiaienses-em-1763-o-texto-contem-descricoes-sobre-africanos-afro-brasileiros-povos-originarios-e-quilombos) | Registro 02317; Cartório Olgado; Livro 12, folhas 278 e 279; 27/08/1763 |
| [101494 — Contrato de Vieira da Costa](https://jundiai.sismu.app/obra/101494/contrato-para-exploracao-de-minas-auriferas-em-territorios-jundiaienses-em-1763-o-texto-contem-descricoes-sobre-africanos-afro-brasileiros-e-povos-originarios) | Registro 02321; Cartório Olgado; Livro 13, folhas 10 e 11; 27/08/1763 |
| [102202 — Transcrição paleográfica](https://jundiai.sismu.app/obra/102202/transcricao-paleografica-do-traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro) | Registro 02294; autoria atribuída a Ana Caroline Carvalho Miranda; Torre do Tombo, Papéis do Brasil, Códice 4, folhas 269–273; PT/TT/PBR/0004/026 |
| [102201 — Fac-símile do Traslado](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro) | Registro 02293; cópia manuscrita produzida em 1767, referente ao acontecimento de 14/12/1656 |

Os livros completos de Atas foram localizados nos registros
[91829 — 1829–1833](https://jundiai.sismu.app/obra/91829/atas-da-camara-municipal-1829-a-1833)
e [91824 — 1787–1795](https://jundiai.sismu.app/obra/91824/atas-da-camara-municipal-1787-a-1795).
As correspondências acima são declarações de catálogo, a confirmar nos pixels
antes de validar linhas. O identificador na URL da obra difere do número de
registro arquivístico; guardar ambos.

### Pendências concretas de qualidade dos metadados

- **Pagamento:** o título do registro e a pasta local dizem 1751; o campo Data
  do mesmo registro e o cabeçalho da edição dizem 27/11/1759. Preservar as duas
  alegações com suas fontes. A data documental continua pendente de conferência.
- **Traslado:** registrar separadamente data do acontecimento (1656) e data da
  cópia manuscrita (1767). Para estudar escrita, a data da cópia é a relevante.
- **Transcrição do Traslado:** o catálogo declara 12 páginas; o PDF local tem
  11 páginas físicas. Isso não demonstra omissão textual. Conferir versão,
  paginação e final do documento antes de afirmar cobertura integral.
- **Carta:** o catálogo descreve 4r e 4v, enquanto há um JPEG com nome genérico
  `Fólio 4.JPG`. Inspecionar o conteúdo antes de declarar lado ausente.
- **Sobreposição de coleções:** o catálogo informa que alguns livros também
  aparecem em outra coleção como A/B. Coleção, URL e intervalo cronológico não
  bastam para declarar documentos independentes ou ausência de duplicação.

## Como cada coleção ajuda o projeto

| Coleção | Uso proposto | Prioridade |
|---|---|---|
| Fundos de Pesquisa | Encontrar edições, transcrições e pares de texto/imagem | Primeira: localizar e classificar referências |
| Imperial | Recuperar livro do piloto de 1831 e amostrar sessões relacionadas | Primeira: manter continuidade com a revisão existente |
| Colonial | Ampliar variedade de manuscritos, atas e autos; contextualizar as edições locais | Segunda: expansão controlada |
| Republicana | Investigar outros períodos, formas de escrita e tipos documentais | Posterior: avaliar generalização separadamente |
| Tribunal de Justiça | Explorar processos, terras, dívidas e heranças | Posterior: corpus próprio, com amostragem e referência específicas |
| Hemeroteca | Pesquisa em impressos e contexto histórico; comparar OCR já disponível | Linha de trabalho separada do reconhecimento de manuscritos |

As seis coleções foram abertas no navegador. Foram inspecionadas as primeiras
páginas e, nos Fundos, os filtros de Atas, Autos e Contratos. Essas três
subcoleções mostraram dois itens cada nesta consulta; isso não é contagem de
todas as transcrições existentes no portal. O Tribunal exibiu processos e
paginação; não mostrou o mesmo seletor de subcoleção das outras páginas.
A [página oficial](https://cultura.jundiai.sp.gov.br/espacos-culturais/arquivo-historico-professora-maria-angela-borges-salvadori/acervo-digital/)
informa consulta/download e pesquisa OCR na Hemeroteca. OCR de impressos não
constitui referência validada para o reconhecimento de manuscritos.

## Duas frentes de mineração

Primeira amostra realizada: [comparação do fólio 269 reto do Traslado](revisao_humana/traslado_269r/comparacao.md).
O reto corresponde à página 1 e ao início da página 2 da transcrição; foram
preparadas 24 linhas candidatas do corpo. A expansão editorial de uma
abreviatura impede copiar esse texto diretamente como referência diplomática.
Nenhuma linha foi validada nesta comparação assistida.

**Pesquisa textual:** os textos das edições permitem começar um corpus de
consulta sobre pessoas, lugares, datas, cargos, valores, relações e assuntos.
Toda ocorrência deve conservar obra, página, trecho e natureza do texto
(descrição catalográfica, edição modernizada ou transcrição paleográfica).
Nomes modernizados e leituras editoriais inferidas exigem marcação própria.
Uma descrição do catálogo não equivale a uma ocorrência no manuscrito.

**Reconhecimento de escrita:** construir pares de imagem e texto na mesma
linha/região, com grafia e abreviaturas conferidas. A transcrição do Traslado é
uma candidata promissora, mas o rótulo “paleográfica” não comprova compatibilidade
com a política atual. Conferir expansões, sinais, quebras, lacunas e cobertura
antes de importá-la como referência. As seis modernizações servem como apoio
de leitura; nenhuma foi promovida a alvo de treino ou avaliação.

A extração de texto dos PDFs modernizados frequentemente junta palavras sem
espaços. Não corrigir isso por inserção arbitrária de espaços nem gerar
automaticamente pares de linha a partir desse resultado. Confrontar texto
extraído com a página renderizada, preservar a extração bruta e fazer a
separação por regiões editoriais. Páginas sem camada textual podem conter
fac-símiles; ausência de texto extraível não significa página vazia.

## Sequência sugerida para implementação

1. **Fechar a origem dos sete conjuntos.** Revisar os vínculos candidatos,
   guardar identificadores, fonte das datas e numeração de página/fólio, autoria,
   versão, hashes e cobertura. Resolver as divergências acima.
2. **Manter o piloto de 1831 e abrir uma amostra do Traslado.** Terminar o trecho
   já em revisão no 100r. No Traslado, selecionar uma região contínua de uma
   página, comparar manuscrito e edição e decidir compatibilidade editorial.
3. **Catalogar antes de baixar em escala.** Fazer uma coleta pequena de fichas
   públicas e seus links, com cache, baixa concorrência, retomada e registro de
   falhas. O portal expõe links de PDF; não foi estabelecida uma API pública
   documentada para coleta em lote. Dimensionar o download depois da seleção.
4. **Produzir o corpus textual com proveniência.** Separar paratexto e conteúdo,
   manter as versões e testar a extração em amostras conferidas. Uma busca por
   nomes e lugares com ligação ao trecho pode ser uma primeira entrega útil,
   mesmo enquanto a referência para HTR cresce.
5. **Ampliar a referência humana e definir os grupos.** Agrupar derivados e
   duplicatas, investigar livros, sessões, contratos e mãos; só então fixar
   treino/validação/teste e retomar a comparação prevista no projeto.

Campos adicionais de um futuro catálogo de coleta: URL da obra, número de
registro, fundo/coleção/série, instituição de guarda, referência arquivística,
datas por função, URL do anexo observada, data da consulta, hash do download,
tipo de edição, créditos, condições de uso e estado da revisão. Esse catálogo
deve ser mapeado ao esquema atual, sem alterar implicitamente seus estados.

O acesso para consulta e download descrito pelo portal não estabelece por si só
licença para redistribuir cada imagem ou edição; manter as condições por fonte
quando houver publicação de corpus.

## O que foi efetivamente realizado

Inventário e hashes dos 15 arquivos locais; leitura das oito estruturas PDF;
inspeção dos critérios das seis modernizações e da abertura da transcrição
paleográfica; renderização e inspeção de cinco páginas selecionadas; navegação
nas seis coleções; consulta às fichas individuais listadas e aos dois livros de
Atas. Não houve download integral dos livros, coleta em massa, alteração de
anotações humanas, envio das transcrições a serviços externos ou novo treino.
