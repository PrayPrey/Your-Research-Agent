import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats

from config import ExperimentConfig
from data_loader import fuzzy_join


def assign_scenario(
    partial_rho: float,
    ci_lo: float,
    ci_hi: float,
    cfg: ExperimentConfig,
) -> dict:
    """Classify partial_rho into scenario a/b/c/ambiguous using pre-specified boundaries."""
    if ci_lo >= ci_hi:
        raise ValueError(f"ci_lo={ci_lo} must be < ci_hi={ci_hi}")
    if not (-1.0 <= partial_rho <= 1.0):
        raise ValueError(f"partial_rho={partial_rho} out of [-1, 1]")

    # Ambiguity: point in grey zone OR CI spans 0 and +0.40 simultaneously
    grey_zone = (-cfg.scenario_a_bound < partial_rho < cfg.scenario_b_bound)
    ci_spans_zero_and_b = (ci_lo < 0) and (ci_hi > cfg.scenario_b_bound)
    is_ambiguous = grey_zone or ci_spans_zero_and_b

    if is_ambiguous:
        scenario = "ambiguous"
        narrative = (
            f"partial_rho={partial_rho:.3f} [BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}] "
            f"falls in grey zone ({-cfg.scenario_a_bound}, {cfg.scenario_b_bound}) or "
            f"CI spans conflicting boundaries. Finding is ambiguous but valid — "
            f"underpowered for definitive scenario resolution with current N."
        )
    elif abs(partial_rho) < cfg.scenario_a_bound:
        scenario = "a"
        narrative = (
            f"Scenario a (Independent Constructs): partial_rho={partial_rho:.3f} "
            f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. After controlling for MMLU, "
            f"TruthfulQA and BBQ are orthogonal (|rho| < {cfg.scenario_a_bound})."
        )
    elif partial_rho > cfg.scenario_b_bound:
        scenario = "b"
        narrative = (
            f"Scenario b (Scale-Free Coherence): partial_rho={partial_rho:.3f} "
            f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. Factuality and bias co-move "
            f"beyond general capability (rho > {cfg.scenario_b_bound})."
        )
    elif partial_rho < cfg.scenario_c_bound:
        scenario = "c"
        narrative = (
            f"Scenario c (Scale-Masked Tradeoff): partial_rho={partial_rho:.3f} "
            f"[BCa 95% CI: {ci_lo:.3f}, {ci_hi:.3f}]. MMLU masks a negative "
            f"factuality-bias relationship (rho < {cfg.scenario_c_bound})."
        )
    else:
        # Fallback — should not reach given grey_zone check above
        scenario = "ambiguous"
        is_ambiguous = True
        narrative = f"Unclassified: partial_rho={partial_rho:.3f}. Review boundaries."

    return {"scenario": scenario, "is_ambiguous": is_ambiguous, "narrative": narrative}


def verify_mechanism_activated(results: dict) -> tuple:
    """Check all mechanism indicators. Returns (all_ok: bool, indicators: dict)."""
    indicators = {}

    indicators["h_m2_loaded"] = (
        "partial_rho" in results
        and results["partial_rho"] is not None
        and isinstance(results["partial_rho"], (int, float))
    )

    indicators["scenario_assigned"] = (
        results.get("scenario") in {"a", "b", "c", "ambiguous"}
    )

    ci = results.get("ci_partial", [])
    indicators["ci_bounds_valid"] = (
        isinstance(ci, (list, tuple))
        and len(ci) == 2
        and ci[0] is not None
        and ci[1] is not None
        and float(ci[0]) < float(ci[1])
    )

    indicators["narrative_generated"] = (
        isinstance(results.get("narrative"), str)
        and len(results.get("narrative", "")) > 10
    )

    for key, val in indicators.items():
        status = "OK" if val else "FAIL"
        print(f"[verify_mechanism] {key}: {status}")

    all_ok = all(indicators.values())
    print(f"[verify_mechanism] overall: {'PASS' if all_ok else 'FAIL'}")
    return (all_ok, indicators)


def tier2_analysis(
    df_tier1: pd.DataFrame,
    harmbench_data: dict,
    cfg: ExperimentConfig,
) -> dict:
    """Fuzzy-join Tier1 with HarmBench, N-gate, compute partial Spearman."""
    required = ["model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
    missing = [c for c in required if c not in df_tier1.columns]
    if missing:
        raise RuntimeError(f"df_tier1 missing columns: {missing}")

    harmbench_df = pd.DataFrame([
        {"model_name": k, "harm_rate": v}
        for k, v in harmbench_data.items()
    ])

    df_merged = fuzzy_join(df_tier1, harmbench_df, threshold=cfg.fuzzy_threshold)
    N_harm = len(df_merged)

    if N_harm < cfg.n_min_harmbench:
        return {
            "tier2_status": "SKIPPED",
            "N_harmbench": N_harm,
            "reason": f"N={N_harm} < n_min={cfg.n_min_harmbench} after fuzzy join",
        }

    if N_harm < 4:
        raise RuntimeError(f"N_harm={N_harm} too small for partial_corr (need >= 4)")

    res_tqa = pg.partial_corr(
        data=df_merged,
        x="TruthfulQA_MC2",
        y="harm_rate",
        covar="MMLU",
        method="spearman",
    )
    rho_tqa = float(res_tqa["r"].iloc[0])
    ci_tqa = list(res_tqa["CI95%"].iloc[0])

    res_bbq = pg.partial_corr(
        data=df_merged,
        x="bbq_accuracy",
        y="harm_rate",
        covar="MMLU",
        method="spearman",
    )
    rho_bbq = float(res_bbq["r"].iloc[0])
    ci_bbq = list(res_bbq["CI95%"].iloc[0])

    scenario_tqa = assign_scenario(rho_tqa, ci_tqa[0], ci_tqa[1], cfg)
    scenario_bbq = assign_scenario(rho_bbq, ci_bbq[0], ci_bbq[1], cfg)

    return {
        "tier2_status": "EXECUTED",
        "N_harmbench": N_harm,
        "tqa_harm_partial_rho": rho_tqa,
        "tqa_harm_ci": ci_tqa,
        "scenario_tqa_harm": scenario_tqa["scenario"],
        "narrative_tqa_harm": scenario_tqa["narrative"],
        "bbq_harm_partial_rho": rho_bbq,
        "bbq_harm_ci": ci_bbq,
        "scenario_bbq_harm": scenario_bbq["scenario"],
        "narrative_bbq_harm": scenario_bbq["narrative"],
    }


def tier3_analysis(delta_bbq: np.ndarray) -> dict:
    """Binomial test on sign(ΔBBQ > 0) for base/chat pairs."""
    n = len(delta_bbq)
    k_positive = int(np.sum(delta_bbq > 0))
    result = stats.binomtest(k=k_positive, n=n, p=0.5, alternative="two-sided")
    p_value = float(result.pvalue)

    if p_value < 0.05:
        direction = "positive" if k_positive / n > 0.5 else "negative"
    else:
        direction = "non-significant"

    return {
        "k_positive": k_positive,
        "n": n,
        "p_value": p_value,
        "direction": direction,
        "proportion_positive": k_positive / n if n > 0 else float("nan"),
    }


def ablation_ci_method(
    partial_rho: float,
    df: pd.DataFrame,
    cfg: ExperimentConfig,
) -> dict:
    """Re-assign scenario using Fisher parametric CI from pingouin.partial_corr."""
    if df is None or len(df) < 4:
        return {"scenario": "unavailable", "matches_primary": None,
                "reason": "insufficient data for Fisher CI computation"}

    required = ["TruthfulQA_MC2", "bbq_accuracy", "MMLU"]
    if not all(c in df.columns for c in required):
        return {"scenario": "unavailable", "matches_primary": None,
                "reason": "missing required columns"}

    res = pg.partial_corr(
        data=df, x="TruthfulQA_MC2", y="bbq_accuracy",
        covar="MMLU", method="spearman",
    )
    rho_fisher = float(res["r"].iloc[0])
    ci_fisher = list(res["CI95%"].iloc[0])

    scenario_fisher = assign_scenario(rho_fisher, ci_fisher[0], ci_fisher[1], cfg)
    primary = assign_scenario(partial_rho, ci_fisher[0], ci_fisher[1], cfg)

    return {
        "scenario": scenario_fisher["scenario"],
        "rho_fisher": rho_fisher,
        "ci_fisher": ci_fisher,
        "matches_primary": scenario_fisher["scenario"] == primary["scenario"],
    }


def ablation_boundary(
    partial_rho: float,
    ci_lo: float,
    ci_hi: float,
    cfg: ExperimentConfig,
) -> dict:
    """Assign scenario under tight and wide boundary variants."""
    import copy
    tight_cfg = copy.copy(cfg)
    tight_cfg.scenario_a_bound = cfg.tight_a
    tight_cfg.scenario_b_bound = cfg.tight_b
    tight_cfg.scenario_c_bound = cfg.tight_c

    wide_cfg = copy.copy(cfg)
    wide_cfg.scenario_a_bound = cfg.wide_a
    wide_cfg.scenario_b_bound = cfg.wide_b
    wide_cfg.scenario_c_bound = cfg.wide_c

    tight_res = assign_scenario(partial_rho, ci_lo, ci_hi, tight_cfg)
    wide_res = assign_scenario(partial_rho, ci_lo, ci_hi, wide_cfg)

    return {
        "tight": {"scenario": tight_res["scenario"]},
        "wide": {"scenario": wide_res["scenario"]},
    }
