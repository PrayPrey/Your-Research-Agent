"""Main experiment orchestration."""
import json
import torch
from pathlib import Path
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')
from config import OUTPUT_CONFIG, EXPERIMENT_CONFIG, TRAINING_CONFIG
from data import get_dataloaders
from train import train_condition
from evaluate import compute_per_class_accuracy, validate_gate_criteria
from visualize import plot_heatmap, plot_group_comparison, plot_dose_response


def run_all_conditions():
    """
    Execute all 5 experimental conditions.

    Returns:
        dict: {baseline: {...}, flip30: {...}, ...}
    """
    conditions = EXPERIMENT_CONFIG["conditions"]
    results = {}

    device = torch.device(TRAINING_CONFIG["device"])

    for condition in conditions:
        print(f"\n{'='*60}")
        print(f"Running condition: {condition.upper()}")
        print(f"{'='*60}")

        # Train model
        training_results = train_condition(condition)

        # Evaluate
        _, test_loader = get_dataloaders(condition, batch_size=TRAINING_CONFIG["batch_size"])
        eval_results = compute_per_class_accuracy(
            training_results["model"],
            test_loader,
            device
        )

        # Store results
        results[condition] = {
            **eval_results,
            "final_train_loss": training_results["train_losses"][-1],
            "final_test_acc": training_results["test_accs"][-1]
        }

        print(f"Overall Acc: {eval_results['overall_acc']:.2f}%")
        print(f"Symmetric Mean: {eval_results['symmetric_mean']:.2f}%")
        print(f"Asymmetric Mean: {eval_results['asymmetric_mean']:.2f}%")

    return results


def save_results(results: dict):
    """Save results and generate visualizations."""
    output_dir = Path(OUTPUT_CONFIG["output_dir"])
    figures_dir = Path(OUTPUT_CONFIG["figures_dir"])
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON results
    results_path = output_dir / OUTPUT_CONFIG["results_file"]
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Generate visualizations
    plot_heatmap(results, str(figures_dir / "heatmap.png"))
    plot_group_comparison(results, str(figures_dir / "group_comparison.png"))
    plot_dose_response(results, str(figures_dir / "dose_response.png"))
    print(f"Figures saved: {figures_dir}")

    # Validate gate criteria
    gate_results = validate_gate_criteria(results)
    gate_path = output_dir / OUTPUT_CONFIG["gate_file"]
    with open(gate_path, "w") as f:
        json.dump({
            "hypothesis": "h-e1",
            "gate_type": "MUST_WORK",
            **gate_results,
            "results_summary": {
                "baseline_acc": results["baseline"]["overall_acc"],
                "flip50_asymmetric_degradation": (
                    results["baseline"]["asymmetric_mean"] -
                    results["flip50"]["asymmetric_mean"]
                ),
                "symmetric_stability": abs(
                    results["baseline"]["symmetric_mean"] -
                    results["flip50"]["symmetric_mean"]
                ),
                "rotation_control": abs(
                    results["rotation"]["asymmetric_mean"] -
                    results["baseline"]["asymmetric_mean"]
                )
            }
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"GATE VALIDATION: {gate_results['action']}")
    print(f"{'='*60}")
    for criterion, passed in gate_results["checks"].items():
        status = "✓" if passed else "✗"
        print(f"{status} {criterion}: {passed}")

    return gate_results


def main():
    """Main execution."""
    print("Starting H-E1 Horizontal Flip Augmentation Study")
    print(f"Output directory: {OUTPUT_CONFIG['output_dir']}\n")

    # Run experiments
    results = run_all_conditions()

    # Save and validate
    gate_results = save_results(results)

    if gate_results["passed"]:
        print("\n✓ All MUST_WORK criteria passed - PROCEED to Phase 4.5")
    else:
        print("\n✗ Gate criteria failed - ABANDON hypothesis")

    return results, gate_results


if __name__ == "__main__":
    main()
