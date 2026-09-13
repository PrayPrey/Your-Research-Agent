"""Statistical tests for min-k% memorization signal (H-M2)."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkStat:
    benchmark: str
    model_size: str       # "1b" or "6.9b"
    mean_pile: float
    mean_deduped: float
    differential: float   # mean_pile - mean_deduped
    t_statistic: float
    p_value: float        # raw one-tailed
    p_corrected: float    # Bonferroni: p_raw * n_benchmarks
    wilcoxon_p: float
    cohens_d: float
    significant: bool     # p_corrected < corrected_alpha


@dataclass
class SpearmanResult:
    rho: float
    p_value: float
    hm1_benchmark_order: list
    hm2_benchmark_order: list


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Pooled Cohen's d effect size."""
    n_a, n_b = len(a), len(b)
    if n_a < 2 or n_b < 2:
        return float("nan")
    pooled_std = np.sqrt(((n_a - 1) * a.std(ddof=1) ** 2 + (n_b - 1) * b.std(ddof=1) ** 2)
                         / (n_a + n_b - 2))
    if pooled_std == 0:
        return float("nan")
    return float((a.mean() - b.mean()) / pooled_std)


def run_benchmark_stat(
    pile_scores: list[float],
    deduped_scores: list[float],
    benchmark: str,
    model_size: str,
    n_benchmarks: int = 4,
    corrected_alpha: float = 0.0125,
) -> BenchmarkStat:
    """Compute paired t-test + Wilcoxon + Cohen's d for one benchmark × model_size."""
    from scipy import stats

    pile = np.array([s for s in pile_scores if not np.isneginf(s)])
    dedup = np.array([s for s in deduped_scores if not np.isneginf(s)])

    # Use minimum overlap for paired test
    min_n = min(len(pile), len(dedup))
    if min_n < 2:
        logger.warning(f"Too few items for {benchmark}/{model_size}: {min_n}")
        return BenchmarkStat(
            benchmark=benchmark, model_size=model_size,
            mean_pile=float(pile.mean()) if len(pile) else float("nan"),
            mean_deduped=float(dedup.mean()) if len(dedup) else float("nan"),
            differential=float("nan"), t_statistic=float("nan"),
            p_value=1.0, p_corrected=1.0, wilcoxon_p=1.0,
            cohens_d=float("nan"), significant=False,
        )

    pile_paired = pile[:min_n]
    dedup_paired = dedup[:min_n]

    t_stat, p_two = stats.ttest_rel(pile_paired, dedup_paired)
    # One-tailed (pile > dedup): if t > 0, p_one = p_two/2; else p_one = 1 - p_two/2
    p_one = p_two / 2 if t_stat > 0 else 1.0 - p_two / 2
    p_corrected = min(1.0, p_one * n_benchmarks)

    try:
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(
            pile_paired, dedup_paired, alternative="greater"
        )
    except Exception:
        wilcoxon_p = 1.0

    d = cohens_d(pile_paired, dedup_paired)
    differential = float(pile.mean()) - float(dedup.mean())

    return BenchmarkStat(
        benchmark=benchmark,
        model_size=model_size,
        mean_pile=float(pile.mean()),
        mean_deduped=float(dedup.mean()),
        differential=differential,
        t_statistic=float(t_stat),
        p_value=float(p_one),
        p_corrected=float(p_corrected),
        wilcoxon_p=float(wilcoxon_p),
        cohens_d=float(d),
        significant=p_corrected < corrected_alpha,
    )


def run_all_tests(
    scores: dict,  # ScoresDict: {model_key: {benchmark: [scores]}}
    n_benchmarks: int = 4,
    corrected_alpha: float = 0.0125,
) -> list[BenchmarkStat]:
    """Run stats for all benchmarks × model sizes."""
    from config import BENCHMARKS

    stats_list = []
    for size in ["1b", "6.9b"]:
        pile_key = f"pile_{size}"
        dedup_key = f"deduped_{size}"
        pile_scores_map = scores.get(pile_key, {})
        dedup_scores_map = scores.get(dedup_key, {})

        for bench in BENCHMARKS:
            pile_bench = pile_scores_map.get(bench, [])
            dedup_bench = dedup_scores_map.get(bench, [])

            if not pile_bench or not dedup_bench:
                logger.warning(f"Missing scores for {bench}/{size}")
                continue

            stat = run_benchmark_stat(
                pile_bench, dedup_bench, bench, size,
                n_benchmarks=n_benchmarks,
                corrected_alpha=corrected_alpha,
            )
            stats_list.append(stat)
            logger.info(
                f"{bench}/{size}: pile={stat.mean_pile:.4f} dedup={stat.mean_deduped:.4f} "
                f"diff={stat.differential:.4f} p_corr={stat.p_corrected:.4f} "
                f"sig={'YES' if stat.significant else 'no'}"
            )

    return stats_list


def compute_spearman_cross_hypothesis(
    hm2_stats: list[BenchmarkStat],
    hm1_results_path,
    model_size: str = "6.9b",
) -> SpearmanResult:
    """Spearman correlation between H-M1 contamination differential and H-M2 memorization differential."""
    import json
    from pathlib import Path
    from scipy.stats import spearmanr
    from config import BENCHMARKS

    hm1_path = Path(hm1_results_path)
    if not hm1_path.exists():
        logger.warning(f"H-M1 results not found: {hm1_path}")
        return SpearmanResult(rho=float("nan"), p_value=float("nan"),
                              hm1_benchmark_order=[], hm2_benchmark_order=[])

    hm1_data = json.loads(hm1_path.read_text())

    x_vals, y_vals, labels = [], [], []
    for bench in BENCHMARKS:
        if bench not in hm1_data:
            continue
        hm1_diff = hm1_data[bench].get("mean_removed", 0) - hm1_data[bench].get("mean_retained", 0)
        hm2_stat = next(
            (s for s in hm2_stats if s.benchmark == bench and s.model_size == model_size), None
        )
        if hm2_stat is None:
            continue
        x_vals.append(hm1_diff)
        y_vals.append(hm2_stat.differential)
        labels.append(bench)

    if len(x_vals) >= 3:
        rho, p_val = spearmanr(x_vals, y_vals)
    else:
        rho, p_val = float("nan"), float("nan")

    hm1_order = [l for _, l in sorted(zip(x_vals, labels), reverse=True)]
    hm2_order = [l for _, l in sorted(zip(y_vals, labels), reverse=True)]

    return SpearmanResult(
        rho=float(rho), p_value=float(p_val),
        hm1_benchmark_order=hm1_order,
        hm2_benchmark_order=hm2_order,
    )
