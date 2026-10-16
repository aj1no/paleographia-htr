"""All worker outputs below are synthetic protocol fixtures, never HTR evidence."""
import copy
import hashlib
import io
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from paleographia.api import create_app
from paleographia.backends import create_recognizer
from paleographia.kraken_recognition import KrakenRecognizer
from paleographia.presentation import present_prediction, review_policy
from paleographia.recognition import ModelUnavailable, TrOCRRecognizer, prepare_weights
from paleographia.io import sha256


def test_legacy_cli_recognition_and_preparation_exit_without_inference(corpus, monkeypatch, capsys):
    from paleographia.__main__ import main
    from paleographia.io import write_jsonl
    root, _, _, lines = corpus
    write_jsonl(root/'lines.jsonl', lines)
    (root/'old.toml').write_text('[recognition]\nmodel="models/trocr-small-handwritten"\n',encoding='utf8')
    monkeypatch.chdir(root)
    assert main(['recognize','--lines','lines.jsonl','--config','old.toml','--output','predictions.jsonl'])==2
    assert main(['prepare-weights','--config','old.toml','--output-dir','weights'])==2
    assert 'TrOCR desativado' in capsys.readouterr().err
    assert not (root/'predictions.jsonl').exists() and not (root/'weights').exists()


@pytest.mark.parametrize('backend',['disabled','kraken_ppocrv6'])
def test_training_never_loads_rejected_or_inference_only_backend(corpus, monkeypatch, backend):
    from paleographia import training
    root, config, pages, rows = corpus
    config=copy.deepcopy(config)
    config['recognition']={'backend':backend,'model':'models/unavailable'}
    monkeypatch.setattr(training,'validate',lambda *a,**k:{'valid':True})
    monkeypatch.setattr(KrakenRecognizer,'load',lambda *a:pytest.fail('Treino não pode carregar worker de inferência'))
    result=training.training_run(rows,pages,config,root/('training_'+backend),root,execute=True)
    assert result['status']=='failed' and result.get('reason')


def test_legacy_config_and_direct_entrypoints_cannot_execute(tmp_path):
    for config in ({}, {"recognition": {"model": "models/trocr-small-handwritten"}},
                   {"recognition": {"backend": "trocr", "model": "old"}},
                   {"recognition": {"backend": "kraken_ppocrv6", "model": "microsoft/trocr-small-handwritten"}}):
        recognizer = create_recognizer(config, tmp_path)
        assert recognizer.status()["state"] == "disabled"
        with pytest.raises(ModelUnavailable, match="desativado"):
            recognizer.load()
    with pytest.raises(ModelUnavailable, match="desativado"):
        TrOCRRecognizer({}).recognize(Image.new("RGB", (10, 10)))
    with pytest.raises(ModelUnavailable, match="desativado"):
        prepare_weights({"recognition": {"model": "microsoft/trocr-small-handwritten"}}, tmp_path/"weights")
    assert not (tmp_path/"weights").exists()


def test_disabled_and_missing_worker_preserve_manual_review(corpus):
    root, config, pages, lines = corpus
    for settings, state in (({"backend": "disabled"}, "disabled"),
                            ({"backend": "kraken_ppocrv6", "model": "models/missing", "sha256": "0"*64}, "not_loaded")):
        config = copy.deepcopy(config)
        config["recognition"] = settings
        config["paths"]["workspace"] += "_"+state
        app = create_app(root, config)
        app.state.service.import_catalog(pages, lines)
        before = copy.deepcopy(app.state.service.state())
        with TestClient(app) as client:
            assert client.get("/health").json()["recognition"]["state"] == state
            response = client.post(f"/api/pages/{pages[0]['page_id']}/recognize")
            assert response.status_code == 503 and response.json()["review_available"]
            assert app.state.service.state() == before
            assert client.patch(f"/api/lines/{lines[0]['line_id']}", json={"revision": before["revision"],
                "changes": {"text_diplomatic": "Rascunho humano preservado"}}).status_code == 200
            assert client.get("/").status_code == 200
            if state == "not_loaded":
                assert client.get("/health").json()["recognition"]["state"] == "unavailable"


def test_worker_protocol_reuses_model_and_receives_only_pixels(tmp_path, monkeypatch):
    weights = tmp_path/"medium.safetensors"
    weights.write_bytes(b"TEST MODEL ONLY")
    digest = sha256(weights)
    settings = {"backend": "kraken_ppocrv6", "model": weights.name, "sha256": digest}
    recognizer = KrakenRecognizer(settings, tmp_path)
    processes = []
    class FakeProcess:
        def __init__(self, command, **kwargs):
            self.stdin, self.stdout, self.stderr = io.StringIO(), io.StringIO(), io.StringIO()
            self.code = None
            processes.append(command)
        def poll(self):
            return self.code
        def wait(self, timeout):
            self.code = 0
        def terminate(self):
            self.code = -1
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(stdout="sha256:test-image\n"))
    monkeypatch.setattr(subprocess, "Popen", FakeProcess)
    def receive():
        if recognizer.identity is None:
            return {"ready": True, "identity": {"backend": "kraken_ppocrv6", "sha256": digest}, "load_seconds": .01}
        request = json.loads(recognizer.process.stdin.getvalue().splitlines()[-1])
        assert set(request) == {"request_id", "image_png", "pixel_sha256"}
        return {"ok": True, "request_id": request["request_id"], "text_raw": "SAÍDA SINTÉTICA",
                "preprocessing": {"pixel_sha256": request["pixel_sha256"]}}
    monkeypatch.setattr(recognizer, "_receive", receive)
    try:
        assert recognizer.status()["state"] == "not_loaded"
        for _ in range(2):
            result = recognizer.recognize(Image.new("RGB", (40, 20)))
            assert result["text_raw"] == "SAÍDA SINTÉTICA"
            assert result["model"]["sha256"] == digest
        assert len(processes) == 1
        assert recognizer.status()["state"] == "ready"
        assert "--network" in processes[0] and "none" in processes[0]
        assert str(tmp_path) not in processes[0]  # no mount of entire project/gabarito
        mounts = [arg for arg in processes[0] if arg.startswith("type=bind")]
        assert len(mounts) == 2 and all("readonly" in arg for arg in mounts)
    finally:
        recognizer.close()


def test_worker_hash_and_transport_failure_are_explicit(tmp_path):
    weights = tmp_path/"model"
    weights.write_bytes(b"bad")
    recognizer = KrakenRecognizer({"model": "model", "sha256": "0"*64}, tmp_path)
    with pytest.raises(ModelUnavailable, match="SHA-256"):
        recognizer.load()
    recognizer.messages.put("not JSON")
    with pytest.raises(ModelUnavailable, match="Resposta inválida"):
        recognizer._receive()
    recognizer.messages.put(None)
    with pytest.raises(ModelUnavailable, match="encerrou"):
        recognizer._receive()


def test_presentation_release_is_bound_to_evaluated_backend_weights_and_worker(corpus):
    _, config, _, lines = corpus
    config = copy.deepcopy(config)
    worker_sha = sha256(Path(__file__).parents[1]/"src/paleographia/kraken_recognition_worker.py")
    config["recognition"] = {"backend": "kraken_ppocrv6", "sha256": "a"*64, "docker_image_id": "sha256:tested"}
    config["presentation"] = {"automatic_transcription_enabled": True, "evaluated_backend": "kraken_ppocrv6",
        "evaluated_model_sha256": "a"*64, "evaluated_docker_image_id": "sha256:tested", "evaluated_worker_sha256": worker_sha}
    prediction = {"status": "ok", "bbox_xyxy": lines[0]["bbox_xyxy"], "text_raw": "TEST ONLY",
                  "model": {"backend": "kraken_ppocrv6", "sha256": "a"*64, "docker_image_id": "sha256:tested", "worker_sha256": worker_sha}}
    assert review_policy(config)["automatic_transcription_enabled"]
    assert present_prediction(prediction, lines[0], config)["status"] == "candidate"
    prediction["model"] = {"id": "microsoft/trocr-small-handwritten"}
    assert present_prediction(prediction, lines[0], config)["status"] == "historical_model"
    config["recognition"]["sha256"] = "b"*64
    assert not review_policy(config)["automatic_transcription_enabled"]
