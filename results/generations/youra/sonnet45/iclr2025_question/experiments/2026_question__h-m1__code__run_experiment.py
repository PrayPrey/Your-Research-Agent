"""Main Experiment Runner for H-M1 Seed Independence."""

import os
import sys
import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict
from datetime import datetime

# Add current directory to path to ensure local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import local modules
import config as cfg
import seed_tester
import statistics as stats_module
import viz_h_m1 as viz

ExperimentConfig = cfg.ExperimentConfig
DeterminismConfig = cfg.DeterminismConfig
get_default_config = cfg.get_default_config
run_seed_independence_test = seed_tester.run_seed_independence_test
compute_all_statistics = stats_module.compute_all_statistics
plot_distance_distribution = viz.plot_distance_distribution
plot_distance_heatmap = viz.plot_distance_heatmap
plot_condition_comparison = viz.plot_condition_comparison
plot_gate_metrics = viz.plot_gate_metrics


def run_single_condition(
    architecture: str,
    dataset: str,
    config: ExperimentConfig
) -> Dict[str, float]:
    """
    Run seed independence test for single condition.

    Args:
        architecture: '1layer' or '2layer'
        dataset: 'mnist' or 'fashion_mnist'
        config: Experiment configuration

    Returns:
        Dictionary with statistics and distances
    """
    condition_name = f"{architecture}_{dataset}"
    print(f"\n{'='*60}")
    print(f"Running condition: {condition_name}")
    print(f"{'='*60}")

    # Initialize models with different seeds
    print(f"Initializing {len(config.seeds)} models with seeds {config.seeds[0]}-{config.seeds[-1]}...")
    models_dict = run_seed_independence_test(architecture, config.seeds, config.device)

    # Compute statistics
    print(f"Computing pairwise distances ({len(config.seeds)} choose 2 = {len(config.seeds)*(len(config.seeds)-1)//2} pairs)...")
    stats = compute_all_statistics(models_dict)

    # Print results
    print(f"\nResults:")
    print(f"  Mean distance: {stats['mean_distance']:.4f}")
    print(f"  Std distance:  {stats['std_distance']:.4f}")
    print(f"  t-statistic:   {stats['t_statistic']:.4f}")
    print(f"  p-value:       {stats['p_value']:.6f}")
    print(f"  n_pairs:       {stats['n_pairs']}")

    # Gate check
    gate_pass = stats['p_value'] < 0.05
    print(f"\n  Gate Check (p < 0.05): {'PASS ✓' if gate_pass else 'FAIL ✗'}")

    # Save results
    results_dir = Path(config.output_dir)
    np.save(results_dir / f"pairwise_distances_{condition_name}.npy", stats['distances'])

    stats_to_save = {k: v for k, v in stats.items() if k != 'distances'}  # Exclude array
    with open(results_dir / f"statistics_{condition_name}.json", 'w') as f:
        json.dump(stats_to_save, f, indent=2)

    # Generate visualizations
    figures_dir = Path(config.figures_dir)
    print(f"\nGenerating visualizations...")
    plot_distance_distribution(
        stats['distances'],
        condition_name,
        figures_dir / f"distance_distribution_{condition_name}.png",
        mean_dist=stats['mean_distance'],
        p_value=stats['p_value']
    )
    plot_distance_heatmap(
        models_dict,
        condition_name,
        figures_dir / f"distance_heatmap_{condition_name}.png"
    )
    print(f"  Saved distribution and heatmap figures")

    return stats


def run_all_conditions(config: ExperimentConfig) -> Dict[str, Dict[str, float]]:
    """
    Execute seed independence test across all 4 conditions.

    Args:
        config: Experiment configuration

    Returns:
        Dictionary mapping condition -> results
    """
    all_results = {}

    for architecture in config.architectures:
        for dataset in config.datasets:
            condition_name = f"{architecture}_{dataset}"
            stats = run_single_condition(architecture, dataset, config)
            all_results[condition_name] = stats

    return all_results


def validate_gate(all_results: Dict[str, Dict[str, float]], alpha: float = 0.05) -> Dict:
    """
    Validate MUST_WORK gate: all conditions must have p < 0.05.

    Args:
        all_results: Dictionary mapping condition -> results
        alpha: Significance threshold

    Returns:
        Gate validation result dictionary
    """
    gate_results = {}

    for condition, stats in all_results.items():
        gate_results[condition] = {
            'p_value': stats['p_value'],
            'pass': stats['p_value'] < alpha
        }

    overall_pass = all(result['pass'] for result in gate_results.values())

    return {
        'overall_pass': overall_pass,
        'alpha': alpha,
        'conditions': gate_results,
        'n_conditions_pass': sum(1 for r in gate_results.values() if r['pass']),
        'n_conditions_total': len(gate_results)
    }


def save_results(
    all_results: Dict[str, Dict[str, float]],
    gate_result: Dict,
    output_dir: Path
) -> None:
    """
    Save aggregated results and gate validation.

    Args:
        all_results: All condition results
        gate_result: Gate validation result
        output_dir: Output directory
    """
    # Save gate result
    with open(output_dir / "gate_result.json", 'w') as f:
        json.dump(gate_result, f, indent=2)

    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'gate_result': gate_result,
        'conditions': {}
    }

    for condition, stats in all_results.items():
        summary['conditions'][condition] = {
            'mean_distance': stats['mean_distance'],
            'std_distance': stats['std_distance'],
            't_statistic': stats['t_statistic'],
            'p_value': stats['p_value'],
            'n_pairs': stats['n_pairs']
        }

    with open(output_dir / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)


def generate_validation_report(
    all_results: Dict[str, Dict[str, float]],
    gate_result: Dict,
    config: ExperimentConfig
) -> None:
    """
    Generate 04_validation.md report.

    Args:
        all_results: All condition results
        gate_result: Gate validation result
        config: Experiment configuration
    """
    output_path = Path(__file__).parent.parent / "04_validation.md"

    with open(output_path, 'w') as f:
        f.write("# Validation Report: H-M1 Seed Independence\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**Hypothesis:** Random seed initialization creates independent training runs without cross-run contamination.\n\n")
        f.write("**Gate Type:** MUST_WORK\n\n")
        f.write("---\n\n")

        # Success criteria
        f.write("## Success Criteria\n\n")
        f.write("**Primary:** Mean pairwise weight distance > 0 with p < 0.05 for all 4 conditions (2 architectures × 2 datasets)\n\n")

        # Experimental setup
        f.write("## Experimental Setup\n\n")
        f.write(f"- **Seeds Tested:** {len(config.seeds)} (seeds {config.seeds[0]}-{config.seeds[-1]})\n")
        f.write(f"- **Architectures:** {', '.join(config.architectures)}\n")
        f.write(f"- **Datasets:** {', '.join(config.datasets)}\n")
        f.write(f"- **Pairwise Comparisons per Condition:** {len(config.seeds) * (len(config.seeds) - 1) // 2}\n")
        f.write(f"- **Total Conditions:** {len(all_results)}\n")
        f.write(f"- **Device:** {config.device}\n\n")

        # Results per condition
        f.write("## Results by Condition\n\n")

        for condition in sorted(all_results.keys()):
            stats = all_results[condition]
            gate_pass = gate_result['conditions'][condition]['pass']

            f.write(f"### {condition}\n\n")
            f.write(f"- **Mean Pairwise Distance:** {stats['mean_distance']:.4f}\n")
            f.write(f"- **Std Pairwise Distance:** {stats['std_distance']:.4f}\n")
            f.write(f"- **t-statistic:** {stats['t_statistic']:.4f}\n")
            f.write(f"- **p-value:** {stats['p_value']:.6f}\n")
            f.write(f"- **n_pairs:** {stats['n_pairs']}\n")
            f.write(f"- **Gate Check (p < 0.05):** {'✓ PASS' if gate_pass else '✗ FAIL'}\n\n")

        # Gate validation
        f.write("## Gate Validation (MUST_WORK)\n\n")
        f.write(f"**Overall Result:** {'✓ PASS' if gate_result['overall_pass'] else '✗ FAIL'}\n\n")
        f.write(f"- **Conditions Passed:** {gate_result['n_conditions_pass']}/{gate_result['n_conditions_total']}\n")
        f.write(f"- **Significance Level (α):** {gate_result['alpha']}\n\n")

        if gate_result['overall_pass']:
            f.write("**Conclusion:** All 4 experimental conditions demonstrate statistically significant seed independence ")
            f.write("(p < 0.05), validating that PyTorch's random seed initialization creates truly independent weight ")
            f.write("configurations across different seeds. The MUST_WORK gate is satisfied.\n\n")
        else:
            failed_conditions = [c for c, r in gate_result['conditions'].items() if not r['pass']]
            f.write(f"**Conclusion:** Gate FAILED. {len(failed_conditions)} condition(s) did not achieve p < 0.05:\n")
            for cond in failed_conditions:
                f.write(f"- {cond}: p = {gate_result['conditions'][cond]['p_value']:.6f}\n")
            f.write("\n")

        # Figures
        f.write("## Visualizations\n\n")
        f.write("### Gate Metrics Comparison\n\n")
        f.write("![Gate Metrics](figures/gate_metrics_comparison.png)\n\n")

        f.write("### Condition Comparison\n\n")
        f.write("![Condition Comparison](figures/condition_comparison.png)\n\n")

        for condition in sorted(all_results.keys()):
            f.write(f"### {condition} - Distance Distribution\n\n")
            f.write(f"![{condition} Distribution](figures/distance_distribution_{condition}.png)\n\n")

            f.write(f"### {condition} - Distance Heatmap\n\n")
            f.write(f"![{condition} Heatmap](figures/distance_heatmap_{condition}.png)\n\n")

        # Next steps
        f.write("## Next Steps\n\n")
        if gate_result['overall_pass']:
            f.write("1. Update verification_state.yaml with gate_result: PASS\n")
            f.write("2. Proceed to H-M2 (Finite Variance) hypothesis verification\n")
            f.write("3. Mark h-m1 phase_4_status: COMPLETED\n")
        else:
            f.write("1. Update verification_state.yaml with gate_result: FAIL\n")
            f.write("2. Investigate PyTorch determinism configuration\n")
            f.write("3. Route to Phase 2A for hypothesis reassessment\n")

    print(f"\nValidation report generated: {output_path}")


def main():
    """Main experiment entry point."""
    print("\n" + "="*80)
    print("H-M1 Seed Independence Experiment")
    print("="*80)

    # Load configuration
    config = get_default_config()

    # Set GPU
    if config.device == "cuda":
        gpu_id = os.environ.get('CUDA_VISIBLE_DEVICES', '0')
        print(f"\nUsing GPU: {gpu_id}")
        if not torch.cuda.is_available():
            print("WARNING: CUDA not available, falling back to CPU")
            config.device = "cpu"
    else:
        print(f"\nUsing device: {config.device}")

    # Setup determinism
    det_config = DeterminismConfig()
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = det_config.cublas_workspace_config
    torch.backends.cudnn.deterministic = det_config.cudnn_deterministic
    torch.backends.cudnn.benchmark = det_config.cudnn_benchmark
    print(f"Determinism enabled: CUDNN deterministic={det_config.cudnn_deterministic}, benchmark={det_config.cudnn_benchmark}")

    # Run all conditions
    all_results = run_all_conditions(config)

    # Generate comparison visualization
    print(f"\n{'='*60}")
    print("Generating cross-condition visualizations...")
    print(f"{'='*60}")
    figures_dir = Path(config.figures_dir)
    plot_condition_comparison(all_results, figures_dir / "condition_comparison.png")
    plot_gate_metrics(all_results, figures_dir / "gate_metrics_comparison.png")
    print("  Saved comparison figures")

    # Validate gate
    print(f"\n{'='*60}")
    print("Gate Validation")
    print(f"{'='*60}")
    gate_result = validate_gate(all_results)
    print(f"\nOverall Gate Result: {'✓ PASS' if gate_result['overall_pass'] else '✗ FAIL'}")
    print(f"Conditions Passed: {gate_result['n_conditions_pass']}/{gate_result['n_conditions_total']}")

    # Save results
    output_dir = Path(config.output_dir)
    save_results(all_results, gate_result, output_dir)
    print(f"\nResults saved to: {output_dir}")

    # Generate validation report
    generate_validation_report(all_results, gate_result, config)

    print("\n" + "="*80)
    print("Experiment Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
