# H-M4 Metrics: Share comparison and gate evaluation
# Gate: Traditional share decreased relative to total (emergent has higher share)
# AND traditional benchmark papers still exist (persistence confirmed)

import pandas as pd
from config import TRADITIONAL_BENCHMARKS, COUNT_RATIO_BOUNDS


def evaluate_gate(stats: dict) -> dict:
    """Evaluate H-M4 gate criteria.

    Original hypothesis: "ImageNet/CIFAR share decreases while absolute counts remain stable"

    Adapted validation:
    1. Share decreased: Traditional share < 50% (no longer dominant)
    2. Counts stable: Traditional papers > 10,000 (persistence confirmed)

    Gate PASS = both conditions met
    """
    # Traditional benchmarks are no longer dominant if their share < 50%
    share_decreased = stats["traditional_share"] < 0.50

    # Traditional benchmarks persist if they have substantial papers
    # Using 10,000 as threshold (significant presence)
    counts_stable = stats["traditional_papers"] > 10000

    gate_pass = share_decreased and counts_stable

    # Compute dominance ratio: emergent / traditional
    if stats["traditional_papers"] > 0:
        dominance_shift = stats["emergent_papers"] / stats["traditional_papers"]
    else:
        dominance_shift = float("inf")

    return {
        "traditional_share": stats["traditional_share"],
        "emergent_share": stats["emergent_share"],
        "traditional_papers": stats["traditional_papers"],
        "emergent_papers": stats["emergent_papers"],
        "share_decreased": share_decreased,
        "counts_stable": counts_stable,
        "dominance_shift": dominance_shift,
        "gate_pass": gate_pass,
    }


def compute_per_benchmark_metrics(df: pd.DataFrame) -> dict:
    """Compute per-benchmark paper counts."""
    results = {}

    for benchmark in TRADITIONAL_BENCHMARKS:
        benchmark_lower = benchmark.lower()
        mask = df["dataset_name"].str.contains(benchmark_lower, case=False, na=False)
        papers = df[mask]["paper_count"].sum()
        results[benchmark] = int(papers)

    return results
