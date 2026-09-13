"""Main experiment runner for H-M1"""
import sys
import json
import pandas as pd
from pathlib import Path
from config import CONFIG
from data.curate import generate_all_conditions
from train import train_all_conditions
from evaluate import evaluate_all_conditions


def main():
    """Run full H-M1 experiment pipeline"""
    print("\n" + "="*60)
    print("H-M1 EXPERIMENT: Data Curation → Information Density")
    print("="*60)

    # Step 1: Generate curated datasets
    print("\nStep 1: Generating 9 curated C4 conditions...")
    condition_paths = generate_all_conditions(
        output_dir="data/curated",
        base_config={"seed": CONFIG.training.seed}
    )
    print(f"Generated {len(condition_paths)} conditions")

    # Step 2: Train on all conditions
    print("\nStep 2: Training GPT-2 on all conditions...")
    metrics_csv = train_all_conditions(
        condition_paths=condition_paths,
        base_config=CONFIG
    )
    print(f"Training complete. Metrics: {metrics_csv}")

    # Step 3: Evaluate gate
    print("\nStep 3: Evaluating gate metrics...")
    metrics_log = pd.read_csv(metrics_csv)
    results = evaluate_all_conditions(metrics_log)

    # Save results
    results_json = Path("outputs") / "experiment_results.json"
    results_json.parent.mkdir(parents=True, exist_ok=True)

    # Convert non-serializable to dict
    results_serializable = {
        "entropy_reduction": results["entropy_reduction"],
        "fisher_increase": results["fisher_increase"],
        "monotonicity": results["monotonicity"],
        "gate_result": results["gate_result"]
    }

    with open(results_json, 'w') as f:
        json.dump(results_serializable, f, indent=2)

    print(f"\nResults saved: {results_json}")
    print(f"Gate Result: {results['gate_result']}")

    # Exit code based on gate
    if results['gate_result'] == 'PASS':
        sys.exit(0)
    elif results['gate_result'] == 'PARTIAL':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
