# Piloto de pré-treinamento VGSL no Kraken 7.1

O ensaio técnico executou duas épocas na CPU com **67 imagens de linhas** da segmentação integral do traslado de 1767. As quatro faixas tratadas da página 5 do contrato do livro 13 de 1763 foram usadas para a validação da tarefa de pré-treinamento. Todos os campos de texto estavam vazios nos arquivos Arrow. O contrato foi usado aqui como desenvolvimento exploratório. As partições científicas ficam registradas separadamente.

O pré-treinamento executou **68 passos de otimização** e exportou pesos VGSL em Safetensors. A perda contrastiva média registrada nas quatro imagens de validação foi 2,785 na primeira época e 2,878 na segunda. Essa perda avalia a tarefa visual do pré-treinamento.

O Kraken carregou os pesos exportados e concluiu uma época supervisionada, com seis linhas diplomáticas do traslado para treino e duas do mesmo documento para validação técnica. O modelo dessa etapa errou 89 dos 91 caracteres na validação. Havia também dois caracteres presentes só na validação. O resultado verifica a transferência de pesos e a execução do treino. Uma avaliação de reconhecimento requer um grupo independente e um controle VGSL com a mesma configuração, iniciado do zero.

## Dados e execução

- [Preparar as imagens sem texto](kraken_vgsl_prepare.py) e [preparar as linhas diplomáticas para verificar a transferência](kraken_vgsl_handoff.py). Execute os dois scripts da raiz do projeto no ambiente Python local. O primeiro recebe o diretório de entrada a criar, e o segundo recebe o diretório 'handoff_data' dentro do diretório de execução.
- Em Docker, monte a entrada sem texto em '/input' e o diretório de execução em '/work'. Para cada conjunto, compile o Arrow com 'ketos --threads 2 compile -f path --keep-empty-lines --force-type baseline -F /input/<conjunto>.lst -o /work/<conjunto>.arrow'. A opção de tipo conserva o tratamento de faixas de linha sem normalização de linha central. Os arquivos '.gt.txt' usados pelo compilador têm tamanho zero. Em '/work', crie 'train.lst' e 'validation.lst' com o caminho do Arrow correspondente em cada um.
- A primeira tentativa direta com 'ketos pretrain' recusou texto vazio dentro do leitor Arrow. O [executor do piloto](kraken_vgsl_pretrain.py) verifica que o texto nos dois arquivos continua vazio e permite esse caso apenas no processo de pré-treinamento do Kraken 7.1. O runtime do projeto segue com a imagem Docker fixada.
- [Resultados, comandos, hashes e caminhos locais](resultado.json). [Inventários do pré-treino e da transferência](evidencias/). Os pesos e logs ficam em 'output/kraken_vgsl_pretrain_smoke_01/'.

O próximo ensaio de reconhecimento pode comparar dois VGSL idênticos, com e sem esse pré-treinamento, ajustados nas mesmas linhas diplomáticas. As previsões e o CER/WER devem ser medidos no mesmo grupo de teste independente. [Documentação do Kraken sobre pré-treinamento](https://kraken.re/main/user_guide/training_recognition.html#pretraining)
