"""Prepare the five-line Traslado sample; repeat preserves existing review."""
import argparse
import json
from pathlib import Path

from paleographia.preparation import prepare_sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", default="configs/traslado_269r_source.json")
    args = parser.parse_args()
    root = Path.cwd()
    spec = json.loads(Path(args.spec).read_bytes())
    comparison = json.loads((root / spec["comparison_source"]).read_bytes())
    print(json.dumps(prepare_sample(root, spec, comparison), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
