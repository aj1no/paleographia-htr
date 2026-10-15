# PaleographIA — transcrição assistida de manuscritos

Piloto local para importar imagens, conferir recortes, registrar revisão humana e
construir um repertório paleográfico rastreável. A interface de revisão e suas
mensagens são apresentadas em português.

O catálogo reúne três fólios candidatos de 1831 e 94 recortes pendentes. O
repertório do fólio 100 reto contém 13 exemplos, com seis confirmações parciais
do usuário. Ainda há **zero linhas integralmente validadas** para treino ou
avaliação. “Hum” permanece como leitura provável.

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
- [Instruções completas](README.pt-br.md)
- [Relatório de execução e limites](docs/execution_report.md)
- [Repertório e exemplos visuais](docs/repertorio_100r.md)
- [Auditoria](docs/audit.md), [política de transcrição](docs/transcription_policy.md)
  e [protocolo de avaliação](docs/evaluation_protocol.md)

Código sob MIT. Os documentos históricos e suas edições têm condições de uso
independentes. Os arquivos originais e o ponteiro do cliente legado foram
preservados; a interface atual está integrada ao servidor local.
