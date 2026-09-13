"""A-6: Statistical Tester — Mann-Whitney U, Bonferroni, Spearman rho."""
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

from config import BENCHMARKS, CORRECTED_ALPHA, CHECKPOINT_DIR


@dataclass
class BenchmarkStat:
    benchmark: str
    u_statistic: float
    p_value: float
    p_corrected: float
    rank_biserial_r: float
    significant: bool
    mean_removed: float
    mean_retained: float
    ratio: float


@dataclass
class SpearmanResult:
    correlation: float
    p_value: float
    expected_ranking: list
    observed_ranking: list


def run_mannwhitney_suite(
    removed: np.ndarray,
    retained: np.ndarray,
    benchmark_names: list[str] = BENCHMARKS,
    alpha: float = 0.05,
    n_benchmarks: int = 4,
) -> list[BenchmarkStat]:
    """One-tailed Mann-Whitney U per benchmark (H1: removed > retained).

    Bonferroni: p_corrected = p_raw * n_benchmarks.
    Rank-biserial r = 1 - 2U / (n1*n2).
    """
    benchmarks = sorted(benchmark_names)
    n1, n2 = len(removed), len(retained)
    corrected_alpha = alpha / n_benchmarks
    stats = []

    for i, bench in enumerate(benchmarks):
        r = removed[:, i].astype(float)
        t = retained[:, i].astype(float)
        u, p = mannwhitneyu(r, t, alternative="greater")
        p_corr = min(float(p) * n_benchmarks, 1.0)
        rr = 1.0 - (2.0 * float(u)) / (n1 * n2)
        mean_r = float(np.mean(r))
        mean_t = float(np.mean(t))
        ratio = mean_r / mean_t if mean_t > 0 else float("inf")
        stats.append(BenchmarkStat(
            benchmark=bench,
            u_statistic=float(u),
            p_value=float(p),
            p_corrected=p_corr,
            rank_biserial_r=rr,
            significant=p_corr < corrected_alpha,
            mean_removed=mean_r,
            mean_retained=mean_t,
            ratio=ratio,
        ))
    return stats


def compute_rank_correlation(
    stats: list[BenchmarkStat],
    expected_ranking: list[str] = ["mmlu", "arc_challenge", "hellaswag", "winogrande"],
) -> SpearmanResult:
    """Spearman rho: expected contamination rank vs observed mean overlap diff."""
    expected_rank = {b: i + 1 for i, b in enumerate(expected_ranking)}
    observed_sorted = sorted(stats, key=lambda s: s.mean_removed - s.mean_retained, reverse=True)
    observed_ranking = [s.benchmark for s in observed_sorted]

    x = [expected_rank[s.benchmark] for s in stats if s.benchmark in expected_rank]
    y = [observed_ranking.index(s.benchmark) + 1 for s in stats if s.benchmark in expected_rank]

    if len(x) < 2:
        return SpearmanResult(correlation=float("nan"), p_value=float("nan"),
                               expected_ranking=expected_ranking, observed_ranking=observed_ranking)

    rho, p = spearmanr(x, y)
    return SpearmanResult(
        correlation=float(rho),
        p_value=float(p),
        expected_ranking=expected_ranking,
        observed_ranking=observed_ranking,
    )


def mechanism_check(stats: list[BenchmarkStat]) -> None:
    """Assert contamination signal is non-trivial (removed/retained MMLU ratio ≥ 1.2×)."""
    mmlu_stats = [s for s in stats if s.benchmark == "mmlu"]
    if not mmlu_stats:
        print("WARNING: mmlu not in stats, skipping mechanism check")
        return
    mmlu = mmlu_stats[0]
    if mmlu.ratio < 1.2:
        raise RuntimeError(
            f"Mechanism check fail: removed/retained MMLU ratio = {mmlu.ratio:.2f}×"
            " (expected ≥ 1.2×). Dedup may not selectively remove benchmark-adjacent docs."
        )
    print(f"✅ Mechanism active: removed/retained MMLU ratio = {mmlu.ratio:.1f}×")
    for s in stats:
        print(f"  {s.benchmark}: mean_removed={s.mean_removed:.4f}, "
              f"mean_retained={s.mean_retained:.4f}, ratio={s.ratio:.1f}×")


def run_tests(
    overlap_scores: dict[str, dict[str, list[float]]],
    checkpoint_path: Path = CHECKPOINT_DIR / "statistical_results.json",
) -> dict:
    """Run Mann-Whitney suite + Spearman, save JSON checkpoint."""
    if checkpoint_path.exists():
        print(f"✓ Loading statistical results from checkpoint")
        return json.loads(checkpoint_path.read_text())

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    benchmarks = sorted(overlap_scores["removed"].keys())
    removed_arr = np.array([overlap_scores["removed"][b] for b in benchmarks], dtype=np.float32).T
    retained_arr = np.array([overlap_scores["retained"][b] for b in benchmarks], dtype=np.float32).T

    print("Running Mann-Whitney U tests...")
    stats = run_mannwhitney_suite(removed_arr, retained_arr, benchmark_names=benchmarks)

    mechanism_check(stats)

    print("Computing Spearman rank correlation...")
    spearman = compute_rank_correlation(stats)

    n_significant = sum(s.significant for s in stats)
    gate_pass = n_significant >= 2

    result = {
        "per_benchmark": {s.benchmark: asdict(s) for s in stats},
        "spearman": asdict(spearman),
        "summary": {
            "n_significant": n_significant,
            "gate_pass": gate_pass,
            "gate_condition": "n_significant >= 2",
            "alpha_corrected": CORRECTED_ALPHA,
        }
    }

    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2))
    os.replace(tmp, checkpoint_path)
    print(f"✓ Statistical results saved. Gate: {'PASS' if gate_pass else 'FAIL'} "
          f"({n_significant}/4 significant)")
    return result
