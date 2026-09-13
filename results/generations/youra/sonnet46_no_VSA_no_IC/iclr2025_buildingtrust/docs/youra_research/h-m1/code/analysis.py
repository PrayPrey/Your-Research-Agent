"""H-M1 statistical analysis: raw and partial Spearman correlations."""
import json
import logging
from pathlib import Path

import pandas as pd

import importlib.util as _ilu, pathlib as _pl
_cfg_spec = _ilu.spec_from_file_location("h_m1_config", _pl.Path(__file__).parent / "config.py")
_cfg = _ilu.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg)
GATE_RHO = _cfg.GATE_RHO
GATE_P = _cfg.GATE_P
RESULTS_DIR = _cfg.RESULTS_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")


def compute_raw_spearman(df: pd.DataFrame) -> dict:
    """
    Raw (unadjusted) Spearman rho between BBQ-Disambig and BBQ-Ambig.

    Returns: {raw_rho, raw_p, n}
    """
    from scipy.stats import spearmanr
    result = spearmanr(df["bbq_disambig"], df["bbq_ambig"])
    return {"raw_rho": float(result.statistic), "raw_p": float(result.pvalue), "n": len(df)}


def compute_partial_spearman(df: pd.DataFrame, covar: str = "mmlu") -> dict:
    """
    Partial Spearman rho between BBQ-Disambig and BBQ-Ambig controlling for covar.

    Returns: {partial_rho, p_value, ci95, n, covar}
    Raises:
        AssertionError: if covar not in df.columns
        ValueError: if p_value is NaN
    """
    import pingouin as pg
    assert covar in df.columns, f"covar '{covar}' not in columns"

    sub = df[["bbq_disambig", "bbq_ambig", covar]].dropna()
    result = pg.partial_corr(
        data=sub,
        x="bbq_disambig",
        y="bbq_ambig",
        covar=[covar],
        method="spearman",
        alternative="greater",
    ).round(6)

    partial_rho = float(result["r"].iloc[0])
    # pingouin 0.6.x uses "p_val"; older versions used "p-val"
    p_col = "p_val" if "p_val" in result.columns else "p-val"
    p_value = float(result[p_col].iloc[0])
    ci95_col = "CI95" if "CI95" in result.columns else "CI95%"
    ci95 = result[ci95_col].iloc[0].tolist()
    n = int(result["n"].iloc[0])

    if pd.isna(p_value):
        raise ValueError("p_value is NaN — check for constant score columns")

    # Mechanism verification
    assert n >= 10, f"Insufficient N: {n}"
    assert -1 <= partial_rho <= 1, f"Invalid rho: {partial_rho}"
    assert 0 <= p_value <= 1, f"Invalid p-value: {p_value}"

    logging.info(f"Partial Spearman rho computed: rho={partial_rho:.3f}, p={p_value:.4f}, n={n}, covar={covar}")
    return {"partial_rho": partial_rho, "p_value": p_value, "ci95": ci95, "n": n, "covar": covar}


def evaluate_gate(partial_rho: float, p_value: float) -> bool:
    """Return True if partial_rho > GATE_RHO and p_value < GATE_P."""
    return partial_rho > GATE_RHO and p_value < GATE_P


def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Full H-M1 analysis: raw + partial (MMLU) + sensitivity (Winogrande) + gate.

    Saves results to RESULTS_DIR/results.json.
    Returns consolidated results dict.
    """
    raw = compute_raw_spearman(df)
    primary = compute_partial_spearman(df, covar="mmlu")

    wino_sub = df.dropna(subset=["winogrande"])
    if len(wino_sub) >= 10:
        sensitivity = compute_partial_spearman(wino_sub, covar="winogrande")
    else:
        sensitivity = None
        logging.warning(f"Winogrande N={len(wino_sub)} < 10, sensitivity skipped")

    gate_pass = evaluate_gate(primary["partial_rho"], primary["p_value"])
    mmlu_explains = raw["raw_rho"] > primary["partial_rho"]

    results = {
        "raw": raw,
        "primary": primary,
        "sensitivity": sensitivity,
        "gate_pass": gate_pass,
        "mmlu_explains_variance": mmlu_explains,
        "partial_rho": primary["partial_rho"],
        "p_value": primary["p_value"],
        "n": primary["n"],
        "ci95": primary["ci95"],
    }

    # Print mechanism activation log (required by 02c verification protocol)
    print(f"Partial Spearman rho computed: rho={primary['partial_rho']:.3f}, p={primary['p_value']:.4f}, n={primary['n']}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
