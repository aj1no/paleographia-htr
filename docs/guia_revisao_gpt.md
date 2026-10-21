# Estado do projeto para revisão — 21/10/2026

Revisar a `main`, branch principal e padrão. Base publicada anterior a esta
atualização documental: `5879f8538146d36e78a996ac1f604deaec36ab83`.
A etapa de refatoração foi incorporada à `main` pelo responsável; a antiga
`codex/refatoracao-piloto` continua preservada. O [índice](README.md) separa
guias atuais e registros históricos. A [nota da adoção da main](manutencao/main_20261020/README.md)
explica por que os pacotes anteriores mantêm suas branches e hashes originais.

## Evidência atual

1. [Referência assistida](revisao_humana/traslado_269r/referencia_assistida_20261020/README.md):
   24 linhas do corpo do 269r, geometria e cinco coberturas completas confirmadas.
   Há 16 linhas validadas e oito pendentes de certeza visual, com autoria,
   apoio editorial e dúvidas registrados.
2. [Diagnóstico de dois reconhecedores](experimentos/traslado_269r_reconhecedores_24_20261020/README.md):
   PP-OCRv5 latino/ONNX, CER/WER 58,45%/94,58%; PP-OCRv6 medium/Kraken,
   15,11%/60,10%. Mesmos 24 recortes, cinco blocos, 1.112 caracteres e 203 palavras.
   Desenvolvimento de um documento, sem treino ou avaliação reservada.
3. [Entrega acadêmica](entregas/pi_iv_pln_20261020/README.md): nove células de
   código executadas, duas figuras, cinco tabelas; reprodução documentada em
   checkout separado. Artigo em primeiro rascunho, autoria/afiliação informadas;
   revisão bibliográfica e adequação final pendentes.
4. Catálogo de 1831 separado: três candidatos, 94 linhas pendentes, 13 exemplos
   de repertório e seis confirmações parciais. Não herda a validação do 269r.

## Código em uso e revisão

CLI/API compartilham `src/paleographia/services.py`; as telas servidas estão em
`src/paleographia/web/`. O Traslado usa `configs/traslado_269r.toml`, workspace
próprio e PP-OCRv6 em Linux separado. No piloto de 1831, a apresentação de
sugestões está desativada. PP-OCRv5 é experimental, TrOCR está bloqueado e
treino Kraken não está implementado. Segmentadores não foram comparados aqui.

Conferir separação entre bruto, edição e decisão humana; autoria e escopo;
pixels, ordem e cobertura; inclusão das linhas difíceis; CER/WER por região;
diferenças de variantes e pré-processamento. Não atribuir a diferença somente
à versão nem presumir generalização, aprovação acadêmica ou economia de trabalho.

## Preservação e reprodução

Use o [guia de execução](runbook.md). A [tarefa acadêmica da CI](manutencao/ci_academica_20261021/README.md)
audita a entrega e reexecuta o notebook em Ubuntu/Python 3.12, sem nova inferência.
Compara as métricas e cinco tabelas, preserva as oito ressalvas e publica somente
os derivados da execução. O notebook e os pacotes históricos permanecem intactos.
Dados, revisões, experimentos e implementações arquivadas fazem parte da
evidência, inclusive resultados ruins. O [inventário desta revisão](revisao_repositorio_20261020.md)
identifica componentes legados e dependências de auditoria.

Ambientes, pesos, saídas locais e workspaces mutáveis são ignorados pelo Git.
Um checkout não contém automaticamente o workspace local. O gitlink `client`
é histórico e não é necessário para abrir a interface integrada ao pacote.
