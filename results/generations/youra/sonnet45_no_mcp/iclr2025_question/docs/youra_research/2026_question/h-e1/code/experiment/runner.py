"""Experiment runner for semantic entropy vs ensemble baseline comparison."""

from sklearn.metrics import roc_auc_score, roc_curve
import numpy as np
from typing import Dict, List
import json


class ExperimentRunner:
    """Orchestrate full experiment: generation + uncertainty + evaluation."""

    def __init__(
        self,
        data_loader,
        generator,
        semantic_estimator,
        ensemble_estimator
    ):
        """
        Initialize experiment with all components.

        Args:
            data_loader: NQDataLoader instance
            generator: MistralGenerator instance
            semantic_estimator: SemanticEntropyEstimator instance
            ensemble_estimator: EnsembleBaseline instance
        """
        self.data_loader = data_loader
        self.generator = generator
        self.semantic_estimator = semantic_estimator
        self.ensemble_estimator = ensemble_estimator

    def run_experiment(self) -> Dict[str, float]:
        """
        Run full experiment.

        Returns:
            Dict with keys: auroc_semantic, auroc_ensemble, difference, gate_pass
        """
        print("=" * 60)
        print("STARTING EXPERIMENT")
        print("=" * 60)

        # Get questions
        questions = self.data_loader.get_questions()
        print(f"Loaded {len(questions)} questions")

        # Initialize score lists
        semantic_scores = []
        ensemble_scores = []

        # Process each question
        print("\nProcessing questions...")
        for i, question in enumerate(questions):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(questions)}")

            # Generate K=10 answers
            answers = self.generator.generate_samples(question, k=10)

            # Compute uncertainty scores
            semantic_score = self.semantic_estimator.compute_uncertainty(answers)
            ensemble_score = self.ensemble_estimator.compute_uncertainty(answers)

            semantic_scores.append(semantic_score)
            ensemble_scores.append(ensemble_score)

        print(f"Processed all {len(questions)} questions")

        # Ground truth: all questions are unanswerable (positive class for uncertainty)
        y_true = [1] * len(questions)

        # Compute AUROC metrics
        auroc_semantic = roc_auc_score(y_true, semantic_scores)
        auroc_ensemble = roc_auc_score(y_true, ensemble_scores)
        difference = auroc_semantic - auroc_ensemble

        # Evaluate gate condition
        gate_pass = self.evaluate_gate({
            'auroc_semantic': auroc_semantic,
            'auroc_ensemble': auroc_ensemble,
            'difference': difference
        })

        results = {
            'auroc_semantic': float(auroc_semantic),
            'auroc_ensemble': float(auroc_ensemble),
            'difference': float(difference),
            'gate_pass': gate_pass,
            'semantic_scores': [float(s) for s in semantic_scores],
            'ensemble_scores': [float(s) for s in ensemble_scores],
            'y_true': y_true,
            'num_questions': len(questions)
        }

        print("\n" + "=" * 60)
        print("EXPERIMENT RESULTS")
        print("=" * 60)
        print(f"AUROC (Semantic Entropy): {auroc_semantic:.4f}")
        print(f"AUROC (Ensemble Baseline): {auroc_ensemble:.4f}")
        print(f"Difference: {difference:.4f}")
        print(f"Gate (MUST_WORK): {'PASS' if gate_pass else 'FAIL'}")
        print("=" * 60)

        return results

    def evaluate_gate(self, results: Dict[str, float]) -> bool:
        """
        Check MUST_WORK gate condition.

        Args:
            results: Dictionary with auroc_semantic, auroc_ensemble, difference

        Returns:
            True if gate passes, False otherwise
        """
        # Gate: AUROC_semantic - AUROC_ensemble >= 0.07 AND AUROC_semantic >= 0.70
        condition1 = results['difference'] >= 0.07
        condition2 = results['auroc_semantic'] >= 0.70

        return condition1 and condition2
