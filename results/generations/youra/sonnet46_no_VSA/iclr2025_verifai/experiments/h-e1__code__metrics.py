"""Metrics computation for contract-strength gap experiment."""
import json
import numpy as np
from pathlib import Path


def compute_per_task_gap(pbt_results: list[dict]) -> dict[str, float]:
    """Compute per-task contract-strength gap.

    Gap = fraction of test-passing programs that fail ≥1 contract (violated=True).
    """
    task_violated: dict[str, list[bool]] = {}
    for r in pbt_results:
        task_id = r["task_id"]
        if r.get("error") and r.get("n_total", 0) == 0:
            continue  # skip execution errors
        task_violated.setdefault(task_id, []).append(r["violated"])

    per_task_gap = {}
    for task_id, violated_list in task_violated.items():
        if violated_list:
            per_task_gap[task_id] = sum(violated_list) / len(violated_list)

    return per_task_gap


def bootstrap_ci(
    gaps: list[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> tuple[float, float]:
    """Compute 95% bootstrap CI for mean gap."""
    if len(gaps) == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    arr = np.array(gaps)
    boot_means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    return ci_lower, ci_upper


def aggregate_metrics(
    all_results: list[dict],
    z3_tractable_ids: set[str],
    n_bootstrap: int = 10_000,
    gate_threshold: float = 0.01,
) -> dict:
    """Compute aggregate contract-strength gap metrics."""
    per_task_gap = compute_per_task_gap(all_results)

    if not per_task_gap:
        return {
            "mean_gap": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "n_tasks": 0,
            "n_programs": 0,
            "gate_passed": False,
            "tractable_gap": None,
            "n_quarantined": 0,
        }

    gaps = list(per_task_gap.values())
    mean_gap = float(np.mean(gaps))
    ci_lower, ci_upper = bootstrap_ci(gaps, n_bootstrap=n_bootstrap)
    gate_passed = ci_lower > gate_threshold

    # Tractable subset gap
    tractable_gaps = [v for k, v in per_task_gap.items() if k in z3_tractable_ids]
    tractable_gap = float(np.mean(tractable_gaps)) if tractable_gaps else None

    # Count programs
    n_programs = sum(
        1 for r in all_results
        if not (r.get("error") and r.get("n_total", 0) == 0)
    )

    # Count quarantined (tasks with no results)
    n_quarantined = 0  # tracked by oracle_checker

    return {
        "mean_gap": mean_gap,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_tasks": len(per_task_gap),
        "n_programs": n_programs,
        "gate_passed": gate_passed,
        "tractable_gap": tractable_gap,
        "n_quarantined": n_quarantined,
    }


def save_results_csv(
    all_results: list[dict],
    out_path: str,
) -> None:
    """Save per-result CSV for analysis."""
    import csv
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    if not all_results:
        return
    fields = ["task_id", "model", "violated", "n_failures", "n_total", "gap", "error"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_results)
