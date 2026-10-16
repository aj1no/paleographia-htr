"""Verify hashes, original receipts, exact pixels, and recompute saved predictions."""
import argparse
import json
from pathlib import Path

from paleographia.frozen_experiment import audit_bundle, restore_support


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default="docs/experimentos/traslado_269r_20261016")
    parser.add_argument("--output", required=True, help="New output directory; never overwrite historical evaluations")
    parser.add_argument("--restore-support", action="store_true", help="Recover missing edition PDF offline; refuse divergent files")
    args = parser.parse_args()
    root = Path.cwd()
    if args.restore_support:
        restore_support(root, args.bundle)
    report = audit_bundle(root, args.bundle, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
