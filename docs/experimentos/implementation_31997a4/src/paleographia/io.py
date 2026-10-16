import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path, root):
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def safe_path(root, value):
    from pathlib import PureWindowsPath
    original = value.as_posix() if isinstance(value, Path) else str(value)
    value = Path(value)
    if value.is_absolute() or PureWindowsPath(original).drive or ".." in value.parts or "\\" in original:
        raise ValueError("Caminho deve ser relativo, sem travessia e usar /.")
    resolved = (Path(root) / value).resolve()
    if not resolved.is_relative_to(Path(root).resolve()):
        raise ValueError("Caminho fora do projeto.")
    return resolved


def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path, rows):
    atomic_write(path, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def deterministic_json_bytes(value):
    """Snapshot contract: UTF-8, sorted keys, indent 2, finite JSON, one final LF."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def same_json_content(left, right):
    """Semantic comparison is deliberately separate from byte integrity."""
    return json.loads(left) == json.loads(right)


def verify_digest(path, expected):
    return sha256(path) == expected


def write_snapshot(directory, value):
    """Create a content-addressed immutable snapshot; never rewrite an existing one."""
    content = deterministic_json_bytes(value)
    digest = hashlib.sha256(content).hexdigest()
    path = Path(directory) / ("snapshot_" + digest + ".json")
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("Snapshot existente divergente; não foi sobrescrito.")
    else:
        atomic_write(path, content.decode("utf-8"))
    if not verify_digest(path, digest):
        raise ValueError("Bytes gravados não correspondem ao digest do snapshot.")
    return path


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".pending-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
