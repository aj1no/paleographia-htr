# Adequação do rascunho às disciplinas

O núcleo empírico é comum: dois reconhecedores já existentes, os mesmos 24
recortes e um protocolo assistido explícito. O texto é um primeiro rascunho;
a execução do notebook não significa aprovação da rubrica pelos professores.

| Item | Evidência disponível | Pendência |
| --- | --- | --- |
| Comparação entre dois reconhecedores, informada como requisito de PLN | PP-OCRv5 × PP-OCRv6, métricas e bruto auditáveis | Confirmar se o desenho específico e o tamanho do estudo atendem à rubrica |
| Notebook | Dez células de código, incluindo a reconferência posterior, tabelas e figuras | Ajustar apresentação ao ambiente da disciplina, se necessário |
| Artigo | Primeiro rascunho em português, fontes e limitações explícitas | Confirmar modelo e limite de páginas; revisar texto e referências com os autores |
| PI IV e a expressão “classificação”, relatada na especificação | Estudo de reconhecimento de sequência e comparação de configurações | Confirmar enquadramento; não declarar um classificador novo que não foi treinado |
| Revisão sistemática de PI IV | Protocolo atualizado em 21/10; B01/B02 executadas no arXiv, cinco IDs distintos registrados | Fazer triagem e leitura com registro; executar demais buscas; não presumir inclusão ou leitura completa |
| Dados e condições de uso | Pacotes publicados, hashes e créditos | Adequar a disponibilização à orientação e às condições das fontes; MIT refere-se ao código |
| Avaliação reservada | Nenhuma; o 269r é desenvolvimento | Reservar outros documentos antes de qualquer escolha de configuração com eles |
| Apresentação | Resultados e duas figuras reutilizáveis | Preparar após revisão do texto e confirmação das rubricas |

## Autoria e identificação

Foram informados quatro autores e o professor Leonardo de Lellis Rossi.
O usuário informou a afiliação: Faculdade de Tecnologia de Jundiaí (FATEC Jundiaí),
Ciência de Dados, 5º semestre, Jundiaí – SP. Os modelos de artigo continuam
pendentes. A função formal
de orientação e eventual coautoria do professor precisam ser definidas pelo grupo.

## Fontes iniciais consultadas

As fontes estão em `fontes_consultadas.json`, com URL, data e escopo real de
consulta. As fichas do acervo fundamentam a identificação do documento e da
edição. Sousa e Trippel (2006) foram consultados por metadados e resumo para
contextualizar representação de corpus; não foram declarados integralmente lidos.
No relatório PaddleOCR foram consultados resumo e seção 2.1. A documentação
RapidOCR e a ficha do checkpoint Zenodo descrevem os componentes.

Não se trata de revisão sistemática concluída. Nenhuma nova arquitetura,
pós-correção, importador lexical ou treinamento faz parte desta entrega.

## Uso de IA a revisar pelos autores

Codex auxiliou a estruturação do notebook, a redação do rascunho, as figuras e
as verificações de reprodução. A leitura humana registrada permanece atribuída
ao revisor identificado. A seleção final de fontes, a conformidade com as
rubricas e a responsabilidade pelo texto cabem aos autores. A descrição antiga
de uso de IA do projeto é histórica; para este estudo os reconhecedores são
PP-OCRv5 e PP-OCRv6, com TrOCR desativado.

## Atualização de 22/10

Esta versão incorpora a reconferência de 21/10 sem alterar alvos ou métricas.
O pacote de 20/10 e as oito ressalvas históricas foram preservados. As dúvidas
atuais e as escolhas editoriais estão na seção 3.1 do artigo e do notebook.
