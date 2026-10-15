# Entrega e verificações — 15/10/2026

Trabalho local na branch `codex/refatoracao-piloto`, baseada em `origin/master` (`2ab24deaa183373bc0926966cbd474a9dde985cb`). Alterações ficam disponíveis para revisão no working tree. Não houve push, merge, publicação de dados ou treinamento longo.

## Implementação entregue

- Pacote importável em `src/paleographia`, configuração TOML e CLI única: inventário/extração, associação explícita, validação, splits persistidos, segmentação, inferência, avaliação, comparação, revisão, exportação e treino com dry run padrão.
- JSONL de páginas e linhas com fonte/checksum, geometria, documento/fólio/região, textos distintos, estados e autoria de revisão. Validação bloqueia modernização usada como referência diplomática, dados ausentes/incoerentes e vazamento por grupos/fontes/derivados.
- OpenCV reaproveita contornos e perfil horizontal. Crops vêm dos pixels originais; binarização somente detecta. Adaptador Kraken 6 usa worker separado com peso explícito, baselines/polígonos e bbox documentada. **Worker neural ainda não executado com pesos reais**.
- TrOCR usa processador/modelo do mesmo checkpoint, sem carregamento na importação, sem fallback, CPU/precisão explícitas, geração configurável, IDs/tokens/predição bruta, detecção do limite e carregamento serializado. Pesos preparados explicitamente e identificados pelo snapshot/hash.
- API e editor de revisão: upload, seleção/desenho/ajuste de linhas, ordem, correção humana e edição modernizada separadas, rejeição, confirmação explícita de revisão, entrega efetiva dos crops e exportação. Snapshots imutáveis e conflito de revisão impedem sobrescrita de estado desatualizado. Um processo local por workspace.
- CER/WER por contagens microagregadas, omissões e espúrias na avaliação principal de região; diagnóstico geométrico e por linha; comparação guarda falhas, tempos, configuração, versões e análise de erros quando os dois métodos forem executáveis.
- Código de ajuste fino condicionado a dados aptos: processador único, labels com padding mascarado, alvos excedentes reportados, deslocamento interno do decodificador, semente, seleção pela validação, teste reservado e modelo/processador salvos juntos. **Nenhum fine-tuning foi executado**.
- Scripts legados preservados em `.py.txt` e desativados no caminho padrão; READMEs corrigidos, CI offline leve preparada para Windows/Linux e Python 3.11/3.12. Política de transcrição, protocolo, enquadramento acadêmico, busca bibliográfica a executar e Comentários sobre IA documentados.

## Dados realmente disponíveis

Extração dos arquivos versionados: 34 JPEGs e 8 PDFs, com nomes de membros e hashes em `data/manifests/archive_members.json`. Há outros documentos/fotos para identificação; não são automaticamente o mesmo corpus.

Piloto: três fólios candidatos da sessão de 11/07/1831, com **94 recortes pendentes**: 32 no 100r, 30 no 100v e 32 no 101r. **Zero referências paleográficas validadas por humano**. Documento e limites da cobertura ainda requerem confirmação; o catálogo não afirma identidade de escriba.

Os 542 registros do CSV legado não foram promovidos a referência. Seus 542 caminhos de crops não estavam presentes neste checkout e há conteúdo editorial nos rótulos. Contagem e checksums dos arquivos originais estão em `legacy_inventory.json`. `git diff --exit-code -- data/raw data/processed/train/metadata.csv` confirmou que os dados versionados originais permaneceram intactos.

## Verificações executadas

| Verificação | Resultado efetivo |
|---|---|
| `python -m pytest -q --junitxml=experiments/tests-github.xml` | **32 passaram**, um aviso de depreciação em Starlette/AnyIO |
| `python -m compileall -q src server tests scripts` | Sem erro de compilação |
| `python -m paleographia --help` | CLI disponível com comandos reais |
| `python -m pip check` | Sem dependências quebradas |
| Importação de módulos sem torch/transformers | Teste passou, sem rede/GPU/pesos |
| Materialização dos crops persistidos | 94 já existentes e preservados; reconstrução/idempotência e recusa a sobrescrita verificadas em fixture sintética |
| Validação do catálogo | Aceita pendências para revisão |
| Validação para avaliação / dry run de treino | Recusados: revisão, cobertura e protocolo ainda ausentes |
| API com reconhecedor de teste | Upload inválido, indisponibilidade 503, processamento, crop, revisão, conflito, exportação e recuperação após reinício passaram |
| API com modelo real | 32 recortes reconhecidos, zero falhas de processamento |
| Navegador | Fólio/crop/sugestão visualizados; rascunho pendente salvo; conflito durante reconhecimento concorrente retornou 409 e foi resolvido com recarga, sem perder dados |

As fixtures são marcas sintéticas e os reconhecedores de teste estão apenas em `tests/`; não contam como resultados científicos de HTR. A matriz remota de CI foi configurada, mas não foi executada no GitHub nesta entrega.

## Inferência real — diagnóstico de integração, sem métricas de qualidade

Modelo: `microsoft/trocr-small-handwritten`, snapshot `b4648cfa171985a6745f37ddd637e98c0da958ac`, preparado em `models/trocr-small-handwritten`, processador do mesmo diretório, CPU/float32. Não há checkpoint especializado treinado neste corpus. Geração: máximo de 128 tokens novos, um beam, sem amostragem, penalidade de repetição 1.0.

1. CLI: três recortes reais (ordem operacional 10 em cada fólio), em `experiments/real_inference_smoke`. Zero falhas. Carregamento inicial de aproximadamente 24,72 s; inferências de 1,37 s, 0,83 s e 1,06 s. Não houve sinal de truncamento.
2. API: 32 recortes do 100r, em `data/workspace/predictions/`, reportados em `experiments/api_real_inference/report.json`. Tempo externo total **58,60 s**, incluindo **19,51 s** de carregamento; soma dos tempos de reconhecimento **38,79 s**. Zero falhas e zero sinais de truncamento. Os tempos valem para esta execução, sem promessa de duração futura.

**As saídas foram inadequadas para transcrição histórica**: apareceram frases em inglês sem correspondência útil com o manuscrito. Exemplo bruto do smoke: “After duty with his military program also is”. O fato de não haver erro HTTP/processamento não implica leitura correta. CER/WER não foram calculados porque não existe referência humana validada. Não houve substituição das saídas por uma transcrição produzida pelo agente.

O carregamento relatou chaves ausentes do pooler do encoder (`encoder.pooler.dense.*`); o aviso e as informações de carregamento foram preservados. Não foi interpretado como ajuste fino concluído. Na preparação ocorreram falhas iniciais de certificado da rede e de symlinks, resolvidas com certificados confiáveis do Windows e download para arquivos regulares, mantendo TLS verificado.

## Não executado e bloqueios objetivos

- **Avaliação e comparação acadêmica**: não executadas; zero referências humanas, correspondências/coberturas pendentes e nenhum split final. `experiments/comparison_initial/comparison.json` registra o bloqueio; não há tabela de resultados simulados.
- **Kraken real**: tentativa de segmentação informou peso ausente. A checagem binária no Windows falhou por falta de distribuição de `coremltools ~=8.1` compatível com Kraken 6.0.0. NumPy também exige ambiente separado. A API foi conferida no código primário da versão, mas a instalação/inferência do worker deve ser validada num ambiente compatível. Instruções em `environment.md`.
- **Treino**: dry run recusado; faltam referência humana e grupos independentes. O corpus candidato tem uma sessão documental. Não quebrar artificialmente fólios/derivados para conseguir três conjuntos.
- **Fontes e disciplina**: faltam vínculos individuais/permissões de redistribuição, revisão dos créditos, confirmação da identidade/datas dos documentos fora do piloto e os PDFs acadêmicos citados na especificação. Enquadramento com PI IV/PLN ainda precisa do professor. Revisão bibliográfica tem protocolo, sem artigos integralmente fichados ou contagens inventadas.
- **Frontend legado**: gitlink mantido, origem/commit não recuperáveis no checkout obtido. A interface local mínima foi implementada e testada; não foi declarada recuperação do Next.js.

## Próximas ações verificáveis

1. Conferir documento e cobertura no 100r e nos outros dois fólios. Separar o trecho anterior à linha editorial 17; os índices automáticos não são numeração editorial.
2. Ajustar recortes/ordem e revisar inicialmente cinco linhas, depois atingir 30–50 em regiões completas, seguindo `transcription_policy.md`. Identificar o revisor e registrar exclusões previamente.
3. Exportar a seleção revisada para novos manifests, validar e persistir split exploratório da sessão única. Congelar parâmetros antes de observar resultados do experimento.
4. Preparar runtime/peso neural em ambiente compatível e executar a comparação com o TrOCR fixo e o controle humano. Registrar também os resultados ruins.
5. Confirmar enquadramento com o professor, completar busca bibliográfica/condições de uso e só considerar fine-tuning após ampliar os grupos e definir protocolo defensável.

Comandos completos e etapas humanas em `runbook.md`. Para abrir agora: `start_safe.bat` ou `.\.venv\Scripts\python.exe -m paleographia serve --host 127.0.0.1 --port 8000`, depois `http://127.0.0.1:8000`.

## Atualização da revisão colaborativa e da publicação

O repertório do 100r tem 13 exemplos e seis confirmações parciais do usuário: a–r–t nos dois exemplos de Artigo; projecto, posturas, ofensivas com um f e defensivas. Hum permanece provável. Esses registros não equivalem a linhas integralmente validadas. As versões anteriores do catálogo foram preservadas.

A interface passou a apresentar avisos em português e mantém indisponíveis as sugestões do reconhecedor inadequado. Os resultados brutos continuam nos registros técnicos. O comparativo qualitativo com a edição está em `diagnostico_reconhecimento.json`; não há métricas acadêmicas.

Foi acrescentada a reconstrução dos recortes do repertório a partir do catálogo existente, sem sobrescrever confirmações. A cópia visual para revisão no GitHub está em `repertorio/`. O guia `guia_revisao_gpt.md` apresenta o estado e as perguntas para a análise.

## Correções posteriores à revisão de 756492c — 15/10/2026

Os resultados acima pertencem à entrega inicial. A atualização corrige validação
global de partições, preservação de regiões/proveniência e rascunhos da interface.
Verificações locais: 46 testes Python e 16 testes em DOM simulado passaram;
compilação, instalação, CLI e dependências também passaram. Houve conferência
em navegador real em instância sintética isolada, incluindo conflito 409 e
reabertura. Os 274 arquivos anteriores conferidos por hash permaneceram intactos.
Detalhes e limites: [correcoes_pos_revisao.md](correcoes_pos_revisao.md).
Não houve novos resultados de HTR ou validação humana do acervo.

## Início da preparação da referência humana — 15/10/2026

Foram preparados cinco recortes consecutivos correspondentes às linhas editoriais
17–21 do 100 reto, dentro do trecho coberto pela página 3 da edição modernizada.
O revisor identificou-se como Rodolfo Vinícius Cima Takemoto e confirmou
parcialmente a abertura «Leu se», com u. A hipótese anterior «Leo se» e sua
pesquisa histórica foram preservadas como etapa anterior.

«Hum» continua provável; «com/em treze», hífen, caixa, geometria e abreviatura
final continuam em conferência. Os sinais superiores parecem «es» ao revisor,
sem resolução da abreviatura. Zero linhas completas ou coberturas foram
validadas; não houve inferência real, treino ou métricas nesta sessão.
O catálogo e as revisões anteriores não foram alterados.

O [caderno da sessão](revisao_humana/100r_17_21/conferencia.md) reúne os recortes,
as observações e o ponto de retomada. O manifesto `preparacao.json` no mesmo
diretório conserva as mensagens de origem e as coordenadas; `arquivos.json`
registra os hashes da cópia publicada.
