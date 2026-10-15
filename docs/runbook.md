# Executar e concluir o piloto

Todos os comandos partem da raiz do repositório. Nesta máquina, a `.venv` já está pronta; use `.\.venv\Scripts\python.exe` no lugar de `python`, ou ative o ambiente. `start_safe.bat` inicia a aplicação. Para um checkout novo, use Python 3.11 ou 3.12 instalado:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,pdf]"
.\.venv\Scripts\python.exe -m pip install -e ".[htr]"
.\.venv\Scripts\python.exe -m paleographia prepare-weights --config configs/trocr-download.toml --output-dir models/trocr-small-handwritten
.\.venv\Scripts\python.exe -m pytest -q
```

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

O workspace desta máquina já foi inicializado com três fólios e 94 candidatos. Para um editor ainda vazio:

```powershell
python -m paleographia import-catalog --pages data/manifests/pages.jsonl --lines data/manifests/lines.jsonl
python -m paleographia serve --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000`. Identifique o documento/fólio, confira a edição, delimite a região transcrita e sua cobertura. Selecione os recortes no fólio ou na lista; desenhe linhas faltantes, ajuste caixas em pixels, corrija ordem e rejeite espúrias. O botão de reconhecimento trabalha nos recortes ativos, não na página inteira. Preserve um catálogo de diagnóstico separado do teste final.

O editor mantém correção humana e edição modernizada em campos distintos. A sugestão do reconhecedor atual fica indisponível na tela por não oferecer leitura utilizável em português; o resultado bruto permanece nos registros técnicos. Salvar rascunho mantém pendente. Para referência, o humano precisa fornecer seu nome e marcar explicitamente conferência do recorte e do texto. Não marcar uma edição modernizada como diplomática sem leitura do manuscrito. No 100r, o início editorial 17 não deve ser confundido com o índice operacional dos recortes.

Revisões e predições ficam em `data/workspace`. Não executar outra instância mutante sobre a mesma pasta. A exportação ZIP tem manifests/textos e não inclui imagens; mantenha fontes e crops. Uma exportação do CLI cria arquivos canônicos em diretório novo:

```powershell
python -m paleographia export --output-dir data/manifests/review_export_NEW
python -m paleographia validate --manifest data/manifests/review_export_NEW/lines.jsonl --pages data/manifests/review_export_NEW/pages.jsonl --purpose catalog --report experiments/review_catalog_NEW.json
```

## Referência, inferência e comparação

Selecione previamente 30–50 linhas revisadas, em regiões de cobertura integral, e registre exclusões e sua justificativa. Exporte seleção para um manifest separado, com suas páginas correspondentes; não apagar o catálogo completo para esconder pendências. Um catálogo com linhas rejeitadas/pendentes não é aceito diretamente como referência de avaliação.

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
