"""
Hierarchical Bayesian Calibrator (HBC) - Core Implementation
Implements three-step causal mechanism:
1. Consistency sampling → epistemic prior C(x)
2. Conformal prediction → aleatoric intervals I(x) (weighted by C(x))
3. Bayesian co-calibration → mutual threshold updating

Author: Anonymous
Date: 2026-07-13
Hypothesis: h-m-integrated
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import torch
from dataclasses import dataclass

# Import base modules from h-e1
from src.consistency_scorer import ConsistencyScorer
from src.conformal_predictor import ConformalPredictor
from src.baseline_model import LlamaGenerator


@dataclass
class HBCPrediction:
    """Output of HBC prediction with uncertainty quantification."""
    prediction: str
    interval_membership: int  # 1 if in interval, 0 otherwise
    consistency_score: float  # C(x) ∈ [0, 1]
    interval_width: float  # Calibrated interval width


class HierarchicalBayesianCalibrator:
    """
    Three-step HBC mechanism with mutual calibration.

    Mechanism:
    1. Consistency Prior: Generate N samples, compute C(x) via NLI+BERTScore
    2. Weighted Conformal: Nonconformity = score / (1 + C(x))
    3. Mutual Calibration: Update thresholds based on coverage feedback
    """

    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        alpha: float = 0.1,
        max_iterations: int = 3,
        initial_threshold: float = 0.5,
        n_samples: int = 5
    ):
        """
        Initialize HBC calibrator.

        Args:
            consistency_scorer: Pre-initialized consistency scorer (from h-e1)
            conformal_predictor: Pre-initialized conformal predictor (from h-e1)
            generator: Llama-2-7B generator (from h-e1)
            alpha: Target miscoverage rate (1 - coverage target)
            max_iterations: Maximum mutual calibration iterations
            initial_threshold: Initial consistency threshold
            n_samples: Number of samples for consistency computation
        """
        self.consistency_scorer = consistency_scorer
        self.conformal_predictor = conformal_predictor
        self.generator = generator
        self.alpha = alpha
        self.max_iterations = max_iterations
        self.consistency_threshold = initial_threshold
        self.n_samples = n_samples

        # Calibration state
        self.conformal_scores: List[float] = []
        self.conformal_quantile: Optional[float] = None
        self.calibrated = False

        # Mutual calibration history
        self.calibration_history: List[Dict] = []

    def calibrate(self, calibration_data: List[Dict]) -> None:
        """
        Three-step calibration on labeled validation set.

        Args:
            calibration_data: List of dicts with keys:
                - 'question': str (input query)
                - 'correct_answer': str (ground truth)
                - 'is_correct_fn': callable (y_pred, y_true) -> bool

        Mechanism:
        1. For each sample: Generate N samples → compute C(x)
        2. Compute weighted nonconformity: score / (1 + C(x))
        3. Iterate: Update conformal quantile → measure coverage → update threshold
        """
        print(f"🔧 HBC Calibration (n={len(calibration_data)}, alpha={self.alpha})")

        # Step 1: Compute consistency scores for all calibration samples
        consistency_scores = []
        predictions = []
        correctness = []

        for i, sample in enumerate(calibration_data):
            if i % 50 == 0:
                print(f"  Processing {i}/{len(calibration_data)}...")

            question = sample['question']
            correct_answer = sample['correct_answer']
            is_correct_fn = sample['is_correct_fn']

            # Generate N samples for consistency
            samples = self.generator.generate_multiple(
                question,
                num_samples=self.n_samples,
                temperature=1.0
            )

            # Main prediction (first sample)
            y_pred = samples[0]
            predictions.append(y_pred)

            # Compute consistency C(x)
            c_x = self.consistency_scorer.compute_consistency(
                reference=y_pred,
                samples=samples[1:]
            )
            consistency_scores.append(c_x)

            # Check correctness
            is_correct = is_correct_fn(y_pred, correct_answer)
            correctness.append(is_correct)

        # Step 2: Mutual calibration loop
        best_coverage = 0.0
        best_threshold = self.consistency_threshold

        for iteration in range(self.max_iterations):
            # Compute weighted nonconformity scores
            weighted_scores = []
            for c_x, is_correct in zip(consistency_scores, correctness):
                # Weighted nonconformity: penalize inconsistent samples
                # Higher C(x) (more consistent) → lower nonconformity
                base_score = 0.0 if is_correct else 1.0
                weighted_score = base_score / (1.0 + c_x)
                weighted_scores.append(weighted_score)

            # Calibrate conformal predictor
            calibration_pairs = list(zip(weighted_scores, correctness))
            self.conformal_predictor.calibrate(calibration_pairs)

            # Measure coverage
            coverage = self.conformal_predictor.compute_coverage(calibration_pairs)

            # Update history
            self.calibration_history.append({
                'iteration': iteration,
                'threshold': self.consistency_threshold,
                'coverage': coverage,
                'target': 1 - self.alpha
            })

            print(f"  Iteration {iteration+1}: threshold={self.consistency_threshold:.3f}, coverage={coverage:.3f}")

            # Step 3: Bayesian threshold updating
            if coverage < (1 - self.alpha) - 0.05:  # Under-coverage
                # Lower threshold to be more permissive
                self.consistency_threshold *= 0.9
            elif coverage > (1 - self.alpha) + 0.05:  # Over-coverage
                # Raise threshold to be more selective
                self.consistency_threshold *= 1.1

            # Clamp threshold
            self.consistency_threshold = np.clip(self.consistency_threshold, 0.1, 0.9)

            # Track best
            if abs(coverage - (1 - self.alpha)) < abs(best_coverage - (1 - self.alpha)):
                best_coverage = coverage
                best_threshold = self.consistency_threshold

            # Convergence check
            if abs(coverage - (1 - self.alpha)) < 0.02:
                print(f"  ✓ Converged at iteration {iteration+1}")
                break

        # Use best threshold
        self.consistency_threshold = best_threshold
        self.calibrated = True
        print(f"✓ Calibration complete: threshold={self.consistency_threshold:.3f}, coverage={best_coverage:.3f}")

    def predict_with_uncertainty(self, query: str, correct_answer: Optional[str] = None) -> HBCPrediction:
        """
        Inference with co-calibrated uncertainty quantification.

        Args:
            query: Input question
            correct_answer: Ground truth (optional, for evaluation)

        Returns:
            HBCPrediction with prediction, interval membership, consistency, width
        """
        if not self.calibrated:
            raise RuntimeError("Calibrator not calibrated. Call calibrate() first.")

        # Step 1: Generate samples and compute consistency
        samples = self.generator.generate_multiple(
            query,
            num_samples=self.n_samples,
            temperature=1.0
        )
        y_pred = samples[0]

        c_x = self.consistency_scorer.compute_consistency(
            reference=y_pred,
            samples=samples[1:]
        )

        # Step 2: Compute weighted nonconformity
        if correct_answer is not None:
            # For evaluation: compute actual nonconformity
            is_correct = (y_pred.strip().lower() == correct_answer.strip().lower())
            base_score = 0.0 if is_correct else 1.0
        else:
            # For inference: use consistency as proxy
            base_score = 1.0 - c_x

        weighted_score = base_score / (1.0 + c_x)

        # Step 3: Conformal interval construction
        interval_membership = self.conformal_predictor.construct_interval(weighted_score)

        # Interval width (epistemic-informed)
        if self.conformal_predictor.conformal_quantile is not None:
            interval_width = self.conformal_predictor.conformal_quantile * (1.0 + c_x)
        else:
            interval_width = 1.0  # Default

        return HBCPrediction(
            prediction=y_pred,
            interval_membership=interval_membership,
            consistency_score=c_x,
            interval_width=interval_width
        )

    def _compute_weighted_nonconformity(
        self,
        y_pred: str,
        y_true: str,
        consistency_score: float
    ) -> float:
        """
        Compute weighted nonconformity score.

        Weighting: Higher consistency → lower nonconformity penalty
        Formula: score / (1 + C(x))
        """
        is_correct = (y_pred.strip().lower() == y_true.strip().lower())
        base_score = 0.0 if is_correct else 1.0
        return base_score / (1.0 + consistency_score)

    def _update_consistency_threshold(self, coverage_results: List[float]) -> float:
        """
        Bayesian updating of consistency threshold based on coverage feedback.

        Args:
            coverage_results: List of empirical coverage rates

        Returns:
            Updated threshold
        """
        target_coverage = 1 - self.alpha
        current_coverage = coverage_results[-1] if coverage_results else 0.0

        # Adaptive update
        if current_coverage < target_coverage - 0.05:
            return self.consistency_threshold * 0.9  # Lower threshold
        elif current_coverage > target_coverage + 0.05:
            return self.consistency_threshold * 1.1  # Raise threshold
        else:
            return self.consistency_threshold  # Maintain

    def get_calibration_stats(self) -> Dict:
        """Return calibration statistics for debugging."""
        return {
            'calibrated': self.calibrated,
            'threshold': self.consistency_threshold,
            'iterations': len(self.calibration_history),
            'history': self.calibration_history
        }
