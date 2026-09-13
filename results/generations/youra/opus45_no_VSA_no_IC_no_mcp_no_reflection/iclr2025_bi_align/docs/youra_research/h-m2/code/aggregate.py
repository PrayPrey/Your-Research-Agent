"""H-M2 Aggregate: Gate computation and results table."""
import json
from pathlib import Path

import pandas as pd

from config import VARIANTS


def compute_gate(eval_results: dict[str, dict]) -> dict:
    """Compute gate: any Ti > max(B1,B2,B3) + 0.02."""
    baselines = ["B1", "B2", "B3"]
    treatments = ["T1", "T2", "T3", "T4"]

    baseline_scores = []
    for b in baselines:
        if b in eval_results and "strict_accuracy" in eval_results[b]:
            baseline_scores.append(eval_results[b]["strict_accuracy"])

    if not baseline_scores:
        return {
            "baseline_max": None,
            "best_ti": None,
            "gate_passed": False,
            "delta_pp": None,
            "error": "No baseline scores available",
        }

    baseline_max = max(baseline_scores)

    ti_scores = {}
    for t in treatments:
        if t in eval_results and "strict_accuracy" in eval_results[t]:
            ti_scores[t] = eval_results[t]["strict_accuracy"]

    if not ti_scores:
        return {
            "baseline_max": baseline_max,
            "best_ti": None,
            "gate_passed": False,
            "delta_pp": None,
            "error": "No treatment scores available",
        }

    best_ti = max(ti_scores, key=ti_scores.get)
    best_ti_score = ti_scores[best_ti]
    delta_pp = best_ti_score - baseline_max

    return {
        "baseline_max": baseline_max,
        "best_ti": best_ti,
        "best_ti_score": best_ti_score,
        "gate_passed": delta_pp >= 0.02,
        "delta_pp": delta_pp,
        "all_ti_scores": ti_scores,
        "all_baseline_scores": {b: eval_results[b].get("strict_accuracy") for b in baselines if b in eval_results},
    }


def results_table(eval_results: dict[str, dict]) -> pd.DataFrame:
    """Create summary DataFrame for all variants."""
    variant_lookup = {v.name: v for v in VARIANTS}

    rows = []
    for name in ["B1", "B2", "B3", "T1", "T2", "T3", "T4"]:
        if name not in eval_results:
            continue

        result = eval_results[name]
        variant = variant_lookup.get(name)

        rows.append({
            "variant": name,
            "strict_accuracy": result.get("strict_accuracy"),
            "loose_accuracy": result.get("loose_accuracy"),
            "alpha": variant.alpha if variant else None,
            "beta": variant.beta if variant else None,
            "reward_mode": variant.reward_mode if variant else None,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    eval_path = Path(__file__).parent / "outputs" / "eval_results.json"
    with open(eval_path) as f:
        eval_results = json.load(f)

    gate = compute_gate(eval_results)
    print("Gate Result:")
    print(json.dumps(gate, indent=2))

    df = results_table(eval_results)
    print("\nResults Table:")
    print(df.to_string(index=False))

    # Save
    output_dir = Path(__file__).parent / "outputs"
    df.to_csv(output_dir / "results.csv", index=False)

    with open(output_dir / "gate_result.json", "w") as f:
        json.dump(gate, f, indent=2)
