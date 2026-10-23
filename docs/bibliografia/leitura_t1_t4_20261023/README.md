# Leitura integral e fichamentos de T1 e T4 — 23/10/2026

Fichamentos concluídos por **Codex (IA)**, mediante leitura dos dois PDFs completos,
incluindo notas e referências: T1, 23 páginas; T4 v1, 14 páginas. As tabelas e
passagens críticas foram também conferidas nas páginas renderizadas. A leitura
das referências listadas pelos autores não implica leitura dos trabalhos citados.
Revisão humana e decisão final de inclusão na revisão sistemática: **pendentes**.

- [T1 — Muehlberger et al. (2019)](T1.md): contexto arquivístico, preparação da
  referência e limites de comparação dos casos do Transkribus.
- [T4 — Kiessling (2026), v1](T4.md): arquitetura, dados, experimentos, métricas,
  resultados negativos e condições de transferência do PP-OCRv6.
- [Fontes, hashes e cobertura da leitura](manifesto.json).
- [Nova versão do artigo e mapa das alterações](../../entregas/pi_iv_pln_20261023_fundamentacao/README.md).

Os [fichamentos parciais anteriores](../fichamentos_parciais_20261023.md) continuam
preservados como registro da consulta inicial. Este lote os sucede para T1/T4;
não altera o estado de leitura das outras doze entradas nem conclui as buscas.
T4 mantém o mesmo ID canônico de `B02-ARXIV-001`, sem contar uma nova publicação.

## Proveniência e licença das fontes

O acesso ao PDF de T1 em Edimburgo retornou bloqueio; a cópia integral foi obtida
no [repositório institucional da UCL](https://discovery.ucl.ac.uk/id/eprint/10065830/).
A ordem de autoria segue a primeira página do artigo, iniciada por Guenter
Muehlberger. T4 foi obtido no arXiv, com versão fixada em **v1**. O cabeçalho
provisório de conferência/DOI de T4 não foi usado como metadado editorial.

As cópias integrais [T1.pdf](fontes/T1.pdf) e [T4.pdf](fontes/T4.pdf) são
redistribuídas sem alteração dos bytes obtidos. Ambos os PDFs declaram
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
na primeira página. Autoria, títulos, fontes e identificadores estão nos
fichamentos e no manifesto. Essa licença pertence aos artigos, separadamente
da licença MIT do código do PaleographIA. Não foram alterados os artigos originais;
os fichamentos são paráfrases e análises novas, identificadas como tais.

## Síntese para o projeto

| Pergunta | Evidência extraída | Consequência para o PaleographIA |
| --- | --- | --- |
| PB1 — comparação de reconhecedores | T4 distingue treino do zero, pré-treino, ajuste e orçamento; T1 não padroniza seus casos como benchmark | Identificar configurações completas e a condição do experimento; evitar superioridade causal da versão |
| PB2 — referência e métricas | T1 enfatiza consistência; T4 usa NFD e conversão de espaços para U+0020 | Declarar a política local NFC e a microagregação; não transportar taxas externas |
| PB3 — domínio, erros e limites | T1 distingue busca de transcrição exata; T4 registra dependência de domínio e resultados negativos | Preservar dúvidas humanas; avaliar novos documentos antes de generalizar ou alegar economia de esforço |

Esta síntese fundamenta decisões e interpretação. Não acrescenta experimentos,
validações de linhas, evidência de ganho do ajuste fino local ou aprovação docente.
