"""Audited native ketos entry point for the pinned, offline Linux experiment.

The only instrumentation is a Lightning callback and resource/step limits.
Model, data module, optimization, validation, selection and conversion are ketos.
No project/editor/reference directories are mounted into this process.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import resource
import subprocess
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
    result = {"status": "failed", "optimizer_steps": 0, "changed_trainable_tensors": 0,
              "reload_inference_ok": False, "test_used": False}
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

        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        result["environment"] = {"python": platform.python_version(), "platform": platform.platform(),
                                 "device": "cpu", "precision": "32-true", "cpu_threads": torch.get_num_threads(),
                                 "torch_compile": False, "torch_dynamo_disabled": __import__("os").environ.get("TORCHDYNAMO_DISABLE"),
                                 "cgroup_memory_max": Path("/sys/fs/cgroup/memory.max").read_text().strip(),
                                 "versions": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}}
        for subcommand in ([], ["train"]):
            proc = subprocess.run(["ketos", *subcommand, "--help"], capture_output=True, text=True, check=True)
            (output / ("ketos_train_help.txt" if subcommand else "ketos_help.txt")).write_text(proc.stdout, encoding="utf-8")

        class Evidence(Callback):
            def __init__(self):
                self.initial = {}
                self.losses = []
                self.validations = []
                self.trainer = None

            def on_fit_start(self, trainer, module):
                self.trainer = trainer
                self.initial = {n: p.detach().cpu().clone() for n, p in module.named_parameters() if p.requires_grad}
                write(output / "initial_tensors.json", {n: {"shape": list(p.shape), "sha256": hashlib.sha256(p.numpy().tobytes()).hexdigest()}
                                                       for n, p in self.initial.items()})

            def on_train_batch_end(self, trainer, module, outputs, batch, batch_idx):
                loss = outputs.get("loss") if isinstance(outputs, dict) else outputs
                if loss is None:
                    loss = trainer.callback_metrics.get("loss", trainer.callback_metrics.get("train_loss"))
                item = {"epoch": trainer.current_epoch, "batch": batch_idx,
                        "optimizer_step": trainer.global_step, "loss": scalar(loss),
                        "learning_rates": [g["lr"] for opt in trainer.optimizers for g in opt.param_groups]}
                self.losses.append(item)
                with (output / "losses.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(item, allow_nan=False) + "\n")

            def on_validation_end(self, trainer, module):
                self.validations.append({"epoch": trainer.current_epoch, "optimizer_step": trainer.global_step,
                                         "metrics": {k: scalar(v) for k, v in trainer.callback_metrics.items()}})
                write(output / "validation_history.json", self.validations)

        audit = Evidence()
        original = kraken.train.KrakenTrainer

        class AuditedTrainer(original):
            def __init__(self, *a, **kw):
                kw["callbacks"] = list(kw.get("callbacks", [])) + [audit]
                kw["enable_progress_bar"] = False
                kw["enable_summary"] = False
                # Technical mode has an independent hard cap, in addition to one
                # epoch over at most eight explicitly selected reviewed examples.
                if plan["mode"] == "technical_smoke":
                    kw["max_steps"] = 8
                super().__init__(*a, **kw)

        kraken.train.KrakenTrainer = AuditedTrainer
        command = ["--device", "cpu", "--precision", "32-true", "--workers", "0", "--threads", "2",
                   "--seed", str(plan["seed"]), "--deterministic", "train", "--load", "/base.safetensors",
                   "--arch", "ppocrv6", "--format-type", "path", "--linetype", "bbox",
                   "--training-data", "/data/train.lst", "--evaluation-data", "/data/validation.lst",
                   "--output", "/output/checkpoints", "--weights-format", "safetensors",
                   "--resize", "fail", "--normalization", "NFC", "--normalize-whitespace", "--no-reorder",
                   "--height", "96", "--max-width", str(plan["max_width"]), "--pad", "16",
                   "--quit", "fixed", "--epochs", str(plan["epochs"]), "--min-epochs", "0",
                   "--batch-size", str(plan["batch_size"]), "--accumulate-grad-batches", "1",
                   "--optimizer", "AdamW", "--lrate", str(plan["learning_rate"]), "--weight-decay", "0",
                   "--warmup", "0", "--schedule", "constant", "--no-augment"]
        write(output / "ketos_arguments.json", command)
        cli.main(args=command, standalone_mode=False)
        trainer = audit.trainer
        if trainer is None:
            raise ValueError("Nenhum passo de treinamento foi iniciado.")
        best = next(cb for cb in trainer.checkpoint_callbacks if getattr(cb, "best_model_path", ""))
        checkpoint = torch.load(best.best_model_path, map_location="cpu", weights_only=False)
        changed = []
        for name, before in audit.initial.items():
            after = checkpoint["state_dict"][name]
            if not torch.equal(before, after):
                delta = (after.float() - before.float()).abs()
                changed.append({"name": name, "shape": list(before.shape), "max_abs_delta": delta.max().item(),
                                "changed_elements": torch.count_nonzero(delta).item(),
                                "before_sha256": hashlib.sha256(before.numpy().tobytes()).hexdigest(),
                                "after_sha256": hashlib.sha256(after.numpy().tobytes()).hexdigest()})
        write(output / "changed_tensors.json", changed)
        optimizer_steps = [scalar(s["step"]) for opt in checkpoint.get("optimizer_states", [])
                           for s in opt.get("state", {}).values() if "step" in s]
        weights = sorted(Path("/output/checkpoints").glob("best_*.safetensors"))
        if len(weights) != 1:
            raise ValueError("Peso selecionado ausente ou ambíguo.")
        from kraken.tasks import RecognitionTaskModel
        from kraken.configs import RecognitionInferenceConfig
        from kraken.lib.dataset import ImageInputTransforms
        from PIL import Image

        model = RecognitionTaskModel.load_model(str(weights[0]))
        net = model.net
        if type(net).__name__ != "PPOCRv6Model" or net.variant != "medium":
            raise ValueError("Arquitetura do peso exportado divergente.")
        # Prove that the converted/reloaded weights match the selected checkpoint.
        selected_net = {k.removeprefix("net."): v for k, v in checkpoint["state_dict"].items() if k.startswith("net.")}
        reloaded_state = net.state_dict()
        if set(selected_net) != set(reloaded_state) or any(not torch.equal(v, reloaded_state[k]) for k, v in selected_net.items()):
            raise ValueError("Peso convertido não corresponde aos tensores do checkpoint selecionado.")
        net.prepare_for_inference(RecognitionInferenceConfig(accelerator="cpu", device=1, precision="32-true",
                                  batch_size=1, num_line_workers=0, padding=16, bidi_reordering=False))
        batch, channels, height, width = net.input
        transforms = ImageInputTransforms(batch, height, width, channels, (16, 0), False, dtype=net._m_dtype)
        image_path = Path("/data/validation.lst").read_text().splitlines()[0]
        with Image.open(image_path) as im, torch.inference_mode():
            tensor = transforms(im.convert("RGB")).unsqueeze(0)
            decoded, lengths = net._rec_predict(tensor, torch.LongTensor([tensor.shape[-1]]))
        if not audit.losses or any(not isinstance(r["loss"], (int, float)) for r in audit.losses):
            raise ValueError("Perda de treinamento numérica não registrada.")
        if not changed or not optimizer_steps or min(optimizer_steps) <= 0 or checkpoint.get("global_step", 0) <= 0:
            raise ValueError("Não há evidência de otimização efetiva.")
        result.update(status="executed", optimizer_steps=checkpoint["global_step"],
                      optimizer_state_step_min=min(optimizer_steps), optimizer_state_step_max=max(optimizer_steps),
                      changed_trainable_tensors=len(changed), trainable_tensors=len(audit.initial),
                      reload_inference_ok=True, selected_tensors_match_export=True,
                      reload_check={"image": image_path, "text_raw": "".join(i[0] for i in decoded[0]),
                                    "purpose": "technical reload check; not held-out quality evidence"},
                      selected_checkpoint={"path": str(Path(best.best_model_path).relative_to(output)),
                                           "sha256": digest(best.best_model_path), "validation_score": best.best_model_score.item()},
                      final_weights={"path": str(weights[0].relative_to(output)), "sha256": digest(weights[0])},
                      losses=audit.losses, validation_history=audit.validations,
                      final_callback_metrics={k: scalar(v) for k, v in trainer.callback_metrics.items()},
                      base_unchanged=digest("/base.safetensors") == plan["base_sha256"])
    except BaseException as exc:
        result.update(reason=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
        traceback.print_exc()
    result.update(duration_seconds=time.monotonic() - started,
                  process_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    peak = Path("/sys/fs/cgroup/memory.peak")
    if peak.exists():
        result["cgroup_peak_memory_bytes"] = int(peak.read_text().strip())
    write(output / "worker_result.json", result)
    return 0 if result["status"] == "executed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
