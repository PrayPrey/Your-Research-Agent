"""H-M3 analysis: per-pair partial Spearman, Fisher z, rank reversals, gate."""
import json
import logging

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import norm, spearmanr

from config import ALPHA, N_COMMON_MIN, RANDOM_SEED, RANK_REVERSAL_MIN_SHIFT, RESULTS_JSON, RHO_THRESHOLD

log = logging.getLogger(__name__)


def compute_partial_spearman(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    covar_col: str = "mmlu",
    alternative: str = "greater",
    n_bootstrap: int = 1000,
) -> dict:
    assert all(c in df.columns for c in [x_col, y_col, covar_col])
    df_clean = df[[x_col, y_col, covar_col]].dropna()
    n = len(df_clean)
    log.info("compute_partial_spearman: N=%d, pair=(%s, %s)", n, x_col, y_col)

    result_df = pg.partial_corr(data=df_clean, x=x_col, y=y_col, covar=covar_col, method="spearman", alternative=alternative)
    rho = float(result_df["r"].iloc[0])
    p_col = "p-val" if "p-val" in result_df.columns else "p_val"
    p_asymptotic = float(result_df[p_col].iloc[0])

    np.random.seed(RANDOM_SEED)
    x_vals = df_clean[x_col].values
    y_vals = df_clean[y_col].values
    boot_rhos = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        r, _ = spearmanr(x_vals[idx], y_vals[idx])
        boot_rhos.append(r)
    ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])

    return {"rho": rho, "p_asymptotic": p_asymptotic, "ci_lower": float(ci_lower), "ci_upper": float(ci_upper), "n": n}


def fisher_z_test_vs_threshold(rho: float, n: int, threshold: float = RHO_THRESHOLD, alternative: str = "less") -> dict:
    z_obs = np.arctanh(np.clip(rho, -0.9999, 0.9999))
    z_thresh = np.arctanh(threshold)
    se = 1.0 / np.sqrt(n - 3)
    z_stat = (z_obs - z_thresh) / se
    p = float(norm.cdf(z_stat))
    return {"z": float(z_stat), "p": p, "significant": p < ALPHA}


def count_rank_reversals(df: pd.DataFrame, id_col: str, ood_col: str, min_shift: int = RANK_REVERSAL_MIN_SHIFT) -> int:
    ranks_id = df[id_col].rank(ascending=False)
    ranks_ood = df[ood_col].rank(ascending=False)
    return int((abs(ranks_id - ranks_ood) >= min_shift).sum())


def verify_mechanism_activated(df: pd.DataFrame, results: dict) -> tuple:
    required_cols = ["glue_score", "advglue_score", "anli_r1_score", "anli_r3_score", "mmlu"]
    indicators = {
        "data_complete": all(c in df.columns for c in required_cols),
        "n_sufficient": len(df.dropna(subset=required_cols)) >= N_COMMON_MIN,
        "advglue_computed": "rho_AdvGLUE" in results and results["rho_AdvGLUE"] is not None,
        "anli_computed": "rho_ANLI" in results and results["rho_ANLI"] is not None,
        "pairs_differ": abs(results.get("rho_AdvGLUE", 0) - results.get("rho_ANLI", 0)) > 0.001,
        "reversals_counted": "reversals_AdvGLUE" in results and "reversals_ANLI" in results,
    }
    all_ok = all(indicators.values())
    log.info("Mechanism indicators: %s", indicators)
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        log.warning("Failed indicators: %s", failed)
    return (all_ok, indicators)


def evaluate_gate(rho_advglue: float, p_advglue: float, rho_anli: float, p_anli: float, threshold: float = RHO_THRESHOLD) -> bool:
    advglue_ok = (rho_advglue < threshold) or (p_advglue >= ALPHA)
    anli_ok = (rho_anli < threshold) or (p_anli >= ALPHA)
    gate_passed = advglue_ok and anli_ok
    log.info(
        "Gate: AdvGLUE=%s, ANLI=%s => %s",
        "PASS" if advglue_ok else "FAIL",
        "PASS" if anli_ok else "FAIL",
        "PASS" if gate_passed else "FAIL",
    )
    return gate_passed


def run_full_analysis(df: pd.DataFrame, rho_fairness: float) -> dict:
    r_adv = compute_partial_spearman(df, "glue_score", "advglue_score")
    log.info("rho_AdvGLUE=%.4f, p=%.4f, CI=[%.3f, %.3f]", r_adv["rho"], r_adv["p_asymptotic"], r_adv["ci_lower"], r_adv["ci_upper"])

    r_anli = compute_partial_spearman(df, "anli_r1_score", "anli_r3_score")
    log.info("rho_ANLI=%.4f, p=%.4f, CI=[%.3f, %.3f]", r_anli["rho"], r_anli["p_asymptotic"], r_anli["ci_lower"], r_anli["ci_upper"])

    fz_adv = fisher_z_test_vs_threshold(r_adv["rho"], r_adv["n"])
    fz_anli = fisher_z_test_vs_threshold(r_anli["rho"], r_anli["n"])

    rev_adv = count_rank_reversals(df, "glue_score", "advglue_score")
    rev_anli = count_rank_reversals(df, "anli_r1_score", "anli_r3_score")

    results = {
        "rho_AdvGLUE": r_adv["rho"],
        "p_AdvGLUE": r_adv["p_asymptotic"],
        "ci_AdvGLUE": [r_adv["ci_lower"], r_adv["ci_upper"]],
        "z_AdvGLUE": fz_adv["z"],
        "p_z_AdvGLUE": fz_adv["p"],
        "sig_AdvGLUE": fz_adv["significant"],
        "rho_ANLI": r_anli["rho"],
        "p_ANLI": r_anli["p_asymptotic"],
        "ci_ANLI": [r_anli["ci_lower"], r_anli["ci_upper"]],
        "z_ANLI": fz_anli["z"],
        "p_z_ANLI": fz_anli["p"],
        "sig_ANLI": fz_anli["significant"],
        "reversals_AdvGLUE": rev_adv,
        "reversals_ANLI": rev_anli,
        "rho_fairness_HM1": rho_fairness,
        "n": r_adv["n"],
    }

    mech_ok, indicators = verify_mechanism_activated(df, results)
    gate = evaluate_gate(r_adv["rho"], r_adv["p_asymptotic"], r_anli["rho"], r_anli["p_asymptotic"])
    results["gate_passed"] = gate
    results["mechanism_ok"] = mech_ok
    results["mechanism_indicators"] = indicators

    RESULTS_JSON.write_text(json.dumps(results, indent=2))
    log.info("Results saved to %s", RESULTS_JSON)

    return results
