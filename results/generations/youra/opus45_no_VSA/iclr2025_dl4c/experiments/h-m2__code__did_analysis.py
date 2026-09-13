"""DiD statistical analysis for H-M2 experiment."""
import numpy as np
from collections import defaultdict


def pass_rate(results: list[dict], model_name: str, condition: str) -> float:
    """Mean refined_pass for given model/condition."""
    subset = [r for r in results if r["model"] == model_name and r["condition"] == condition]
    if not subset:
        return 0.0
    return np.mean([r["refined_pass"] for r in subset])


def compute_did_contrast(results: list[dict]) -> float:
    """(RL_actual - RL_control) - (CE_actual - CE_control)."""
    rl_actual = pass_rate(results, "RL", "actual")
    rl_control = pass_rate(results, "RL", "control")
    ce_actual = pass_rate(results, "CE", "actual")
    ce_control = pass_rate(results, "CE", "control")
    return (rl_actual - rl_control) - (ce_actual - ce_control)


def bootstrap_did_ci(
    results: list[dict],
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict:
    """Stratified bootstrap CI for DiD contrast (resample by task_id)."""
    by_task = defaultdict(list)
    for r in results:
        by_task[r["problem_id"]].append(r)

    task_ids = list(by_task.keys())
    rng = np.random.RandomState(seed)
    did_samples = []

    for _ in range(n_bootstrap):
        sampled_ids = rng.choice(task_ids, size=len(task_ids), replace=True)
        boot_results = []
        for tid in sampled_ids:
            boot_results.extend(by_task[tid])
        did_samples.append(compute_did_contrast(boot_results))

    did_samples = np.array(did_samples)
    ci_lower = np.percentile(did_samples, 100 * alpha / 2)
    ci_upper = np.percentile(did_samples, 100 * (1 - alpha / 2))
    did_point = compute_did_contrast(results)
    p_value = np.mean(did_samples <= 0)

    return {
        "did_contrast": did_point,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "significant": ci_lower > 0,
        "p_value_one_sided": p_value,
        "boot_samples": did_samples.tolist(),
    }


def per_error_type_did(results: list[dict]) -> dict[str, float]:
    """DiD contrast computed within each error category."""
    by_type = defaultdict(list)
    for r in results:
        by_type[r["error_type"]].append(r)

    did_by_type = {}
    for etype, etype_results in by_type.items():
        if len(etype_results) >= 4:
            did_by_type[etype] = compute_did_contrast(etype_results)
    return did_by_type


def per_problem_effect_sizes(results: list[dict]) -> list[float]:
    """Per-problem (RL_diff - CE_diff) for effect histogram."""
    by_task = defaultdict(list)
    for r in results:
        by_task[r["problem_id"]].append(r)

    effects = []
    for tid, rows in by_task.items():
        rl_actual = [r["refined_pass"] for r in rows if r["model"] == "RL" and r["condition"] == "actual"]
        rl_control = [r["refined_pass"] for r in rows if r["model"] == "RL" and r["condition"] == "control"]
        ce_actual = [r["refined_pass"] for r in rows if r["model"] == "CE" and r["condition"] == "actual"]
        ce_control = [r["refined_pass"] for r in rows if r["model"] == "CE" and r["condition"] == "control"]

        if rl_actual and rl_control and ce_actual and ce_control:
            rl_diff = np.mean(rl_actual) - np.mean(rl_control)
            ce_diff = np.mean(ce_actual) - np.mean(ce_control)
            effects.append(rl_diff - ce_diff)

    return effects


def cell_means(results: list[dict]) -> dict[str, float]:
    """Return pass@1 for each of 4 cells."""
    return {
        "RL_actual": pass_rate(results, "RL", "actual"),
        "RL_control": pass_rate(results, "RL", "control"),
        "CE_actual": pass_rate(results, "CE", "actual"),
        "CE_control": pass_rate(results, "CE", "control"),
    }
