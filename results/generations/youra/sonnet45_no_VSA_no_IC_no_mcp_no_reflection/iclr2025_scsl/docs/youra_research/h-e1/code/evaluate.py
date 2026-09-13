"""
Evaluation and visualization for h-e1: Statistical testing and gate validation.
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt


def compute_temporal_gap(results: list[dict]) -> dict:
    """
    Compute statistical metrics for temporal gap analysis.

    Returns:
        {
            'mean_delta': float,
            'std_delta': float,
            't_stat': float,
            'p_value': float,
            'n_converged': int,  # Number of seeds where both E_s and E_c converged
            'n_total': int
        }
    """
    # Extract valid pairs (where both spurious and core converged)
    E_spurious = []
    E_core = []

    for r in results:
        if r['E_spurious'] is not None and r['E_core'] is not None:
            E_spurious.append(r['E_spurious'])
            E_core.append(r['E_core'])

    if len(E_spurious) < 2:
        return {
            'mean_delta': None,
            'std_delta': None,
            't_stat': None,
            'p_value': None,
            'n_converged': len(E_spurious),
            'n_total': len(results)
        }

    # Compute deltas
    deltas = np.array(E_core) - np.array(E_spurious)

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(E_core, E_spurious)

    return {
        'mean_delta': float(np.mean(deltas)),
        'std_delta': float(np.std(deltas)),
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'n_converged': len(E_spurious),
        'n_total': len(results)
    }


def check_poc_pass(all_results: dict[str, list]) -> dict:
    """
    Validate PoC pass criteria for MUST_WORK gate.

    PoC Pass:
        1. Code runs without errors on all 4 datasets
        2. Direction check: E_s < E_c for >5/10 seeds on ALL datasets
        3. Magnitude check: mean(Δ) ≥ 2 epochs on at least 2/4 datasets

    Returns:
        {
            'poc_pass': bool,
            'direction_pass': bool,
            'magnitude_pass': bool,
            'details': dict
        }
    """
    direction_pass_count = 0
    magnitude_pass_count = 0
    details = {}

    for dataset, results in all_results.items():
        # Direction check: count E_s < E_c
        direction_correct = sum(
            1 for r in results
            if r['E_spurious'] is not None and r['E_core'] is not None
            and r['E_spurious'] < r['E_core']
        )

        # Compute mean delta
        stats_result = compute_temporal_gap(results)
        mean_delta = stats_result['mean_delta']

        dataset_direction_pass = direction_correct > 5  # >50% of 10 seeds
        dataset_magnitude_pass = mean_delta is not None and mean_delta >= 2.0

        if dataset_direction_pass:
            direction_pass_count += 1
        if dataset_magnitude_pass:
            magnitude_pass_count += 1

        details[dataset] = {
            'direction_correct_count': direction_correct,
            'direction_pass': dataset_direction_pass,
            'mean_delta': mean_delta,
            'magnitude_pass': dataset_magnitude_pass,
            'stats': stats_result
        }

    # Overall PoC pass: direction on ALL 4, magnitude on ≥2
    direction_pass = direction_pass_count == 4
    magnitude_pass = magnitude_pass_count >= 2
    poc_pass = direction_pass and magnitude_pass

    return {
        'poc_pass': poc_pass,
        'direction_pass': direction_pass,
        'magnitude_pass': magnitude_pass,
        'direction_pass_count': direction_pass_count,
        'magnitude_pass_count': magnitude_pass_count,
        'details': details
    }


def check_full_pass(all_results: dict[str, list]) -> dict:
    """
    Validate full statistical pass criteria.

    Full Pass:
        1. All datasets: p < 0.05 (paired t-test)
        2. At least 3/4 datasets: mean(Δ) ≥ 2 epochs

    Returns:
        {
            'full_pass': bool,
            'significance_pass': bool,
            'magnitude_pass': bool,
            'details': dict
        }
    """
    significance_pass_count = 0
    magnitude_pass_count = 0
    details = {}

    for dataset, results in all_results.items():
        stats_result = compute_temporal_gap(results)
        p_value = stats_result['p_value']
        mean_delta = stats_result['mean_delta']

        dataset_sig_pass = p_value is not None and p_value < 0.05
        dataset_mag_pass = mean_delta is not None and mean_delta >= 2.0

        if dataset_sig_pass:
            significance_pass_count += 1
        if dataset_mag_pass:
            magnitude_pass_count += 1

        details[dataset] = {
            'p_value': p_value,
            'significance_pass': dataset_sig_pass,
            'mean_delta': mean_delta,
            'magnitude_pass': dataset_mag_pass,
            'stats': stats_result
        }

    significance_pass = significance_pass_count == 4
    magnitude_pass = magnitude_pass_count >= 3
    full_pass = significance_pass and magnitude_pass

    return {
        'full_pass': full_pass,
        'significance_pass': significance_pass,
        'magnitude_pass': magnitude_pass,
        'significance_pass_count': significance_pass_count,
        'magnitude_pass_count': magnitude_pass_count,
        'details': details
    }


def save_results(all_results: dict[str, list], output_dir: str):
    """
    Export results to CSV and JSON.

    CSV: columns [dataset, seed, E_spurious, E_core, E_baseline, delta]
    JSON: statistical summary per dataset
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # CSV export
    csv_path = output_path / 'convergence_data.csv'
    with open(csv_path, 'w') as f:
        f.write('dataset,seed,E_spurious,E_core,E_baseline,delta\n')
        for dataset, results in all_results.items():
            for r in results:
                f.write(f"{r['dataset']},{r['seed']},{r['E_spurious']},{r['E_core']},{r['E_baseline']},{r['delta']}\n")

    # JSON summary
    stats_summary = {}
    for dataset, results in all_results.items():
        stats_summary[dataset] = compute_temporal_gap(results)

    json_path = output_path / 'stats_summary.json'
    with open(json_path, 'w') as f:
        json.dump(stats_summary, f, indent=2)

    print(f"\nResults saved:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")


def plot_convergence_comparison(all_results: dict[str, list], output_path: str):
    """
    MANDATORY: Bar chart of mean(E_s) vs mean(E_c) per dataset.

    Required for gate validation report.
    """
    datasets = list(all_results.keys())
    mean_E_spurious = []
    mean_E_core = []
    std_E_spurious = []
    std_E_core = []

    for dataset in datasets:
        results = all_results[dataset]

        E_s = [r['E_spurious'] for r in results if r['E_spurious'] is not None]
        E_c = [r['E_core'] for r in results if r['E_core'] is not None]

        mean_E_spurious.append(np.mean(E_s) if E_s else 0)
        mean_E_core.append(np.mean(E_c) if E_c else 0)
        std_E_spurious.append(np.std(E_s) if E_s else 0)
        std_E_core.append(np.std(E_c) if E_c else 0)

    x = np.arange(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, mean_E_spurious, width, yerr=std_E_spurious,
                   label='Spurious (E_s)', capsize=5)
    bars2 = ax.bar(x + width/2, mean_E_core, width, yerr=std_E_core,
                   label='Core (E_c)', capsize=5)

    ax.set_xlabel('Dataset')
    ax.set_ylabel('Convergence Epoch')
    ax.set_title('Spurious vs Core Feature Convergence')
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Figure saved: {output_path}")


def plot_temporal_gap_distribution(all_results: dict[str, list], output_path: str):
    """Histogram of Δ across all seeds/datasets."""
    all_deltas = []
    for results in all_results.values():
        deltas = [r['delta'] for r in results if r['delta'] is not None]
        all_deltas.extend(deltas)

    if not all_deltas:
        print("No valid deltas to plot")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(all_deltas, bins=15, edgecolor='black', alpha=0.7)
    ax.axvline(x=2.0, color='red', linestyle='--', linewidth=2, label='Δ=2 (threshold)')
    ax.set_xlabel('Temporal Gap (Δ = E_core - E_spurious)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Temporal Gap Across All Experiments')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Figure saved: {output_path}")
