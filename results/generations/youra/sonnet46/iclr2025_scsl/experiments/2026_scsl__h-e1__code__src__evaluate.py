"""
evaluate.py - compute_metrics(), gate_check(), verify_mechanism_activated(), save_results()
"""

import json
import datetime
import numpy as np
from sklearn.metrics import roc_auc_score


GATE_RATIO   = 3.0
GATE_AUC     = 0.70
GATE_BALANCE = 0.10
TOP_K_FRACTION = 0.25
EPSILON = 1e-8


def compute_metrics(
    g_tilde: np.ndarray,       # (N,) float32
    g_raw: np.ndarray,         # (N,) float32
    h_norm: np.ndarray,        # (N,) float32
    group_labels: np.ndarray,  # (N,) int64 — {0,1,2,3}
    class_labels: np.ndarray,  # (N,) int64 — {0,1}
) -> dict:
    """
    Computes primary gate metrics and secondary per-group statistics.

    minority = G1 (group==1, landbird/water) | G2 (group==2, waterbird/land)
    majority = G0 (group==0) | G3 (group==3)

    Returns dict with:
      ratio, auc, balance_deviation  (primary gate metrics)
      g_tilde_mean_G{0-3}, h_norm_mean_G{0-3}, g_raw_mean_G{0-3}  (secondary)
      features_count, h_norm_std_ratio  (for verify_mechanism_activated)
    """
    N = len(g_tilde)
    minority_mask = (group_labels == 1) | (group_labels == 2)  # (N,) bool

    # 1. Ratio: minority mean g_tilde / majority mean g_tilde
    minority_mean = float(g_tilde[minority_mask].mean())
    majority_mean = float(g_tilde[~minority_mask].mean())
    ratio = minority_mean / (majority_mean + EPSILON)

    # 2. AUC: g_tilde predicting binary minority membership
    binary_labels = minority_mask.astype(np.int32)
    auc = float(roc_auc_score(binary_labels, g_tilde))

    # 3. Balance deviation: top-25% by g_tilde, within-class group balance
    top_k = max(1, int(TOP_K_FRACTION * N))
    top_k_idx = np.argsort(g_tilde)[-top_k:]
    selected_y = class_labels[top_k_idx]
    selected_g = group_labels[top_k_idx]

    deviations = []
    for y_val in [0, 1]:
        y_mask = (selected_y == y_val)
        if y_mask.sum() > 0:
            place_bits = selected_g[y_mask] % 2   # place in {0,1}
            counts = np.bincount(place_bits, minlength=2)
            p_place = counts / counts.sum()
            deviations.append(float(np.max(np.abs(p_place - 0.5))))
    balance_deviation = float(max(deviations)) if deviations else 0.0

    # 4. Per-group secondary metrics
    per_group_g_tilde = {}
    per_group_h_norm = {}
    per_group_g_raw = {}
    for g in range(4):
        mask_g = group_labels == g
        per_group_g_tilde[g] = float(g_tilde[mask_g].mean()) if mask_g.sum() > 0 else float('nan')
        per_group_h_norm[g]  = float(h_norm[mask_g].mean())  if mask_g.sum() > 0 else float('nan')
        per_group_g_raw[g]   = float(g_raw[mask_g].mean())   if mask_g.sum() > 0 else float('nan')

    # 5. h_norm_std_ratio for mechanism verification
    h_norm_mean_all = float(h_norm.mean())
    h_norm_std_all  = float(h_norm.std())
    h_norm_std_ratio = h_norm_std_all / (h_norm_mean_all + EPSILON)

    metrics = {
        'ratio': ratio,
        'auc': auc,
        'balance_deviation': balance_deviation,
        'features_count': int(N),
        'h_norm_std_ratio': h_norm_std_ratio,
        **{f'g_tilde_mean_G{g}': v for g, v in per_group_g_tilde.items()},
        **{f'h_norm_mean_G{g}':  v for g, v in per_group_h_norm.items()},
        **{f'g_raw_mean_G{g}':   v for g, v in per_group_g_raw.items()},
    }
    return metrics


def gate_check(metrics: dict) -> tuple:
    """
    Check primary gate criteria.

    Returns: (all_pass: bool, criteria: dict[str, bool])
    """
    criteria = {
        'ratio':             metrics['ratio'] >= GATE_RATIO,
        'auc':               metrics['auc'] > GATE_AUC,
        'balance_deviation': metrics['balance_deviation'] <= GATE_BALANCE,
    }
    all_pass = all(criteria.values())
    return all_pass, criteria


def verify_mechanism_activated(epoch_results: dict) -> tuple:
    """
    Check that the gradient norm mechanism is actually firing and providing signal.

    Indicators:
      hook_fired             : features_count > 0
      ratio_above_chance     : ratio > 1.5
      auc_above_random       : auc > 0.55
      feature_norms_equalized: h_norm_std_ratio < 0.5

    Returns: (all_activated: bool, indicators: dict[str, bool])
    """
    indicators = {
        'hook_fired':              epoch_results.get('features_count', 0) > 0,
        'ratio_above_chance':      epoch_results.get('ratio', 0.0) > 1.5,
        'auc_above_random':        epoch_results.get('auc', 0.0) > 0.55,
        'feature_norms_equalized': epoch_results.get('h_norm_std_ratio', 1.0) < 0.5,
    }
    all_activated = all(indicators.values())
    return all_activated, indicators


def save_results(
    per_epoch_metrics: dict,   # {epoch: metrics_dict}
    gate_results: dict,        # {'all_pass': bool, 'criteria': dict}
    secondary_metrics: dict,
    output_path: str,
) -> None:
    """
    Write results.json.

    Schema (FR-7.1):
    {
      "hypothesis_id": "H-E1",
      "generated_at": "<ISO datetime>",
      "gate_pass": <bool>,
      "gate_criteria": {...},
      "primary_epoch": 5,
      "per_epoch_metrics": {epoch: {...}},
      "secondary_metrics": {...}
    }
    """
    results = {
        'hypothesis_id': 'H-E1',
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'gate_pass': gate_results.get('all_pass', False),
        'gate_criteria': gate_results.get('criteria', {}),
        'primary_epoch': 5,
        'per_epoch_metrics': {str(k): v for k, v in per_epoch_metrics.items()},
        'secondary_metrics': secondary_metrics,
    }
    import os
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")
