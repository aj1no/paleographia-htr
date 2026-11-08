"""Treino supervisionado CRNN-CTC do zero (ou a partir do pré-treino não supervisionado).

Escolha do checkpoint: só pela validação interna da Inquisição (documentos separados).
A validação de Jundiaí é transcrita uma única vez, no fim, com o checkpoint já escolhido.

Exemplos:
  python treinar.py --nome supervisionado_do_zero --passos 30000
  python treinar.py --nome ssl_ajuste --passos 30000 --init runs/ssl/encoder.pt
  python treinar.py --nome sonda_ssl --passos 6000 --init runs/ssl/encoder.pt --congelar
  python treinar.py --nome poucos_rotulos --passos 8000 --fracao 0.05
"""
import argparse
import json
import random
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from comum import (AQUI, CRNN, USAR_FP16, Codificador, Linhas, LotesPorLargura, carregar_alfabeto, carregar_manifesto,
                   cer_wer, juntar, transcrever)

REPETIR_JUNDIAI = 3  # o Traslado é pequeno e é o domínio-alvo


def iniciar_trabalhador(_):
    info = torch.utils.data.get_worker_info()
    info.dataset.rng = random.Random(torch.initial_seed() % (1 << 31))
    torch.set_num_threads(1)  # evita disputa de CPU com o processo principal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True)
    ap.add_argument("--passos", type=int, default=30000)
    ap.add_argument("--lote", type=int, default=24)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--init", default=None, help="encoder do pré-treino não supervisionado")
    ap.add_argument("--congelar", action="store_true", help="sonda linear: só a camada de saída aprende")
    ap.add_argument("--fracao", type=float, default=1.0, help="fração das linhas rotuladas de treino")
    ap.add_argument("--avaliar_cada", type=int, default=1000)
    ap.add_argument("--semente", type=int, default=20261107)
    ap.add_argument("--trabalhadores", type=int, default=4)
    a = ap.parse_args()

    torch.manual_seed(a.semente)
    random.seed(a.semente)
    np.random.seed(a.semente)
    pasta = AQUI / "runs" / a.nome
    pasta.mkdir(parents=True, exist_ok=True)
    disp = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    manifesto = carregar_manifesto()
    cod = Codificador(carregar_alfabeto())
    treino = [r for r in manifesto if r["split"] == "treino"]
    if a.fracao < 1:
        treino = random.Random(a.semente).sample(treino, max(1, round(a.fracao * len(treino))))
    rotuladas = len(treino)
    treino = treino + [r for r in treino if r["fonte"].startswith("jundiai")] * (REPETIR_JUNDIAI - 1)
    val_inq = [r for r in manifesto if r["split"] == "val_inq"]
    val_jdi = [r for r in manifesto if r["split"] == "val_jundiai"]
    assert not any("pagamento" in json.dumps(r).lower() for r in manifesto)

    modelo = CRNN(len(cod.alfabeto) + 1).to(disp)
    if a.init:
        modelo.enc.load_state_dict(torch.load(AQUI / a.init, map_location=disp))
    if a.congelar:
        for p in modelo.enc.parameters():
            p.requires_grad = False
    treinaveis = [p for p in modelo.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(treinaveis, lr=a.lr, weight_decay=1e-4)
    agenda = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=a.passos, pct_start=0.05)
    escala = torch.amp.GradScaler(enabled=USAR_FP16 and disp.type == "cuda")
    ctc = nn.CTCLoss(blank=0, zero_infinity=True)

    ds = Linhas(treino, cod, aumentar_dados=True, semente=a.semente)
    carregador = DataLoader(ds, batch_sampler=LotesPorLargura(ds, a.lote, a.semente), collate_fn=juntar,
                            num_workers=a.trabalhadores, persistent_workers=a.trabalhadores > 0,
                            worker_init_fn=iniciar_trabalhador if a.trabalhadores else None, pin_memory=True)
    config = vars(a) | {"linhas_rotuladas": rotuladas, "amostras_por_epoca": len(treino),
                        "val_inq": len(val_inq), "val_jundiai": len(val_jdi), "alfabeto": len(cod.alfabeto),
                        "parametros": sum(p.numel() for p in modelo.parameters()),
                        "treinaveis": sum(p.numel() for p in treinaveis),
                        "gpu": torch.cuda.get_device_name(0) if disp.type == "cuda" else "cpu",
                        "torch": torch.__version__}
    (pasta / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(config, ensure_ascii=False), flush=True)

    log = (pasta / "log.jsonl").open("a", encoding="utf-8")
    passo, melhor, inicio, perdas = 0, None, time.time(), []
    while passo < a.passos:
        modelo.train()
        if a.congelar:
            modelo.enc.eval()
        for imgs, alvos, tam_ent, tam_alvo, _ in carregador:
            imgs = imgs.to(disp, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.float16, enabled=USAR_FP16 and disp.type == "cuda"):
                logits = modelo(imgs)
            logp = logits.float().log_softmax(-1)
            perda = ctc(logp, alvos, tam_ent, tam_alvo)
            opt.zero_grad(set_to_none=True)
            escala.scale(perda).backward()
            escala.unscale_(opt)
            nn.utils.clip_grad_norm_(treinaveis, 5.0)
            escala.step(opt)
            escala.update()
            agenda.step()
            perdas.append(perda.item())
            passo += 1
            if passo % 100 == 0:
                print(f"passo {passo}/{a.passos} perda {np.mean(perdas[-100:]):.3f} "
                      f"lr {agenda.get_last_lr()[0]:.2e} {time.time() - inicio:.0f}s", flush=True)
            if passo % a.avaliar_cada == 0 or passo == a.passos:
                hip = transcrever(modelo, val_inq, cod, disp)
                cer, wer = cer_wer([(r["texto"], h) for r, h in zip(val_inq, hip)])
                reg = {"passo": passo, "perda": float(np.mean(perdas[-a.avaliar_cada:])), "cer_val_inq": cer,
                       "wer_val_inq": wer, "segundos": round(time.time() - inicio)}
                if melhor is None or cer < melhor["cer_val_inq"]:
                    melhor = reg
                    torch.save(modelo.state_dict(), pasta / "melhor.pt")
                reg["melhor_ate_aqui"] = melhor["passo"]
                log.write(json.dumps(reg) + "\n")
                log.flush()
                print("AVAL", json.dumps(reg), "| exemplo:", hip[0][:70], flush=True)
                modelo.train()
                if a.congelar:
                    modelo.enc.eval()
            if passo >= a.passos:
                break
    torch.save(modelo.state_dict(), pasta / "ultimo.pt")

    # Avaliação final, uma vez, com o checkpoint escolhido pela validação interna.
    modelo.load_state_dict(torch.load(pasta / "melhor.pt", map_location=disp))
    resultado = {"checkpoint": f"passo {melhor['passo']} (menor CER na validação interna da Inquisição)",
                 "minutos": round((time.time() - inicio) / 60, 1)}
    for nome, regs in (("val_inq", val_inq), ("val_jundiai", val_jdi)):
        hip = transcrever(modelo, regs, cod, disp)
        cer, wer = cer_wer([(r["texto"], h) for r, h in zip(regs, hip)])
        resultado[nome] = {"linhas": len(regs), "cer": cer, "wer": wer}
        por_doc = {}
        for r, h in zip(regs, hip):
            por_doc.setdefault(r["documento"], []).append((r["texto"], h))
        if nome == "val_jundiai":
            resultado[nome]["por_documento"] = {d: dict(zip(("cer", "wer"), cer_wer(p))) | {"linhas": len(p)}
                                                for d, p in por_doc.items()}
            resultado[nome]["linhas_transcritas"] = [{"documento": r["documento"], "referencia": r["texto"],
                                                      "modelo": h} for r, h in zip(regs, hip)]
    (pasta / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print("RESULTADO", json.dumps({k: v for k, v in resultado.items() if k != "val_jundiai"} |
                                  {"val_jundiai": {k: resultado["val_jundiai"][k] for k in ("cer", "wer")}}), flush=True)


if __name__ == "__main__":
    main()
