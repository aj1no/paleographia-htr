# PaleographIA — continuidade após a consolidação e a retificação para Juiz

Data: 28/10/2026.
Base da análise: commit `3c94ff62b270dbaddf0be7047aa90e1384e178d0`.

## Pedido ao Codex

Dê continuidade à documentação e à curadoria do bloco de oito linhas da sessão da Câmara de Jundiaí de 1795, seguindo este parecer.

Antes de editar, leia as instruções locais aplicáveis e compare o estado atual do repositório e do editor com o commit de referência. Preserve alterações posteriores e não reimporte catálogos históricos sobre o workspace atual.

Nesta etapa, aplique os ajustes documentais indicados e prepare a conferência textual das pendências reais. As geometrias, a sequência e a correção humana para **Juiz** já foram confirmadas: não solicitar novamente essas decisões.

Não há nova leitura humana neste documento. As sugestões paleográficas da IA são hipóteses assistidas pela edição, sem autorização para preencher lacunas ou aprovar transcrições. Não iniciar reconhecimento, treinamento ou cálculo de métricas para resolver esta tarefa.

## Estado confirmado no commit de referência

| Item | Estado |
| --- | --- |
| Revisão após a consolidação geométrica | `20261028T160355_969eab97` |
| Revisão após a retificação humana | `20261028T162318_8769604b` |
| Geometrias | 8 com `geometry_status=validated` |
| Transcrições | 8 com `review_status=pending_review` |
| Tipo da referência nas linhas | `reference_kind=unknown` |
| Pares elegíveis para treinamento | 0 |
| Correspondência documental | Pendente |
| Cobertura | Região do bloco, pendente e com `complete=false` |
| Linha 4 | Rascunho parcial, com `exclusion_reason` explícito |
| Novas execuções nesta consolidação/retificação | Sem OCR, treinamento ou cálculo de métricas |

O rascunho atual da linha 4 é:

```text
de São Paulo, em casas de morada de Juiz
```

A observação 020 corrige somente **Luiz → Juiz**. Não aprova a preposição, a vírgula ou a continuação. **Presidente** permanece no apoio editorial, sem incorporação automática ao alvo diplomático.

## Evidências principais

- [Estado atual e retificação](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/retificacao_juiz_20261028/README.md).
- [Observação humana 020](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/retificacao_juiz_20261028/observacao_020_linha04_retificacao_Juiz.json).
- [Catálogo atual](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/retificacao_juiz_20261028/catalogo_depois.json).
- [Linhas da exportação atual](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/retificacao_juiz_20261028/exportacao_editor/lines.jsonl).
- [Verificação da retificação](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/retificacao_juiz_20261028/verificacao_retificacao.json).
- [Registro da aplicação geométrica](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/consolidacao_20261028/registro_consolidacao.json).
- [Índice geral da revisão](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/revisao_humana/sessao_1795/README.md).
- [Recortes e edição modernizada](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/dataset_expansion_20261023/curation_sessao_1795_bloco01/README.md).
- [Política de transcrição](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/transcription_policy.md).
- [Protocolo experimental](https://github.com/aj1no/paleographia-htr/blob/3c94ff6/docs/evaluation_protocol.md).

## Achados da análise crítica

### 1. Consolidação geométrica consistente

As confirmações humanas foram associadas por ID, fonte, hash do recorte e caixa. Os oito recibos formam uma cadeia de revisões e preservam as datas das declarações humanas.

Na comparação dos snapshots da consolidação, mudaram somente `geometry_status`, `reviewed_at` e, na linha 4, `exclusion_reason`. Textos, caixas, ordem, páginas e predições foram preservados.

Rodolfo Vinicius Cima Takemoto aparece como revisor das decisões humanas. Codex aparece como agente que as aplicou sob autorização registrada. Não foi encontrada aprovação textual indevida.

### 2. Retificação consistente entre catálogo e exportação

Na retificação, somente a linha 4 mudou, nos campos `text_diplomatic`, `reviewed_at` e `exclusion_reason`. As outras sete linhas, páginas e predições permaneceram iguais.

As linhas exportadas coincidem integralmente com o snapshot atual. Os manifests no ZIP coincidem com os publicados separadamente. A parcialidade acompanha a exportação e a continuação não foi acrescentada.

A análise também comparou os 52 arquivos históricos relacionados em `verificacao_retificacao.json` com o commit anterior à retificação: todos permaneceram idênticos. Os hashes e dimensões dos oito recortes foram conferidos.

### 3. Ajuste necessário no índice geral

Na seção **Preservação** de `docs/revisao_humana/sessao_1795/README.md`, a expressão:

> o snapshot final conserva o estado textual atual

fica ambígua após a observação 020. Ajustar o trecho para identificar explicitamente a rodada histórica, por exemplo:

> O snapshot inicial de 28/10 conserva o estado anterior às releituras das linhas 3 e 4. O snapshot final daquela rodada conserva as leituras anteriores à observação 020. O estado atual após a retificação para Juiz está em retificacao_juiz_20261028/catalogo_depois.json.

Usar links relativos no arquivo. Manter o resumo inicial, que já aponta corretamente para Juiz.

Não substituir Luiz em snapshots, observações, recibos ou pareceres antigos. Nesses materiais, a palavra descreve o estado de sua própria data.

### 4. Preparação candidata e metadados herdados precisam de contexto

O índice em `docs/dataset_expansion_20261023/curation_sessao_1795_bloco01/README.md` ainda descreve alvos vazios e geometria pendente. Isso corresponde à preparação candidata de 23/10.

Acrescentar uma nota curta no início, identificando-o como retrato da preparação e apontando para a revisão atual. Preservar as descrições e manifests candidatos como histórico. Não orientar uma nova importação para recuperar o estado atual.

Metadados auxiliares como `segmentation_method=manual_candidate_not_human_approved` e `alignment_status=candidate_pending_human_confirmation` foram herdados dessa preparação. Sua presença deve ser contextualizada na documentação; não equivale a rebaixar o `geometry_status=validated`. Não mudar campos de proveniência ou inventar novos estados apenas para uniformizar a aparência do catálogo.

### 5. Significado de reviewed_at

O esquema compartilha `reviewed_at` entre revisões textuais e geométricas. O serviço atualiza esse campo quando qualquer um desses estados está validado.

Assim:

- Os carimbos da consolidação registram a aplicação geométrica, não uma aprovação textual.
- O novo carimbo da linha 4 na retificação não significa nova confirmação de seus limites.
- As datas das declarações humanas continuam nas observações e nos recibos.
- A interpretação deve consultar `geometry_status`, `review_status`, a ação e o histórico.

Manter essa explicação explícita. Não alterar o esquema ou apagar os carimbos para resolver a ambiguidade.

### 6. Limites dos relatórios de validação

A verificação publicada informa catálogo válido, avaliação bloqueada e treinamento bloqueado. Os erros por linha apontam correspondência documental pendente.

No validador existente, essa checagem acontece antes das condições de aprovação textual. Ao encontrar o primeiro erro da linha, ele não enumera necessariamente todos os bloqueios restantes.

Portanto, não descrever os erros atuais como lista exaustiva de tudo que falta. Após resolver uma etapa, executar novamente os validadores para verificar as condições seguintes. A correspondência documental, isoladamente, não libera os exemplos.

## Conferência textual que permanece aberta

As observações abaixo decorrem da inspeção assistida da IA. Não são novas transcrições aprovadas.

| Ponto | Situação atual | Dúvida restante | Ação recomendada |
| --- | --- | --- | --- |
| Linha 4: Juiz | Correção humana recebida e aplicada; compatível com os traços. | A decisão não resolve as palavras vizinhas. | Preservar Juiz sem nova solicitação dessa mesma decisão. |
| Linha 4: de/do | O rascunho mantém de. | A pequena forma arredondada anterior a Juiz favorece provisoriamente o; a ligação entre letras dificulta isolá-la. | Conferir a vogal especificamente. Não alterar para do pela plausibilidade da frase. |
| Linha 4: continuação | Há palavra visível após Juiz, ainda fora do alvo. | Inicial alta com laço e sequência de traços são compatíveis com Presidente; a grafia exata, inclusive s/z, permanece aberta. | Comparar letras da mesma mão. Não importar automaticamente a forma modernizada. |
| Linha 4: pontuação | A vírgula do rascunho permanece. | Sua presença gráfica não foi aprovada pela retificação. | Conferir separadamente e preservar o caráter pendente. |
| Linha 1 | Rascunho preenchido; dias foi declarado pelo revisor. | Aos/aos e eventual abreviatura no grupo compacto correspondente a dias. | Distinguir leitura lexical de representação dos sinais. |
| Linha 2 | annos e Villa são compatíveis com as duplicações visíveis. | Forma final correspondente a Nossa, possivelmente compacta ou abreviada. | Conferir a representação literal sem expandir automaticamente. |
| Linha 3 | jundiahy permanece como leitura humana. | Inicial alongada e escolhas de caixa. | Conferir a caixa sem modernizar para Jundiaí. |
| Linha 5 | achavão é compatível com a sequência visível. | Forma e posição do til; vírgula após Prado. | Registrar decisões de diacrítico e pontuação separadamente da palavra. |
| Linha 6 | officiaes, Camara, acto e Vereança são compatíveis. | Cedilha, caixa e pontuação. | Preservar grafias históricas e conferir os sinais restantes. |
| Linhas 6–7 | trat- / ando preserva a divisão física; hífen já confirmado pelo usuário. | A aparência exata do sinal não autoriza modernizar ou unir as linhas. | Manter trat- e ando em recortes distintos. Não repetir a aprovação já recebida. |
| Linha 7 | commum permanece no rascunho. | Contagem das consoantes centrais em uma sequência de hastes e ligações. | Comparar m e suas conexões em exemplos da mesma mão. |
| Linha 8 | O tratamento correspondente a Senhor aparenta abreviação. | Representação de huma, final de abriu/abrio e letras/diacrítico de José. | Conferir os sinais e registrar convenção diplomática quando necessária. Expansões ficam no apoio editorial. |

A quarta linha deve permanecer parcial se a reprodução não permitir decisão. Não completar por contexto, não inventar sobrenome e não remover `exclusion_reason` apenas para obter aprovação do validador.

## Identificação, cobertura e eventual treinamento

As confirmações de limites e sequência abrangem o bloco apresentado. Não comprovam o lado do fólio ou a identificação documental completa. O numeral 91 foi relatado; a página tem texto adicional fora das oito linhas.

Antes de considerar pares elegíveis:

1. Consolidar identificação e correspondência documental no fluxo existente, com autoria e evidências.
2. Resolver as leituras ou aplicar uma convenção humana explícita compatível com a política. Manter pendentes os trechos não resolvidos.
3. Aprovar formalmente cada transcrição somente quando os requisitos forem atendidos, incluindo `reference_kind`, revisor e proveniência.
4. Registrar o escopo de cobertura exigido pelo protocolo. Uma região textual completa não pode ocultar a continuação ausente da linha 4.
5. Conferir as condições de uso dos manuscritos e da edição. A licença do código não licencia automaticamente as fontes.
6. Planejar partições por documento, mantendo fólios, reproduções e derivados no mesmo grupo. O bloco de um único documento não estabelece sozinho treino, validação e teste independentes.
7. Executar os validadores existentes para catálogo e, quando houver um conjunto candidato adequado, avaliação e treinamento. Usar o desenho completo das partições, sem forçar todas as divisões dentro dessas oito linhas.

Não declarar as outras sete linhas aptas por ausência da dúvida principal da quarta. Não apresentar um subconjunto como se cobrisse o bloco inteiro. Exclusões e subconjuntos precisam ter escopo e contagens explícitos.

## Trabalho a executar agora

1. Conferir HEAD, editor e instruções locais, preservando mudanças posteriores à base.
2. Registrar este parecer como análise assistida por IA, vinculada ao commit de referência.
3. Corrigir a expressão ambígua do índice geral e acrescentar contexto histórico ao índice de preparação candidata.
4. Manter o catálogo atual e as aprovações existentes. Alterações textuais adicionais dependem de novas decisões humanas sobre os pontos ainda abertos.
5. Preparar uma conferência objetiva das pendências textuais, com os recortes existentes e sem repetir perguntas já respondidas.
6. Se forem necessários novos estudos visuais, usar as melhores reproduções já disponíveis e documentar sua origem. Ampliação não recupera informação ausente.
7. Executar verificações apropriadas às alterações realizadas. Para ajustes somente documentais, conferir links e consistência de referências; não repetir testes de treinamento ou reconhecimento.
8. Apresentar relatório com arquivos alterados, verificações executadas, pendências e estados finais, sem confundir tarefa preparada com revisão humana realizada.

## Critérios de conclusão

- Juiz permanece no estado atual; Luiz aparece somente como leitura histórica ou descrição da retificação.
- A quarta linha continua parcial, com ressalva preservada na exportação.
- Oito geometrias e a sequência anterior permanecem aproveitadas.
- Nenhuma nova aprovação textual foi criada a partir deste parecer.
- Índices distinguem preparação, rodadas históricas e catálogo atual.
- `reviewed_at` está explicado sem equivaler a aprovação textual.
- Nenhuma afirmação de cobertura da página inteira foi introduzida.
- Fontes, recortes, predições e registros históricos permanecem preservados.
- Os bloqueios de elegibilidade continuam em vigor enquanto faltarem os requisitos.
- Não há mudança de funcionalidade ou nova frente experimental nesta etapa.

## Limitações da análise encaminhada

Foram acessados os materiais publicados, os oito recortes, a página marcada e as duas ampliações contextuais da linha 4. A análise já conhecia a edição e as leituras humanas.

Não houve acesso aos arquivos brutos externos ao Git nem ao editor local em funcionamento. A correspondência entre snapshots e exportações foi conferida; a correspondência com um editor aberto no computador do usuário não foi verificada diretamente.

O validador completo dependente das fontes locais não foi reexecutado pelo ChatGPT. Foram examinados seu código e os relatórios publicados. As verificações próprias desta análise incluíram comparação dos snapshots e exportações, arquivos históricos, cadeia de recibos e hashes dos recortes. Não houve novo OCR, treino ou cálculo de métricas.

