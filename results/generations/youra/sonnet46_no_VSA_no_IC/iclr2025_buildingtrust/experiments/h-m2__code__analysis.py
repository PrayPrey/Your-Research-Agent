"""H-M2 analysis: raw rho, partial rho x3, delta_rho, Fisher z-test."""
import json
import logging
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

from config import DELTA_RHO_GATE, N_COMMON_MIN, RESULTS_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def compute_raw_rho_all(df: pd.DataFrame) -> dict:
    """
    Compute raw (unadjusted) Spearman rho for all 3 dimension pairs.

    Args:
        df: DataFrame with required score columns

    Returns:
        dict: {rho_fair_raw, rho_advglue_raw, rho_anli_raw, delta_rho_raw, n}
    """
    rho_fair    = spearmanr(df["bbq_disambig"],  df["bbq_ambig"]).statistic
    rho_advglue = spearmanr(df["glue_score"],    df["advglue_score"]).statistic
    rho_anli    = spearmanr(df["anli_r1_score"], df["anli_r3_score"]).statistic
    delta_raw   = float(rho_fair) - float(np.mean([rho_advglue, rho_anli]))
    return {
        "rho_fair_raw":    float(rho_fair),
        "rho_advglue_raw": float(rho_advglue),
        "rho_anli_raw":    float(rho_anli),
        "delta_rho_raw":   float(delta_raw),
        "n":               len(df),
    }


def compute_partial_rho(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str = "mmlu"
) -> dict:
    """
    Compute partial Spearman rho between x and y controlling for covar via pingouin.

    Args:
        df: DataFrame with columns [x, y, covar], N >= N_COMMON_MIN
        x: predictor column name
        y: outcome column name
        covar: control variable column name (default "mmlu")

    Returns:
        dict: {rho, p_value, ci95, n, x, y, covar}

    Raises:
        AssertionError: if covar not in df.columns
        ValueError: if p_value is NaN or |rho| > 0.999
    """
    import pingouin as pg
    assert covar in df.columns, f"covar '{covar}' not in DataFrame"

    sub = df[[x, y, covar]].dropna()
    result = pg.partial_corr(
        data=sub,
        x=x,
        y=y,
        covar=[covar],
        method="spearman",
        alternative="two-sided",
    ).round(6)

    rho     = float(result["r"].iloc[0])
    p_value = float(result["p_val"].iloc[0])
    ci95    = result["CI95"].iloc[0].tolist()
    n       = int(result["n"].iloc[0])

    if pd.isna(p_value):
        raise ValueError(
            f"p_value is NaN for ({x}, {y}, covar={covar}) — constant scores?"
        )
    if abs(rho) > 0.999:
        raise ValueError(
            f"|rho|={abs(rho):.4f} > 0.999 for ({x},{y}) — Fisher z undefined; "
            "fallback to Kendall tau"
        )

    logging.info(f"partial_rho({x},{y},covar={covar}): rho={rho:.3f}, p={p_value:.4f}, n={n}")
    return {"rho": rho, "p_value": p_value, "ci95": ci95, "n": n,
            "x": x, "y": y, "covar": covar}


def fisher_z_test_difference(
    rho1: float,
    rho2: float,
    n: int
) -> dict:
    """
    Fisher z-test for the difference between two independent correlation coefficients.
    Implements psinger/CorrelationStats independent_corr formula (inline).

    Args:
        rho1: partial Spearman rho_fairness (MMLU-controlled)
        rho2: rho_robust_mean (mean of rho_AdvGLUE and rho_ANLI)
        n: sample size (N_common_robust; same for all pairs)

    Returns:
        dict: {z_stat, p_value_two_tailed, z_rho1, z_rho2, se_diff}

    Raises:
        ValueError: if |rho1| >= 1.0 or |rho2| >= 1.0 or n <= 3
    """
    if abs(rho1) >= 1.0:
        raise ValueError(f"|rho1|={abs(rho1)} >= 1.0 — Fisher z undefined")
    if abs(rho2) >= 1.0:
        raise ValueError(f"|rho2|={abs(rho2)} >= 1.0 — Fisher z undefined")
    if n <= 3:
        raise ValueError(f"n={n} <= 3 — insufficient for Fisher z (denominator n-3 <= 0)")

    z_rho1  = 0.5 * np.log((1 + rho1) / (1 - rho1))   # atanh(rho1)
    z_rho2  = 0.5 * np.log((1 + rho2) / (1 - rho2))   # atanh(rho2)
    se_diff = np.sqrt(2 / (n - 3))                       # same N for all pairs
    z_stat  = (z_rho1 - z_rho2) / se_diff
    p_val   = 2 * (1 - norm.cdf(abs(z_stat)))            # two-tailed, exploratory

    return {
        "z_stat":             float(z_stat),
        "p_value_two_tailed": float(p_val),
        "z_rho1":             float(z_rho1),
        "z_rho2":             float(z_rho2),
        "se_diff":            float(se_diff),
    }


def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Orchestrate complete H-M2 statistical analysis.

    Args:
        df: DataFrame from build_master_dataframe(), shape (N_common_robust, 9)

    Returns:
        dict with all metrics, gate_directional bool, and sensitivity analysis

    Side effects:
        Saves results to RESULTS_DIR/results.json
        Logs gate status: "H-M2 analysis: delta_rho=... (threshold: 0.2), direction: PASS/FAIL"
    """
    # Step 1: Raw baseline
    raw = compute_raw_rho_all(df)

    # Steps 2-4: Partial rho per dimension (MMLU-controlled, two-sided)
    res_fair = compute_partial_rho(df, x="bbq_disambig",  y="bbq_ambig",     covar="mmlu")
    res_adv  = compute_partial_rho(df, x="glue_score",    y="advglue_score",  covar="mmlu")
    res_anli = compute_partial_rho(df, x="anli_r1_score", y="anli_r3_score",  covar="mmlu")

    # Step 5: delta_rho
    rho_robust_mean = float(np.mean([res_adv["rho"], res_anli["rho"]]))
    delta_rho       = res_fair["rho"] - rho_robust_mean

    # Step 6: Fisher z-test for difference
    fisher = fisher_z_test_difference(
        rho1=res_fair["rho"],
        rho2=rho_robust_mean,
        n=res_fair["n"]
    )

    # Step 7: Gate evaluation
    gate_directional = bool(delta_rho >= DELTA_RHO_GATE)
    secondary_both   = (res_adv["rho"] < res_fair["rho"]) and (res_anli["rho"] < res_fair["rho"])
    label = "PASS" if gate_directional else "FAIL"
    msg = f"H-M2 analysis: delta_rho={delta_rho:.3f} (threshold: {DELTA_RHO_GATE}), direction: {label}"
    logging.info(msg)
    print(msg)

    # Step 8: Sensitivity (Winogrande control)
    sensitivity_wino = None
    if "winogrande" in df.columns:
        wino_df = df.dropna(subset=["winogrande"])
        if len(wino_df) >= N_COMMON_MIN:
            res_fair_w = compute_partial_rho(wino_df, "bbq_disambig",  "bbq_ambig",     "winogrande")
            res_adv_w  = compute_partial_rho(wino_df, "glue_score",    "advglue_score",  "winogrande")
            res_anli_w = compute_partial_rho(wino_df, "anli_r1_score", "anli_r3_score",  "winogrande")
            rho_rob_w  = float(np.mean([res_adv_w["rho"], res_anli_w["rho"]]))
            delta_wino = res_fair_w["rho"] - rho_rob_w
            sensitivity_wino = {
                "rho_fairness":    res_fair_w,
                "rho_advglue":     res_adv_w,
                "rho_anli":        res_anli_w,
                "rho_robust_mean": rho_rob_w,
                "delta_rho":       delta_wino,
            }
            logging.info(f"Sensitivity (Winogrande): delta_rho={delta_wino:.3f}, N={len(wino_df)}")
        else:
            logging.warning(f"Winogrande N={len(wino_df)} < {N_COMMON_MIN}, sensitivity skipped")

    results = {
        "raw":             raw,
        "rho_fairness":    res_fair,
        "rho_advglue":     res_adv,
        "rho_anli":        res_anli,
        "rho_robust_mean": rho_robust_mean,
        "delta_rho":       delta_rho,
        "fisher_z":        fisher,
        "gate_directional": gate_directional,
        "secondary_both":  secondary_both,
        "sensitivity_wino": sensitivity_wino,
        "n":               res_fair["n"],
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logging.info(f"Results saved to {out_path}")

    return results


def evaluate_gate(delta_rho: float) -> bool:
    """Return delta_rho >= DELTA_RHO_GATE."""
    return delta_rho >= DELTA_RHO_GATE
