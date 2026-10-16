# Executar e concluir o piloto

Todos os comandos partem da raiz do repositório. Nesta máquina, a `.venv` já está pronta; use `.\.venv\Scripts\python.exe` no lugar de `python`, ou ative o ambiente. `start_safe.bat` inicia a aplicação. Para um checkout novo, use Python 3.11 ou 3.12 instalado:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,pdf]"
.\.venv\Scripts\python.exe -m pytest -q
```

O reconhecedor atual é PP-OCRv6 medium em [runtime Linux separado](../runtime/kraken_ppocrv6/README.md).
TrOCR e sua preparação antiga estão desativados; os experimentos históricos
continuam auditáveis sem executá-lo. O [diagnóstico do 269r e a integração](experimentos/traslado_269r_ppocrv6_20261016/README.md)
mostram as cinco entradas/saídas, CER 12,40%, WER 51,11% e comandos atuais.

## Importação

Fontes novas: copiar para `data/raw/inbox/` e inventariar. Não processar PDF digitado como manuscrito.

```powershell
python -m paleographia inventory --input-dir data/raw/inbox --output data/manifests/new_pages.jsonl
python -m paleographia extract-reference --pdf "data/raw/inbox/Transcrição..pdf" --output data/manifests/new_edition.jsonl
```

Para materializar os manifests versionados em checkout novo, com UnRAR disponível no PATH:

```powershell
python -m paleographia extract --input-dir data/raw --output-dir data/raw/import_20261015
python scripts/materialize_pilot.py
python scripts/build_repertoire.py --materialize
```

As fontes extraídas já existem nesta máquina; não repita `extract` sobre o diretório existente. O materializador usa as caixas persistidas, confere fontes/checksums e recria somente crops ausentes; recortes existentes divergentes causam erro, sem sobrescrita. Não modifica os manifests revisados. A opção `--materialize` do repertório reconstrói as imagens a partir do catálogo existente e preserva suas confirmações; não execute a preparação inicial sobre um catálogo já revisado.

Para refazer a detecção de desenvolvimento em saídas novas, mantendo o catálogo versionado:

```powershell
python -m paleographia inventory --input-dir data/raw/import_20261015 --output data/manifests/rebuild/inventory.jsonl
python scripts/prepare_pilot.py --inventory data/manifests/rebuild/inventory.jsonl --output-pages data/manifests/rebuild/pages.jsonl --output-lines data/manifests/rebuild/lines.jsonl --output-dir data/processed/rebuild
```

Esse script prepara somente os três candidatos explícitos da auditoria; identificações e referências ficam pendentes. Para fontes diferentes, use `associate` com JSONL de mapeamento explícito ou a identificação no editor. A operação nunca usa ordem alfabética como validação.

```powershell
python -m paleographia associate --pages data/manifests/new_pages.jsonl --mapping data/manifests/mapping.jsonl --output data/manifests/mapped_pages.jsonl
python -m paleographia segment --pages data/manifests/mapped_pages.jsonl --method opencv --config configs/pilot.toml --output-dir data/processed/new_detection
```

Um mapeamento tem `page_id`, `document_id`, `folio_id`, `side`, `correspondence_status` e `transcribed_coverage`. Cada cobertura identifica explicitamente região, caixa no original, fonte e páginas da edição. Deixe pendente enquanto não houver revisor. Páginas compartilhadas da edição podem aparecer em dois fólios; nunca presumir pares 1:1. Veja `data_schema.md`.

## Revisão local

Para o Traslado 269r, use o [roteiro específico das cinco primeiras linhas](revisao_humana/traslado_269r/conferencia_bloco.md).
Ele prepara catálogo próprio e usa `configs/traslado_269r.toml`, workspace
`data/workspace_traslado_269r` e porta 8011, preservando o piloto de 1831.
O roteiro inclui exportação, validação e diagnóstico exploratório condicionado
à revisão humana. Consulte também o [contrato de integridade dos snapshots](revisao_humana/traslado_269r/integridade.md).

O workspace desta máquina já foi inicializado com três fólios e 94 candidatos. Para um editor ainda vazio:

```powershell
python -m paleographia import-catalog --pages data/manifests/pages.jsonl --lines data/manifests/lines.jsonl
python -m paleographia serve --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000`. Identifique o documento/fólio, confira a edição, delimite a região transcrita e sua cobertura. Selecione os recortes no fólio ou na lista; desenhe linhas faltantes, ajuste caixas em pixels, corrija ordem e rejeite espúrias. O botão de reconhecimento trabalha nos recortes ativos, não na página inteira. Preserve um catálogo de diagnóstico separado do teste final.

O editor mantém correção humana e edição modernizada em campos distintos. O Traslado tem sugestões experimentais do PP-OCRv6 vinculadas à configuração avaliada; no piloto de 1831 a apresentação continua desativada. O resultado bruto permanece nos registros técnicos. Salvar rascunho mantém pendente. Para referência, o humano precisa fornecer seu nome e marcar explicitamente conferência do recorte e do texto. Não marcar uma edição modernizada como diplomática sem leitura do manuscrito. No 100r, o início editorial 17 não deve ser confundido com o índice operacional dos recortes.

Os rascunhos locais são mantidos por linha e fólio durante a navegação e a
atualização do catálogo. A tela informa quantos ainda não foram salvos. Use
**Salvar revisão** ou **Salvar identificação** para persistir; a memória da aba
não sobrevive garantidamente ao fechamento. Em conflito 409, atualize o catálogo,
confira a versão salva no painel e só então escolha **Manter rascunho após
conferir esta versão**, revise os campos e salve novamente. Nenhuma sobrescrita
é feita automaticamente.

Na identificação, selecione a região antes de editar seus limites ou fonte.
Adicionar/remover são ações explícitas no rascunho; salvar somente créditos não
altera coberturas. Para remover ou renomear uma região com linhas, reatribua
essas linhas primeiro. As demais regiões mantêm revisor, data e proveniência.

Revisões e predições ficam em `data/workspace`. Não executar outra instância mutante sobre a mesma pasta. A exportação ZIP tem manifests/textos e não inclui imagens; mantenha fontes e crops. Uma exportação do CLI cria arquivos canônicos em diretório novo:

```powershell
python -m paleographia export --output-dir data/manifests/review_export_NEW
python -m paleographia validate --manifest data/manifests/review_export_NEW/lines.jsonl --pages data/manifests/review_export_NEW/pages.jsonl --purpose catalog --report experiments/review_catalog_NEW.json
```

## Referência, inferência e comparação

Roteiro atualizado em **15/10/2026**, após as correções de revisão:

1. Escolher uma região curta e legível com correspondência documental conferida.
2. Revisar inicialmente **cinco linhas completas**: limites, ordem, transcrição
   paleográfica, convenções de abreviaturas/incertezas e identificação do revisor.
   As seis confirmações parciais do repertório não cumprem essa etapa.
3. Ampliar gradualmente para 30–50 linhas úteis ao diagnóstico. Essa quantidade
   não garante treino suficiente nem independência entre documentos.
4. Marcar cobertura completa somente quando todas as linhas da região estiverem
   efetivamente representadas na referência; registrar exclusões e justificativas.
5. Com referência disponível, avaliar o reconhecedor de base e investigar
   candidatos adequados ao português e à escrita do acervo. Registrar modelo,
   revisão dos pesos, ambiente, entradas e saídas, inclusive resultados ruins.
6. Definir protocolo e separar desenvolvimento da avaliação reservada **antes**
   da seleção de modelos ou ajuste de parâmetros. Uma sessão permite apenas
   exploração; não distribuir seus fólios entre treino e teste como independentes.
7. Comparar segmentadores com o mesmo reconhecedor, as mesmas regiões e condições
   de medição comparáveis, separando carregamento inicial do processamento.

Preserve o catálogo completo com a partição para `compare`: `[paths].lines`
deve incluir as linhas dos demais conjuntos, inclusive pendentes. A validação
global verifica integridade e vazamento antes da seleção; somente as linhas
de `[experiment].split` precisam de referência paleográfica/geometria revisadas.
`validation.json` registra as duas verificações e a validade conjunta. Linhas
pendentes/rejeitadas dentro da seleção não são referências de avaliação.
Para avaliação direta, exporte a referência revisada e suas páginas para novos
manifests, sem apagar os registros do catálogo completo.

Com uma sessão documental, a única divisão oferecida é exploratória sem treino:

```powershell
python -m paleographia split --lines data/manifests/reviewed_selection.jsonl --exploratory --seed 1831 --output data/manifests/pilot_exploratory.jsonl
python -m paleographia validate --manifest data/manifests/pilot_exploratory.jsonl --pages data/manifests/reviewed_pages.jsonl --purpose evaluation --report experiments/reference_validation_NEW.json
python -m paleographia recognize --lines data/manifests/pilot_exploratory.jsonl --config configs/pilot.toml --output experiments/baseline_NEW/predictions.jsonl
python -m paleographia evaluate --reference data/manifests/pilot_exploratory.jsonl --pages data/manifests/reviewed_pages.jsonl --predictions experiments/baseline_NEW/predictions.jsonl --output-dir experiments/baseline_NEW/evaluation
```

Atualize `[paths].pages`, `[paths].lines` e `[experiment].split` em uma **cópia** do TOML, mantendo hashes/configuração usados. Configure o runtime neural conforme `environment.md` e então:

```powershell
python -m paleographia compare --config configs/reviewed_pilot.toml --output-dir experiments/comparison_NEW
python -m paleographia train --config configs/reviewed_pilot.toml --output-dir experiments/training_check_NEW
```

O treino acima é dry run. Com a única sessão candidata será recusado, mesmo após revisão, por ausência de três grupos independentes. Não usar `--execute` até dados e protocolo estarem aptos. O teste reservado não é usado na seleção do modelo; após treino autorizado, execute avaliação separada do checkpoint escolhido, uma única vez conforme o protocolo.

Falhas retornam código 2 e relatórios explicam o motivo. `compare` pode registrar método não executado/execução parcial; isso também retorna falha. O health em `/health` mostra modelo configurado, realmente carregado, dispositivo e eventual erro. `/docs` documenta a API. `/process-folio` foi mantido: por padrão detecta sem reconhecer, para permitir revisão; `?recognize=true` solicita sugestões e retorna 503 se modelo indisponível. IDs de linhas são estáveis, e os percentuais antigos acompanham as coordenadas em pixels.
