# Logic Design: H-M3
# Per-Pair Adversarial Rank Disruption Analysis

**Date:** 2026-08-20
**Hypothesis Type:** MECHANISM (INCREMENTAL on H-M2)
**Applied:** standard statistical pipeline pattern — sequential function calls with dict return types

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (incremental on H-M2)
**Status:** Base code patterns referenced from H-M2 architecture
**Analyzed Path:** `docs/youra_research/h-m2/code/` (referenced via architecture doc)
**Findings:** H-M2 implements `compute_partial_spearman()` and `fisher_z_test_vs_threshold()` as standalone functions in `analysis.py`. H-M3 reuses the same function signatures with identical parameters; only the column arguments differ per-pair. Bootstrap CI loop uses `np.random.choice` + `spearmanr` — same pattern confirmed in H-M2 logic.

**Applied:** standard stats pipeline pattern — flat function module, dict return schema, seed-before-bootstrap pattern
**Applied:** incremental reuse pattern — copy base functions, extend with new analysis functions rather than reimplementing

---

## External Dependencies API

| Library | Function | Exact Call Signature |
|---------|----------|----------------------|
| pingouin | partial_corr | `df.partial_corr(x='col', y='col', covar='mmlu', method='spearman', alternative='greater')` returns DataFrame with columns: `n, r, CI95%, r2, adj_r2, p-val, power` |
| scipy.stats | spearmanr | `spearmanr(x_array, y_array)` returns `SpearmanrResult(statistic, pvalue)` — use `.statistic` |
| scipy.stats | norm.cdf | `norm.cdf(z_stat)` returns float P(Z < z_stat) |
| numpy | arctanh | `np.arctanh(rho)` — raises if rho = ±1.0; guard with clip(-0.999, 0.999) |
| numpy | random.choice | `np.random.choice(n, n, replace=True)` for bootstrap index resampling |

**Critical Notes:**
- pingouin `alternative='greater'` tests H1: ρ > 0; we use this for the primary partial_corr call then separately test vs threshold with Fisher z
- For N < 30, asymptotic p-values from pingouin are unreliable — always report bootstrap CI alongside
- `np.arctanh(1.0)` is `inf`; clip inputs to `[-0.9999, 0.9999]`

---

## Data Shapes

| Object | Shape / Schema |
|--------|----------------|
| Input DataFrame `df` | (N, 6+) where N ≥ 10; cols: model_name(str), glue_score(float), advglue_score(float), anli_r1_score(float), anli_r3_score(float), mmlu(float) |
| bootstrap samples | list[float], len=1000 |
| partial_corr result | DataFrame (1, 7): n, r, CI95%, r2, adj_r2, p-val, power |
| Return dict from `compute_partial_spearman` | {rho: float, p_asymptotic: float, ci_lower: float, ci_upper: float, n: int} |
| Return dict from `fisher_z_test_vs_threshold` | {z: float, p: float, significant: bool} |
| Return dict from `run_full_analysis` | see Section: run_full_analysis schema |

---

## Subtask L-3-1: compute_partial_spearman — pingouin call + bootstrap

**Parent Epic:** A-3 (Partial Spearman per pair, complexity 10)

### Full Signature

```python
def compute_partial_spearman(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    covar_col: str = "mmlu",
    alternative: str = "greater",
    n_bootstrap: int = 1000,
) -> dict:
    """
    Partial Spearman rho(x_col, y_col | covar_col) via pingouin regression-on-ranks.
    Supplements with bootstrap CI for small N.

    Returns:
        {
          'rho': float,           # partial Spearman rho
          'p_asymptotic': float,  # pingouin asymptotic p-value
          'ci_lower': float,      # 2.5th percentile of bootstrap distribution
          'ci_upper': float,      # 97.5th percentile of bootstrap distribution
          'n': int                # sample size
        }
    """
```

### Pseudo-code

```
FUNCTION compute_partial_spearman(df, x_col, y_col, covar_col, alternative, n_bootstrap):
    # 1. Validate inputs
    ASSERT x_col, y_col, covar_col IN df.columns
    df_clean = df[[x_col, y_col, covar_col]].dropna()
    n = len(df_clean)
    LOG f"compute_partial_spearman: N={n}, pair=({x_col}, {y_col})"

    # 2. Partial Spearman via pingouin (regression-on-ranks)
    result_df = df_clean.partial_corr(
        x=x_col, y=y_col, covar=covar_col,
        method='spearman', alternative=alternative
    )
    rho = float(result_df['r'].iloc[0])
    p_asymptotic = float(result_df['p-val'].iloc[0])

    # 3. Bootstrap CI (1000 resamples of marginal Spearman, no partial control)
    #    NOTE: bootstrap is on raw Spearman(x, y) for CI width estimate
    #    because partial_corr bootstrap is computationally expensive for N~15
    np.random.seed(RANDOM_SEED)
    boot_rhos = []
    x_vals = df_clean[x_col].values
    y_vals = df_clean[y_col].values
    FOR _ IN range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        r, _ = spearmanr(x_vals[idx], y_vals[idx])
        boot_rhos.append(r)
    ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])

    RETURN {
        'rho': rho,
        'p_asymptotic': p_asymptotic,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'n': n
    }
```

---

## Subtask L-3-2: compute_partial_spearman — per-pair application

**Parent Epic:** A-3 (continuation)

### Application Pattern

```python
# In run_full_analysis():

# AdvGLUE pair
res_advglue = compute_partial_spearman(
    df, x_col='glue_score', y_col='advglue_score', covar_col='mmlu'
)
LOG f"rho_AdvGLUE = {res_advglue['rho']:.4f}, "
    f"p = {res_advglue['p_asymptotic']:.4f}, "
    f"CI = [{res_advglue['ci_lower']:.3f}, {res_advglue['ci_upper']:.3f}]"

# ANLI pair
res_anli = compute_partial_spearman(
    df, x_col='anli_r1_score', y_col='anli_r3_score', covar_col='mmlu'
)
LOG f"rho_ANLI = {res_anli['rho']:.4f}, "
    f"p = {res_anli['p_asymptotic']:.4f}, "
    f"CI = [{res_anli['ci_lower']:.3f}, {res_anli['ci_upper']:.3f}]"
```

---

## Subtask L-6-1: verify_mechanism_activated — 6 indicator checks

**Parent Epic:** A-6 (Mechanism verification + gate, complexity 9)

### Full Signature

```python
def verify_mechanism_activated(df: pd.DataFrame, results: dict) -> tuple[bool, dict]:
    """
    Verify all 6 H-M3 mechanism indicators.

    Args:
        df: loaded scores DataFrame
        results: dict containing rho_AdvGLUE, rho_ANLI, reversals_AdvGLUE, reversals_ANLI

    Returns:
        (all_ok: bool, indicators: dict with 6 bool values)
    """
```

### Pseudo-code

```
FUNCTION verify_mechanism_activated(df, results):
    required_cols = ['glue_score', 'advglue_score', 'anli_r1_score', 'anli_r3_score', 'mmlu']

    indicators = {
        'data_complete':    ALL(col IN df.columns FOR col IN required_cols),
        'n_sufficient':     len(df.dropna(subset=required_cols)) >= N_COMMON_MIN,
        'advglue_computed': 'rho_AdvGLUE' IN results AND results['rho_AdvGLUE'] IS NOT None,
        'anli_computed':    'rho_ANLI' IN results AND results['rho_ANLI'] IS NOT None,
        'pairs_differ':     abs(results.get('rho_AdvGLUE', 0) - results.get('rho_ANLI', 0)) > 0.001,
        'reversals_counted': 'reversals_AdvGLUE' IN results AND 'reversals_ANLI' IN results
    }
    all_ok = ALL(indicators.values())

    LOG f"Mechanism indicators: {indicators}"
    IF NOT all_ok:
        failed = [k FOR k, v IN indicators.items() IF NOT v]
        LOG f"WARNING: Failed indicators: {failed}"

    RETURN (all_ok, indicators)
```

---

## Additional Function Signatures

### fisher_z_test_vs_threshold

```python
def fisher_z_test_vs_threshold(
    rho: float,
    n: int,
    threshold: float = 0.4,
    alternative: str = "less",
) -> dict:
    """
    One-tailed Fisher z-test: H0: rho >= threshold; H1: rho < threshold.

    Formula:
        z_obs   = arctanh(clip(rho, -0.9999, 0.9999))
        z_thresh= arctanh(threshold)
        se      = 1 / sqrt(n - 3)
        z_stat  = (z_obs - z_thresh) / se
        p       = norm.cdf(z_stat)   # lower tail

    Returns:
        {'z': float, 'p': float, 'significant': bool}
    """
    z_obs = np.arctanh(np.clip(rho, -0.9999, 0.9999))
    z_thresh = np.arctanh(threshold)
    se = 1.0 / np.sqrt(n - 3)
    z_stat = (z_obs - z_thresh) / se
    p = float(norm.cdf(z_stat))
    return {'z': z_stat, 'p': p, 'significant': p < ALPHA}
```

### count_rank_reversals

```python
def count_rank_reversals(
    df: pd.DataFrame,
    id_col: str,
    ood_col: str,
    min_shift: int = 5,
) -> int:
    """
    Count models with |rank(id_col) - rank(ood_col)| >= min_shift.
    Ranks are ascending=False (rank 1 = best score).
    """
    ranks_id  = df[id_col].rank(ascending=False)
    ranks_ood = df[ood_col].rank(ascending=False)
    return int((abs(ranks_id - ranks_ood) >= min_shift).sum())
```

### evaluate_gate

```python
def evaluate_gate(
    rho_advglue: float, p_advglue: float,
    rho_anli: float,    p_anli: float,
    threshold: float = 0.4,
) -> bool:
    """
    SHOULD_WORK gate:
        (rho_advglue < threshold OR p_advglue >= ALPHA)
        AND
        (rho_anli < threshold OR p_anli >= ALPHA)
    """
    advglue_ok = (rho_advglue < threshold) or (p_advglue >= ALPHA)
    anli_ok    = (rho_anli    < threshold) or (p_anli    >= ALPHA)
    gate_passed = advglue_ok and anli_ok
    LOG f"Gate: AdvGLUE={'PASS' if advglue_ok else 'FAIL'}, ANLI={'PASS' if anli_ok else 'FAIL'} => {'PASS' if gate_passed else 'FAIL'}"
    return gate_passed
```

---

## run_full_analysis — Return Dict Schema

```python
def run_full_analysis(df: pd.DataFrame, rho_fairness: float) -> dict:
    """
    Orchestrates full H-M3 analysis pipeline.

    Returns dict (also saved to RESULTS_JSON):
    {
        # AdvGLUE pair
        'rho_AdvGLUE':   float,
        'p_AdvGLUE':     float,
        'ci_AdvGLUE':    [float, float],   # [lower, upper]
        'z_AdvGLUE':     float,
        'p_z_AdvGLUE':   float,            # Fisher z p-value vs threshold
        'sig_AdvGLUE':   bool,
        # ANLI pair
        'rho_ANLI':      float,
        'p_ANLI':        float,
        'ci_ANLI':       [float, float],
        'z_ANLI':        float,
        'p_z_ANLI':      float,
        'sig_ANLI':      bool,
        # Rank reversals
        'reversals_AdvGLUE': int,
        'reversals_ANLI':    int,
        # Gate + mechanism
        'gate_passed':       bool,
        'mechanism_ok':      bool,
        'mechanism_indicators': dict,
        # Reference
        'rho_fairness_HM1':  float,
        'n':                 int,
    }
    """
```

### Pseudo-code

```
FUNCTION run_full_analysis(df, rho_fairness):
    # 1. Per-pair partial Spearman
    r_adv  = compute_partial_spearman(df, 'glue_score', 'advglue_score')
    r_anli = compute_partial_spearman(df, 'anli_r1_score', 'anli_r3_score')

    # 2. Fisher z vs threshold
    fz_adv  = fisher_z_test_vs_threshold(r_adv['rho'],  r_adv['n'])
    fz_anli = fisher_z_test_vs_threshold(r_anli['rho'], r_anli['n'])

    # 3. Rank reversals
    rev_adv  = count_rank_reversals(df, 'glue_score',    'advglue_score')
    rev_anli = count_rank_reversals(df, 'anli_r1_score', 'anli_r3_score')

    # 4. Assemble results
    results = {
        'rho_AdvGLUE': r_adv['rho'],  'p_AdvGLUE': r_adv['p_asymptotic'],
        'ci_AdvGLUE':  [r_adv['ci_lower'], r_adv['ci_upper']],
        'z_AdvGLUE':   fz_adv['z'],   'p_z_AdvGLUE': fz_adv['p'],  'sig_AdvGLUE': fz_adv['significant'],
        'rho_ANLI':    r_anli['rho'], 'p_ANLI': r_anli['p_asymptotic'],
        'ci_ANLI':     [r_anli['ci_lower'], r_anli['ci_upper']],
        'z_ANLI':      fz_anli['z'],  'p_z_ANLI': fz_anli['p'],    'sig_ANLI': fz_anli['significant'],
        'reversals_AdvGLUE': rev_adv, 'reversals_ANLI': rev_anli,
        'rho_fairness_HM1': rho_fairness, 'n': r_adv['n'],
    }

    # 5. Mechanism + gate
    mech_ok, indicators = verify_mechanism_activated(df, results)
    gate = evaluate_gate(r_adv['rho'], r_adv['p_asymptotic'],
                         r_anli['rho'], r_anli['p_asymptotic'])
    results['gate_passed'] = gate
    results['mechanism_ok'] = mech_ok
    results['mechanism_indicators'] = indicators

    # 6. Save
    RESULTS_JSON.write_text(json.dumps(results, indent=2))
    LOG f"Results saved to {RESULTS_JSON}"

    RETURN results
```
