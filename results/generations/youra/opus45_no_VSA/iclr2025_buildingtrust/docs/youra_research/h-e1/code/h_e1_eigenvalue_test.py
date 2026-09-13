#!/usr/bin/env python3
"""H-E1 Existence Test: Residual eigenvalue significance via permutation."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_leaderboard
from preprocessing import filter_models, build_matrices, BENCHMARK_COLS
from analysis import residualize, fit_pca, permutation_test, check_assumptions
from visualization import plot_permutation_dist, plot_scree, plot_pc1_loadings


CONFIG = {
    "dataset_id": "open-llm-leaderboard/contents",
    "benchmarks": BENCHMARK_COLS,
    "min_benchmarks": 4,
    "date_range": ("2023-01-01", "2025-12-31"),
    "cache_path": "outputs/cache/open_llm_leaderboard.parquet",
    "n_permutations": 1000,
    "significance_level": 0.05,
    "min_sample_size": 80,
    "vif_threshold": 5.0,
    "random_seed": 42,
    "output_dir": "outputs",
    "results_filename": "h_e1_results.json",
    "figure_dpi": 150,
}


def main() -> dict:
    """Run full H-E1 pipeline."""
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-E1 Existence Test: Residual Eigenvalue Significance")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/6] Loading Open LLM Leaderboard data...")
    df = load_leaderboard(CONFIG["cache_path"])
    print(f"  Raw dataset: {len(df)} models")

    # Step 2: Filter
    print("\n[2/6] Applying inclusion criteria...")
    df_filtered = filter_models(
        df,
        min_benchmarks=CONFIG["min_benchmarks"],
        date_start=CONFIG["date_range"][0],
        date_end=CONFIG["date_range"][1],
        min_sample_size=CONFIG["min_sample_size"],
    )
    n_models = len(df_filtered)
    print(f"  Filtered dataset: {n_models} models")

    # Step 3: Build matrices
    print("\n[3/6] Building benchmark and confound matrices...")
    Y, X, model_names, benchmarks_used = build_matrices(df_filtered)
    print(f"  Y shape: {Y.shape}, X shape: {X.shape}")
    print(f"  Benchmarks: {benchmarks_used}")

    # Save benchmark matrix
    benchmark_df = pd.DataFrame(Y, columns=benchmarks_used, index=model_names)
    benchmark_df.to_csv(output_dir / "benchmark_matrix.csv")

    # Step 4: Residualize
    print("\n[4/6] Residualizing on confounds (log_params, release_date)...")
    Y_resid, r_squared = residualize(Y, X)
    print(f"  R² per benchmark: {[f'{r:.3f}' for r in r_squared]}")

    # Save residualized matrix
    resid_df = pd.DataFrame(Y_resid, columns=benchmarks_used, index=model_names)
    resid_df.to_csv(output_dir / "residualized_matrix.csv")

    # Step 5: PCA + Permutation test
    print("\n[5/6] Running PCA and permutation test (1000 permutations)...")
    pca_result = fit_pca(Y_resid)
    perm_result = permutation_test(Y_resid, n_perms=CONFIG["n_permutations"], seed=CONFIG["random_seed"])

    print(f"  λ₁ observed: {perm_result['lambda_obs']:.4f}")
    print(f"  95th percentile null: {perm_result['threshold_95']:.4f}")
    print(f"  p-value: {perm_result['p_value']:.4f}")
    print(f"  Variance explained by PC1: {pca_result['variance_explained_pc1']*100:.1f}%")

    # Step 6: Assumption checks
    print("\n[6/6] Running assumption checks...")
    assumptions = check_assumptions(Y_resid, X)
    print(f"  Shapiro-Wilk p-value: {assumptions['shapiro_p']:.4f}")
    print(f"  Max VIF: {assumptions['vif_max']:.2f}")
    print(f"  KMO: {assumptions['kmo']}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_permutation_dist(
        perm_result["null_dist"],
        perm_result["lambda_obs"],
        perm_result["threshold_95"],
        str(output_dir / "permutation_dist.png"),
    )
    plot_scree(pca_result["eigenvalues"], str(output_dir / "scree_plot.png"))
    plot_pc1_loadings(pca_result["loadings_pc1"], benchmarks_used, str(output_dir / "pc1_loadings.png"))

    # Assemble results
    results = {
        "hypothesis_id": "H-E1",
        "n_models": n_models,
        "benchmarks": benchmarks_used,
        "confounds_controlled": ["log_params", "release_date"],
        "r_squared_per_benchmark": dict(zip(benchmarks_used, r_squared)),
        "pca": {
            "lambda_1": pca_result["lambda_1"],
            "variance_explained_pc1": pca_result["variance_explained_pc1"],
            "eigenvalues": pca_result["eigenvalues"],
            "loadings_pc1": dict(zip(benchmarks_used, pca_result["loadings_pc1"])),
        },
        "permutation_test": {
            "n_permutations": CONFIG["n_permutations"],
            "lambda_obs": perm_result["lambda_obs"],
            "threshold_95": perm_result["threshold_95"],
            "p_value": perm_result["p_value"],
            "hypothesis_passed": perm_result["hypothesis_passed"],
        },
        "assumptions": assumptions,
        "gate_verdict": "PASS" if perm_result["hypothesis_passed"] else "FAIL",
        "success_criteria": {
            "p_value_lt_0.05": perm_result["p_value"] < 0.05,
            "lambda_exceeds_95th": perm_result["lambda_obs"] > perm_result["threshold_95"],
            "variance_explained_gt_20pct": pca_result["variance_explained_pc1"] > 0.20,
        },
    }

    # Validate output schema
    required_keys = ["hypothesis_id", "n_models", "pca", "permutation_test", "gate_verdict"]
    for key in required_keys:
        assert key in results, f"Missing required key: {key}"

    # Write results
    results_path = output_dir / CONFIG["results_filename"]
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"H-E1 GATE VERDICT: {results['gate_verdict']}")
    print("=" * 60)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0 if results["gate_verdict"] == "PASS" else 1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
