"""Main pipeline for H-E1 Cross-Benchmark Factor Analysis."""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fa_config import get_default_config
from benchmark_loader import BenchmarkLoader
from fa_preprocessor import DataPreprocessor
from fa_analyzer import CrossBenchmarkFactorAnalyzer
from fa_visualizer import FactorVisualizer


def main() -> dict:
    """
    Run full factor analysis pipeline.

    Returns:
        dict: Results including gate status and metrics
    """
    print("="*80)
    print("H-E1: Cross-Benchmark Truthfulness Factor Analysis")
    print("="*80)

    # Load configuration
    config = get_default_config()
    print(f"\nHypothesis: {config.hypothesis_id}")
    print(f"Random seed: {config.factor_analysis.random_state}")

    # Create output directories
    os.makedirs(config.export.data_dir, exist_ok=True)
    os.makedirs(config.export.output_dir, exist_ok=True)
    os.makedirs(config.visualization.output_dir, exist_ok=True)

    # ========================================================================
    # STEP 1: Data Loading
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 1: Data Loading")
    print("="*80)

    loader = BenchmarkLoader(config.data_sources.__dict__)
    raw_matrix = loader.build_matrix()

    # Save raw matrix
    raw_path = os.path.join(config.export.data_dir, "benchmark_matrix_raw.csv")
    raw_matrix.to_csv(raw_path)
    print(f"\n[Export] Saved raw matrix to {raw_path}")

    # ========================================================================
    # STEP 2: Preprocessing
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: Preprocessing")
    print("="*80)

    preprocessor = DataPreprocessor(config.preprocessing.max_missing_ratio)

    # Filter models by coverage
    filtered = preprocessor.filter_models(raw_matrix)

    # Handle missing data
    imputed = preprocessor.handle_missing(filtered)

    # Standardize
    X_scaled, matrix_unstd = preprocessor.standardize(imputed)

    # Save preprocessed matrix
    preprocessed_df = pd.DataFrame(
        X_scaled,
        index=filtered.index,
        columns=filtered.columns
    )
    preprocessed_path = os.path.join(config.export.data_dir, "benchmark_matrix_preprocessed.csv")
    preprocessed_df.to_csv(preprocessed_path)
    print(f"\n[Export] Saved preprocessed matrix to {preprocessed_path}")

    # ========================================================================
    # STEP 3: Factor Analysis
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 3: Factor Analysis")
    print("="*80)

    analyzer = CrossBenchmarkFactorAnalyzer(config.factor_analysis.random_state)

    # Determine number of factors (Kaiser criterion)
    n_factors = analyzer.determine_n_factors(X_scaled)

    # Fit factor analysis
    analyzer.fit(X_scaled, n_factors)

    # Extract results
    loadings = analyzer.extract_loadings()
    scores = analyzer.compute_scores()
    prop_var, cumulative_var = analyzer.explained_variance()

    # Save loadings
    loadings_df = pd.DataFrame(
        loadings,
        index=filtered.columns,
        columns=[f'Factor_{i+1}' for i in range(n_factors)]
    )
    loadings_path = os.path.join(config.export.output_dir, "factor_loadings.csv")
    loadings_df.to_csv(loadings_path)
    print(f"\n[Export] Saved factor loadings to {loadings_path}")

    # Save factor scores
    scores_df = pd.DataFrame(
        scores,
        index=filtered.index,
        columns=[f'Factor_{i+1}' for i in range(n_factors)]
    )
    scores_path = os.path.join(config.export.output_dir, "factor_scores.csv")
    scores_df.to_csv(scores_path)
    print(f"\n[Export] Saved factor scores to {scores_path}")

    # Save explained variance
    variance_df = pd.DataFrame({
        'Factor': [f'Factor_{i+1}' for i in range(n_factors)],
        'Eigenvalue': analyzer.eigenvalues[:n_factors],
        'Proportion_Variance': prop_var,
        'Cumulative_Variance': cumulative_var
    })
    variance_path = os.path.join(config.export.output_dir, "explained_variance.csv")
    variance_df.to_csv(variance_path, index=False)
    print(f"[Export] Saved explained variance to {variance_path}")

    # ========================================================================
    # STEP 4: Gate Check
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 4: Gate Check (MUST_WORK)")
    print("="*80)

    # Gate conditions:
    # 1. Cumulative variance >= 70%
    # 2. n_factors in {2, 3}
    # 3. All eigenvalues > 1.0

    condition_1 = cumulative_var[-1] >= config.validation.cumulative_var_threshold
    condition_2 = n_factors in range(
        config.factor_analysis.expected_n_factors[0],
        config.factor_analysis.expected_n_factors[1] + 1
    )
    condition_3 = all(analyzer.eigenvalues[:n_factors] > config.factor_analysis.kaiser_threshold)

    gate_passed = condition_1 and condition_2 and condition_3

    print(f"\n[Gate Check] Condition 1 - Cumulative variance >= 70%: {condition_1}")
    print(f"             Actual: {cumulative_var[-1]:.2%}")
    print(f"\n[Gate Check] Condition 2 - n_factors in {{2, 3}}: {condition_2}")
    print(f"             Actual: {n_factors}")
    print(f"\n[Gate Check] Condition 3 - All eigenvalues > 1.0: {condition_3}")
    print(f"             Actual: {analyzer.eigenvalues[:n_factors]}")

    print(f"\n{'='*80}")
    print(f"GATE STATUS: {'PASSED ✓' if gate_passed else 'FAILED ✗'}")
    print(f"{'='*80}")

    # Save gate check results
    gate_results = {
        "hypothesis_id": config.hypothesis_id,
        "timestamp": datetime.now().isoformat(),
        "gate_type": "MUST_WORK",
        "gate_passed": bool(gate_passed),
        "conditions": {
            "cumulative_variance_threshold": config.validation.cumulative_var_threshold,
            "cumulative_variance_actual": float(cumulative_var[-1]),
            "condition_1_passed": bool(condition_1),
            "expected_n_factors": list(config.factor_analysis.expected_n_factors),
            "n_factors_actual": int(n_factors),
            "condition_2_passed": bool(condition_2),
            "kaiser_threshold": config.factor_analysis.kaiser_threshold,
            "eigenvalues_actual": analyzer.eigenvalues[:n_factors].tolist(),
            "condition_3_passed": bool(condition_3)
        },
        "metrics": {
            "n_factors": int(n_factors),
            "eigenvalues": analyzer.eigenvalues.tolist(),
            "variance_per_factor": prop_var.tolist(),
            "cumulative_variance": cumulative_var.tolist(),
            "total_variance_explained": float(cumulative_var[-1])
        },
        "data": {
            "n_models": int(X_scaled.shape[0]),
            "n_benchmarks": int(X_scaled.shape[1]),
            "missing_data_imputed": bool(raw_matrix.isna().sum().sum() > 0)
        }
    }

    gate_path = os.path.join(config.export.output_dir, "gate_check.json")
    with open(gate_path, 'w') as f:
        json.dump(gate_results, f, indent=config.export.json_indent)
    print(f"\n[Export] Saved gate check results to {gate_path}")

    # ========================================================================
    # STEP 5: Visualization
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 5: Visualization")
    print("="*80)

    visualizer = FactorVisualizer(config.visualization.output_dir)

    # Required figures
    visualizer.plot_scree(analyzer.eigenvalues, config.factor_analysis.kaiser_threshold)
    visualizer.plot_loadings_heatmap(
        loadings,
        filtered.columns.tolist(),
        config.visualization.loading_threshold
    )
    visualizer.plot_cumulative_variance(cumulative_var, config.validation.cumulative_var_threshold)
    visualizer.plot_gate_metrics(
        config.validation.cumulative_var_threshold,
        cumulative_var[-1],
        gate_passed
    )

    # Optional: Factor scores scatter
    if n_factors >= 2:
        visualizer.plot_factor_scores(scores, filtered.index.tolist())

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*80)
    print("EXPERIMENT SUMMARY")
    print("="*80)
    print(f"\nGate Status: {'PASSED ✓' if gate_passed else 'FAILED ✗'}")
    print(f"Number of Factors: {n_factors}")
    print(f"Cumulative Variance Explained: {cumulative_var[-1]:.2%}")
    print(f"Models Analyzed: {X_scaled.shape[0]}")
    print(f"Benchmarks: {X_scaled.shape[1]}")
    print(f"\nVariance per Factor:")
    for i, (ev, pv, cv) in enumerate(zip(analyzer.eigenvalues[:n_factors], prop_var, cumulative_var)):
        print(f"  Factor {i+1}: Eigenvalue={ev:.3f}, Variance={pv:.2%}, Cumulative={cv:.2%}")

    print(f"\nOutputs saved to:")
    print(f"  Data: {config.export.data_dir}")
    print(f"  Results: {config.export.output_dir}")
    print(f"  Figures: {config.visualization.output_dir}")

    return gate_results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_passed"] else 1)
