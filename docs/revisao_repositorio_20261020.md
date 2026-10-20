# Revisão do repositório — 20/10/2026

Base: `3a629e316e7f0485bc8eaec2ad2c882d3bb3a749`, branch
`codex/refatoracao-piloto`, sincronizada com a origem no início da revisão.
Escopo: estrutura, documentação de entrada, comandos, referências legadas,
testes e integridade. Não é auditoria exaustiva de segurança ou dependências.

**Desdobramento posterior à revisão:** os seis auxiliares aprovados foram
arquivados em [legacy/auxiliares_20261020](../legacy/auxiliares_20261020/README.md),
com caminhos, hashes e commit de origem. A descrição abaixo preserva as
constatações da revisão anterior ao arquivamento; os demais candidatos permanecem.

## Visibilidade no GitHub

A API do GitHub confirmou `main` como branch padrão, no commit
`701dec4ad62863be119260bbe381a88af7c240c0`. Seu README ainda está em inglês e
anuncia TrOCR especializado, ajuste fino e Next.js como recursos atuais, sem
corresponder ao piloto desta branch. A descrição pública também atribui o sistema
ao TrOCR. Portanto, quem abre a página inicial do repositório não vê a entrega
mais recente da `codex/refatoracao-piloto`.

Esta revisão não altera branch padrão, descrição remota ou `main`, nem faz
mesclagem. Para apresentar esta entrega, use o endereço da branch de trabalho.
Uma descrição sugerida, para decisão posterior do responsável, é:
“Protótipo local de transcrição assistida de manuscritos históricos de Jundiaí,
com revisão humana rastreável e comparação de reconhecedores.”

## Constatações e correções

| Constatação | Efeito | Correção |
| --- | --- | --- |
| READMEs ainda descreviam cinco ou 10–15 linhas | Ocultavam a referência atual e misturavam amostras | Entrada principal em português: 24 linhas, oito ressalvas, métricas e links atuais; caminho português mantido como referência |
| Guia de revisão tratava TrOCR como atual e dizia que CER/WER não haviam sido calculados | Orientava a revisão de um estado antigo | Guia atualizado com artefatos atuais e limites |
| `requirements.txt` recomendava `[htr]`; guia de ambiente indicava download TrOCR | Dependências antigas sem habilitar o modelo atual | Comentário corrigido; ambientes por finalidade e bloqueio TrOCR explícitos |
| Runbook destacava a preparação de cinco linhas, treino e segmentadores | Confusão entre preparação inicial, workspace humano e experimento atual | Roteiro atual de auditoria, importação em workspace vazio, revisão e exportação |
| Declaração de IA atribuía sugestões atuais ao TrOCR | Não refletia os componentes utilizados | Declaração atualizada, com histórico distinguido |
| Contribuição pressupunha partir de `main`; execuções apontavam apenas para relatório antigo | Orientação incompatível com esta entrega | Branch, verificações e referências corrigidas |
| Faltava índice entre guias e registros datados | Relatórios antigos pareciam orientação atual | Criado `docs/README.md` |

## Componentes e candidatos a organização

| Caminho/componente | Papel e decisão |
| --- | --- |
| `src/paleographia/`, `src/paleographia/web/` | Implementação atual; `api.py` serve a interface desse pacote |
| PP-OCRv6/Kraken 7.1, configuração 269r e runtime Docker | Reconhecimento experimental atual, com identidades fixadas |
| PP-OCRv5/ONNX e `scripts/recognize_latin.py` | Usados no experimento acadêmico; não são código abandonado |
| Materializadores e repertório de 1831 | Reconstrução do catálogo anterior; mantidos e testados |
| `scripts/prepare_traslado.py`, `data/manifests/traslado_269r/` | Preparação inicial de cinco linhas; não substituir a referência humana final |
| TrOCR, `configs/trocr-download.toml`, extra `[htr]` e código antigo de treino | Fora do fluxo atual, bloqueado. Candidatos a isolamento posterior com análise de importações/testes; treino Kraken não implementado |
| `neural_worker.py`, Kraken 6 e `compare` | Rota secundária de segmentação, não medida; distinta do reconhecimento Kraken 7.1 e do experimento de dois reconhecedores |
| Scripts numerados da raiz | Wrappers que interrompem o fluxo antigo e indicam a CLI; remoção mudaria compatibilidade |
| `legacy/*.py.txt` | Cópias literais dos originais auditados; não executar nem apagar como sobra |
| `docs/experimentos/implementation_31997a4/`, `implementation_3284e07/` | `frozen_experiment.artifact_for_hash` consulta essas cópias por hash; necessárias à auditoria |
| `server/main.py` | Entrada ASGI de compatibilidade que delega ao pacote atual |
| `index.html` da raiz | Página antiga, não servida por `api.py`; candidata a arquivamento após conferir uso externo |
| `client` | Gitlink histórico, modo 160000, sem `.gitmodules`; não é a interface atual. Origem não recuperada nesta revisão |
| `test_encoding.py` | Diagnóstico antigo com `fitz`/PyMuPDF e caminho específico; fora da suíte em `tests/`. Não justifica dependência básica nova |
| `downloads_list.txt`, `downloads_utf8.txt`, `train_log.txt`, `server/Texto importantes.txt` | Auxiliares antigos sem referência identificada na execução atual inspecionada. Candidatos a arquivamento; pode haver uso externo |

## Volume e preservação

Inventariados **606 arquivos regulares versionados**, mais o gitlink `client`.
Antes das edições, `data/` ocupava aproximadamente 70,4 MB e `docs/` 38,9 MB em
arquivos regulares versionados. São tamanhos do conteúdo atual, não do histórico
Git ou de um clone completo. Os cinco maiores arquivos são os ZIPs/RAR originais;
não são caches que possam ser apagados como limpeza.

Nenhum arquivo antigo foi removido ou movido. Produto, configurações, pesos,
originais, manifests, revisões, pacotes congelados e entrega acadêmica foram
preservados. Renomear ou reformatar pacotes congelados quebraria inventários.

## Verificações

| Verificação local | Resultado |
| --- | --- |
| Suíte Python | 90 testes passaram; um aviso de depreciação já existente em Starlette/AnyIO |
| Suíte do editor JavaScript | 29 testes passaram |
| Auditoria da referência assistida | 58 arquivos, 24 recortes; 16 linhas validadas e oito dúvidas preservadas |
| Auditoria do experimento | 29 arquivos conferidos; métricas reproduzidas e distâncias verificadas independentemente |
| Auditoria da entrega acadêmica | 24 arquivos conferidos, métricas idênticas, nove células executadas e duas figuras preservadas |
| Importação descrita no runbook | Catálogo congelado importado em workspace isolado; 24 linhas, 16 validadas, oito ressalvas; interface/health disponíveis sem modelo |
| Compilação e ajuda da CLI | Passaram |
| Documentação atualizada | Links locais conferidos; `git diff --check` sem erros |
| Preservação por hash | 597 arquivos versionados fora da edição e 82 arquivos dos workspaces locais idênticos |

O [recibo da revisão](revisao_repositorio_20261020.json) lista arquivos alterados,
contagens e limites. Nove arquivos existentes foram atualizados e três documentos
foram acrescentados, incluindo esse recibo. Não houve nova inferência ou reexecução
do notebook. Estas verificações são locais; uma nova CI depende de publicação.

## Pendências separadas desta revisão

1. Decidir arquivamento dos auxiliares da raiz após conferir links externos e
   compatibilidade. Preservar snapshots de implementação exigidos pelos auditores.
2. Considerar isolamento do extra `[htr]` e do código de treino bloqueado em
   alteração própria, com testes e preservação dos registros.
3. A CI não reexecuta o notebook nem seu auditor acadêmico; existem validações
   locais publicadas. Uma inclusão futura pode ser tratada separadamente.
4. Confirmar suporte e canal de segurança com o mantenedor: `SECURITY.md` se
   refere somente à `main` e não fornece contato explícito. Esta revisão não
   presume um novo compromisso de suporte.
5. Atualizar e executar o protocolo bibliográfico para os dois reconhecedores.
   O plano antigo contém consultas de segmentação/TrOCR e não é revisão concluída.
6. Decidir como apresentar a versão atual no GitHub: descrição e branch padrão
   continuam antigas. Qualquer alteração de apresentação ou integração deve
   respeitar a preservação das branches e do histórico.

Relatórios de 15–19/10 e pacotes publicados preservam o estado de cada etapa.
A atualização dos guias não deve reescrever evidências para fazê-las parecer atuais.
