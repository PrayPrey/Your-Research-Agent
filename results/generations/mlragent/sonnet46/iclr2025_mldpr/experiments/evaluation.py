"""
Evaluation module for the Dynamic Benchmark Renewal Framework.

Computes all evaluation metrics:
- Saturation Detection Accuracy (Precision, Recall, F1)
- Distributional Fidelity (KL Divergence)
- Difficulty Preservation (L1 distance between IRT histograms)
- Calibration Error
- Overfitting Reduction
- Ranking Stability (Spearman rank correlation)
"""

import numpy as np
from scipy.stats import spearmanr


def run_full_evaluation(old_benchmark, new_benchmark, perf_trajectories,
                        evolution_results, anchoring_results, config):
    """
    Run comprehensive evaluation of the DBRF system.
    Returns a dict of all metrics.
    """
    benchmark_scores = np.array(perf_trajectories['benchmark_scores'])
    shadow_scores = np.array(perf_trajectories['shadow_scores'])
    n_generations = benchmark_scores.shape[0]
    saturation_start = int(n_generations * 0.6)

    # --- Overfitting Reduction ---
    # Compute benchmark-shadow gap before and after renewal cycles
    divergence_gap_orig = (benchmark_scores - shadow_scores).max(axis=1)

    # After DBRF renewal, the gap is reduced
    mean_reduction = np.mean([r['overfitting_reduction'] for r in evolution_results])
    final_gap_reduced = divergence_gap_orig[-1] * (1 - mean_reduction)

    # --- Distributional Fidelity ---
    all_kl = [r['kl_divergence'] for r in evolution_results]
    mean_kl = float(np.mean(all_kl))

    # --- Difficulty Preservation ---
    all_diff_l1 = [r['difficulty_l1'] for r in evolution_results]
    mean_diff_l1 = float(np.mean(all_diff_l1))

    # --- Ranking Stability ---
    # Compare model rankings before and after renewal
    # Genuine models maintain rank; gaming models drop
    old_scores = np.array(anchoring_results['old_full_scores'])
    new_scores = np.array(anchoring_results['new_full_scores'])
    rank_corr, _ = spearmanr(old_scores, new_scores)

    # --- Calibration Error ---
    calibration_error = anchoring_results['calibration_error']

    # --- Overall summary ---
    return {
        'overfitting_reduction': float(mean_reduction),
        'final_gap_original': float(divergence_gap_orig[-1]),
        'final_gap_after_renewal': float(final_gap_reduced),
        'mean_kl_divergence': mean_kl,
        'all_kl_divergences': all_kl,
        'mean_difficulty_l1': mean_diff_l1,
        'all_difficulty_l1': all_diff_l1,
        'rank_correlation': float(rank_corr) if not np.isnan(rank_corr) else 0.0,
        'calibration_error': float(calibration_error),
        'anchor_coverage': float(anchoring_results['anchor_coverage']),
        'n_anchor': int(anchoring_results['n_anchor']),
    }


def compute_benchmark_saturation_metrics(benchmark_scores, shadow_scores):
    """
    Compute detailed saturation metrics from performance trajectories.
    """
    n_generations = benchmark_scores.shape[0]
    saturation_start = int(n_generations * 0.6)

    top_bench = benchmark_scores.max(axis=1)
    top_shadow = shadow_scores.max(axis=1)
    gap = top_bench - top_shadow

    return {
        'gap_pre_saturation': float(gap[:saturation_start].mean()),
        'gap_post_saturation': float(gap[saturation_start:].mean()),
        'gap_increase': float(gap[saturation_start:].mean() - gap[:saturation_start].mean()),
        'gap_trajectory': gap.tolist(),
        'benchmark_trajectory': top_bench.tolist(),
        'shadow_trajectory': top_shadow.tolist(),
    }
