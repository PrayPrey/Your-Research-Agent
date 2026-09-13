"""Mixed-effects logistic regression for depth-accuracy analysis."""
import warnings

from config import HOLM_N_TESTS


def fit_glmer_rpy2(df: "pd.DataFrame") -> dict:
    """
    Primary GLMM via rpy2 + lme4::glmer.
    df columns: depth_percentile (float), correct (int 0/1), task_id (str).
    Returns {beta, ci_low, ci_high, p_value, method}.
    Raises ImportError if rpy2 or R packages unavailable.
    """
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr

    pandas2ri.activate()

    lme4 = importr("lme4")
    importr("lmerTest")  # shadows lme4::glmer for Satterthwaite df

    r_df = pandas2ri.py2rpy(df)

    formula = ro.Formula("correct ~ depth_percentile + (1|task_id)")
    model = lme4.glmer(formula, data=r_df, family=ro.r("binomial"))

    coef_table = ro.r("summary")(model).rx2("coefficients")
    beta = float(coef_table.rx("depth_percentile", "Estimate")[0])
    p_value = float(coef_table.rx("depth_percentile", "Pr(>|z|)")[0])

    # ponytail: Wald CI for speed; use method="profile" for publication-quality
    ci_matrix = ro.r("confint")(model, parm="beta_", method="Wald")
    ci_row = ci_matrix.rx("depth_percentile", True)
    ci_low = float(ci_row[0])
    ci_high = float(ci_row[1])

    return {
        "beta": beta,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "method": "glmer",
    }


def fit_mixedlm_statsmodels(df: "pd.DataFrame") -> dict:
    """
    Fallback: linear mixed model (approximation for binary outcome).
    df columns: depth_percentile (float), correct (int 0/1), task_id (str).
    """
    import statsmodels.formula.api as smf

    # ponytail: LMM not logistic; fine for PoC, replace with glmer if R available
    model = smf.mixedlm("correct ~ depth_percentile", data=df, groups=df["task_id"])
    result = model.fit(reml=False)

    beta = float(result.params["depth_percentile"])
    ci = result.conf_int()
    ci_low = float(ci.loc["depth_percentile", 0])
    ci_high = float(ci.loc["depth_percentile", 1])
    p_value = float(result.pvalues["depth_percentile"])

    return {
        "beta": beta,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "method": "mixedlm_approx",
        "approximation_warning": True,
    }


def fit_model(records: list[dict], model_label: str) -> dict:
    """
    Strategy dispatcher: try rpy2 glmer, fall back to statsmodels mixedlm.
    records must have: depth_percentile (float), correct (int), category (str).
    """
    import pandas as pd

    df = pd.DataFrame({
        "depth_percentile": [r["depth_percentile"] for r in records],
        "correct": [int(r["correct"]) for r in records],
        # ponytail: only 2 groups; random intercept weakly identified; glmer may warn
        "task_id": [r["category"] for r in records],
    })

    if df["correct"].nunique() < 2:
        raise ValueError(
            f"[{model_label}] Only one outcome class in retrieval subset — cannot fit regression"
        )

    try:
        result = fit_glmer_rpy2(df)
        print(f"[Regression] {model_label}: glmer fitted, β={result['beta']:.4f}")
    except Exception as e:
        warnings.warn(
            f"[{model_label}] rpy2/glmer failed ({type(e).__name__}: {e}), "
            "falling back to statsmodels MixedLM"
        )
        result = fit_mixedlm_statsmodels(df)
        print(f"[Regression] {model_label}: mixedlm_approx fitted, β={result['beta']:.4f}")

    result["model_label"] = model_label
    return result


def apply_holm_correction(p_values: list[float]) -> list[float]:
    """
    Holm-Bonferroni correction for exactly 2 tests.
    Returns corrected p-values in same order as input.
    """
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    corrected = [0.0] * n
    prev_corrected = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        multiplier = n - rank
        corrected[orig_idx] = max(prev_corrected, min(1.0, p * multiplier))
        prev_corrected = corrected[orig_idx]
    return corrected


def run_regression(
    mohawk_records: list[dict],
    lawcat_records: list[dict],
) -> dict:
    """
    Fit regression for both models, apply Holm correction.
    Returns full results dict ready for gate evaluation.
    """
    ssm_result = fit_model(mohawk_records, "mohawk_ssm")
    lawcat_result = fit_model(lawcat_records, "lawcat")

    raw_pvals = [ssm_result["p_value"], lawcat_result["p_value"]]
    corrected = apply_holm_correction(raw_pvals)

    return {
        "mohawk_ssm": ssm_result,
        "lawcat": lawcat_result,
        "holm_corrected_p_values": {
            "mohawk_ssm": corrected[0],
            "lawcat": corrected[1],
        },
    }
