# Imagem SÓ PARA TREINO em GPU NVIDIA (CUDA 12.6). A inferência do editor continua
# na imagem de CPU avaliada (runtime/kraken_ppocrv6). Mesma base Python, mesmo
# Kraken 7.1 e demais dependências fixadas pelo requirements.lock da imagem de CPU;
# só torch/torchvision mudam para as builds CUDA das mesmas versões.
FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir torch==2.9.1 torchvision==0.24.1 --index-url https://download.pytorch.org/whl/cu126
COPY constraints.txt /tmp/constraints.txt
RUN python -m pip install --no-cache-dir kraken==7.1.0 -c /tmp/constraints.txt && python -c "import torch, kraken; print(torch.__version__, torch.version.cuda)"
WORKDIR /work
