# Comparação exploratória de dois VGSL no Kraken 7.1

| Papel no piloto | Documento | Linhas diplomáticas validadas |
| --- | --- | ---: |
| Ajuste supervisionado, igual para os dois modelos | Traslado da criação da vila, 1767, fólio 269r | 12 |
| Monitoramento interno, mesmo documento | Traslado da criação da vila, 1767, fólio 269r | 4 |
| Avaliação externa ao treino dos dois VGSL | Carta de José Gomes de Gouveia, 1767, fólio 4r | 3 |
| Avaliação externa ao treino dos dois VGSL | Sessão de 25/06/1795, fólio 91r | 7 |

O grupo de avaliação ficou fora dos dados do pré-treinamento, do ajuste e do monitoramento. Os contêineres de treino tiveram acesso às 16 linhas do traslado. Na inferência externa, o processo recebeu somente as dez imagens e os pesos finais. A carta e a sessão já haviam aparecido em outras atividades do projeto. Os papéis deste piloto não alteram as partições oficiais nem substituem a reserva de um teste científico independente.

Os dois modelos usaram a mesma arquitetura, alfabeto, semente 1831, lote 2, taxa 0,001 e recortes. O VGSL pré-treinado iniciou com os pesos do ensaio de 67 imagens sem texto. A cabeça de reconhecimento foi criada para o alfabeto das linhas de treino. Na primeira checagem, após 25 épocas, o modelo do zero retornou vazio nas quatro linhas internas e o pré-treinado retornou 'e e e' nas quatro. O treino dos dois foi estendido para 75 épocas antes de qualquer inferência externa. A comparação usa os dois checkpoints da época 75. Ambos registraram 451 passos de otimização, um a mais que a conta de uma execução contínua de 75 épocas.

A normalização das métricas é Unicode NFC e espaços normalizados, com maiúsculas, acentos e pontuação preservados. O CER e o WER agregados somam as edições por linha e dividem pelo total de caracteres ou palavras da referência. O piloto tem uma semente, um documento de treino e dez linhas avaliadas. A comparação mede reconhecimento em recortes de linhas já delimitadas.

## Resultados

| Documento | Linhas | CER do zero | CER com pré-treino | WER do zero | WER com pré-treino |
| --- | ---: | ---: | ---: | ---: | ---: |
| Carta de 1767 | 3 | 96,88% (124/128) | 95,31% (122/128) | 100,00% (26/26) | 96,15% (25/26) |
| Sessão de 1795 | 7 | 96,81% (334/345) | 93,33% (322/345) | 100,00% (67/67) | 97,01% (65/67) |
| Total | 10 | 96,83% (458/473) | 93,87% (444/473) | 100,00% (93/93) | 96,77% (90/93) |

As omissões dominaram os erros dos dois modelos. O VGSL do zero omitiu 453 caracteres, trocou cinco e produziu 'ta' em nove das dez linhas. O pré-treinado omitiu 443 caracteres, trocou um e acertou três palavras, todas 'e'. Para 'Aos vinte e cinco dias do mes de junho de mil sete', as saídas foram 'ta' e 'e ea', respectivamente. As duas saídas continuam muito distantes de uma transcrição utilizável.

O pré-treinamento reduziu 14 edições de caracteres e três edições de palavras nesse piloto. A amostra e a semente única limitam a comparação a estas execuções. [Métricas por linha, saídas e tipos de erro](resultados.json)

## Reprodução

1. Da raiz do projeto, execute [preparar.py](preparar.py) com o caminho de uma pasta de execução nova. O inventário verifica os manifestos de origem, as referências e os pixels dos recortes.
2. Execute os [comandos do Kraken e o inventário](evidencias/). Monte 'supervised' como '/data', a pasta de cada modelo como '/model' e 'weights_initial' como '/initial' só no primeiro treino do modelo pré-treinado. A imagem Docker fixada é 'sha256:511fb2e2b76db8de0d3eb87dcf04398f7a02fc06b5d91887629b2492f826af5b'. As execuções usaram CPU, dois threads e 'TORCHDYNAMO_DISABLE=1'.
3. Execute [inferir.py](inferir.py) no mesmo Docker, montando 'models' em '/models', 'evaluation_images' em '/images' e uma pasta vazia 'predictions' em '/predictions'. Os pesos e o alfabeto são verificados antes de gravar as saídas brutas.
4. Execute [avaliar.py](avaliar.py) no ambiente local, passando a pasta da execução e o caminho de saída do JSON.
