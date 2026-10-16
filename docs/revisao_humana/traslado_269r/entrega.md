# Preparação do 269r para revisão no editor — 16/10/2026

Foram preparados uma página, cinco linhas e uma região candidatas, com
configuração e workspace próprios. O [caderno de conferência](conferencia_bloco.md)
mostra as cinco imagens, o bloco, caixas, página inteira, textos, confirmações
e pendências. As observações humanas foram copiadas com mensagem original,
escopo, horário e vínculos; `Dias` na proposta não altera `dias` na edição.

`src/paleographia/preparation.py` prepara recortes RGB diretamente dos pixels
originais, recupera somente a edição arquivada correta quando necessário e
recusa divergências de fontes, imagens ou manifests existentes. O comando é
`python scripts/prepare_traslado.py`; a especificação explícita está em
`configs/traslado_269r_source.json`. O primeiro recorte mantém uma pendência
visível no floreio da inicial, que deve ser conferido com a página inteira.

`Page` e `Line` existentes aceitam os registros e preservam os campos extras.
`reference_kind` começa como `unknown`, a natureza publicada está em
`published_reference`, `text_diplomatic` e `text_modernized` são nulos,
texto/geometria/correspondência/cobertura ficam pendentes e `split` é nulo.
O responsável previsto é distinto de revisor e timestamp de revisão efetiva.

A interface acrescenta apoio publicado de somente leitura, proposta assistida,
observações parciais e acesso à página inteira. Os campos humanos e o apoio
modernizado de 1831 preservam seu comportamento; salvar/exportar mantém os
metadados publicados. A amostra utiliza `data/workspace_traslado_269r`; o
workspace `data/workspace` e os manifests de 1831 não foram substituídos.

Os oito snapshots legados continuam com os mesmos nomes e blobs. O registro
de integridade distingue hash publicado LF de identificador histórico CRLF.
Novos snapshots usam JSON determinístico UTF-8/LF, hash completo e escrita
atômica existente. Veja o [contrato e comandos](integridade.md). A CI busca o
histórico Git para executar a regressão de blobs também em clones novos.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| Suíte Python completa | 53 passaram no Windows; um aviso de depreciação Starlette/AnyIO |
| JavaScript servido pela aplicação, em DOM simulado | 18 passaram |
| Compilação de `src server tests scripts`, CLI e `pip check` | Passaram |
| Snapshots novos e legado | Bytes determinísticos sob simulação LF/CRLF; oito blobs antigos intactos; alterações divergentes recusadas |
| Cinco recortes reais | Inspecionados visualmente e comparados pixel a pixel com fonte/caixas |
| Importação real no workspace do Traslado | Uma página, cinco linhas pendentes |
| Segunda preparação | Catálogo e revisão preservados |
| Segunda importação | Recusada pelo serviço, sem substituir o workspace |
| Exportação real e validação de catálogo | Conteúdo confere com o workspace; catálogo aceito |
| Validação de referência para avaliação | Recusada com código 2, conforme esperado |
| Região sem cobertura completa em fixture sintética | Avaliação bloqueada mesmo com outros estados simulados como aprovados; nenhuma métrica gerada |
| Navegador real | Página e recorte carregados, apoio publicado somente leitura, campo humano vazio, caixas de validação desmarcadas |
| Piloto anterior | Dez arquivos ativos de workspace/manifests conferidos por hash, intactos |

Dados sintéticos e DOM simulado comprovam comportamento do software; não são
resultados de HTR. O teste de finais de linha simula LF/CRLF localmente; a
execução real entre sistemas cabe à matriz Linux/Windows da CI. Resultados de
CI remota são informados depois do envio, separadamente deste registro local.

[preparacao.json](preparacao.json) guarda os checksums e evidências desta
preparação. Não houve nova inferência real, download de pesos, CER/WER, treino
ou coleta em escala. A entrega prepara revisão; a aptidão para avaliar continua
condicionada à conferência humana real do bloco e de sua cobertura.
