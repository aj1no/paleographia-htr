# Diagnóstico integral do 269 verso — 22/10/2026

O mesmo fluxo do reto integral recebeu a imagem inteira do verso: OpenCV por
projeção e PP-OCRv6 medium/Kraken. Pesos, configuração, imagem Docker e parâmetros
foram mantidos. O resultado é **diagnóstico de desenvolvimento contra a edição
publicada**, sem treinamento ou nova validação humana.

- [Relatório](relatorio.md) e [comparação visual completa](relatorio.html).
- [Saída bruta](transcricao_bruta.txt), [texto oficial](texto_oficial.txt) e
  [imagem com os recortes](segmentacao/p_traslado_269v_overlay.png).
- [Métricas](comparacao.json), [protocolo](protocolo.json),
  [auditoria](validacao.json) e [inventário SHA-256](inventario.json).

A referência tem 34 linhas: dez na página PDF 2 e 24 na página PDF 3 da edição,
após `269/Verso.` e antes de `270`. Foram mantidos os 36 recortes automáticos,
incluindo as duas bordas vazias. O cálculo usa uma única sequência da página,
com NFC e colapso de espaços, preservando grafia, caixa, acentos e pontuação.

O verso pertence ao mesmo documento usado no desenvolvimento. O resultado não
demonstra generalização para documentos reservados e não substitui a comparação
PP-OCRv5 × PP-OCRv6 nas 24 linhas do reto. Os pacotes acadêmicos de 20/10 e 22/10,
as revisões humanas e suas oito ressalvas permanecem preservados. Não houve nova
função no sistema, alteração no editor ou promoção de estados humanos.

## Conferência offline, sem nova inferência

Na raiz do repositório, com o ambiente do projeto e `pypdf==6.1.1`:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/verificar.py
```

Confere inventário, fontes, alvos editoriais, imagem embutida, configuração idêntica
ao reto, geometria e pixels dos recortes, identidade registrada do modelo, bruto,
alinhamentos e CER/WER com uma segunda implementação da distância de edição.
Não carrega pesos, não usa Docker e não acessa rede. O recibo de preservação é
histórico; não impede que as revisões vivas evoluam depois da rodada.

## Repetição com nova inferência, em outra pasta

Requer os pesos e a imagem Docker já documentados, além das dependências acima.
Não baixa pesos ou imagens. Não execute estes comandos para apenas conferir
os resultados arquivados:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/reproduzir.py preparar --output-root output/269v_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/reproduzir.py segmentar --output-root output/269v_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/reproduzir.py reconhecer --output-root output/269v_integral_repeticao_NOVA
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/reproduzir.py avaliar --output-root output/269v_integral_repeticao_NOVA
```

Use sempre uma pasta nova. A preparação recusa pasta existente; reconhecimento e
avaliação recusam resultados existentes. Os alvos são congelados antes da inferência,
e o modelo recebe apenas imagens. Os pesos são montados somente para leitura,
com rede desativada, CPU/float32 e identidades fixadas por hash. O TOML conserva
seus caminhos históricos para manter identidade byte a byte; os comandos acima
usam explicitamente os manifestos e as saídas da pasta escolhida, sem invocar o editor.

O gerador de relatórios apenas lê os artefatos existentes, sem reconhecimento:

```powershell
.venv/Scripts/python.exe docs/experimentos/traslado_269v_integral_edicao_20261022/gerar_relatorio.py
```

Ele recusa sobrescrever os relatórios. Esta pasta não foi adicionada à matriz
automática da CI acadêmica; o recibo registra as verificações locais realizadas.
