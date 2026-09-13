"""Orchestration: multi-condition experiment execution"""
from pathlib import Path
from typing import Dict
import json
import sys
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, ExperimentConfig
from train import train_model
from evaluate import evaluate_model, dose_response_test
from visualize import (
    plot_dose_response_curve,
    plot_per_digit_heatmap,
    plot_degradation_bars,
    plot_gate_metrics
)
from data import get_dataloaders


def run_single_condition(
    config: ExperimentConfig,
    flip_prob: float
) -> Dict:
    """Run training for single flip probability condition (5 seeds).

    Args:
        config: Experiment configuration
        flip_prob: Flip probability (0.0, 0.3, 0.5, 0.9)

    Returns:
        results dict for this condition
    """
    seed_results = []
    asymmetric_accs = []

    device = config.training.device if torch.cuda.is_available() else "cpu"

    for seed in config.training.seeds:
        print(f"  Training: flip_prob={flip_prob}, seed={seed}")

        # Train model
        model, train_result = train_model(config, flip_prob, seed)

        # Evaluate on test set
        _, test_loader = get_dataloaders(config.data, flip_prob=0.0)  # No augmentation for test
        eval_results = evaluate_model(
            model, test_loader, device,
            asymmetric_digits=config.evaluation.asymmetric_digits
        )

        seed_results.append({
            "seed": seed,
            "best_epoch": train_result["best_epoch"],
            "overall_accuracy": eval_results["overall_accuracy"],
            "asymmetric_accuracy": eval_results["asymmetric_accuracy"],
            "per_digit_accuracy": eval_results["per_digit_accuracy"]
        })

        asymmetric_accs.append(eval_results["asymmetric_accuracy"])

    return {
        "flip_prob": flip_prob,
        "seed_results": seed_results,
        "mean_asymmetric_acc": float(sum(asymmetric_accs) / len(asymmetric_accs)),
        "std_asymmetric_acc": float((sum((x - sum(asymmetric_accs)/len(asymmetric_accs))**2 for x in asymmetric_accs) / len(asymmetric_accs))**0.5),
        "mean_overall_acc": float(sum(r["overall_accuracy"] for r in seed_results) / len(seed_results))
    }


def run_all_conditions(
    config: ExperimentConfig
) -> Dict:
    """Run all flip probability conditions (4 conditions × 5 seeds = 20 runs).

    Args:
        config: Experiment configuration

    Returns:
        all_results dict with gate status
    """
    all_results = {
        "conditions": {},
        "hypothesis_id": config.hypothesis_id
    }

    # Run all conditions
    for flip_prob in config.data.flip_probabilities:
        print(f"\nRunning condition: flip_prob={flip_prob}")
        condition_result = run_single_condition(config, flip_prob)
        all_results["conditions"][flip_prob] = condition_result

    # Prepare data for dose-response test
    dose_response_data = {
        p: [r["asymmetric_accuracy"] for r in all_results["conditions"][p]["seed_results"]]
        for p in config.data.flip_probabilities
    }

    # Statistical test
    dose_response_result = dose_response_test(
        dose_response_data,
        alpha=config.evaluation.alpha
    )

    all_results["spearman_rho"] = dose_response_result["spearman_rho"]
    all_results["spearman_p"] = dose_response_result["spearman_p"]
    all_results["gate_status"] = dose_response_result["gate_status"]

    return all_results


def save_results(
    results: Dict,
    output_dir: Path
) -> None:
    """Save results to JSON file.

    Args:
        results: Results from run_all_conditions
        output_dir: Output directory
    """
    results_file = output_dir / "results" / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")


def generate_visualizations(
    results: Dict,
    config: ExperimentConfig
) -> None:
    """Generate all required visualizations.

    Args:
        results: Results from run_all_conditions
        config: Experiment configuration
    """
    print("\nGenerating visualizations...")

    # Prepare data
    dose_response_data = {
        p: [r["asymmetric_accuracy"] for r in results["conditions"][p]["seed_results"]]
        for p in config.data.flip_probabilities
    }

    per_digit_data = {
        p: {
            digit: sum(r["per_digit_accuracy"][digit] for r in results["conditions"][p]["seed_results"]) / len(results["conditions"][p]["seed_results"])
            for digit in range(10)
        }
        for p in config.data.flip_probabilities
    }

    # 1. Dose-response curve
    plot_dose_response_curve(
        dose_response_data,
        config.figures_dir / config.visualization.dose_response_filename,
        config.visualization
    )

    # 2. Per-digit heatmap
    plot_per_digit_heatmap(
        per_digit_data,
        config.figures_dir / config.visualization.heatmap_filename,
        config.visualization
    )

    # 3. Degradation bars
    plot_degradation_bars(
        dose_response_data,
        config.figures_dir / config.visualization.degradation_filename,
        config.visualization
    )

    # 4. Gate metrics
    plot_gate_metrics(
        target_rho=config.evaluation.gate_rho_threshold,
        target_p=config.evaluation.gate_p_threshold,
        actual_rho=results["spearman_rho"],
        actual_p=results["spearman_p"],
        gate_status=results["gate_status"],
        output_path=config.figures_dir / config.visualization.gate_metrics_filename,
        config=config.visualization
    )

    print(f"Visualizations saved to: {config.figures_dir}")


def main() -> None:
    """Main entry point: load config, run experiments, save results."""
    print("="*60)
    print("H-M1 Dose-Response Experiment")
    print("="*60)

    # Load config
    config = get_config()

    print(f"\nExperiment Configuration:")
    print(f"  Flip probabilities: {config.data.flip_probabilities}")
    print(f"  Seeds: {config.training.seeds}")
    print(f"  Total runs: {len(config.data.flip_probabilities) * len(config.training.seeds)}")
    print(f"  Output directory: {config.output_root}")

    # Run all conditions
    all_results = run_all_conditions(config)

    # Save results
    save_results(all_results, config.output_root)

    # Generate visualizations
    generate_visualizations(all_results, config)

    # Print summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Gate Status: {all_results['gate_status']}")
    print(f"Spearman ρ: {all_results['spearman_rho']:.4f}")
    print(f"Spearman p-value: {all_results['spearman_p']:.4f}")
    print("\nMean Asymmetric Accuracies:")
    for flip_prob in config.data.flip_probabilities:
        mean_acc = all_results['conditions'][flip_prob]['mean_asymmetric_acc']
        std_acc = all_results['conditions'][flip_prob]['std_asymmetric_acc']
        print(f"  p={flip_prob}: {mean_acc:.4f} ± {std_acc:.4f}")
    print("="*60)


if __name__ == "__main__":
    main()
