"""Result persistence for H-M3."""
import json
import os
from dataclasses import asdict


def write_records(results: list, path: str) -> None:
    """Write per-(problem, category) repair records as JSONL."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in results:
            if hasattr(r, "__dataclass_fields__"):
                rec = asdict(r)
            else:
                rec = r
            f.write(json.dumps(rec) + "\n")
    print(f"Wrote {len(results)} records to {path}")


def write_summary(analysis: dict, path: str) -> None:
    """Write analysis summary as JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_clean(x) for x in obj]
        if hasattr(obj, "item"):  # numpy scalar
            return obj.item()
        return obj

    with open(path, "w") as f:
        json.dump(_clean(analysis), f, indent=2)
    print(f"Wrote summary to {path}")
