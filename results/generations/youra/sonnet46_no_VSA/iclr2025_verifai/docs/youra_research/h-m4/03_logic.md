# Logic: H-M4 Cross-Model Contract-Satisfaction Statistical Analysis

**Applied**: Standard Python flat-function pattern (consistent with H-M3/H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Relevant Symbols**:
- `load_contracteval_tasks(jsonl_path: str = None) -> dict` — delegates to H-M1 data_loader
- `load_exp_a_results(results_path: str = None) -> list[dict]` — JSONL reader
- H-M3 uses `Path(__file__).parent.parent` for path resolution; no classes, flat functions

---

## External Dependencies API (Base Hypothesis)

The following APIs are called or referenced from H-M3/H-M1. Signatures verified from actual implementation.

```python
# From: docs/youra_research/h-m3/code/data_loader.py (ACTUAL CODE)
def load_contracteval_tasks(jsonl_path: str = None) -> dict:
    """Returns {task_id: task_dict} using H-M1 data_loader."""
    ...

def load_exp_a_results(results_path: str = None) -> list[dict]:
    """Load Exp A per-triple static oracle results."""
    # returns list of dicts with keys: task_id, model, program_idx, static_failure_rate, task_type
    ...
```

**Note**: H-M4 reads H-M3 Experiment B results as CSV — no direct Python import of H-M3 modules required. The CSV path is `h-m3/results/experiment_b_per_model_task_rates.csv`.

**Verified from**: `docs/youra_research/h-m3/code/data_loader.py` (actual code, not spec)

---

## Dataclass Definitions

```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class TauResult:
    tau: float            # Kendall tau-b statistic
    pvalue: float         # exact permutation p-value (two-sided)
    null_distribution: List[float]  # all 5! = 120 permutation tau values

@dataclass
class SpearmanResult:
    rho: float
    pvalue: float

@dataclass
class DeltaR2Result:
    delta_r2: float       # R2_full - R2_reduced
    r2_full: float
    r2_reduced: float
    converged: bool       # False if fallback optimizer was used
    fallback_ols: bool    # True if OLS used instead of MixedLM

@dataclass
class GapResult:
    gap: float            # max(residual) - min(residual) across models
    ci_low: float         # 2.5th percentile bootstrap
    ci_high: float        # 97.5th percentile bootstrap
    best_model: str       # model with highest residual rate
    worst_model: str      # model with lowest residual rate

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
```

---

## A-4: Mixed-Effects Regression [Complexity: 14, Budget: 4 subtasks]

**Applied**: statsmodels MixedLM with convergence retry and OLS fallback

### API Signatures

```python
def fit_full_mixedlm(
    df_long: pd.DataFrame,
    reml: bool = True,
) -> tuple[object, bool, bool]:
    """Fit full model: contract_sat_rate ~ pass_at_1 + log_size + C(model_family).
    Returns (fitted_model, converged, fallback_ols).
    Groups by task_id as random intercept.
    """
    ...

def fit_reduced_mixedlm(
    df_long: pd.DataFrame,
    reml: bool = True,
) -> tuple[object, bool, bool]:
    """Fit reduced model: contract_sat_rate ~ pass_at_1 + log_size.
    Returns (fitted_model, converged, fallback_ols).
    Groups by task_id as random intercept.
    """
    ...

def marginal_r2(fitted_model: object, fallback_ols: bool = False) -> float:
    """Nakagawa-Schielzeth marginal R². Returns float in [0, 1]."""
    ...

def compute_delta_r2(df_long: pd.DataFrame) -> DeltaR2Result:
    """Compute partial delta R² = R2_full - R2_reduced. Returns DeltaR2Result."""
    ...
```

### Pseudo-code

**fit_full_mixedlm / fit_reduced_mixedlm** (shared pattern via `fit_mixedlm` helper):
```
formula_full    = "contract_sat_rate ~ pass_at_1 + log_size + C(model_family)"
formula_reduced = "contract_sat_rate ~ pass_at_1 + log_size"

def fit_mixedlm(df_long, formula, reml=True):
    model = smf.mixedlm(formula, df_long, groups=df_long["task_id"])
    for method in ["powell", "lbfgs", "bfgs"]:
        try:
            result = model.fit(reml=reml, method=method)
            return result, True, False
        except (ConvergenceWarning, np.linalg.LinAlgError):
            continue
    # OLS fallback
    ols_result = smf.ols(formula, df_long).fit()
    return ols_result, False, True
```

**marginal_r2 (Nakagawa-Schielzeth)**:
```
fe_var       = var(fitted_model.fittedvalues)
if fallback_ols:
    re_var   = 0.0
    resid_var = var(fitted_model.resid)
else:
    re_var   = sum(v for v in fitted_model.cov_re.values())  # random intercept variance
    resid_var = fitted_model.scale  # residual variance
R2_m = fe_var / (fe_var + re_var + resid_var)
return R2_m
```

**compute_delta_r2**:
```
full_model,    conv_f, ols_f = fit_full_mixedlm(df_long)
reduced_model, conv_r, ols_r = fit_reduced_mixedlm(df_long)
r2_full    = marginal_r2(full_model,    ols_f)
r2_reduced = marginal_r2(reduced_model, ols_r)
delta = r2_full - r2_reduced
return DeltaR2Result(delta, r2_full, r2_reduced, conv_f and conv_r, ols_f or ols_r)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | fit_full_mixedlm | Full model fit with convergence retry and OLS fallback |
| L-4-2 | fit_reduced_mixedlm | Reduced model fit (same retry/fallback logic) |
| L-4-3 | marginal_r2 | Nakagawa-Schielzeth formula, handles OLS fallback |
| L-4-4 | compute_delta_r2 | Orchestrates full/reduced fits, returns DeltaR2Result |

---

## A-3: Kendall τ + Permutation Test [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard Python flat-function pattern

### API Signatures

```python
def compute_kendall_tau(
    contract_rates: np.ndarray,   # shape [N_models] — per-model mean contract rate
    pass_at_1: np.ndarray,        # shape [N_models] — per-model pass@1 score
) -> TauResult:
    """Kendall tau-b + exact permutation p-value (all 5!=120 perms). Returns TauResult."""
    ...

def compute_spearman(
    contract_rates: np.ndarray,   # shape [N_models]
    pass_at_1: np.ndarray,        # shape [N_models]
) -> SpearmanResult:
    """Spearman rho as secondary metric. Returns SpearmanResult."""
    ...
```

### Pseudo-code

**compute_kendall_tau**:
```
from scipy.stats import kendalltau, permutation_test

observed_tau, _ = kendalltau(contract_rates, pass_at_1, variant='b')

def stat_fn(x, y):
    return kendalltau(x, y, variant='b').statistic

perm_result = permutation_test(
    (contract_rates, pass_at_1),
    statistic=stat_fn,
    permutation_type='pairings',
    n_resamples=np.inf,        # all 5! = 120 exact permutations
    alternative='two-sided',
)
null_dist = perm_result.null_distribution.tolist()
pvalue    = perm_result.pvalue

return TauResult(tau=observed_tau, pvalue=pvalue, null_distribution=null_dist)
```

**compute_spearman**:
```
from scipy.stats import spearmanr
result = spearmanr(contract_rates, pass_at_1)
return SpearmanResult(rho=result.statistic, pvalue=result.pvalue)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_kendall_tau | kendalltau + permutation_test with permutation_type='pairings', n_resamples=inf |
| L-3-2 | compute_spearman | spearmanr secondary metric |

---

## A-5: Cross-Model Gap [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard Python flat-function pattern

### API Signatures

```python
def compute_cross_model_gap(
    df_long: pd.DataFrame,
) -> GapResult:
    """Task-controlled residual gap = max(residual_rate) - min(residual_rate).
    Returns GapResult with gap, ci from bootstrap_gap_ci, best/worst model.
    """
    ...

def bootstrap_gap_ci(
    df_long: pd.DataFrame,
    n_boot: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Bootstrap 95% CI on task-controlled residual gap.
    Returns (ci_low, ci_high).
    """
    ...
```

### Pseudo-code

**compute_cross_model_gap**:
```
# 1. Compute per-task mean across all models
task_means = df_long.groupby("task_id")["contract_sat_rate"].mean()

# 2. Merge task_mean back; compute residual
df_long["task_mean"] = df_long["task_id"].map(task_means)
df_long["residual"]  = df_long["contract_sat_rate"] - df_long["task_mean"]

# 3. Per-model mean residual
model_residuals = df_long.groupby("model_id")["residual"].mean()

gap         = model_residuals.max() - model_residuals.min()
best_model  = model_residuals.idxmax()
worst_model = model_residuals.idxmin()

ci_low, ci_high = bootstrap_gap_ci(df_long)
return GapResult(gap, ci_low, ci_high, best_model, worst_model)
```

**bootstrap_gap_ci**:
```
rng    = np.random.default_rng(seed)
tasks  = df_long["task_id"].unique()
gaps   = []

for _ in range(n_boot):
    sampled_tasks = rng.choice(tasks, size=len(tasks), replace=True)
    boot_df       = df_long[df_long["task_id"].isin(sampled_tasks)]
    task_means    = boot_df.groupby("task_id")["contract_sat_rate"].mean()
    boot_df       = boot_df.copy()
    boot_df["residual"] = boot_df["contract_sat_rate"] - boot_df["task_id"].map(task_means)
    model_res     = boot_df.groupby("model_id")["residual"].mean()
    gaps.append(model_res.max() - model_res.min())

gaps = np.array(gaps)
return (np.percentile(gaps, 2.5), np.percentile(gaps, 97.5))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_cross_model_gap | Task-controlled residual gap, best/worst model |
| L-5-2 | bootstrap_gap_ci | 1000-iteration bootstrap CI on gap, seed=42 |

---

## Summary: All Subtasks [8/8 used]

| ID | Task | Subtask | Module |
|----|------|---------|--------|
| L-4-1 | A-4 | fit_full_mixedlm | analysis.py |
| L-4-2 | A-4 | fit_reduced_mixedlm | analysis.py |
| L-4-3 | A-4 | marginal_r2 | analysis.py |
| L-4-4 | A-4 | compute_delta_r2 | analysis.py |
| L-3-1 | A-3 | compute_kendall_tau | analysis.py |
| L-3-2 | A-3 | compute_spearman | analysis.py |
| L-5-1 | A-5 | compute_cross_model_gap | analysis.py |
| L-5-2 | A-5 | bootstrap_gap_ci | analysis.py |
