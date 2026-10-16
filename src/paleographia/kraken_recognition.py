"""Lazy, serialized, persistent Kraken worker in a separate Linux Docker runtime."""
import base64
import collections
import hashlib
import io
import json
import queue
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path

from .io import now, safe_path, sha256
from .recognition import ModelUnavailable

MODEL_URL = "https://zenodo.org/records/21788410/files/medium.safetensors?download=1"
MODEL_MD5 = "e3411a453ce3b9e9efae3f8631d85762"
MODEL_SIZE = 63779644
MODEL_SHA256 = "15313b51ace64cbfa81f8f6ef25ad64f04e5a6fb7f7823e67b107527bc081ac9"


def download_weights(output):
    """Explicit download into a new directory; size + Zenodo MD5 + SHA256 recorded."""
    import urllib.request
    from .io import write_json
    output = Path(output)
    if output.exists():
        raise ValueError("Pesos exigem diretório novo.")
    content = urllib.request.urlopen(MODEL_URL, timeout=120).read()
    if (len(content) != MODEL_SIZE or hashlib.md5(content).hexdigest() != MODEL_MD5
            or hashlib.sha256(content).hexdigest() != MODEL_SHA256):
        raise ValueError("Download dos pesos divergente; nada foi gravado.")
    output.mkdir(parents=True)
    with (output/"medium.safetensors").open("xb") as stream:
        stream.write(content)
    record = {"url": MODEL_URL, "record": "https://zenodo.org/records/21788410", "version": "v1",
              "size": len(content), "md5": MODEL_MD5, "sha256": hashlib.sha256(content).hexdigest()}
    write_json(output/"provenance.json", record)
    return record


class KrakenRecognizer:
    def __init__(self, settings, root):
        self.settings, self.root = settings, Path(root)
        self.lock = threading.RLock()
        self.process = None
        self.identity = None
        self.error = None
        self.load_seconds = 0.0
        self.startup_seconds = 0.0
        self.messages = queue.Queue()
        self.stderr = collections.deque(maxlen=100)
        self.container_name = "paleographia-rec-"+uuid.uuid4().hex[:16]

    def status(self):
        alive = self.process is not None and self.process.poll() is None
        return {"state": "ready" if alive and self.identity else "unavailable" if self.error or self.identity else "not_loaded",
                "backend": "kraken_ppocrv6", "configured_model": self.settings.get("model"),
                "loaded_model": self.identity, "device": "cpu", "precision": "float32",
                "load_seconds": self.load_seconds, "startup_seconds": self.startup_seconds,
                "error": self.error}

    def _pump(self, stream, output):
        try:
            for line in stream:
                if output:
                    self.messages.put(line)
                else:
                    self.stderr.append(line.rstrip())
        except (OSError, ValueError):
            pass  # Stream was closed during shutdown.
        finally:
            if output:
                self.messages.put(None)

    def _receive(self):
        try:
            line = self.messages.get(timeout=self.settings.get("timeout_seconds", 180))
        except queue.Empty:
            raise ModelUnavailable("Tempo limite do worker Kraken excedido.") from None
        if line is None:
            raise ModelUnavailable("Worker Kraken encerrou: "+"\n".join(self.stderr)[-2500:])
        try:
            return json.loads(line)
        except json.JSONDecodeError as exc:
            raise ModelUnavailable("Resposta inválida do worker Kraken.") from exc

    def load(self):
        with self.lock:
            if self.status()["state"] == "ready":
                return
            self.close()
            self.identity = None
            started = time.perf_counter()
            try:
                if self.settings.get("device", "cpu") != "cpu" or self.settings.get("precision", "float32") != "float32":
                    raise ValueError("Este worker exige CPU/float32.")
                weights = safe_path(self.root, self.settings["model"])
                expected = self.settings["sha256"]
                if not re.fullmatch("[a-f0-9]{64}", expected) or sha256(weights) != expected:
                    raise ValueError("Pesos ausentes ou hash SHA-256 divergente.")
                image = self.settings.get("docker_image", "paleographia-kraken:7.1.0-cpu")
                if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./:@-]*", image):
                    raise ValueError("Identificador de imagem Docker inválido.")
                inspection = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", image],
                                            capture_output=True, text=True, encoding="utf-8", timeout=20, check=True)
                image_id = inspection.stdout.strip()
                pinned = self.settings.get("docker_image_id")
                if pinned and pinned != image_id:
                    raise ValueError("Imagem Docker diverge da configuração avaliada.")
                worker = Path(__file__).with_name("kraken_recognition_worker.py").resolve()
                if any("," in str(p) for p in (weights, worker)):
                    raise ValueError("O mount Docker requer caminhos sem vírgula.")
                command = ["docker", "run", "--rm", "-i", "--name", self.container_name,
                           "--network", "none", "--cpus", "2", "--memory", "4g", "--read-only",
                           "--tmpfs", "/tmp:rw,size=256m", "--env", "HOME=/tmp",
                           "--mount", f"type=bind,source={weights},target=/model.safetensors,readonly",
                           "--mount", f"type=bind,source={worker},target=/worker.py,readonly",
                           image_id, "python", "-u", "/worker.py", "--weights", "/model.safetensors", "--sha256", expected]
                self.messages = queue.Queue()
                self.stderr.clear()
                self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1)
                for stream, output in ((self.process.stdout, True), (self.process.stderr, False)):
                    threading.Thread(target=self._pump, args=(stream, output), daemon=True).start()
                ready = self._receive()
                if not ready.get("ready"):
                    raise ModelUnavailable(ready.get("error", "Worker não ficou pronto."))
                if ready["identity"].get("sha256") != expected or ready["identity"].get("backend") != "kraken_ppocrv6":
                    raise ModelUnavailable("Identidade inesperada no worker.")
                self.identity = dict(ready["identity"], docker_image_id=image_id,
                                     worker_sha256=sha256(worker))
                self.load_seconds = ready["load_seconds"]
                self.error = None
            except Exception as exc:
                self.error = f"Kraken indisponível: {exc}. Confira Docker Linux, imagem e pesos; a revisão manual continua disponível."
                self.close()
                raise ModelUnavailable(self.error) from exc
            finally:
                self.startup_seconds = time.perf_counter()-started

    def recognize(self, image):
        with self.lock:
            self.load()
            converted = image.convert("RGB")
            pixel_sha = hashlib.sha256(converted.tobytes()).hexdigest()
            buffer = io.BytesIO()
            converted.save(buffer, format="PNG")
            request_id = uuid.uuid4().hex
            try:
                self.process.stdin.write(json.dumps({"request_id": request_id, "pixel_sha256": pixel_sha,
                    "image_png": base64.b64encode(buffer.getvalue()).decode("ascii")})+"\n")
                self.process.stdin.flush()
                result = self._receive()
                if result.get("request_id") != request_id:
                    raise ModelUnavailable("Resposta fora da ordem no worker.")
                if not result.get("ok"):
                    raise RuntimeError(result.get("error", "Falha de reconhecimento."))
                if result["preprocessing"]["pixel_sha256"] != pixel_sha:
                    raise ModelUnavailable("Pixels recebidos pelo worker divergentes.")
                if not isinstance(result.get("text_raw"), str):
                    raise ModelUnavailable("Worker não retornou texto bruto válido.")
            except (ModelUnavailable, BrokenPipeError, OSError, KeyError, TypeError) as exc:
                self.error = str(exc)
                self.close()
                raise ModelUnavailable(self.error) from exc
            return {k: v for k, v in dict(result, model=self.identity, device="cpu", precision="float32",
                    possible_truncation=False, generation_limit_reached=False, seed=1831,
                    created_at=now(), decoding="Kraken greedy CTC; no correction").items()
                    if k not in {"request_id", "ok"}}

    def close(self):
        with self.lock:
            process, self.process = self.process, None
            if process is not None:
                try:
                    process.stdin.close()
                    process.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        subprocess.run(["docker", "rm", "-f", self.container_name], capture_output=True, timeout=15)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                    finally:
                        process.terminate()
                finally:
                    for stream in (process.stdout, process.stderr):
                        stream.close()
