# Artigo preparado para PI IV e PLN — 23/10/2026

Texto integral revisto quanto à estrutura, fundamentação, citações, método,
resultados e conclusão. O artigo tem **três páginas**, incluindo referências,
abstract e declaração de IA, no layout de duas colunas do modelo PLN2026
encontrado em Downloads. É uma versão preparada para entrega aos autores;
não registra aprovação docente ou revisão humana que não ocorreram.

- [Artigo em PDF](artigo.pdf): versão de leitura e impressão, exportada do Word.
- [Artigo editável](artigo.docx): mesmo conteúdo, tabela editável e links ativos.
- [Fonte textual em Markdown](artigo.md).
- [Relatório da revisão e adequação às disciplinas](revisao_e_adequacao.md).
- [Proveniência, verificações e hashes](manifesto.json).
- [Fontes e conferência das citações](citacoes.json).
- [Gerador do DOCX](gerar_artigo.py) e [exportação do PDF pelo Word](exportar_pdf.ps1).

O conteúdo deriva do [rascunho com fundamentação ampliada](../pi_iv_pln_20261023_fundamentacao/README.md).
As versões anteriores e seus manifestos permanecem preservados. Não foram
alterados alvos, saídas, dados, modelos ou estados de validação humana.

## Uso para as disciplinas

O artigo comum apresenta dois reconhecedores, política de referência assistida,
análise de erros e limitações. Em PI IV, inclui a declaração de ferramenta e
utilização dentro da seção **Comentários**, conforme os slides consultados.
O modelo de PLN também solicita identificar ferramentas e suas funções.

O [notebook executado de 22/10](../pi_iv_pln_20261022/comparacao_reproduzivel.ipynb),
sua [leitura em HTML](../pi_iv_pln_20261022/comparacao_reproduzivel.html) e os
auditores continuam sendo o complemento numérico. Eles não foram renomeados
como experimento novo nem reempacotados sem suas dependências. Para executar,
usar o checkout completo e as instruções daquele pacote.

As exigências de classificação/deep learning de PI IV ainda precisam de
enquadramento docente. A revisão sistemática e o teste reservado não foram
concluídos por esta preparação editorial. A publicação final dos arquivos
não equivale à submissão no Classroom. O limite de cinco páginas é uma
restrição operacional conservada dos registros do projeto; não foi localizado
como regra explícita nos modelos examinados.

## Diagramação e reprodução

O modelo `Modelo_Artigo_PLN2026.zip` contém fonte LaTeX com A4, margens laterais
de 10 mm, superior/inferior de 13 mm, duas colunas com intervalo de 10 mm,
corpo aproximado de Times de 10 pt, títulos em Arial/Helvetica e resumos em
largura total. O DOCX foi construído com essas medidas, sem usar exemplos de
autoria, robótica ou referências fictícias do modelo. O professor não foi
inserido como coautor sem indicação de autoria no histórico do projeto.

O Word 16.0 exportou o PDF do DOCX aberto somente para leitura. O conversor
LibreOffice do helper de documentos estava ausente; a rasterização do helper
foi reutilizada sobre o PDF exportado pelo Word, com Poppler do runtime.
As três páginas finais foram inspecionadas visualmente a 150 dpi, além das
conferências de texto, tabela, links e caracteres. Imagens de QA ficam em `tmp/`
e não fazem parte da entrega. O PDF final é um artefato de entrega, não uma prévia.

Os modelos e slides externos não são redistribuídos neste pacote; suas origens,
hashes e passagens utilizadas estão no manifesto. O gerador recebe o Markdown
como fonte e usa `python-docx`; o exportador requer Microsoft Word no Windows.
Nova geração pode modificar metadados binários, sem alterar o conteúdo textual.
