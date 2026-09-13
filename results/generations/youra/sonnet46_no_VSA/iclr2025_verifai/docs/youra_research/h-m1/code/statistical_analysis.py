"""Statistical analysis for H-M1 oracle isolation experiment."""
import json
import csv
import numpy as np
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AggregatedStats:
    mean_isolation_gap: float
    wilcoxon_stat: float
    wilcoxon_p_raw: float
    wilcoxon_p_corrected: float
    gap_ci_lower: float
    gap_ci_upper: float
    mean_diff_failure_rate: float
    mean_contract_failure_rate: float
    mean_contract_unique_mass: float
    cu_ci_lower: float
    cu_ci_upper: float
    n_tasks_evaluated: int
    n_programs_total: int
    task_coverage_rate: float
    gate_passed: bool
    by_model: dict
    by_task_type: dict


def bootstrap_ci(values: list, n_bootstrap: int = 10_000, seed: int = 42) -> tuple:
    """95% bootstrap CI on mean. Identical to H-E1 metrics.bootstrap_ci."""
    if len(values) == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    arr = np.array(values)
    boot_means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(boot_means, 2.5)), float(np.percentile(boot_means, 97.5))


def wilcoxon_holm(per_task_gaps: list) -> tuple:
    """Wilcoxon signed-rank + Holm correction. Returns (stat, p_raw, p_corrected)."""
    from scipy.stats import wilcoxon
    from statsmodels.stats.multitest import multipletests

    if len(per_task_gaps) == 0:
        return 0.0, 1.0, 1.0

    # Remove zeros for Wilcoxon (zero-difference observations)
    nonzero = [g for g in per_task_gaps if g != 0.0]
    if len(nonzero) < 2:
        return 0.0, 1.0, 1.0

    try:
        stat, p_raw = wilcoxon(per_task_gaps, alternative="greater")
    except Exception:
        return 0.0, 1.0, 1.0

    # Holm correction (single p-value here — trivially equal)
    _, pvals_corrected, _, _ = multipletests([p_raw], method="holm")
    return float(stat), float(p_raw), float(pvals_corrected[0])


def compute_per_task_stats(results: list) -> dict:
    """Aggregate across programs per task.
    Returns {task_id: {mean_gap, mean_cu_mass, mean_diff_rate, mean_contract_rate, n_programs, task_type}}.
    """
    task_data = {}
    for r in results:
        tid = r.task_id
        task_data.setdefault(tid, {
            "gaps": [], "cu_masses": [], "diff_rates": [], "contract_rates": [],
            "task_type": r.task_type,
        })
        task_data[tid]["gaps"].append(r.oracle_isolation_gap)
        task_data[tid]["cu_masses"].append(r.contract_unique_mass)
        task_data[tid]["diff_rates"].append(r.diff_failure_rate)
        task_data[tid]["contract_rates"].append(r.contract_failure_rate)

    per_task = {}
    for tid, d in task_data.items():
        per_task[tid] = {
            "mean_gap": float(np.mean(d["gaps"])),
            "mean_cu_mass": float(np.mean(d["cu_masses"])),
            "mean_diff_rate": float(np.mean(d["diff_rates"])),
            "mean_contract_rate": float(np.mean(d["contract_rates"])),
            "n_programs": len(d["gaps"]),
            "task_type": d["task_type"],
        }
    return per_task


def aggregate_stats(
    results: list,
    n_total_tasks: int = 364,
    n_bootstrap: int = 10_000,
    seed: int = 42,
    gap_threshold: float = 0.10,
    cu_threshold: float = 0.05,
    cu_ci_threshold: float = 0.03,
    p_threshold: float = 0.01,
) -> tuple:
    """Compute all gate metrics. Returns (AggregatedStats, per_task dict)."""
    per_task = compute_per_task_stats(results)
    n_tasks = len(per_task)

    per_task_gaps = [d["mean_gap"] for d in per_task.values()]
    per_task_cu = [d["mean_cu_mass"] for d in per_task.values()]
    per_task_diff = [d["mean_diff_rate"] for d in per_task.values()]
    per_task_contract = [d["mean_contract_rate"] for d in per_task.values()]

    mean_gap = float(np.mean(per_task_gaps)) if per_task_gaps else 0.0
    mean_cu = float(np.mean(per_task_cu)) if per_task_cu else 0.0
    mean_diff = float(np.mean(per_task_diff)) if per_task_diff else 0.0
    mean_contract = float(np.mean(per_task_contract)) if per_task_contract else 0.0

    gap_ci_lower, gap_ci_upper = bootstrap_ci(per_task_gaps, n_bootstrap, seed)
    cu_ci_lower, cu_ci_upper = bootstrap_ci(per_task_cu, n_bootstrap, seed + 1)
    w_stat, p_raw, p_corrected = wilcoxon_holm(per_task_gaps)

    gate_passed = (
        mean_gap >= gap_threshold
        and p_corrected < p_threshold
        and cu_ci_lower > cu_ci_threshold
    )

    # Stratify by model
    by_model = {}
    for r in results:
        by_model.setdefault(r.model, {"gaps": [], "cu": [], "task_ids": set()})
        by_model[r.model]["gaps"].append(r.oracle_isolation_gap)
        by_model[r.model]["cu"].append(r.contract_unique_mass)
        by_model[r.model]["task_ids"].add(r.task_id)
    by_model_agg = {
        m: {
            "mean_gap": float(np.mean(d["gaps"])),
            "mean_cu_mass": float(np.mean(d["cu"])),
            "n_tasks": len(d["task_ids"]),
        }
        for m, d in by_model.items()
    }

    # Stratify by task type
    by_type = {}
    for tid, d in per_task.items():
        tt = d["task_type"]
        by_type.setdefault(tt, {"gaps": []})
        by_type[tt]["gaps"].append(d["mean_gap"])
    by_task_type = {
        tt: {"mean_gap": float(np.mean(d["gaps"])), "n_tasks": len(d["gaps"])}
        for tt, d in by_type.items()
    }

    stats = AggregatedStats(
        mean_isolation_gap=mean_gap,
        wilcoxon_stat=w_stat,
        wilcoxon_p_raw=p_raw,
        wilcoxon_p_corrected=p_corrected,
        gap_ci_lower=gap_ci_lower,
        gap_ci_upper=gap_ci_upper,
        mean_diff_failure_rate=mean_diff,
        mean_contract_failure_rate=mean_contract,
        mean_contract_unique_mass=mean_cu,
        cu_ci_lower=cu_ci_lower,
        cu_ci_upper=cu_ci_upper,
        n_tasks_evaluated=n_tasks,
        n_programs_total=len(results),
        task_coverage_rate=n_tasks / max(n_total_tasks, 1),
        gate_passed=gate_passed,
        by_model=by_model_agg,
        by_task_type=by_task_type,
    )
    return stats, per_task


def save_results(stats: "AggregatedStats", per_task: dict, results_dir: str, results: list) -> None:
    """Write oracle_isolation_results.json and per_task_results.csv."""
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result_dict = asdict(stats)
    with open(out_dir / "oracle_isolation_results.json", "w") as f:
        json.dump(result_dict, f, indent=2)

    # per-program CSV
    fields = ["task_id", "task_type", "model", "program_idx",
              "diff_failure_rate", "contract_failure_rate", "oracle_isolation_gap",
              "contract_unique_mass", "n_inputs", "n_redundant", "n_contract_unique",
              "n_differential_only", "n_neither", "n_errors"]
    from dataclasses import asdict as _asdict
    with open(out_dir / "per_task_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(_asdict(r))

    print(f"Results saved to {out_dir}")
