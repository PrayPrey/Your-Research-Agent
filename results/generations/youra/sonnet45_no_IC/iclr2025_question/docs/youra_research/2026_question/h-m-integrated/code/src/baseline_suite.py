"""
Baseline Suite Implementation (M-2)
Implements three baseline methods for comparison with HBC:
1. SelfCheckGPT-only (consistency threshold)
2. COIN-only (standard conformal)
3. Independent Cascade (sequential SelfCheckGPT → COIN)

Author: Anonymous
Date: 2026-07-13
Hypothesis: h-m-integrated
"""

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass

from src.consistency_scorer import ConsistencyScorer
from src.conformal_predictor import ConformalPredictor
from src.baseline_model import LlamaGenerator


@dataclass
class BaselinePrediction:
    """Output of baseline prediction."""
    prediction: str
    interval_membership: int  # 1 if in interval, 0 otherwise
    consistency_score: Optional[float] = None  # For SelfCheckGPT-based methods
    method_name: str = "unknown"


class SelfCheckGPTBaseline:
    """
    Baseline 1: SelfCheckGPT-only with threshold grid search.

    Mechanism: Consistency-based filtering without conformal calibration.
    """

    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        generator: LlamaGenerator,
        n_samples: int = 5,
        threshold_range: Tuple[float, float] = (0.3, 0.7),
        threshold_steps: int = 20
    ):
        self.consistency_scorer = consistency_scorer
        self.generator = generator
        self.n_samples = n_samples
        self.threshold_range = threshold_range
        self.threshold_steps = threshold_steps
        self.threshold: Optional[float] = None
        self.calibrated = False

    def calibrate(self, calibration_data: List[Dict]) -> None:
        """
        Grid search for optimal consistency threshold.

        Args:
            calibration_data: List of dicts with 'question', 'correct_answer', 'is_correct_fn'
        """
        print(f"🔧 SelfCheckGPT Calibration (grid search)")

        # Generate predictions and consistency scores
        consistency_scores = []
        correctness = []

        for i, sample in enumerate(calibration_data):
            if i % 50 == 0:
                print(f"  Processing {i}/{len(calibration_data)}...")

            question = sample['question']
            correct_answer = sample['correct_answer']
            is_correct_fn = sample['is_correct_fn']

            samples = self.generator.generate_multiple(
                question,
                num_samples=self.n_samples,
                temperature=1.0
            )
            y_pred = samples[0]

            c_x = self.consistency_scorer.compute_consistency(y_pred, samples[1:])
            consistency_scores.append(c_x)

            is_correct = is_correct_fn(y_pred, correct_answer)
            correctness.append(is_correct)

        # Grid search for best threshold
        thresholds = np.linspace(self.threshold_range[0], self.threshold_range[1], self.threshold_steps)
        best_threshold = thresholds[0]
        best_f1 = 0.0

        for threshold in thresholds:
            # Classify: consistent if C(x) >= threshold
            predictions_binary = [1 if c >= threshold else 0 for c in consistency_scores]

            # Compute precision/recall/F1
            tp = sum(p and c for p, c in zip(predictions_binary, correctness))
            fp = sum(p and not c for p, c in zip(predictions_binary, correctness))
            fn = sum(not p and c for p, c in zip(predictions_binary, correctness))

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        self.threshold = best_threshold
        self.calibrated = True
        print(f"✓ Best threshold: {self.threshold:.3f} (F1={best_f1:.3f})")

    def predict_with_uncertainty(self, query: str, correct_answer: Optional[str] = None) -> BaselinePrediction:
        """Predict with consistency-based filtering."""
        if not self.calibrated:
            raise RuntimeError("Not calibrated")

        samples = self.generator.generate_multiple(query, num_samples=self.n_samples, temperature=1.0)
        y_pred = samples[0]
        c_x = self.consistency_scorer.compute_consistency(y_pred, samples[1:])

        # Binary classification: in interval if C(x) >= threshold
        interval_membership = 1 if c_x >= self.threshold else 0

        return BaselinePrediction(
            prediction=y_pred,
            interval_membership=interval_membership,
            consistency_score=c_x,
            method_name="SelfCheckGPT-only"
        )


class COINBaseline:
    """
    Baseline 2: COIN-only (standard conformal without weighting).

    Mechanism: Standard conformal prediction without epistemic prior.
    """

    def __init__(
        self,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator
    ):
        self.conformal_predictor = conformal_predictor
        self.generator = generator
        self.calibrated = False

    def calibrate(self, calibration_data: List[Dict]) -> None:
        """Standard conformal calibration."""
        print(f"🔧 COIN Calibration")

        # Compute nonconformity scores
        scores = []
        correctness = []

        for i, sample in enumerate(calibration_data):
            if i % 50 == 0:
                print(f"  Processing {i}/{len(calibration_data)}...")

            question = sample['question']
            correct_answer = sample['correct_answer']
            is_correct_fn = sample['is_correct_fn']

            y_pred = self.generator.generate_single(question, temperature=0.7)
            is_correct = is_correct_fn(y_pred, correct_answer)

            # Standard nonconformity: 0 if correct, 1 if wrong
            score = 0.0 if is_correct else 1.0
            scores.append(score)
            correctness.append(is_correct)

        # Calibrate
        calibration_pairs = list(zip(scores, correctness))
        self.conformal_predictor.calibrate(calibration_pairs)
        self.calibrated = True

        coverage = self.conformal_predictor.compute_coverage(calibration_pairs)
        print(f"✓ Coverage: {coverage:.3f}")

    def predict_with_uncertainty(self, query: str, correct_answer: Optional[str] = None) -> BaselinePrediction:
        """Predict with standard conformal interval."""
        if not self.calibrated:
            raise RuntimeError("Not calibrated")

        y_pred = self.generator.generate_single(query, temperature=0.7)

        if correct_answer is not None:
            is_correct = (y_pred.strip().lower() == correct_answer.strip().lower())
            score = 0.0 if is_correct else 1.0
        else:
            score = 0.5  # Default

        interval_membership = self.conformal_predictor.construct_interval(score)

        return BaselinePrediction(
            prediction=y_pred,
            interval_membership=interval_membership,
            method_name="COIN-only"
        )


class IndependentCascadeBaseline:
    """
    Baseline 3: Independent Cascade (SelfCheckGPT → COIN sequentially).

    Mechanism: Apply SelfCheckGPT first, then COIN on accepted samples.
    No joint calibration.
    """

    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        n_samples: int = 5,
        consistency_threshold: float = 0.5
    ):
        self.selfcheck = SelfCheckGPTBaseline(consistency_scorer, generator, n_samples)
        self.coin = COINBaseline(conformal_predictor, generator)
        self.consistency_threshold = consistency_threshold

    def calibrate(self, calibration_data: List[Dict]) -> None:
        """Sequential calibration: SelfCheckGPT → COIN."""
        print(f"🔧 Independent Cascade Calibration")

        # Step 1: Calibrate SelfCheckGPT
        self.selfcheck.calibrate(calibration_data)

        # Step 2: Filter by consistency, then calibrate COIN
        filtered_data = []
        for sample in calibration_data:
            question = sample['question']
            samples = self.selfcheck.generator.generate_multiple(question, num_samples=self.selfcheck.n_samples, temperature=1.0)
            y_pred = samples[0]
            c_x = self.selfcheck.consistency_scorer.compute_consistency(y_pred, samples[1:])

            if c_x >= self.selfcheck.threshold:
                filtered_data.append(sample)

        print(f"  Filtered: {len(filtered_data)}/{len(calibration_data)} samples")

        if len(filtered_data) > 0:
            self.coin.calibrate(filtered_data)
        else:
            print("  Warning: No samples passed SelfCheckGPT filter")
            self.coin.calibrate(calibration_data)  # Fallback

    def predict_with_uncertainty(self, query: str, correct_answer: Optional[str] = None) -> BaselinePrediction:
        """Two-stage prediction."""
        # Stage 1: SelfCheckGPT
        selfcheck_result = self.selfcheck.predict_with_uncertainty(query, correct_answer)

        if selfcheck_result.interval_membership == 0:
            # Rejected by SelfCheckGPT
            return BaselinePrediction(
                prediction=selfcheck_result.prediction,
                interval_membership=0,
                consistency_score=selfcheck_result.consistency_score,
                method_name="IndependentCascade"
            )

        # Stage 2: COIN
        coin_result = self.coin.predict_with_uncertainty(query, correct_answer)

        return BaselinePrediction(
            prediction=coin_result.prediction,
            interval_membership=coin_result.interval_membership,
            consistency_score=selfcheck_result.consistency_score,
            method_name="IndependentCascade"
        )


class BaselineEvaluationWrapper:
    """Unified interface for all baselines."""

    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator
    ):
        self.selfcheck = SelfCheckGPTBaseline(consistency_scorer, generator)
        self.coin = COINBaseline(conformal_predictor, generator)
        self.cascade = IndependentCascadeBaseline(consistency_scorer, conformal_predictor, generator)

    def calibrate_all(self, calibration_data: List[Dict]) -> None:
        """Calibrate all three baselines."""
        print("="*60)
        print("BASELINE CALIBRATION")
        print("="*60)

        self.selfcheck.calibrate(calibration_data)
        print()
        self.coin.calibrate(calibration_data)
        print()
        self.cascade.calibrate(calibration_data)
        print()

    def get_methods(self) -> Dict[str, object]:
        """Return all baseline methods."""
        return {
            'SelfCheckGPT-only': self.selfcheck,
            'COIN-only': self.coin,
            'IndependentCascade': self.cascade
        }
