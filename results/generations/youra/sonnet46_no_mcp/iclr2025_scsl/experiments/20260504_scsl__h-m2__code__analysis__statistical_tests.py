import numpy as np
from typing import Dict, Any


def apply_bonferroni_correction(
    p_values: Dict[str, float],
    alpha: float = 0.05,
) -> Dict[str, float]:
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests
    return {k: corrected_alpha for k in p_values}


def evaluate_gate(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    alpha: float = 0.05,
) -> Dict[str, Any]:
    metrics = ["fft", "variance", "separability"]
    per_metric_result = {}
    n_pass_wb = 0
    n_pass_cb = 0

    for metric in metrics:
        wb = waterbirds_results.get(metric, {})
        cb = celeba_results.get(metric, {})

        direction_ok_wb = bool(wb.get("direction_correct", False))
        p_ok_wb = float(wb.get("p_value", 1.0)) < alpha
        direction_ok_cb = bool(cb.get("direction_correct", False))

        if direction_ok_wb and p_ok_wb:
            n_pass_wb += 1
        if direction_ok_cb:
            n_pass_cb += 1

        per_metric_result[metric] = {
            "waterbirds": {
                "direction_correct": direction_ok_wb,
                "p_value": wb.get("p_value"),
                "p_significant": p_ok_wb,
                "passes_gate": direction_ok_wb and p_ok_wb,
            },
            "celeba": {
                "direction_correct": direction_ok_cb,
                "p_value": cb.get("p_value"),
            },
        }

    gate_pass = n_pass_wb >= 2
    gate_label = "PASS" if gate_pass else "FAIL"

    return {
        "gate_pass": gate_pass,
        "n_metrics_pass_waterbirds": n_pass_wb,
        "n_metrics_pass_celeba": n_pass_cb,
        "gate_label": gate_label,
        "per_metric_result": per_metric_result,
    }


def compute_complexity_delta_ci(
    spurious_vals: np.ndarray,
    core_vals: np.ndarray,
    confidence: float = 0.95,
    n_bootstrap: int = 10000,
) -> Dict[str, float]:
    rng = np.random.RandomState(42)
    delta_obs = float(np.mean(core_vals) - np.mean(spurious_vals))

    boot_deltas = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        s_boot = rng.choice(spurious_vals, size=len(spurious_vals), replace=True)
        c_boot = rng.choice(core_vals, size=len(core_vals), replace=True)
        boot_deltas[i] = np.mean(c_boot) - np.mean(s_boot)

    alpha = 1.0 - confidence
    ci_low = float(np.percentile(boot_deltas, 100 * alpha / 2))
    ci_high = float(np.percentile(boot_deltas, 100 * (1 - alpha / 2)))

    return {
        "delta": delta_obs,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n_bootstrap": n_bootstrap,
        "significant": ci_low > 0,
    }
