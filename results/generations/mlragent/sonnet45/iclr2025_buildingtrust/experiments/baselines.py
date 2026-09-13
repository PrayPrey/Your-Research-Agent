"""
Baseline Methods for Confidence Calibration
"""
import numpy as np
from typing import List, Dict
import re


class BaselineMethod:
    """Base class for baseline confidence estimation methods"""

    def __init__(self, name: str):
        self.name = name

    def estimate_confidence(self, responses: List[Dict], **kwargs) -> float:
        """Estimate confidence for a set of responses"""
        raise NotImplementedError


class ConstantConfidence(BaselineMethod):
    """Always return a constant confidence value"""

    def __init__(self, confidence: float = 0.5):
        super().__init__("Constant Confidence")
        self.confidence = confidence

    def estimate_confidence(self, responses: List[Dict], **kwargs) -> float:
        return self.confidence


class MajorityVoting(BaselineMethod):
    """Confidence based on majority voting agreement"""

    def __init__(self):
        super().__init__("Majority Voting")

    def estimate_confidence(self, responses: List[Dict], **kwargs) -> float:
        """Confidence = proportion of models agreeing with majority"""
        response_texts = [r['response'].lower().strip() for r in responses if not r.get('error', False)]

        if len(response_texts) == 0:
            return 0.0

        # Count unique responses
        from collections import Counter
        response_counts = Counter(response_texts)

        if len(response_counts) == 0:
            return 0.0

        # Get majority count
        max_count = max(response_counts.values())

        # Confidence = agreement ratio
        confidence = max_count / len(response_texts)

        return float(confidence)


class LengthBasedConfidence(BaselineMethod):
    """Confidence based on response length consistency"""

    def __init__(self):
        super().__init__("Length-Based Confidence")

    def estimate_confidence(self, responses: List[Dict], **kwargs) -> float:
        """Lower length variance -> higher confidence"""
        response_texts = [r['response'] for r in responses if not r.get('error', False)]

        if len(response_texts) < 2:
            return 0.5

        lengths = [len(r.split()) for r in response_texts]
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)

        if mean_length == 0:
            return 0.5

        # CV = std / mean
        cv = std_length / mean_length

        # Confidence = 1 - cv (capped at [0, 1])
        confidence = max(0.0, min(1.0, 1.0 - cv))

        return float(confidence)


class SimpleSemanticSimilarity(BaselineMethod):
    """Confidence based on simple semantic similarity"""

    def __init__(self):
        super().__init__("Simple Semantic Similarity")

    def estimate_confidence(self, responses: List[Dict], analysis_results: Dict = None, **kwargs) -> float:
        """Use semantic dispersion from analysis results"""
        if analysis_results is None:
            return 0.5

        # Low dispersion -> high confidence
        dispersion = analysis_results.get('semantic_dispersion', 0.5)
        confidence = 1.0 - dispersion

        return float(np.clip(confidence, 0.0, 1.0))


class UncertaintyEstimator(BaselineMethod):
    """Simple uncertainty estimator based on composite metrics"""

    def __init__(self):
        super().__init__("Uncertainty Estimator")

    def estimate_confidence(self, responses: List[Dict], analysis_results: Dict = None, **kwargs) -> float:
        """Use composite uncertainty score"""
        if analysis_results is None:
            return 0.5

        # Convert uncertainty to confidence
        uncertainty = analysis_results.get('composite_uncertainty', 0.5)
        confidence = 1.0 - uncertainty

        return float(np.clip(confidence, 0.0, 1.0))


class BaselineEvaluator:
    """Evaluate multiple baseline methods"""

    def __init__(self):
        self.baselines = {
            'constant': ConstantConfidence(0.5),
            'majority_voting': MajorityVoting(),
            'length_based': LengthBasedConfidence(),
            'semantic_similarity': SimpleSemanticSimilarity(),
            'uncertainty_estimator': UncertaintyEstimator(),
        }

    def evaluate_baseline(self, baseline_name: str,
                          response_dict: Dict[str, List[Dict]],
                          analysis_dict: Dict[str, Dict],
                          ground_truth: Dict[str, bool]) -> Dict[str, float]:
        """
        Evaluate a baseline method
        Returns confidence scores for each question
        """
        baseline = self.baselines[baseline_name]
        confidences = {}

        for question, responses in response_dict.items():
            analysis = analysis_dict.get(question, {})

            confidence = baseline.estimate_confidence(
                responses,
                analysis_results=analysis
            )

            confidences[question] = confidence

        return confidences

    def evaluate_all_baselines(self, response_dict: Dict[str, List[Dict]],
                                analysis_dict: Dict[str, Dict],
                                ground_truth: Dict[str, bool]) -> Dict[str, Dict[str, float]]:
        """Evaluate all baseline methods"""
        results = {}

        for baseline_name in self.baselines.keys():
            print(f"Evaluating baseline: {baseline_name}")
            confidences = self.evaluate_baseline(
                baseline_name,
                response_dict,
                analysis_dict,
                ground_truth
            )
            results[baseline_name] = confidences

        return results
