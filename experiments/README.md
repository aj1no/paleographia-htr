# Execuções locais e evidências publicadas

Uma saída por execução; nunca reaproveitar um diretório com revisões/predições.
Os diretórios gerados aqui são ignorados pelo Git. Configuração e manifests com
hashes ficam junto da execução. O [índice da documentação](../docs/README.md)
indica o estado atual; `docs/execution_report.md` é um relatório histórico.

## Entrega atual — 20/10/2026

- [Comparação PP-OCRv5 × PP-OCRv6 em 24 recortes](../docs/experimentos/traslado_269r_reconhecedores_24_20261020/README.md).
- [Notebook, artigo e evidências](../docs/entregas/pi_iv_pln_20261020/README.md).
- [Referência assistida e oito ressalvas](../docs/revisao_humana/traslado_269r/referencia_assistida_20261020/README.md).

Diagnóstico de desenvolvimento de um documento, sem treino ou teste reservado.

## Histórico

A [entrega versionada do Traslado 269r](../docs/experimentos/traslado_269r_20261016/README.md)
preserva cópias literais da execução inicial do TrOCR e da comparação PP-OCRv5
latino, com referência humana congelada, mapeamento de caminhos e auditoria
offline. As execuções originais ignoradas não foram movidas ou reescritas.
TrOCR está bloqueado para novas execuções. A [integração inicial do PP-OCRv6](../docs/experimentos/traslado_269r_ppocrv6_20261016/README.md)
nas cinco primeiras linhas também permanece publicada.

`comparison_initial` e `training_dry_run` registram bloqueios reais por falta de revisão e splits, sem resultados de HTR inventados. Testes de integração usam fixtures sintéticas e não são experimentos acadêmicos.
