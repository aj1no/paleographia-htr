# Diagnóstico do 269 reto inteiro contra a edição — 22/10/2026

O programa recebeu a imagem integral e aplicou os componentes já existentes:
segmentação OpenCV por projeção e reconhecimento PP-OCRv6 medium/Kraken.
Foram mantidos todos os 35 recortes automáticos, incluindo bordas e saídas vazias.
A referência contém cabeçalho, foliação, título, resumo e corpo, extraídos da
edição publicada. Não houve nova conferência humana, treinamento ou uso de
documento reservado. **Diagnóstico de desenvolvimento**.

- [Relatório com CER/WER, erros e limitações](relatorio.md).
- [Comparação visual em HTML](relatorio.html).
- [Saída bruta](transcricao_bruta.txt), [texto oficial](texto_oficial.txt),
  [recortes automáticos sobre a imagem](segmentacao/p_traslado_269r_overlay.png).
- [Protocolo](protocolo.json), [entradas congeladas](entradas_congeladas.json),
  [recibo de auditoria](validacao.json), [inventário](inventario.json).

As 36 unidades editoriais são três elementos do cabeçalho/foliação, duas linhas
do título, sete do resumo e 24 do corpo; não são 36 linhas físicas do manuscrito.
A ordem do cabeçalho segue a imagem da esquerda para a direita, com seu conteúdo
literal; a disposição vertical do PDF difere e está documentada no protocolo.
As métricas preservam convenções da edição, incluindo `Magestade`. As revisões
humanas anteriores e sua forma abreviada `Magᵈᵉ` permanecem em seus próprios pacotes.

## Reprodução em nova pasta

Na raiz do repositório, com o ambiente do projeto, `pypdf==6.1.1`, os pesos e
a imagem Docker já documentados. O comando de preparação não baixa pesos ou imagens.

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269r_integral_edicao_20261022/reproduzir.py preparar --output-root output/269r_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269r_integral_edicao_20261022/reproduzir.py segmentar --output-root output/269r_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269r_integral_edicao_20261022/reproduzir.py reconhecer --output-root output/269r_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269r_integral_edicao_20261022/reproduzir.py avaliar --output-root output/269r_integral_repeticao_NOVA
```

Use outra pasta em cada repetição; cada etapa recusa sobrescrever seus resultados.
Não execute treinamento. O modelo é montado somente para leitura em Docker, com
rede desativada, CPU/float32 e a imagem fixada por hash. A referência é extraída
e congelada antes do reconhecimento; o reconhecedor recebe somente imagens.

Para conferir o pacote arquivado **sem nova inferência, pesos ou Docker**:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269r_integral_edicao_20261022/verificar.py
```

O auditor confere hashes, extração do PDF, todas as caixas e pixels, identidade
do modelo, preservação do bruto, contagens CER/WER, uma implementação independente
de distância de edição e os pacotes históricos. A revisão estrita do catálogo não
foi alterada nem apresentada como aprovada. O log de preservação das revisões é
um recibo da rodada; não exige que o workspace vivo pare de evoluir no futuro.

O corpus continua sendo desenvolvimento. A comparação anterior de 24 recortes,
as oito ressalvas históricas, os notebooks de 20/10 e 22/10 e a CI dessas versões
não foram modificados ou substituídos. Este protocolo mede também segmentação e
convenções editoriais; suas taxas não indicam mudança isolada no reconhecedor.
