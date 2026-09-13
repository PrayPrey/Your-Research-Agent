"""Statistical analysis for H-E1: Model Zoo Dataset Validity."""

import numpy as np
from scipy import stats

GATE_THRESHOLD = 10.0

def validate_model_zoo_variance(accuracies: np.ndarray) -> dict:
    """Compute mean/std/min/max/quartiles/IQR outliers/Shapiro-Wilk; gate_passed = std > 10.0."""

    n_samples = len(accuracies)
    mean_acc = float(np.mean(accuracies))
    std_acc = float(np.std(accuracies))
    min_acc = float(np.min(accuracies))
    max_acc = float(np.max(accuracies))

    q1, q2, q3 = np.percentile(accuracies, [25, 50, 75])
    iqr = q3 - q1

    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    n_outliers = int(np.sum((accuracies < lower_fence) | (accuracies > upper_fence)))

    # Shapiro-Wilk on subset (max 5000 per PRD)
    sample_for_shapiro = accuracies[:5000] if n_samples > 5000 else accuracies
    try:
        shapiro_stat, shapiro_p = stats.shapiro(sample_for_shapiro)
    except Exception:
        shapiro_stat, shapiro_p = np.nan, np.nan

    gate_passed = std_acc > GATE_THRESHOLD

    return {
        "n_samples": n_samples,
        "mean": mean_acc,
        "std": std_acc,
        "min": min_acc,
        "max": max_acc,
        "q1": float(q1),
        "q2": float(q2),
        "q3": float(q3),
        "iqr": float(iqr),
        "n_outliers": n_outliers,
        "shapiro_stat": float(shapiro_stat),
        "shapiro_p": float(shapiro_p),
        "gate_passed": gate_passed,
        "gate_threshold": GATE_THRESHOLD
    }


def report_gate(stats: dict) -> str:
    """Format PASS/FAIL message from stats dict."""
    status = "PASS" if stats["gate_passed"] else "FAIL"
    return (
        f"\n{'='*50}\n"
        f"GATE RESULT: {status}\n"
        f"{'='*50}\n"
        f"Observed std(accuracy): {stats['std']:.2f}%\n"
        f"Required threshold:     {stats['gate_threshold']:.1f}%\n"
        f"N samples:              {stats['n_samples']}\n"
        f"Mean accuracy:          {stats['mean']:.2f}%\n"
        f"Range:                  [{stats['min']:.2f}%, {stats['max']:.2f}%]\n"
        f"{'='*50}\n"
    )
