import json
import os
import numpy as np
from pathlib import Path
from config import H_M2Config


def extract_frac_zero_std(log_history: list) -> list:
    """
    Extract frac_reward_zero_std values from TRL log_history.
    Raises ValueError if metric not found in any log entry.
    """
    values = [
        entry["frac_reward_zero_std"]
        for entry in log_history
        if "frac_reward_zero_std" in entry
    ]

    if not values:
        available = list(log_history[0].keys()) if log_history else []
        raise ValueError(
            f"frac_reward_zero_std not found in log_history. "
            f"Check TRL >= 0.15.0. Available keys: {available}"
        )

    if len(values) < 50:
        print(f"[analyze] WARNING: Expected 50 steps, got {len(values)} frac_zero_std entries")

    return values


def compute_gate_metrics(
    frac_var: list,
    frac_rnd: list,
    checkpoints: list = None,
) -> dict:
    """
    Compute mean frac_zero_std at each checkpoint, gate booleans, secondary gap.
    frac_var[i] = step i+1 value (0-indexed, steps 1..N use slice [0:N]).
    """
    if checkpoints is None:
        checkpoints = [10, 20, 50]

    results = {}
    for N in checkpoints:
        mean_var = float(np.mean(frac_var[0:N]))
        mean_rnd = float(np.mean(frac_rnd[0:N]))
        gap = mean_rnd - mean_var  # positive = variance-50 wins
        results[f"checkpoint_{N}"] = {
            "mean_frac_var": mean_var,
            "mean_frac_rnd": mean_rnd,
            "gap_pp": gap,
            "gate_pass": bool(mean_var < mean_rnd),
        }

    results["primary_gate_pass"] = all(
        results[f"checkpoint_{N}"]["gate_pass"] for N in checkpoints
    )
    results["secondary_gate_pass"] = bool(
        results["checkpoint_10"]["gap_pp"] >= 0.05
    )
    return results


def save_results(
    cfg: H_M2Config,
    gate_metrics: dict,
    frac_var: list,
    frac_rnd: list,
    variance_50_ids: list,
    random_50_ids: list,
) -> None:
    """Write gate_results.json per C-5-2 schema."""
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    output = {
        "hypothesis": "H-M2",
        **gate_metrics,
        "frac_zero_std_variance50": frac_var,
        "frac_zero_std_random50": frac_rnd,
        "variance_50_ids": variance_50_ids,
        "random_50_ids": random_50_ids,
    }

    out_path = os.path.join(cfg.results_dir, "gate_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[analyze] Results saved: {out_path}")
