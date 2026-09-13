# H-M2 Logic: Predictive Validity of Epistemic Composite for Adversarial Robustness

Applied: BCa-bootstrap-partial-spearman (H-M1 _bca_bootstrap_partial pattern reuse + LOO-AUC percentile bootstrap)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-M1 code
**Analyzed Path**: `docs/youra_research/20260430_buildingtrust/h-m1/code/`
**Relevant Symbols**:
- `_bca_bootstrap_partial(df, x, y, covar, n_boot, seed, alpha=0.05) -> tuple[float, float]`
  - Uses `pg.partial_corr(data=d, x=x, y=y, covar=covar, method="spearman")`
  - BCa: z0 via bootstrap, acceleration `a` via jackknife; returns `(ci_lo, ci_hi)`
  - Parameter names: `x`, `y`, `covar` (not `x_col`, `y_col`) — verified from actual code
- `load_score_matrix(path: str) -> pd.DataFrame` — raises `FileNotFoundError` / `ValueError`
- `validate_schema(df, required_cols, gate_cols) -> bool` — raises on missing cols or NaN in gate_cols
- `REQUIRED_COLS: list[str]` — same 8-column schema reused in H-M2

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual H-M1 Code)

```python
# From: h-m1/code/analyzers.py (ACTUAL CODE — verified)

def _bca_bootstrap_partial(
    df: pd.DataFrame,
    x: str,          # ← verified: "x" not "x_col"
    y: str,          # ← verified: "y" not "y_col"
    covar: str,      # ← verified: "covar" not "covariate"
    n_boot: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for pg.partial_corr Spearman. Returns (ci_lo, ci_hi)."""
    ...

# From: h-m1/code/data_loader.py (ACTUAL CODE — verified)

def load_score_matrix(path: str) -> pd.DataFrame:
    """Load and validate greedy score matrix. Raises ValueError on schema/row issues."""
    ...

def validate_schema(
    df: pd.DataFrame,
    required_cols: list[str],
    gate_cols: list[str],
) -> bool:
    """Check all required_cols present and no NaN in gate_cols. Returns True if valid."""
    ...
```

**Verified from**: `h-m1/code/analyzers.py` lines 69–126, `h-m1/code/data_loader.py` lines 9–42

**Key notes for H-M2 reimplementation**:
- `_bca_bootstrap_partial` inner `_stat(d)` calls `pg.partial_corr(data=d, x=x, y=y, covar=covar, method="spearman")`
- `rho_obs = _stat(df)` (not re-called from `pg` separately)
- BCa `_adj` function: `norm.cdf(z0 + inner / (1.0 - a * inner))` where `inner = z0 + z_val`
- jackknife uses `df.drop(index=df.index[i]).reset_index(drop=True)` — matches H-M2 pattern exactly

---

## A-3: Partial Rho Analyzers [Complexity: 10, Budget: 2 subtasks]

Applied: BCa-bootstrap-partial-spearman (direct reuse of H-M1 _bca_bootstrap_partial structure)

### API Signatures

```python
def _bca_bootstrap_partial(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for partial Spearman rho via pg.partial_corr. Returns (ci_lo, ci_hi)."""
    ...

def compute_partial_rho_advglue(
    df: pd.DataFrame,
    n_boot: int,
    seed: int,
) -> dict:
    """Partial Spearman rho for AdvGLUE and ANLI with BCa CIs.

    Returns dict with keys:
      rho_partial_advglue (float)   — partial rho(ECE, AdvGLUE_drop | MMLU_acc)
      bca_ci_low (float)            — 95% BCa CI lower bound for AdvGLUE partial rho
      bca_ci_high (float)           — 95% BCa CI upper bound
      ci_excludes_zero (bool)       — True if ci_low > 0 or ci_high < 0
      passes_threshold (bool)       — abs(rho_partial_advglue) >= PARTIAL_RHO_THRESHOLD AND ci_excludes_zero
      rho_partial_anli (float)      — partial rho(ECE, ANLI_drop | MMLU_acc)
      anli_bca_ci_low (float)       — 95% BCa CI lower bound for ANLI partial rho
      anli_bca_ci_high (float)      — 95% BCa CI upper bound for ANLI
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | _bca_bootstrap_partial signature | Implement BCa bootstrap for partial Spearman; exact H-M1 parameter names (x, y, covar); handle NaN boot samples; jackknife acceleration |
| L-3-2 | compute_partial_rho_advglue return types | Call _bca_bootstrap_partial twice (AdvGLUE + ANLI); assemble full return dict; ci_excludes_zero = (ci_low > 0 or ci_high < 0); passes_threshold checks abs() >= PARTIAL_RHO_THRESHOLD |

### Pseudo-code

```
compute_partial_rho_advglue(df, n_boot, seed):
    # AdvGLUE arm
    res_adv = pg.partial_corr(data=df, x=PARTIAL_X, y=PARTIAL_Y_ADV, covar=COVARIATE, method="spearman")
    rho_adv = float(res_adv["r"].values[0])
    ci_lo_adv, ci_hi_adv = _bca_bootstrap_partial(df, PARTIAL_X, PARTIAL_Y_ADV, COVARIATE, n_boot, seed)
    ci_excl = (ci_lo_adv > 0 or ci_hi_adv < 0)
    passes = abs(rho_adv) >= PARTIAL_RHO_THRESHOLD and ci_excl

    # ANLI arm (seed+1 to keep independent)
    res_anli = pg.partial_corr(data=df, x=PARTIAL_X, y=PARTIAL_Y_ANLI, covar=COVARIATE, method="spearman")
    rho_anli = float(res_anli["r"].values[0])
    ci_lo_anli, ci_hi_anli = _bca_bootstrap_partial(df, PARTIAL_X, PARTIAL_Y_ANLI, COVARIATE, n_boot, seed+1)

    return {rho_partial_advglue, bca_ci_low, bca_ci_high, ci_excludes_zero, passes_threshold,
            rho_partial_anli, anli_bca_ci_low, anli_bca_ci_high}
```

---

## A-4: LOO Logistic Regression [Complexity: 11, Budget: 2 subtasks]

Applied: Standard PyTorch — sklearn LOO logistic regression AUC pattern

### API Signatures

```python
def _run_loo_logistic(
    X: np.ndarray,   # shape (N, F) — already standardized
    y: np.ndarray,   # shape (N,)   — binary int labels
    seed: int,
) -> np.ndarray:
    """LOO cross-validation with LogisticRegression. Returns y_proba of shape (N,)."""
    ...

def compute_loo_auc(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,   # "top_quartile_advglue"
    seed: int,
) -> dict:
    """LOO-AUC for given feature set.

    Returns dict with keys:
      auc (float)               — roc_auc_score(y_true, y_proba)
      y_proba (np.ndarray)      — shape (N,) predicted probabilities
      y_true (np.ndarray)       — shape (N,) integer labels
      feature_cols (list[str])  — echo of input feature_cols
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | _run_loo_logistic API | LeaveOneOut loop; StandardScaler fit on train fold only (no leakage); LogisticRegression(C=LR_C, max_iter=LR_MAX_ITER, random_state=seed); collect predict_proba[:,1] at each LOO position |
| L-4-2 | compute_loo_auc error handling | Extract X=[N,F], y=[N,]; guard: raise ValueError if len(np.unique(y)) < 2; call _run_loo_logistic; compute roc_auc_score; return full dict |

### Pseudo-code

```
_run_loo_logistic(X, y, seed):  # X: (N,F), y: (N,)
    loo = LeaveOneOut()
    y_proba = np.zeros(len(y))
    for train_idx, test_idx in loo.split(X):
        X_tr, X_te = X[train_idx], X[test_idx]
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)
        clf = LogisticRegression(C=LR_C, max_iter=LR_MAX_ITER, random_state=seed)
        clf.fit(X_tr_s, y[train_idx])
        y_proba[test_idx] = clf.predict_proba(X_te_s)[:, 1]
    return y_proba  # (N,)

compute_loo_auc(df, feature_cols, target_col, seed):
    X = df[feature_cols].values        # (N, F)
    y = df[target_col].values.astype(int)  # (N,)
    if len(np.unique(y)) < 2:
        raise ValueError(f"target_col '{target_col}' has fewer than 2 classes")
    y_proba = _run_loo_logistic(X, y, seed)
    auc = roc_auc_score(y, y_proba)
    return {auc, y_proba, y_true: y, feature_cols}
```

---

## A-5: Delta AUC Bootstrap [Complexity: 13, Budget: 2 subtasks]

Applied: percentile-bootstrap-delta-AUC (LOO AUC difference with paired resampling)

### API Signatures

```python
def compute_delta_auc_bootstrap(
    df: pd.DataFrame,
    composite_cols: list[str],   # ["ECE", "TruthfulQA_pct", "Brier"]
    baseline_cols: list[str],    # ["MMLU_acc"]
    target_col: str,             # "top_quartile_advglue"
    n_boot: int,                 # 10_000
    seed: int,                   # 42
) -> dict:
    """Bootstrap CI for delta LOO-AUC (composite minus baseline).

    Returns dict with keys:
      auc_composite (float)          — observed LOO-AUC for composite predictor
      auc_baseline (float)           — observed LOO-AUC for MMLU-only baseline
      delta_auc (float)              — auc_composite - auc_baseline
      delta_auc_ci (list[float])     — [ci_low, ci_high] 95% percentile bootstrap CI
      ci_excludes_zero (bool)        — delta_auc_ci[0] > 0
      passes_delta_threshold (bool)  — delta_auc >= DELTA_AUC_THRESHOLD AND ci_excludes_zero
      passes_auc_threshold (bool)    — auc_composite >= AUC_THRESHOLD
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_delta_auc_bootstrap internals | Observed delta from full-data LOO; paired bootstrap loop: resample row indices with replacement, run LOO on each bootstrap sample for both composite and baseline, collect delta; 95% percentile CI from boot_deltas array |
| L-5-2 | nested LOO edge cases | Bootstrap sample may produce single-class y after resampling: wrap inner LOO in try/except, append np.nan on failure; filter nan before CI; guard len(valid) >= n_boot*0.9 else warn; ensure StandardScaler fit inside each LOO fold (no leakage across bootstrap) |

### Pseudo-code

```
compute_delta_auc_bootstrap(df, composite_cols, baseline_cols, target_col, n_boot, seed):
    # Observed LOO-AUC (full data)
    comp_result  = compute_loo_auc(df, composite_cols, target_col, seed)
    base_result  = compute_loo_auc(df, baseline_cols, target_col, seed)
    auc_c = comp_result["auc"]
    auc_b = base_result["auc"]
    delta_obs = auc_c - auc_b

    # Percentile bootstrap for CI on delta
    rng = np.random.default_rng(seed)
    boot_deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        df_b = df.iloc[idx].reset_index(drop=True)
        y_b = df_b[target_col].values.astype(int)
        if len(np.unique(y_b)) < 2:          # single-class edge case
            boot_deltas.append(np.nan)
            continue
        try:
            auc_bc = compute_loo_auc(df_b, composite_cols, target_col, seed)["auc"]
            auc_bb = compute_loo_auc(df_b, baseline_cols, target_col, seed)["auc"]
            boot_deltas.append(auc_bc - auc_bb)
        except Exception:
            boot_deltas.append(np.nan)

    arr = np.array(boot_deltas)
    valid = arr[~np.isnan(arr)]
    if len(valid) < n_boot * 0.9:
        warnings.warn(f"Only {len(valid)}/{n_boot} valid bootstrap samples")
    ci_lo = float(np.percentile(valid, 2.5))
    ci_hi = float(np.percentile(valid, 97.5))

    return {
        auc_composite: auc_c,
        auc_baseline: auc_b,
        delta_auc: delta_obs,
        delta_auc_ci: [ci_lo, ci_hi],
        ci_excludes_zero: ci_lo > 0,
        passes_delta_threshold: delta_obs >= DELTA_AUC_THRESHOLD and ci_lo > 0,
        passes_auc_threshold: auc_c >= AUC_THRESHOLD,
    }
```

### Tensor Shapes (non-obvious)

| Variable | Shape | Note |
|----------|-------|------|
| X (composite) | (N, 3) | N=30, F=3 features |
| X (baseline) | (N, 1) | MMLU_acc only |
| y | (N,) | binary int, N_pos ≈ 7–8 |
| y_proba | (N,) | LOO predicted probabilities |
| boot_deltas | (n_boot,) | some entries may be nan |

---

## Summary: Subtask Allocation [6/6 used]

| ID | Task | Subtask | Priority |
|----|------|---------|----------|
| L-3-1 | A-3 | _bca_bootstrap_partial signature + H-M1 exact parameter names | High |
| L-3-2 | A-3 | compute_partial_rho_advglue return dict + ci_excludes_zero logic | High |
| L-4-1 | A-4 | _run_loo_logistic with per-fold StandardScaler (no data leakage) | High |
| L-4-2 | A-4 | compute_loo_auc error handling + single-class guard | High |
| L-5-1 | A-5 | compute_delta_auc_bootstrap paired bootstrap internals | Highest |
| L-5-2 | A-5 | nested LOO edge cases: single-class, nan filtering, leakage guard | Highest |
