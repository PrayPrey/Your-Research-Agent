"""A-7: Ablation Runner — n-gram size, ARC-Easy, and subset-stratified ablations."""
import json
import os
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import numpy as np

from config import BENCHMARKS, N_WORKERS, NGRAM_SIZE, CHECKPOINT_DIR
from sampler import DocWithMeta
from statistical_tester import BenchmarkStat, run_mannwhitney_suite


def _load_benchmark_ngrams(benchmarks: list[str], n: int) -> dict[str, frozenset]:
    from benchmark_ngrams import extract_ngrams
    ckpt = CHECKPOINT_DIR / f"ngram_sets_n{n}.pkl"
    return extract_ngrams(benchmarks=benchmarks, n=n, checkpoint_path=ckpt)


def _compute_batch(docs: list[DocWithMeta], ngram_sets: dict[str, frozenset], n: int) -> np.ndarray:
    from overlap_computer import compute_overlap_batch
    return compute_overlap_batch(docs, ngram_sets, n=n, n_workers=N_WORKERS)


def run_ngram_ablation(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    base_ngram_sets: dict[str, frozenset],
    ablation_sizes: list[int] = [8, 1],
    n_workers: int = N_WORKERS,
) -> dict[int, list[BenchmarkStat]]:
    """Repeat overlap + Mann-Whitney for n=8 and n=1."""
    benchmarks = sorted(base_ngram_sets.keys())
    results = {}
    for n in ablation_sizes:
        print(f"  N-gram ablation n={n}...")
        ngram_sets = _load_benchmark_ngrams(benchmarks, n)
        r_arr = _compute_batch(removed_docs, ngram_sets, n)
        t_arr = _compute_batch(retained_docs, ngram_sets, n)
        stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks)
        results[n] = stats
    return results


def run_benchmark_ablation(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    extra_benchmarks: list[str] = ["arc_easy"],
    n: int = NGRAM_SIZE,
    n_workers: int = N_WORKERS,
) -> dict[str, BenchmarkStat]:
    """Add arc_easy (or others) and rerun overlap + test for those benchmarks."""
    print(f"  Benchmark ablation: {extra_benchmarks}...")
    ngram_sets = _load_benchmark_ngrams(extra_benchmarks, n)
    benchmarks = sorted(ngram_sets.keys())
    r_arr = _compute_batch(removed_docs, ngram_sets, n)
    t_arr = _compute_batch(retained_docs, ngram_sets, n)
    stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks,
                                   alpha=0.05, n_benchmarks=len(benchmarks))
    return {s.benchmark: s for s in stats}


def run_subset_stratified(
    removed_docs: list[DocWithMeta],
    retained_docs: list[DocWithMeta],
    ngram_sets: dict[str, frozenset],
    n: int = NGRAM_SIZE,
    min_subset_size: int = 50,
    n_workers: int = N_WORKERS,
) -> dict[str, list[BenchmarkStat]]:
    """Within each Pile subset, compare removed vs retained overlap."""
    removed_by_subset: dict[str, list] = defaultdict(list)
    retained_by_subset: dict[str, list] = defaultdict(list)
    for d in removed_docs:
        removed_by_subset[d.pile_subset].append(d)
    for d in retained_docs:
        retained_by_subset[d.pile_subset].append(d)

    benchmarks = sorted(ngram_sets.keys())
    results = {}
    for subset in removed_by_subset:
        r_docs = removed_by_subset[subset]
        t_docs = retained_by_subset.get(subset, [])
        if len(r_docs) < min_subset_size or len(t_docs) < min_subset_size:
            continue
        print(f"  Subset '{subset}': removed={len(r_docs)}, retained={len(t_docs)}")
        r_arr = _compute_batch(r_docs, ngram_sets, n)
        t_arr = _compute_batch(t_docs, ngram_sets, n)
        stats = run_mannwhitney_suite(r_arr, t_arr, benchmark_names=benchmarks,
                                       alpha=0.05, n_benchmarks=1)
        results[subset] = stats
    return results


def compile_ablation_report(
    ngram_ablation: dict[int, list[BenchmarkStat]],
    benchmark_ablation: dict[str, BenchmarkStat],
    subset_ablation: dict[str, list[BenchmarkStat]],
) -> dict:
    """Aggregate all ablation results into serializable dict."""
    def stat_to_dict(s: BenchmarkStat) -> dict:
        return {
            "significant": s.significant,
            "p_corrected": s.p_corrected,
            "ratio": s.ratio,
            "rank_biserial_r": s.rank_biserial_r,
            "mean_removed": s.mean_removed,
            "mean_retained": s.mean_retained,
        }

    report = {
        "ngram_sizes": {
            str(n): {s.benchmark: stat_to_dict(s) for s in stats}
            for n, stats in ngram_ablation.items()
        },
        "extra_benchmarks": {b: stat_to_dict(s) for b, s in benchmark_ablation.items()},
        "subset_stratified": {
            subset: {s.benchmark: stat_to_dict(s) for s in stats}
            for subset, stats in subset_ablation.items()
        },
        "summary": {
            f"n{n}_n_significant": sum(s.significant for s in stats)
            for n, stats in ngram_ablation.items()
        },
    }
    return report


def run_all_ablations(
    sampled_docs: dict[str, list[DocWithMeta]],
    ngram_sets: dict[str, frozenset],
    checkpoint_path: Path = CHECKPOINT_DIR / "ablation_results.json",
) -> dict:
    """Orchestrate all ablation variants, save to JSON."""
    if checkpoint_path.exists():
        print(f"✓ Loading ablation results from checkpoint")
        return json.loads(checkpoint_path.read_text())

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    removed_docs = sampled_docs["removed"]
    retained_docs = sampled_docs["retained"]

    print("Running n-gram size ablations (n=8, n=1)...")
    ngram_abl = run_ngram_ablation(removed_docs, retained_docs, ngram_sets)

    print("Running benchmark ablation (arc_easy)...")
    bench_abl = run_benchmark_ablation(removed_docs, retained_docs)

    print("Running subset-stratified ablation...")
    subset_abl = run_subset_stratified(removed_docs, retained_docs, ngram_sets)

    report = compile_ablation_report(ngram_abl, bench_abl, subset_abl)

    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2))
    os.replace(tmp, checkpoint_path)
    print(f"✓ Ablation results saved to {checkpoint_path}")
    return report
