# Apresentação das saídas em português

A revisão apresenta mensagens em português. Os resultados brutos do modelo são
preservados sem alterações nos arquivos técnicos e na exportação; não são
traduzidos, pois traduzir um reconhecimento errado criaria uma falsa transcrição.
Os identificadores dos campos técnicos continuam estáveis para compatibilidade.

O teste qualitativo com as linhas editoriais 17–19 do 100r, registrado em
`experiments/reference_spotcheck_100r/comparison.json`, encontrou resultados
incompatíveis com a edição conhecida. Por isso, a configuração de apresentação
mantém `automatic_transcription_enabled = false`. A tela mostra a indisponibilidade
da leitura automática em português, inclusive para as predições antigas, e mantém
o recorte, a correção humana e a edição modernizada disponíveis.

Essa configuração não detecta idioma nem modifica o modelo. Sua liberação futura
exige uma decisão explícita após avaliar um reconhecedor adequado. Esconder a
saída inadequada não significa que a capacidade de reconhecimento melhorou.

## Próximos passos sugeridos

1. Conferir os limites de cada linha e a correspondência com a edição disponível.
2. Produzir referências paleográficas com revisão humana. Preservar grafia,
   abreviaturas e quebras físicas; guardar a edição modernizada separadamente.
3. Montar exemplos confirmados de letras e palavras do fólio para auxiliar a
   leitura das partes sem edição, sem completar automaticamente as lacunas.
4. Avaliar um modelo adequado ao português histórico ou adaptar o reconhecedor
   usando material revisado. Reservar documentos distintos para avaliação;
   os três fólios da mesma sessão não constituem uma avaliação independente.
5. Mostrar cada sugestão ao lado do recorte e registrar dúvidas e correções.
   Calcular erros de caracteres e palavras somente com referências compatíveis.

O checkpoint atual é o `microsoft/trocr-small-handwritten`, ajustado ao conjunto
IAM, conforme a [ficha oficial](https://huggingface.co/microsoft/trocr-small-handwritten).
O fluxo de adaptação é descrito na
[documentação do TrOCR](https://huggingface.co/docs/transformers/model_doc/trocr).
