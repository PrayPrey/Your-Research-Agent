"""End-to-end experiment orchestration for H-M2."""

import os
import json
import pickle
import numpy as np
from datetime import datetime

from config import (
    SEED, DATASET_NAME, MIN_TURNS, OUTPUT_DIR, FIGURES_DIR,
    RESULTS_PATH, GATE_R_THRESHOLD, GATE_P_THRESHOLD
)
from data import load_and_pair
from formality import FormalityScorer, score_pairs
from correlation import compute_correlation, check_gate
from baseline import run_permutation_test
from visualize import generate_all_figures
from ablation import run_ablations


def main() -> dict:
    """Run full H-M2 experiment pipeline."""
    np.random.seed(SEED)
    start_time = datetime.now()

    print("=" * 60)
    print("H-M2: AI Formality Response Varies")
    print("=" * 60)

    # Step 1: Load and pair data
    print("\n[1/6] Loading dataset and extracting pairs...")
    pairs = load_and_pair(DATASET_NAME, MIN_TURNS)
    print(f"  Loaded {len(pairs)} valid (human_1, AI_1) pairs")

    if len(pairs) < 10000:
        raise ValueError(f"Insufficient pairs: {len(pairs)} < 10000")

    # Step 2: Score formality
    print("\n[2/6] Scoring formality with DeBERTa...")
    scorer = FormalityScorer()
    human_scores, ai_scores = score_pairs(pairs, scorer)

    # Step 3: Compute correlation
    print("\n[3/6] Computing correlation...")
    corr_results = compute_correlation(human_scores, ai_scores)
    print(f"  n = {corr_results['n']}")
    print(f"  Pearson r = {corr_results['pearson_r']:.4f} (p = {corr_results['pearson_p']:.2e})")
    print(f"  Spearman rho = {corr_results['spearman_rho']:.4f} (p = {corr_results['spearman_p']:.2e})")
    print(f"  Human formality: mean={corr_results['human_mean']:.4f}, SD={corr_results['human_sd']:.4f}")
    print(f"  AI formality: mean={corr_results['ai_mean']:.4f}, SD={corr_results['ai_sd']:.4f}")

    # Step 4: Run permutation baseline
    print("\n[4/6] Running permutation baseline...")
    baseline_results = run_permutation_test(human_scores, ai_scores)
    print(f"  Null mean = {baseline_results['null_mean']:.6f}")
    print(f"  Null std = {baseline_results['null_std']:.6f}")
    print(f"  Null p-value = {baseline_results['null_p']:.4f}")

    # Step 5: Check gate
    print("\n[5/6] Evaluating SHOULD_WORK gate...")
    gate_results = check_gate(corr_results)
    print(f"  Gate threshold: |r| > {gate_results['r_threshold']}, p < {gate_results['p_threshold']}")
    print(f"  Observed |r| = {abs(corr_results['pearson_r']):.4f}")
    print(f"  Gate verdict: {gate_results['verdict']}")

    # Step 6: Generate visualizations
    print("\n[6/6] Generating visualizations...")
    generate_all_figures(human_scores, ai_scores, corr_results['pearson_r'])

    # Compile results
    results = {
        'hypothesis_id': 'h-m2',
        'timestamp': start_time.isoformat(),
        'duration_seconds': (datetime.now() - start_time).total_seconds(),
        'dataset': DATASET_NAME,
        'n_pairs': len(pairs),
        'correlation': corr_results,
        'baseline': baseline_results,
        'gate': gate_results,
        'figures_generated': [
            'scatter_regression.png',
            'correlation_bar.png',
            'hexbin_density.png',
            'qq_plot.png',
            'residual_plot.png'
        ]
    }

    # Run ablations if gate failed
    if not gate_results['gate_pass']:
        print("\n[Ablation] Gate failed - running ablation studies...")
        ablation_results = run_ablations(human_scores, ai_scores, pairs)
        results['ablation'] = ablation_results
        print(f"  Extreme filter r = {ablation_results['extreme_filter'].get('pearson_r', 'N/A')}")

    # Save results
    with open(RESULTS_PATH, 'wb') as f:
        pickle.dump(results, f)
    print(f"\nResults saved: {RESULTS_PATH}")

    json_path = os.path.join(OUTPUT_DIR, 'experiment_results.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"JSON saved: {json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("H-M2 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate: {gate_results['verdict']}")
    print(f"r = {corr_results['pearson_r']:.4f}, p = {corr_results['pearson_p']:.2e}, n = {corr_results['n']}")

    return results


if __name__ == "__main__":
    results = main()
