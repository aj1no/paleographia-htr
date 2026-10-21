# Execução, revisão e reprodução — 21/10/2026

Comandos na raiz do repositório, com Python 3.11/3.12. Instale o pacote com
o extra `[test]`, conforme o [README](../README.md). Exemplos no Windows;
em Linux use `.venv/bin/python` no lugar de `.venv/Scripts/python.exe`.

## Obter a versão principal

A branch principal e padrão é `main`. Para um checkout novo:

```powershell
git clone --branch main https://github.com/aj1no/paleographia-htr.git
cd paleographia-htr
```

Em um checkout existente sem alterações locais:

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
```

O código atual e as evidências estão na `main`. Referências à antiga branch
de refatoração em snapshots e relatórios preservam a origem das publicações;
não substitua esses campos. Consulte a [nota da adoção da main](manutencao/main_20261020/README.md).

## Conferir a entrega sem nova inferência

A [entrega acadêmica](entregas/pi_iv_pln_20261020/README.md) reúne notebook,
HTML, artigo, tabelas e figuras. Para auditar a referência e as métricas:

```powershell
.venv/Scripts/python.exe docs/revisao_humana/traslado_269r/referencia_assistida_20261020/verificar.py
.venv/Scripts/python.exe docs/experimentos/traslado_269r_reconhecedores_24_20261020/verificar.py
```

Essas verificações usam arquivos locais, sem pesos, Docker ou reconhecimento.
O validador humano estrito continua bloqueando a avaliação integral das 24
linhas como referência visualmente validada. O diagnóstico usa alvos assistidos
separados e preserva as oito ressalvas, sem promover estados no editor.

O notebook tem [ambiente e executor separados](entregas/pi_iv_pln_20261020/README.md)
e gera derivados em `output/`, preservando o notebook arquivado. Para repetir
inferências, siga o [experimento de 24 recortes](experimentos/traslado_269r_reconhecedores_24_20261020/README.md):
é necessário ter pesos e imagem Docker conferidos e escolher pasta nova.

A [CI acadêmica](manutencao/ci_academica_20261021/README.md) usa o mesmo executor
congelado, acrescentando auditoria antes/depois, proteções contra inferência e
comparação dos derivados. Para reproduzir essa tarefa, use um checkout limpo,
sem `models/`, workspaces ou a pasta de saída já existente; não apague revisões
ou derivados desta máquina para satisfazer essa condição. O guia fornece o
comando `python scripts/ci_academica.py` e a instalação opcional correspondente.

## Retomar o editor do Traslado nesta máquina

```powershell
.venv/Scripts/python.exe -m paleographia serve --config configs/traslado_269r.toml --host 127.0.0.1 --port 8011
```

Abra `http://127.0.0.1:8011/`. O workspace é `data/workspace_traslado_269r`.
Ele já contém as revisões locais. Não importe outro catálogo sobre ele nem
execute dois processos mutantes na mesma pasta.

### Checkout novo e workspace vazio

O clone contém os pacotes publicados, mas não o workspace desta máquina.
Para consultar/revisar uma cópia do catálogo congelado de 24 linhas:

```powershell
.venv/Scripts/python.exe -m paleographia import-catalog --pages docs/revisao_humana/traslado_269r/referencia_assistida_20261020/paginas_congeladas.jsonl --lines docs/revisao_humana/traslado_269r/referencia_assistida_20261020/linhas_congeladas.jsonl --config configs/traslado_269r.toml
.venv/Scripts/python.exe -m paleographia serve --config configs/traslado_269r.toml --host 127.0.0.1 --port 8011
```

O import cria uma nova revisão inicial na cópia local, com os campos e dúvidas
do catálogo. Não restaura a cadeia completa nem as predições do editor original:
snapshots, predições e vínculos continuam no [pacote publicado](revisao_humana/traslado_269r/referencia_assistida_20261020/README.md).
Não execute o import em workspace que já possui revisão.

Os manifests em `data/manifests/traslado_269r/` e `scripts/prepare_traslado.py`
correspondem à preparação inicial de cinco linhas. Não representam o estado
humano final de 24 linhas e não devem substituir essa referência.

### Reconhecer, consultar e salvar

O [runtime PP-OCRv6](../runtime/kraken_ppocrv6/README.md) é preparado separadamente.
Sem pesos ou Docker, a revisão manual continua disponível. Sugestões exigem
conferência humana e não validam automaticamente o texto.

Rascunho na aba não equivale a revisão persistida. Use **Salvar revisão** ou
**Salvar identificação**. Em conflito 409, atualize o catálogo, confira a versão
salva e só então escolha **Manter rascunho após conferir esta versão**. Fechar
a aba pode perder rascunhos não salvos. Revisor e confirmações de texto/recorte
são explícitos; apoio editorial não equivale a certeza visual.

O painel **Vocabulário histórico e fontes** consulta os 21 registros de
`data/lexicon/` sem novo reconhecimento. Aplicar um candidato muda o rascunho;
salvar registra a proveniência. Consulte a [política lexical](lexico_historico.md).

Para exportar o estado atual a uma pasta ainda inexistente:

```powershell
.venv/Scripts/python.exe -m paleographia export --config configs/traslado_269r.toml --output-dir output/export_269r_NOVO
```

A exportação contém manifests/textos, não todas as imagens nem a cadeia completa
de revisões. Preserve fontes, recortes e histórico separadamente.

## Piloto anterior de 1831

Usa `configs/pilot.toml`, `data/workspace` e porta 8000. `start_safe.bat` abre
essa configuração: 94 candidatos pendentes e apresentação de sugestões
desativada. Para reconstruir derivados em checkout novo:

```powershell
.venv/Scripts/python.exe -m pip install -e ".[pdf]"
.venv/Scripts/python.exe -m paleographia extract --input-dir data/raw --output-dir data/raw/import_20261015
.venv/Scripts/python.exe scripts/materialize_pilot.py
.venv/Scripts/python.exe scripts/build_repertoire.py --materialize
```

RAR exige extrator externo compatível no PATH. Não repita a extração sobre
diretório existente. Materializadores recriam somente imagens ausentes,
conferem pixels e preservam manifests/confirmações; divergências são recusadas.
Não use a preparação inicial para regravar um catálogo revisado.

Somente com workspace vazio:

```powershell
.venv/Scripts/python.exe -m paleographia import-catalog --pages data/manifests/pages.jsonl --lines data/manifests/lines.jsonl --config configs/pilot.toml
.venv/Scripts/python.exe -m paleographia serve --config configs/pilot.toml --host 127.0.0.1 --port 8000
```

## Verificações e rotas secundárias

```powershell
.venv/Scripts/python.exe -m pytest -q
node --test tests/web_review.test.cjs
.venv/Scripts/python.exe -m compileall -q src server tests scripts
.venv/Scripts/python.exe -m paleographia --help
```

A CI usa Node 22 para o editor. A suíte leve não executa modelos reais; a tarefa
acadêmica separada reexecuta o notebook sem inferência. `/health` informa o
reconhecedor; `/docs` apresenta a API.
O servidor deve permanecer local, com um processo por workspace.

`compare` compara **segmentadores**, com reconhecedor fixo; não é o experimento
PP-OCRv5 × PP-OCRv6. Essa rota é secundária e não foi medida neste corpus.
TrOCR e sua preparação estão bloqueados; `train` não oferece treinamento do
backend Kraken atual. Não houve ajuste fino neste corpus.

Para eventual ampliação, congele o protocolo e reserve outros documentos antes
de usá-los na seleção. O 269r permanece desenvolvimento. Consulte as
[pendências acadêmicas](entregas/pi_iv_pln_20261020/adequacao_academica.md).
