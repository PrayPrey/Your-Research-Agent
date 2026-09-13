"""
Evaluation metrics for the Mutual Calibration Framework.
Includes performance metrics, calibration metrics, trust metrics, and agency metrics.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict


def compute_performance_metrics(
    ai_predictions: torch.Tensor,
    human_decisions: torch.Tensor,
    true_labels: torch.Tensor
) -> Dict[str, float]:
    """
    Compute performance metrics for AI, human, and collaborative decisions.
    """
    ai_correct = (ai_predictions == true_labels).float()
    human_correct = (human_decisions == true_labels).float()

    return {
        "ai_accuracy": ai_correct.mean().item(),
        "human_accuracy": human_correct.mean().item(),
        "collaborative_accuracy": human_correct.mean().item(),  # Final decision is human's
    }


def compute_calibration_metrics(
    predictions: torch.Tensor,
    confidences: torch.Tensor,
    true_labels: torch.Tensor,
    n_bins: int = 10
) -> Dict[str, float]:
    """
    Compute calibration metrics including ECE.
    """
    pred_labels = predictions.argmax(dim=1)
    correct = (pred_labels == true_labels).float()

    # Expected Calibration Error
    ece = 0.0
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    confidences_np = confidences.cpu().numpy()
    correct_np = correct.cpu().numpy()

    bin_accs = []
    bin_confs = []
    bin_sizes = []

    for i in range(n_bins):
        in_bin = (confidences_np > bin_boundaries[i]) & (confidences_np <= bin_boundaries[i + 1])
        prop_in_bin = in_bin.mean()

        if prop_in_bin > 0:
            avg_confidence = confidences_np[in_bin].mean()
            avg_accuracy = correct_np[in_bin].mean()
            ece += prop_in_bin * np.abs(avg_accuracy - avg_confidence)
            bin_accs.append(avg_accuracy)
            bin_confs.append(avg_confidence)
            bin_sizes.append(prop_in_bin)

    # Maximum Calibration Error
    if bin_accs:
        mce = max(np.abs(np.array(bin_accs) - np.array(bin_confs)))
    else:
        mce = 0.0

    return {
        "ece": ece,
        "mce": mce,
        "mean_confidence": confidences.mean().item(),
        "accuracy": correct.mean().item()
    }


def compute_reliance_metrics(
    ai_predictions: torch.Tensor,
    ai_confidences: torch.Tensor,
    human_decisions: torch.Tensor,
    true_labels: torch.Tensor
) -> Dict[str, float]:
    """
    Compute reliance metrics: ARR, over-reliance, under-reliance rates.
    """
    ai_correct = (ai_predictions == true_labels).float()
    human_correct = (human_decisions == true_labels).float()
    followed_ai = (human_decisions == ai_predictions).float()

    # Over-reliance: accepted wrong AI recommendation
    over_reliance = (followed_ai * (1 - ai_correct)).mean().item()

    # Under-reliance: rejected correct AI recommendation and got it wrong
    under_reliance = ((1 - followed_ai) * ai_correct * (1 - human_correct)).mean().item()

    # Correct override: rejected wrong AI, made correct decision
    correct_override = ((1 - followed_ai) * (1 - ai_correct) * human_correct).mean().item()

    # Appropriate Reliance Rate (ARR)
    correct_agreement = (followed_ai * ai_correct).mean().item()
    arr = correct_agreement + correct_override

    # Reliance rate
    reliance_rate = followed_ai.mean().item()

    # Conditional reliance (when AI is confident vs uncertain)
    high_conf_mask = ai_confidences > 0.7
    low_conf_mask = ai_confidences < 0.5

    reliance_when_confident = followed_ai[high_conf_mask].mean().item() if high_conf_mask.sum() > 0 else 0
    reliance_when_uncertain = followed_ai[low_conf_mask].mean().item() if low_conf_mask.sum() > 0 else 0

    return {
        "appropriate_reliance_rate": arr,
        "over_reliance_rate": over_reliance,
        "under_reliance_rate": under_reliance,
        "correct_override_rate": correct_override,
        "reliance_rate": reliance_rate,
        "reliance_when_confident": reliance_when_confident,
        "reliance_when_uncertain": reliance_when_uncertain
    }


def compute_deference_metrics(
    deference_scores: torch.Tensor,
    ai_predictions: torch.Tensor,
    human_only_decisions: torch.Tensor,
    true_labels: torch.Tensor
) -> Dict[str, float]:
    """
    Compute metrics related to deference appropriateness.
    """
    ai_correct = (ai_predictions == true_labels).float()
    human_correct = (human_only_decisions == true_labels).float()

    # Optimal deference: defer when human is better
    human_better = (human_correct > ai_correct).float()

    # Deference appropriateness
    high_deference_mask = deference_scores > 0.5
    low_deference_mask = deference_scores <= 0.5

    # Appropriate high deference: AI defers when human would be better
    appropriate_high_deference = (high_deference_mask.float() * human_better).sum()
    total_high_deference = high_deference_mask.float().sum()
    high_deference_accuracy = (appropriate_high_deference / total_high_deference).item() if total_high_deference > 0 else 0

    # Appropriate low deference: AI confident when AI is better
    ai_better = (ai_correct > human_correct).float()
    appropriate_low_deference = (low_deference_mask.float() * ai_better).sum()
    total_low_deference = low_deference_mask.float().sum()
    low_deference_accuracy = (appropriate_low_deference / total_low_deference).item() if total_low_deference > 0 else 0

    # Overall deference appropriateness
    appropriate_deference = appropriate_high_deference + appropriate_low_deference
    total_deference_decisions = total_high_deference + total_low_deference
    overall_deference_accuracy = (appropriate_deference / total_deference_decisions).item() if total_deference_decisions > 0 else 0

    return {
        "deference_appropriateness": overall_deference_accuracy,
        "high_deference_accuracy": high_deference_accuracy,
        "low_deference_accuracy": low_deference_accuracy,
        "mean_deference": deference_scores.mean().item(),
        "deference_std": deference_scores.std().item()
    }


def compute_agency_metrics(
    human_decisions: torch.Tensor,
    ai_predictions: torch.Tensor,
    true_labels: torch.Tensor
) -> Dict[str, float]:
    """
    Compute metrics related to human agency preservation.
    """
    # Override rate: how often human deviates from AI
    override_rate = (human_decisions != ai_predictions).float().mean().item()

    # Override accuracy: how often overrides are correct
    override_mask = human_decisions != ai_predictions
    if override_mask.sum() > 0:
        override_accuracy = (human_decisions[override_mask] == true_labels[override_mask]).float().mean().item()
    else:
        override_accuracy = 0.0

    # Unique contribution: cases where human override corrected AI mistake
    ai_wrong = ai_predictions != true_labels
    human_right = human_decisions == true_labels
    unique_contribution = (ai_wrong & human_right).float().mean().item()

    return {
        "override_rate": override_rate,
        "override_accuracy": override_accuracy,
        "unique_contribution_rate": unique_contribution
    }


def compute_all_metrics(
    ai_predictions: torch.Tensor,
    ai_confidences: torch.Tensor,
    deference_scores: torch.Tensor,
    human_decisions: torch.Tensor,
    human_only_decisions: torch.Tensor,
    true_labels: torch.Tensor,
    predictions: torch.Tensor = None
) -> Dict[str, float]:
    """
    Compute all evaluation metrics.
    """
    metrics = {}

    # Performance metrics
    perf = compute_performance_metrics(ai_predictions, human_decisions, true_labels)
    metrics.update({f"perf_{k}": v for k, v in perf.items()})

    # Calibration metrics (if full predictions available)
    if predictions is not None:
        calib = compute_calibration_metrics(predictions, ai_confidences, true_labels)
        metrics.update({f"calib_{k}": v for k, v in calib.items()})

    # Reliance metrics
    reliance = compute_reliance_metrics(ai_predictions, ai_confidences, human_decisions, true_labels)
    metrics.update({f"rel_{k}": v for k, v in reliance.items()})

    # Deference metrics
    if deference_scores is not None:
        deference = compute_deference_metrics(deference_scores, ai_predictions, human_only_decisions, true_labels)
        metrics.update({f"def_{k}": v for k, v in deference.items()})

    # Agency metrics
    agency = compute_agency_metrics(human_decisions, ai_predictions, true_labels)
    metrics.update({f"agency_{k}": v for k, v in agency.items()})

    return metrics


class ExperimentTracker:
    """
    Track metrics across multiple experiments and conditions.
    """

    def __init__(self):
        self.results = defaultdict(lambda: defaultdict(list))

    def add_result(
        self,
        model_name: str,
        expertise_level: str,
        metrics: Dict[str, float]
    ):
        """Add result from single experiment."""
        key = (model_name, expertise_level)
        for metric_name, value in metrics.items():
            self.results[key][metric_name].append(value)

    def get_summary(self) -> Dict:
        """Get summary statistics for all experiments."""
        summary = {}
        for (model_name, expertise_level), metrics in self.results.items():
            key = f"{model_name}_{expertise_level}"
            summary[key] = {}
            for metric_name, values in metrics.items():
                summary[key][metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
        return summary

    def get_aggregated_by_model(self) -> Dict:
        """Get metrics aggregated across expertise levels."""
        model_results = defaultdict(lambda: defaultdict(list))

        for (model_name, expertise_level), metrics in self.results.items():
            for metric_name, values in metrics.items():
                model_results[model_name][metric_name].extend(values)

        summary = {}
        for model_name, metrics in model_results.items():
            summary[model_name] = {}
            for metric_name, values in metrics.items():
                summary[model_name][metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values)
                }
        return summary
