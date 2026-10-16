# PaleographIA — piloto de transcrição assistida

Protótipo local para importar manuscritos, conferir recortes, gerar sugestões com TrOCR, registrar revisão humana e exportar dados rastreáveis. A comparação proposta mantém o reconhecedor fixo e varia segmentação OpenCV/Kraken. Não há ajuste fino validado para português histórico nem evidência de alto desempenho.

O catálogo de 1831 contém três fólios candidatos e 94 recortes pendentes, sem linhas completas validadas. O repertório reúne 13 exemplos e seis confirmações parciais, preservando “hum” como provável. No Traslado, fólio 269r, o usuário conferiu cinco linhas completas e a cobertura somente desse bloco. A [comparação de reconhecedores com referência congelada](docs/experimentos/traslado_269r_20261016/README.md) publica predições e auditoria: CER/WER de 80,58%/100% para TrOCR e 57,02%/95,56% para PP-OCRv5 latino. As saídas ainda são inadequadas. A amostra é desenvolvimento, de um documento; não há treino nem teste reservado.

## Abrir nesta máquina

O ambiente `.venv` está instalado. Execute `start_safe.bat` ou:

```powershell
.\.venv\Scripts\python.exe -m paleographia serve --host 127.0.0.1 --port 8000
```

Abra [a interface local](http://127.0.0.1:8000). Selecione um fólio, clique numa linha, ajuste o recorte e registre sua leitura. O modelo carrega sob demanda; os resultados brutos ficam nos registros técnicos. A apresentação de sugestões está desativada porque o modelo atual não produziu leituras utilizáveis em português. Correção humana e edição modernizada continuam separadas. Marcar como validada exige conferência humana explícita.

## Instalação em outro checkout

Use Python 3.11 ou 3.12. O ambiente básico não instala PyTorch nem baixa pesos.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,pdf]"
.\.venv\Scripts\python.exe -m pip install -e ".[htr]"
.\.venv\Scripts\python.exe -m paleographia prepare-weights --config configs/trocr-download.toml --output-dir models/trocr-small-handwritten
.\.venv\Scripts\python.exe -m pytest -q
```

Os manifests versionados apontam para derivados locais ignorados. Para reproduzi-los, extraia os arquivos originais preservados e siga o [guia de execução](docs/runbook.md). Não sobrescrever manifests já revisados.

## Documentação

- [Traslado: cinco recortes candidatos prontos para revisão no editor](docs/revisao_humana/traslado_269r/conferencia_bloco.md)
- [Traslado: comparação do fólio 269 reto e confirmações parciais com imagens](docs/revisao_humana/traslado_269r/comparacao.md)
- [Acervo de Jundiaí: inventário das transcrições e proposta de mineração](docs/mineracao_acervo_jundiai.md)
- [Preparação da referência humana: 100 reto, linhas 17–21 e ponto de retomada](docs/revisao_humana/100r_17_21/conferencia.md)
- [Correções após revisão e testes de regressão](docs/correcoes_pos_revisao.md)
- [Estado do projeto para revisão](docs/guia_revisao_gpt.md)
- [Repertório de letras e abreviaturas](docs/repertorio_100r.md)
- [Apresentação das saídas em português](docs/saidas_em_portugues.md)
- [Instalação, importação, revisão, inferência e comparação](docs/runbook.md)
- [Auditoria e decisões de migração](docs/audit.md)
- [Esquema e estados de revisão](docs/data_schema.md)
- [Política de transcrição](docs/transcription_policy.md)
- [Protocolo e métricas](docs/evaluation_protocol.md)
- [Ambientes e bloqueio neural no Windows](docs/environment.md)
- [Enquadramento acadêmico pendente](docs/academic_alignment.md), [revisão bibliográfica a executar](docs/literature_review.md)
- [Fontes/condições de uso](docs/sources.md) e [Comentários sobre uso de IA](docs/ai_comments.md)

O pacote está em `src/paleographia`; CLI e API compartilham o serviço. Scripts antigos orientam à CLI, com cópias preservadas em `legacy/`. O ponteiro Git `client` foi mantido; o editor atual é HTML integrado ao backend. Código sob MIT; condições de uso dos manuscritos/edições são independentes e precisam ser verificadas antes de redistribuição.
