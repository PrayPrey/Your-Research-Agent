"""H-M3 statistical analysis: per-problem delta, Welch's t-test, confound control."""

import numpy as np
from scipy import stats
from collections import defaultdict


def compute_per_problem_delta(results: list, dataset: str) -> tuple:
    """Per-problem pass@1 averaged over seeds and rounds.

    Returns (pass_a_per_problem, pass_b_per_problem) parallel lists.
    For each problem, pass@1 = 1 if any round passed across any seed, else 0.
    """
    ds_results = [r for r in results if r.get("dataset") == dataset]

    # group by (condition, task_id) -> list of seed results
    by_cond_task = defaultdict(list)
    for r in ds_results:
        by_cond_task[(r["condition"], r["task_id"])].append(r)

    # collect all task_ids in consistent order
    all_task_ids = sorted(set(r["task_id"] for r in ds_results))

    pass_a = []
    pass_b = []
    for task_id in all_task_ids:
        records_a = by_cond_task[("A", task_id)]
        records_b = by_cond_task[("B", task_id)]
        # pass@1 per seed: 1 if any round passed
        val_a = np.mean([float(r["final_passed"]) for r in records_a]) if records_a else 0.0
        val_b = np.mean([float(r["final_passed"]) for r in records_b]) if records_b else 0.0
        pass_a.append(val_a)
        pass_b.append(val_b)

    return pass_a, pass_b


def welch_test(pass_a: list, pass_b: list) -> dict:
    """Welch's t-test on per-problem values. Gate: p < 0.05 AND delta >= 0.01."""
    arr_a = np.array(pass_a)
    arr_b = np.array(pass_b)
    delta = arr_b - arr_a
    absolute_improvement = float(np.mean(delta))
    n = len(delta)

    if n < 2 or np.std(arr_a) == 0 and np.std(arr_b) == 0:
        t_stat, p_value = 0.0, 1.0
    else:
        t_stat, p_value = stats.ttest_ind(arr_b, arr_a, equal_var=False)

    ci = stats.t.interval(0.95, df=n - 1, loc=absolute_improvement,
                          scale=stats.sem(delta)) if n > 1 else (0.0, 0.0)

    gate_passed = bool(p_value < 0.05 and absolute_improvement >= 0.01)
    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "absolute_improvement": absolute_improvement,
        "ci_95": [float(ci[0]), float(ci[1])],
        "n": n,
        "gate_passed": gate_passed,
        "mean_pass_a": float(np.mean(arr_a)),
        "mean_pass_b": float(np.mean(arr_b)),
    }


def confound_analysis(results: list, dataset: str) -> dict:
    """Mean token delta (Condition B - A) per round for confound control."""
    ds = [r for r in results if r.get("dataset") == dataset]
    per_round_a = defaultdict(list)
    per_round_b = defaultdict(list)
    for r in ds:
        cond = r["condition"]
        for rd in r.get("rounds", []):
            tokens = rd.get("prompt_tokens", 0)
            if tokens > 0:
                k = rd["round"]
                if cond == "A":
                    per_round_a[k].append(tokens)
                else:
                    per_round_b[k].append(tokens)

    per_round_delta = {}
    for k in range(1, 6):
        mean_a = np.mean(per_round_a[k]) if per_round_a[k] else 0.0
        mean_b = np.mean(per_round_b[k]) if per_round_b[k] else 0.0
        per_round_delta[k] = float(mean_b - mean_a)

    all_deltas = list(per_round_delta.values())
    mean_delta = float(np.mean(all_deltas)) if all_deltas else 0.0
    return {"per_round_delta": per_round_delta, "mean_delta": mean_delta}


def compute_summary(results: list, dataset: str) -> dict:
    """Full analysis dict for one dataset."""
    pass_a, pass_b = compute_per_problem_delta(results, dataset)
    wt = welch_test(pass_a, pass_b)
    confound = confound_analysis(results, dataset)

    ds = [r for r in results if r.get("dataset") == dataset]
    cond_b = [r for r in ds if r["condition"] == "B"]
    mypy_triggered_count = sum(
        1 for r in cond_b
        for rd in r.get("rounds", [])
        if rd.get("mypy_error_count", 0) > 0
    )
    total_b_rounds = sum(len(r.get("rounds", [])) for r in cond_b)
    mypy_triggered_fraction = mypy_triggered_count / total_b_rounds if total_b_rounds > 0 else 0.0
    mechanism_activated = mypy_triggered_count > 0

    return {
        "dataset": dataset,
        "pass_a": pass_a,
        "pass_b": pass_b,
        "welch_test": wt,
        "confound": confound,
        "mechanism_activated": mechanism_activated,
        "mypy_triggered_count": mypy_triggered_count,
        "mypy_triggered_fraction": mypy_triggered_fraction,
        "gate_passed": wt["gate_passed"],
        "n_problems": len(pass_a),
    }


def compute_pass_at_1_by_round(results: list, dataset: str) -> dict:
    """Pass@1 per round k (0..5) per condition for F2 trajectory plot."""
    ds = [r for r in results if r.get("dataset") == dataset]
    by_cond = {"A": [r for r in ds if r["condition"] == "A"],
               "B": [r for r in ds if r["condition"] == "B"]}

    trajectory = {}
    for cond, rs in by_cond.items():
        by_round = defaultdict(list)
        for r in rs:
            for rd in r.get("rounds", []):
                by_round[rd["round"]].append(float(rd["exec_passed"]))
        trajectory[cond] = {k: float(np.mean(v)) for k, v in sorted(by_round.items())}

    return trajectory
