"""H-M1 analysis: Spearman ρ + trajectory stats."""

import statistics
from scipy.stats import spearmanr


def compute_mean_errors_per_round(
    records: list,
    benchmark: str,
    k_max: int = 5,
) -> dict:
    """Return {round_k: {"mean": float, "std": float, "n": int}}
    over problems with ≥1 mypy error at round 1."""
    bench_short = benchmark.replace("+", "")
    bench_records = [r for r in records if r["benchmark"] == bench_short]

    round1 = {
        r["task_id"]: r["mypy_error_count"]
        for r in bench_records if r["round"] == 1
    }
    eligible_tasks = {tid for tid, cnt in round1.items() if cnt > 0}

    result = {}
    for k in range(1, k_max + 1):
        errors_at_k = []
        for task_id in eligible_tasks:
            k_records = [r for r in bench_records if r["task_id"] == task_id and r["round"] == k]
            if k_records:
                errors_at_k.append(k_records[0]["mypy_error_count"])
            else:
                errors_at_k.append(0)  # early exit = exec passed = 0 errors

        n = len(errors_at_k)
        mean = statistics.mean(errors_at_k) if n > 0 else 0.0
        std = statistics.stdev(errors_at_k) if n > 1 else 0.0
        result[k] = {"mean": mean, "std": std, "n": n}

    return result


def compute_spearman(mean_errors_per_round: dict) -> tuple:
    """Return (rho, pval) from scipy.stats.spearmanr on mean error trajectory."""
    rounds = sorted(mean_errors_per_round.keys())
    means = [mean_errors_per_round[k]["mean"] for k in rounds]
    rho, pval = spearmanr(rounds, means)
    return float(rho), float(pval)


def verify_mechanism_activated(
    records: list,
    benchmark: str = "mbpp+",
) -> tuple:
    """Return (activated, indicators). activated = log_found AND rho_negative."""
    mean_errors = compute_mean_errors_per_round(records, benchmark)
    rho, pval = compute_spearman(mean_errors)

    bench_short = benchmark.replace("+", "")
    rounds_found = set(r["round"] for r in records if r["benchmark"] == bench_short)
    log_found = all(k in rounds_found for k in range(1, 6))

    indicators = {
        "log_found": log_found,
        "rho_negative": rho < 0,
        "round5_less_than_round1": (
            mean_errors.get(5, {}).get("mean", float("inf")) <
            mean_errors.get(1, {}).get("mean", 0.0)
        ),
        "rho": rho,
        "pval": pval,
    }
    activated = indicators["log_found"] and indicators["rho_negative"]
    return activated, indicators


def aggregate_results(records: list, k_max: int = 5) -> dict:
    """Return summary dict per benchmark: trajectory + spearman + gate."""
    benchmarks = list(set(r["benchmark"] for r in records))
    summary = {}
    for benchmark in benchmarks:
        mean_errors = compute_mean_errors_per_round(records, benchmark, k_max)
        rho, pval = compute_spearman(mean_errors)
        n_problems = len(set(r["task_id"] for r in records if r["benchmark"] == benchmark))
        summary[benchmark] = {
            "n_problems": n_problems,
            "n_with_initial_mypy_errors": mean_errors.get(1, {}).get("n", 0),
            "mean_errors_by_round": {k: v for k, v in mean_errors.items()},
            "spearman_rho": rho,
            "p_value": pval,
            "round5_less_than_round1": (
                mean_errors.get(5, {}).get("mean", float("inf")) <
                mean_errors.get(1, {}).get("mean", 0.0)
            ),
            "gate_passed": rho < 0,
        }
    return summary
