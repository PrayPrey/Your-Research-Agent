# Mediation analysis module for h-m1
import os
import json
import numpy as np
import pandas as pd
from scipy.stats import norm
from config import PATHS, N_BOOTSTRAP, RANDOM_SEED


def compute_sobel_z(coef_a: float, se_a: float, coef_b: float, se_b: float) -> tuple:
    """Sobel test: z = a*b / sqrt(b^2*se_a^2 + a^2*se_b^2). Returns (z, p)."""
    se_indirect = np.sqrt(coef_b**2 * se_a**2 + coef_a**2 * se_b**2)
    if se_indirect == 0:
        return 0.0, 1.0
    z = (coef_a * coef_b) / se_indirect
    p = 2 * (1 - norm.cdf(abs(z)))
    return float(z), float(p)


def run_mediation_analysis(df: pd.DataFrame) -> dict:
    """
    Run mediation analysis: metadata_score -> prep_entropy -> iqr
    Uses pingouin.mediation_analysis with bootstrap CI.
    """
    try:
        from pingouin import mediation_analysis
    except ImportError:
        raise ImportError("pingouin required: pip install pingouin")

    df = df.copy()
    df["algo_family_code"] = pd.Categorical(df["algo_family"]).codes

    result = mediation_analysis(
        data=df,
        x="metadata_score",
        m="prep_entropy",
        y="iqr",
        covar=["stability", "log_popularity", "algo_family_code"],
        alpha=0.05,
        n_boot=N_BOOTSTRAP,
        seed=RANDOM_SEED
    )

    def get_row(path_name):
        row = result[result["path"] == path_name]
        if row.empty:
            return {"coef": 0.0, "se": 0.0, "pval": 1.0, "ci_lower": 0.0, "ci_upper": 0.0}
        return {
            "coef": float(row["coef"].values[0]),
            "se": float(row["se"].values[0]) if "se" in row.columns else 0.0,
            "pval": float(row["pval"].values[0]) if "pval" in row.columns else 1.0,
            "ci_lower": float(row["CI[2.5%]"].values[0]) if "CI[2.5%]" in row.columns else 0.0,
            "ci_upper": float(row["CI[97.5%]"].values[0]) if "CI[97.5%]" in row.columns else 0.0,
        }

    a = get_row("prep_entropy ~ X")  # Path a: X -> M
    b = get_row("Y ~ prep_entropy")   # Path b: M -> Y
    indirect = get_row("Indirect")
    total = get_row("Total")
    direct = get_row("Direct")

    sobel_z, sobel_p = compute_sobel_z(a["coef"], a["se"], b["coef"], b["se"])

    proportion_mediated = 0.0
    if total["coef"] != 0:
        proportion_mediated = abs(indirect["coef"] / total["coef"])

    return {
        "indirect_effect": indirect["coef"],
        "indirect_se": indirect["se"],
        "indirect_ci_lower": indirect["ci_lower"],
        "indirect_ci_upper": indirect["ci_upper"],
        "indirect_pval": indirect["pval"],
        "total_effect": total["coef"],
        "direct_effect": direct["coef"],
        "proportion_mediated": proportion_mediated,
        "sobel_z": sobel_z,
        "sobel_p": sobel_p,
        "path_a": a["coef"],
        "path_a_se": a["se"],
        "path_b": b["coef"],
        "path_b_se": b["se"],
    }


def save_mediation_results(result: dict, path: str) -> None:
    """Save mediation results to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved mediation results to {path}")
