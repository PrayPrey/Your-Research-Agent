"""Aggregate H-M3 results and compute statistics."""
import json
import numpy as np
import yaml
from pathlib import Path
from statsmodels.stats.proportion import proportion_confint, proportions_ztest


def load_results(jsonl_path: str):
    """Load JSONL results."""
    with open(jsonl_path) as f:
        return [json.loads(line) for line in f]


def compute_metrics(results):
    """Compute aggregate statistics."""
    total = len(results)
    solved = sum(1 for r in results if r['outcome'] == 'solved')
    success_rate = solved / total

    # Wilson 95% CI
    ci_lower, ci_upper = proportion_confint(solved, total, alpha=0.05, method='wilson')

    # Failure modes
    budget_exhausted = sum(1 for r in results if r['outcome'] == 'budget_exhausted')
    timeout = sum(1 for r in results if r['outcome'] == 'timeout')
    error = sum(1 for r in results if r['outcome'] == 'error')

    # Tactic consumption (solved only)
    solved_results = [r for r in results if r['outcome'] == 'solved']
    if solved_results:
        tactics_used = [r['tactics_used'] for r in solved_results]
        mean_tactics = float(np.mean(tactics_used))
        median_tactics = float(np.median(tactics_used))
        std_tactics = float(np.std(tactics_used))
        cv_tactics = std_tactics / mean_tactics if mean_tactics > 0 else 0.0
    else:
        mean_tactics = median_tactics = std_tactics = cv_tactics = 0.0

    return {
        'total': total,
        'solved': solved,
        'success_rate': success_rate,
        'ci_95': [ci_lower, ci_upper],
        'failure_modes': {
            'budget_exhausted': budget_exhausted,
            'timeout': timeout,
            'error': error
        },
        'tactic_consumption': {
            'mean': mean_tactics,
            'median': median_tactics,
            'std': std_tactics,
            'cv': cv_tactics
        }
    }


def compare_to_baseline(h_m3_metrics, h_e1_baseline):
    """Compare H-M3 to H-E1 baseline."""
    h_m3_solved = h_m3_metrics['solved']
    h_e1_solved = h_e1_baseline['solved_count']
    total = h_m3_metrics['total']  # Use actual problem count

    # Delta
    delta = h_m3_metrics['success_rate'] - h_e1_baseline['success_rate']

    # One-sided z-test (H-M3 > H-E1)
    z, p = proportions_ztest(
        [h_m3_solved, h_e1_solved],
        [total, total],
        alternative='larger'
    )

    return {
        'delta': float(delta),
        'z_statistic': float(z),
        'p_value': float(p),
        'significant': p < 0.05
    }


def stratify_by_source(results):
    """Stratify results by problem source."""
    sources = {}
    for r in results:
        src = r.get('source', 'UNKNOWN')
        if src not in sources:
            sources[src] = []
        sources[src].append(r)

    stratified = {}
    for src, src_results in sources.items():
        solved = sum(1 for r in src_results if r['outcome'] == 'solved')
        total = len(src_results)
        stratified[src] = {
            'solved': solved,
            'total': total,
            'success_rate': solved / total if total > 0 else 0.0
        }

    return stratified


def evaluate_gate(metrics, comparison):
    """Evaluate SHOULD_WORK gate criteria."""
    success_in_range = 0.18 <= metrics['success_rate'] <= 0.25
    delta_in_range = 0.03 <= comparison['delta'] <= 0.10
    significant = comparison['p_value'] < 0.05

    passed = success_in_range and delta_in_range and significant

    return {
        'success_rate_in_range': success_in_range,
        'delta_in_range': delta_in_range,
        'statistically_significant': significant,
        'overall': 'PASS' if passed else 'FAIL'
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=str, default='results/h_m3_results.jsonl')
    parser.add_argument('--output', type=str, default='results/h_m3_aggregate.yaml')
    args = parser.parse_args()

    # H-E1 baseline from verification_state.yaml
    h_e1_baseline = {
        'success_rate': 0.156,
        'solved_count': 38,
        'ci_95': [0.115, 0.203]
    }

    # Load and compute
    results = load_results(args.results)
    metrics = compute_metrics(results)
    comparison = compare_to_baseline(metrics, h_e1_baseline)
    stratified = stratify_by_source(results)
    gate = evaluate_gate(metrics, comparison)

    # Print summary
    print("\n" + "="*60)
    print("H-M3 RESULTS: Random Mathlib Tactic Sampling")
    print("="*60)
    print(f"\nSuccess Rate: {metrics['success_rate']*100:.1f}% [{metrics['ci_95'][0]*100:.1f}%, {metrics['ci_95'][1]*100:.1f}%]")
    print(f"Solved: {metrics['solved']}/{metrics['total']}")
    print(f"\nComparison to H-E1 (lean-auto):")
    print(f"  H-E1 Baseline: {h_e1_baseline['success_rate']*100:.1f}%")
    print(f"  Delta: {comparison['delta']*100:+.1f} percentage points")
    print(f"  Z-statistic: {comparison['z_statistic']:.2f}")
    print(f"  P-value: {comparison['p_value']:.4f}")
    print(f"  Significant (p<0.05): {comparison['significant']}")
    print(f"\nGate Evaluation (SHOULD_WORK):")
    print(f"  Success rate ∈ [18%, 25%]: {gate['success_rate_in_range']}")
    print(f"  Delta ∈ [3%, 10%]: {gate['delta_in_range']}")
    print(f"  Statistically significant: {gate['statistically_significant']}")
    print(f"  Overall Gate: {gate['overall']}")
    print(f"\nFailure Modes:")
    print(f"  Budget exhausted: {metrics['failure_modes']['budget_exhausted']} ({metrics['failure_modes']['budget_exhausted']/metrics['total']*100:.1f}%)")
    print(f"  Timeout: {metrics['failure_modes']['timeout']} ({metrics['failure_modes']['timeout']/metrics['total']*100:.1f}%)")
    print(f"  Error: {metrics['failure_modes']['error']} ({metrics['failure_modes']['error']/metrics['total']*100:.1f}%)")

    if metrics['solved'] > 0:
        print(f"\nTactic Consumption (solved problems):")
        print(f"  Mean: {metrics['tactic_consumption']['mean']:.1f}")
        print(f"  Median: {metrics['tactic_consumption']['median']:.1f}")
        print(f"  Std: {metrics['tactic_consumption']['std']:.1f}")
        print(f"  CV: {metrics['tactic_consumption']['cv']:.2f}")

    if stratified:
        print(f"\nStratification by Source:")
        for src, data in sorted(stratified.items()):
            print(f"  {src}: {data['success_rate']*100:.1f}% ({data['solved']}/{data['total']})")

    # Write YAML
    aggregate_data = {
        'h_m3_results': metrics,
        'comparison': comparison,
        'gate_evaluation': gate,
        'stratification': stratified,
        'h_e1_baseline': h_e1_baseline
    }

    with open(args.output, 'w') as f:
        yaml.dump(aggregate_data, f, default_flow_style=False)

    print(f"\nAggregate statistics written to {args.output}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
