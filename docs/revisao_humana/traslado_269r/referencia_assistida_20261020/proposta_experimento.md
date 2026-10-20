# Proposta para alinhamento com PI IV e PLN

Estado: **minuta para alinhamento**, sem envio. Em 20/10/2026, o usuário
esclareceu: **“PLN exige comparar dois reconhecedores.”** A comparação de
segmentadores deixa de ser a proposta principal para PLN. O enquadramento
de PI IV e a adequação do desenho específico continuam sem confirmação.
Base: [enquadramento existente](../../../academic_alignment.md) e
[protocolo existente](../../../evaluation_protocol.md).

## Dados e política de referência

O corpo do 269r tem 24 linhas incorporadas, cobertura e geometrias conferidas.
O revisor adotou a edição publicada para dirimir escolhas textuais duvidosas,
com autoria e proveniência registradas. Oito linhas ainda têm ressalvas visuais.
Descrever esse conjunto como referência assistida por edição publicada.

O 269r foi consultado durante desenvolvimento, análise de erros, revisão e
curadoria lexical. Deve permanecer no desenvolvimento. Reservar **outros
documentos completos**, incluindo seus fólios e derivados, para avaliação,
antes de usá-los em demonstrações ou escolhas de configuração. A ampliação para
30–50 linhas é uma meta operacional; não garante representatividade estatística.

## Comparação de reconhecedores para PLN

Proposta: comparar **PP-OCRv6 medium/Kraken** e **latin PP-OCRv5 mobile/ONNX**,
ambos já existentes no projeto, sobre os **mesmos recortes humanos**, sem detector
automático ou pós-correção. Assim, a segmentação fica controlada. O desenho não
acrescenta reconhecedor, correção automática, dicionário ou treinamento.

O PP-OCRv5 foi carregado com sucesso em CPU pelo componente existente
`LatinONNXRecognizer`, com os pesos locais de SHA-256
`b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a`.
O hash dos pesos locais PP-OCRv6 confere com a configuração do editor:
`15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9`.
O recibo está em [disponibilidade_reconhecedores.json](disponibilidade_reconhecedores.json).
Isso é verificação de disponibilidade, **sem nova inferência nem métrica**.

Cada modelo mantém seu pré-processamento nativo documentado, embora receba
os mesmos pixels de origem. Ambos usam CPU/float32; implementações e tempos de
carregamento diferem e precisam ser reportados. O PP-OCRv5 já teve desempenho
insatisfatório nas cinco linhas iniciais: serve como comparador de diagnóstico,
sem promessa de melhora. TrOCR permanece desativado; o reconhecedor do editor
continua PP-OCRv6.

Já existe `scripts/recognize_latin.py --model ... --lines ... --output ...`
para inferência local do PP-OCRv5, sem download obrigatório. A execução deve
usar uma nova pasta e um manifesto congelado do conjunto aprovado para a
comparação. Os diagnósticos históricos de cinco linhas não substituem uma
avaliação reservada e não foram repetidos nesta sessão.

A comparação anterior OpenCV × segmentação Kraken fica documentada como
planejamento secundário. Não iniciar duas frentes experimentais neste escopo.

## Decisões que precisam dos professores

1. **PI IV:** o estudo de segmentação e reconhecimento de texto manuscrito atende
   ao enquadramento exigido, inclusive a expressão “classificação” registrada na
   especificação recebida?
2. **PLN:** o usuário informou a exigência de **dois reconhecedores**. Confirmar
   a adequação do desenho específico PP-OCRv5 × PP-OCRv6, do corpus e do tamanho
   de avaliação à rubrica. Essa informação não significa aprovação de todas
   as escolhas desta minuta.
3. **Referência:** aceitar a leitura assistida pela edição com ressalvas para
   diagnóstico de desenvolvimento, ou exigir uma revisão independente dessas
   linhas antes de medir CER/WER? Fixar o tratamento de abreviaturas e espaços.
4. **Entregas:** confirmar rubricas, limites e prazos de notebook, artigo,
   apresentação, revisão sistemática e registro de uso de IA. A documentação
   atual descreve requisitos relatados, não rubricas oficiais lidas diretamente.

## Protocolo a manter após o alinhamento

Usar o mesmo conjunto, cobertura, política textual e normalização nos métodos:
Unicode NFC e colapso de espaços, preservando caixa e diacríticos. Manter as
quebras físicas no catálogo. A abreviatura Magᵈᵉ não pode virar Magestade somente
em um dos alvos. A separação que mais deve ser igual em todas as condições.

Aplicar o avaliador existente à região completa em ordem, somando substituições,
deleções e inserções antes de dividir pelo total de caracteres/palavras de
referência. Omissões, linhas espúrias e falhas entram como previsto no protocolo.
Não selecionar apenas as linhas fáceis/validadas dentro de um bloco e apresentar
o resultado como se cobrisse o bloco inteiro.

Fixar os limiares geométricos já propostos: IoU 0,5; sobreposição 0,2. Registrar
tempos externos separadamente de inferência, falhas e exclusões. A análise de
erros deve distinguir segmentação, letras, acentos, espaços, abreviaturas e
divergências da própria referência. Não inferir economia de trabalho humano
sem sessões realmente cronometradas.

## Entregas após os pré-requisitos

- Notebook reproduzível: dados congelados, configurações, execuções, contagens
  CER/WER e exemplos de erro.
- Artigo: problema, corpus e fontes, política textual, método, resultados e
  limitações, adequados à rubrica confirmada.
- Apresentação: comparação controlada, exemplos visuais e limites da conclusão.

Ainda não há novo resultado comparativo nesta consolidação. A avaliação integral
das 24 linhas continua bloqueada pelo validador existente, e nenhum professor
foi contatado automaticamente.
