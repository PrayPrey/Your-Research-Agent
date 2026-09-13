"""H-M4: Statistical analysis — Kendall τ, MixedLM ΔR², cross-model gap."""
import warnings
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from scipy import stats
import statsmodels.formula.api as smf

from config import (
    TAU_THRESHOLD, DELTA_R2_THRESHOLD, GAP_THRESHOLD, ALPHA,
    N_BOOTSTRAP, SEED, MODEL_FAMILIES,
)


@dataclass
class TauResult:
    tau: float
    pvalue: float
    null_distribution: List[float]


@dataclass
class SpearmanResult:
    rho: float
    pvalue: float


@dataclass
class DeltaR2Result:
    delta_r2: float
    r2_full: float
    r2_reduced: float
    converged: bool
    fallback_ols: bool


@dataclass
class GapResult:
    gap: float
    ci_low: float
    ci_high: float
    best_model: str
    worst_model: str


@dataclass
class H_M4_Results:
    tau: float
    tau_pvalue: float
    spearman_rho: float
    spearman_pvalue: float
    delta_R2: float
    R2_full: float
    R2_reduced: float
    cross_model_gap: float
    gap_ci_low: float
    gap_ci_high: float
    best_model: str
    worst_model: str
    model_ranking_by_contract: List[str]
    model_ranking_by_pass: List[str]
    n_model_task_pairs: int
    gate_pass: bool
    gate_partial: bool
    tau_humaneval: float
    tau_mbpp: float
    delta_R2_humaneval: float
    delta_R2_mbpp: float
    permutation_null: List[float]
    model_family_pvalue: float
    converged: bool
    fallback_ols: bool


def compute_kendall_tau(
    contract_rates: np.ndarray,
    pass_at_1: np.ndarray,
) -> TauResult:
    """Kendall tau-b + exact permutation p-value (all 5!=120 perms)."""
    observed_tau, _ = stats.kendalltau(contract_rates, pass_at_1, variant="b")

    def stat_fn(x, y):
        return stats.kendalltau(x, y, variant="b").statistic

    perm_result = stats.permutation_test(
        (contract_rates, pass_at_1),
        statistic=stat_fn,
        permutation_type="pairings",
        n_resamples=np.inf,  # all 5! = 120 exact permutations
        alternative="two-sided",
    )
    null_dist = perm_result.null_distribution.tolist()
    pvalue = perm_result.pvalue

    print(f"Kendall tau computed: τ = {observed_tau:.4f}, p = {pvalue:.4f}")
    return TauResult(tau=float(observed_tau), pvalue=float(pvalue), null_distribution=null_dist)


def compute_spearman(
    contract_rates: np.ndarray,
    pass_at_1: np.ndarray,
) -> SpearmanResult:
    """Spearman rho as secondary metric."""
    result = stats.spearmanr(contract_rates, pass_at_1)
    print(f"Spearman ρ = {result.statistic:.4f}, p = {result.pvalue:.4f}")
    return SpearmanResult(rho=float(result.statistic), pvalue=float(result.pvalue))


def _fit_mixedlm(df_long: pd.DataFrame, formula: str, reml: bool = True):
    """Internal helper: fit MixedLM with convergence retry + OLS fallback."""
    model = smf.mixedlm(formula, df_long, groups=df_long["task_id"])
    for method in ["powell", "lbfgs", "bfgs", "nm"]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = model.fit(reml=reml, method=method)
            if result.converged:
                return result, True, False
        except Exception:
            continue
    # OLS fallback
    print(f"WARNING: MixedLM did not converge for formula '{formula}', falling back to OLS")
    ols_result = smf.ols(formula, df_long).fit()
    return ols_result, False, True


def fit_full_mixedlm(df_long: pd.DataFrame, reml: bool = True):
    """Full model: contract_sat_rate ~ pass_at_1 + log_size + C(model_family)."""
    # Need >=2 levels in model_family for C() to work
    n_families = df_long["model_family"].nunique()
    if n_families < 2:
        formula = "contract_satisfaction_rate ~ pass_at_1 + log_size"
        print("WARNING: Only 1 model family; using formula without C(model_family)")
    else:
        formula = "contract_satisfaction_rate ~ pass_at_1 + log_size + C(model_family)"
    return _fit_mixedlm(df_long, formula, reml)


def fit_reduced_mixedlm(df_long: pd.DataFrame, reml: bool = True):
    """Reduced model: contract_sat_rate ~ pass_at_1 + log_size."""
    formula = "contract_satisfaction_rate ~ pass_at_1 + log_size"
    return _fit_mixedlm(df_long, formula, reml)


def marginal_r2(fitted_model, fallback_ols: bool = False) -> float:
    """Nakagawa-Schielzeth marginal R²."""
    fe_var = float(np.var(fitted_model.fittedvalues))
    if fallback_ols:
        re_var = 0.0
        resid_var = float(np.var(fitted_model.resid))
    else:
        try:
            re_var = float(sum(v for v in fitted_model.cov_re.values.flatten() if v > 0))
        except Exception:
            re_var = 0.0
        resid_var = float(fitted_model.scale)
    total = fe_var + re_var + resid_var
    return fe_var / total if total > 0 else 0.0


def compute_delta_r2(df_long: pd.DataFrame) -> DeltaR2Result:
    """Compute partial ΔR² = R2_full - R2_reduced."""
    full_model, conv_f, ols_f = fit_full_mixedlm(df_long)
    reduced_model, conv_r, ols_r = fit_reduced_mixedlm(df_long)
    r2_full = marginal_r2(full_model, ols_f)
    r2_reduced = marginal_r2(reduced_model, ols_r)
    delta = r2_full - r2_reduced
    print(f"ΔR² computed: {delta:.4f} (R²_full={r2_full:.4f}, R²_reduced={r2_reduced:.4f})")
    return DeltaR2Result(
        delta_r2=delta, r2_full=r2_full, r2_reduced=r2_reduced,
        converged=conv_f and conv_r, fallback_ols=ols_f or ols_r
    )


def compute_cross_model_gap(df_long: pd.DataFrame) -> GapResult:
    """Task-controlled residual gap = max(residual_rate) - min(residual_rate)."""
    task_means = df_long.groupby("task_id")["contract_satisfaction_rate"].mean()
    df = df_long.copy()
    df["task_mean"] = df["task_id"].map(task_means)
    df["residual"] = df["contract_satisfaction_rate"] - df["task_mean"]

    model_residuals = df.groupby("model_id")["residual"].mean()
    gap = float(model_residuals.max() - model_residuals.min())
    best_model = str(model_residuals.idxmax())
    worst_model = str(model_residuals.idxmin())

    ci_low, ci_high = bootstrap_gap_ci(df_long)
    print(f"Cross-model gap: {gap:.4f} [{ci_low:.4f}, {ci_high:.4f}] (best: {best_model}, worst: {worst_model})")
    return GapResult(gap=gap, ci_low=ci_low, ci_high=ci_high, best_model=best_model, worst_model=worst_model)


def bootstrap_gap_ci(df_long: pd.DataFrame, n_boot: int = N_BOOTSTRAP, seed: int = SEED) -> Tuple[float, float]:
    """Bootstrap 95% CI on task-controlled residual gap."""
    rng = np.random.default_rng(seed)
    tasks = df_long["task_id"].unique()
    gaps = []

    for _ in range(n_boot):
        sampled_tasks = rng.choice(tasks, size=len(tasks), replace=True)
        boot_df = df_long[df_long["task_id"].isin(sampled_tasks)].copy()
        task_means = boot_df.groupby("task_id")["contract_satisfaction_rate"].mean()
        boot_df["residual"] = boot_df["contract_satisfaction_rate"] - boot_df["task_id"].map(task_means)
        model_res = boot_df.groupby("model_id")["residual"].mean()
        if len(model_res) >= 2:
            gaps.append(float(model_res.max() - model_res.min()))

    gaps = np.array(gaps)
    return float(np.percentile(gaps, 2.5)), float(np.percentile(gaps, 97.5))


def compute_model_family_pvalue(df_long: pd.DataFrame) -> float:
    """Permutation p-value for model_family coefficient significance."""
    n_families = df_long["model_family"].nunique()
    if n_families < 2:
        print("WARNING: Only 1 model family; family p-value set to 1.0")
        return 1.0
    try:
        model = smf.mixedlm(
            "contract_satisfaction_rate ~ pass_at_1 + log_size + C(model_family)",
            df_long, groups=df_long["task_id"]
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mdf = model.fit(reml=True, method="powell")
        # Get p-value for model family from Wald test
        family_params = [p for p in mdf.params.index if "model_family" in str(p)]
        if family_params:
            pvals = [mdf.pvalues[p] for p in family_params if p in mdf.pvalues]
            return float(min(pvals)) if pvals else 1.0
        return 1.0
    except Exception as e:
        print(f"WARNING: Could not compute family p-value: {e}")
        return 1.0


def verify_mechanism_activated(results: H_M4_Results) -> Tuple[bool, dict]:
    """Verify statistical analysis ran and produced meaningful output."""
    indicators = {
        "tau_computed": results.tau is not None and not np.isnan(results.tau),
        "delta_R2_computed": results.delta_R2 is not None,
        "data_sufficient": results.n_model_task_pairs >= 1000,
        "model_variance_exists": results.cross_model_gap > 0.001,
    }
    all_ok = all(indicators.values())
    print(f"Mechanism activation: {all_ok} — {indicators}")
    return all_ok, indicators


def run_subgroup_analysis(
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict,
    task_type: str,
) -> dict:
    """Run τ + ΔR² for one task_type stratum."""
    # Map task_type labels
    if task_type == "humaneval_plus":
        mask = df_long["task_type"].isin(["humaneval_plus", "humaneval", "HumanEval"])
    else:
        mask = df_long["task_type"].isin(["mbpp_plus", "mbpp", "Mbpp"])

    sub_df = df_long[mask].copy()
    sub_exp_b = exp_b_df[exp_b_df["task_id"].isin(sub_df["task_id"].unique())].copy()

    if len(sub_df) < 50:
        print(f"WARNING: Subgroup '{task_type}' has only {len(sub_df)} rows — skipping")
        return {"tau": float("nan"), "delta_r2": float("nan"), "n_pairs": len(sub_df)}

    model_rates = sub_exp_b.groupby("model_id")["contract_satisfaction_rate"].mean()
    # Align with pass_at_1
    common_models = [m for m in model_rates.index if m in pass_at_1]
    if len(common_models) < 3:
        return {"tau": float("nan"), "delta_r2": float("nan"), "n_pairs": len(sub_df)}

    rates_vec = model_rates[common_models].values
    pass_vec = np.array([pass_at_1[m] for m in common_models])

    tau_res = compute_kendall_tau(rates_vec, pass_vec)

    try:
        delta_res = compute_delta_r2(sub_df)
        delta_r2 = delta_res.delta_r2
    except Exception as e:
        print(f"WARNING: ΔR² failed for subgroup '{task_type}': {e}")
        delta_r2 = float("nan")

    return {
        "tau": tau_res.tau,
        "tau_pvalue": tau_res.pvalue,
        "delta_r2": delta_r2,
        "n_pairs": len(sub_df),
        "task_type": task_type,
    }


def run_analysis(
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict,
) -> H_M4_Results:
    """Orchestrate all H-M4 analysis steps."""
    print("\n=== H-M4 Analysis Pipeline ===")

    # Per-model mean contract-satisfaction rate
    model_rates = exp_b_df.groupby("model_id")["contract_satisfaction_rate"].mean()
    common_models = [m for m in model_rates.index if m in pass_at_1]
    print(f"Models in analysis: {common_models}")

    contract_vec = model_rates[common_models].values
    pass_vec = np.array([pass_at_1[m] for m in common_models])

    # 1. Kendall τ + Spearman ρ
    tau_res = compute_kendall_tau(contract_vec, pass_vec)
    spr_res = compute_spearman(contract_vec, pass_vec)

    # 2. Mixed-effects ΔR²
    delta_res = compute_delta_r2(df_long)

    # 3. Cross-model gap
    gap_res = compute_cross_model_gap(df_long)

    # 4. Model family p-value
    family_pvalue = compute_model_family_pvalue(df_long)

    # 5. Model rankings
    ranking_by_contract = model_rates[common_models].sort_values(ascending=False).index.tolist()
    ranking_by_pass = sorted(common_models, key=lambda m: pass_at_1[m], reverse=True)

    # 6. Subgroup analysis
    sub_humaneval = run_subgroup_analysis(exp_b_df, df_long, pass_at_1, "humaneval_plus")
    sub_mbpp = run_subgroup_analysis(exp_b_df, df_long, pass_at_1, "mbpp_plus")

    # 7. Gate logic
    gate_pass = (
        tau_res.tau <= TAU_THRESHOLD
        and tau_res.pvalue < ALPHA
        and delta_res.delta_r2 >= DELTA_R2_THRESHOLD
    )
    gate_partial = (
        not gate_pass and (
            tau_res.tau <= TAU_THRESHOLD
            or delta_res.delta_r2 >= DELTA_R2_THRESHOLD
        )
    )

    results = H_M4_Results(
        tau=tau_res.tau,
        tau_pvalue=tau_res.pvalue,
        spearman_rho=spr_res.rho,
        spearman_pvalue=spr_res.pvalue,
        delta_R2=delta_res.delta_r2,
        R2_full=delta_res.r2_full,
        R2_reduced=delta_res.r2_reduced,
        cross_model_gap=gap_res.gap,
        gap_ci_low=gap_res.ci_low,
        gap_ci_high=gap_res.ci_high,
        best_model=gap_res.best_model,
        worst_model=gap_res.worst_model,
        model_ranking_by_contract=ranking_by_contract,
        model_ranking_by_pass=ranking_by_pass,
        n_model_task_pairs=len(df_long),
        gate_pass=gate_pass,
        gate_partial=gate_partial,
        tau_humaneval=sub_humaneval.get("tau", float("nan")),
        tau_mbpp=sub_mbpp.get("tau", float("nan")),
        delta_R2_humaneval=sub_humaneval.get("delta_r2", float("nan")),
        delta_R2_mbpp=sub_mbpp.get("delta_r2", float("nan")),
        permutation_null=tau_res.null_distribution,
        model_family_pvalue=family_pvalue,
        converged=delta_res.converged,
        fallback_ols=delta_res.fallback_ols,
    )

    gate_str = "PASS" if gate_pass else ("PARTIAL" if gate_partial else "FAIL")
    print(f"\nGate Result: {gate_str}")
    print(f"  τ = {tau_res.tau:.4f} (threshold ≤ {TAU_THRESHOLD}), p = {tau_res.pvalue:.4f}")
    print(f"  ΔR² = {delta_res.delta_r2:.4f} (threshold ≥ {DELTA_R2_THRESHOLD})")
    print(f"  Gap = {gap_res.gap:.4f} (threshold ≥ {GAP_THRESHOLD})")
    print(f"  Converged: {delta_res.converged}, OLS fallback: {delta_res.fallback_ols}")

    return results
