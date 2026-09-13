"""End-to-end run script for H-E1: Model Zoo Dataset Validity."""

import json
import os
import sys

def main() -> None:
    # Set output paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    figures_dir = os.path.join(base_dir, "figures")
    results_path = os.path.join(base_dir, "results.json")

    os.makedirs(figures_dir, exist_ok=True)

    # Step 1: Load accuracies
    print("Loading Model Zoo accuracies...")
    try:
        from data import load_accuracies
        accuracies = load_accuracies()
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        sys.exit(1)

    # Step 2: Validate variance
    print("Computing statistics...")
    from analysis import validate_model_zoo_variance, report_gate
    stats = validate_model_zoo_variance(accuracies)

    # Step 3: Generate visualizations
    print("Generating figures...")
    from visualize import plot_gate_comparison, plot_histogram, plot_boxplot
    plot_gate_comparison(stats, figures_dir)
    plot_histogram(accuracies, stats, figures_dir)
    plot_boxplot(accuracies, figures_dir)

    # Step 4: Report gate result
    print(report_gate(stats))

    # Step 5: Save results
    with open(results_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Results saved to {results_path}")

    # Exit code based on gate
    sys.exit(0 if stats["gate_passed"] else 1)


if __name__ == "__main__":
    main()
