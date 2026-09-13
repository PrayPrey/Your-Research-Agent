"""evaluate.py — Statistical testing, mechanism verification, gate condition for H-E1."""
import json
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


def test_discriminability(
    saturated_signals: np.ndarray,
    healthy_signals: np.ndarray,
) -> dict:
    """Mann-Whitney U + Cohen's d + AUC for one domain."""
    saturated_signals = np.asarray(saturated_signals, dtype=float)
    healthy_signals = np.asarray(healthy_signals, dtype=float)
    n_sat = len(saturated_signals)
    n_healthy = len(healthy_signals)

    if n_sat == 0 or n_healthy == 0:
        return {"u_stat": 0.0, "p_value": 1.0, "cohens_d": 0.0,
                "auc": 0.5, "n_sat": n_sat, "n_healthy": n_healthy}

    u_stat, p_value = stats.mannwhitneyu(
        saturated_signals, healthy_signals, alternative="two-sided"
    )
    auc = float(u_stat) / (n_sat * n_healthy)

    mean_diff = np.mean(saturated_signals) - np.mean(healthy_signals)
    var_sat = np.var(saturated_signals, ddof=1) if n_sat > 1 else 0.0
    var_healthy = np.var(healthy_signals, ddof=1) if n_healthy > 1 else 0.0
    pooled_std = np.sqrt(
        ((n_sat - 1) * var_sat + (n_healthy - 1) * var_healthy)
        / max(n_sat + n_healthy - 2, 1)
    )
    cohens_d = float(mean_diff) / (float(pooled_std) + 1e-9)

    return {
        "u_stat": float(u_stat),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "auc": float(auc),
        "n_sat": int(n_sat),
        "n_healthy": int(n_healthy),
    }


def evaluate_domain(
    domain_signals: pd.DataFrame,
    baseline_probs: np.ndarray,
    domain: str,
) -> dict:
    """Full domain evaluation: discriminability + baseline comparison."""
    sat_mask = domain_signals["label"] == "saturated"
    healthy_mask = domain_signals["label"] == "healthy"

    sat_signals = domain_signals.loc[sat_mask, "hd_signal"].values
    healthy_signals = domain_signals.loc[healthy_mask, "hd_signal"].values

    disc = test_discriminability(sat_signals, healthy_signals)

    # Compute signal AUC using all benchmarks (sat=1, healthy=0)
    labeled = domain_signals[domain_signals["label"].isin(["saturated", "healthy"])].copy()
    labels_bin = (labeled["label"] == "saturated").astype(int).values
    signals = labeled["hd_signal"].values

    if len(np.unique(labels_bin)) > 1 and len(signals) > 0:
        from sklearn.metrics import roc_auc_score
        signal_auc = float(roc_auc_score(labels_bin, signals))
        # ROC curve data
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(labels_bin, signals)
        roc_data = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
    else:
        signal_auc = 0.5
        roc_data = {"fpr": [0.0, 1.0], "tpr": [0.0, 1.0]}

    # Baseline AUC
    if baseline_probs is not None and len(baseline_probs) == len(domain_signals):
        baseline_labeled = baseline_probs[domain_signals["label"].isin(["saturated", "healthy"]).values]
        if len(np.unique(labels_bin)) > 1 and len(baseline_labeled) > 0:
            from sklearn.metrics import roc_auc_score, roc_curve
            baseline_auc = float(roc_auc_score(labels_bin, baseline_labeled))
            fpr_b, tpr_b, _ = roc_curve(labels_bin, baseline_labeled)
            baseline_roc = {"fpr": fpr_b.tolist(), "tpr": tpr_b.tolist()}
        else:
            baseline_auc = 0.5
            baseline_roc = {"fpr": [0.0, 1.0], "tpr": [0.0, 1.0]}
    else:
        baseline_auc = 0.5
        baseline_roc = {"fpr": [0.0, 1.0], "tpr": [0.0, 1.0]}

    passes_gate = disc["p_value"] < 0.05 and abs(disc["cohens_d"]) > 0.5

    return {
        "domain": domain,
        "discriminability": disc,
        "baseline_auc": baseline_auc,
        "signal_auc": signal_auc,
        "passes_gate": passes_gate,
        "roc_data": roc_data,
        "baseline_roc": baseline_roc,
        "n_benchmarks": len(domain_signals["benchmark"].unique()),
        "n_saturated": int(sat_mask.sum()),
        "n_healthy": int(healthy_mask.sum()),
    }


def verify_mechanism_activated(domain_results: dict) -> tuple:
    """Check 4 indicators per domain."""
    indicators = {}
    all_activated = True

    for domain, res in domain_results.items():
        disc = res.get("discriminability", {})
        signal_auc = res.get("signal_auc", 0.0)
        baseline_auc = res.get("baseline_auc", 0.0)
        ind = {
            "p_lt_005": disc.get("p_value", 1.0) < 0.05,
            "d_gt_05": abs(disc.get("cohens_d", 0.0)) > 0.5,
            "auc_gt_065": disc.get("auc", 0.5) > 0.65,
            "n_sufficient": disc.get("n_sat", 0) >= 15 and disc.get("n_healthy", 0) >= 15,
        }
        indicators[domain] = ind
        if not all(ind.values()):
            all_activated = False

    return (all_activated, indicators)


def check_gate_condition(domain_results: dict) -> tuple:
    """PASS if p<0.05 AND Cohen's d>0.5 in >=2 of 3 domains."""
    gate_details = {}
    n_passing = 0

    for domain, res in domain_results.items():
        disc = res.get("discriminability", {})
        p_val = disc.get("p_value", 1.0)
        cohens_d = disc.get("cohens_d", 0.0)
        passes = p_val < 0.05 and abs(cohens_d) > 0.5
        gate_details[domain] = {
            "p_value": p_val,
            "cohens_d": cohens_d,
            "passes": passes,
        }
        if passes:
            n_passing += 1

    passed = n_passing >= 2
    gate_details["summary"] = {
        "n_passing": n_passing,
        "threshold": 2,
        "passed": passed,
    }
    return (passed, gate_details)


def run_temporal_test(
    panel: pd.DataFrame,
    domain: str,
    lookbacks: list = None,
) -> dict:
    """Test discriminability at multiple lookback horizons."""
    if lookbacks is None:
        lookbacks = [6, 12, 18, 24]

    from signal_compute import compute_domain_signals

    results = {}
    for lb in lookbacks:
        try:
            signals = compute_domain_signals(panel, domain, lookback_months=lb)
            sat = signals.loc[signals["label"] == "saturated", "hd_signal"].values
            healthy = signals.loc[signals["label"] == "healthy", "hd_signal"].values
            if len(sat) > 0 and len(healthy) > 0:
                disc = test_discriminability(sat, healthy)
            else:
                disc = {"p_value": 1.0, "cohens_d": 0.0, "auc": 0.5,
                        "u_stat": 0.0, "n_sat": 0, "n_healthy": 0}
        except Exception as e:
            disc = {"p_value": 1.0, "cohens_d": 0.0, "auc": 0.5,
                    "u_stat": 0.0, "n_sat": 0, "n_healthy": 0, "error": str(e)}
        results[lb] = disc

    return results


def save_results(results: dict, output_path: str) -> None:
    """Save results dict as JSON to output_path."""
    import os
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    def _serialize(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_serialize(v) for v in obj]
        return obj

    with open(output_path, "w") as f:
        json.dump(_serialize(results), f, indent=2)
    print(f"Results saved to {output_path}")
