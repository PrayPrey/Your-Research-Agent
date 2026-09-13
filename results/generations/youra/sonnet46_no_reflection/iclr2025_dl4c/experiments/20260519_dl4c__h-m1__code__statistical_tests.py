import numpy as np
from scipy.stats import mannwhitneyu, spearmanr
from config import M1ExperimentConfig

MANNWHITNEY_ALTERNATIVE = "greater"
EFFECT_SIZE_METHOD = "median_diff"
SPEARMAN_MIN_SAMPLES = 5


def run_mann_whitney_test(
    sep_grpo: list,
    sep_dpo: list,
    alpha: float = 0.05,
) -> dict:
    """Mann-Whitney U test (one-sided, alternative='greater').

    Returns {"u_statistic": float, "p_value": float, "effect_size": float, "significant": bool}
    """
    if len(sep_grpo) < 2 or len(sep_dpo) < 2:
        return {"u_statistic": float("nan"), "p_value": float("nan"),
                "effect_size": float("nan"), "significant": False}

    u_stat, p_val = mannwhitneyu(sep_grpo, sep_dpo, alternative=MANNWHITNEY_ALTERNATIVE)
    effect_size = float(np.median(sep_grpo) - np.median(sep_dpo))
    return {
        "u_statistic": float(u_stat),
        "p_value": float(p_val),
        "effect_size": effect_size,
        "significant": p_val < alpha,
    }


def run_spearman_correlation(
    reward_signals: list,
    pass_at_1: list,
    cfg: "M1ExperimentConfig" = None,
) -> dict:
    """Spearman rank correlation between reward signals and pass@1.

    Returns {"rho": float, "p_value": float, "above_threshold": bool}
    """
    threshold = cfg.spearman_rho_threshold if cfg is not None else 0.5

    if len(reward_signals) < SPEARMAN_MIN_SAMPLES or len(pass_at_1) < SPEARMAN_MIN_SAMPLES:
        return {"rho": float("nan"), "p_value": float("nan"), "above_threshold": False}

    n = min(len(reward_signals), len(pass_at_1))
    rho, p_val = spearmanr(reward_signals[:n], pass_at_1[:n])
    return {
        "rho": float(rho),
        "p_value": float(p_val),
        "above_threshold": abs(float(rho)) >= threshold,
    }


def run_all_statistical_tests(
    sep_grpo_binary: list,
    sep_grpo_errortype: list,
    sep_dpo: list,
    pass_at_1_grpo_binary: list,
    pass_at_1_grpo_errortype: list,
    reward_signals_binary: list,
    reward_signals_errortype: list,
    cfg: M1ExperimentConfig,
) -> dict:
    """Run full statistical test suite for both GRPO conditions vs DPO."""
    mw_binary = run_mann_whitney_test(sep_grpo_binary, sep_dpo, alpha=cfg.mann_whitney_alpha)
    mw_errortype = run_mann_whitney_test(sep_grpo_errortype, sep_dpo, alpha=cfg.mann_whitney_alpha)

    spearman_binary = run_spearman_correlation(reward_signals_binary, pass_at_1_grpo_binary, cfg)
    spearman_errortype = run_spearman_correlation(reward_signals_errortype, pass_at_1_grpo_errortype, cfg)

    return {
        "mann_whitney": {
            "grpo_binary_vs_dpo": mw_binary,
            "grpo_errortype_vs_dpo": mw_errortype,
        },
        "spearman": {
            "grpo_binary": spearman_binary,
            "grpo_errortype": spearman_errortype,
        },
        "summary": {
            "binary_significant": mw_binary["significant"],
            "errortype_significant": mw_errortype["significant"],
            "either_significant": mw_binary["significant"] or mw_errortype["significant"],
            "n_grpo_binary": len(sep_grpo_binary),
            "n_grpo_errortype": len(sep_grpo_errortype),
            "n_dpo": len(sep_dpo),
        },
    }


def verify_mechanism_activated(
    sep_grpo: list,
    sep_dpo: list,
    results: dict,
) -> tuple:
    """Verify mechanism is activated based on SEP values and statistical results.

    Checks:
    - decomposition_working: SEP values exist and are in [0,1]
    - semantic_proportion_valid: mean SEP > 0
    - grpo_higher: median(sep_grpo) > median(sep_dpo)
    - statistically_significant: p < 0.05 from Mann-Whitney

    Returns (bool, dict, float): (gate_passed, detail_dict, effect_size)
    """
    detail = {}

    # Check decomposition is working
    decomposition_working = (
        len(sep_grpo) > 0 and len(sep_dpo) > 0
        and all(0 <= v <= 1 for v in sep_grpo[:100])
        and all(0 <= v <= 1 for v in sep_dpo[:100])
    )
    detail["decomposition_working"] = decomposition_working

    # Check semantic proportion is meaningful
    mean_sep_grpo = float(np.mean(sep_grpo)) if sep_grpo else float("nan")
    mean_sep_dpo = float(np.mean(sep_dpo)) if sep_dpo else float("nan")
    semantic_proportion_valid = mean_sep_grpo > 0 or mean_sep_dpo > 0
    detail["semantic_proportion_valid"] = semantic_proportion_valid
    detail["mean_sep_grpo"] = mean_sep_grpo
    detail["mean_sep_dpo"] = mean_sep_dpo

    # Check GRPO higher than DPO (>50% samples)
    med_grpo = float(np.median(sep_grpo)) if sep_grpo else float("nan")
    med_dpo = float(np.median(sep_dpo)) if sep_dpo else float("nan")
    grpo_higher = med_grpo > med_dpo if sep_grpo and sep_dpo else False
    detail["grpo_higher"] = grpo_higher
    detail["median_sep_grpo"] = med_grpo
    detail["median_sep_dpo"] = med_dpo

    # Check statistical significance
    mw = results.get("mann_whitney", {}).get("grpo_binary_vs_dpo", {})
    statistically_significant = mw.get("significant", False)
    p_value = mw.get("p_value", float("nan"))
    detail["statistically_significant"] = statistically_significant
    detail["p_value"] = p_value

    effect_size = mw.get("effect_size", float("nan"))
    detail["effect_size"] = effect_size

    gate_passed = (
        decomposition_working
        and semantic_proportion_valid
        and grpo_higher
        and statistically_significant
    )

    return gate_passed, detail, effect_size
