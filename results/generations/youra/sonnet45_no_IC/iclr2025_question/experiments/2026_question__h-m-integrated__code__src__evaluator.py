"""Experiment evaluator and visualization."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


class ExperimentEvaluator:
    """Run experiment and generate evaluation metrics."""

    def __init__(
        self,
        output_folder: str = "outputs",
        figures_folder: str = "../figures"
    ):
        """Initialize evaluator."""
        self.output_folder = Path(output_folder)
        self.figures_folder = Path(figures_folder)

        # Create directories
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.figures_folder.mkdir(parents=True, exist_ok=True)

    def run_experiment(
        self,
        generator,
        consistency_scorer,
        conformal_predictor,
        correlation_analyzer,
        data_loader,
        config: dict
    ) -> dict:
        """Run full experiment pipeline."""

        # Load datasets
        print("Loading datasets...")
        data_loader.load_all_datasets()
        print()

        all_results = {}
        per_dataset_results = {}

        # Process each dataset
        for dataset_name in config["datasets"]:
            print(f"Processing {dataset_name}...")
            print("-" * 60)

            # Get data splits
            calibration_data = data_loader.get_split(dataset_name, "calibration")
            test_data = data_loader.get_split(dataset_name, "test")

            # Limit test size for PoC
            test_data = test_data[:min(len(test_data), 100)]  # Use 100 samples for PoC

            print(f"  Calibration samples: {len(calibration_data)}")
            print(f"  Test samples: {len(test_data)}")
            print()

            # Calibration phase
            print("  Calibration phase...")
            calibration_conformity = []

            for i, item in enumerate(tqdm(calibration_data[:200], desc="  Calibrating")):  # Use 200 for PoC
                question = item["question"]

                # Generate answer
                answer = generator.generate_single(question, max_tokens=config["max_tokens"])

                # Compute conformity score using actual correctness
                # Check if generated answer matches any correct answer
                correct_answers = item.get("correct_answers", [])
                is_correct = False
                conformity_score = 0.0

                if correct_answers:
                    # Use F1 score between generated answer and correct answers
                    answer_tokens = set(answer.lower().split())
                    max_f1 = 0.0
                    for correct_ans in correct_answers:
                        correct_tokens = set(str(correct_ans).lower().split())
                        if len(answer_tokens) == 0 or len(correct_tokens) == 0:
                            f1 = 0.0
                        else:
                            intersection = answer_tokens & correct_tokens
                            precision = len(intersection) / len(answer_tokens) if len(answer_tokens) > 0 else 0
                            recall = len(intersection) / len(correct_tokens) if len(correct_tokens) > 0 else 0
                            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                        max_f1 = max(max_f1, f1)

                    conformity_score = max_f1
                    is_correct = max_f1 > 0.3  # Threshold for correctness
                else:
                    # For datasets without ground truth (like HH-RLHF), use consistency as proxy
                    # Generate multiple samples and check self-consistency
                    samples = generator.generate_multiple(question, num_samples=3, max_tokens=config["max_tokens"])
                    answer_tokens = set(answer.lower().split())
                    consistency_scores = []
                    for sample in samples:
                        sample_tokens = set(sample.lower().split())
                        if len(answer_tokens) == 0 or len(sample_tokens) == 0:
                            consistency_scores.append(0.0)
                        else:
                            intersection = answer_tokens & sample_tokens
                            jaccard = len(intersection) / len(answer_tokens | sample_tokens)
                            consistency_scores.append(jaccard)
                    conformity_score = np.mean(consistency_scores)
                    is_correct = conformity_score > 0.3

                calibration_conformity.append((conformity_score, is_correct))

            # Calibrate conformal predictor
            conformal_predictor.calibrate(calibration_conformity)
            print(f"  Quantile threshold: {conformal_predictor.quantile_threshold:.2f}")
            print()

            # Test phase
            print("  Test phase...")
            C_scores = []
            I_indicators = []

            for item in tqdm(test_data, desc="  Testing"):
                question = item["question"]

                # Generate multiple samples for consistency
                samples = generator.generate_multiple(
                    question,
                    num_samples=config["num_samples"],
                    max_tokens=config["max_tokens"]
                )

                # Use first sample as reference
                reference = samples[0]
                other_samples = samples[1:]

                # Compute consistency score C
                C = consistency_scorer.compute_consistency(reference, other_samples)
                C_scores.append(C)

                # Compute conformal interval indicator I using actual correctness
                correct_answers = item.get("correct_answers", [])

                if correct_answers:
                    # Use F1 score as conformity metric
                    reference_tokens = set(reference.lower().split())
                    max_f1 = 0.0
                    for correct_ans in correct_answers:
                        correct_tokens = set(str(correct_ans).lower().split())
                        if len(reference_tokens) == 0 or len(correct_tokens) == 0:
                            f1 = 0.0
                        else:
                            intersection = reference_tokens & correct_tokens
                            precision = len(intersection) / len(reference_tokens) if len(reference_tokens) > 0 else 0
                            recall = len(intersection) / len(correct_tokens) if len(correct_tokens) > 0 else 0
                            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                        max_f1 = max(max_f1, f1)
                    conformity_score = max_f1
                else:
                    # For datasets without ground truth, use self-consistency
                    reference_tokens = set(reference.lower().split())
                    consistency_scores = []
                    for sample in other_samples:
                        sample_tokens = set(sample.lower().split())
                        if len(reference_tokens) == 0 or len(sample_tokens) == 0:
                            consistency_scores.append(0.0)
                        else:
                            intersection = reference_tokens & sample_tokens
                            jaccard = len(intersection) / len(reference_tokens | sample_tokens)
                            consistency_scores.append(jaccard)
                    conformity_score = np.mean(consistency_scores) if consistency_scores else 0.0

                I = conformal_predictor.construct_interval(conformity_score)
                I_indicators.append(I)

            # Correlation analysis
            rho, p_value = correlation_analyzer.compute_correlation(C_scores, I_indicators)

            # Compute coverage using actual correctness
            print("  Computing coverage...")
            test_conformity = []
            for item in test_data[:50]:  # Sample for coverage
                question = item["question"]
                answer = generator.generate_single(question, max_tokens=config["max_tokens"])
                correct_answers = item.get("correct_answers", [])

                if correct_answers:
                    # Use F1 score as conformity metric
                    answer_tokens = set(answer.lower().split())
                    max_f1 = 0.0
                    for correct_ans in correct_answers:
                        correct_tokens = set(str(correct_ans).lower().split())
                        if len(answer_tokens) == 0 or len(correct_tokens) == 0:
                            f1 = 0.0
                        else:
                            intersection = answer_tokens & correct_tokens
                            precision = len(intersection) / len(answer_tokens) if len(answer_tokens) > 0 else 0
                            recall = len(intersection) / len(correct_tokens) if len(correct_tokens) > 0 else 0
                            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                        max_f1 = max(max_f1, f1)
                    conformity_score = max_f1
                    is_correct = max_f1 > 0.3
                else:
                    # For datasets without ground truth, use self-consistency
                    samples = generator.generate_multiple(question, num_samples=3, max_tokens=config["max_tokens"])
                    answer_tokens = set(answer.lower().split())
                    consistency_scores = []
                    for sample in samples:
                        sample_tokens = set(sample.lower().split())
                        if len(answer_tokens) == 0 or len(sample_tokens) == 0:
                            consistency_scores.append(0.0)
                        else:
                            intersection = answer_tokens & sample_tokens
                            jaccard = len(intersection) / len(answer_tokens | sample_tokens)
                            consistency_scores.append(jaccard)
                    conformity_score = np.mean(consistency_scores) if consistency_scores else 0.0
                    is_correct = conformity_score > 0.3

                test_conformity.append((conformity_score, is_correct))

            coverage = conformal_predictor.compute_coverage(test_conformity)

            # Store results
            per_dataset_results[dataset_name] = {
                "correlation": rho,
                "p_value": p_value,
                "coverage": coverage,
                "n_samples": len(test_data),
                "mean_consistency": float(np.mean(C_scores)),
                "mean_interval_membership": float(np.mean(I_indicators))
            }

            print()
            print(f"  Results:")
            print(f"    ρ(C,I) = {rho:.4f}")
            print(f"    p-value = {p_value:.4e}")
            print(f"    Coverage = {coverage:.2%}")
            print()

        # Overall gate check
        gate_satisfied_per_dataset = []
        for dataset_name, metrics in per_dataset_results.items():
            is_valid = correlation_analyzer.validate_gate_condition(
                metrics["correlation"],
                metrics["p_value"]
            )
            gate_satisfied_per_dataset.append(is_valid)

        gate_satisfied = all(gate_satisfied_per_dataset)

        # Aggregate results
        all_results = {
            "gate_result": {
                "satisfied": gate_satisfied,
                "type": "MUST_WORK",
                "criteria": "0.3 ≤ ρ(C,I) ≤ 0.7 on all datasets with p < 0.05"
            },
            "per_dataset_results": per_dataset_results,
            "config": config,
            "timestamp": str(Path("experiment_results.json").stat().st_mtime if Path("experiment_results.json").exists() else "")
        }

        # Generate visualizations
        print("Generating figures...")
        self._generate_figures(per_dataset_results)
        print()

        return all_results

    def _generate_figures(self, results: dict):
        """Generate required figures."""

        # Figure 1: Correlation scatter plots
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        for idx, (dataset_name, metrics) in enumerate(results.items()):
            ax = axes[idx]
            # Placeholder scatter (actual data would be passed)
            ax.scatter([0.5], [0.5], alpha=0.6)
            ax.set_xlabel("Consistency Score (C)")
            ax.set_ylabel("Interval Indicator (I)")
            ax.set_title(f"{dataset_name}\nρ={metrics['correlation']:.3f}")
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_folder / "correlation_scatter.png", dpi=150)
        plt.close()

        # Figure 2: Correlation bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        datasets = list(results.keys())
        correlations = [results[d]["correlation"] for d in datasets]

        ax.bar(datasets, correlations, alpha=0.7)
        ax.axhline(y=0.3, color='r', linestyle='--', label='Lower bound (0.3)')
        ax.axhline(y=0.7, color='r', linestyle='--', label='Upper bound (0.7)')
        ax.set_ylabel("Correlation ρ(C,I)")
        ax.set_title("Correlation Between Consistency and Conformal Signals")
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.figures_folder / "correlation_bars.png", dpi=150)
        plt.close()

        print(f"  Figures saved to: {self.figures_folder}")
