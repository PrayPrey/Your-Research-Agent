"""Persist H-M2 measurement records."""
import json
from pathlib import Path


def write_records(records: list[dict], path: str = "results/h-m2/results.jsonl") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(records)} records to {path}")


def write_summary(analysis: dict, path: str = "results/h-m2/summary.json") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Wrote summary to {path}")
