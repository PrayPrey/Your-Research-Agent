"""Evaluation metrics for reconstruction test."""
import statistics
from typing import Dict, List, Any


def compute_reconstruction_metrics(per_sample: List[Dict[str, Any]], fields: List[str]) -> Dict[str, Any]:
    """Compute aggregate metrics from per-sample results."""
    accuracies = [s["accuracy"] for s in per_sample]

    mean_acc = statistics.mean(accuracies)
    std_acc = statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0
    pass_rate = sum(1 for s in per_sample if s["perfect_match"]) / len(per_sample)

    # Per-field accuracy
    per_field = {f: 0.0 for f in fields}
    for sample in per_sample:
        orig = sample["original"]
        recon = sample["reconstructed"]
        for field in fields:
            if field == "code_context":
                orig_set = set(str(v).strip() for v in (orig.get(field) or []))
                recon_set = set(str(v).strip() for v in (recon.get(field) or []))
                if orig_set == recon_set:
                    per_field[field] += 1
            else:
                if str(orig.get(field, "")).strip().lower() == str(recon.get(field, "")).strip().lower():
                    per_field[field] += 1

    for field in fields:
        per_field[field] /= len(per_sample)

    return {
        "mean_accuracy": mean_acc,
        "std_accuracy": std_acc,
        "pass_rate": pass_rate,
        "per_field": per_field,
        "n_samples": len(per_sample),
    }


def per_error_type_breakdown(pairs: List[Dict[str, Any]], per_sample: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Group per-sample accuracy by error type."""
    by_type: Dict[str, List[float]] = {}

    for i, sample in enumerate(per_sample):
        error_type = pairs[i]["structured_error"].get("error_type", "Unknown")
        if error_type not in by_type:
            by_type[error_type] = []
        by_type[error_type].append(sample["accuracy"])

    breakdown = {}
    for error_type, accuracies in by_type.items():
        breakdown[error_type] = {
            "mean_accuracy": statistics.mean(accuracies),
            "std_accuracy": statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0,
            "n_samples": len(accuracies),
            "pass_rate": sum(1 for a in accuracies if a == 1.0) / len(accuracies),
        }

    return breakdown


def gate_check(metrics: Dict[str, Any], acc_thresh: float = 0.95, pass_thresh: float = 0.90) -> bool:
    """Check if reconstruction metrics pass the gate."""
    return metrics["mean_accuracy"] >= acc_thresh and metrics["pass_rate"] >= pass_thresh
