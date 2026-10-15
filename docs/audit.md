# Auditoria do checkout — 15/10/2026

O diretório recebido continha somente `.git`, sem commits, remoto ou alterações do usuário. Foi configurado `origin` para `https://github.com/aj1no/paleographia-htr.git` e feito fetch. Não houve push, merge nem modificação remota.

| Ref inspecionada | Commit | Constatação |
|---|---|---|
| origin/main | 701dec4ad62863be119260bbe381a88af7c240c0 | Base curta, sem servidor completo |
| origin/master | 2ab24deaa183373bc0926966cbd474a9dde985cb | Scripts, servidor, metadados e arquivos compactados |

Base escolhida: `origin/master`; branch local `codex/refatoracao-piloto`. Não foram encontrados AGENTS.md no checkout nem nos diretórios ancestrais consultados. `core.longpaths=true` foi necessário no Git local para restaurar um nome legado longo no Windows.

## Fatos confirmados

- Scripts 2/3 associavam páginas por posição; o 3 removia diretórios com `rmtree`. Scripts 4/7 associavam texto a recortes pela posição; o 7 descartava excedentes usando `min`.
- `metadata.csv` contém o título editorial “Transcrição das Atas da Câmara Municipal” entre os alvos. O CSV inteiro permanece legado não validado, sem migração para ground truth.
- Script 8 usa small no dataset e base nas métricas; split aleatório por linha sem semente. Script relâmpago não separa avaliação e promete tempo fixo. Script de inferência não distingue página de linha.
- Servidor antigo carregava pesos durante importação, escolhia fallback por existência de pasta, tinha geração fixa, não servia os crops e convertia HTTP 400 em 500. A explicação de greedy era incorreta.
- `client` tem modo Git 160000, commit `154677e3f3547c8a73aac174b5ed018f29640d9e`. Não há `.gitmodules`; o objeto não está no banco de objetos obtido e não há árvore recuperável local. Isso não prova que seja irrecuperável em outras origens. O gitlink foi preservado. Foi entregue editor HTML local integrado ao FastAPI; nenhuma migração de framework foi tentada.
- Requisitos legados não tinham versões; CI somente compilava. Havia ignore global de imagens/PDFs. Foram substituídos por dependências opcionais, versões diretas e testes offline, com ignores por diretório.

## Fontes efetivamente encontradas

Quatro ZIPs e um RAR já estavam versionados em `data/raw`. Extração nova em `data/raw/import_20261015`, sem mover/renomear os originais: **34 JPEGs e 8 PDFs**. O arquivo `extraction.json` preserva membro, arquivo de origem e checksums. As 27 fotos dos ZIPs continuam sem identificação documental. Os sete JPEGs do RAR incluem os três candidatos de 1831 e documentos de outros contextos. Não foram interpretados como 34 documentos independentes.

Os três candidatos de 1831 estão explicitamente listados no script `scripts/prepare_pilot.py`, pelo identificador do membro extraído; não pela posição no diretório. A inspeção das imagens e da edição é compatível com 100r, 100v e 101r, mas a correspondência continua `pending_review`. Identidade de escriba não foi estabelecida.

A edição de 1831 encontrada tem **8 páginas**: advertência, critérios, transcrição nas páginas 3–5 e reproduções nas páginas 6–8. A página 3 contém trechos de dois fólios e a 4 também atravessa a mudança de fólio. As reproduções não foram importadas como fontes independentes de treino. O texto anterior à linha editorial 17 no 100r exige delimitação da cobertura; ainda não há caixa humana confirmada para esse limite.

Permanece a divergência 1751 no nome do diretório de Thomas Pardo versus 1759 indicado no diagnóstico. Não houve alteração de data com base no nome do arquivo. Outros materiais e PDFs acadêmicos citados na especificação não foram encontrados nas entradas do projeto e não foram procurados fora delas.

## Migração e decisões

Originais dos scripts foram copiados byte a byte para `legacy/*.py.txt`; os pontos de entrada antigos agora orientam para a CLI, impedindo o fluxo destrutivo padrão. O servidor é um wrapper ASGI. Dados antigos permanecem intactos.

Arquitetura: pacote Python importável, TOML, JSONL, serviço compartilhado por CLI/API, checkpoints sob demanda e histórico imutável por revisão. A aplicação deve usar **um processo local**; o lock é por processo e não constitui armazenamento distribuído. Não executar editores/CLIs mutantes concorrentes no mesmo workspace.

Um ensaio de desenvolvimento com contornos produziu 11 candidatos; o perfil horizontal produziu 94 (32/30/32 em 100r/100v/101r). As duas saídas foram preservadas. São contagens de recortes, sem anotação humana ou afirmação de qualidade. Não havia teste reservado durante esse diagnóstico. A configuração deve ser congelada antes do experimento final.

## Pendências externas

Referências humanas: zero. Delimitação integral das regiões: pendente. Treino/validação/teste entre documentos: inviável com a única sessão candidata atual. Aprovação do enquadramento acadêmico: pendente. Kraken e pesos neurais: execução independente ainda necessária. Ver `execution_report.md` para o estado medido e `environment.md` para os ambientes.
