# H-M2 Logic Design

Applied: non-parametric-matched-group-comparison
Applied: propensity-score-matching-reuse
Applied: rank-biserial-effect-size

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from h-m1 actual code
**Analyzed Path**: h-m1/code/src/ (matching.py, survival_prep.py, ingest.py)
**Relevant Symbols**:
- `fit_propensity_model(survival_df, covariate_cols, treatment_col, seed)` → `(model, ps: np.ndarray[N])`
- `nearest_neighbor_match(survival_df, ps_scores, treatment_col, caliper, ratio=1)` → `matched_df`
- `compute_smd(df_before, df_after, covariate_cols, treatment_col)` → `smd_df`
- `run_matching(survival_df, cfg, caliper_factor=None, ratio=1)` → `(matched_df, smd_df, matching_meta)`
- `encode_covariates(cohort)` → `cohort` with `creation_year_quartile`, `task_type_encoded`, `size_decile`
- `build_survival_df(cohort, observation_window_days)` → `survival_df`
- `validate_preconditions(survival_df, cfg)` → `dict`

**CRITICAL**: `run_matching()` hardcodes `treatment_col="high_findable"`. h-m2 must NOT call `run_matching()`; instead call `fit_propensity_model`, `nearest_neighbor_match`, `compute_smd` directly with `treatment_col="high_accessible"`.

---

## External Dependencies API

### API Signatures (From Actual h-m1 Code)

```python
# From: h-m1/code/src/matching.py (ACTUAL CODE)
def fit_propensity_model(
    survival_df: pd.DataFrame,
    covariate_cols: list,
    treatment_col: str,   # ← pass "high_accessible" here
    seed: int,
) -> tuple:
    """Returns: (fitted_model, propensity_scores: np.ndarray shape [N])"""

def nearest_neighbor_match(
    survival_df: pd.DataFrame,
    ps_scores: np.ndarray,     # shape [N]
    treatment_col: str,        # ← pass "high_accessible" here
    caliper: float,
    ratio: int = 1,
) -> pd.DataFrame:
    """Returns matched_df with pair_id column."""

def compute_smd(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    covariate_cols: list,
    treatment_col: str,        # ← pass "high_accessible" here
) -> pd.DataFrame:
    """Returns DataFrame[covariate, smd_before, smd_after]."""

# From: h-m1/code/src/survival_prep.py (ACTUAL CODE)
def encode_covariates(cohort: pd.DataFrame) -> pd.DataFrame:
    """Adds creation_year_quartile, task_type_encoded, size_decile columns."""

# From: h-m1/code/src/ingest.py (ACTUAL CODE)
def load_he1_scores(scores_csv: str) -> pd.DataFrame:
    """Returns DataFrame[did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, status]."""

def fetch_run_timestamps(dataset_ids: list, cache_dir: str, retry_max: int = 3) -> pd.DataFrame:
    """Returns DataFrame[did, first_run_timestamp, run_count]."""
```

---

## A-3: AccessiblePrep Module [Complexity: 3, Budget: 2]

Applied: propensity-score-matching-reuse

### API Signatures

```python
# File: src/accessible_prep.py

def compute_12m_run_counts(
    datasets_df: pd.DataFrame,
    runs_df: pd.DataFrame,
    window_days: int = 365,
) -> pd.DataFrame:
    """Add run_count_12m column: runs within window_days of dataset upload.
    datasets_df: DataFrame[did, upload_date, ...]
    runs_df: DataFrame[did, upload_time]
    Returns: datasets_df with run_count_12m column added. Shape: same rows.
    """
    ...

def compute_accessible_score(
    df: pd.DataFrame,
    he1_scores_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge fair_A sub-score; compute median split -> high_accessible (0/1).
    df: DataFrame[did, ...]
    he1_scores_df: DataFrame[did, fair_A, ...]
    Returns: df with fair_A and high_accessible columns. Shape: same rows.
    """
    ...

def build_analysis_df(
    datasets_df: pd.DataFrame,
    runs_df: pd.DataFrame,
    he1_scores_df: pd.DataFrame,
    config,
) -> pd.DataFrame:
    """Full pipeline: counts -> accessible score -> encode covariates -> validate.
    Returns: analysis_df ready for matching and MWU analysis.
    """
    ...

def validate_preconditions(df: pd.DataFrame, min_pairs: int) -> None:
    """Assert n_high >= min_pairs AND n_low >= min_pairs.
    Raises ValueError if either condition fails.
    """
    ...
```

### Pseudo-code

```
compute_12m_run_counts(datasets_df, runs_df, window_days):
    runs_df["upload_time"] = pd.to_datetime(runs_df["upload_time"])
    for each did:
        upload = datasets_df[did].upload_date
        cutoff = upload + timedelta(days=window_days)
        count = len(runs within [upload, cutoff])
    datasets_df["run_count_12m"] = counts
    return datasets_df

compute_accessible_score(df, he1_scores_df):
    merged = df.merge(he1_scores_df[["did","fair_A"]], on="did", how="left")
    median_a = merged["fair_A"].median()
    merged["high_accessible"] = (merged["fair_A"] >= median_a).astype(int)
    return merged

build_analysis_df(datasets_df, runs_df, he1_scores_df, config):
    df = compute_12m_run_counts(datasets_df, runs_df)
    df = compute_accessible_score(df, he1_scores_df)
    df = encode_covariates(df)           # reuse from h-m1 survival_prep
    validate_preconditions(df, config.MIN_MATCHED_PAIRS)
    return df

validate_preconditions(df, min_pairs):
    n_high = (df["high_accessible"] == 1).sum()
    n_low  = (df["high_accessible"] == 0).sum()
    if n_high < min_pairs or n_low < min_pairs:
        raise ValueError(f"Insufficient groups: n_high={n_high}, n_low={n_low}, min={min_pairs}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_12m_run_counts | Window-based run aggregation per dataset |
| L-3-2 | compute_accessible_score + build_analysis_df + validate_preconditions | Accessible score merge, median split, full pipeline |

---

## A-4: Matching Pipeline Integration [Complexity: 3, Budget: 2]

Applied: propensity-score-matching-reuse

### API Signatures

```python
# File: src/matching_accessible.py

def run_accessible_matching(
    analysis_df: pd.DataFrame,
    cfg,
    caliper_factor: float = None,
    ratio: int = 1,
) -> tuple:
    """Propensity matching on high_accessible treatment.
    Calls h-m1 functions directly with treatment_col='high_accessible'.
    Returns: (matched_df, smd_df, matching_meta: dict)
    """
    ...
```

### Pseudo-code

```
run_accessible_matching(analysis_df, cfg, caliper_factor, ratio):
    covariate_cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    available_covs = [c for c in covariate_cols if c in analysis_df.columns]
    seed = getattr(cfg, "SEED", 42)
    treatment_col = "high_accessible"          # ← NOT "high_findable"

    model, ps_scores = fit_propensity_model(   # from h-m1 matching.py
        analysis_df, available_covs, treatment_col, seed)

    logit_ps = np.log(ps_scores / (1 - ps_scores))
    cf = caliper_factor or getattr(cfg, "CALIPER_FACTOR", 0.2)
    caliper = cf * logit_ps.std()

    matched_df = nearest_neighbor_match(       # from h-m1 matching.py
        analysis_df, ps_scores, treatment_col, caliper, ratio)

    smd_df = compute_smd(                      # from h-m1 matching.py
        analysis_df, matched_df, available_covs, treatment_col)

    n_matched_pairs = len(matched_df) // (ratio + 1)
    smd_max = float(smd_df["smd_after"].max()) if len(smd_df) > 0 else float("nan")
    matching_meta = {
        "n_matched_pairs": n_matched_pairs,
        "smd_max": smd_max,
        "caliper_used": caliper,
        "balance_ok": smd_max < getattr(cfg, "SMD_THRESHOLD", 0.1),
    }
    return matched_df, smd_df, matching_meta
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_accessible_matching | Wrap h-m1 PS functions with high_accessible treatment |
| L-4-2 | matching_meta validation | Log balance_ok, raise warning if SMD > threshold |

---

## A-5: MWU Analysis Module [Complexity: 4, Budget: 4]

Applied: non-parametric-matched-group-comparison
Applied: rank-biserial-effect-size

### API Signatures

```python
# File: src/mwu_analysis.py
from scipy import stats
import statsmodels.formula.api as smf

def compute_effect_size_r(mwu_stat: float, n1: int, n2: int) -> float:
    """Rank-biserial r = 1 - (2*U) / (n1*n2). Range [-1, 1]."""
    ...

def run_mwu_unadjusted(
    df: pd.DataFrame,
    dv_col: str = 'run_count_12m',
    treatment_col: str = 'high_accessible',
) -> dict:
    """MWU test on full unmatched sample.
    Returns: {mwu_stat, p_value, n_high, n_low, high_mean, low_mean}
    """
    ...

def run_mwu_matched(
    matched_df: pd.DataFrame,
    dv_col: str = 'run_count_12m',
    treatment_col: str = 'high_accessible',
) -> dict:
    """MWU test on matched sample; computes rank-biserial r.
    Returns: {mwu_stat, p_value, effect_size_r, n_high, n_low,
              high_mean, low_mean, direction_pass}
    """
    ...

def run_ols_standardized(
    df: pd.DataFrame,
    fair_cols: list,
    dv_col: str = 'run_count_12m',
) -> dict:
    """Log-transform DV, z-score predictors, fit OLS.
    Returns: {beta_coefficients: dict, p_values: dict,
              r_squared, accessible_beta, accessible_p}
    """
    ...

def run_mechanism_check(results: dict) -> None:
    """Assert matched pairs >= 30, SMD < 0.1, high_mean >= 0; print mechanism log.
    Raises AssertionError if any condition fails.
    """
    ...
```

### Tensor Shapes (Data Shapes)

| Variable | Shape | Note |
|----------|-------|------|
| df (input) | [N, F] | N datasets, F features |
| matched_df | [M, F] | M = 2 * n_matched_pairs |
| high_group / low_group | [n_high] / [n_low] | DV values per group |
| beta_coefficients | dict[str, float] | One per predictor |

### Pseudo-code

```
compute_effect_size_r(mwu_stat, n1, n2):
    return 1.0 - (2.0 * mwu_stat) / (n1 * n2)

run_mwu_unadjusted(df, dv_col, treatment_col):
    high = df[df[treatment_col] == 1][dv_col].dropna()
    low  = df[df[treatment_col] == 0][dv_col].dropna()
    stat, p = scipy.stats.mannwhitneyu(high, low, alternative="two-sided")
    return {mwu_stat: stat, p_value: p, n_high: len(high), n_low: len(low),
            high_mean: high.mean(), low_mean: low.mean()}

run_mwu_matched(matched_df, dv_col, treatment_col):
    high = matched_df[matched_df[treatment_col] == 1][dv_col].dropna()
    low  = matched_df[matched_df[treatment_col] == 0][dv_col].dropna()
    stat, p = scipy.stats.mannwhitneyu(high, low, alternative="two-sided")
    r = compute_effect_size_r(stat, len(high), len(low))
    direction_pass = high.mean() > low.mean()
    return {mwu_stat: stat, p_value: p, effect_size_r: r,
            n_high: len(high), n_low: len(low),
            high_mean: high.mean(), low_mean: low.mean(),
            direction_pass: direction_pass}

run_ols_standardized(df, fair_cols, dv_col):
    df2 = df.copy()
    df2["log_dv"] = np.log1p(df2[dv_col])
    for col in fair_cols:
        mu, sd = df2[col].mean(), df2[col].std()
        df2[col + "_z"] = (df2[col] - mu) / sd if sd > 0 else 0.0
    z_cols = [c + "_z" for c in fair_cols]
    formula = "log_dv ~ " + " + ".join(z_cols)
    model = smf.ols(formula, data=df2).fit()
    accessible_z = "fair_A_z"  # key predictor
    return {beta_coefficients: dict(model.params),
            p_values: dict(model.pvalues),
            r_squared: model.rsquared,
            accessible_beta: model.params.get(accessible_z, float("nan")),
            accessible_p: model.pvalues.get(accessible_z, float("nan"))}

run_mechanism_check(results):
    assert results["n_matched_pairs"] >= 30, f"Too few pairs: {results['n_matched_pairs']}"
    assert results["smd_max"] < 0.1, f"SMD imbalance: {results['smd_max']}"
    assert results["high_mean"] >= 0, "high_mean must be non-negative"
    print("[MWU] Mechanism check PASSED:", results)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_effect_size_r | Rank-biserial r formula |
| L-5-2 | run_mwu_unadjusted + run_mwu_matched | MWU tests on full and matched samples |
| L-5-3 | run_ols_standardized | Log-DV, z-score, OLS regression |
| L-5-4 | run_mechanism_check | Assertion-based mechanism validation |

---

## A-6: Ablation Experiments [Complexity: 3, Budget: 2]

Applied: non-parametric-matched-group-comparison

### API Signatures

```python
# File: src/ablation.py

def run_ablation_caliper(
    analysis_df: pd.DataFrame,
    cfg,
    caliper_factors: list = None,
) -> pd.DataFrame:
    """Run matching + MWU across multiple caliper_factor values.
    caliper_factors: list of floats, default [0.1, 0.2, 0.3]
    Returns: DataFrame[caliper_factor, n_matched_pairs, smd_max, p_value, effect_size_r]
    """
    ...

def run_ablation_ratio(
    analysis_df: pd.DataFrame,
    cfg,
    ratios: list = None,
) -> pd.DataFrame:
    """Run matching + MWU across multiple matching ratios (1:1, 1:2, 1:3).
    ratios: list of ints, default [1, 2, 3]
    Returns: DataFrame[ratio, n_matched_pairs, smd_max, p_value, effect_size_r]
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_ablation_caliper | Sweep caliper_factor values, collect MWU results |
| L-6-2 | run_ablation_ratio | Sweep matching ratios, collect MWU results |

---

## A-9: Unit Tests [Complexity: 2, Budget: 2]

### API Signatures

```python
# File: tests/test_accessible_prep.py

def test_compute_12m_run_counts_basic():
    """Verify run_count_12m counts only runs within 365-day window."""
    ...

def test_compute_accessible_score_median_split():
    """Verify high_accessible == 1 for fair_A >= median, 0 otherwise."""
    ...

def test_validate_preconditions_raises():
    """Verify ValueError raised when n_high < min_pairs."""
    ...

# File: tests/test_mwu_analysis.py

def test_compute_effect_size_r_bounds():
    """Verify r in [-1, 1] for valid U, n1, n2."""
    ...

def test_run_mwu_unadjusted_returns_keys():
    """Verify dict keys: mwu_stat, p_value, n_high, n_low, high_mean, low_mean."""
    ...

def test_run_mwu_matched_direction_pass():
    """Verify direction_pass=True when high_mean > low_mean."""
    ...

def test_run_mechanism_check_fails_on_few_pairs():
    """Verify AssertionError when n_matched_pairs < 30."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | tests/test_accessible_prep.py | Unit tests for accessible_prep module |
| L-9-2 | tests/test_mwu_analysis.py | Unit tests for mwu_analysis module |

---

## Subtask Budget Summary

| Epic | Allocated | Used |
|------|-----------|------|
| A-3 AccessiblePrep | 2 | 2 |
| A-4 Matching Integration | 2 | 2 |
| A-5 MWU Analysis | 4 | 4 |
| A-6 Ablation | 2 | 2 |
| A-9 Unit Tests | 2 | 2 |
| **Total** | **12** | **12** |
