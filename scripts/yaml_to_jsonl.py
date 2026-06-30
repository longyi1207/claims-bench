#!/usr/bin/env python3
"""Export revelation YAML scenarios to JSONL v2 format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/revelation"))
    parser.add_argument("--output", type=Path, default=Path("data/v2_revelation.jsonl"))
    parser.add_argument("--exclude", default="_template.yaml")
    args = parser.parse_args()

    if yaml is None:
        raise SystemExit("Install PyYAML: pip install pyyaml")

    items = []
    for path in sorted(args.input_dir.glob("*.yaml")):
        if path.name == args.exclude:
            continue
        with path.open() as f:
            item = yaml.safe_load(f)
        if item:
            items.append(item)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(items)} items to {args.output}")


if __name__ == "__main__":
    main()
