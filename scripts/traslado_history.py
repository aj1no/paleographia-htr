"""Verify legacy Git blobs separately from checkout bytes; create future LF snapshots."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from paleographia.io import deterministic_json_bytes, same_json_content, sha256, write_json, write_snapshot

BASE = "632e8ff71eef2913f003cece810f834aa1ca4382"
DIRECTORY = "docs/revisao_humana/traslado_269r"


def git_blob(root, revision, path):
    return subprocess.run(["git", "show", f"{revision}:{path}"], cwd=root,
                          check=True, capture_output=True).stdout


def record_integrity(root, output):
    root, output = Path(root), Path(output)
    paths = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASE,
                            DIRECTORY + "/revisions/"], cwd=root, check=True,
                           capture_output=True, text=True).stdout.splitlines()
    rows = []
    for path in paths:
        if not Path(path).name.startswith("comparacao_"):
            continue
        blob = git_blob(root, BASE, path)
        legacy_bytes = blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        legacy_digest = hashlib.sha256(legacy_bytes).hexdigest()
        if not Path(path).stem.endswith(legacy_digest[:16]):
            raise ValueError("Identificador legado não corresponde à serialização CRLF declarada.")
        rows.append({"path": path, "published_sha256": hashlib.sha256(blob).hexdigest(),
                     "published_bytes": len(blob), "legacy_crlf_sha256": legacy_digest})
    result = {"schema_version": 1, "git_revision": BASE,
              "published_digest_basis": "Exact Git blob bytes read with git show, not checkout bytes.",
              "legacy_identifier_basis": "First 16 SHA-256 hex characters of UTF-8 JSON serialized with CRLF. Names and blobs preserved.",
              "new_snapshot_contract": "UTF-8; sorted keys; ensure_ascii=False; indent=2; allow_nan=False; LF; exactly one final LF; full SHA-256 of written bytes.",
              "snapshots": rows}
    if output.exists():
        if json.loads(output.read_bytes()) != result:
            raise ValueError("Registro de integridade existente divergente; não foi sobrescrito.")
    else:
        write_json(output, result)
    return result


def verify_history(root, record):
    root = Path(root)
    data = json.loads(Path(record).read_bytes())
    rows = []
    for entry in data["snapshots"]:
        blob = git_blob(root, data["git_revision"], entry["path"])
        local = (root / entry["path"]).read_bytes()
        if hashlib.sha256(blob).hexdigest() != entry["published_sha256"]:
            raise ValueError("Digest publicado divergente.")
        current = git_blob(root, "HEAD", entry["path"])
        if current != blob:
            raise ValueError("Blob histórico foi alterado em HEAD.")
        if local != blob and local != blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"):
            raise ValueError("Cópia local alterada além de conversão LF/CRLF.")
        if not same_json_content(local, blob):
            raise ValueError("Conteúdo semântico histórico divergente.")
        rows.append({"path": entry["path"], "published_verified": True,
                     "checkout_sha256": sha256(root / entry["path"]),
                     "checkout_matches_blob": local == blob, "semantic_match": True})
    new = []
    for path in sorted((root / DIRECTORY / "revisions").glob("snapshot_*.json")):
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if path.name != "snapshot_" + digest + ".json" or content != deterministic_json_bytes(json.loads(content)):
            raise ValueError("Novo snapshot não segue o contrato determinístico.")
        new.append({"path": path.relative_to(root).as_posix(), "sha256": digest})
    return {"valid": True, "snapshots": rows, "new_snapshots": new}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["record", "verify", "snapshot"])
    parser.add_argument("--source", default=DIRECTORY + "/comparacao.json")
    args = parser.parse_args()
    root = Path.cwd()
    record = root / DIRECTORY / "integridade.json"
    if args.action == "record":
        result = record_integrity(root, record)
        print(json.dumps({"snapshots": len(result["snapshots"]), "record": str(record)}))
    elif args.action == "verify":
        print(json.dumps(verify_history(root, record), ensure_ascii=False, indent=2))
    else:
        path = write_snapshot(root / DIRECTORY / "revisions", json.loads(Path(args.source).read_bytes()))
        print(json.dumps({"snapshot": str(path), "sha256": sha256(path)}))


if __name__ == "__main__":
    main()
