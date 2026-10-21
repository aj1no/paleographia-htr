# Protocolo de revisão bibliográfica — ainda não executado

Registrar data, base, consulta exata, filtros, total retornado, duplicatas, seleção por título/resumo, leitura integral e motivo de exclusão. Bases propostas: Google Scholar, ACM Digital Library, IEEE Xplore e arXiv; confirmar acesso e critérios com orientação de PI IV. Não há contagem de seleção ou lista de artigos cientificamente fichados nesta entrega.

Consultas iniciais propostas: `historical manuscript handwritten text recognition line segmentation`; `baseline segmentation historical documents Kraken`; `TrOCR Portuguese historical handwriting`; `segmentation impact character error rate HTR`. Período e idiomas: definir antes da busca e justificar eventuais textos fundacionais anteriores ao recorte.

Incluir trabalhos primários sobre HTR histórico e localização de linhas/baselines, com método, dados e avaliação identificáveis. Excluir duplicatas, publicidade sem avaliação, OCR exclusivamente impresso sem relação com a pergunta e trabalhos sem acesso suficiente para verificar método. Registrar exceções justificadas, sem mudar critérios para favorecer resultados.

Matriz para preencher após leitura:

| Referência/DOI/URL | Questão | Dados/idioma | Unidade/grupos | Segmentação | Reconhecedor | Métricas/protocolo | Limitações | Aplicação ao piloto |
|---|---|---|---|---|---|---|---|---|

Fontes técnicas consultadas para implementar APIs (não contadas como revisão sistemática):

- [Documentação TrOCR](https://huggingface.co/docs/transformers/v4.57.1/en/model_doc/trocr)
- [Seq2SeqTrainer e argumentos](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/trainer)
- [Model card do small](https://huggingface.co/microsoft/trocr-small-handwritten)
- [Código primário Kraken 6.0.0 blla](https://raw.githubusercontent.com/mittagessen/kraken/6.0.0/kraken/blla.py)
- [Dependências Kraken 6.0.0](https://pypi.org/pypi/kraken/6.0.0/json)

O artigo [TrOCR, Li et al.](https://arxiv.org/abs/2109.10282) é candidato para leitura/fichamento; não foi declarado integralmente lido. Registre fichamento com objetivo, desenho experimental, resultados, limitações e relação concreta com RQ1–RQ3.
