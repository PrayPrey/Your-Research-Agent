"""Main analysis orchestrator for H-M2."""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from config import AnalysisConfig, get_default_config
from data_loader import get_dataloader
from trainer import train_condition
from artifact_loader import (
    verify_all_artifacts_exist,
    load_final_weights,
    load_loss_trajectories
)
from trajectory_analyzer import (
    analyze_weight_divergence,
    calculate_loss_cv
)
from visualize import plot_gate_metrics_comparison


def run_training_phase(config: AnalysisConfig) -> None:
    """Generate training data for all conditions."""
    print("\n" + "="*60)
    print("PHASE 1: Training Data Generation")
    print("="*60)

    for architecture in config.training.architectures:
        for dataset in config.training.datasets:
            # Get dataloader
            train_loader = get_dataloader(
                dataset_name=dataset,
                data_root=config.data_cache,
                batch_size=config.training.batch_size,
                train=True
            )

            # Train all seeds for this condition
            train_condition(
                architecture=architecture,
                dataset=dataset,
                train_loader=train_loader,
                n_seeds=config.training.n_seeds,
                n_epochs=config.training.n_epochs,
                learning_rate=config.training.learning_rate,
                momentum=config.training.momentum,
                device=config.training.device,
                save_dir=config.output_dir
            )

    print("\n✓ Training phase complete")


def run_single_condition_analysis(
    condition: str,
    config: AnalysisConfig
) -> Dict[str, float]:
    """
    Run analysis for one condition.

    Returns:
        Dict with keys: mean_final_distance, final_distance_p_value,
                       final_distance_t_stat, cv_final_loss_percent,
                       test1_passed, test2_passed, n_seeds, n_params
    """
    # Load artifacts
    final_weights = load_final_weights(
        config.output_dir, condition, config.training.n_seeds
    )
    loss_trajectories = load_loss_trajectories(
        config.output_dir, condition, config.training.n_seeds
    )

    # Compute metrics
    weight_stats = analyze_weight_divergence(final_weights)
    cv = calculate_loss_cv(loss_trajectories)

    # Test pass/fail
    test1_passed = (
        weight_stats['p_value'] < config.primary_alpha and
        weight_stats['mean_distance'] > 0
    )
    test2_passed = cv >= config.secondary_cv_threshold

    return {
        'mean_final_distance': weight_stats['mean_distance'],
        'final_distance_p_value': weight_stats['p_value'],
        'final_distance_t_stat': weight_stats['t_statistic'],
        'cv_final_loss_percent': cv,
        'test1_passed': test1_passed,
        'test2_passed': test2_passed,
        'distances': weight_stats['distances'],
        'loss_trajectories': loss_trajectories,
        'n_seeds': config.training.n_seeds,
        'n_params': len(final_weights[0])
    }


def run_all_conditions(config: AnalysisConfig) -> Dict[str, Dict]:
    """Run analysis for all 4 conditions."""
    print("\n" + "="*60)
    print("PHASE 2: Trajectory Divergence Analysis")
    print("="*60)

    results = {}
    for condition in config.training.conditions:
        print(f"\nAnalyzing: {condition}")
        results[condition] = run_single_condition_analysis(condition, config)
        print(f"  Mean distance: {results[condition]['mean_final_distance']:.4f}")
        print(f"  P-value: {results[condition]['final_distance_p_value']:.2e}")
        print(f"  CV final: {results[condition]['cv_final_loss_percent']:.2f}%")
        print(f"  Test 1 (distance): {'PASS' if results[condition]['test1_passed'] else 'FAIL'}")
        print(f"  Test 2 (CV): {'PASS' if results[condition]['test2_passed'] else 'FAIL'}")

    return results


def validate_gate(results: Dict[str, Dict]) -> Tuple[bool, str]:
    """
    Determine MUST_WORK gate pass/fail.

    Primary: ALL 4 conditions p < 0.05 and mean_distance > 0
    Secondary: ≥2/4 conditions CV ≥ 1%

    Returns:
        (gate_passed: bool, summary: str)
    """
    # Primary criterion: ALL 4 conditions
    test1_count = sum(r['test1_passed'] for r in results.values())
    primary_pass = (test1_count == 4)

    # Secondary criterion: ≥2/4 conditions
    test2_count = sum(r['test2_passed'] for r in results.values())
    secondary_pass = (test2_count >= 2)

    # MUST_WORK requires primary only
    gate_passed = primary_pass

    summary = (
        f"Primary: {test1_count}/4 conditions passed\n"
        f"Secondary: {test2_count}/4 conditions passed\n"
        f"Gate: {'PASS' if gate_passed else 'FAIL'}"
    )

    return gate_passed, summary


def save_results(
    results: Dict[str, Dict],
    gate_passed: bool,
    gate_summary: str,
    config: AnalysisConfig
) -> None:
    """Save analysis results to JSON."""
    # Prepare serializable results (remove numpy arrays)
    serializable_results = {}
    for condition, result in results.items():
        serializable_results[condition] = {
            'mean_final_distance': result['mean_final_distance'],
            'final_distance_p_value': result['final_distance_p_value'],
            'final_distance_t_stat': result['final_distance_t_stat'],
            'cv_final_loss_percent': result['cv_final_loss_percent'],
            'test1_passed': result['test1_passed'],
            'test2_passed': result['test2_passed'],
            'n_seeds': result['n_seeds'],
            'n_params': result['n_params']
        }

    # Save analysis results
    with open(config.output_dir / "analysis_results.json", 'w') as f:
        json.dump(serializable_results, f, indent=2)

    # Save gate validation
    gate_data = {
        'gate_passed': gate_passed,
        'summary': gate_summary,
        'conditions': serializable_results
    }
    with open(config.output_dir / "gate_validation.json", 'w') as f:
        json.dump(gate_data, f, indent=2)

    print(f"\n✓ Results saved to: {config.output_dir}")


def generate_validation_report(
    results: Dict[str, Dict],
    gate_passed: bool,
    gate_summary: str,
    config: AnalysisConfig
) -> None:
    """Generate human-readable validation report."""
    report_path = config.output_dir.parent / "04_validation.md"

    with open(report_path, 'w') as f:
        f.write("# H-M2 Validation Report: Trajectory Divergence\n\n")
        f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Gate Type:** MUST_WORK\n")
        f.write(f"**Gate Result:** {'PASS ✓' if gate_passed else 'FAIL ✗'}\n\n")

        f.write("## Gate Validation Summary\n\n")
        f.write(f"```\n{gate_summary}\n```\n\n")

        f.write("## Per-Condition Results\n\n")
        for condition, result in results.items():
            f.write(f"### {condition}\n\n")
            f.write(f"- **Mean Final Distance:** {result['mean_final_distance']:.4f}\n")
            f.write(f"- **P-value:** {result['final_distance_p_value']:.2e}\n")
            f.write(f"- **T-statistic:** {result['final_distance_t_stat']:.2f}\n")
            f.write(f"- **CV Final Loss:** {result['cv_final_loss_percent']:.2f}%\n")
            f.write(f"- **Test 1 (Distance):** {'PASS ✓' if result['test1_passed'] else 'FAIL ✗'}\n")
            f.write(f"- **Test 2 (CV):** {'PASS ✓' if result['test2_passed'] else 'FAIL ✗'}\n")
            f.write(f"- **Seeds:** {result['n_seeds']}\n")
            f.write(f"- **Parameters:** {result['n_params']}\n\n")

        f.write("## Key Findings\n\n")
        if gate_passed:
            f.write("- All 4 conditions show significant final weight divergence (p < 0.05)\n")
            f.write("- Different initial weights lead to different optimization trajectories\n")
            f.write("- Mechanism validated: SGD converges to different local minima\n")
        else:
            f.write("- Gate FAILED: Not all conditions show significant divergence\n")
            f.write("- Review conditions that failed Test 1\n")

    print(f"✓ Validation report saved: {report_path}")


def main():
    """Main entry point."""
    # Get configuration
    config = get_default_config()

    # Set absolute paths
    base_dir = Path(__file__).parent.parent
    config.output_dir = base_dir / "results"
    config.figures_dir = base_dir / "figures"
    config.data_cache = base_dir.parent.parent.parent / ".data_cache"

    print("\n" + "="*60)
    print("H-M2: Trajectory Divergence Analysis")
    print("="*60)
    print(f"Output dir: {config.output_dir}")
    print(f"Figures dir: {config.figures_dir}")
    print(f"Conditions: {config.training.conditions}")
    print(f"Seeds per condition: {config.training.n_seeds}")
    print(f"Epochs: {config.training.n_epochs}")

    # Phase 1: Check if training data exists, otherwise train
    all_exist, missing = verify_all_artifacts_exist(
        config.output_dir,
        config.training.conditions,
        config.training.n_seeds
    )

    if not all_exist:
        print(f"\nMissing {len(missing)} artifact files - running training phase...")
        run_training_phase(config)
    else:
        print("\n✓ All training artifacts exist - skipping training")

    # Phase 2: Analysis
    results = run_all_conditions(config)

    # Phase 3: Gate validation
    print("\n" + "="*60)
    print("PHASE 3: Gate Validation")
    print("="*60)
    gate_passed, gate_summary = validate_gate(results)
    print(f"\n{gate_summary}")

    # Phase 4: Visualization
    print("\n" + "="*60)
    print("PHASE 4: Visualization")
    print("="*60)
    plot_gate_metrics_comparison(results, config.figures_dir / "gate_metrics_comparison.png")

    # Phase 5: Save results
    print("\n" + "="*60)
    print("PHASE 5: Save Results")
    print("="*60)
    save_results(results, gate_passed, gate_summary, config)
    generate_validation_report(results, gate_passed, gate_summary, config)

    print("\n" + "="*60)
    print(f"H-M2 Analysis Complete: {'PASS ✓' if gate_passed else 'FAIL ✗'}")
    print("="*60)


if __name__ == "__main__":
    main()
