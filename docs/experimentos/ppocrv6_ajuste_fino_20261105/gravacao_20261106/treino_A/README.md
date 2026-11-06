# Treino A gravado em 06/11/2026: PP-OCRv6 medium ajustado no Traslado

Registro do ajuste fino feito ao vivo com `gravar_treino.bat` (opção A), que chama
`scripts/treinar_ao_vivo.py A`. A tela foi gravada em vídeo pela equipe. Esta pasta
guarda as provas que acompanham o vídeo: prints, log completo e o resultado do worker.

## Execução

| Item | Valor |
|---|---|
| Início / fim | 06/11/2026 12h57 → 15h19 (141,7 min) |
| Commit do código | `c35baeb73fbe519ad0065b262146901286a9efec` |
| Imagem Docker | `sha256:b5e275eb694b25aeac0b159181953b8c3824e777ed9c8d49996db5347b6a0c1a` (Kraken 7.1, torch 2.9.1+cu126) |
| Dispositivo | NVIDIA GeForce GTX 1650 (4 GB), CUDA 12.6, FP32 |
| Dados | 191 linhas do Traslado com rótulo da edição (382 imagens de treino com 1 variante cada), 7 linhas de validação |
| Teste reservado | não usado (`test_used: false`); o pagamento a Thomas Pardo é recusado pelo código |
| Hiperparâmetros | lote 2, acumula 4, taxa 2e-5 (cosseno, warmup 40), BatchNorm congelada, rótulos NFD, parada após 8 validações sem melhora |
| Passos do otimizador | 191, em 4 épocas completas (o resumo imprime "épocas 5" porque o contador do Lightning avança ao fim) |
| Melhor checkpoint | `checkpoint_01-0.9080.ckpt` (passo 95), exportado como `best_0.9080.safetensors` |
| SHA-256 do peso exportado | `04194328e5d12b4f7a72bb2764a0c4c76f5030e9856e5c41ce96d04ab8b7c148` |

O peso exportado não está no Git (tamanho). Fica em
`output/treino_ao_vivo_A_20261106T125719/checkpoints/` na máquina que treinou. O SHA
acima permite conferir qualquer cópia.

## Validações (acerto do `ketos`, validação de 7 linhas)

| Época | Passo | Minutos | Caracteres | Palavras |
|---|---|---|---|---|
| 1 | 11 | 9,4 | 90,23% | 61,19% |
| 1 | 23 | 18,2 | 90,23% | 62,69% |
| 1 | 35 | 26,8 | 89,08% | 58,21% |
| 1 | 47 | 35,2 | 89,66% | 61,19% |
| 2 | 59 | 44,2 | 89,37% | 59,70% |
| 2 | 71 | 52,9 | 89,66% | 59,70% |
| 2 | 83 | 61,4 | 90,23% | 61,19% |
| **2** | **95** | **69,9** | **90,80%** | **64,18%** |
| 3 | 107 | 79,4 | 90,23% | 64,18% |
| 3 | 119 | 88,4 | 90,23% | 64,18% |
| 3 | 131 | 96,9 | 90,23% | 64,18% |
| 3 | 143 | 105,3 | 89,94% | 62,69% |
| 4 | 155 | 114,3 | 89,94% | 62,69% |
| 4 | 167 | 122,6 | 90,23% | 64,18% |
| 4 | 179 | 132,4 | 90,80% | 62,69% |
| 4 | 191 | 141,1 | 90,23% | 61,19% |

Referência: o modelo base sem ajuste fica em 86,8% / 46,3% nessa mesma validação, e o
treino A de 05/11 parou em 90,2% / 61,2%. Com só 7 linhas de validação, uma linha a
mais ou a menos certa move bastante o número. As oscilações acima são desse tamanho.
A comparação definitiva fica para o teste reservado, rodado uma única vez no fim.

## CER e WER em NFC (métrica do projeto)

Mesmas 7 linhas, pelo worker de inferência do editor (imagem de CPU avaliada), com
`scripts/avaliar_validacao.py` ([linhas](../../dados/avaliacao_validacao_base_A_A2_nfc.json)):

| Modelo | CER | WER |
|---|---|---|
| PP-OCRv6 base | 14,20% | 56,72% |
| Ajustado A de 05/11 | 12,17% | 50,75% |
| **Ajustado A gravado (este treino)** | **10,72%** | **41,79%** |

Exemplo, linha 7: referência "ando sobre o bem commum do povo, na mesma se"; base "lando sobre
obem commûm dopovo, namyma se"; este modelo "lando sobre o bem commum dopovo, namesma se".

## Arquivos

- `prints/treino_A_*.png`: a janela do terminal a cada 10 min e o resumo final (`*_final.png`).
- `prints/treino_A_validacao_passoNNN.png`: a janela logo depois de cada validação.
- `prints/docker_*.png`: o Docker Desktop com o contêiner `paleographia-finetune` rodando na imagem `b5e275eb6…`.
- `console.log`: saída completa do contêiner, linha a linha.
- `validation_history.json`, `losses.jsonl`: métricas gravadas pelo worker.
- `worker_result.json`, `training.json`: resultado, dispositivo, checkpoint escolhido e SHA do peso.
- `ketos_arguments.json`, `command.json`: os argumentos exatos do `ketos` e do `docker run`
  (em `command.json` a pasta do projeto aparece como `<raiz do projeto>`).

Para refazer: `gravar_treino.bat` → A, ou `python scripts/treinar_ao_vivo.py A` na raiz,
com Docker aberto. Sem GPU NVIDIA o script cai para a CPU, bem mais lenta.
