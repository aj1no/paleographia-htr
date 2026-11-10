# Curadoria assistida dos fólios novos para treino (10/11/2026)

Para refinar o reconhecedor, a equipe vai ler e validar fólios que ainda não entraram em nenhum
treino supervisionado. As linhas validadas serão os rótulos de um **ajustado C** (Traslado +
linhas novas), comparado com A e B na validação de 1795.

## Fólios

| Documento | Fólios | Uso anterior |
| --- | --- | --- |
| Código de Posturas de Jundiaí, 1831 | 100r, 100v, 101r | Piloto de segmentação (sem texto validado) e demonstração |
| Carta de José Gomes de Gouveia, 1767 | fólio 4 | Três linhas na avaliação do modernizador (não do HTR) |
| Contrato do livro 13, 1763 (Cartório Olgado) | páginas 5 e 6 do PDF da edição | Só no pré-treino não supervisionado do modelo do zero |

Os arquivos da pasta `Transcrições` enviada pelo usuário em 10/11 são os mesmos do corpus v0.2,
byte a byte (SHA-256 conferido). **Não entram aqui**, e o script recusa: o teste reservado
(pagamento a Thomas Pardo, contrato do livro 12) e a validação de 1795. O Traslado já é o treino
de A e B.

## Como foi montada

[`scripts/preparar_novos_folios.py`](../../../scripts/preparar_novos_folios.py) confere o SHA-256 de cada
imagem, desenha as linhas com o blla do Kraken (juntando os pedaços cortados) e pede a leitura do
**ajustado B**, que aparece como sugestão. Configuração: [`configs/novos_folios.toml`](../../../configs/novos_folios.toml).
Workspace: `data/workspace_novos_folios/`, fora do Git, como os demais.

## Como revisar

1. Abrir `iniciar_curadoria_novos_folios.bat` (ou `.venv/Scripts/python.exe -m paleographia serve --config configs/novos_folios.toml --port 8020`) e ir ao **Modo leitura**.
2. Ler cada linha **na imagem** e corrigir a sugestão até ficar diplomática: como está escrito, sem
   modernizar nem desenvolver abreviaturas, nas mesmas convenções do 269r e de 1795.
3. Validar só o que foi lido de fato. O que não der para ler fica como **Ilegível**. Recortes ruins
   podem ser ajustados, juntados (**Juntar linhas**) ou rejeitados.
4. A edição modernizada do Arquivo pode ajudar numa dúvida, **depois** de olhar a imagem, mas
   não substitui a leitura.

**Ressalva a declarar:** a leitura é assistida. O revisor vê a sugestão do B antes de corrigir, e
isso pode puxar a leitura para o que o modelo propôs. Para rótulo de treino isso é aceitável; para
teste não seria (por isso o teste reservado foi lido às cegas).

## Antes de treinar o C

- Só linhas com `review_status = validated`, revisor identificado e sem motivo de exclusão.
- Conferir que nenhum trecho do contrato do livro 13 repete texto do contrato do livro 12 (teste
  reservado). O README do teste pede essa verificação, porque os dois contratos são do mesmo
  cartório e da mesma data. **Primeira conferência (10/11), nas duas edições:** fora as páginas de
  advertência, normas e créditos, que são iguais, só se repetem fórmulas curtas: "registro de uma
  petição", "ao qual me reporto e vai sem coisa que", "mandou aqui lançar vila de Jundiaí vinte
  sete de agosto de mil", "setecentos e sessenta e três anos e eu". Regra para o treino: sai do C
  toda linha do livro 13 que tenha uma sequência de 6 palavras em comum com a referência do livro 12.
- A validação continua sendo as 7 linhas de 1795, e o teste reservado só roda **uma vez** para o C.
