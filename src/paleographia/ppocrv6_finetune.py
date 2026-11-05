"""Host side of the PP-OCRv6 fine-tuning: data export, static augmentation and Docker run.

Pairs arrive as dicts with ``crop_image``, ``text`` (one physical line), ``document_id``,
``split`` ("train" or "validation") and ``label_source``. The reserved test document
is refused here, so it can never reach training or checkpoint selection.
"""
import hashlib
import json
import random
import subprocess
import time
import uuid
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

from .io import now, safe_path, sha256, write_json

RESERVED_TEST_DOCUMENTS = {"pagamento_thomas_pardo"}


def augment_variants(image, count, rng):
    """Mild, label-preserving variants: rotation, scale, blur/sharpen, contrast, brightness, noise."""
    variants = []
    for _ in range(count):
        out = image.convert("RGB")
        paper = out.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
        angle = rng.uniform(-1.5, 1.5)
        out = out.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=paper)
        scale = rng.uniform(0.85, 1.15)
        out = out.resize((max(8, int(out.width * scale)), max(8, int(out.height * rng.uniform(0.9, 1.1)))),
                         Image.Resampling.BICUBIC)
        choice = rng.random()
        if choice < 0.3:
            out = out.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 1.0)))
        elif choice < 0.5:
            out = out.filter(ImageFilter.UnsharpMask(radius=1.5, percent=80))
        out = ImageEnhance.Contrast(out).enhance(rng.uniform(0.7, 1.3))
        out = ImageEnhance.Brightness(out).enhance(rng.uniform(0.85, 1.15))
        if rng.random() < 0.3:
            noise = Image.effect_noise(out.size, rng.uniform(4, 12)).convert("RGB")
            out = Image.blend(out, noise, 0.06)
        variants.append(out)
    return variants


def prepare(pairs, output, root, augment=3, seed=1831, max_width=2560):
    """Write ketos ``path`` data (PNG + .gt.txt) under ``output/data``; return evidence rows."""
    root, data = Path(root), Path(output) / "data"
    rng = random.Random(seed)
    evidence, lists = [], {"train": [], "validation": []}
    for index, pair in enumerate(pairs):
        if pair["document_id"] in RESERVED_TEST_DOCUMENTS or pair.get("split") not in lists:
            raise ValueError("Teste reservado ou partição inválida não pode entrar no ajuste.")
        text = pair["text"]
        if not text.strip() or "\n" in text or "\r" in text:
            raise ValueError("Cada alvo deve ser uma linha física não vazia.")
        crop = safe_path(root, pair["crop_image"])
        with Image.open(crop) as opened:
            image = opened.convert("RGB")
        base = f"{pair['split']}_{index:05d}"
        directory = data / pair["split"]
        directory.mkdir(parents=True, exist_ok=True)
        count = pair.get("augment", augment)  # per-pair override, e.g. to balance sources
        images = [image] + (augment_variants(image, count, rng) if pair["split"] == "train" else [])
        for k, variant in enumerate(images):
            if variant.width * 96 / variant.height > max_width:
                continue
            name = f"{base}_{k}"
            variant.info.clear()
            variant.save(directory / (name + ".png"))
            (directory / (name + ".gt.txt")).write_text(text, encoding="utf-8", newline="\n")
            lists[pair["split"]].append(f"/data/{pair['split']}/{name}.png")
        evidence.append({"index": index, "document_id": pair["document_id"], "split": pair["split"],
                         "label_source": pair.get("label_source"), "crop_image": pair["crop_image"],
                         "crop_sha256": sha256(crop),
                         "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "variants": len(images)})
    for split, paths in lists.items():
        if not paths:
            raise ValueError(f"Partição {split} vazia.")
        (data / (split + ".lst")).write_text("\n".join(paths) + "\n", encoding="utf-8", newline="\n")
    return evidence, {k: len(v) for k, v in lists.items()}


def run(pairs, config, output, root, execute=True, timeout_hours=10.0):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Treinamento exige saída nova.")
    output.mkdir(parents=True)
    rec, settings = config["recognition"], config.get("finetune", {})
    model = safe_path(root, rec["model"])
    if sha256(model) != rec["sha256"]:
        raise ValueError("SHA-256 do checkpoint inicial divergente.")
    evidence, counts = prepare(pairs, output, root, settings.get("augment_variants", 3), settings.get("seed", 1831))
    plan = {"seed": settings.get("seed", 1831), "threads": settings.get("threads", 6),
            "normalization": settings.get("normalization", "NFD"), "max_width": 2560,
            "max_epochs": settings.get("max_epochs", 40), "min_epochs": settings.get("min_epochs", 3),
            "lag": settings.get("lag", 5), "min_delta": settings.get("min_delta", 0.001),
            "batch_size": settings.get("batch_size", 4), "accumulate": settings.get("accumulate", 1),
            "learning_rate": settings.get("learning_rate", 1e-4), "min_learning_rate": settings.get("min_learning_rate", 1e-6),
            "weight_decay": settings.get("weight_decay", 0.0), "warmup_steps": settings.get("warmup_steps", 100),
            "device": settings.get("device", "cpu"), "precision": settings.get("precision", "32-true"),
            "deterministic": settings.get("deterministic", True), "freq": settings.get("freq", 1.0),
            "freeze_batchnorm": settings.get("freeze_batchnorm", True),
            "base_sha256": rec["sha256"], "counts": counts, "data": evidence,
            "checkpoint_selection": "ketos val_metric on validation only; reserved test never mounted"}
    write_json(output / "data" / "plan.json", plan)
    worker = Path(__file__).with_name("ppocrv6_finetune_worker.py").resolve()
    implementation = output / "implementation"
    implementation.mkdir()
    for source in (Path(__file__), worker):
        (implementation / source.name).write_bytes(source.read_bytes())
    name = "paleographia-finetune-" + uuid.uuid4().hex[:12]
    paths = [model.resolve(), (implementation / worker.name).resolve(), (output / "data").resolve(), output]
    if any("," in str(p) for p in paths):
        raise ValueError("Mount Docker não aceita vírgula nos caminhos.")
    image_id = settings.get("docker_image_id") or rec["docker_image_id"]
    command = ["docker", "run", "--rm", "--pull", "never", "--name", name, "--network", "none",
               *(["--gpus", "all"] if plan["device"].startswith("cuda") else []),
               "--cpus", str(plan["threads"]), "--memory", settings.get("memory", "7g"), "--shm-size", "512m",
               "--env", f"OMP_NUM_THREADS={plan['threads']}", "--env", f"MKL_NUM_THREADS={plan['threads']}",
               "--env", "TORCHDYNAMO_DISABLE=1"]
    for path, target, readonly in zip(paths, ("/base.safetensors", "/worker.py", "/data", "/output"), (1, 1, 1, 0)):
        command += ["--mount", f"type=bind,source={path},target={target}" + (",readonly" if readonly else "")]
    command += [image_id, "python", "/worker.py", "--plan", "/data/plan.json"]
    write_json(output / "command.json", command)
    result = {"status": "ready", "started_at": now(), "counts": counts, "docker_image_id": image_id,
              "device": plan["device"], "precision": plan["precision"],
              "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()}
    if execute:
        started = time.monotonic()
        try:
            with (output / "console.log").open("w", encoding="utf-8") as log:
                done = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout_hours * 3600)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=60)
            raise ValueError("Orçamento de tempo excedido; contêiner interrompido.") from None
        proof_path = output / "worker_result.json"
        # 137 = SIGKILL, usually the container memory limit; no worker result is written then.
        proof = json.loads(proof_path.read_bytes()) if proof_path.exists() else {
            "status": "failed", "reason": f"contêiner encerrou sem resultado (código {done.returncode}; 137 indica falta de memória)"}
        result.update(status=proof.get("status"), returncode=done.returncode, evidence=proof,
                      duration_seconds=time.monotonic() - started, finished_at=now())
        if sha256(model) != rec["sha256"]:
            raise ValueError("Checkpoint inicial alterado.")
    write_json(output / "training.json", result)
    return result
