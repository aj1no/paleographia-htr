"""Audit saved corpus/optimization evidence offline, without Docker or torch."""
import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from paleographia.io import read_jsonl, relative, safe_path, sha256, write_json

DEFAULT = "docs/dataset_expansion_20261023"
EVIDENCE = ("training.json", "provenance.json", "partitions.json", "worker_result.json",
            "changed_tensors.json", "initial_tensors.json", "losses.jsonl", "validation_history.json",
            "ketos_arguments.json", "ketos_help.txt", "ketos_train_help.txt", "console.log", "command.json")


def publish(root, run, bundle):
    """Explicitly freeze the completed run; large checkpoints remain local."""
    root, run, bundle = Path(root), Path(run), Path(bundle)
    target = bundle / "training_ppocrv6_smoke"
    if target.exists():
        raise ValueError("Publicação exige evidências novas; não sobrescreva a anterior.")
    result = json.loads((run / "training.json").read_bytes())
    if result["status"] != "executed" or result["plan"]["mode"] != "technical_smoke":
        raise ValueError("Somente ensaio técnico efetivamente executado pode ser publicado aqui.")
    target.mkdir(parents=True)
    for name in EVIDENCE:
        shutil.copyfile(run / name, target / name)
    for dirname in ("data", "implementation"):
        shutil.copytree(run / dirname, target / dirname)
    checkpoint_files = []
    for record in (result["evidence"]["selected_checkpoint"], result["evidence"]["final_weights"]):
        path = run / record["path"]
        if sha256(path) != record["sha256"]:
            raise ValueError("Peso/checkpoint diverge da execução.")
        checkpoint_files.append({"path": relative(path, root), "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json(target / "large_artifacts.json", {"local_only": True, "files": checkpoint_files})
    return target


def freeze(root, bundle):
    root, bundle = Path(root), Path(bundle)
    inventory_path = bundle / "inventory.json"
    if inventory_path.exists():
        raise ValueError("Inventário já existe; não substitua a publicação congelada.")
    paths = [p for p in bundle.rglob("*") if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in p.parts]
    catalog = root / "data/manifests/corpus_expandido_v02"
    paths += [p for p in catalog.rglob("*") if p.is_file() and "pdf_images" not in p.parts]
    paths += [root / n for n in ("configs/curation_sessao_1795_bloco01.json", "configs/training_ppocrv6_smoke.toml",
                                "configs/training_ppocrv6_scientific.toml", "configs/curation_sessao_1795.toml")]
    write_json(inventory_path, {"root": "repository", "files": [{"path": relative(p, root), "sha256": sha256(p)}
                                                               for p in sorted(paths)]})


def audit(root, bundle, local_artifacts=False):
    root, bundle = Path(root), Path(bundle)
    inventory = json.loads((bundle / "inventory.json").read_bytes())
    seen = set()
    for row in inventory["files"]:
        if row["path"] in seen or sha256(safe_path(root, row["path"])) != row["sha256"]:
            raise ValueError("Hash divergente/duplicado: " + row["path"])
        seen.add(row["path"])
    catalog = root / "data/manifests/corpus_expandido_v02"
    core = read_jsonl(catalog / "core_lines.jsonl")
    if Counter(r["review_status"] for r in core) != {"validated": 16, "pending_review": 8}:
        raise ValueError("Estados históricos alterados.")
    if any(r["split"] is not None or r["partition"] != "development" or
           r["review_status"] != r["frozen_sample"]["estado_textual"] or
           r["subsequent_reconference"] != r["frozen_sample"]["reconferencia_posterior"] for r in core):
        raise ValueError("Partição/estado/reconferência histórica alterados.")
    candidates = read_jsonl(bundle / "curation_sessao_1795_bloco01/lines.jsonl")
    if len(candidates) != 8 or any(r["review_status"] != "pending_review" or r["geometry_status"] != "pending_review"
                                  or r["text_diplomatic"] is not None for r in candidates):
        raise ValueError("Candidatos promovidos indevidamente.")
    run = bundle / "training_ppocrv6_smoke"
    result = json.loads((run / "training.json").read_bytes())
    proof = json.loads((run / "worker_result.json").read_bytes())
    changes = json.loads((run / "changed_tensors.json").read_bytes())
    losses = read_jsonl(run / "losses.jsonl")
    if (result["status"] != "executed" or proof["status"] != "executed"
            or result["plan"]["mode"] != "technical_smoke" or proof["optimizer_steps"] != 2
            or proof["optimizer_state_step_min"] != 2 or proof["optimizer_state_step_max"] != 2
            or not proof["base_unchanged"] or not proof["reload_inference_ok"] or not proof["selected_tensors_match_export"]
            or proof["test_used"] or result["scientific_experiment_completed"]):
        raise ValueError("Evidência incompleta de execução ou classificação científica incorreta.")
    if len(changes) != proof["changed_trainable_tensors"] or not changes or any(
            c["before_sha256"] == c["after_sha256"] or c["changed_elements"] <= 0 or c["max_abs_delta"] <= 0 for c in changes):
        raise ValueError("Mudanças reais de tensores não comprovadas.")
    initial = json.loads((run / "initial_tensors.json").read_bytes())
    if any(initial[c["name"]]["sha256"] != c["before_sha256"] for c in changes):
        raise ValueError("Tensores iniciais divergem das mudanças registradas.")
    if [l["optimizer_step"] for l in losses] != [1, 2] or any(not isinstance(l["loss"], (float, int)) for l in losses):
        raise ValueError("Perdas/passos não registrados.")
    if not proof["validation_history"] or "val_metric" not in proof["validation_history"][-1]["metrics"]:
        raise ValueError("Métricas de validação ausentes.")
    provenance = json.loads((run / "provenance.json").read_bytes())
    if sha256(run / "data/plan.json") != provenance["plan_sha256"]:
        raise ValueError("Plano de treinamento alterado.")
    for code in provenance["code"]:
        if sha256(safe_path(run, code["snapshot"])) != code["sha256"]:
            raise ValueError("Código executado divergente.")
    for data in result["plan"]["data"]:
        prefix = run / "data" / data["split"] / data["line_id"]
        if sha256(prefix.with_suffix(".png")) != data["png_sha256"] or sha256(prefix.with_suffix(".gt.txt")) != data["target_sha256"]:
            raise ValueError("Par usado no ensaio alterado.")
    large = json.loads((run / "large_artifacts.json").read_bytes())
    if local_artifacts:
        for row in large["files"]:
            if sha256(safe_path(root, row["path"])) != row["sha256"]:
                raise ValueError("Checkpoint/peso local divergente.")
    return {"valid": True, "files_verified": len(seen), "core_lines": len(core), "new_validated_pairs": 0,
            "candidate_lines": len(candidates), "training_status": "technical_smoke_executed",
            "optimizer_steps": proof["optimizer_steps"], "changed_trainable_tensors": len(changes),
            "reloaded_for_inference": True, "scientific_experiment_completed": False,
            "test_used": False, "large_artifacts_checked": local_artifacts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default=DEFAULT)
    parser.add_argument("--publish-run")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--local-artifacts", action="store_true")
    args = parser.parse_args()
    root, bundle = Path.cwd(), Path(args.bundle)
    if args.publish_run:
        publish(root, Path(args.publish_run), bundle)
    if args.freeze:
        freeze(root, bundle)
    if args.publish_run and not (bundle / "inventory.json").exists():
        print(json.dumps({"status": "published_pending_inventory", "bundle": str(bundle)}))
        return
    print(json.dumps(audit(root, bundle, args.local_artifacts), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
