"""Pearson r, Kendall tau, gate evaluation with R6 fallback."""
import math
import numpy as np
from typing import Dict, Tuple
from scipy.stats import pearsonr, kendalltau


def compute_pearson_r(
    sparsity: np.ndarray,
    accuracy_drops: np.ndarray,
    sensitive_mask: np.ndarray,
) -> Tuple[float, float]:
    """Pearson r on sensitive layers only. Returns (r, p_value).
    Returns (nan, nan) if fewer than 3 sensitive layers.
    """
    sensitive_indices = np.where(sensitive_mask)[0]
    if len(sensitive_indices) < 3:
        return float("nan"), float("nan")

    sp = sparsity[sensitive_indices]
    drops = accuracy_drops[sensitive_indices]
    r, p = pearsonr(sp, drops)
    return float(r), float(p)


def compute_kendall_tau(
    sparsity: np.ndarray,
    adalora_ranks: np.ndarray,
) -> Tuple[float, float]:
    """Kendall's tau (variant='b') across all 32 layers.
    Returns (tau, p_value).
    """
    tau, p = kendalltau(sparsity, adalora_ranks, variant="b")
    return float(tau), float(p)


def check_r6_fallback(n_sensitive_sst2: int, cfg) -> bool:
    """Returns True if SST-2 has fewer than r6_min_sensitive_layers sensitive layers."""
    return n_sensitive_sst2 < cfg.r6_min_sensitive_layers


def evaluate_gate(
    pearson_r_sst2: float,
    pearson_r_mnli: float,
    kendall_tau_sst2: float,
    kendall_tau_mnli: float,
    unique_var_sparsity: float,
    p_value_sparsity_beta: float,
    n_sensitive_sst2: int,
    cfg,
) -> Dict:
    """Evaluate all gate conditions including R6 fallback.

    Returns {gate_pearson, gate_tau, gate_spectral, gate_pass, r6_fallback, all_metrics}.
    """
    r6_fallback = check_r6_fallback(n_sensitive_sst2, cfg)

    if r6_fallback:
        print(f"[GATE] R6 fallback triggered: n_sensitive_sst2={n_sensitive_sst2} < {cfg.r6_min_sensitive_layers}")
        gate_pearson = (not math.isnan(pearson_r_mnli)) and (pearson_r_mnli <= cfg.pearson_r_threshold)
        gate_tau = kendall_tau_mnli >= cfg.kendall_tau_threshold
    else:
        p_sst2 = pearson_r_sst2 if not math.isnan(pearson_r_sst2) else 0.0
        p_mnli = pearson_r_mnli if not math.isnan(pearson_r_mnli) else 0.0
        gate_pearson = (p_sst2 <= cfg.pearson_r_threshold and
                        p_mnli <= cfg.pearson_r_threshold)
        gate_tau = (kendall_tau_sst2 >= cfg.kendall_tau_threshold and
                    kendall_tau_mnli >= cfg.kendall_tau_threshold)

    gate_spectral = (unique_var_sparsity >= cfg.unique_var_threshold and
                     p_value_sparsity_beta < cfg.p_value_threshold)

    gate_pass = gate_pearson and gate_tau and gate_spectral

    all_metrics = {
        "pearson_r_sst2": pearson_r_sst2,
        "pearson_r_mnli": pearson_r_mnli,
        "kendall_tau_sst2": kendall_tau_sst2,
        "kendall_tau_mnli": kendall_tau_mnli,
        "unique_var_sparsity": unique_var_sparsity,
        "p_value_sparsity_beta": p_value_sparsity_beta,
        "n_sensitive_sst2": n_sensitive_sst2,
    }

    status = "PASS" if gate_pass else "FAIL"
    print(f"[GATE] MUST_WORK: {status}")
    print(f"  Pearson r (SST-2={pearson_r_sst2:.4f}, MNLI={pearson_r_mnli:.4f}, threshold={cfg.pearson_r_threshold}): {'PASS' if gate_pearson else 'FAIL'}")
    print(f"  Kendall tau (SST-2={kendall_tau_sst2:.4f}, MNLI={kendall_tau_mnli:.4f}, threshold={cfg.kendall_tau_threshold}): {'PASS' if gate_tau else 'FAIL'}")
    print(f"  Spectral (unique_var={unique_var_sparsity:.4f}, p={p_value_sparsity_beta:.4f}): {'PASS' if gate_spectral else 'FAIL'}")

    return {
        "gate_pearson": gate_pearson,
        "gate_tau": gate_tau,
        "gate_spectral": gate_spectral,
        "gate_pass": gate_pass,
        "r6_fallback": r6_fallback,
        "all_metrics": all_metrics,
    }
