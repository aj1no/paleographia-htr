# Execuções locais

Uma saída por execução; nunca reaproveitar um diretório com revisões/predições. Os diretórios gerados são ignorados pelo Git. Configuração resolvida e manifests com hashes ficam junto da execução. O relatório consolidado é `docs/execution_report.md`.

A [entrega versionada do Traslado 269r](../docs/experimentos/traslado_269r_20261016/README.md)
preserva cópias literais da execução inicial do TrOCR e da comparação PP-OCRv5
latino, com referência humana congelada, mapeamento de caminhos e auditoria
offline. As execuções originais ignoradas não foram movidas ou reescritas.

`comparison_initial` e `training_dry_run` registram bloqueios reais por falta de revisão e splits, sem resultados de HTR inventados. Testes de integração usam fixtures sintéticas e não são experimentos acadêmicos.
