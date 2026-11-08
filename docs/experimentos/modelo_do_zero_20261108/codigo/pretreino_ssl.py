"""Pré-treino NÃO supervisionado: o modelo nunca vê texto.

Tarefa (autoencoder mascarado sobre colunas): trechos da linha (8 a 32 px de largura, ~40% da
linha) são apagados; o codificador CNN + BiLSTM, o mesmo do reconhecedor, tem de reconstruir os
pixels apagados a partir do contexto. Para isso precisa aprender a forma das letras e como a
escrita continua. Depois o encoder é reaproveitado no treino com CTC (ajuste) ou congelado
(sonda linear), para medir quanto do reconhecimento ele aprendeu sem rótulos.

Imagens usadas: só as linhas de treino (sem os textos). Nenhuma imagem de validação ou do teste.
"""
import argparse
import json
import random
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from comum import AQUI, ALTURA, PASSO, USAR_FP16, Codificador_Visual, Linhas, LotesPorLargura, carregar_manifesto, juntar
from treinar import iniciar_trabalhador


def mascarar(imgs, tam_ent, proporcao, gerador):
    """Devolve imagens mascaradas e a máscara por passo de tempo (B, T). imgs já na GPU."""
    B, _, _, W = imgs.shape
    T = W // PASSO
    mascara = np.zeros((B, T), dtype=bool)
    for b in range(B):
        t_valido = int(tam_ent[b])
        n = max(1, int(proporcao * t_valido / 5))  # trechos de 2 a 8 passos, média 5
        comps = gerador.integers(2, 9, n)
        inis = gerador.integers(0, max(1, t_valido - 8), n)
        for i, c in zip(inis, comps):
            mascara[b, i:i + c] = True
    mascara = torch.from_numpy(mascara).to(imgs.device)
    pix = mascara.repeat_interleave(PASSO, dim=1)[:, None, None, :]
    return imgs.masked_fill(pix, 0.0), mascara  # 0 = papel limpo (imagem invertida: tinta = alto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", default="ssl")
    ap.add_argument("--passos", type=int, default=20000)
    ap.add_argument("--lote", type=int, default=24)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--proporcao", type=float, default=0.4)
    ap.add_argument("--semente", type=int, default=20261107)
    ap.add_argument("--trabalhadores", type=int, default=4)
    a = ap.parse_args()
    torch.manual_seed(a.semente)
    random.seed(a.semente)
    gerador = np.random.default_rng(a.semente)
    pasta = AQUI / "runs" / a.nome
    pasta.mkdir(parents=True, exist_ok=True)
    disp = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    imagens = [r for r in carregar_manifesto() if r["split"] == "treino"]
    ds = Linhas(imagens, codificador=None, aumentar_dados=True, semente=a.semente)  # sem texto
    carregador = DataLoader(ds, batch_sampler=LotesPorLargura(ds, a.lote, a.semente), collate_fn=juntar,
                            num_workers=a.trabalhadores, persistent_workers=a.trabalhadores > 0,
                            worker_init_fn=iniciar_trabalhador if a.trabalhadores else None, pin_memory=True)
    enc = Codificador_Visual().to(disp)
    cabeca = nn.Sequential(nn.Linear(enc.saida_dim, 512), nn.GELU(), nn.Linear(512, ALTURA * PASSO)).to(disp)
    params = list(enc.parameters()) + list(cabeca.parameters())
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.05)
    agenda = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=a.passos, pct_start=0.05)
    escala = torch.amp.GradScaler(enabled=USAR_FP16 and disp.type == "cuda")
    config = vars(a) | {"imagens": len(imagens), "textos_usados": 0}
    (pasta / "config.json").write_text(json.dumps(config, indent=1), encoding="utf-8")
    print(json.dumps(config), flush=True)

    log = (pasta / "log.jsonl").open("a", encoding="utf-8")
    passo, inicio, perdas = 0, time.time(), []
    while passo < a.passos:
        for imgs, _, tam_ent, _, _ in carregador:
            imgs = imgs.to(disp, non_blocking=True)
            entrada, mascara = mascarar(imgs, tam_ent, a.proporcao, gerador)
            B, _, H, W = imgs.shape
            T = W // PASSO
            # alvo: os pixels de cada coluna de 4 px, normalizados por trecho
            alvo = imgs[:, 0].reshape(B, H, T, PASSO).permute(2, 0, 1, 3).reshape(T, B, H * PASSO)
            alvo = (alvo - alvo.mean(-1, keepdim=True)) / (alvo.std(-1, keepdim=True) + 1e-3)
            m = mascara.t()
            with torch.autocast("cuda", dtype=torch.float16, enabled=USAR_FP16 and disp.type == "cuda"):
                pred = cabeca(enc(entrada))
            erro = ((pred.float() - alvo) ** 2).mean(-1)
            perda = (erro * m).sum() / m.sum().clamp(min=1)
            opt.zero_grad(set_to_none=True)
            escala.scale(perda).backward()
            escala.unscale_(opt)
            nn.utils.clip_grad_norm_(params, 5.0)
            escala.step(opt)
            escala.update()
            agenda.step()
            perdas.append(perda.item())
            passo += 1
            if passo % 100 == 0:
                print(f"passo {passo}/{a.passos} perda {np.mean(perdas[-100:]):.4f} {time.time() - inicio:.0f}s", flush=True)
            if passo % 1000 == 0 or passo == a.passos:
                log.write(json.dumps({"passo": passo, "perda": float(np.mean(perdas[-1000:])),
                                      "segundos": round(time.time() - inicio)}) + "\n")
                log.flush()
                torch.save(enc.state_dict(), pasta / "encoder.pt")
            if passo == a.passos or passo % 5000 == 0:
                exemplo = {"entrada": entrada[0, 0].cpu().numpy(), "original": imgs[0, 0].cpu().numpy(),
                           "reconstrucao_coluna_norm": pred[:, 0].float().detach().cpu().numpy()}
                np.savez_compressed(pasta / f"exemplo_{passo}.npz", **exemplo)
            if passo >= a.passos:
                break
    torch.save(enc.state_dict(), pasta / "encoder.pt")
    print("FIM", round((time.time() - inicio) / 60, 1), "min", flush=True)


if __name__ == "__main__":
    main()
