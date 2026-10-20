# Referência assistida do corpo do 269r — 20/10/2026

As 24 linhas foram incorporadas ao editor, com autoria de **Rodolfo Vinícius
Cima Takemoto**, preservação das revisões anteriores e separação entre
reconhecimento bruto, edição publicada e texto adotado na conferência.
Nenhuma função do produto, configuração do reconhecedor ou peso foi alterado.

A revisão final desta consolidação é `20261020T170710_160e8f3f`, filha de
`20261020T170540_d044a4f0`, que incorporou as nove linhas restantes a partir de
`20261019T153953_c011dcd6`. Os snapshots e seus vínculos estão neste pacote.
A segunda gravação preserva as observações anteriores e apresenta a nova
proveniência no painel **Confirmações parciais e escopo**, já existente no editor.

## Critério adotado pelo revisor

O usuário determinou: “VAmos sempre usar o que esta na oficial, na duvida vamos
por ela, essa eu tbm vejo o ao dito”. A decisão e a fonte com SHA-256 estão em
[politica_textual.json](politica_textual.json).

Nas dúvidas, adota-se a edição publicada com registro explícito de apoio editorial.
Essa adoção não transforma sinais duvidosos em confirmações visuais. Leituras
explicitamente confirmadas no manuscrito continuam preservadas: **Eram**, na
linha 14, em lugar de **Heram**; **Com**, na 20; **Como**, na 21. As linhas 1–10
permanecem exatamente iguais às linhas do snapshot anterior, inclusive autoria
e datas originais. A confirmação visual de **ao dito**, na 11, foi acrescentada.

Na linha 22, o texto é **outros que mais**, separado conforme a edição. A
observação de escrita ligada permanece registrada, sem atribuição de erro ao
escriba. Na 24, **Magᵈᵉ** conserva a forma abreviada em conferência; **Magestade**
é seu desenvolvimento na edição e permanece no campo de apoio editorial.
As quebras físicas de linha foram preservadas.

## Estado da referência

Os cinco blocos têm cobertura completa confirmada, e as 24 geometrias estão
validadas. O recorte cobre somente o corpo selecionado do 269r; não inclui
cabeçalho, resumo ou verso. As confirmações estão em
[aprovacoes_blocos.json](aprovacoes_blocos.json).

Há **16 linhas validadas** e **8 pendentes quanto à certeza visual**:

| Linha | Leitura adotada com apoio editorial / dúvida preservada |
| --- | --- |
| 11 | Requererão; sinal superior/final e pontuação |
| 15 | , e ficaram |
| 16 | , e da villa de |
| 17 | ministros; primeira vogal; segmentos intermediários e de Jus |
| 19 | orgente; primeira letra e pontuação |
| 20 | muito Grande detrimento de to |
| 23 | Justissa; dois s |
| 24 | Base Mag e pontuação final; de elevado confirmado |

As linhas 11 e 15 estavam marcadas como validadas no editor anterior, apesar
das ressalvas na conversa. A nova revisão as mantém preenchidas e pendentes
para representar essas ressalvas; seus estados anteriores permanecem no histórico.
Não se exige nova confirmação das coberturas já aprovadas.

Esta é uma **versão congelada para documentação do desenvolvimento assistido**.
Não é uma referência integralmente independente da edição, nem teste reservado.
O validador existente aceita o catálogo e bloqueia a avaliação integral das 24
linhas enquanto as oito ressalvas permanecem. Não foram calculadas novas
métricas, excluídas silenciosamente linhas difíceis ou executadas novas inferências.

## Arquivos e reprodução

- [editor_anterior.json](editor_anterior.json): snapshot anterior preservado.
- [editor_consolidado.json](editor_consolidado.json): snapshot final salvo no editor.
- [conferencia.json](conferencia.json): decisões e histórico por linha, de 11 a 24.
- [texto_adotado.txt](texto_adotado.txt): transcrição adotada, com 24 linhas físicas.
- [linhas_congeladas.jsonl](linhas_congeladas.jsonl): catálogo com os recortes
  arquivados em `recortes/`, independente dos caminhos temporários do editor.
  A edição aponta para a cópia idêntica já publicada em
  `docs/experimentos/traslado_269r_20261016/support/edition.pdf`; os caminhos
  originais estão preservados nos campos terminados em `_no_editor`.
- [predicoes_editor.jsonl](predicoes_editor.jsonl): projeção das predições no editor.
- `predicoes_originais/`: nove arquivos originais de reconhecimento, copiados
  byte a byte. Os quinze anteriores estão no snapshot anterior.
- [mapeamento_predicoes.json](mapeamento_predicoes.json): somente a associação
  dos novos resultados a região e caminho do recorte foi ajustada no editor;
  texto bruto, tokens, tempos, identificação dos pesos e demais campos permanecem iguais.
- [verificacoes.json](verificacoes.json): validação do catálogo, bloqueio de avaliação
  integral e verificações de preservação.
- [inventario.json](inventario.json): SHA-256 dos arquivos deste pacote, exceto o próprio inventário.

Na raiz do projeto, execute:

```powershell
.venv/Scripts/python.exe docs/revisao_humana/traslado_269r/referencia_assistida_20261020/verificar.py
```

O verificador confere os arquivos congelados; futuras revisões do editor não
alteram este retrato. A fonte original do manuscrito e o PDF editorial continuam
nos caminhos de origem, identificados por hash. O material conserva as condições
das fontes; a licença MIT do projeto refere-se ao código.

Antes da publicação, passaram **90 testes Python**, **29 testes JavaScript** e
os verificadores desta referência e da sessão anterior. A suíte Python emitiu
um aviso de depreciação Starlette/AnyIO, sem falha. A CI passa a conferir também
este pacote em seus ambientes existentes. Não houve treino nem nova inferência.

O próximo passo acadêmico está em
[proposta_experimento.md](proposta_experimento.md). Não houve contato com
professores nem confirmação de enquadramento nesta sessão. O usuário informou
que PLN exige dois reconhecedores; a adequação do desenho específico permanece
pendente. Esta entrega é destinada exclusivamente à branch
`codex/refatoracao-piloto`, com histórico aditivo e dúvidas preservadas.
