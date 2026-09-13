import json
import os
import numpy as np
from pathlib import Path
from config import H_M3Config


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

    return values


def extract_log_steps(log_history: list) -> list:
    """Extract step indices from log_history entries that have frac_reward_zero_std."""
    return [
        int(e["step"])
        for e in log_history
        if "step" in e and "frac_reward_zero_std" in e
    ]


def compute_gate_metrics(
    frac_var: list,
    frac_rnd: list,
    checkpoints: list = None,
) -> dict:
    """
    Compute mean frac_zero_std at each checkpoint (cumulative mean, kept from H-M2 for Fig 1).
    """
    if checkpoints is None:
        checkpoints = [10, 20, 50]

    results = {}
    for N in checkpoints:
        mean_var = float(np.mean(frac_var[0:N]))
        mean_rnd = float(np.mean(frac_rnd[0:N]))
        gap = mean_rnd - mean_var
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


def verify_warm_start_succeeded(
    log_history_var50: list,
    log_history_rnd50: list,
) -> tuple:
    """
    Check that warm-start config produced nonzero rewards in at least one condition.
    Returns (warm_start_ok, stats) where stats = {max_reward_var50, max_reward_rnd50}.
    """
    def _extract_rewards(log_history):
        return [
            e.get("rewards/reward_fn/mean", 0.0)
            for e in log_history
            if "rewards/reward_fn/mean" in e
        ]

    var_rewards = _extract_rewards(log_history_var50)
    rnd_rewards = _extract_rewards(log_history_rnd50)

    max_var = max(var_rewards, default=0.0)
    max_rnd = max(rnd_rewards, default=0.0)
    warm_start_ok = any(r > 0.0 for r in var_rewards + rnd_rewards)

    return warm_start_ok, {
        "max_reward_var50": max_var,
        "max_reward_rnd50": max_rnd,
        "warm_start_ok": warm_start_ok,
    }


def compute_gap_trajectory(
    frac_var: list,
    frac_rnd: list,
    log_steps: list,
) -> tuple:
    """
    Compute per-step gap and extract checkpoint values.
    Returns (gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention).
    gap_by_step: dict[int, float] = {step: frac_rnd - frac_var}
    gap_retention: gap_at_50 / gap_at_10 if gap_at_10 > 0 else 0.0
    """
    assert len(frac_var) == len(frac_rnd) == len(log_steps), (
        f"Lengths must match: frac_var={len(frac_var)}, "
        f"frac_rnd={len(frac_rnd)}, log_steps={len(log_steps)}"
    )

    gap_by_step = {
        step: rnd - var
        for step, var, rnd in zip(log_steps, frac_var, frac_rnd)
    }

    gap_at_10 = gap_by_step.get(10, 0.0)
    gap_at_20 = gap_by_step.get(20, 0.0)
    gap_at_50 = gap_by_step.get(50, 0.0)

    if gap_at_10 > 0:
        gap_retention = gap_at_50 / gap_at_10
    else:
        gap_retention = 0.0

    return gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention


def save_results(
    cfg: H_M3Config,
    warm_start_ok: bool,
    gap_by_step: dict,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    frac_var: list,
    frac_rnd: list,
    variance_50_ids: list,
    random_50_ids: list,
    gate_passed: bool,
    p1_pass: bool,
    p2_pass: bool,
    max_rewards: dict,
) -> None:
    """Write gate_results.json per FR-12 schema."""
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    # Convert int keys to str for JSON serialization
    gap_by_step_str = {str(k): v for k, v in gap_by_step.items()}

    output = {
        "hypothesis": "H-M3",
        "warm_start_succeeded": warm_start_ok,
        "gate_passed": gate_passed,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "gap_by_checkpoint": {
            "10": gap_at_10,
            "20": gap_at_20,
            "50": gap_at_50,
        },
        "gap_retention": gap_retention,
        "gap_by_step": gap_by_step_str,
        "max_rewards": max_rewards,
        "frac_zero_std_variance50": frac_var,
        "frac_zero_std_random50": frac_rnd,
        "variance_50_ids": variance_50_ids,
        "random_50_ids": random_50_ids,
        "config": {
            "max_steps": cfg.max_steps,
            "learning_rate": cfg.learning_rate,
            "max_completion_length": cfg.max_completion_length,
            "num_generations": cfg.num_generations,
            "seed": cfg.seed,
        },
    }

    out_path = os.path.join(cfg.results_dir, "gate_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[analyze] Results saved: {out_path}")
