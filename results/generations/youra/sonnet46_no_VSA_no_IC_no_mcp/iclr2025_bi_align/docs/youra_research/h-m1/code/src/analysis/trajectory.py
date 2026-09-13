"""H-M1: Trajectory analysis — monotonicity test, peak-reversal detection, divergence."""
import numpy as np
import pandas as pd
from scipy import stats


RHO_THRESHOLD = 0.8
P_THRESHOLD = 0.05
PEAK_KL_MIN = 1.0
PEAK_KL_MAX = 9.0


def run_rm_monotonicity_test(kl: np.ndarray, rm: np.ndarray) -> dict:
    if len(kl) < 3:
        return {
            "rho_rm_kl": float("nan"), "p_rho": float("nan"),
            "monotone_pass": False,
            "reason": f"Insufficient data: N={len(kl)} (need >= 3)",
        }

    rho, p_rho = stats.spearmanr(kl, rm)

    if np.isnan(rho):
        return {
            "rho_rm_kl": float("nan"), "p_rho": float("nan"),
            "monotone_pass": False,
            "reason": "FAIL: constant RM values — Spearman undefined",
        }

    monotone_pass = (rho > RHO_THRESHOLD) and (p_rho < P_THRESHOLD)

    if monotone_pass:
        reason = f"PASS: rho={rho:.3f} > {RHO_THRESHOLD}, p={p_rho:.4f} < {P_THRESHOLD}"
    elif rho <= RHO_THRESHOLD:
        reason = f"FAIL: rho={rho:.3f} <= {RHO_THRESHOLD} (re-digitize Figure 3)"
    else:
        reason = f"FAIL: p={p_rho:.4f} >= {P_THRESHOLD} (insufficient N)"

    return {
        "rho_rm_kl": float(rho),
        "p_rho": float(p_rho),
        "monotone_pass": monotone_pass,
        "reason": reason,
    }


def detect_peak_reversal(kl: np.ndarray, gold: np.ndarray) -> dict:
    if len(gold) < 3:
        return {
            "peak_idx": -1, "peak_kl": float("nan"),
            "reversal_confirmed": False, "peak_kl_valid": False,
            "reason": f"Insufficient data: N={len(gold)}",
        }

    peak_idx = int(np.argmax(gold))
    peak_kl = float(kl[peak_idx])
    reversal_confirmed = bool(gold[peak_idx] > gold[-1])
    peak_kl_valid = PEAK_KL_MIN <= peak_kl <= PEAK_KL_MAX

    if reversal_confirmed and peak_kl_valid:
        reason = (
            f"PASS: peak at KL={peak_kl:.2f} nats (valid [{PEAK_KL_MIN},{PEAK_KL_MAX}]), "
            f"gold[peak]={gold[peak_idx]:.3f} > gold[final]={gold[-1]:.3f}"
        )
    elif not reversal_confirmed:
        reason = (
            f"FAIL: no reversal — gold[peak]={gold[peak_idx]:.3f} <= gold[final]={gold[-1]:.3f}; "
            f"re-digitize gold preference curve"
        )
    else:
        reason = (
            f"WARNING: reversal confirmed but peak_kl={peak_kl:.2f} outside "
            f"[{PEAK_KL_MIN},{PEAK_KL_MAX}]; possible axis calibration error"
        )

    return {
        "peak_idx": peak_idx,
        "peak_kl": peak_kl,
        "reversal_confirmed": reversal_confirmed,
        "peak_kl_valid": peak_kl_valid,
        "reason": reason,
    }


def compute_divergence(rm: np.ndarray, gold: np.ndarray) -> dict:
    divergence_curve = rm - gold
    divergence_final = float(divergence_curve[-1])
    divergence_max = float(divergence_curve.max())
    divergence_positive = divergence_final > 0.0

    if divergence_positive:
        reason = f"PASS: divergence_final={divergence_final:.3f} > 0 (RM exceeds gold at max KL)"
    else:
        reason = (
            f"WARNING: divergence_final={divergence_final:.3f} <= 0; "
            f"unexpected (gold >= RM at final KL)"
        )

    return {
        "divergence_curve": divergence_curve,
        "divergence_final": divergence_final,
        "divergence_positive": divergence_positive,
        "divergence_max": divergence_max,
        "reason": reason,
    }


def run_analysis(df: pd.DataFrame, dataset_name: str = "Coste2023") -> dict:
    df = df.sort_values("kl_budget").reset_index(drop=True)
    kl = df["kl_budget"].values
    rm = df["rm_score"].values
    gold = df["gold_preference"].values

    mono = run_rm_monotonicity_test(kl, rm)
    peak = detect_peak_reversal(kl, gold)
    div = compute_divergence(rm, gold)

    gate_pass = mono["monotone_pass"] and peak["reversal_confirmed"]

    return {
        "dataset": dataset_name,
        "n_kl_levels": len(kl),
        "baseline_rm": float(rm[0]),
        "baseline_gold": float(gold[0]),
        "gate_pass": gate_pass,
        # monotonicity
        "rho_rm_kl": mono["rho_rm_kl"],
        "p_rho": mono["p_rho"],
        "monotone_pass": mono["monotone_pass"],
        "mono_reason": mono["reason"],
        # peak reversal
        "peak_idx": peak["peak_idx"],
        "peak_kl": peak["peak_kl"],
        "reversal_confirmed": peak["reversal_confirmed"],
        "peak_kl_valid": peak["peak_kl_valid"],
        "peak_reason": peak["reason"],
        # divergence
        "divergence_curve": div["divergence_curve"],
        "divergence_final": div["divergence_final"],
        "divergence_positive": div["divergence_positive"],
        "divergence_max": div["divergence_max"],
        "div_reason": div["reason"],
    }
