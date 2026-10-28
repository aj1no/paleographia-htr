# Aplicação do novo recorte da primeira linha — 28/10/2026

A observação 026 aprovou explicitamente a proposta com topo em 305, mantendo base 377 e laterais 95/1030. O recorte anterior continua na preparação congelada e nas revisões anteriores. A nova imagem em `linha01_recorte_aprovado.png` é uma cópia literal do arquivo derivado pelo serviço e tem os mesmos pixels da proposta aprovada.

O fluxo existente foi corrigido em `ReviewService.update_line`: quando a caixa muda e a linha já possui `crop_sha256`, esse hash é atualizado para o novo arquivo. A falha foi reproduzida por um teste de regressão da API; após a correção, os 19 testes de `tests/test_api.py` e `tests/test_data.py` passaram. Os testes usam imagens sintéticas e reconhecedores simulados. Nenhuma inferência real, treinamento ou cálculo de métricas foi executado.

O servidor local foi reiniciado para carregar a correção; o catálogo antes da aplicação permaneceu igual. A mudança foi realizada pela API com controle da revisão esperada, preservando ID, texto, fonte, ordem, demais linhas e predições. O bloqueio geométrico por corte foi removido porque a causa foi resolvida por aprovação humana; isso não aprovou a transcrição nem a tornou elegível para treino.

O contorno candidato do bloco foi ampliado no topo para conter a nova caixa. Isso não é confirmação de cobertura textual: `complete=false`, `review_status=pending_review` da cobertura e correspondência documental pendente foram preservados. As oito geometrias estão validadas e os oito textos continuam pendentes.

A exportação nativa aponta ao recorte derivado no workspace local. A cópia versionável, o caminho de destino e o hash estão em `aplicacao_recorte_aprovado.json`; em outro checkout, o arquivo pode ser materializado nesse destino a partir da cópia, sem importar um catálogo sobre um workspace já revisado.
