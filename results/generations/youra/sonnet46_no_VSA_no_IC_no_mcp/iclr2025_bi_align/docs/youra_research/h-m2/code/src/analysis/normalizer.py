import numpy as np
from scipy import stats
import pandas as pd


def normalize_rm(rm: np.ndarray) -> np.ndarray:
    rm_min, rm_max = rm.min(), rm.max()
    if rm_max <= rm_min:
        raise ValueError(f"Degenerate RM range: min={rm_min}, max={rm_max}")
    return (rm - rm_min) / (rm_max - rm_min)


def compute_gap(rm_norm: np.ndarray, gold: np.ndarray) -> np.ndarray:
    return rm_norm - gold


def run_gap_analysis(df: pd.DataFrame, high_kl_min_positive: int = 3) -> dict:
    df = df.sort_values("kl_budget").reset_index(drop=True)
    kl   = df["kl_budget"].values
    rm   = df["rm_score"].values
    gold = df["gold_preference"].values

    rm_min, rm_max = float(rm.min()), float(rm.max())
    rm_norm = normalize_rm(rm)
    gap = compute_gap(rm_norm, gold)

    median_kl    = float(np.median(kl))
    high_kl_mask = kl > median_kl
    gap_high_kl  = gap[high_kl_mask]

    n_positive_high_kl = int(np.sum(gap_high_kl > 0))
    rho_gap_kl, p_rho_gap = stats.spearmanr(kl, gap)
    rho_gap_kl = float(rho_gap_kl)
    p_rho_gap  = float(p_rho_gap)
    mean_gap_high_kl = float(np.mean(gap_high_kl))
    max_gap          = float(np.max(gap))
    prop_positive    = float(np.mean(gap > 0))

    gate_pass = (n_positive_high_kl >= high_kl_min_positive) and (rho_gap_kl > 0)

    if gate_pass:
        gate_reason = (
            f"PASS: n_positive_high_kl={n_positive_high_kl}/{len(gap_high_kl)} "
            f">= {high_kl_min_positive}; rho_gap_kl={rho_gap_kl:.3f} > 0"
        )
    elif n_positive_high_kl < high_kl_min_positive:
        gate_reason = (
            f"FAIL: only {n_positive_high_kl}/{len(gap_high_kl)} high-KL gaps > 0 "
            f"(need >= {high_kl_min_positive}); recheck normalization range"
        )
    else:
        gate_reason = (
            f"FAIL: rho_gap_kl={rho_gap_kl:.3f} <= 0; "
            f"gap does not grow with KL — check data loading order"
        )

    return {
        "kl": kl, "rm": rm, "gold": gold,
        "rm_norm": rm_norm, "rm_min": rm_min, "rm_max": rm_max,
        "gap": gap,
        "median_kl": median_kl, "high_kl_mask": high_kl_mask,
        "gap_high_kl": gap_high_kl,
        "n_positive_high_kl": n_positive_high_kl,
        "rho_gap_kl": rho_gap_kl, "p_rho_gap": p_rho_gap,
        "mean_gap_high_kl": mean_gap_high_kl,
        "max_gap": max_gap,
        "prop_positive": prop_positive,
        "gate_pass": gate_pass,
        "gate_reason": gate_reason,
        "dataset_n": len(df),
    }
