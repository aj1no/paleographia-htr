# Segundo documento do teste reservado: contrato do livro 12, 1763 (decisão de 09/11/2026)

Registro aditivo. Não altera a [reserva de 05/11](../pagamento_thomas_pardo_teste/README.md), o
catálogo `data/manifests/corpus_expandido_v02/` nem outros pacotes congelados.

## Decisão

Em 09/11/2026, durante a transcrição às cegas do pagamento a Thomas Pardo, o revisor informou
que as linhas finais dos fólios 113v e 114r estão quase ilegíveis. Até então, 14 das 61 linhas
estavam validadas. O solicitante decidiu **somar** um segundo documento ao teste reservado, em vez
de trocar o primeiro:

| Papel | Documento | Situação em 09/11 |
| --- | --- | --- |
| Teste reservado, documento 1 | Pagamento a Thomas Pardo, livro 0146, 113v e 114r | Mantido. As linhas que o revisor não consegue ler ficam pendentes, com motivo de exclusão |
| **Teste reservado, documento 2** | **Contrato de Francisco Vieira da Costa e Manoel da Siqueira Gil, 27/08/1763, Cartório Olgado, livro 12, folhas 278 e 279** | Curadoria criada nesta data, sem linhas transcritas |

**O critério foi só a legibilidade para o leitor humano.** Até esta data, nenhum modelo rodou em
nenhum dos dois documentos. A escolha não usou nenhum resultado de modelo.

## Por que o livro 12

Ele era o único documento do corpus v0.2 sem nenhum uso anterior (ver a tabela da reserva de
05/11). Na conferência de 09/11, as únicas referências ao livro 12 no projeto estão nos
inventários e nos manifestos do corpus. Não há referência em treinos, experimentos, configurações
de modelo nem notebooks.

As quatro imagens do manuscrito também não são cópias de imagens de outros documentos. Comparadas
em miniatura com todas as imagens grandes do corpus, a diferença média mínima foi de 17,9 a 23,1
níveis de cinza (de 0 a 255). Uma cópia ficaria perto de zero.

## Ressalvas a declarar em qualquer resultado

- **Mesmo cartório, mesma data e uma parte em comum com o contrato do livro 13.** O livro 13 entrou
  só no pré-treino não supervisionado do reconhecedor feito do zero (a curiosidade do artigo) e
  numa exploração de imagem. Ele **não** entrou no treino do PP-OCRv6 ajustado A nem do B.
  Trechos de texto repetidos entre os dois contratos devem ser identificados pelo revisor.
- **As imagens vêm de dentro do PDF da edição** (páginas 9 a 12 do PDF), com 1361 a 1652 × 2048
  pixels. O revisor lê os recortes na curadoria, sem abrir o PDF. A edição pode apoiar a leitura
  depois, como no documento 1, mas não substitui a conferência visual.
- **Fólio e face** ficam para o revisor identificar na imagem. O catálogo indica as folhas 278 e 279.
- **Dois documentos pequenos.** Reportar o resultado por documento e o agregado, com contagens de
  caracteres e palavras.

## Fontes

| Imagem (página do PDF da edição) | SHA-256 |
| --- | --- |
| `data/manifests/corpus_expandido_v02/pdf_images/c7ffb34ac9b8c735/p009_i00.jpg` (p. 9) | `a147ae6a5c9bd3f5eac9e2db0520c6948cc2e4f651de02a857d2a312f30baf45` |
| `data/manifests/corpus_expandido_v02/pdf_images/c7ffb34ac9b8c735/p010_i00.jpg` (p. 10) | `08a5eb976ab0320038d215bca761b66bf29d01c420b3d139c8ac0306ee7bbb25` |
| `data/manifests/corpus_expandido_v02/pdf_images/c7ffb34ac9b8c735/p011_i00.jpg` (p. 11) | `3b4aa4ecb7e0b683d2118e2a0979d28d2398bcee24e85c32f97249e25bfa864e` |
| `data/manifests/corpus_expandido_v02/pdf_images/c7ffb34ac9b8c735/p012_i00.jpg` (p. 12) | `43456b368c7d1a00d4f7909d58b914266f836d117d8e1fd44f0604202a67e92b` |
| `data/raw/corpus_expandido_v02/fontes/contrato_livro12_1763/modernized_edition_c7ffb34ac9b8c735.pdf` (edição) | `c7ffb34ac9b8c735bf5b25cfa6c32d98b3e752fbc8744fa9a8feb14489620e07` |

Catálogo: [SISMU, obra 101489](https://jundiai.sismu.app/obra/101489/contrato-para-exploracao-de-minas-auriferas-em-territorios-jundiaienses-em-1763-o-texto-contem-descricoes-sobre-africanos-afro-brasileiros-povos-originarios-e-quilombos),
registro 02317. Edição: Gilson Santos (AHMJ), revisão Isabella Ferraro (AHMJ).

## Curadoria

- Criada com [`scripts/preparar_teste_contrato12.py`](../../../scripts/preparar_teste_contrato12.py):
  cataloga as quatro imagens conferindo o SHA-256 e desenha as linhas com o **blla** do Kraken (só
  segmentação, sem leitura de texto). O texto da edição não foi lido.
- Resultado: 154 recortes, 40 marcados como margem (p. 9: 35/11; p. 10: 43/11; p. 11: 42/11;
  p. 12: 34/7). Revisão do workspace: `20261109T155422_8818c865`. Nenhuma predição.
- Abrir com `iniciar_curadoria_teste_contrato12.bat`, ou
  `.venv/Scripts/python.exe -m paleographia serve --config configs/curation_teste_contrato12.toml --host 127.0.0.1 --port 8017`.
  O reconhecedor fica **desligado**, e `tests/test_review_integrity.py` impede ligá-lo.
- O protocolo é o mesmo do documento 1: conferir e ajustar os recortes, rejeitar margens,
  assinaturas e rubricas, transcrever diplomaticamente na imagem, excluir com motivo o que não
  for legível, congelar a referência e rodar cada configuração final **uma única vez**.

O workspace `data/workspace_teste_contrato12/` fica fora do Git, como os demais workspaces locais.
