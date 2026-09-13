"""Main experiment orchestration for H-E1 variance measurement."""

import torch
import pandas as pd
import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from config import ExperimentConfig
from data import load_dataset
from model import create_model
from train import set_seed_deterministic, train_model
from evaluate import evaluate_model, compute_variance_metrics, check_gate_condition
from visualize import generate_all_figures


def run_single_experiment(
    dataset_name: str,
    architecture: str,
    seed: int,
    config: ExperimentConfig,
    device: str
) -> Dict[str, Any]:
    """Execute one training run.

    Args:
        dataset_name: 'mnist' or 'fashion_mnist'
        architecture: '1layer' or '2layer'
        seed: Random seed
        config: Experiment configuration
        device: 'cuda' or 'cpu'

    Returns:
        Result dictionary with test_accuracy and metadata
    """
    # Set deterministic seed
    set_seed_deterministic(seed)

    # Load data
    train_loader, test_loader = load_dataset(
        dataset_name,
        config.data_root,
        config.batch_size,
        seed
    )

    # Create model
    model = create_model(architecture).to(device)

    # Train
    train_model(
        model,
        train_loader,
        config.epochs,
        config.lr,
        config.momentum,
        device
    )

    # Evaluate
    test_accuracy = evaluate_model(model, test_loader, device)

    return {
        "dataset": dataset_name,
        "architecture": architecture,
        "seed": seed,
        "test_accuracy": test_accuracy,
        "device": device
    }


def run_all_experiments(config: ExperimentConfig, device: str = "cuda") -> pd.DataFrame:
    """Run 120 experiments (4 conditions × 30 seeds).

    Args:
        config: Experiment configuration
        device: 'cuda' or 'cpu'

    Returns:
        DataFrame with all experiment results
    """
    results = []
    conditions = config.get_conditions()
    total_experiments = len(conditions) * len(config.seeds)

    print(f"Running {total_experiments} experiments...")
    print(f"Conditions: {len(conditions)}, Seeds per condition: {len(config.seeds)}")
    print(f"Device: {device}")
    print("")

    start_time = time.time()
    experiment_count = 0

    for dataset, architecture in conditions:
        condition_results = []

        for seed in config.seeds:
            experiment_count += 1

            try:
                result = run_single_experiment(
                    dataset, architecture, seed, config, device
                )
                condition_results.append(result)
                results.append(result)

                # Progress update every 10 experiments
                if experiment_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = experiment_count / elapsed
                    remaining = (total_experiments - experiment_count) / rate
                    print(f"Progress: {experiment_count}/{total_experiments} "
                          f"({100*experiment_count/total_experiments:.1f}%) - "
                          f"ETA: {remaining/60:.1f} min")

            except Exception as e:
                print(f"ERROR in experiment {experiment_count}: {e}")
                # Record failure but continue
                results.append({
                    "dataset": dataset,
                    "architecture": architecture,
                    "seed": seed,
                    "test_accuracy": None,
                    "device": device,
                    "error": str(e)
                })

        # Condition summary
        if condition_results:
            accuracies = [r["test_accuracy"] for r in condition_results if r["test_accuracy"] is not None]
            if accuracies:
                print(f"✓ {dataset}, {architecture}: "
                      f"mean={sum(accuracies)/len(accuracies):.2f}%, "
                      f"std={pd.Series(accuracies).std():.2f}%")

    elapsed_time = time.time() - start_time
    print(f"\nAll experiments completed in {elapsed_time/60:.2f} minutes")

    return pd.DataFrame(results)


def generate_variance_summary(results_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Aggregate variance metrics per condition.

    Args:
        results_df: Experiment results DataFrame

    Returns:
        Summary dictionary: {condition_name: metrics_dict}
    """
    variance_summary = {}

    for (dataset, architecture), group in results_df.groupby(['dataset', 'architecture']):
        condition_name = f"{dataset}, {architecture}"

        # Filter out any failed experiments (None values)
        accuracies = group['test_accuracy'].dropna().tolist()

        if accuracies:
            metrics = compute_variance_metrics(accuracies)
            variance_summary[condition_name] = metrics

    return variance_summary


def save_results(
    results_df: pd.DataFrame,
    variance_summary: Dict,
    gate_result: Dict,
    config: ExperimentConfig
) -> None:
    """Save experiment logs, variance summary, and gate result.

    Args:
        results_df: Experiment results DataFrame
        variance_summary: Variance metrics per condition
        gate_result: Gate validation result
        config: Experiment configuration
    """
    # Save experiment logs (CSV)
    results_path = Path(config.results_dir) / "experiment_logs.csv"
    results_df.to_csv(results_path, index=False)
    print(f"✓ Experiment logs saved to {results_path}")

    # Save variance summary (JSON)
    summary_path = Path(config.results_dir) / "variance_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(variance_summary, f, indent=2)
    print(f"✓ Variance summary saved to {summary_path}")

    # Save gate result (JSON)
    gate_path = Path(config.results_dir) / "gate_result.json"
    with open(gate_path, 'w') as f:
        json.dump(gate_result, f, indent=2)
    print(f"✓ Gate result saved to {gate_path}")


def main():
    """Entry point: orchestrate full experiment workflow."""
    print("=" * 60)
    print("H-E1 VARIANCE MEASUREMENT EXPERIMENT")
    print("=" * 60)
    print("")

    # Configuration
    config = ExperimentConfig()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Configuration:")
    print(f"  Datasets: {config.datasets}")
    print(f"  Architectures: {config.architectures}")
    print(f"  Seeds: {len(config.seeds)} (0-{len(config.seeds)-1})")
    print(f"  Epochs: {config.epochs}")
    print(f"  Learning rate: {config.lr}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Device: {device}")
    print("")

    # Run experiments (120 total)
    results_df = run_all_experiments(config, device)

    # Compute variance metrics
    print("\nComputing variance metrics...")
    variance_summary = generate_variance_summary(results_df)

    # Display variance summary
    print("\nVariance Summary:")
    for condition, metrics in variance_summary.items():
        print(f"\n{condition}:")
        print(f"  Mean: {metrics['mean']:.2f}%")
        print(f"  Variance: {metrics['variance']:.4f}%²")
        print(f"  Std: {metrics['std']:.4f}%")
        print(f"  CV%: {metrics['cv_percent']:.2f}%")
        print(f"  95% CI: [{metrics['ci_lower']:.2f}, {metrics['ci_upper']:.2f}]")

    # Validate gate
    print("\nValidating gate condition...")
    gate_result = check_gate_condition(variance_summary, threshold=0.3)

    print(f"\nGate Result: {gate_result['gate_result']}")
    print(f"  Criterion: {gate_result['criterion']}")
    print(f"  Conditions passed: {gate_result['conditions_passed']}/{gate_result['total_conditions']}")
    print(f"  Passing conditions: {gate_result['passing_conditions']}")

    # Save results
    print("\nSaving results...")
    save_results(results_df, variance_summary, gate_result, config)

    # Generate figures
    print("\nGenerating figures...")
    generate_all_figures(results_df, variance_summary, threshold=0.3, figures_dir=config.figures_dir)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE - Gate: {gate_result['gate_result']}")
    print("=" * 60)

    return gate_result['gate_result']


if __name__ == "__main__":
    result = main()
    exit(0 if result == "PASS" else 1)
