#!/usr/bin/env python3
"""Main entrypoint for H-M3 dose-response analysis."""
import sys
import json
from pathlib import Path
from config import DoseResponseConfig
from sweep_loader import load_sweep_results, generate_synthetic_sweep, to_ensemble_matrix
from dose_response import analyze_dose_response, verify_optimal_balance_point
from figures import plot_dose_response_curve, plot_model_comparison, plot_bootstrap_distribution

def main():
    print("=" * 60)
    print("H-M3: Dose-Response Analysis for Optimal Threshold")
    print("=" * 60)

    config = DoseResponseConfig()

    sweep = load_sweep_results(config.paths.sweep_data_path)
    if sweep is None:
        print("\nNo existing sweep data found. Generating synthetic data...")
        print("(Real experiment would use H-E1 perplexity sweep results)")
        sweep = generate_synthetic_sweep(
            thresholds=config.sweep.thresholds,
            n_seeds=config.sweep.n_seeds,
            optimal_threshold=45.0,
            peak_score=0.52,
            base_score=0.40,
            noise_std=0.005
        )

    thresholds, scores_matrix = to_ensemble_matrix(sweep)
    print(f"\nLoaded {len(thresholds)} threshold levels, {scores_matrix.shape[1]} seeds each")
    print(f"Thresholds: {thresholds.tolist()}")

    mean_scores = scores_matrix.mean(axis=1)
    print(f"\nMean scores by threshold:")
    for t, s in zip(thresholds, mean_scores):
        print(f"  p{int(t)}: {s:.4f}")

    print("\n--- Running Dose-Response Analysis ---")
    result = analyze_dose_response(sweep)

    print(f"\nModel AICs: {result.aic_values}")
    print(f"Model BICs: {result.bic_values}")
    print(f"Selected model: {result.best_model}")

    passed = verify_optimal_balance_point(result)

    print("\n--- Generating Figures ---")
    Path(config.paths.figures_dir).mkdir(parents=True, exist_ok=True)

    plot_dose_response_curve(
        thresholds, scores_matrix, result,
        save_path=f"{config.paths.figures_dir}/dose_response_curve.png"
    )
    plot_model_comparison(
        result.aic_values, result.bic_values,
        save_path=f"{config.paths.figures_dir}/model_comparison.png"
    )
    plot_bootstrap_distribution(
        thresholds, scores_matrix,
        n_bootstrap=config.bootstrap.n_bootstrap,
        seed=config.bootstrap.seed,
        save_path=f"{config.paths.figures_dir}/bootstrap_distribution.png"
    )

    results_summary = {
        "optimal_threshold": float(result.optimal_threshold),
        "optimal_score": float(result.optimal_score),
        "confidence_interval": [float(result.confidence_interval[0]), float(result.confidence_interval[1])],
        "best_model": result.best_model,
        "is_peak_internal": bool(result.is_peak_internal),
        "ci_width": float(result.confidence_interval[1] - result.confidence_interval[0]),
        "passed": bool(passed)
    }

    output_path = Path(config.paths.output_dir) / "analysis_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nResults saved: {output_path}")

    print("\n" + "=" * 60)
    print(f"H-M3 VERDICT: {'PASS' if passed else 'FAIL'}")
    print("=" * 60)

    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
