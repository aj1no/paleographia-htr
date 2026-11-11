"""ketos fine-tuning worker for PP-OCRv6 medium, run inside the pinned Kraken 7.1 image.

Differs from the technical smoke worker (ppocrv6_training_worker.py, kept byte for
byte for its frozen evidence) in what a real fine-tuning needs: configurable label
normalization (NFD fits the checkpoint alphabet), early stopping on validation,
a warmup + cosine schedule, more CPU threads and no step cap. Data, model,
selection and export are native ketos; this file only records evidence.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import resource
import time
import traceback
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def scalar(value):
    if hasattr(value, "detach"):
        value = value.detach().cpu().item()
    if isinstance(value, (float, int)):
        return value if math.isfinite(value) else str(value)
    return str(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()
    started = time.monotonic()
    output = Path("/output")
    result = {"status": "failed", "test_used": False}
    try:
        plan = json.loads(Path(args.plan).read_bytes())
        if digest("/base.safetensors") != plan["base_sha256"]:
            raise ValueError("Checkpoint inicial divergente.")
        if importlib.metadata.version("kraken") not in {"7.1", "7.1.0"}:
            raise ValueError("Requer Kraken 7.1 fixado.")
        import torch
        from lightning.pytorch.callbacks import Callback
        import kraken.train
        from kraken.ketos import cli

        threads = int(plan["threads"])
        torch.set_num_threads(threads)
        torch.set_num_interop_threads(1)
        if plan.get("device", "cpu").startswith("cuda") and not torch.cuda.is_available():
            raise ValueError("GPU pedida, mas CUDA indisponível no contêiner.")
        result["device"] = {"requested": plan.get("device", "cpu"), "precision": plan.get("precision", "32-true"),
                            "cuda": torch.version.cuda, "torch": torch.__version__,
                            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}

        class Evidence(Callback):
            def __init__(self):
                self.trainer, self.validations, self.steps = None, [], 0

            def on_fit_start(self, trainer, module):
                self.trainer = trainer
                self.norms = [m for m in module.modules() if isinstance(m, torch.nn.modules.batchnorm._BatchNorm)]
                if plan.get("freeze_batchnorm", True):
                    for norm in self.norms:
                        for parameter in norm.parameters():
                            parameter.requires_grad_(False)
                result["batchnorm_layers_frozen"] = len(self.norms) if plan.get("freeze_batchnorm", True) else 0

            def on_train_batch_start(self, trainer, module, batch, batch_idx):
                # Lightning puts the module in train mode each epoch and after validation.
                # With batches of 1-2 lines of very different widths, BatchNorm running
                # statistics drift and wreck the pretrained model regardless of the learning
                # rate; keep them at the checkpoint's values.
                if plan.get("freeze_batchnorm", True):
                    for norm in self.norms:
                        norm.eval()

            def on_train_batch_end(self, trainer, module, outputs, batch, batch_idx):
                self.steps = trainer.global_step
                loss = outputs.get("loss") if isinstance(outputs, dict) else outputs
                every = int(plan.get("log_every", 0))
                if every and batch_idx % every == 0:
                    # Human-readable progress line for watching or recording the run.
                    total = trainer.num_training_batches
                    print(f"TREINO  época {trainer.current_epoch + 1}  lote {batch_idx + 1}/{total}  "
                          f"passo {trainer.global_step}  perda {scalar(loss):.4f}  "
                          f"{(time.monotonic() - started) / 60:5.1f} min", flush=True)
                if trainer.global_step % 50 == 0:
                    with (output / "losses.jsonl").open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps({"epoch": trainer.current_epoch, "step": trainer.global_step,
                                                 "loss": scalar(loss), "elapsed_s": time.monotonic() - started}) + "\n")

            def on_validation_end(self, trainer, module):
                item = {"epoch": trainer.current_epoch, "step": trainer.global_step,
                        "elapsed_s": time.monotonic() - started,
                        "metrics": {k: scalar(v) for k, v in trainer.callback_metrics.items()}}
                self.validations.append(item)
                write(output / "validation_history.json", self.validations)
                print("VALIDATION", json.dumps(item), flush=True)
                m = item["metrics"]
                if "val_accuracy" in m:
                    print(f"VALIDAÇÃO  época {item['epoch'] + 1}  passo {item['step']}  "
                          f"acerto de caracteres {float(m['val_accuracy']):.2%}  "
                          f"acerto de palavras {float(m.get('val_word_accuracy', 0)):.2%}", flush=True)

        audit = Evidence()
        original = kraken.train.KrakenTrainer

        class AuditedTrainer(original):
            def __init__(self, *a, **kw):
                kw["callbacks"] = list(kw.get("callbacks", [])) + [audit]
                # O ketos guarda os 10 melhores checkpoints (cerca de 420 MB cada). Só o melhor é usado,
                # então o Lightning mantém apenas ele e apaga os piores ao salvar um novo melhor.
                for callback in kw["callbacks"]:
                    if hasattr(callback, "save_top_k"):
                        callback.save_top_k = int(plan.get("keep_checkpoints", 1))
                kw["enable_progress_bar"] = False
                kw["enable_summary"] = False
                super().__init__(*a, **kw)

        kraken.train.KrakenTrainer = AuditedTrainer
        command = ["--device", plan.get("device", "cpu"), "--precision", plan.get("precision", "32-true"),
                   "--workers", "0", "--threads", str(threads),
                   "--seed", str(plan["seed"]), "--deterministic" if plan.get("deterministic", True) else "--no-deterministic", "train", "--load", "/base.safetensors",
                   "--arch", "ppocrv6", "--format-type", "path", "--linetype", "bbox",
                   "--training-data", "/data/train.lst", "--evaluation-data", "/data/validation.lst",
                   "--output", "/output/checkpoints", "--weights-format", "safetensors",
                   "--resize", "fail", "--normalization", plan["normalization"], "--normalize-whitespace",
                   "--no-reorder", "--height", "96", "--max-width", str(plan["max_width"]), "--pad", "16",
                   "--freq", str(plan.get("freq", 1.0)), "--quit", plan.get("quit", "early"), "--lag", str(plan["lag"]), "--min-delta", str(plan["min_delta"]),
                   "--epochs", str(plan["max_epochs"]), "--min-epochs", str(plan["min_epochs"]),
                   "--batch-size", str(plan["batch_size"]), "--accumulate-grad-batches", str(plan["accumulate"]),
                   "--optimizer", "AdamW", "--lrate", str(plan["learning_rate"]), "--weight-decay", str(plan["weight_decay"]),
                   "--warmup", str(plan["warmup_steps"]), "--schedule", "cosine",
                   "--cos-max", str(plan["max_epochs"]), "--cos-min-lr", str(plan["min_learning_rate"]),
                   "--no-augment"]
        write(output / "ketos_arguments.json", command)
        cli.main(args=command, standalone_mode=False)
        trainer = audit.trainer
        if trainer is None:
            raise ValueError("Nenhum passo de treinamento foi iniciado.")
        best = next(cb for cb in trainer.checkpoint_callbacks if getattr(cb, "best_model_path", ""))
        weights = sorted(Path("/output/checkpoints").glob("best_*.safetensors"))
        if len(weights) != 1:
            raise ValueError("Peso selecionado ausente ou ambíguo.")
        from kraken.tasks import RecognitionTaskModel
        net = RecognitionTaskModel.load_model(str(weights[0])).net
        if type(net).__name__ != "PPOCRv6Model" or net.variant != "medium":
            raise ValueError("Arquitetura do peso exportado divergente.")
        result.update(status="executed", optimizer_steps=trainer.global_step, epochs_run=trainer.current_epoch + 1,
                      selected_checkpoint={"path": str(Path(best.best_model_path).relative_to(output)),
                                           "validation_score": scalar(best.best_model_score)},
                      final_weights={"path": str(weights[0].relative_to(output)), "sha256": digest(weights[0])},
                      validation_history=audit.validations,
                      base_unchanged=digest("/base.safetensors") == plan["base_sha256"])
    except BaseException as exc:
        result.update(reason=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
        traceback.print_exc()
    result.update(duration_seconds=time.monotonic() - started,
                  process_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write(output / "worker_result.json", result)
    return 0 if result["status"] == "executed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
