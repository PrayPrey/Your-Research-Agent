from typing import Dict
import numpy as np
import pandas as pd
import pingouin as pg


def build_icc_dataframe(
    sparsity_profiles: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """Build long-format DataFrame: columns [layer, distribution, sparsity], 128 rows.
    Expected: 4 distributions × 32 layers = 128 rows."""
    rows = []
    for dist_name, profile in sparsity_profiles.items():
        for layer_idx, val in enumerate(profile):
            rows.append({
                "layer": layer_idx,
                "distribution": dist_name,
                "sparsity": float(val),
            })
    return pd.DataFrame(rows)


def compute_icc3k(
    sparsity_profiles: Dict[str, np.ndarray]
) -> Dict[str, float]:
    """Run pingouin.intraclass_corr, extract ICC3k value and 95% CI.
    Returns: {icc3k: float, ci_lower: float, ci_upper: float}"""
    df = build_icc_dataframe(sparsity_profiles)
    icc_results = pg.intraclass_corr(
        data=df,
        targets="layer",
        raters="distribution",
        ratings="sparsity",
    )
    # pingouin >=0.5.4 uses Type="ICC(C,k)" for consistency coefficient (two-way mixed, k raters)
    # which corresponds to what literature calls ICC3k
    icc_type = "ICC(C,k)"
    subset = icc_results[icc_results["Type"] == icc_type]
    if subset.empty:
        # fallback: try any k-form
        subset = icc_results[icc_results["Type"].str.contains(r"\(.*,k\)", regex=True)]
    if subset.empty:
        raise ValueError(f"ICC(C,k) not found in pingouin results. Types: {icc_results['Type'].tolist()}")
    row = subset.iloc[0]
    icc_val = float(row["ICC"])
    # Column name is "CI95" in pingouin >=0.5.4 (was "CI95%" in older versions)
    ci_col = "CI95" if "CI95" in row.index else "CI95%"
    ci = row[ci_col]
    return {
        "icc3k": icc_val,
        "ci_lower": float(ci[0]),
        "ci_upper": float(ci[1]),
    }


def compute_icc_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]]
) -> Dict[float, Dict[str, float]]:
    """Compute ICC3k for each epsilon value. Returns {epsilon: icc_result_dict}."""
    return {eps: compute_icc3k(profiles) for eps, profiles in sparsity_by_epsilon.items()}
