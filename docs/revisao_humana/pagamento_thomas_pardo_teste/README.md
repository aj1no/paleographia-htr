# Grupo de teste reservado: pagamento a Thomas Pardo (decisão de 05/11/2026)

Registro aditivo. Não altera a [partição candidata de 04/11](../../entregas/continuidade_20261103/particoes_ppocrv6_20261104/README.md),
o catálogo `data/manifests/corpus_expandido_v02/` nem outros pacotes congelados. As alterações
de papel abaixo valem a partir desta data.

## Decisão

Em 05/11/2026, o solicitante escolheu o **mandado de pagamento a Thomas Pardo** como grupo de
**teste final reservado** (opção A do levantamento). Nenhum outro documento do corpus v0.2 tem
pixels sem nenhum uso anterior:

| Documento | Livro de origem | Uso anterior |
| --- | --- | --- |
| Traslado 269r | Torre do Tombo, códice 4 | Métricas de desenvolvimento, treino e pré-treino VGSL |
| Sessão de 1795 | Atas 1787–1795 | Pares revisados, avaliação VGSL |
| Posturas de 1831 | Atas 1829–1833 | Piloto do editor, predições TrOCR, repertório |
| Contrato livro 13, 1763 | Cartório Olgado | Pré-treino VGSL, exploração de imagem |
| Contrato livro 12, 1763 | Cartório Olgado | Nenhum, mas fica no mesmo grupo do livro 13 |
| Carta de 1767 | Livro 0146 | Notebook 2, avaliação VGSL |
| **Pagamento a Thomas Pardo** | **Livro 0146** | **Nenhum** |

**Até 05/11/2026, nenhuma inferência, treino ou ajuste de parâmetro usou estas imagens.**

## Partição proposta a partir de 05/11

| Papel | Documento | Pares validados hoje | Observação |
| --- | --- | ---: | --- |
| Treino | Traslado 269r | 16 | As 94 linhas de 1831, depois de revisadas, também podem entrar no treino |
| Validação | Sessão de 1795 | 7 | Seleção de checkpoint e parada |
| **Teste reservado** | **Pagamento a Thomas Pardo, 113v e 114r** | 0 | Referência a produzir neste workspace |
| Exploratório, fora do treino | Carta de 1767 | 3 | **Sai do treino** proposto em 04/11, porque pertence ao mesmo livro 0146 do teste |
| Exploratório | Contratos de 1763, livros 12 e 13 | 0 | Sem mudança |

O treino passa de 19 para 16 pares. A troca evita que o modelo veja, no treino, outra peça do
mesmo livro avaliado no teste.

## Ressalvas a declarar em qualquer resultado

- **Mesmo livro da carta de 1767.** A carta só foi avaliada, sem entrar em treino. A edição do
  pagamento identifica o escrivão como *Antonio da Costa Pereira, tabelião*. Uma comparação
  visual preliminar, feita por IA e **não validada**, sugere mãos diferentes: a carta tem cursiva
  menor e regular, com muitas abreviaturas; o pagamento, cursiva grande e espalhada. A
  confirmação cabe ao revisor humano.
- **Um único documento, cerca de 45 linhas de texto.** O teste é pequeno; reportar contagens de
  caracteres e palavras e o resultado por linha.
- **Data.** O título do catálogo diz 27/11/1751. A edição e o próprio manuscrito (fim de 114r e
  anotação de margem em 113v) indicam **1759**. Registrar a leitura humana da data.
- **Cobertura.** O topo de 113v traz outro recibo, assinado por Caetano Antonio Rangel, que não
  faz parte da edição. Definir a região de cobertura antes de validar linhas.

## Fontes conferidas

| Arquivo | SHA-256 |
| --- | --- |
| `data/raw/corpus_expandido_v02/fontes/pagamento_thomas_pardo/manuscript_image_37eec7f6ae756ba4.jpg` (Fólio 113 verso) | `37eec7f6ae756ba44fd877bf89610d8bc4b3298ddf1a474f4226297dec61c0bb` |
| `data/raw/corpus_expandido_v02/fontes/pagamento_thomas_pardo/manuscript_image_bfa219c731ebc77b.jpg` (Fólio 114 reto) | `bfa219c731ebc77bdc306b775ead886b54bbb33a08bf776118cd628ed8892396` |
| `data/raw/corpus_expandido_v02/fontes/pagamento_thomas_pardo/modernized_edition_ba07a3fb9769e23b.pdf` (edição modernizada) | `ba07a3fb9769e23b66db806676efc9509f2acb9944753192159e3927408ac39e` |

Catálogo: [SISMU, obra 102151](https://jundiai.sismu.app/obra/102151/pagamento-realizado-ao-capitao-do-mato-thomas-pardo-por-ter-posto-a-cabeca-de-um-negro-quilombola-na-estrada-real-que-vai-para-sao-paulo-27-de-novembro-de-1751),
registro 02398; Autos de Diligências e Mandados 1742–1783, registro 0146; páginas 317–318 do
PDF do livro. Edição: Gilson Santos (AHMJ), revisão Isabella Ferraro (AHMJ).

## Protocolo de curadoria do teste

1. Abrir o workspace com `iniciar_curadoria_teste.bat`, ou
   `.venv/Scripts/python.exe -m paleographia serve --config configs/curation_teste_pagamento.toml --host 127.0.0.1 --port 8014`.
   O reconhecedor fica **desligado**: a referência não pode ser produzida vendo sugestões de modelos.
2. Identificar documento, fólio e face de cada página e definir a região de cobertura.
3. Conferir os recortes. Os 53 candidatos automáticos (26 em 113v, 27 em 114r) **não seguem bem as
   linhas** nestas páginas: há faixas que cortam o texto, faixas vazias e a última linha de 114r
   ficou de fora. Ajustar com "Ajustar selecionada", desenhar os que faltam e rejeitar margens,
   assinaturas e o recibo fora da cobertura.
4. Transcrever cada linha diplomaticamente na imagem, com revisor identificado. A edição
   modernizada pode apoiar a leitura, mas não substitui a conferência visual; registrar as dúvidas.
5. Ao concluir, **congelar** a referência: exportar, registrar hashes dos recortes e das linhas e
   publicar um registro datado. Só então treinar e escolher checkpoints com treino e validação.
6. **Rodar os modelos no teste uma única vez por configuração final**: PP-OCRv6 base e ajustado, com
   as mesmas referências, NFC e CER/WER por linha e agregados.

O workspace `data/workspace_teste_pagamento/` fica fora do Git, como os demais workspaces locais.
Ele foi criado em 05/11/2026 com as duas páginas apontando para os arquivos originais acima e
com a segmentação automática por projeção; nenhuma linha foi revisada.
