#!/usr/bin/env python3
"""h-c2: Permutation Control for RandomForest-only subset."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import config
from data import load_rf_subset
from permutation import run_permutation_test
from evaluate import check_success, save_results
from visualize import plot_permutation_histogram, plot_effect_comparison


def main():
    print("h-c2 Permutation Test: RandomForest-only Analysis")
    print("=" * 50)

    # Load RF subset
    print(f"Loading data from: {config.SOURCE_DATA_PATH}")
    df = load_rf_subset(config.SOURCE_DATA_PATH, config.FILTER_ALGO, config.MIN_RF_SAMPLES)
    print(f"RF subset: {len(df)} rows, {df['dataset_id'].nunique()} datasets")

    # Run permutation test
    print(f"\nRunning permutation test (n={config.N_PERMUTATIONS}, seed={config.RANDOM_SEED})...")
    result = run_permutation_test(df, config.N_PERMUTATIONS, config.RANDOM_SEED)

    # Results
    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")
    print(f"True coefficient: {result['true_coef']:.6f}")
    print(f"P-value: {result['p_value']:.6f}")
    print(f"Percentile rank: {result['percentile_rank']:.2f}%")
    print(f"Effect ratio (95th/true): {result['effect_ratio']:.6f}")

    # Success check
    success = check_success(result, config.SUCCESS_CRITERIA)
    print(f"\n{'='*50}")
    print(f"GATE VERDICT: {'PASS' if success else 'FAIL'}")
    print(f"{'='*50}")
    print(f"  percentile_rank > {config.SUCCESS_CRITERIA['percentile_rank_min']}: {result['percentile_rank']:.2f} {'✓' if result['percentile_rank'] > config.SUCCESS_CRITERIA['percentile_rank_min'] else '✗'}")
    print(f"  p_value < {config.SUCCESS_CRITERIA['p_value_max']}: {result['p_value']:.6f} {'✓' if result['p_value'] < config.SUCCESS_CRITERIA['p_value_max'] else '✗'}")
    print(f"  effect_ratio < {config.SUCCESS_CRITERIA['effect_ratio_max']}: {result['effect_ratio']:.6f} {'✓' if result['effect_ratio'] < config.SUCCESS_CRITERIA['effect_ratio_max'] else '✗'}")

    # Save results and figures
    os.makedirs(os.path.dirname(config.PATHS["results"]), exist_ok=True)
    os.makedirs(config.PATHS["figures_dir"], exist_ok=True)

    save_results(result, success, config.PATHS["results"])
    print(f"\nResults saved to: {config.PATHS['results']}")

    plot_permutation_histogram(result, config.PATHS["hist_fig"])
    plot_effect_comparison(result, config.PATHS["effect_fig"])
    print(f"Figures saved to: {config.PATHS['figures_dir']}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
