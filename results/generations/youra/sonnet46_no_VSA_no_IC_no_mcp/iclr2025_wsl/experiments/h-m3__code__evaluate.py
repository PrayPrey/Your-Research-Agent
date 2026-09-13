"""H-M3 evaluation: Spearman rho, bootstrap CI, gate checks P1 and P2."""
import numpy as np
from scipy.stats import spearmanr


def bootstrap_spearman(y_pred, y_true, n_boot=1000, seed=42):
    """
    Returns (rho_obs, ci_lo, ci_hi).
    """
    y_pred = np.asarray(y_pred)
    y_true = np.asarray(y_true)
    # Remove NaN pairs
    mask = np.isfinite(y_pred) & np.isfinite(y_true)
    y_pred, y_true = y_pred[mask], y_true[mask]
    N = len(y_pred)
    rho_obs = float(spearmanr(y_pred, y_true).statistic)
    rng = np.random.default_rng(seed)
    boot_idx = rng.integers(0, N, (n_boot, N))
    boot_rhos = [float(spearmanr(y_pred[idx], y_true[idx]).statistic) for idx in boot_idx]
    return rho_obs, float(np.percentile(boot_rhos, 2.5)), float(np.percentile(boot_rhos, 97.5))


def aggregate_seeds(per_seed_rhos):
    """
    per_seed_rhos: list of {condition: {label: (rho, ci_lo, ci_hi)}}
    Returns: {condition: {label: {rho_mean, ci_lo, ci_hi}}}
    """
    if not per_seed_rhos:
        return {}
    conditions = list(per_seed_rhos[0].keys())
    labels = list(per_seed_rhos[0][conditions[0]].keys())
    result = {}
    for cond in conditions:
        result[cond] = {}
        for label in labels:
            rhos = [s[cond][label][0] for s in per_seed_rhos]
            ci_los = [s[cond][label][1] for s in per_seed_rhos]
            ci_his = [s[cond][label][2] for s in per_seed_rhos]
            result[cond][label] = {
                'rho_mean': float(np.mean(rhos)),
                'ci_lo': float(np.mean(ci_los)),
                'ci_hi': float(np.mean(ci_his)),
            }
    return result


def check_p1(rho_D, ci_D, rho_A, ci_A, delta_threshold=0.05):
    """
    P1: delta_rho >= 0.05 AND CI of delta_rho excludes 0.
    ci_D, ci_A: (ci_lo, ci_hi) tuples
    """
    delta_rho = rho_D - rho_A
    ci_delta_lo = ci_D[0] - ci_A[1]
    ci_delta_hi = ci_D[1] - ci_A[0]
    ci_excludes_zero = ci_delta_lo > 0
    delta_ge_threshold = delta_rho >= delta_threshold
    return {
        'pass': bool(ci_excludes_zero and delta_ge_threshold),
        'delta_rho': float(delta_rho),
        'ci_excludes_zero': bool(ci_excludes_zero),
        'delta_ge_threshold': bool(delta_ge_threshold),
        'ci_delta': (float(ci_delta_lo), float(ci_delta_hi)),
    }


def check_p2(rho_table):
    """
    P2: rho_D > rho_E on >= 2/3 tasks.
    rho_table: {condition: {label: rho_mean or float}}
    """
    labels = list(rho_table.get('D', {}).keys())
    per_task = {}
    for label in labels:
        rho_d = rho_table['D'][label]
        rho_e = rho_table['E'][label]
        if isinstance(rho_d, dict):
            rho_d = rho_d['rho_mean']
        if isinstance(rho_e, dict):
            rho_e = rho_e['rho_mean']
        per_task[label] = bool(rho_d > rho_e)
    n_pass = sum(per_task.values())
    n_required = 2
    return {
        'pass': n_pass >= n_required,
        'n_pass': n_pass,
        'n_required': n_required,
        'per_task': per_task,
    }
