# Teste de salvamento lexical em cópia isolada

**Artefatos de teste de interface e persistência. Não constituem nova revisão
humana, referência paleográfica ou experimento de reconhecimento.**

O usuário autorizou publicar este relatório e suas evidências na branch
`codex/refatoracao-piloto`. A cópia local foi usada para salvar `Annodo → Anno do`
e `Sundiahy → Jundiahy`, mantendo as linhas pendentes e identificando os novos
salvamentos como **Codex · teste de salvamento em cópia isolada**.

As revisões originais continuam intactas. No original, o ponteiro permanece
`20261016T191933_07d31bad`, com dez linhas validadas e cinco pendentes. Somente
na cópia as linhas 1 e 5 voltaram a pendentes, resultando em oito validadas e
sete pendentes. A cobertura foi herdada sem nova confirmação.

## Relatório e arquivos

- [Relatório em Markdown](PaleographIA_Teste_Salvamento_Lexical_20261019.md):
  procedimento, textos, eventos JSON completos, fontes e limitações.
- [Recibo de verificação](evidencias/verificacao.json): histórico, eventos com
  fontes resolvidas e hashes dos arquivos originais conferidos no teste.
- [Snapshots da cópia](evidencias/revisions/): estado inicial e duas revisões
  novas, sem regravar os snapshots anteriores.
- [Catálogo de fontes](evidencias/sources.json) e [entradas](evidencias/entries.jsonl):
  bytes da base lexical usada. Os eventos guardam IDs, versão e fingerprint;
  a bibliografia completa é recuperada nesses arquivos.
- [Linha 1 após salvar](evidencias/linha_1_salva.png) e
  [linha 5 após salvar](evidencias/linha_5_salva.png): imagens reais do editor da cópia.
- [Registro de publicação](publicacao.json): origem dos arquivos, adaptações
  documentais e SHA-256 antes/depois.
- [Preservação na publicação](evidencias/preservacao_publicacao.json): comparação
  por hash dos dados, revisões humanas e experimentos preexistentes.
- [Inventário publicado](evidencias/sha256.json): SHA-256 de todos os arquivos
  desta pasta, exceto o próprio inventário.

## Conferência reproduzível

Na raiz do checkout, com Python 3.11 ou 3.12, sem dependências adicionais:

```powershell
python docs/testes/lexico_copia_20261019/verificar.py
```

O verificador é de somente leitura. Confere os hashes, o fingerprint lexical,
o encadeamento dos três snapshots, os eventos e suas fontes, os estados
pendentes e a preservação das predições, páginas e outras linhas. No checkout,
também confere o arquivo publicado que originou as atestações. Fora dele,
informa a indisponibilidade dessa conferência adicional.

As imagens originais do manuscrito e todo o workspace local não são duplicados
nesta pasta. Os snapshots são evidências, separados dos manifests utilizados
pela aplicação e pela avaliação. A prova de preservação registra os arquivos
disponíveis na máquina durante o teste/publicação; ela não restaura nem altera
esses arquivos ao ser executada em outro checkout.

## Preparação para publicação

Os sete arquivos de evidência de origem (três snapshots, dois catálogos e duas
imagens) mantêm seus bytes. O Markdown e o recibo usam caminhos relativos ao
repositório; o Markdown também recebeu uma nota sobre esta publicação. Os
artefatos locais anteriores permanecem intactos. O inventário foi regenerado
para cobrir a versão publicada e os arquivos de conferência adicionais.

Não houve nova inferência, treino ou métrica CER/WER. As três entradas usadas
vêm das próprias linhas humanas 1 e 5, do mesmo grupo de desenvolvimento;
recuperá-las não é confirmação independente. O verbete `ANNO` de Bluteau não
foi escolhido nesses eventos. O `reference_kind="human_diplomatic"` herdado da
cópia não altera o fato de que os dois textos de teste estão pendentes.
