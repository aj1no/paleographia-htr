# Sessão do Traslado 269r — 16/10/2026

Estado salvo para retomar a revisão na linha 11. Revisão do editor:
`20261016T191933_07d31bad`, salva às 16:19:33 de Brasília.
O navegador não apresentava rascunhos locais pendentes ao encerrar a sessão.

| Bloco do corpo | Texto e geometria | Cobertura completa |
|---|---|---|
| 1–5 (`body_first5`) | Validados pelo usuário | Confirmada somente nesse bloco |
| 6–10 (`body_06_10`) | Validados pelo usuário | Confirmada explicitamente pelo usuário às 16:18:33 |
| 11–15 (`body_11_15`) | Pendentes; campo humano vazio | Pendente |

As 15 sugestões brutas estão preservadas, separadas da transcrição humana.
As linhas 6–10 e 11–15 foram reconhecidas em dois lotes de cinco recortes
originais pelo PP-OCRv6 medium, com zero falhas. O modelo recebeu somente as
imagens. A edição publicada permanece apoio de leitura separado. Esta sessão
não acrescenta CER/WER, treino ou teste reservado; os resultados anteriores
continuam no [experimento das primeiras cinco linhas](../../../experimentos/traslado_269r_ppocrv6_20261016/README.md).

## Arquivos publicados

- `pages.jsonl`, `lines.jsonl` e `predictions.jsonl`: exportação legível do estado
  atual, com caminhos dos recortes adaptados para `crops/` nesta pasta. IDs,
  textos, sinais, estados, autores, horários e proveniência foram preservados.
- `crops/`: os 15 recortes, comparados pixel a pixel com a imagem original.
- `crop_path_mapping.json`: correspondência entre caminhos locais e publicados.
- `workspace.zip`: cópia integral dos 65 arquivos do workspace, incluindo as
  revisões imutáveis, ponteiro atual, recortes, recibos das duas execuções,
  scripts locais de preparação, exportações e imagens do editor. Os caminhos
  e bytes originais estão preservados dentro do ZIP.
- `workspace_files.json`: inventário dos caminhos e hashes originais do ZIP.
- `app_configuration.toml`: configuração em uso, copiada sem alteração.
- `verification.json`: validação do catálogo e restauração do ZIP conferidas.
- `inventory.json`: hashes dos arquivos publicados nesta pasta, exceto ele próprio.

As notas históricas de preparação dentro dos registros continuam literais;
os campos `review_status`, `geometry_status` e `transcribed_coverage` do estado
atual informam as aprovações efetivas. Os manifests candidatos originais e os
experimentos congelados anteriores não foram sobrescritos.

## Retomada nesta máquina

O workspace local já contém esse estado. Na raiz do projeto:

```powershell
.venv/Scripts/python.exe -m paleographia serve --config configs/traslado_269r.toml --host 127.0.0.1 --port 8011
```

Abra `http://127.0.0.1:8011/` e selecione a linha **11**. Confira as linhas 11–15
no manuscrito, preservando grafia, sinais e quebras. Valide texto e geometria
individualmente; a confirmação de cobertura desse novo bloco é separada.
As linhas 16–24 ainda não foram preparadas no editor.

## Recuperação em um clone novo

Depois de instalar o ambiente Python descrito no projeto, recupere a edição
publicada a partir do suporte já versionado:

```powershell
python scripts/audit_traslado_experiment.py --restore-support --output output/audit_retomada_NEW
```

**Somente em clone novo, com o servidor parado e sem a pasta
`data/workspace_traslado_269r`:** extraia o ZIP a partir da raiz do repositório.
O ZIP contém o prefixo completo `data/workspace_traslado_269r/`.

```powershell
python -m zipfile -e docs/revisao_humana/traslado_269r/sessao_20261016/workspace.zip .
python -m paleographia serve --config configs/traslado_269r.toml --host 127.0.0.1 --port 8011
```

Não extraia por cima de revisões existentes. A restauração foi executada em
uma pasta nova e o estado recuperado coincidiu integralmente com o original.
É possível ler e revisar as sugestões salvas sem executar o reconhecedor.
Para novas inferências, os pesos e o runtime Docker continuam externos ao Git;
o procedimento e os hashes estão em [runtime/kraken_ppocrv6](../../../../runtime/kraken_ppocrv6/README.md).
