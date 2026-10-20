# Scripts numerados — compatibilidade em 20/10/2026

Os dez caminhos antigos continuam na raiz. São avisos independentes do pacote:
executá-los termina com **código 1**, como antes, sem rodar a CLI, criar saídas,
baixar pesos ou alterar dados. Importá-los não executa operações nem imprime
mensagens. Argumentos como `--execute` não são encaminhados a outro programa.

## Orientações atuais

| Caminho preservado | Orientação e limite |
| --- | --- |
| `1_organizar_arquivos.py` | Extração explícita de compactados para pasta nova; não reorganiza ou move originais |
| `1_testar_recorte_linhas.py` | Detecção de candidatos com `segment`; sem validação humana automática |
| `2_mapear_e_organizar.py` | `associate` exige mapeamento explícito; ordem dos arquivos não prova correspondência |
| `3_limpar_e_extrair_fiel.py` | `extract-reference` extrai edição como apoio pendente, não referência humana validada |
| `4_gerar_dataset_trocr.py` | Geração automática de dataset TrOCR desativada; recortes detectados exigem conferência |
| `5_limpar_nomes_arquivos.py` | `inventory` preserva os nomes; não substitui uma rotina de renomeação |
| `7_segmentador_avancado.py` | Detecção explícita de candidatos, sem pareamento automático com a edição |
| `8_treinar_modelo.py` | Treinamento indisponível para os backends atuais; ajuda da CLI descreve a entrada mantida para diagnóstico |
| `9_transcrever_imagem.py` | Reconhecimento de recortes de linha com configuração explícita; PP-OCRv6 exige runtime/pesos separados; TrOCR bloqueado |
| `9_treino_relampago.py` | Nenhum treino relâmpago habilitado ou duração garantida |

As linhas de comando exatas constam no [inventário](inventario.json) e nos
avisos. `PAGINAS.jsonl`, `MAPEAMENTO.jsonl` e `EDICAO.pdf` são exemplos a
substituir por entradas reais; saídas marcadas como novas não devem existir.
Os avisos não constituem uma migração automática dos algoritmos anteriores.

Para a operação atual, use o [guia de execução](../../runbook.md). A comparação
acadêmica está na [entrega de PI IV e PLN](../../entregas/pi_iv_pln_20261020/README.md).
Esta manutenção não altera reconhecedores, treino, segmentação ou seus contratos.

## Histórico e integridade

O inventário registra, para cada caminho, SHA-256 do aviso no commit anterior
`951363bdb588268dd973de6ead96d7d36c538df6`, SHA-256 do aviso atualizado e
caminho/hash do código original em `legacy/*.py.txt`. Os avisos anteriores
continuam recuperáveis nesse commit; os originais arquivados não foram alterados.

Os avisos são gravados em UTF-8/LF, com regra explícita em `.gitattributes` para
conservar hashes em Windows/Linux. Não foram movidos scripts, renumerados
caminhos, habilitado treino ou modificados inventários dos experimentos.
`training.py`, `recognition.py`, o worker neural e as implementações congeladas
permanecem intactos.

## Verificações

`tests/test_legacy_entrypoints.py` executa os dez avisos em diretório isolado,
sem acesso aos pacotes instalados, com e sem argumentos de execução; confere
código de saída e preservação de arquivos. Também testa importação sem efeitos,
integridade dos avisos e preservação dos originais e avisos anteriores.
Os comandos indicados são conferidos pelo analisador de argumentos existente,
sem executá-los. Esses testes integram a suíte e a CI existentes.

O [recibo de validação](validacao.json) registra testes, auditorias e escopo da
preservação. Não houve nova inferência nem reexecução do notebook.
