"""
Evaluation Metrics for Confidence Calibration
"""
import numpy as np
from typing import List, Tuple, Dict
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss


class CalibrationMetrics:
    """Compute calibration quality metrics"""

    @staticmethod
    def expected_calibration_error(confidences: np.ndarray,
                                   correctness: np.ndarray,
                                   n_bins: int = 10) -> float:
        """
        Compute Expected Calibration Error (ECE)
        Lower is better (0 is perfect calibration)
        """
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = np.mean(in_bin)

            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(correctness[in_bin])
                avg_confidence_in_bin = np.mean(confidences[in_bin])
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return float(ece)

    @staticmethod
    def brier_score(confidences: np.ndarray, correctness: np.ndarray) -> float:
        """
        Compute Brier Score (BS)
        Lower is better (0 is perfect)
        """
        return float(brier_score_loss(correctness, confidences))

    @staticmethod
    def auroc(confidences: np.ndarray, correctness: np.ndarray) -> float:
        """
        Compute AUROC for predicting correctness from confidence
        Higher is better (1.0 is perfect)
        """
        try:
            return float(roc_auc_score(correctness, confidences))
        except:
            return 0.5

    @staticmethod
    def auprc(confidences: np.ndarray, correctness: np.ndarray) -> float:
        """
        Compute AUPRC (Area Under Precision-Recall Curve)
        Higher is better
        """
        try:
            return float(average_precision_score(correctness, confidences))
        except:
            return np.mean(correctness)

    @staticmethod
    def sharpness(confidences: np.ndarray) -> float:
        """
        Compute sharpness (average confidence)
        Higher means more confident predictions
        """
        return float(np.mean(confidences))

    @staticmethod
    def confidence_entropy(confidences: np.ndarray) -> float:
        """
        Compute average entropy of confidence distribution
        Lower means more decisive predictions
        """
        eps = 1e-8
        entropy = -(confidences * np.log(confidences + eps) +
                    (1 - confidences) * np.log(1 - confidences + eps))
        return float(np.mean(entropy))

    @staticmethod
    def selective_accuracy(confidences: np.ndarray,
                           correctness: np.ndarray,
                           coverage: float = 0.8) -> float:
        """
        Compute accuracy on top coverage% most confident predictions
        """
        threshold_idx = int(len(confidences) * (1 - coverage))
        sorted_indices = np.argsort(confidences)[::-1]  # Sort descending

        selected_indices = sorted_indices[:-threshold_idx] if threshold_idx > 0 else sorted_indices
        if len(selected_indices) == 0:
            return 0.0

        return float(np.mean(correctness[selected_indices]))

    @staticmethod
    def compute_all_metrics(confidences: np.ndarray,
                            correctness: np.ndarray,
                            n_bins: int = 10) -> Dict[str, float]:
        """Compute all calibration metrics"""
        metrics = {
            'ece': CalibrationMetrics.expected_calibration_error(confidences, correctness, n_bins),
            'brier_score': CalibrationMetrics.brier_score(confidences, correctness),
            'auroc': CalibrationMetrics.auroc(confidences, correctness),
            'auprc': CalibrationMetrics.auprc(confidences, correctness),
            'sharpness': CalibrationMetrics.sharpness(confidences),
            'confidence_entropy': CalibrationMetrics.confidence_entropy(confidences),
            'selective_acc_80': CalibrationMetrics.selective_accuracy(confidences, correctness, 0.8),
            'selective_acc_90': CalibrationMetrics.selective_accuracy(confidences, correctness, 0.9),
            'average_correctness': float(np.mean(correctness)),
        }

        return metrics

    @staticmethod
    def print_metrics(metrics: Dict[str, float], title: str = "Metrics"):
        """Pretty print metrics"""
        print(f"\n{title}:")
        print("=" * 50)
        print(f"  ECE:                  {metrics['ece']:.4f}")
        print(f"  Brier Score:          {metrics['brier_score']:.4f}")
        print(f"  AUROC:                {metrics['auroc']:.4f}")
        print(f"  AUPRC:                {metrics['auprc']:.4f}")
        print(f"  Sharpness:            {metrics['sharpness']:.4f}")
        print(f"  Confidence Entropy:   {metrics['confidence_entropy']:.4f}")
        print(f"  Selective Acc@80%:    {metrics['selective_acc_80']:.4f}")
        print(f"  Selective Acc@90%:    {metrics['selective_acc_90']:.4f}")
        print(f"  Average Correctness:  {metrics['average_correctness']:.4f}")
        print("=" * 50)


def check_answer_correctness(prediction: str, ground_truth: str, aliases: List[str] = None) -> bool:
    """
    Check if prediction matches ground truth
    Handles various formats and aliases
    """
    # Normalize strings
    pred_lower = prediction.lower().strip()
    gt_lower = ground_truth.lower().strip()

    # Direct match
    if gt_lower in pred_lower:
        return True

    # Check aliases
    if aliases:
        for alias in aliases:
            if alias.lower().strip() in pred_lower:
                return True

    return False


def get_consensus_answer(responses: List[Dict]) -> Tuple[str, float]:
    """
    Get consensus answer from multiple model responses
    Returns (consensus_answer, agreement_score)
    """
    # Extract response texts
    response_texts = [r['response'] for r in responses if not r.get('error', False)]

    if len(response_texts) == 0:
        return "", 0.0

    # For simplicity, use the first response as consensus
    # In practice, could use majority voting or similarity clustering
    consensus = response_texts[0]

    # Compute agreement as inverse of response diversity
    # (could be improved with actual similarity computation)
    agreement = 1.0 / len(set(response_texts)) if len(response_texts) > 0 else 0.0

    return consensus, agreement
