import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multitest import multipletests
from typing import Dict, Tuple, List
from config import CONFIG

def two_way_anova(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[float]]:
    model = ols("passed_int ~ C(format) * C(model)", data=df).fit()
    anova_table = anova_lm(model, typ=CONFIG["stats"]["anova_ss_type"])

    pvals = []
    for idx in ["C(format)", "C(model)", "C(format):C(model)"]:
        if idx in anova_table.index:
            pvals.append(anova_table.loc[idx, "PR(>F)"])

    _, pvals_adj, _, _ = multipletests(pvals, method=CONFIG["stats"]["correction_method"])
    return anova_table, list(pvals_adj)

def eta_squared(anova_table: pd.DataFrame, effect_row: str) -> float:
    ss_effect = anova_table.loc[effect_row, "sum_sq"]
    ss_total = anova_table["sum_sq"].sum()
    return ss_effect / ss_total

def partial_eta_squared(anova_table: pd.DataFrame, effect_row: str) -> float:
    ss_effect = anova_table.loc[effect_row, "sum_sq"]
    ss_resid = anova_table.loc["Residual", "sum_sq"]
    return ss_effect / (ss_effect + ss_resid)

def cohens_d_proportions(p1: float, n1: int, p2: float, n2: int) -> float:
    pooled_var = (p1 * (1 - p1) + p2 * (1 - p2)) / 2
    if pooled_var <= 0:
        return 0.0
    return (p1 - p2) / np.sqrt(pooled_var)

def wilson_ci_diff(p1: float, n1: int, p2: float, n2: int, alpha: float = 0.05) -> Tuple[float, float]:
    diff = p1 - p2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = scipy_stats.norm.ppf(1 - alpha / 2)
    return diff - z * se, diff + z * se

def simple_effect(df: pd.DataFrame, model_key: str) -> Dict:
    model_df = df[df["model"] == model_key]
    structured = model_df[model_df["format"] == "structured"]
    raw = model_df[model_df["format"] == "raw"]

    p_struct = structured["passed"].mean()
    p_raw = raw["passed"].mean()
    n_struct = len(structured)
    n_raw = len(raw)

    effect = p_struct - p_raw
    d = cohens_d_proportions(p_struct, n_struct, p_raw, n_raw)
    ci_low, ci_high = wilson_ci_diff(p_struct, n_struct, p_raw, n_raw)

    se = np.sqrt(p_struct * (1 - p_struct) / n_struct + p_raw * (1 - p_raw) / n_raw)

    return {
        "effect": effect,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "d": d,
        "p_structured": p_struct,
        "p_raw": p_raw,
        "n_structured": n_struct,
        "n_raw": n_raw,
        "se": se
    }

def linear_trend_contrast(effects: Dict[str, Dict]) -> Dict:
    ordered_keys = ["7B", "34B", "gpt4"]
    weights = np.array([-1, 0, 1])

    effect_vals = np.array([effects[k]["effect"] for k in ordered_keys])
    variances = np.array([effects[k]["se"] ** 2 for k in ordered_keys])

    L = np.sum(weights * effect_vals)
    se_L = np.sqrt(np.sum(weights ** 2 * variances))

    if se_L > 0:
        t_stat = L / se_L
        df_approx = sum(effects[k]["n_structured"] + effects[k]["n_raw"] for k in ordered_keys) - 6
        p_two = 2 * scipy_stats.t.sf(abs(t_stat), df_approx)
        p_one = scipy_stats.t.sf(t_stat, df_approx)
    else:
        t_stat, p_two, p_one = 0.0, 1.0, 0.5

    pattern_confirmed = (effect_vals[0] > effect_vals[1] > effect_vals[2])

    return {
        "contrast_estimate": L,
        "t": t_stat,
        "p_two_sided": p_two,
        "p_one_sided": p_one,
        "pattern_confirmed": pattern_confirmed,
        "effects_ordered": list(effect_vals)
    }

def compute_all_stats(df: pd.DataFrame) -> Dict:
    anova_table, pvals_adj = two_way_anova(df)

    interaction_row = "C(format):C(model)"
    interaction_p = anova_table.loc[interaction_row, "PR(>F)"]
    interaction_eta2 = eta_squared(anova_table, interaction_row)
    interaction_partial_eta2 = partial_eta_squared(anova_table, interaction_row)

    effects = {}
    for model_key in ["7B", "34B", "gpt4"]:
        effects[model_key] = simple_effect(df, model_key)

    contrast = linear_trend_contrast(effects)

    pass_criteria = (
        pvals_adj[2] < CONFIG["stats"]["alpha"] and
        interaction_eta2 > 0.01 and
        contrast["pattern_confirmed"]
    )

    return {
        "anova_table": anova_table.to_dict(),
        "interaction_p": interaction_p,
        "interaction_p_adj": pvals_adj[2],
        "interaction_eta2": interaction_eta2,
        "interaction_partial_eta2": interaction_partial_eta2,
        "simple_effects": effects,
        "contrast": contrast,
        "pvals_adjusted": {"format": pvals_adj[0], "model": pvals_adj[1], "interaction": pvals_adj[2]},
        "pass_criteria": pass_criteria
    }
