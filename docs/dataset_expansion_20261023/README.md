# Expansão do corpus e ajuste fino — 23/10/2026

Incorporação executada sobre a `main` em `75b7b24aa2f03aa906aedf2c6d3dfecfa89cb627`.
O corpus de fontes foi ampliado e o caminho de treinamento PP-OCRv6 foi implementado.
**Situação: ensaio técnico executado; experimento científico ainda pendente de curadoria.**

## Fontes e imagens disponíveis

O ZIP v0.2 recebido tem SHA-256
`62e1c3da154b4dcc9bdf63715c01eba788d7a2f6f5cce7a973938755772e25bd`.
Todas as entradas foram conferidas pelo inventário interno, e as 15 fontes
correspondem aos hashes do inventário de 16/10. Os scripts do pacote foram
preservados como fontes, sem execução. Os originais estão em
`data/raw/corpus_expandido_v02/`; os caminhos dos catálogos são relativos à raiz
do repositório. O ZIP original permanece em Downloads.

São oito PDFs, 59 páginas, sete grupos candidatos e sete JPEGs avulsos.
A inspeção visual dos PDFs combinados encontrou mais 12 reproduções de
manuscritos, além das nove já indexadas no fac-símile. O inventário completo
dos PDFs registra 80 objetos de imagem, incluindo logotipos e marcas editoriais.
**As 28 ocorrências de manuscritos não equivalem a 28 fólios independentes:**
há JPEGs e reproduções PDF do mesmo documento, recompressões e uma abertura
com dois fólios no pagamento.

| Grupo candidato | Ocorrências | Reprodução nos PDFs (páginas base 1) |
| --- | ---: | --- |
| Carta de José Gomes, 1767 | 2 | Edição: 5; mais JPEG |
| Contrato, livro 12, 1763 | 4 | Edição: 9–12 |
| Contrato, livro 13, 1763 | 2 | Edição: 5–6 |
| Pagamento a Thomas Pardo | 3 | Edição: 4; mais dois JPEGs |
| Posturas, 1831 | 6 | Edição: 6–8; mais três JPEGs |
| Sessão, 1795 | 2 | Edição: 4; mais JPEG |
| Traslado da criação da vila | 9 | Fac-símile: 1–9 |

Os [catálogos](../../data/manifests/corpus_expandido_v02/) registram fontes,
créditos editoriais, tipos de edição, hashes, ocorrências, coordenadas de origem
PDF, fólio/lado quando declarados no nome original e os estados de conferência.
Os textos integrais extraídos incluem títulos, créditos e páginas vazias;
continuam sendo apoio editorial. A extração atual usa pypdf 6.1.1/Pillow 11.3.0,
do ambiente do projeto; a extração pypdf 6.10.0 recebida foi preservada no pacote.
Há diferenças de espaçamento entre extratores; nenhuma contagem de linhas de
PDF foi convertida em quantidade de alvos.

## Dataset supervisionado e próxima revisão

O núcleo congelado continua com **24 linhas de desenvolvimento: 16 validadas,
oito pendentes/ressalvadas**. Texto publicado, alvo histórico adotado, política
assistida pela edição, autoria, datas, geometria, dúvidas e reconferência de
21/10 foram preservados, sem promoção de estado. Essas linhas já existiam.

Foi preparado um [bloco concreto de oito recortes da sessão de 1795](curation_sessao_1795_bloco01/README.md),
com página contextual, sobreposição dos limites e texto modernizado separado.
Os alvos diplomáticos permanecem vazios. **Novos pares validados: zero.**
As decisões humanas necessárias são a correspondência/fólio, os limites dos
oito recortes e suas leituras históricas, incluindo abreviaturas e hifens físicos.
A aprovação anterior do uso da edição como apoio continua válida.

## Grupos e partições

O [protocolo registrado](../../data/manifests/corpus_expandido_v02/partitions.json)
mantém os sete grupos candidatos sem sorteio e sem impor 80/10/10. A independência
documental ainda precisa de confirmação, especialmente nos PDFs contratuais.
As imagens de 1831 foram vinculadas ao ID do documento do catálogo anterior;
todo o Traslado conserva o ID documental do 269r. Cópias e derivados ficam
no mesmo grupo. Ambos já foram usados no desenvolvimento e só poderão
contribuir ao treino, nunca a um novo teste científico.

Não há novos grupos com pares aptos suficientes para preencher treino,
validação e teste científicos. A configuração científica candidata falha antes
de iniciar Docker enquanto a independência e as referências estiverem pendentes.
O teste não foi exportado, montado no contêiner ou usado para codec, limites,
taxa de aprendizado, épocas ou seleção de checkpoint.

## Ajuste fino realmente executado

`training.py` agora encaminha o backend PP-OCRv6 a um experimento `ketos`
explicitamente configurado. TrOCR continua bloqueado. O comando nativo foi
conferido na documentação e na ajuda instalada do Kraken 7.1.
O [snapshot da execução](training_ppocrv6_smoke/) contém configuração, versões,
ajuda, plano e hashes dos dados, código executado, perdas, validação,
identidade dos checkpoints e comparação dos tensores.

| Item | Ensaio técnico final |
| --- | --- |
| Modelo inicial | PP-OCRv6 medium, SHA-256 `15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9` |
| Ambiente | Imagem Docker fixada `sha256:511fb2e2b76db8de0d3eb87dcf04398f7a02fc06b5d91887629b2492f826af5b`; Kraken 7.1; PyTorch 2.9.1+cpu; Python 3.12.15 |
| Dados | Linhas históricas 01–02 para treino, linha 03 para validação técnica; mesmo documento de desenvolvimento |
| Orçamento | Uma época, lote 1, dois passos, CPU/float32, dois threads, teto Docker de 4 GiB e timeout de 300 s |
| Semente / otimizador | 1831 / AdamW, taxa `0.00001`, sem warmup, sem aumento artificial de dados |
| Entrada | Recortes PNG e arquivos homônimos `.gt.txt` UTF-8; manifests explícitos `train.lst` e `validation.lst` |
| Política | NFC, espaços normalizados; sem reorder; codec inicial preservado (`resize=fail`); altura 96, largura máxima fixa 2560 |
| Perdas registradas | Passo 1: 9,595231; passo 2: 9,548119; média da época: 9,571674 |
| Seleção nativa | Maior `val_metric`, usando somente validação técnica; valor observado 0,875 |
| Prova de otimização | Estado AdamW no passo 2; 318 tensores treináveis alterados, com hashes e deltas individuais |
| Recarga | Peso convertido corresponde ao checkpoint selecionado; inferência executada após recarga |
| Tempo observado | Cerca de 167 s no host; 145 s no worker |
| Memória | Pico do cgroup: 4.289.536.000 bytes, próximo do limite de 4 GiB |

Os valores nativos de validação (`val_accuracy=0.875`, `val_word_accuracy≈0.60`)
são diagnósticos de uma única linha do mesmo documento. Não substituem a
avaliação CER/WER do projeto nem são comparáveis à tabela histórica de 24 linhas.
As duas perdas são de exemplos diferentes: sua diferença não demonstra uma
melhora de qualidade. O ensaio prova otimização, atualização de pesos e recarga.

A primeira tentativa falhou por ausência de compilador C++ para `torch.compile`;
o [registro da falha](attempt01_failure/) foi preservado. A solução usa
`TORCHDYNAMO_DISABLE=1` somente no contêiner de treino, mantendo autograd eager.
Não houve download, instalação, reconstrução da imagem ou modificação do
reconhecedor ativo. Não ampliar o orçamento científico automaticamente: o pico
de memória já ficou próximo do limite no ensaio pequeno.

O peso final local é
`experiments/ppocrv6_smoke_20261023_final/checkpoints/best_0.8750.safetensors`,
SHA-256 `f6cc0f072a162772b628a7d71358353c6d0915170504aa5e77382090b4b0efa7`.
O checkpoint com otimizador também foi preservado localmente. Esses arquivos
grandes ficam fora do Git; seus caminhos, tamanhos e hashes estão registrados.
Os pesos-base permanecem somente para leitura e com hash original.

## Reproduzir e conferir

Na raiz do repositório, para restaurar somente fontes/imagens ausentes de um
checkout que já possui os catálogos versionados:

```powershell
.venv/Scripts/python.exe -m paleographia restore-corpus --archive D:/Downloads/PaleographIA_Corpus_Expandido_v0_2_20261023.zip
```

O comando confere o ZIP e recusa sobrescrever arquivos divergentes. Para fazer
outra incorporação integral, escolha **duas pastas novas** com `expand-corpus
--archive ... --source-dir data/raw/nova_versao --output-dir data/manifests/nova_versao`.
Catálogos históricos e fontes recebidas permanecem intactos.

Auditoria das evidências salvas, sem Docker, pesos ou nova inferência:

```powershell
.venv/Scripts/python.exe scripts/audit_dataset_expansion.py
# Nesta máquina, conferir também os bytes do checkpoint/peso grande:
.venv/Scripts/python.exe scripts/audit_dataset_expansion.py --local-artifacts
```

Preparar um ensaio novo (dry-run) e executar somente quando desejado:

```powershell
.venv/Scripts/python.exe -m paleographia train --config configs/training_ppocrv6_smoke.toml --output-dir experiments/novo_dry_run
.venv/Scripts/python.exe -m paleographia train --config configs/training_ppocrv6_smoke.toml --output-dir experiments/novo_ensaio --execute
```

Um dry-run registra `ready_dry_run`; não conta como execução. A imagem deve
estar instalada e o modelo-base deve corresponder ao hash fixado. Há mounts
separados para modelo-base, código e dados somente para leitura, e saída gravável;
rede desabilitada, sem montar o projeto/editor no contêiner.

Depois da revisão de documentos independentes, produzir novos manifests e
protocolo com todas as três partições, revisores e datas. A configuração
`configs/training_ppocrv6_scientific.toml` é candidata e está bloqueada pelos
dados atuais. Fixar o modelo usando somente validação e só então comparar base
e ajustado no mesmo teste, com NFC/espaços e CER/WER idênticos. A comparação
PP-OCRv5 × PP-OCRv6 publicada permanece como diagnóstico histórico.

## Para o professor

O **corpus de fontes** contém imagens, documentos e edições; suas 59 páginas
não são 59 exemplos supervisionados. O **dataset supervisionado** exige pares
de recorte de linha e transcrição histórica com revisão e proveniência.
A **inferência** aplica os pesos existentes para sugerir texto; o **ajuste fino**
calcula perda, retropropaga gradientes e atualiza parâmetros.

Agora há evidência concreta de ajuste fino do PP-OCRv6: dois passos de AdamW,
318 tensores alterados e peso recarregado com sucesso. Essa demonstração técnica
usa desenvolvimento já conhecido, preservando os oito casos históricos incertos.
O próximo avanço científico depende da revisão dos novos recortes, da confirmação
de documentos independentes e da reserva de teste antes de selecionar o modelo.
