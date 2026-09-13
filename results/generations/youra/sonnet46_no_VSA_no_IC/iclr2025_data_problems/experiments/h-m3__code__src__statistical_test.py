"""Fisher z-test, Holm-Bonferroni correction, and gate verification."""
from __future__ import annotations
import numpy as np
from scipy import stats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def fisher_z_test(rho1: float, rho2: float, n: int) -> tuple[float, float]:
    """One-tailed Fisher z-test: H1: rho1 > rho2. Returns (z_stat, p_one_tailed)."""
    r1 = np.clip(rho1, -0.9999, 0.9999)
    r2 = np.clip(rho2, -0.9999, 0.9999)
    z1, z2 = np.arctanh(r1), np.arctanh(r2)
    se = np.sqrt(2.0 / (n - 3))
    z_stat = (z1 - z2) / se
    p_one_tailed = float(1 - stats.norm.cdf(z_stat))
    return float(z_stat), p_one_tailed


def apply_holm_bonferroni(p_values: list[float], alpha: float = config.FISHER_ALPHA) -> list[bool]:
    """Holm-Bonferroni step-down correction. Returns list of reject-H0 booleans."""
    m = len(p_values)
    sorted_idx = np.argsort(p_values)
    reject = [False] * m
    for k, idx in enumerate(sorted_idx):
        threshold = alpha / (m - k)
        if p_values[idx] <= threshold:
            reject[idx] = True
        else:
            break  # stop at first non-rejection
    return reject


def verify_mechanism_activated(
    results_by_model_size: dict,
) -> tuple[bool, dict]:
    """Gate: P1 directional count >= 2 of 3 model sizes.
    results_by_model_size: {model_size: CorrelationMatrix}"""
    wiki = config.FOCAL_DOMAINS["wikipedia"]
    books = config.FOCAL_DOMAINS["books"]

    p1_confirmed = 0
    p2_confirmed = 0

    for model_size, matrix in results_by_model_size.items():
        rho_wm = matrix[wiki]["mmlu"].rho
        rho_wh = matrix[wiki]["hellaswag"].rho
        rho_bh = matrix[books]["hellaswag"].rho
        rho_bm = matrix[books]["mmlu"].rho
        n_valid = matrix[wiki]["mmlu"].n
        assert n_valid >= 100, f"Floor filter removed too many checkpoints: {n_valid}"

        if rho_wm > rho_wh:
            p1_confirmed += 1
        if rho_bh > rho_bm:
            p2_confirmed += 1

    indicators = {
        "p1_directional_count": p1_confirmed,
        "p2_directional_count": p2_confirmed,
        "p1_gate_passed": p1_confirmed >= 2,
        "p2_gate_passed": p2_confirmed >= 2,
    }
    return indicators["p1_gate_passed"], indicators


def run_all_tests(
    focal_by_model: dict,
    matrices_by_model: dict,
) -> dict:
    """Run P1 + P2 Fisher z-tests for all model sizes. Returns full test results."""
    wiki = config.FOCAL_DOMAINS["wikipedia"]
    books = config.FOCAL_DOMAINS["books"]
    results = {}
    p1_pvals = []
    p2_pvals = []
    p1_model_map = {}
    p2_model_map = {}

    for model_size, matrix in matrices_by_model.items():
        n = matrix[wiki]["mmlu"].n
        rho_wm = matrix[wiki]["mmlu"].rho
        rho_wh = matrix[wiki]["hellaswag"].rho
        rho_bh = matrix[books]["hellaswag"].rho
        rho_bm = matrix[books]["mmlu"].rho

        z_p1, p_p1 = fisher_z_test(rho_wm, rho_wh, n)
        z_p2, p_p2 = fisher_z_test(rho_bh, rho_bm, n)

        p1_pvals.append(p_p1)
        p2_pvals.append(p_p2)
        p1_model_map[model_size] = len(p1_pvals) - 1
        p2_model_map[model_size] = len(p2_pvals) - 1

        results[model_size] = {
            "n_valid": n,
            "p1": {"z_stat": z_p1, "p_one_tailed": p_p1, "rho_wm": rho_wm, "rho_wh": rho_wh},
            "p2": {"z_stat": z_p2, "p_one_tailed": p_p2, "rho_bh": rho_bh, "rho_bm": rho_bm},
        }

    all_pvals = p1_pvals + p2_pvals
    hb_reject = apply_holm_bonferroni(all_pvals, config.FISHER_ALPHA)

    for model_size in matrices_by_model:
        results[model_size]["p1"]["holm_reject"] = hb_reject[p1_model_map[model_size]]
        results[model_size]["p2"]["holm_reject"] = hb_reject[len(p1_pvals) + p2_model_map[model_size]]

    return results
