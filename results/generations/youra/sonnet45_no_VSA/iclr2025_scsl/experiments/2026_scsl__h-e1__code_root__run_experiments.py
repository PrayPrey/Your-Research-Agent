#!/usr/bin/env python3
"""
Main orchestration script for H-E1 SAM+SWA experiments
Runs 50 experiments: 5 methods × 2 datasets × 5 seeds
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_samswa import get_config
from train import train_method
from evaluate import generate_validation_report


def run_all_experiments(
    output_dir: str = "outputs/h-e1",
    methods: list = None,
    datasets: list = None,
    seeds: list = None
):
    """
    Run all 50 experiments and generate validation report.

    Args:
        output_dir: Output directory for results
        methods: List of methods to test
        datasets: List of datasets to test
        seeds: List of seeds to use
    """
    # Default experimental design
    if methods is None:
        methods = ["ERM", "SAM", "SWA", "Joint", "Sequential"]
    if datasets is None:
        datasets = ["ColoredMNIST", "CelebA"]
    if seeds is None:
        seeds = [42, 123, 456, 789, 2024]

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    results_file = output_path / "results.csv"
    analysis_file = output_path / "statistical_analysis.json"
    report_file = output_path / "04_validation.md"

    # Collect results
    all_results = []

    total_experiments = len(methods) * len(datasets) * len(seeds)
    experiment_count = 0

    print(f"Running {total_experiments} experiments...")
    print(f"Methods: {methods}")
    print(f"Datasets: {datasets}")
    print(f"Seeds: {seeds}")
    print(f"Output directory: {output_dir}\n")

    for dataset in datasets:
        for method in methods:
            for seed in seeds:
                experiment_count += 1
                print(f"\n{'='*80}")
                print(f"Experiment {experiment_count}/{total_experiments}")
                print(f"Method: {method}, Dataset: {dataset}, Seed: {seed}")
                print(f"{'='*80}")

                try:
                    # Get config
                    config = get_config(method, dataset, seed)

                    # Run training
                    result = train_method(
                        method=method,
                        dataset_name=dataset,
                        seed=seed,
                        config=config,
                        output_dir=output_dir
                    )

                    all_results.append(result)

                    # Save intermediate results
                    df = pd.DataFrame(all_results)
                    df.to_csv(results_file, index=False)
                    print(f"Intermediate results saved to {results_file}")

                except Exception as e:
                    print(f"ERROR in experiment {experiment_count}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

    # Generate final results
    print(f"\n{'='*80}")
    print("All experiments completed!")
    print(f"{'='*80}\n")

    if len(all_results) > 0:
        df = pd.DataFrame(all_results)
        df.to_csv(results_file, index=False)
        print(f"Final results saved to {results_file}")

        # Generate validation report
        print("\nGenerating validation report...")
        generate_validation_report(str(results_file), str(report_file))
        print(f"Validation report saved to {report_file}")

        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        for dataset in datasets:
            print(f"\n{dataset}:")
            df_dataset = df[df["dataset"] == dataset]
            for method in methods:
                scores = df_dataset[df_dataset["method"] == method]["test_wg_acc"]
                if len(scores) > 0:
                    print(f"  {method:12s}: {scores.mean()*100:.2f}% ± {scores.std()*100:.2f}% (n={len(scores)})")

        total_time = df["training_time_hours"].sum()
        print(f"\nTotal GPU-hours: {total_time:.2f}h")
        print(f"Within budget (35h): {total_time <= 35.0}")

    else:
        print("No results to save!")


def main():
    parser = argparse.ArgumentParser(
        description="Run H-E1 SAM+SWA experiments"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/h-e1",
        help="Output directory for results"
    )
    parser.add_argument(
        "--methods",
        type=str,
        nargs="+",
        default=None,
        help="Methods to test (default: all)"
    )
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=None,
        help="Datasets to test (default: both)"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=None,
        help="Seeds to use (default: 5 seeds)"
    )

    args = parser.parse_args()

    run_all_experiments(
        output_dir=args.output_dir,
        methods=args.methods,
        datasets=args.datasets,
        seeds=args.seeds
    )


if __name__ == "__main__":
    main()
