"""H-M3 Evaluation: Metrics, Mechanism Verification, Comparison"""
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score


def compute_metrics(y_val: np.ndarray, probs: np.ndarray) -> dict:
    """Compute AUROC and accuracy."""
    auroc = roc_auc_score(y_val, probs)
    y_pred = (probs >= 0.5).astype(int)
    accuracy = accuracy_score(y_val, y_pred)
    return {"auroc": float(auroc), "accuracy": float(accuracy)}


def verify_mechanism(probe, X_val: np.ndarray, y_val: np.ndarray,
                     weight_norm_min: float = 1e-6,
                     pred_std_min: float = 0.01,
                     auroc_min: float = 0.55) -> dict:
    """Verify probe mechanism is working (non-trivial weights, non-constant preds, AUROC > random)."""
    weights = probe.clf.coef_[0]
    weight_norm = float(np.linalg.norm(weights))

    probs = probe.predict_proba(X_val)
    pred_std = float(probs.std())

    auroc = roc_auc_score(y_val, probs)

    checks = {
        "weight_norm": weight_norm,
        "weight_norm_pass": weight_norm > weight_norm_min,
        "pred_std": pred_std,
        "pred_std_pass": pred_std > pred_std_min,
        "auroc": float(auroc),
        "auroc_pass": auroc > auroc_min
    }
    checks["all_pass"] = all([checks["weight_norm_pass"], checks["pred_std_pass"], checks["auroc_pass"]])
    return checks


def compare_to_baseline(probe_auroc: float, baseline_auroc: float) -> dict:
    """Compare probe vs baseline AUROC."""
    delta = probe_auroc - baseline_auroc
    return {
        "probe_auroc": probe_auroc,
        "baseline_auroc": baseline_auroc,
        "delta": delta,
        "exceeds_baseline_by_20": delta > 0.20
    }
