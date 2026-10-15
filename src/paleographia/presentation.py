"""Portuguese review messages, kept separate from immutable model output."""


def review_policy(config):
    # This is an explicit release decision, not a language detector or a claim
    # that changing a setting can teach Portuguese to a recognition model.
    return {"language": "pt-BR", "automatic_transcription_enabled":
            config.get("presentation", {}).get("automatic_transcription_enabled", False)}


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
    if prediction.get("possible_truncation"):
        return {"status": "truncated", "text": "A leitura automática pode estar incompleta.",
                "message": "A geração atingiu seu limite. Confira o recorte antes de usar a sugestão."}
    return {"status": "candidate", "text": prediction.get("text_raw", ""),
            "message": "Sugestão automática; confira cada palavra na imagem."}


def present_predictions(predictions, lines, config):
    by_id = {line["line_id"]: line for line in lines}
    return [dict(prediction, presentation=present_prediction(
        prediction, by_id.get(prediction["line_id"]), config)) for prediction in predictions]
