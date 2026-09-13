"""Analysis pipeline for invalid beam pruning results."""

import numpy as np
import json
import csv
import os


def analyze_reduction_rates(tracking_results: dict) -> dict:
    """Compute reduction rate statistics."""
    rates = [e['reduction_rate'] for e in tracking_results['experiments']]
    mean_rate = float(np.mean(rates))
    median_rate = float(np.median(rates))

    return {
        'mean': mean_rate,
        'median': median_rate,
        'gate_pass': mean_rate >= 0.50
    }


def analyze_final_validity(tracking_results: dict) -> dict:
    """Compute final validity statistics."""
    k = 5
    proportions = [e['final_valid_count'] / k for e in tracking_results['experiments']]
    mean_prop = float(np.mean(proportions))

    return {
        'mean_valid_proportion': mean_prop,
        'gate_pass': mean_prop >= 0.60
    }


def compare_baseline(combined_results: dict, pure_results: dict) -> dict:
    """Compare combined scoring vs pure log-likelihood."""
    k = 5
    combined_valid = [e['final_valid_count'] / k for e in combined_results['experiments']]
    pure_valid = [e['final_valid_count'] / k for e in pure_results['experiments']]

    combined_mean = float(np.mean(combined_valid))
    pure_mean = float(np.mean(pure_valid))

    return {
        'combined_mean_valid': combined_mean,
        'pure_mean_valid': pure_mean,
        'improvement': combined_mean - pure_mean
    }


def save_beam_validity_logs(tracking_results: dict, output_path: str):
    """Save per-step beam validity logs to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['problem_id', 'step', 'invalid_count', 'invalid_proportion'])
        for exp in tracking_results['experiments']:
            for log in exp['temporal_log']:
                writer.writerow([
                    exp['problem_id'],
                    log['step'],
                    log['invalid_count'],
                    log['invalid_proportion']
                ])


def save_reduction_rates(tracking_results: dict, output_path: str):
    """Save reduction rate analysis to JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    analysis = analyze_reduction_rates(tracking_results)
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)


def save_final_validity(tracking_results: dict, output_path: str):
    """Save final validity analysis to JSON."""
    from experiments import experiment_b_final_validity
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    analysis = experiment_b_final_validity(tracking_results)
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)


def save_temporal_dynamics(tracking_results: dict, output_path: str):
    """Save temporal dynamics analysis to JSON."""
    from experiments import experiment_c_temporal_dynamics
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    analysis = experiment_c_temporal_dynamics(tracking_results)
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)


def save_baseline_comparison(combined_results: dict, pure_results: dict, output_path: str):
    """Save baseline comparison to JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    comparison = compare_baseline(combined_results, pure_results)
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)
