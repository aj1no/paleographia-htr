from pathlib import Path

from PIL import Image

from .data import validate
from .evaluation import aggregate, counts
from .experiments import provenance
from .io import safe_path, write_json
from .backends import create_recognizer
from .recognition import ModelUnavailable


def training_run(rows, pages, config, output_dir, root=Path.cwd(), execute=False, manifests=()):
    output = Path(output_dir)
    if output.exists():
        raise ValueError("Treinamento exige saída nova.")
    output.mkdir(parents=True)
    report = validate(rows, root, "training", pages)
    write_json(output/"validation.json", report)
    write_json(output/"provenance.json", provenance(config, manifests))
    result = {"status": "not_executed", "mode": "execute" if execute else "dry_run", "validation": report}
    if not report["valid"]:
        write_json(output/"training.json", result)
        return result
    try:
        recognizer = create_recognizer(config, root)
        if config.get("recognition", {}).get("backend") == "kraken_ppocrv6":
            raise ModelUnavailable("Treinamento do backend Kraken não foi implementado neste piloto; use somente reconhecimento e revisão manual.")
        recognizer.load()
        processor, model = recognizer.processor, recognizer.model
        tokenizer = processor.tokenizer
        settings = config.get("training", {})
        limit = settings.get("max_target_length", 128)
        # Do not inspect held-out text for parameter selection, including target limits.
        development = [r for r in rows if r["split"] in {"train", "validation"}]
        lengths = [(r["line_id"], len(tokenizer(r["text_diplomatic"], truncation=False).input_ids)) for r in development]
        excessive = [{"line_id": lid, "tokens": length} for lid, length in lengths if length > limit]
        result.update(model=recognizer.status(), target_limit=limit, excessive_targets=excessive,
                      counts={s: sum(r["split"] == s for r in rows) for s in ("train", "validation", "test")})
        if excessive:
            raise ValueError("Alvos excedentes; ajuste o protocolo explicitamente. Nenhum alvo foi truncado.")
        if model.config.decoder_start_token_id is None:
            start = tokenizer.cls_token_id if tokenizer.cls_token_id is not None else tokenizer.bos_token_id
            if start is None:
                raise ValueError("Checkpoint sem decoder_start_token_id.")
            model.config.decoder_start_token_id = start
        model.config.pad_token_id = tokenizer.pad_token_id
        if model.config.pad_token_id is None:
            raise ValueError("Checkpoint sem token de padding.")
        result["decoder_start_token_id"] = model.config.decoder_start_token_id
        if not execute:
            result["status"] = "ready_dry_run"
            write_json(output/"training.json", result)
            return result
        import numpy as np
        import torch
        from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, default_data_collator, set_seed
        set_seed(settings.get("seed", 1831))

        class Dataset(torch.utils.data.Dataset):
            def __init__(self, split):
                self.rows = [r for r in development if r["split"] == split]

            def __len__(self):
                return len(self.rows)

            def __getitem__(self, index):
                row = self.rows[index]
                with Image.open(safe_path(root, row["crop_image"])) as image:
                    pixels = processor(images=image.convert("RGB"), return_tensors="pt").pixel_values.squeeze(0)
                labels = tokenizer(row["text_diplomatic"], padding="max_length", max_length=limit, truncation=False).input_ids
                if len(labels) > limit:
                    raise ValueError("Alvo excedente; truncamento proibido.")
                labels = torch.tensor([token if token != tokenizer.pad_token_id else -100 for token in labels])
                # VisionEncoderDecoderModel shifts labels internally; no manual shift.
                return {"pixel_values": pixels, "labels": labels}

        def compute_metrics(pred):
            labels = np.array(pred.label_ids, copy=True)
            labels[labels == -100] = tokenizer.pad_token_id
            references = processor.batch_decode(labels, skip_special_tokens=True)
            predictions = processor.batch_decode(pred.predictions, skip_special_tokens=True)
            metrics = aggregate([counts(r, p) for r, p in zip(references, predictions, strict=True)])
            return {"cer": metrics["characters"]["rate"], "wer": metrics["words"]["rate"]}

        for key, value in config["generation"].items():
            setattr(model.generation_config, key, value)
        args = Seq2SeqTrainingArguments(output_dir=str(output/"checkpoints"), predict_with_generate=True,
                 eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
                 metric_for_best_model="cer", greater_is_better=False, save_total_limit=2,
                 per_device_train_batch_size=settings.get("batch_size", 1),
                 per_device_eval_batch_size=settings.get("batch_size", 1),
                 gradient_accumulation_steps=settings.get("gradient_accumulation_steps", 4),
                 num_train_epochs=settings.get("epochs", 3), learning_rate=settings.get("learning_rate", 5e-5),
                 seed=settings.get("seed", 1831), data_seed=settings.get("seed", 1831),
                 fp16=recognizer.device.startswith("cuda") and config["recognition"].get("precision") == "float16",
                 bf16=recognizer.device.startswith("cuda") and config["recognition"].get("precision") == "bfloat16",
                 use_cpu=recognizer.device == "cpu", report_to="none", dataloader_num_workers=0)
        trainer = Seq2SeqTrainer(model=model, args=args, processing_class=processor,
                  train_dataset=Dataset("train"), eval_dataset=Dataset("validation"),
                  data_collator=default_data_collator, compute_metrics=compute_metrics)
        fit = trainer.train()
        trainer.save_model(str(output/"model"))
        processor.save_pretrained(output/"model")
        result.update(status="executed", train_metrics=fit.metrics, validation_metrics=trainer.evaluate(),
                      test_status="reserved_not_used; evaluate separately once after selection")
    except Exception as exc:
        result.update(status="failed" if execute else "not_executed", reason=str(exc))
    write_json(output/"training.json", result)
    return result
