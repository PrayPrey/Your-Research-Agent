"""
H-M4 Main Experiment: Cross-Architecture Directional Replication
Tests if correlation directions replicate across 5 model families
"""

import torch
import numpy as np
import pandas as pd
import json
import os
from pathlib import Path
import sys

# Import h-m4 specific modules
from config_h_m4 import (
    MODEL_FAMILIES, LORA_CONFIG, TRAINING_CONFIG,
    DIMENSIONS, DIRECTION_THRESHOLDS, GATE_CRITERION,
    OUTPUT_DIR, FIGURES_DIR, RESULTS_FILE, EXPERIMENT_RESULTS_FILE
)
from model_family_manager import ModelFamilyManager
from directional_analyzer import DirectionalReplicationAnalyzer

# Import h-m3 modules (reuse evaluation logic)
from data_multi_dimensional import MultiDimensionalDataLoader
from evaluate import evaluate_model_on_dimensions
from train import train_lora_model


def run_single_seed(
    family_name: str,
    model_manager: ModelFamilyManager,
    data_loader: MultiDimensionalDataLoader,
    seed: int,
    target_dimension: str = "truthfulness"
) -> Dict[str, float]:
    """Run single seed experiment for one model family"""

    print(f"\n{'='*60}")
    print(f"Family: {family_name}, Seed: {seed}")
    print(f"{'='*60}")

    # Set seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Load model and tokenizer
    model, tokenizer = model_manager.load_model_family(family_name)

    # Baseline evaluation
    print(f"\n[Baseline] Evaluating {family_name}...")
    baseline_scores = evaluate_model_on_dimensions(
        model, tokenizer, data_loader, DIMENSIONS
    )
    print(f"Baseline: {baseline_scores}")

    # Apply LoRA
    model = model_manager.apply_lora(model, family_name)

    # Train on target dimension
    print(f"\n[Training] Fine-tuning on {target_dimension}...")
    train_dataset = data_loader.get_train_data(target_dimension)

    trained_model = train_lora_model(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        num_epochs=TRAINING_CONFIG["num_epochs"],
        learning_rate=TRAINING_CONFIG["learning_rate"],
        batch_size=TRAINING_CONFIG["batch_size"],
        max_samples=TRAINING_CONFIG["max_samples"]
    )

    # Post-intervention evaluation
    print(f"\n[Post-intervention] Evaluating {family_name}...")
    post_scores = evaluate_model_on_dimensions(
        trained_model, tokenizer, data_loader, DIMENSIONS
    )
    print(f"Post-intervention: {post_scores}")

    # Compute deltas
    deltas = {
        dim: post_scores[dim] - baseline_scores[dim]
        for dim in DIMENSIONS
    }
    print(f"Deltas: {deltas}")

    return deltas


def run_family_experiment(
    family_name: str,
    model_manager: ModelFamilyManager,
    data_loader: MultiDimensionalDataLoader,
    num_seeds: int = 5
) -> Dict[str, List[float]]:
    """Run full experiment for one model family across multiple seeds"""

    print(f"\n{'#'*60}")
    print(f"# Experimenting with {family_name.upper()}")
    print(f"{'#'*60}")

    # Collect deltas across seeds
    all_deltas = {dim: [] for dim in DIMENSIONS}

    for seed in range(num_seeds):
        try:
            deltas = run_single_seed(
                family_name, model_manager, data_loader, seed
            )

            # Store deltas
            for dim in DIMENSIONS:
                all_deltas[dim].append(deltas[dim])

        except Exception as e:
            print(f"ERROR in {family_name} seed {seed}: {e}")
            # Add zero delta for failed seed
            for dim in DIMENSIONS:
                all_deltas[dim].append(0.0)

    return all_deltas


def main():
    """Main experiment execution"""

    print("="*60)
    print("H-M4: Cross-Architecture Directional Replication")
    print("="*60)

    # Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Initialize managers
    model_manager = ModelFamilyManager(MODEL_FAMILIES, LORA_CONFIG, device)
    data_loader = MultiDimensionalDataLoader()
    analyzer = DirectionalReplicationAnalyzer(DIMENSIONS, DIRECTION_THRESHOLDS)

    # Track all results
    all_family_results = {}
    all_family_deltas = {}

    # Run experiments for each model family
    families_to_test = ["llama", "mistral", "qwen"]  # Start with 3 for PoC

    for family_name in families_to_test:
        try:
            # Run family experiment
            family_deltas = run_family_experiment(
                family_name, model_manager, data_loader,
                num_seeds=TRAINING_CONFIG["num_seeds"]
            )

            all_family_deltas[family_name] = family_deltas

            # Compute correlations for this family
            family_correlations = analyzer.compute_family_correlations(family_deltas)
            all_family_results[family_name] = family_correlations

            print(f"\n{family_name.upper()} Correlations:")
            for pair, (r, p, direction) in family_correlations.items():
                print(f"  {pair}: r={r:.3f}, p={p:.3f}, direction={direction}")

        except Exception as e:
            print(f"ERROR processing {family_name}: {e}")
            continue

    # Compute replication rates
    print("\n" + "="*60)
    print("REPLICATION ANALYSIS")
    print("="*60)

    replication_results = analyzer.compute_replication_rate(all_family_results)

    for pair, results in replication_results.items():
        print(f"\n{pair}:")
        print(f"  Majority direction: {results['majority_direction']}")
        print(f"  Replication rate: {results['replication_rate']:.2%} ({results['replication_count']}/{results['total_families']})")
        print(f"  Matching families: {results['matching_families']}")
        print(f"  Gate passed: {'✓' if results['gate_passed'] else '✗'}")

    # Check gate criterion
    gate_passed, gate_summary = analyzer.check_gate_criterion(replication_results)

    print("\n" + "="*60)
    print("GATE EVALUATION (SHOULD_WORK)")
    print("="*60)
    print(f"Gate passed: {'✓ PASS' if gate_passed else '✗ FAIL'}")
    print(f"Passed pairs: {gate_summary['passed_pairs']}")
    print(f"Replication rates: {gate_summary['replication_rates']}")

    # Save results
    results_summary = {
        "experiment": "h-m4",
        "families_tested": families_to_test,
        "num_seeds": TRAINING_CONFIG["num_seeds"],
        "gate_type": GATE_CRITERION["type"],
        "gate_passed": gate_passed,
        "gate_summary": gate_summary,
        "replication_results": replication_results,
        "family_correlations": {
            family: {
                pair: {"r": r, "p": p, "direction": direction}
                for pair, (r, p, direction) in correlations.items()
            }
            for family, correlations in all_family_results.items()
        },
        "family_deltas": all_family_deltas
    }

    # Save to JSON
    with open(EXPERIMENT_RESULTS_FILE, 'w') as f:
        json.dump(results_summary, f, indent=2)
    print(f"\n✓ Results saved to {EXPERIMENT_RESULTS_FILE}")

    # Save to CSV
    rows = []
    for family in families_to_test:
        if family in all_family_results:
            for pair, (r, p, direction) in all_family_results[family].items():
                rows.append({
                    "family": family,
                    "dimension_pair": pair,
                    "correlation": r,
                    "p_value": p,
                    "direction": direction
                })

    df = pd.DataFrame(rows)
    csv_path = os.path.join(OUTPUT_DIR, RESULTS_FILE)
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV saved to {csv_path}")

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)

    return gate_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
