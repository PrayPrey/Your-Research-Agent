"""Per-task yield analysis and low-yield flagging."""
import csv
from pathlib import Path


def compute_yield_stats(results: list[dict]) -> dict:
    """Groups by task_id; returns {task_id: {mean_n_valid, mean_filter_rate, low_yield}}."""
    task_data: dict[str, list] = {}
    for r in results:
        tid = r["task_id"] if isinstance(r, dict) else r.task_id
        n_valid = r["n_valid"] if isinstance(r, dict) else r.n_valid
        filter_rate = r["filter_rate"] if isinstance(r, dict) else r.filter_rate
        task_data.setdefault(tid, []).append((n_valid, filter_rate))

    stats = {}
    for tid, entries in task_data.items():
        mean_n_valid = sum(e[0] for e in entries) / len(entries)
        mean_filter_rate = sum(e[1] for e in entries) / len(entries)
        low_yield = mean_n_valid < 100 or mean_filter_rate > 0.95
        stats[tid] = {
            "mean_n_valid": mean_n_valid,
            "mean_filter_rate": mean_filter_rate,
            "low_yield": low_yield,
        }
    return stats


def get_low_yield_tasks(
    yield_stats: dict,
    filter_rate_threshold: float = 0.95,
    min_valid: int = 100,
) -> list[str]:
    return [tid for tid, s in yield_stats.items() if s["low_yield"]]


def get_excluded_tasks(yield_stats: dict, results: list) -> list[str]:
    """Tasks where ALL triples have n_valid = 0."""
    task_valids: dict[str, list] = {}
    for r in results:
        tid = r["task_id"] if isinstance(r, dict) else r.task_id
        n_valid = r["n_valid"] if isinstance(r, dict) else r.n_valid
        task_valids.setdefault(tid, []).append(n_valid)
    return [tid for tid, vals in task_valids.items() if all(v == 0 for v in vals)]


def save_low_yield_report(yield_stats: dict, out_path: str = "results/low_yield_tasks.csv") -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "mean_n_valid", "mean_filter_rate", "low_yield"])
        writer.writeheader()
        for tid, s in yield_stats.items():
            writer.writerow({"task_id": tid, **s})
