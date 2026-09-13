"""
H-M4: Results Aggregator — merges H-M3 token-matched and H-M4 step-matched differentials.
"""

import json
from pathlib import Path


def load_hm3_differentials(hm3_results_dir: str) -> dict:
    """Load token-count-matched differentials from H-M3 experiment_results.json."""
    p = Path(hm3_results_dir)
    # H-M3 stores results in experiment_results.json at the hypothesis root
    candidates = [
        p / "experiment_results.json",
        p.parent / "experiment_results.json",
    ]
    for c in candidates:
        if c.exists():
            with open(c) as f:
                d = json.load(f)
            diffs = d.get("accuracy_differentials")
            if diffs:
                print(f"Loaded H-M3 token-matched differentials from {c}")
                return diffs
    raise FileNotFoundError(f"H-M3 accuracy_differentials not found in {hm3_results_dir}")


def load_hm4_step_matched(hm4_results_dir: str) -> dict:
    """Load step-matched differentials from H-M4 results."""
    p = Path(hm4_results_dir) / "step_matched_raw.json"
    with open(p) as f:
        d = json.load(f)
    diffs = d.get("differentials")
    if not diffs:
        raise ValueError(f"No 'differentials' key in {p}")
    print(f"Loaded H-M4 step-matched differentials from {p}")
    return diffs


def aggregate(token_matched: dict, step_matched: dict) -> dict:
    """Merge both conditions into unified structure."""
    return {
        "token_matched": token_matched,
        "step_matched": step_matched,
    }


def save_aggregated(aggregated: dict, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(aggregated, f, indent=2)
    print(f"Saved aggregated differentials: {out_path}")


if __name__ == "__main__":
    from pathlib import Path
    base = Path(__file__).parent.parent.parent

    hm3_dir = base / "h-m3"
    hm4_results = Path(__file__).parent.parent / "results"

    token_matched = load_hm3_differentials(str(hm3_dir))
    step_matched = load_hm4_step_matched(str(hm4_results))

    aggregated = aggregate(token_matched, step_matched)
    out = hm4_results / "aggregated_differentials.json"
    save_aggregated(aggregated, str(out))
    print("Aggregation complete.")
