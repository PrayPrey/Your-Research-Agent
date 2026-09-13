#!/usr/bin/env python3
"""
H-E1 Main Experiment Runner
Executes complete spectral analysis pipeline with REAL GitHub data.
"""
import json
import sys
import os
from datetime import datetime
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collection import load_github_data, add_confounds
from analysis import (
    ConfoundRegressor,
    SpectralAnalyzer,
    StatisticalValidator
)
from visualization import generate_all_figures

def main():
    """Run H-E1 experiment."""
    print("=" * 80)
    print("H-E1: Aspect-Dominant Structure Existence - REAL DATA Experiment")
    print("=" * 80)
    print()

    # Configuration
    N_COMMITS = 10000
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

    print(f"Configuration:")
    print(f"  Commits: {N_COMMITS}")
    print(f"  Data Directory: {DATA_DIR}")
    print(f"  Dataset: GitHub Minimal-Diff Commit Corpus (REAL)")
    print()

    # Step 1: Load REAL GitHub data
    print("Step 1: Loading real GitHub commit data...")
    try:
        commits, Y = load_github_data(
            n_commits=N_COMMITS,
            data_dir=DATA_DIR
        )
        print(f"  ✅ Loaded {len(commits)} REAL commits from GitHub")
        print(f"  Outcome matrix shape: {Y.shape}")
    except FileNotFoundError as e:
        print(f"  ❌ ERROR: Real dataset not found!")
        print()
        print(str(e))
        print()
        print("CRITICAL: This experiment REQUIRES real GitHub data.")
        print("Mock/synthetic data is NOT acceptable per 02c_experiment_brief.md")
        sys.exit(1)
    print()

    # Step 2: Extract confound features
    print("Step 2: Extracting confounding variables...")
    Y_data, X_confounds = add_confounds(Y, commits)
    print(f"  ✅ Extracted confounds (edit_size, file_entropy, repo_id)")
    print(f"  Confound matrix shape: {X_confounds.shape}")
    print()

    # Step 3: Remove confounds via regression
    print("Step 3: Removing confounds via regression...")
    regressor = ConfoundRegressor()
    Y_residual = regressor.fit(Y_data, X_confounds)
    print(f"  ✅ Computed residual matrix")
    print(f"  Residual variance: {np.var(Y_residual):.4f}")
    print()

    # Step 4: Run statistical validation
    print("Step 4: Running statistical validation...")
    validator = StatisticalValidator()

    aspect_labels = np.array([c.aspect_label for c in commits])
    repo_ids = np.array([hash(c.repo_name) % 100 for c in commits])

    results = validator.run_full_validation(Y_residual, aspect_labels, repo_ids)
    print(f"  ✅ Validation complete")
    print()

    # Step 5: Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print("Spectral Analysis:")
    print(f"  Eigenvalues: {np.array(results['spectral_analysis']['eigenvalues'])}")
    print(f"  Spectral Gap: {results['spectral_analysis']['spectral_gap']:.4f}")
    print(f"  Cross-Aspect Coupling: {results['spectral_analysis']['coupling']:.4f}")
    print()

    print("Permutation Test:")
    print(f"  p-value: {results['permutation_test']['p_value']:.4f}")
    print(f"  Significant: {results['permutation_test']['significant']}")
    print(f"  95th Percentile: {results['permutation_test']['percentile_95']:.4f}")
    print()

    print("Directional Stability:")
    print(f"  Mean Z-Score: {results['directional_stability']['mean_z_score']:.4f}")
    print(f"  Significant: {results['directional_stability']['significant']}")
    print()

    print("Cross-Validation:")
    print(f"  Mean Alignment: {results['cross_validation']['mean_alignment']:.4f}")
    print(f"  Consistent: {results['cross_validation']['consistent']}")
    print()

    print("=" * 80)
    print("GATE EVALUATION (MUST_WORK)")
    print("=" * 80)
    print()

    gate = results['gate_evaluation']
    print(f"Primary Criteria (spectral_gap > 2.0, p < 0.05, coupling ≤ 0.2):")
    print(f"  ✅ PASS" if gate['primary_criteria_pass'] else "  ❌ FAIL")
    print()
    print(f"Secondary Criteria (directional stability, CV consistency):")
    print(f"  ✅ PASS" if gate['secondary_criteria_pass'] else "  ❌ FAIL")
    print()
    print(f"Overall Gate Result:")
    print(f"  {'✅ PASS - Hypothesis VALIDATED' if gate['overall_pass'] else '❌ FAIL - Hypothesis REJECTED'}")
    print()

    # Step 6: Generate visualizations
    print("Step 5: Generating visualizations...")
    figures_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'figures')
    generate_all_figures(results, figures_dir)
    print()

    # Step 7: Save results
    print("Step 6: Saving results...")
    results_file = os.path.join(os.path.dirname(__file__), 'outputs', 'experiment_results.json')

    results['metadata'] = {
        'hypothesis_id': 'h-e1',
        'experiment_type': 'REAL_DATA',
        'dataset': 'GitHub Minimal-Diff Commit Corpus',
        'n_commits': N_COMMITS,
        'data_source': 'GitHub API (real commits)',
        'timestamp': datetime.now().isoformat()
    }

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  ✅ Results saved to: {results_file}")
    print(f"  ✅ Figures saved to: {figures_dir}/")
    print()

    # Step 8: Generate results CSV
    print("Step 7: Generating results CSV...")
    import pandas as pd

    results_csv = os.path.join(os.path.dirname(__file__), 'outputs', 'results.csv')

    df = pd.DataFrame({
        'metric': [
            'spectral_gap',
            'coupling',
            'permutation_p_value',
            'directional_z_score',
            'cv_alignment',
            'primary_criteria_pass',
            'secondary_criteria_pass',
            'overall_pass'
        ],
        'value': [
            results['spectral_analysis']['spectral_gap'],
            results['spectral_analysis']['coupling'],
            results['permutation_test']['p_value'],
            results['directional_stability']['mean_z_score'],
            results['cross_validation']['mean_alignment'],
            float(gate['primary_criteria_pass']),
            float(gate['secondary_criteria_pass']),
            float(gate['overall_pass'])
        ]
    })

    df.to_csv(results_csv, index=False)
    print(f"  ✅ CSV saved to: {results_csv}")
    print()

    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

    # Exit with appropriate code
    sys.exit(0 if gate['overall_pass'] else 1)

if __name__ == '__main__':
    main()
