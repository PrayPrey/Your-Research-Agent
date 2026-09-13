import pandas as pd
import numpy as np
from typing import Dict, List
import statsmodels.formula.api as smf
from config import CONFIG

def build_results_dataframe(records: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["success"] = df["passed"].astype(int)
    return df

def fit_quadratic_contrast(df: pd.DataFrame) -> Dict:
    df = df.copy()
    df["level_sq"] = df["level"] ** 2

    if df["model"].nunique() > 1:
        md = smf.mixedlm("success ~ level + level_sq + C(model)", df, groups=df["error_id"])
    else:
        md = smf.mixedlm("success ~ level + level_sq", df, groups=df["error_id"])

    fit = md.fit(reml=False, method="powell")
    quad_coef = fit.params["level_sq"]
    quad_pval = fit.pvalues["level_sq"]
    means = df.groupby("level")["success"].mean()
    peak_level = int(means.idxmax())

    return {"quad_coef": quad_coef, "quad_pval": quad_pval, "peak_level": peak_level}

def check_gate_criteria(fit_result: Dict, df: pd.DataFrame) -> Dict:
    means = df.groupby("level")["success"].mean()
    quad_negative = fit_result["quad_coef"] < 0
    quad_significant = fit_result["quad_pval"] < CONFIG["quad_pval_threshold"]
    peak_at_1_or_2 = fit_result["peak_level"] in (1, 2)
    mid = max(means.get(1, 0), means.get(2, 0))
    level1_2_beat_0 = mid > means.get(0, 0)
    level1_2_beat_3 = mid > means.get(3, 0)
    gate_passed = quad_negative and quad_significant and peak_at_1_or_2

    return {
        "gate_passed": gate_passed,
        "quad_negative": quad_negative,
        "quad_significant": quad_significant,
        "peak_at_1_or_2": peak_at_1_or_2,
        "level1_2_beat_0": level1_2_beat_0,
        "level1_2_beat_3": level1_2_beat_3,
        "level_means": {k: float(v) for k, v in means.items()}
    }

def demo():
    np.random.seed(42)
    records = []
    for i in range(100):
        for level in [0, 1, 2, 3]:
            p = {0: 0.3, 1: 0.6, 2: 0.7, 3: 0.4}[level]
            records.append({
                "error_id": f"e_{i}", "model": "m1", "benchmark": "b",
                "level": level, "rep": 0, "passed": np.random.random() < p,
                "attempts_used": 1, "error_type": "IndexError", "first_iter_success": False
            })

    df = build_results_dataframe(records)
    fit_result = fit_quadratic_contrast(df)
    gate = check_gate_criteria(fit_result, df)

    assert fit_result["quad_coef"] < 0, f"Expected negative quad coef, got {fit_result['quad_coef']}"
    assert fit_result["peak_level"] in (1, 2), f"Expected peak at 1 or 2, got {fit_result['peak_level']}"
    print(f"analysis.py demo PASS (quad_coef={fit_result['quad_coef']:.4f}, peak={fit_result['peak_level']})")

if __name__ == "__main__":
    demo()
