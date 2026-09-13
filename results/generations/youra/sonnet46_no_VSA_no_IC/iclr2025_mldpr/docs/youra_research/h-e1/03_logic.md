# Logic Design: H-E1
# PELT Change-Point Detection — API Signatures, Pseudo-code, Algorithms

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Budget:** 4 subtasks (A-2 × 2, A-3 × 2)

Applied: N/A — no domain-relevant Archon KB content found for statistical analysis domain (all queries returned HuggingFace diffusion model content, similarity 0.28–0.42)

---

## Codebase Analysis (Serena)

**Analyzed Path:** `docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/`

Key findings from archive:
- `ingest_pwc.py`: `fetch_pwc_benchmarks(min_papers=MIN_PAPERS)` returns DataFrame with columns `[name, dataset_name, task_name, paper_count, year_introduced, num_rows]`. Uses `load_dataset("pwc-archive/evaluation-tables", split="train")`.
- `derive.py`: `compute_result_cov(results_df)` returns Series indexed by benchmark_name. CoV = `std(ddof=1)/mean` per group. Filters groups with < 3 rows (returns NaN).
- Archive `run.py` orchestrates the pipeline — different scope (includes ablation/join not needed for H-E1).
- No existing `pipeline.py`, `evaluate.py`, or `visualize.py` in archive — these are new modules.

**Reuse decision:** Copy `ingest_pwc.py` and `derive.py` verbatim. Implement `pipeline.py`, `evaluate.py`, `visualize.py`, `run_experiment.py` fresh.

---

## Subtask L-2-1: `ols_detrend()` — OLS Detrending

**Parent Epic:** A-2 (pipeline.py, complexity=10)
**File:** `h-e1/code/pipeline.py`

### API Signature

```python
def ols_detrend(
    paper_counts: np.ndarray,   # shape (N,) — raw paper counts per benchmark
    cov_values: np.ndarray,     # shape (N,) — raw CoV per benchmark (parallel to paper_counts)
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Sort benchmarks by paper_count, fit OLS CoV ~ paper_count, return residuals.

    Returns:
        sorted_paper_counts: np.ndarray shape (N,) — ascending paper_count
        residual_cov: np.ndarray shape (N,) — OLS residuals (PELT input)
        ols_metrics: dict with keys:
            slope: float
            intercept: float
            rho: float         # Pearson r
            r2: float          # r-squared
            p_value: float     # OLS p-value for slope
    """
```

### Pseudo-code

```python
def ols_detrend(paper_counts, cov_values):
    # Step 1: Sort ascending by paper_count (stable sort)
    sort_idx = np.argsort(paper_counts, kind="stable")
    sorted_pc = paper_counts[sort_idx]      # shape (N,)
    sorted_cov = cov_values[sort_idx]       # shape (N,)

    # Step 2: OLS fit
    slope, intercept, rho, p_value, _ = scipy.stats.linregress(sorted_pc, sorted_cov)
    r2 = rho ** 2

    # Step 3: Residuals
    fitted = slope * sorted_pc + intercept
    residual_cov = sorted_cov - fitted      # shape (N,)

    ols_metrics = {
        "slope": float(slope),
        "intercept": float(intercept),
        "rho": float(rho),
        "r2": float(r2),
        "p_value": float(p_value),
    }

    return sorted_pc, residual_cov, ols_metrics
```

### Edge Cases
- If N < 2: raises `ValueError("Insufficient data for OLS: N={N}")`
- If `cov_values.std() == 0`: raises `ValueError("Zero variance in CoV — degenerate input")`

---

## Subtask L-2-2: `run_pelt_changepoint()` — PELT Detection

**Parent Epic:** A-2 (pipeline.py, complexity=10)
**File:** `h-e1/code/pipeline.py`

### API Signature

```python
def run_pelt_changepoint(
    paper_counts: np.ndarray,           # shape (N,) — raw paper counts
    cov_values: np.ndarray,             # shape (N,) — raw CoV values
    pen_range: tuple[float, float] = (1.0, 50.0),
    n_pen: int = 20,
    min_size: int = 3,
) -> dict:
    """
    Run OLS detrend + PELT change-point detection with BIC penalty.

    Returns dict with keys:
        paper_count_star: float | None     — paper_count at detected breakpoint
        breakpoint_idx: int | None         — 0-based index in sorted array
        pen_used: float                    — BIC penalty value used
        n_bkps: int                        — number of detected breakpoints
        residual_cov_sorted: np.ndarray    — shape (N,) sorted residuals
        sorted_paper_counts: np.ndarray    — shape (N,) sorted paper counts
        bkps_list: list[list[int]]         — breakpoints for each pen in sweep
        pen_values: np.ndarray             — shape (n_pen,) penalty sweep values
        ols_metrics: dict                  — from ols_detrend()
    """
```

### Pseudo-code

```python
def run_pelt_changepoint(paper_counts, cov_values,
                          pen_range=(1.0, 50.0), n_pen=20, min_size=3):
    # Step 1: OLS detrend + sort
    sorted_pc, residual_cov, ols_metrics = ols_detrend(paper_counts, cov_values)
    T = len(residual_cov)

    # Step 2: BIC penalty (L2 cost, 1D Gaussian signal)
    sigma = residual_cov.std(ddof=1)
    bic_pen = sigma ** 2 * np.log(T)   # Killick et al. 2012 formula

    # Step 3: Penalty sensitivity sweep
    pen_values = np.logspace(
        np.log10(pen_range[0]),
        np.log10(pen_range[1]),
        n_pen,
    )
    algo = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(residual_cov)
    bkps_list = [algo.predict(pen=p) for p in pen_values]

    # Step 4: Primary detection at BIC penalty
    bkps = algo.predict(pen=bic_pen)
    # bkps convention: last element = T (end sentinel); internal breaks are bkps[:-1]
    n_bkps = len(bkps) - 1  # subtract end sentinel

    if n_bkps >= 1:
        bkp_idx = bkps[0] - 1      # convert 1-based ruptures index to 0-based
        paper_count_star = float(sorted_pc[bkp_idx])
    else:
        bkp_idx = None
        paper_count_star = None

    # Log activation indicator
    print(f"PELT detected {n_bkps} breakpoint(s) at index {bkp_idx} "
          f"→ paper_count* = {paper_count_star}")

    return {
        "paper_count_star": paper_count_star,
        "breakpoint_idx": bkp_idx,
        "pen_used": float(bic_pen),
        "n_bkps": n_bkps,
        "residual_cov_sorted": residual_cov,
        "sorted_paper_counts": sorted_pc,
        "bkps_list": bkps_list,
        "pen_values": pen_values,
        "ols_metrics": ols_metrics,
    }
```

### Edge Cases
- If `n_bkps == 0`: `paper_count_star = None`, `breakpoint_idx = None` — gate will fail
- If `bic_pen` is very large (huge sigma): PELT may return no breakpoints — log and continue

---

## Subtask L-3-1: `run_permutation_test()` — Primary Gate

**Parent Epic:** A-3 (evaluate.py, complexity=13)
**File:** `h-e1/code/evaluate.py`

### API Signature

```python
def run_permutation_test(
    paper_counts: np.ndarray,       # shape (N,) — original paper counts
    cov_values: np.ndarray,         # shape (N,) — original CoV values
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Permutation test: shuffle paper_count labels, rerun full pipeline, compare breakpoint positions.

    Null hypothesis: paper_count assignment is arbitrary (no structural break).
    Test statistic: breakpoint_idx from PELT on residual CoV.
    p-value: fraction of null statistics <= observed (one-sided, lower is more extreme).

    Returns dict with keys:
        permutation_p: float              — p-value
        null_distribution: np.ndarray     — shape (n_permutations,) breakpoint positions
        observed_bkp_idx: int | None      — observed breakpoint index
    """
```

### Pseudo-code

```python
def run_permutation_test(paper_counts, cov_values, n_permutations=1000, seed=42):
    rng = np.random.default_rng(seed)

    # Observed statistic
    observed = run_pelt_changepoint(paper_counts, cov_values)
    observed_bkp_idx = observed["breakpoint_idx"]

    # If no breakpoint detected: p-value is 1.0 (null trivially not rejected)
    if observed_bkp_idx is None:
        return {
            "permutation_p": 1.0,
            "null_distribution": np.array([]),
            "observed_bkp_idx": None,
        }

    # Null distribution: shuffle paper_counts, keep cov_values fixed
    null_bkp_positions = []
    for _ in range(n_permutations):
        shuffled_pc = rng.permutation(paper_counts)   # shuffle paper_count labels
        null_result = run_pelt_changepoint(shuffled_pc, cov_values)
        null_bkp = null_result["breakpoint_idx"]
        # Treat "no breakpoint" as position T (rightmost — least extreme)
        null_bkp_positions.append(null_bkp if null_bkp is not None else len(paper_counts))

    null_dist = np.array(null_bkp_positions)

    # p-value: fraction of null breakpoints <= observed (lower index = more extreme break)
    permutation_p = float(np.sum(null_dist <= observed_bkp_idx) / n_permutations)

    return {
        "permutation_p": permutation_p,
        "null_distribution": null_dist,
        "observed_bkp_idx": observed_bkp_idx,
    }
```

### Statistical Rationale
Null: shuffle paper_count labels → destroys any real structural relationship. If PELT on shuffled data also finds early breaks frequently, the observed break is not significant. We count how often null ≤ observed (earlier or equal break) — small fraction → low p-value → significant.

---

## Subtask L-3-2: `run_bootstrap_ci()` + `run_piecewise_ftest()` + `verify_mechanism_activated()`

**Parent Epic:** A-3 (evaluate.py, complexity=13)
**File:** `h-e1/code/evaluate.py`

### API Signatures

```python
def run_bootstrap_ci(
    paper_counts: np.ndarray,       # shape (N,)
    cov_values: np.ndarray,         # shape (N,)
    n_resamples: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> dict:
    """
    Bootstrap CI for paper_count* via percentile method.
    Resample N benchmarks with replacement; rerun full pipeline each iteration.

    Returns:
        bootstrap_ci_lower: float
        bootstrap_ci_upper: float
        bootstrap_ci_width: float
        bootstrap_estimates: np.ndarray shape (n_resamples,)  — paper_count* per resample
    """

def run_piecewise_ftest(
    paper_counts: np.ndarray,       # shape (N,) sorted ascending
    cov_values: np.ndarray,         # shape (N,) aligned with paper_counts
    paper_count_star: float,        # detected breakpoint value
) -> dict:
    """
    F-test: piecewise linear vs single linear model at paper_count_star.

    Returns:
        piecewise_f_p: float        — F-test p-value
        f_statistic: float
    """

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Check all mechanism activation indicators.

    Returns:
        (all_pass: bool, indicators: dict)
        indicators keys: pelt_detected_breakpoint, paper_count_star_in_range,
                         permutation_p_significant
    """
```

### Pseudo-code: `run_bootstrap_ci()`

```python
def run_bootstrap_ci(paper_counts, cov_values, n_resamples=1000, seed=42,
                      confidence_level=0.95):
    rng = np.random.default_rng(seed)
    N = len(paper_counts)
    estimates = []

    for _ in range(n_resamples):
        # Resample N benchmarks with replacement
        idx = rng.integers(0, N, size=N)
        boot_pc = paper_counts[idx]
        boot_cov = cov_values[idx]

        result = run_pelt_changepoint(boot_pc, boot_cov)
        pcs = result["paper_count_star"]
        estimates.append(pcs if pcs is not None else np.nan)

    estimates = np.array(estimates)
    # Drop NaN (no breakpoint detected in resample)
    valid = estimates[~np.isnan(estimates)]

    alpha = 1 - confidence_level
    ci_lower = float(np.nanpercentile(estimates, 100 * alpha / 2))
    ci_upper = float(np.nanpercentile(estimates, 100 * (1 - alpha / 2)))
    ci_width = ci_upper - ci_lower

    return {
        "bootstrap_ci_lower": ci_lower,
        "bootstrap_ci_upper": ci_upper,
        "bootstrap_ci_width": float(ci_width),
        "bootstrap_estimates": estimates,
    }
```

### Pseudo-code: `run_piecewise_ftest()`

```python
def run_piecewise_ftest(paper_counts, cov_values, paper_count_star):
    import statsmodels.api as sm

    # Sort by paper_count
    sort_idx = np.argsort(paper_counts)
    pc = paper_counts[sort_idx].astype(float)
    cov = cov_values[sort_idx]

    # Piecewise linear: dummy variable for post-break segment
    above = (pc >= paper_count_star).astype(float)
    pc_above = pc * above     # interaction term

    # Full model: cov ~ pc + above + pc_above (piecewise linear)
    X_full = sm.add_constant(np.column_stack([pc, above, pc_above]))
    model_full = sm.OLS(cov, X_full).fit()

    # Restricted model: cov ~ pc (single linear)
    X_restricted = sm.add_constant(pc)
    model_restricted = sm.OLS(cov, X_restricted).fit()

    # F-test for additional parameters
    f_stat = ((model_restricted.ssr - model_full.ssr) / 2) / (model_full.ssr / model_full.df_resid)
    from scipy.stats import f as f_dist
    piecewise_f_p = float(1 - f_dist.cdf(f_stat, dfn=2, dfd=model_full.df_resid))

    return {
        "piecewise_f_p": piecewise_f_p,
        "f_statistic": float(f_stat),
    }
```

### Pseudo-code: `verify_mechanism_activated()`

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    indicators = {
        "pelt_detected_breakpoint": results.get("n_bkps_detected", 0) >= 1,
        "paper_count_star_in_range": (
            results.get("paper_count_star") is not None
            and 10 <= results["paper_count_star"] <= 120
        ),
        "permutation_p_significant": results.get("permutation_p", 1.0) < 0.05,
    }
    all_pass = all(indicators.values())
    if not all_pass:
        print(f"MECHANISM VERIFICATION FAILED: {indicators}")
    else:
        print(
            f"MECHANISM VERIFIED: paper_count* = {results['paper_count_star']}, "
            f"p = {results['permutation_p']:.4f}"
        )
    return all_pass, indicators
```

---

## Array Shape Summary

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| paper_counts (input) | (N,) | int | N=111 after filtering |
| cov_values (input) | (N,) | float | result_CoV per benchmark |
| sorted_paper_counts | (N,) | int | ascending sort |
| residual_cov | (N,) | float | OLS residuals |
| null_distribution | (n_permutations,) | int | breakpoint positions |
| bootstrap_estimates | (n_resamples,) | float | paper_count* per resample (NaN if no bkp) |
| pen_values | (n_pen,) | float | log-spaced [1, 50] |
| bkps_list | list of list[int] | — | one list per penalty value |
