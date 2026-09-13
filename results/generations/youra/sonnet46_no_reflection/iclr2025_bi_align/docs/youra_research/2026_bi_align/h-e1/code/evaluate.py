"""
evaluate.py — H-E1: Metrics extraction, gate check, and result saving.
"""
import json
import os
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats

ModelResult = Any

# ---------------------------------------------------------------------------
# Constants (C-E1-2, C-E1-3)
# ---------------------------------------------------------------------------
GATE_BETA4_MIN: float = 0.0
GATE_OR_MIN: float = 1.10
GATE_PVAL_MAX: float = 0.01
GATE_CI_LO_MIN: float = 1.0

MIN_CLUSTER_COUNT: int = 100
MIN_PAIRS_PER_CLUSTER: int = 2
MIN_SPLIT_SIZE: int = 1000
MIN_DELTA_AIFS_STD: float = 0.01
MIN_EFFECT_SIZE: float = 1e-6

RESULTS_DIR: str = "h-e1/results"
METRICS_FILE: str = "h-e1/results/metrics.json"
MODEL_SUMMARY_FILE: str = "h-e1/results/model_summary.txt"
PAIRS_DF_FILE: str = "h-e1/results/pairs_df.parquet"


# ---------------------------------------------------------------------------
# Metrics Extraction (L-4-1)
# ---------------------------------------------------------------------------

def compute_metrics(
    result_baseline: ModelResult,
    result_proposed: ModelResult,
) -> dict:
    """Extract gate-relevant metrics from fitted models."""
    beta4 = float(result_proposed.params[2])  # type: ignore[arg-type]

    # conf_int() returns numpy ndarray shape (n_params, 2): rows=params, cols=[lo,hi]
    conf = np.array(result_proposed.conf_int())
    ci_lo = float(np.exp(conf[2, 0]))
    ci_hi = float(np.exp(conf[2, 1]))

    # p-value for beta4
    pval = float(result_proposed.pvalues[2])  # type: ignore[arg-type]

    # McFadden R² — ConditionalLogit results don't expose llnull; use llf only
    def mcfadden_r2(result: ModelResult) -> float:
        try:
            llf = float(result.llf)
            llnull = float(result.llnull)
            if llnull == 0:
                return 0.0
            return 1.0 - llf / llnull
        except AttributeError:
            return float("nan")

    # LRT statistic (2 * log-likelihood difference)
    lrt_stat = float(2 * (result_proposed.llf - result_baseline.llf))
    lrt_pval = float(scipy.stats.chi2.sf(lrt_stat, df=1))

    return {
        "beta4": beta4,
        "OR": float(np.exp(beta4)),
        "CI_lo": ci_lo,
        "CI_hi": ci_hi,
        "pval": pval,
        "mcfadden_r2_baseline": mcfadden_r2(result_baseline),
        "mcfadden_r2_proposed": mcfadden_r2(result_proposed),
        "lrt_stat": lrt_stat,
        "lrt_pval": lrt_pval,
    }


def check_gate(metrics: dict) -> bool:
    """Return True iff β₄>0 AND OR>=1.10 AND pval<0.01 AND CI_lo>1.0."""
    return (
        metrics["beta4"] > GATE_BETA4_MIN
        and metrics["OR"] >= GATE_OR_MIN
        and metrics["pval"] < GATE_PVAL_MAX
        and metrics["CI_lo"] > GATE_CI_LO_MIN
    )


# ---------------------------------------------------------------------------
# Output Saving
# ---------------------------------------------------------------------------

def save_metrics(metrics: dict, gate_passed: bool) -> None:
    """Write metrics + gate_passed to h-e1/results/metrics.json."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = dict(metrics)
    output["gate_passed"] = gate_passed
    with open(METRICS_FILE, "w") as f:
        json.dump(output, f, indent=2)


def save_model_summary(result_proposed: ModelResult) -> None:
    """Write result_proposed.summary().as_text() to h-e1/results/model_summary.txt."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(MODEL_SUMMARY_FILE, "w") as f:
        f.write(result_proposed.summary().as_text())


def save_pairs_df(df_pairs: pd.DataFrame) -> None:
    """Write df_pairs to h-e1/results/pairs_df.parquet."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    df_pairs.to_parquet(PAIRS_DF_FILE, index=False)
