"""H-M2 Model Consistency: Cross-model analysis."""
import numpy as np
from loader import MODEL_FIELDS, MODEL_KEY_MAP
from threshold_sweep import high_conf_rate


def per_model_rates(records: list, threshold: float = 0.7) -> dict:
    """
    Compute high-conf rate per model.
    Returns {model_field: {"A": rate, "B": rate, "diff": float}}.
    """
    results = {}
    for field in MODEL_FIELDS:
        rate_a = 0
        rate_b = 0
        n_a = 0
        n_b = 0

        for t in records:
            conf = t.get(field, 0)
            if t["task_type"] == "A":
                n_a += 1
                if conf >= threshold:
                    rate_a += 1
            else:
                n_b += 1
                if conf >= threshold:
                    rate_b += 1

        r_a = rate_a / n_a if n_a > 0 else 0
        r_b = rate_b / n_b if n_b > 0 else 0

        results[field] = {
            "rate_A": r_a,
            "rate_B": r_b,
            "diff": abs(r_a - r_b),
            "n_A": n_a,
            "n_B": n_b,
        }

    return results


def consistency_score(per_model: dict) -> dict:
    """
    Compute consistency metrics across models.
    Returns std dev of rate_difference and whether all models pass gate.
    """
    diffs = [m["diff"] for m in per_model.values()]
    gate_passes = [m["diff"] < 0.15 for m in per_model.values()]

    return {
        "std_rate_difference": float(np.std(diffs)),
        "mean_rate_difference": float(np.mean(diffs)),
        "same_gate_pass": all(gate_passes),
        "n_models_pass": sum(gate_passes),
        "n_models": len(diffs),
    }
