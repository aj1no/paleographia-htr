# PaleographIA — transcrição assistida de manuscritos

Piloto local para importar imagens, conferir recortes, registrar revisão humana e
construir um repertório paleográfico rastreável. A interface de revisão e suas
mensagens são apresentadas em português.

O catálogo reúne três fólios candidatos de 1831 e 94 recortes pendentes. O
repertório do fólio 100 reto contém 13 exemplos, com seis confirmações parciais
do usuário. Nesse catálogo de 1831, nenhuma linha foi integralmente validada.
“Hum” permanece como leitura provável.

A revisão do Traslado do Auto de Criação da Vila começou pelo fólio 269 reto,
com 24 linhas candidatas da edição. **Cinco linhas do corpo foram integralmente
conferidas pelo usuário**, incluindo geometria, correspondência e cobertura
somente desse bloco. O
[caderno do Traslado](docs/revisao_humana/traslado_269r/comparacao.md) inclui
imagens e histórico da preparação. A [referência congelada e comparação de
reconhecedores](docs/experimentos/traslado_269r_20261016/README.md) publica
manifests, configurações, predições, métricas, hashes e auditoria offline.
Na mesma amostra de desenvolvimento, TrOCR teve CER/WER de 80,58%/100% e
PP-OCRv5 latino, 57,02%/95,56%. Ambos continuam inadequados para leitura automática.

O TrOCR disponível foi executado em 3 recortes de diagnóstico e nos 32 recortes
do 100r. As saídas foram inadequadas. A interface informa a indisponibilidade de
leitura automática utilizável em português; os resultados brutos são preservados
nos registros técnicos. Essa mudança de apresentação não melhora o reconhecedor.

```powershell
# Python 3.11 ou 3.12
python -m pip install -e ".[test]"
python -m pytest -q
python -m paleographia serve --host 127.0.0.1 --port 8000
```

Abra [a revisão local](http://127.0.0.1:8000) ou
[o repertório](http://127.0.0.1:8000/repertorio).
Para reconstruir imagens e inicializar um checkout novo, siga o
[guia de execução](docs/runbook.md). A instalação básica e os testes não baixam
pesos nem exigem GPU.

- [Guia para revisar o estado atual do projeto](docs/guia_revisao_gpt.md)
- [Acervo de Jundiaí e proposta de mineração](docs/mineracao_acervo_jundiai.md)
- [Instruções completas](README.pt-br.md)
- [Relatório de execução e limites](docs/execution_report.md)
- [Repertório e exemplos visuais](docs/repertorio_100r.md)
- [Auditoria](docs/audit.md), [política de transcrição](docs/transcription_policy.md)
  e [protocolo de avaliação](docs/evaluation_protocol.md)

Código sob MIT. Os documentos históricos e suas edições têm condições de uso
independentes. Os arquivos originais e o ponteiro do cliente legado foram
preservados; a interface atual está integrada ao servidor local.
