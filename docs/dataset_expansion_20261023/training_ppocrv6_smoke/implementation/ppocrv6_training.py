"""Explicit ketos fine-tuning, isolated from the editor's inference runtime."""
import json
import math
import platform
import re
import subprocess
import time
import uuid
from pathlib import Path

from .data import check_reviewer, validate
from .io import now, read_jsonl, relative, safe_path, sha256, write_json


def select_data(rows, pages, settings, root):
    mode = settings.get("mode")
    if mode == "technical_smoke":
        by_id = {r["line_id"]: r for r in rows}
        ids = {split: settings.get(split + "_line_ids", []) for split in ("train", "validation")}
        if any(not v or len(v) != len(set(v)) for v in ids.values()) or set(ids["train"]) & set(ids["validation"]):
            raise ValueError("Ensaio exige IDs explícitos, únicos e separados de treino/validação.")
        selected = {s: [by_id[i] for i in names] for s, names in ids.items()}
        flat = [r for rs in selected.values() for r in rs]
        if len(flat) > 8 or settings.get("epochs", 1) != 1 or settings.get("batch_size", 1) != 1:
            raise ValueError("Ensaio limitado a oito linhas, lote 1 e uma época.")
        if any(r.get("partition") != "development" or r.get("split") == "test" for r in flat):
            raise ValueError("Ensaio usa somente desenvolvimento já exposto; teste é proibido.")
        report = validate(flat, root, "evaluation", pages)
        protocol = {"mode": mode, "scientific_evaluation": False, "assignments": ids,
                    "document_overlap_permitted_for_technical_check_only": True,
                    "test_used": False, "limitation": "Otimização e recarga; não mede generalização."}
    elif mode == "scientific":
        protocol_path = safe_path(root, settings["partition_protocol"])
        protocol = json.loads(protocol_path.read_bytes())
        groups = protocol.get("groups", [])
        assignments = {}
        for group in groups:
            if group.get("independence_status") != "validated" or group.get("scientific_split") not in {"train", "validation", "test"}:
                raise ValueError("Partições científicas exigem independência documental confirmada.")
            check_reviewer(group)
            if group["document_id"] in assignments:
                raise ValueError("Documento repetido no protocolo.")
            assignments[group["document_id"]] = group["scientific_split"]
        for row in rows:
            if row.get("split") != assignments.get(row["document_id"]):
                raise ValueError("Manifest e protocolo de partições divergem.")
            if (row.get("partition") == "development" or row["document_id"] == "tt_pbr_0004_026_traslado_1767") and row.get("split") != "train":
                raise ValueError("Desenvolvimento previamente exposto não pode virar validação/teste científico.")
        report = validate(rows, root, "training", pages)
        selected = {s: [r for r in rows if r["split"] == s] for s in ("train", "validation")}
        protocol = dict(protocol, protocol_sha256=sha256(protocol_path), test_exported=False)
    else:
        raise ValueError("Defina training.mode como technical_smoke ou scientific explicitamente.")
    if not report["valid"]:
        raise ValueError("; ".join(report["errors"]))
    # Check content aliases across train/validation even in the technical check.
    owners = {}
    for split, records in selected.items():
        for row in records:
            digest = sha256(safe_path(root, row["crop_image"]))
            if digest in owners and owners[digest] != split:
                raise ValueError("Mesmo recorte em treino e validação.")
            owners[digest] = split
    return selected, protocol, report


def docker_command(image_id, model, worker, data, output, name):
    paths = [Path(p).resolve() for p in (model, worker, data, output)]
    if any("," in str(p) for p in paths):
        raise ValueError("Mount Docker não aceita vírgula nos caminhos.")
    command = ["docker", "run", "--rm", "--pull", "never", "--name", name,
               "--network", "none", "--cpus", "2", "--memory", "4g", "--shm-size", "256m",
               "--env", "OMP_NUM_THREADS=2", "--env", "MKL_NUM_THREADS=2"]
    # Native Kraken uses torch.compile, while the pinned inference image has no
    # C++ toolchain. Eager autograd keeps the exact image/packages/model intact.
    command += ["--env", "TORCHDYNAMO_DISABLE=1"]
    for path, target, readonly in zip(paths, ("/base.safetensors", "/worker.py", "/data", "/output"), (True, True, True, False)):
        command += ["--mount", f"type=bind,source={path},target={target}" + (",readonly" if readonly else "")]
    return command + [image_id, "python", "/worker.py", "--plan", "/data/plan.json"]


def run(rows, pages, config, output_dir, root=Path.cwd(), execute=False, manifests=()):
    root, output = Path(root).resolve(), Path(output_dir).resolve()
    if output.exists():
        raise ValueError("Treinamento exige saída nova.")
    output.mkdir(parents=True)
    result = {"status": "not_executed", "mode": "execute" if execute else "dry_run", "started_at": now(),
              "engine": "ketos", "backend": "kraken_ppocrv6", "test_used": False}
    started = time.monotonic()
    try:
        settings = dict(config.get("training", {}))
        if settings.get("engine") != "ketos":
            raise ValueError("Ajuste fino requer configuração separada com training.engine=ketos.")
        selected, protocol, validation = select_data(rows, pages, settings, root)
        result.update(validation=validation, protocol=protocol)
        write_json(output / "partitions.json", protocol)
        rec = config["recognition"]
        model = safe_path(root, rec["model"])
        if sha256(model) != rec["sha256"]:
            raise ValueError("SHA-256 do checkpoint inicial divergente.")
        image_id = rec["docker_image_id"]
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
            raise ValueError("Exige identidade completa da imagem Docker fixada.")
        observed = subprocess.run(["docker", "image", "inspect", image_id, "--format", "{{.Id}}"],
                                  capture_output=True, text=True, check=True, timeout=30).stdout.strip()
        if observed != image_id:
            raise ValueError("Identidade Docker divergente.")
        if rec.get("device") != "cpu" or rec.get("precision") != "float32":
            raise ValueError("Este experimento fixou CPU/float32.")
        epochs, batch = settings.get("epochs", 1), settings.get("batch_size", 1)
        lr = settings.get("learning_rate", 1e-5)
        timeout = settings.get("timeout_seconds", 300)
        if (type(epochs) is not int or not 1 <= epochs <= 100 or type(batch) is not int or not 1 <= batch <= 32
                or not isinstance(lr, (int, float)) or not math.isfinite(lr) or not 0 < lr <= .01
                or type(timeout) is not int or not 30 <= timeout <= 3600):
            raise ValueError("Orçamento ou taxa de aprendizado inválidos.")
        data = output / "data"
        data.mkdir()
        evidence = []
        for split, records in selected.items():
            directory = data / split
            directory.mkdir()
            paths = []
            for row in records:
                lid = row["line_id"]
                if not re.fullmatch(r"[a-zA-Z0-9_-]+", lid):
                    raise ValueError("ID inseguro.")
                crop = safe_path(root, row["crop_image"])
                if row.get("crop_sha256") and row["crop_sha256"] != sha256(crop):
                    raise ValueError("Recorte diverge do hash registrado.")
                # Re-encode to PNG, so the extension always describes the bytes.
                from PIL import Image
                with Image.open(crop) as im:
                    rgb = im.convert("RGB")
                    rgb.info.clear()
                    rgb.save(directory / (lid + ".png"))
                text = row["text_diplomatic"]
                if "\n" in text or "\r" in text or not text.strip():
                    raise ValueError("Cada alvo deve corresponder a uma linha física não vazia.")
                (directory / (lid + ".gt.txt")).write_text(text, encoding="utf-8", newline="\n")
                paths.append(f"/data/{split}/{lid}.png")
                evidence.append({"line_id": lid, "document_id": row["document_id"], "split": split,
                                 "source_crop_sha256": sha256(crop), "reference_policy": row.get("reference_policy"),
                                 "reviewer": row["reviewer"], "reviewed_at": row["reviewed_at"],
                                 "png_sha256": sha256(directory / (lid + ".png")),
                                 "target_sha256": sha256(directory / (lid + ".gt.txt"))})
            (data / (split + ".lst")).write_text("\n".join(paths) + "\n", encoding="utf-8", newline="\n")
        plan = {"mode": settings["mode"], "seed": settings.get("seed", 1831), "epochs": epochs,
                "batch_size": batch, "learning_rate": lr, "base_sha256": rec["sha256"],
                "resize": "fail", "normalization": "NFC", "max_width": 2560,
                "torch_compile": False, "execution": "eager_autograd; no C++ compiler in pinned image",
                "checkpoint_selection": "maximum native val_metric; validation only", "data": evidence}
        write_json(data / "plan.json", plan)
        worker_source = Path(__file__).with_name("ppocrv6_training_worker.py")
        implementation = output / "implementation"
        implementation.mkdir()
        for source in (Path(__file__), worker_source):
            (implementation / source.name).write_bytes(source.read_bytes())
        worker = implementation / worker_source.name
        write_json(output / "provenance.json", {"config": config, "plan_sha256": sha256(data / "plan.json"),
                   "docker_image_id": observed, "base_sha256": sha256(model), "host_python": platform.python_version(),
                   "manifests": [{"path": relative(p, root), "sha256": sha256(p)} for p in manifests],
                   "code": [{"path": "src/paleographia/" + p.name, "sha256": sha256(p),
                             "snapshot": "implementation/" + p.name} for p in (Path(__file__), worker_source)],
                   "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()})
        command = docker_command(observed, model, worker, data, output, "paleographia-train-" + uuid.uuid4().hex[:12])
        write_json(output / "command.json", command)
        result.update(status="ready_dry_run", plan=plan, timeout_seconds=timeout)
        if execute:
            name = command[command.index("--name") + 1]
            try:
                with (output / "console.log").open("w", encoding="utf-8") as log:
                    completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
            except subprocess.TimeoutExpired:
                # Killing the docker client alone does not terminate its container.
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=30)
                raise ValueError("Orçamento de tempo excedido; contêiner interrompido.") from None
            if completed.returncode:
                raise ValueError(f"ketos falhou (código {completed.returncode}); veja console.log e worker_result.json.")
            proof = json.loads((output / "worker_result.json").read_bytes())
            if (not proof.get("optimizer_steps", 0) or not proof.get("changed_trainable_tensors", 0)
                    or not proof.get("reload_inference_ok") or proof.get("status") != "executed"):
                raise ValueError("Evidência incompleta de otimização, alteração de tensores e recarga.")
            if sha256(model) != rec["sha256"]:
                raise ValueError("Checkpoint inicial alterado.")
            result.update(status="executed", evidence=proof,
                          scientific_experiment_completed=settings["mode"] == "scientific",
                          held_out_evaluation="not_run; freeze selected model before test")
    except Exception as exc:
        result.update(status="failed" if execute else "not_executed", reason=f"{type(exc).__name__}: {exc}")
    result.update(finished_at=now(), duration_seconds=time.monotonic() - started)
    write_json(output / "training.json", result)
    return result
