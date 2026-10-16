# Reconhecedor Kraken 7.1 em Linux separado

A aplicação permanece no Python do Windows. O backend `kraken_ppocrv6` executa
um worker persistente em contêiner Linux, com CPU/float32. O ambiente principal
não recebe dependências do Kraken. O worker recebe somente PNGs dos recortes e
carrega o modelo uma vez; ele não monta o projeto, edição ou referência humana.

Nesta máquina o Docker Desktop já estava instalado, com WSL2. Foi iniciado e a
imagem construída. Houve perda transitória da conexão do Docker na primeira
exportação; a segunda construção recuperou os passos em cache e terminou.
`python -m pip check` no contêiner passou. A imagem Linux/amd64 tem cerca de
2,27 GB; os pesos têm 63.779.644 bytes. Após reconhecer, o worker residente
usava aproximadamente 534 MiB, observado em repouso, não uma medida de pico.
Há limites de 2 CPUs e 4 GiB para o contêiner. Não foi usada GPU.

## Preparação

Com Docker Linux em execução, na raiz do projeto:

```powershell
docker build --provenance=false -t paleographia-kraken:7.1.0-cpu runtime/kraken_ppocrv6
python -m paleographia prepare-weights --config configs/traslado_269r.toml --output-dir models/kraken_ppocrv6_medium
docker run --rm --network none paleographia-kraken:7.1.0-cpu python -m pip check
docker image inspect paleographia-kraken:7.1.0-cpu --format '{{.Id}}'
```

Pule a preparação de pesos se o diretório correto já existir. O comando exige
saída nova e confere tamanho, MD5 publicado e SHA-256 fixado antes de gravar.
O download é explícito; carregar/reconhecer não baixa imagens Docker ou pesos.
A API não inicia o Docker Desktop nem aceita termos de instalação.

O Dockerfile fixa a base por digest, Kraken 7.1.0 e PyTorch/torchvision de CPU.
[requirements.lock](requirements.lock) registra as 71 distribuições exatas do
ambiente executado. Para reconstruir também as dependências transitivas,
use `Dockerfile.locked`. Instalações e construções exigem rede; a inferência usa
`--network none`, pesos/worker montados como somente leitura e diretório temporário
isolado. Os caminhos são argumentos de subprocesso, sem shell. Os mounts Windows
usam caminhos absolutos e o Docker os apresenta como `/model.safetensors` e
`/worker.py`; as imagens de entrada seguem pelo stdin em JSON/base64. Caminhos
de mount contendo vírgula são recusados explicitamente.

## Identidade e reprodução

A execução publicada usou a imagem
`sha256:511fb2e2b76db8de0d3eb87dcf04398f7a02fc06b5d91887629b2492f826af5b`.
`recognition.docker_image_id` fixa essa identidade. Uma imagem reconstruída pode
ter outro ID, inclusive com versões iguais; nesse caso a configuração publicada
recusa sua carga. Crie uma **nova configuração candidata** com o ID retornado
por `docker image inspect`, mantenha `automatic_transcription_enabled=false` e
repita a avaliação controlada antes de aprovar sugestões nessa nova identidade.
A configuração e os artefatos congelados anteriores permanecem intactos.

Para transferir a imagem exata entre máquinas autorizadas, `docker save` e
`docker load` preservam sua identidade; o arquivo grande deve ficar fora do Git.
O modelo também permanece em `models/`, ignorado. Não há necessidade de publicar
o projeto ou manuscritos em um serviço externo para reconhecer.

## Contrato de inferência

O peso Zenodo v1 tem `height=96` em seus metadados, embora a ficha descreva 128.
Seguimos o checkpoint: RGB, altura 96, largura proporcional variável, padding
horizontal 16 e `ImageInputTransforms` nativo. Não executamos segmentação,
extração de polígonos ou normalização de baseline. A linha inteira já recortada
é entregue ao CTC nativo (`_rec_predict`), cuja API privada foi conferida e
fixada à versão 7.1. A divergência da ficha e a tentativa inicial, que parou
antes de produzir predições, estão registradas na entrega experimental.

O worker verifica os pixels recebidos, devolve texto bruto, tokens, tempos e
identidade. A aplicação serializa o acesso e reutiliza o processo no lote e nas
solicitações seguintes. Ao encerrar o servidor, fecha o worker. Falha de modelo,
Docker ou protocolo é explícita; não há fallback para TrOCR. Treinamento desse
backend não foi implementado nesta entrega.
