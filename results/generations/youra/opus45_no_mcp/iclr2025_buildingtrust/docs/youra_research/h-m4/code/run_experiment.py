#!/usr/bin/env python3
"""H-M4 Experiment Runner: Orchestrate hedging-confidence correlation analysis."""

import json
import sys
import yaml
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import H_M4_Config
from data_loader import load_h_m2_cache, validate_cache_format, extract_pairs
from correlation_analyzer import (
    compute_spearman,
    compute_confidence_interval,
    detect_outliers,
    compute_gate_metrics
)
from visualization import (
    plot_scatter_regression,
    plot_box_by_bucket,
    plot_gate_comparison,
    plot_hedging_histogram
)


def run_h_m4_experiment(config: H_M4_Config = None) -> dict:
    """Run complete H-M4 correlation analysis experiment."""
    if config is None:
        config = H_M4_Config()

    print(f"[H-M4] Starting hedging-confidence correlation analysis")
    print(f"[H-M4] Cache path: {config.h_m2_cache_path}")

    data = load_h_m2_cache(config.h_m2_cache_path)
    if not validate_cache_format(data):
        raise ValueError("Invalid H-M2 cache format")

    hedging_counts, confidence_scores = extract_pairs(data)
    n = len(hedging_counts)
    print(f"[H-M4] Extracted {n} valid pairs")

    if n < config.min_samples:
        print(f"[H-M4] WARNING: n={n} < min_samples={config.min_samples}")

    stats = compute_spearman(hedging_counts, confidence_scores)
    print(f"[H-M4] Spearman r={stats['spearman_r']:.4f}, p={stats['p_value']:.4e}")

    ci = compute_confidence_interval(
        hedging_counts, confidence_scores,
        n_boot=config.n_bootstrap,
        alpha=config.alpha,
        seed=config.bootstrap_seed
    )
    print(f"[H-M4] 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

    outliers = detect_outliers(hedging_counts, confidence_scores)
    print(f"[H-M4] Outliers detected: {outliers['outlier_count']}")

    gate_metrics = compute_gate_metrics(stats, ci, n, config)
    print(f"[H-M4] Gate 1 (r < {config.gate_r_threshold}): {'PASS' if gate_metrics['gate_1_r_pass'] else 'FAIL'}")
    print(f"[H-M4] Gate 2 (p < {config.gate_p_threshold}): {'PASS' if gate_metrics['gate_2_p_pass'] else 'FAIL'}")
    print(f"[H-M4] Gate 3 (n >= {config.min_samples}): {'PASS' if gate_metrics['gate_3_n_pass'] else 'FAIL'}")
    print(f"[H-M4] All gates: {'PASS' if gate_metrics['all_gates_pass'] else 'FAIL'}")

    figures_dir = config.figures_dir

    plot_scatter_regression(
        hedging_counts, confidence_scores,
        stats['spearman_r'], stats['p_value'],
        figures_dir / 'scatter_regression.png',
        dpi=config.figure_dpi
    )

    plot_box_by_bucket(
        hedging_counts, confidence_scores,
        config.hedging_buckets,
        figures_dir / 'box_by_bucket.png',
        dpi=config.figure_dpi
    )

    plot_gate_comparison(
        gate_metrics,
        figures_dir / 'gate_comparison.png',
        dpi=config.figure_dpi
    )

    plot_hedging_histogram(
        hedging_counts,
        figures_dir / 'hedging_histogram.png',
        dpi=config.figure_dpi
    )

    print(f"[H-M4] Figures saved to {figures_dir}")

    results = {
        'hypothesis_id': config.hypothesis_id,
        'hypothesis_type': config.hypothesis_type,
        'timestamp': datetime.now().isoformat(),
        'spearman_r': stats['spearman_r'],
        'p_value': stats['p_value'],
        'n_samples': n,
        'confidence_interval': list(ci),
        'outlier_count': outliers['outlier_count'],
        'gate_metrics': gate_metrics,
        'gate_pass': gate_metrics['all_gates_pass']
    }

    results_path = config.output_dir / 'h-m4_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[H-M4] Results saved to {results_path}")

    gate_path = config.output_dir / 'gate_metrics.yaml'
    with open(gate_path, 'w') as f:
        yaml.dump(gate_metrics, f, default_flow_style=False)
    print(f"[H-M4] Gate metrics saved to {gate_path}")

    return results


if __name__ == '__main__':
    results = run_h_m4_experiment()
    gate_pass = results.get('gate_pass', False)
    print(f"\n[H-M4] Experiment completed. Gate: {'PASS' if gate_pass else 'FAIL'}")
    sys.exit(0 if gate_pass else 1)
