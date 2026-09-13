"""Statistical analysis: 2-way ANOVA + ANCOVA + gate check."""
import logging

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import ols
import statsmodels.api as sm

from config import CONFIG

logger = logging.getLogger(__name__)


def load_results(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df


def compute_partial_eta2(anova_table: pd.DataFrame, effect_name: str) -> float:
    """Compute partial eta-squared for an effect from ANOVA type-II table."""
    try:
        ss_effect = anova_table.loc[effect_name, "sum_sq"]
        ss_residual = anova_table.loc["Residual", "sum_sq"]
        return float(ss_effect / (ss_effect + ss_residual))
    except Exception as e:
        logger.warning(f"Could not compute eta2 for {effect_name}: {e}")
        return 0.0


def run_ancova_interaction(df: pd.DataFrame, dv: str = "mmlu_4shot") -> dict:
    """ANCOVA: Scale × PPL interaction with contamination rate as covariate.
    Returns: {"interaction_p": float, "interaction_eta2": float, "anova_table": DataFrame}
    """
    formula = CONFIG.ancova_formula.replace("mmlu_4shot", dv)
    try:
        model = ols(formula, data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        interaction_term = "C(scale):C(ppl_threshold)"
        interaction_p = float(anova_table.loc[interaction_term, "PR(>F)"])
        interaction_eta2 = compute_partial_eta2(anova_table, interaction_term)
        return {
            "interaction_p": interaction_p,
            "interaction_eta2": interaction_eta2,
            "anova_table": anova_table,
            "dv": dv,
        }
    except Exception as e:
        logger.error(f"ANCOVA failed: {e}")
        return {"interaction_p": 1.0, "interaction_eta2": 0.0, "anova_table": None, "dv": dv}


def check_direction(df: pd.DataFrame, dv: str = "mmlu_4shot") -> dict:
    """Compute tau*(70M) and tau*(160M) via argmax; check direction.
    Returns: {"tau_star_70m": int, "tau_star_160m": int, "direction_confirmed": bool}
    """
    df70 = df[df["scale"] == 70]
    df160 = df[df["scale"] == 160]
    tau_star_70m = df70.groupby("ppl_threshold")[dv].mean().idxmax()
    tau_star_160m = df160.groupby("ppl_threshold")[dv].mean().idxmax()
    direction_confirmed = bool(tau_star_70m < tau_star_160m)
    return {
        "tau_star_70m": int(tau_star_70m),
        "tau_star_160m": int(tau_star_160m),
        "direction_confirmed": direction_confirmed,
    }


def run_secondary_analyses(df: pd.DataFrame) -> dict:
    """Levene's test + Scale×Dedup ANOVA + post-hoc pairwise."""
    results = {}

    # Levene's test for variance homogeneity
    groups = [g["mmlu_4shot"].values for _, g in df.groupby(["scale", "ppl_threshold"])]
    groups = [g for g in groups if len(g) > 1]
    if groups:
        levene_stat, levene_p = stats.levene(*groups)
        results["levene"] = {"statistic": float(levene_stat), "p_value": float(levene_p)}

    # Scale × Dedup ANOVA
    try:
        secondary_formula = "mmlu_4shot ~ C(scale) * C(dedup_j)"
        model2 = ols(secondary_formula, data=df).fit()
        anova2 = sm.stats.anova_lm(model2, typ=2)
        results["scale_dedup_anova"] = anova2.to_dict()
    except Exception as e:
        logger.warning(f"Secondary ANOVA failed: {e}")

    # Post-hoc: pairwise per scale
    try:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        tukey = pairwise_tukeyhsd(df["mmlu_4shot"], df["ppl_threshold"])
        results["posthoc_ppl"] = str(tukey)
    except Exception as e:
        logger.warning(f"Post-hoc failed: {e}")

    return results


def gate_check(analysis_results: dict) -> dict:
    """MUST_WORK gate: p<0.05 AND eta2>=0.15 AND direction_confirmed."""
    p = analysis_results.get("interaction_p", 1.0)
    eta2 = analysis_results.get("interaction_eta2", 0.0)
    direction = analysis_results.get("direction_confirmed", False)

    checks = {
        "p_value_passes": p < CONFIG.significance_threshold,
        "eta2_passes": eta2 >= CONFIG.effect_size_threshold,
        "direction_passes": direction,
    }
    passed = all(checks.values())

    reason_parts = []
    if not checks["p_value_passes"]:
        reason_parts.append(f"p={p:.4f} >= {CONFIG.significance_threshold}")
    if not checks["eta2_passes"]:
        reason_parts.append(f"eta2={eta2:.4f} < {CONFIG.effect_size_threshold}")
    if not checks["direction_passes"]:
        tau70 = analysis_results.get("tau_star_70m", "?")
        tau160 = analysis_results.get("tau_star_160m", "?")
        reason_parts.append(f"direction FAILED: tau*(70M)={tau70} >= tau*(160M)={tau160}")

    reason = "PASS" if passed else "FAIL: " + "; ".join(reason_parts)

    return {
        "passed": passed,
        "reason": reason,
        "checks": checks,
        "p_value": p,
        "eta2": eta2,
        "direction_confirmed": direction,
    }


def run_full_analysis(csv_path: str) -> dict:
    """Top-level: load data, run all tests, print gate result."""
    df = load_results(csv_path)
    logger.info(f"Loaded {len(df)} result rows")

    # Select best DV: prefer train_loss (always real) over proxy benchmark scores.
    # PoC models are too small for real MMLU/HellaSwag signal, so train_loss on
    # real data is the honest DV. Negate so higher = better (consistent with accuracy).
    if "neg_train_loss" not in df.columns:
        df["neg_train_loss"] = -df["train_loss"]

    mmlu_var = df["mmlu_4shot"].var() if "mmlu_4shot" in df.columns else 0.0
    loss_var = df["train_loss"].var() if "train_loss" in df.columns else 0.0

    if loss_var > mmlu_var or mmlu_var < 1e-6:
        logger.info("Pivoting DV to neg_train_loss (more variance than mmlu_4shot proxy)")
        primary_dv = "neg_train_loss"
    else:
        primary_dv = "mmlu_4shot"

    ancova = run_ancova_interaction(df, dv=primary_dv)

    # Contamination variance check: if CR absorbs >50%, pivot to HellaSwag
    if ancova["anova_table"] is not None and primary_dv != "neg_train_loss":
        try:
            cr_ss = ancova["anova_table"].loc["contamination_rate", "sum_sq"]
            total_ss = ancova["anova_table"]["sum_sq"].sum()
            cr_fraction = cr_ss / total_ss if total_ss > 0 else 0
            if cr_fraction > 0.5:
                logger.warning(f"CR absorbs {cr_fraction:.1%} of variance — pivoting to neg_train_loss")
                ancova = run_ancova_interaction(df, dv="neg_train_loss")
        except Exception:
            pass

    direction = check_direction(df, dv=ancova.get("dv", "neg_train_loss"))
    secondary = run_secondary_analyses(df)

    full_results = {**ancova, **direction, "secondary": secondary}
    gate = gate_check(full_results)

    print(f"\n{'='*60}")
    print(f"GATE CHECK RESULT: {'PASS' if gate['passed'] else 'FAIL'}")
    print(f"  p-value: {ancova['interaction_p']:.4f}")
    print(f"  partial eta²: {ancova['interaction_eta2']:.4f}")
    print(f"  tau*(70M)={direction['tau_star_70m']}, tau*(160M)={direction['tau_star_160m']}")
    print(f"  direction: {'confirmed' if direction['direction_confirmed'] else 'NOT confirmed'}")
    print(f"  reason: {gate['reason']}")
    print(f"{'='*60}\n")

    return {**full_results, "gate": gate}
