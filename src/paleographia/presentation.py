"""Portuguese review messages, kept separate from immutable model output."""


def review_policy(config):
    # This is an explicit release decision, not a language detector or a claim
    # that changing a setting can teach Portuguese to a recognition model.
    from pathlib import Path
    from .io import sha256
    settings = config.get("recognition", {})
    policy = config.get("presentation", {})
    approved = (settings.get("backend") == policy.get("evaluated_backend") == "kraken_ppocrv6"
                and bool(settings.get("sha256"))
                and settings.get("sha256") == policy.get("evaluated_model_sha256")
                and bool(settings.get("docker_image_id"))
                and settings.get("docker_image_id") == policy.get("evaluated_docker_image_id")
                and policy.get("evaluated_worker_sha256") == sha256(Path(__file__).with_name("kraken_recognition_worker.py")))
    return {"language": "pt-BR", "experimental": True,
            "automatic_transcription_enabled": bool(policy.get("automatic_transcription_enabled", False) and approved)}


def present_prediction(prediction, line, config):
    if prediction.get("status") != "ok":
        return {"status": "failed", "text": "Não foi possível reconhecer esta linha.",
                "message": "Confira o recorte. O detalhe técnico foi preservado no registro da execução."}
    if line and prediction.get("bbox_xyxy") != line.get("bbox_xyxy"):
        return {"status": "outdated", "text": "Esta sugestão pertence a um recorte anterior.",
                "message": "Confira os novos limites antes de executar outro reconhecimento."}
    if not review_policy(config)["automatic_transcription_enabled"]:
        return {"status": "unavailable_in_portuguese",
                "text": "Leitura automática em português indisponível para o modelo atual.",
                "message": "Confira a imagem e registre sua leitura. O resultado bruto está preservado no registro técnico; ele não foi traduzido nem usado como transcrição."}
    settings = config.get("recognition", {})
    identity = prediction.get("model", {})
    if (identity.get("backend") != "kraken_ppocrv6" or identity.get("sha256") != settings.get("sha256")
            or identity.get("docker_image_id") != settings.get("docker_image_id")
            or identity.get("worker_sha256") != config["presentation"].get("evaluated_worker_sha256")):
        return {"status": "historical_model", "text": "Resultado de outro reconhecedor preservado no histórico.",
                "message": "Execute o reconhecedor experimental atual para gerar uma nova sugestão."}
    if prediction.get("possible_truncation"):
        return {"status": "truncated", "text": "A leitura automática pode estar incompleta.",
                "message": "A geração atingiu seu limite. Confira o recorte antes de usar a sugestão."}
    return {"status": "candidate", "text": prediction.get("text_raw", ""),
            "message": "Sugestão experimental do PP-OCRv6; confira cada palavra na imagem. Não altera sua revisão humana."}


def present_predictions(predictions, lines, config):
    by_id = {line["line_id"]: line for line in lines}
    return [dict(prediction, presentation=present_prediction(
        prediction, by_id.get(prediction["line_id"]), config)) for prediction in predictions]
