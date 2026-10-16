# PaleographIA — piloto de transcrição assistida

Protótipo local para importar manuscritos, conferir recortes, gerar sugestões experimentais com PP-OCRv6/Kraken, registrar revisão humana e exportar dados rastreáveis. A comparação posterior de segmentadores manterá o reconhecedor fixo. Não houve ajuste fino neste projeto; o reconhecimento ainda exige correção humana.

O catálogo de 1831 contém três fólios candidatos e 94 recortes pendentes, sem linhas completas validadas. O repertório reúne 13 exemplos e seis confirmações parciais, preservando “hum” como provável. No Traslado, fólio 269r, o usuário conferiu cinco linhas completas e a cobertura somente desse bloco. A [avaliação e integração do PP-OCRv6](docs/experimentos/traslado_269r_ppocrv6_20261016/README.md) obteve CER/WER de **12,40%/51,11%**, com saídas relacionadas ao manuscrito e sugestões experimentais no editor. Os resultados históricos de TrOCR (80,58%/100%) e PP-OCRv5 latino (57,02%/95,56%) permanecem preservados. A amostra é desenvolvimento, de um documento; não há treino nem teste reservado. TrOCR está desativado para novas execuções.

## Abrir nesta máquina

O ambiente `.venv` está instalado. Execute `start_safe.bat` ou:

```powershell
.\.venv\Scripts\python.exe -m paleographia serve --host 127.0.0.1 --port 8000
```

Abra [a interface local](http://127.0.0.1:8000). Para o Traslado, inicie com `--config configs/traslado_269r.toml --port 8011` e abra [o editor experimental](http://127.0.0.1:8011/). Selecione o fólio e clique em **Testar reconhecedor**. O modelo carrega sob demanda; a proposta fica separada da correção humana e da edição. Marcar como validada exige conferência humana explícita. As sugestões do piloto de 1831 continuam desativadas.

## Instalação em outro checkout

Use Python 3.11 ou 3.12. O ambiente básico não instala PyTorch nem baixa pesos.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,pdf]"
.\.venv\Scripts\python.exe -m pytest -q
```

Para reconhecer, prepare separadamente o [runtime Linux do Kraken](runtime/kraken_ppocrv6/README.md). A instalação básica não instala seus pesos ou dependências. Para reconstruir derivados e revisão, siga o [guia de execução](docs/runbook.md). Não sobrescrever manifests já revisados.

## Documentação

- [PP-OCRv6: cinco leituras reais, métricas e integração experimental](docs/experimentos/traslado_269r_ppocrv6_20261016/README.md)
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
