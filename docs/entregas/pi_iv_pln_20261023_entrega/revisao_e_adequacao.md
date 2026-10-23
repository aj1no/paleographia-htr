# Revisão integral e adequação da versão de entrega

Revisor desta etapa: **Codex (IA), 23/10/2026**. O trabalho incluiu leitura de
todo o artigo, cotejo das citações com as fontes disponíveis, conferência do
desenho experimental e revisão visual de todas as páginas finais. A revisão
dos autores e eventual aprovação dos professores não foram atribuídas à IA.

## Correções e integração

| Ponto revisto | Tratamento na versão preparada |
| --- | --- |
| Coerência entre pergunta, método e conclusão | Mantido diagnóstico de duas configurações nas mesmas 24 linhas; conclusão limitada ao documento de desenvolvimento |
| Fundamentação de T1 | Liga fluxo arquivístico, consistência textual e revisão humana, sem transformar casos heterogêneos em benchmark |
| Fundamentação de T4 | Liga pré-treino/adaptação, métricas e domínio à interpretação local; resultados negativos não são previsão do ajuste local |
| Artigo e checkpoint de Kiessling | 2026a identifica o preprint v1; 2026b, a ficha Zenodo. Explicita divergências de altura/cobertura entre as descrições, sem presumir identidade de protocolos ou afirmar que os pesos são outros |
| Evidência versus comparação externa | NFD/macro externos e NFC/micro locais permanecem distintos; nenhum resultado externo entrou na tabela do projeto |
| Arredondamento | Explicita que a diferença de CER de 43,35 pontos é calculada nas contagens antes do arredondamento; subtrair somente 58,45 e 15,11 produz 43,34 |
| Referências | Oito entradas em ordem alfabética; todas citadas e sem citação órfã. T4 referenciado por URL da v1; DOI pendente no registro não é necessário para identificá-lo |
| Fonte documental | Ficha do traslado e autoria da edição distinguidas; produção em 1767 e evento de 1656 não se confundem |
| Resumos | Resumo e abstract apresentam as mesmas configurações, quatro taxas, ressalvas e limites; cinco palavras-chave em cada idioma |
| Forma do artigo | Retirados avisos de rascunho e códigos internos T1/T4 do corpo. Mantidas as qualificações científicas relevantes |
| Tabelas e figura | Tabela principal com CER/WER e contagens no texto. Removida a figura que repetia as quatro taxas; o gráfico original permanece nas versões históricas |
| Reconferência | Síntese no artigo; tabela integral continua no notebook e nos registros preservados, sem promoção de oito ressalvas |
| IA | Nome e função dentro de Comentários no próprio artigo; reconhecedores e revisão humana distinguidos |

## Conferência das citações

| Entrada | Evidência efetivamente consultada | Uso no artigo |
| --- | --- | --- |
| Sousa e Trippel (2006) | Registro e resumo da ACL; escopo parcial conservado | Reestruturação, marcação e padrões abertos em corpus histórico |
| Muehlberger et al. (2019) | PDF completo preservado, 23 páginas; p. 958–963 para as afirmações usadas | Fluxo HTR, consistência e distinção entre busca e transcrição |
| Cui et al. (2025) | Registro/resumo reconferidos; resumo e seção 2.1 da consulta histórica | PP-OCRv5 como componente de reconhecimento multilíngue |
| Kiessling (2026a) | PDF v1 completo preservado, 14 páginas; p. 3–6 e 8–9 | Arquitetura, adaptação, normalização e limites experimentais |
| Kiessling (2026b) | Descrição da ficha Zenodo v1, reconferida nesta etapa | Identidade do peso, altura de 128 px, 44 línguas e mistura de convenções |
| RapidAI (s.d.) | Página oficial de modelos reconferida | Disponibilidade de conversões e rotas ONNX, sem atribuir desempenho local à documentação |
| Jundiaí (s.d.) | Ficha institucional reconferida | Código do documento e distinção 1767/1656 |
| Miranda (s.d.) | Ficha institucional reconferida; créditos do PDF editorial preservado | Origem da edição e revisão de Thiago Paschoal |

Os [fichamentos de T1/T4](../../bibliografia/leitura_t1_t4_20261023/README.md)
mantêm extração detalhada e avaliação de qualidade. Conferir uma citação não
significa concluir a revisão sistemática ou ler integralmente as outras fontes.

## Requisitos e limites da entrega

Os slides de PI IV foram efetivamente consultados nesta etapa. A versão cujo
nome contém `(1)` identifica o calendário como proposta e admite alterações;
a outra cópia tem calendário sem essa ressalva. Nenhuma das duas substitui
orientações posteriores do Classroom. Não foi inferido um prazo final.

| Requisito ou orientação | Origem | Situação verificável |
| --- | --- | --- |
| Artigo com problema, método, resultados, discussão e conclusões | Modelos PLN2026/PLN2025 | Presente; três páginas com referências e resumos |
| Nome das ferramentas de IA e função | DOCX PLN2025, seção Uso de IA; slides PI IV, p. 10 | Presente no próprio artigo, em Comentários |
| Comparar dois reconhecedores | Esclarecimento do usuário registrado em 20/10 | PP-OCRv5 e PP-OCRv6 avaliados nos mesmos 24 recortes |
| Artigo e notebook | Slides PI IV, p. 9, 12–13 | Artigo preparado; notebook executado e auditado disponível no pacote de 22/10. Execução/publicação em Colab nesta etapa: não realizada |
| Dataset público | Slides PI IV, p. 16–17 | Fontes e evidências com links públicos; condições das imagens/edição são próprias, sem atribuir MIT aos dados |
| Modelo de classificação e deep learning com comparação | Slides PI IV, p. 12–13 | Há comparação de reconhecimento, não novo classificador supervisionado. Enquadramento docente permanece pendente; ensaio de ajuste fino não é avaliação científica de ganho |
| Revisão sistemática | Requisito relatado nos registros anteriores do projeto; não detalhado nesses 19 slides | Protocolo e leituras parciais disponíveis; não concluída nem simulada por esta revisão do artigo |
| Até cinco páginas | Restrição relatada no histórico, sem regra explícita localizada nos arquivos examinados | Três páginas, incluindo referências; não implica validação de rubrica |
| Coautoria/orientação do professor | Histórico informa nome e contato; função formal não confirmada | Quatro autores preservados; professor não acrescentado como coautor |
| Entrega no Classroom e aprovação final | Responsabilidade acadêmica do grupo | Não executadas; arquivos preparados para revisão e submissão pelos autores |

## Arquivos externos examinados

- `D:/Downloads/Modelo_Artigo_PLN2026.zip`: `main.tex` e `sample.bib` lidos;
  as referências fictícias e a imagem demonstrativa não foram aproveitadas.
- `D:/Downloads/PLN2025_Mod_Artigo_.docx`: texto, estrutura de seções, estilos,
  tabelas e partes do pacote examinados; usado para cotejar instruções, não
  como documento a sobrescrever ou origem da identidade visual de terceiros.
- As duas cópias de `01_Apresentação_Projeto Integrador PI IV 2026 _ 2.pdf`:
  19 páginas cada, extração integral; passagens de requisitos identificadas
  acima. A regra de Comentários está em ambas, p. 10.
- O planejamento inicial em DOCX foi consultado como histórico. Suas propostas
  de segmentação e de ferramentas não foram tratadas como experimentos ou usos
  executados neste diagnóstico posterior de reconhecimento.

Os hashes dos externos estão no manifesto. Não houve alteração dos arquivos
de Downloads. Os requisitos dos documentos foram usados como evidência para
esta preparação autorizada; não como autorização para outras ações.
