"""Peças compartilhadas: dados, aumento de dados, modelo CRNN-CTC, decodificação e métricas.

Tudo escrito do zero; nenhum peso pré-treinado é carregado.
"""
import json
import math
import random
import unicodedata
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageFilter
from torch import nn
from torch.utils.data import Dataset, Sampler

AQUI = Path(__file__).resolve().parent
ALTURA = 64
PASSO = 4  # colunas de pixel por passo de tempo na saída
USAR_FP16 = False  # GTX 16xx gera NaN em meia precisão (problema conhecido); fp32 em tudo


def carregar_manifesto():
    linhas = (AQUI / "dados/manifesto.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in linhas]


def carregar_alfabeto():
    return json.loads((AQUI / "dados/alfabeto.json").read_text(encoding="utf-8"))


class Codificador:
    def __init__(self, alfabeto):
        self.alfabeto = alfabeto
        self.indice = {c: i + 1 for i, c in enumerate(alfabeto)}  # 0 = branco do CTC

    def codificar(self, texto):
        return [self.indice[c] for c in texto if c in self.indice]

    def decodificar_guloso(self, logits):
        """logits: (T, C) de uma amostra."""
        melhor = logits.argmax(-1).tolist()
        saida, anterior = [], 0
        for k in melhor:
            if k != anterior and k != 0:
                saida.append(self.alfabeto[k - 1])
            anterior = k
        return "".join(saida)


# ---------------------------------------------------------------- aumento de dados
def aumentar(img, rng):
    """img: PIL L com altura 64. Distorções leves de escrita, papel e digitalização."""
    w, h = img.size
    fundo = int(np.median(np.asarray(img)))
    if rng.random() < 0.7:  # inclinação da escrita e pequena rotação
        cis = rng.uniform(-0.35, 0.35)
        ang = math.radians(rng.uniform(-0.6, 0.6))  # linha larga: 0,6° já desloca ~5 px nas pontas
        a, b = math.cos(ang), cis + math.sin(ang)
        d, e = -math.sin(ang), math.cos(ang)
        c = -b * h / 2
        f = math.sin(ang) * w / 2 + rng.uniform(-2, 2)
        img = img.transform((w, h), Image.Transform.AFFINE, (a, b, c, d, e, f),
                            resample=Image.Resampling.BILINEAR, fillcolor=fundo)
    if rng.random() < 0.5:  # largura da letra
        img = img.resize((max(16, int(w * rng.uniform(0.8, 1.2))), h), Image.Resampling.BILINEAR)
    if rng.random() < 0.3:  # traço mais fino ou mais grosso
        img = img.filter(ImageFilter.MinFilter(3) if rng.random() < 0.5 else ImageFilter.MaxFilter(3))
    if rng.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 1.2)))
    x = np.asarray(img, dtype=np.float32) / 255.0
    if rng.random() < 0.8:  # contraste e brilho do papel
        x = (x - x.mean()) * rng.uniform(0.6, 1.4) + x.mean() + rng.uniform(-0.15, 0.15)
    if rng.random() < 0.3:
        x = x + np.random.default_rng(rng.randrange(1 << 30)).normal(0, rng.uniform(0.01, 0.06), x.shape)
    return np.clip(x, 0, 1).astype(np.float32)


class Linhas(Dataset):
    def __init__(self, registros, codificador=None, aumentar_dados=False, semente=0):
        self.r = registros
        self.cod = codificador
        self.aumentar = aumentar_dados
        self.rng = random.Random(semente)

    def __len__(self):
        return len(self.r)

    def largura(self, i):
        return self.r[i]["largura"]

    def __getitem__(self, i):
        reg = self.r[i]
        img = Image.open(AQUI / reg["img"]).convert("L")
        if self.aumentar:
            x = aumentar(img, random.Random(self.rng.randrange(1 << 30) ^ i))
        else:
            x = np.asarray(img, dtype=np.float32) / 255.0
        alvo = self.cod.codificar(reg["texto"]) if self.cod else []
        return torch.from_numpy(x), torch.tensor(alvo, dtype=torch.long), i


def juntar(lote):
    larguras = [x.shape[1] for x, _, _ in lote]
    W = int(math.ceil(max(larguras) / 128) * 128)  # poucas larguras distintas: o cuDNN reaproveita os planos
    imgs = torch.zeros(len(lote), 1, ALTURA, W)
    for k, (x, _, _) in enumerate(lote):
        imgs[k, 0] = float(x.median())
        imgs[k, 0, :, : x.shape[1]] = x
    alvos = torch.cat([a for _, a, _ in lote])
    tam_alvo = torch.tensor([len(a) for _, a, _ in lote])
    tam_ent = torch.tensor([max(1, w // PASSO) for w in larguras])
    idx = [i for _, _, i in lote]
    return 1.0 - imgs, alvos, tam_ent, tam_alvo, idx  # tinta = valores altos


class LotesPorLargura(Sampler):
    """Embaralha, agrupa por largura parecida (menos preenchimento) e embaralha os lotes."""

    def __init__(self, dataset, tamanho, semente=0):
        self.ds, self.tam, self.rng = dataset, tamanho, random.Random(semente)

    def __iter__(self):
        idx = list(range(len(self.ds)))
        self.rng.shuffle(idx)
        lotes = []
        bloco = self.tam * 50
        for s in range(0, len(idx), bloco):
            parte = sorted(idx[s:s + bloco], key=self.ds.largura)
            lotes += [parte[k:k + self.tam] for k in range(0, len(parte), self.tam)]
        self.rng.shuffle(lotes)
        return iter(lotes)

    def __len__(self):
        return math.ceil(len(self.ds) / self.tam)


# ---------------------------------------------------------------- modelo
def bloco(c_in, c_out):
    return nn.Sequential(nn.Conv2d(c_in, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU(inplace=True))


class Codificador_Visual(nn.Module):
    """CNN + BiLSTM: imagem (B,1,64,W) -> traços por coluna (T=W/4, B, 512)."""

    def __init__(self, oculto=256, camadas=3):
        super().__init__()
        self.cnn = nn.Sequential(
            bloco(1, 32), nn.MaxPool2d(2, 2),                      # 32 x W/2
            bloco(32, 64), nn.MaxPool2d(2, 2),                     # 16 x W/4
            bloco(64, 128), bloco(128, 128), nn.MaxPool2d((2, 1)),  # 8
            bloco(128, 256), bloco(256, 256), nn.MaxPool2d((2, 1)),  # 4
            bloco(256, 256), nn.Dropout2d(0.1),
        )
        self.proj = nn.Linear(256 * 4, oculto)
        self.rnn = nn.LSTM(oculto, oculto, num_layers=camadas, bidirectional=True, dropout=0.25)
        self.saida_dim = 2 * oculto

    def forward(self, x):
        f = self.cnn(x)                        # B, 256, 4, T
        B, C, H, T = f.shape
        f = f.permute(3, 0, 1, 2).reshape(T, B, C * H)
        f = torch.relu(self.proj(f))
        f, _ = self.rnn(f)
        return f                               # T, B, 512


class CRNN(nn.Module):
    def __init__(self, n_classes):
        super().__init__()
        self.enc = Codificador_Visual()
        self.drop = nn.Dropout(0.25)
        self.cls = nn.Linear(self.enc.saida_dim, n_classes)

    def forward(self, x):
        return self.cls(self.drop(self.enc(x)))  # T, B, C


# ---------------------------------------------------------------- métricas
def distancia(a, b):
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + (ca != cb)))
        anterior = atual
    return anterior[-1]


def cer_wer(pares):
    """pares: [(referência, predição)] em NFC. CER e WER agregados (erros / tamanho da referência)."""
    ec = nc = ew = nw = 0
    for ref, hip in pares:
        ref, hip = unicodedata.normalize("NFC", ref), unicodedata.normalize("NFC", hip)
        ec += distancia(ref, hip)
        nc += len(ref)
        ew += distancia(ref.split(), hip.split())
        nw += len(ref.split())
    return ec / max(1, nc), ew / max(1, nw)


@torch.no_grad()
def transcrever(modelo, registros, cod, dispositivo, lote=32):
    modelo.eval()
    ds = Linhas(registros)
    ordem = sorted(range(len(ds)), key=ds.largura)
    saida = {}
    for s in range(0, len(ordem), lote):
        imgs, _, tam_ent, _, idx = juntar([ds[i] for i in ordem[s:s + lote]])
        with torch.autocast("cuda", dtype=torch.float16, enabled=USAR_FP16 and dispositivo.type == "cuda"):
            logits = modelo(imgs.to(dispositivo)).float()
        for k, i in enumerate(idx):
            saida[i] = cod.decodificar_guloso(logits[: tam_ent[k], k])
    return [saida[i] for i in range(len(ds))]
