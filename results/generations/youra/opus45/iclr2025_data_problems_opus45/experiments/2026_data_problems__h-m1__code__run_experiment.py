"""
H-M1 Experiment Orchestration: Convex Metric Coupling Test

Tests whether corr(rho_r, rho_m | budget) >= 0.95 in convex settings
(logistic regression on ResNet-18 features).

MUST_WORK gate: Pass if correlation >= 0.95 at all 5 budget levels.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd

from config import get_config
from features import FeatureExtractor
from convex_model import ConvexLogisticModel
from loo_influence import ClosedFormLOO
from attribution_convex import LinearAttributionRunner
from metrics_analysis import (
    build_metrics_dataframe,
    compute_partial_correlations_all_budgets,
    compute_single_error_axis_r2,
    check_success_criteria,
)
from visualize import plot_all


def main():
    """
    Full H-M1 pipeline:
    1. Extract ResNet-18 features from CIFAR-10 subset
    2. Fit logistic regression, verify convexity
    3. Compute closed-form LOO via Hessian inversion
    4. Run all attribution methods (4 x 5 x 3 grid)
    5. Build metrics DataFrame
    6. Compute partial correlations per budget
    7. Compute single-error-axis R^2
    8. Check success criteria, save results
    9. Generate all figures
    """
    start_time = time.time()

    print("=" * 60)
    print("H-M1: Convex Metric Coupling Experiment")
    print("=" * 60)

    # Get config
    cfg = get_config()

    # Check for GPU
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Step 1: Extract features
    print("\n[1/9] Extracting features from ResNet-18...")
    extractor = FeatureExtractor(cfg, device=device)
    X_train, y_train, X_test, y_test = extractor.get_features()
    print(f"  X_train: {X_train.shape}, y_train: {y_train.shape}")
    print(f"  X_test: {X_test.shape}, y_test: {y_test.shape}")

    # Step 2: Fit logistic regression and verify convexity
    print("\n[2/9] Fitting Logistic Regression (convex model)...")
    convex_model = ConvexLogisticModel(cfg)
    convex_model.fit(X_train, y_train)

    print("\n[3/9] Verifying convexity (Hessian positive-definite)...")
    convexity_result = convex_model.verify_convexity(X_train)
    eigenvalues = convexity_result['eigenvalues']

    if not convexity_result['is_convex']:
        print("ERROR: Model is not convex! Hessian has non-positive eigenvalues.")
        return

    # Step 3: Compute closed-form LOO influences
    print("\n[4/9] Computing closed-form LOO influences...")
    loo_computer = ClosedFormLOO(convex_model, cfg)
    H_inv = loo_computer.compute_hessian_inverse(X_train)
    loo_exact = loo_computer.compute_influence(X_train, y_train, X_test, y_test, H_inv)

    # Step 4: Run attribution methods
    print("\n[5/9] Running attribution methods (4 methods x 5 budgets x 3 seeds)...")
    theta = convex_model.get_theta()
    runner = LinearAttributionRunner(cfg, theta)
    method_scores = runner.run_all(X_train, y_train, X_test, y_test, H_inv=H_inv)

    # Step 5: Build metrics DataFrame
    print("\n[6/9] Building metrics DataFrame...")
    metrics_df = build_metrics_dataframe(method_scores, loo_exact)
    print(f"  DataFrame shape: {metrics_df.shape}")
    print(metrics_df.head(10))

    # Save metrics CSV
    csv_path = os.path.join(cfg.results_dir, 'metrics.csv')
    metrics_df.to_csv(csv_path, index=False)
    print(f"  Saved: {csv_path}")

    # Step 6: Compute partial correlations
    print("\n[7/9] Computing partial correlations per budget...")
    partial_corrs = compute_partial_correlations_all_budgets(
        metrics_df, cfg.compute_budgets
    )

    # Step 7: Compute single-error-axis R^2
    print("\n[8/9] Computing single-error-axis R^2...")
    r2_results = compute_single_error_axis_r2(metrics_df)

    # Step 8: Check success criteria
    print("\n[9/9] Checking success criteria...")
    success_result = check_success_criteria(partial_corrs, r2_results, cfg)

    # Save success criteria JSON
    json_path = os.path.join(cfg.results_dir, 'success_criteria.json')
    # Convert numpy types to Python types for JSON serialization
    json_result = {
        'gate_pass': bool(success_result['gate_pass']),
        'partial_corr_pass': bool(success_result['partial_corr_pass']),
        'r2_pass': bool(success_result['r2_pass']),
        'partial_corrs': {str(k): float(v) for k, v in success_result['partial_corrs'].items()},
        'r2_results': {k: float(v) for k, v in success_result['r2_results'].items()},
        'min_partial_corr': float(success_result['min_partial_corr']),
        'failed_budgets': [int(b) for b in success_result['failed_budgets']],
        'convexity': {
            'is_convex': bool(convexity_result['is_convex']),
            'min_eigenvalue': float(convexity_result['min_eigenvalue']),
            'max_eigenvalue': float(convexity_result['max_eigenvalue']),
        },
    }
    with open(json_path, 'w') as f:
        json.dump(json_result, f, indent=2)
    print(f"  Saved: {json_path}")

    # Step 9: Generate figures
    plot_all(partial_corrs, metrics_df, eigenvalues, cfg)

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Elapsed time: {elapsed:.1f}s")
    print(f"\nGate Result: {'PASS' if success_result['gate_pass'] else 'FAIL'}")
    print(f"Min partial correlation: {success_result['min_partial_corr']:.4f}")
    print(f"R^2 average: {r2_results['r2_avg']:.4f}")

    if success_result['gate_pass']:
        print("\nMUST_WORK gate PASSED: Convex metric coupling confirmed.")
        print("corr(rho_r, rho_m | budget) >= 0.95 at all budget levels.")
    else:
        print("\nMUST_WORK gate FAILED:")
        print(f"  Failed budgets: {success_result['failed_budgets']}")

    return success_result


if __name__ == '__main__':
    main()
