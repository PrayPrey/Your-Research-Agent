# Logic Design: H-M3
## Panel OLS Regression — Domain Coefficient Benchmark-Specificity

**Date:** 2026-08-20
**Hypothesis:** H-M3 (MECHANISM — INCREMENTAL on H-E1 + H-M1 + H-M2)

Applied: panel fixed-effects estimation pattern (entity demeaning via linearmodels PanelOLS)
Applied: clustered standard errors pattern (cluster_entity=True for within-model temporal autocorrelation)
Applied: likelihood ratio test pattern (LRT: 2*(LL_alt - LL_null), chi2 with domain df)
Applied: FDR correction pattern (Benjamini-Hochberg via statsmodels multipletests)
Applied: resume-capable batch evaluation pattern (cache-hit short-circuit before expensive GPU compute)

---

## Codebase Analysis (Serena)

Analyzed H-M2 actual code at `docs/youra_research/h-m2/code/`:

**`config.py` (verified field names):**
- `MODEL_SIZES: list[str] = ["70m", "1b", "6.9b"]` → H-M3 extends to all 16 sizes
- `CHECKPOINT_STEPS: list[int]` — 154 steps (0,1,2,4,...,143000) — reuse as-is
- `PILE_DOMAINS: list[str]` — 22 domains, exact names verified (e.g. `"Wikipedia (en)"`, `"Books3"`)
- `FOCAL_DOMAINS: dict = {"wikipedia": "Wikipedia (en)", "books": "Books3"}` — reuse
- `TASKS: dict` — only `mmlu` and `hellaswag` in H-M2; H-M3 adds `arc_challenge` and `winogrande`
- `FLOOR_THRESHOLD: float = 0.20` — H-M2 lowered from 0.30; PRD specifies 0.30 for H-M3 all-benchmark check; coder must verify 70m survives
- `H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"` — reuse

**`src/` module structure (verified):**
- `data_loader.py` — loads H-E1 exposure fractions; extend to 16 models
- `evaluator.py` — `evaluate_checkpoint(model_id, step, tasks, cache_dir, ...)` → extend tasks list
- `correlation_analysis.py` — Spearman ρ; H-M3 replaces with panel regression
- `statistical_test.py` — Fisher z-test; H-M3 reuses for P1/P2 one-tailed tests
- `visualization.py` — extend; add 4 new figures
- `reporter.py` — extend; add panel-specific save functions

**Key H-M2 API (verified from actual evaluator.py pattern):**
```python
# H-M2 evaluate_checkpoint signature (from code inspection):
evaluate_checkpoint(model_id: str, step: int, tasks: list[str],
                    cache_dir: Path, num_fewshot_map: dict[str, int],
                    device: str = "cuda", batch_size: str = "auto",
                    dtype: str = "float") -> dict[str, float]
```

**Critical finding:** `load_scores_array` in H-M2 hardcodes `mmlu_scores` and `hellaswag_scores` — must refactor to iterate over `config.TASKS.keys()` when extending to 4 benchmarks.

---

## External Dependencies API

**linearmodels.panel.PanelOLS (v4.0+):**
```python
from linearmodels.panel import PanelOLS

# Constructor (from_formula is preferred)
PanelOLS.from_formula(
    formula: str,      # e.g. "mmlu ~ domain_1 + ... + EntityEffects"
    data: pd.DataFrame # MultiIndex (entity, time)
) -> PanelOLS

# Fit
result = model.fit(
    cov_type: str = 'clustered',
    cluster_entity: bool = True   # cluster SEs by entity (model_size)
) -> PanelEffectsResults

# Key result attributes:
result.params          # pd.Series: β coefficients per domain
result.std_errors      # pd.Series: clustered SEs
result.pvalues         # pd.Series: two-tailed p-values
result.rsquared_within # float: within-entity R²
result.loglik          # float: log-likelihood (for LRT)
```

**statsmodels OLS (for shared-β model):**
```python
import statsmodels.api as sm

# Stacked OLS with benchmark + model-size dummies
sm.OLS(endog, exog).fit()  # returns OLSResults
result.llf               # float: log-likelihood
result.compare_lr_test(restricted_result)  # -> (lr_stat, p_value, df_diff)
```

**statsmodels VIF:**
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = variance_inflation_factor(X.values, i)  # float for column i
```

**statsmodels FDR:**
```python
from statsmodels.stats.multitest import multipletests
reject, pvals_corrected, _, _ = multipletests(pvals, method='fdr_bh')
```

---

## Module A-5: Panel Regression (4 subtasks)

### Subtask A-5-1: `fit_benchmark_specific_models`

```python
def fit_benchmark_specific_models(
    panel_df: pd.DataFrame,          # MultiIndex (model_size, checkpoint)
    domain_cols: list[str],          # 21 domain columns (1 dropped)
    benchmarks: list[str],           # ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    cov_type: str = 'clustered',
    cluster_entity: bool = True,
) -> dict[str, PanelEffectsResults]:
    """
    Fit 4 separate PanelOLS regressions, one per benchmark.
    Uses EntityEffects (entity demeaning) to remove model-size fixed effects.
    Clustered SEs by model_size handle within-model temporal autocorrelation.

    Args:
        panel_df: MultiIndex DataFrame (model_size, checkpoint) with domain and score columns
        domain_cols: list of 21 domain fraction columns (after dropping 1 to break sum constraint)
        benchmarks: list of benchmark column names
        cov_type: covariance type for SE estimation
        cluster_entity: if True, cluster SEs by entity (model_size); N=16 entities

    Returns:
        dict mapping benchmark_name -> PanelEffectsResults

    Raises:
        ValueError: if any benchmark column missing from panel_df
        ValueError: if clustered SEs are NaN for Wikipedia or Books3 (insufficient variation)

    Note:
        N=16 clusters is borderline for clustered inference (rule of thumb: ≥30).
        Document this limitation in results. Consider wild cluster bootstrap if p-values are marginal.
    """
    results = {}
    domain_terms = " + ".join(domain_cols)
    for benchmark in benchmarks:
        if benchmark not in panel_df.columns:
            raise ValueError(f"Benchmark '{benchmark}' not in panel_df columns")
        formula = f"{benchmark} ~ {domain_terms} + EntityEffects"
        mod = PanelOLS.from_formula(formula, panel_df)
        res = mod.fit(cov_type=cov_type, cluster_entity=cluster_entity)
        # Sanity check: at least one domain has |β| > 1 SE
        if not (res.params.abs() > res.std_errors).any():
            import warnings
            warnings.warn(f"No domain coefficient exceeds its SE for {benchmark} — domain exposure may have no predictive power")
        # Critical check: Wikipedia and Books3 SEs must be finite
        for focal in ["Wikipedia (en)", "Books3"]:
            focal_mapped = [c for c in domain_cols if focal in c]
            if focal_mapped and np.isnan(res.std_errors[focal_mapped[0]]):
                raise ValueError(f"Clustered SE is NaN for {focal} in {benchmark} — check Books3 within-variation")
        results[benchmark] = res
        logging.info(f"PanelOLS fit complete for benchmark {benchmark}: "
                     f"N={res.entity_info.total}, T={res.time_info.total}, "
                     f"R²_within={res.rsquared_within:.4f}")
    return results
```

**Tensor shapes:**
- Input `panel_df`: (2464, 21+4+1) — 2464 obs, 21 domains, 4 benchmarks, 1 log_params
- `res.params`: (21,) per benchmark — one β per domain column
- `res.std_errors`: (21,) per benchmark

### Subtask A-5-2: `fit_shared_beta_model`

```python
def fit_shared_beta_model(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Fit shared-β null model: pool all 4 benchmarks with common domain coefficients.
    Uses statsmodels OLS with explicit benchmark dummies + model-size dummies
    (linearmodels cannot natively stack multi-outcome panels — see FR-6.3).

    Stack structure: 4 × 2464 = 9856 rows
    Columns: domain_cols (shared β) + 3 benchmark dummies + 15 model-size dummies

    Returns:
        OLSResults with .llf attribute for LRT computation

    Note:
        log-likelihood from stacked OLS is NOT directly comparable to per-benchmark
        PanelOLS (different estimators). LRT uses sum of per-benchmark OLS ll values
        as unrestricted alternative, vs stacked OLS ll as restricted null.
        Both are estimated with model-size dummies (equivalent to entity demeaning) for
        comparability.
    """
    frames = []
    for i, bench in enumerate(benchmarks):
        sub = panel_df[domain_cols + [bench, 'log_params']].copy()
        sub = sub.rename(columns={bench: 'score'})
        sub['benchmark'] = bench
        # Add model_size dummy from MultiIndex level 0
        sub['model_size'] = sub.index.get_level_values('model_size')
        frames.append(sub)
    stacked = pd.concat(frames, ignore_index=True)

    # Dummies: benchmark (3 dummies, drop first) + model_size (15 dummies, drop first)
    bench_dummies = pd.get_dummies(stacked['benchmark'], drop_first=True, prefix='bench')
    size_dummies = pd.get_dummies(stacked['model_size'], drop_first=True, prefix='size')
    X = pd.concat([stacked[domain_cols], bench_dummies, size_dummies], axis=1)
    X = sm.add_constant(X)
    y = stacked['score']
    return sm.OLS(y, X).fit()
```

### Subtask A-5-3: `extract_focal_coefficients`

```python
def extract_focal_coefficients(
    results: dict[str, PanelEffectsResults],
    domain_cols: list[str],
    focal_domains: dict[str, str],   # {"wikipedia": "Wikipedia (en)", "books": "Books3"}
    pca_loadings: np.ndarray | None = None,  # (n_components, n_original_domains) if PCA applied
    original_domain_names: list[str] | None = None,
) -> dict[str, dict[str, dict]]:
    """
    Extract β and SE for Wikipedia and Books3 from each benchmark model.

    If PCA was applied (pca_loadings is not None):
        - Map focal domain to its dominant PC component (highest |loading|)
        - Use that PC's β and SE as proxy
        - Set pca_approximation=True flag in output

    Returns:
        {
          "mmlu": {
            "Wikipedia (en)": {"beta": float, "se": float, "pca_approx": bool},
            "Books3": {"beta": float, "se": float, "pca_approx": bool},
          },
          "hellaswag": {...}, ...
        }
    """
    output = {}
    for bench, res in results.items():
        output[bench] = {}
        for key, domain_name in focal_domains.items():
            if domain_name in domain_cols:
                # Direct: domain present as column
                output[bench][domain_name] = {
                    "beta": float(res.params[domain_name]),
                    "se": float(res.std_errors[domain_name]),
                    "pca_approx": False,
                }
            elif pca_loadings is not None and original_domain_names is not None:
                # PCA fallback: find dominant PC for this domain
                domain_idx = original_domain_names.index(domain_name)
                pc_idx = int(np.argmax(np.abs(pca_loadings[:, domain_idx])))
                pc_col = f"PC{pc_idx}"
                output[bench][domain_name] = {
                    "beta": float(res.params[pc_col]),
                    "se": float(res.std_errors[pc_col]),
                    "pca_approx": True,
                    "dominant_pc": pc_col,
                    "loading": float(pca_loadings[pc_idx, domain_idx]),
                }
            else:
                output[bench][domain_name] = {"beta": np.nan, "se": np.nan, "pca_approx": False}
    return output
```

### Subtask A-5-4: `save_panel_results`

```python
def save_panel_results(
    results: dict[str, PanelEffectsResults],
    shared_result: sm.regression.linear_model.RegressionResultsWrapper,
    focal_coeffs: dict,
    output_dir: Path,
) -> None:
    """
    Serialize panel regression results to JSON.
    PanelEffectsResults is not directly JSON-serializable; extract key fields.
    """
    for bench, res in results.items():
        payload = {
            "benchmark": bench,
            "n_obs": int(res.nobs),
            "rsquared_within": float(res.rsquared_within),
            "rsquared_between": float(res.rsquared_between),
            "loglik": float(res.loglik) if hasattr(res, 'loglik') else None,
            "params": res.params.to_dict(),
            "std_errors": res.std_errors.to_dict(),
            "pvalues": res.pvalues.to_dict(),
        }
        (output_dir / f"panel_results_{bench}.json").write_text(json.dumps(payload, indent=2))

    # Shared-β model
    shared_payload = {
        "loglik": float(shared_result.llf),
        "nobs": int(shared_result.nobs),
        "df_resid": float(shared_result.df_resid),
    }
    (output_dir / "panel_results_shared_beta.json").write_text(json.dumps(shared_payload, indent=2))

    # Focal coefficients
    (output_dir / "focal_coefficients.json").write_text(json.dumps(focal_coeffs, indent=2))
```

---

## Module A-6: Hypothesis Tests (4 subtasks)

### Subtask A-6-1: `test_p1_p2`

```python
def test_p1_p2(
    focal_coeffs: dict[str, dict[str, dict]],
    alpha: float = 0.05,
) -> dict:
    """
    Test P1: β_Wikipedia > β_Books3 for MMLU (one-tailed)
    Test P2: β_Books3 > β_Wikipedia for HellaSwag (one-tailed)

    Uses Wald-type z-test: z = (β1 - β2) / sqrt(SE1² + SE2²)
    One-tailed p: p = 1 - norm.cdf(z)  [for H1: β1 > β2]

    Note: SEs are clustered; assuming approximate normality for clustered estimator
    with N=16 clusters (borderline — document limitation).

    Returns:
        {
          "P1": {"direction": bool, "z": float, "p_one_tailed": float, "passed": bool,
                 "beta_wiki_mmlu": float, "beta_books_mmlu": float},
          "P2": {"direction": bool, "z": float, "p_one_tailed": float, "passed": bool,
                 "beta_books_hs": float, "beta_wiki_hs": float},
        }
    """
    from scipy.stats import norm

    def wald_z_one_tailed(beta1, se1, beta2, se2):
        z = (beta1 - beta2) / np.sqrt(se1**2 + se2**2)
        p = 1.0 - norm.cdf(z)
        return float(z), float(p)

    wiki = "Wikipedia (en)"
    books = "Books3"

    # P1: MMLU — H1: β_wiki > β_books
    mmlu = focal_coeffs.get("mmlu", {})
    beta_wiki_mmlu = mmlu.get(wiki, {}).get("beta", np.nan)
    se_wiki_mmlu   = mmlu.get(wiki, {}).get("se", np.nan)
    beta_books_mmlu = mmlu.get(books, {}).get("beta", np.nan)
    se_books_mmlu   = mmlu.get(books, {}).get("se", np.nan)
    z1, p1 = wald_z_one_tailed(beta_wiki_mmlu, se_wiki_mmlu, beta_books_mmlu, se_books_mmlu)

    # P2: HellaSwag — H1: β_books > β_wiki
    hs = focal_coeffs.get("hellaswag", {})
    beta_books_hs = hs.get(books, {}).get("beta", np.nan)
    se_books_hs   = hs.get(books, {}).get("se", np.nan)
    beta_wiki_hs  = hs.get(wiki, {}).get("beta", np.nan)
    se_wiki_hs    = hs.get(wiki, {}).get("se", np.nan)
    z2, p2 = wald_z_one_tailed(beta_books_hs, se_books_hs, beta_wiki_hs, se_wiki_hs)

    return {
        "P1": {
            "direction": bool(beta_wiki_mmlu > beta_books_mmlu),
            "z": z1, "p_one_tailed": p1,
            "passed": bool(beta_wiki_mmlu > beta_books_mmlu and p1 < alpha),
            "beta_wiki_mmlu": float(beta_wiki_mmlu),
            "beta_books_mmlu": float(beta_books_mmlu),
        },
        "P2": {
            "direction": bool(beta_books_hs > beta_wiki_hs),
            "z": z2, "p_one_tailed": p2,
            "passed": bool(beta_books_hs > beta_wiki_hs and p2 < alpha),
            "beta_books_hs": float(beta_books_hs),
            "beta_wiki_hs": float(beta_wiki_hs),
        },
    }
```

### Subtask A-6-2: `run_lrt_all_pairs`

```python
def run_lrt_all_pairs(
    benchmark_results: dict[str, PanelEffectsResults],
    shared_beta_result: sm.regression.linear_model.RegressionResultsWrapper,
    benchmarks: list[str],
    n_domain_cols: int,   # df for LRT = n_domain_cols (extra params in alt model per pair)
) -> pd.DataFrame:
    """
    Run LRT for all 6 pairwise benchmark comparisons.

    LRT statistic per pair (b1, b2):
        lr_stat = 2 * (LL_b1 + LL_b2 - LL_shared_pair)

    Where LL_shared_pair is the log-likelihood of a shared-β OLS fitted on the
    2-benchmark stack (b1+b2) with model-size dummies.
    The degrees of freedom = n_domain_cols (the additional domain parameters freed).

    Returns:
        pd.DataFrame with columns: [pair, lr_stat, df, p_value]
        indexed by pair name e.g. "mmlu_vs_hellaswag"
    """
    from itertools import combinations
    from scipy.stats import chi2

    rows = []
    for b1, b2 in combinations(benchmarks, 2):
        ll_b1 = float(benchmark_results[b1].loglik) if hasattr(benchmark_results[b1], 'loglik') else _estimate_loglik(benchmark_results[b1])
        ll_b2 = float(benchmark_results[b2].loglik) if hasattr(benchmark_results[b2], 'loglik') else _estimate_loglik(benchmark_results[b2])
        # Fit pair-specific shared-β model for accurate LL_null
        ll_shared = _fit_pair_shared_ll(benchmark_results, b1, b2, n_domain_cols)
        lr_stat = 2.0 * (ll_b1 + ll_b2 - ll_shared)
        df = n_domain_cols
        p_value = float(chi2.sf(lr_stat, df))
        rows.append({"pair": f"{b1}_vs_{b2}", "b1": b1, "b2": b2,
                     "lr_stat": lr_stat, "df": df, "p_value": p_value})
    return pd.DataFrame(rows).set_index("pair")
```

### Subtask A-6-3: `apply_fdr_correction`

```python
def apply_fdr_correction(
    lrt_df: pd.DataFrame,
    alpha: float = 0.05,
) -> dict:
    """
    Apply Benjamini-Hochberg FDR correction to 6 LRT p-values.

    Returns:
        {
          "reject": list[bool],       # per-pair rejection at FDR level
          "pvals_corrected": list[float],
          "n_significant": int,       # count of rejected pairs
          "p3_passed": bool,          # True if n_significant >= 2
          "pairs": list[str],
        }
    """
    pvals = lrt_df["p_value"].values
    reject, pvals_corrected, _, _ = multipletests(pvals, alpha=alpha, method='fdr_bh')
    return {
        "reject": reject.tolist(),
        "pvals_corrected": pvals_corrected.tolist(),
        "n_significant": int(reject.sum()),
        "p3_passed": bool(reject.sum() >= 2),
        "pairs": lrt_df.index.tolist(),
    }
```

### Subtask A-6-4: `evaluate_gate`

```python
def evaluate_gate(
    p1_result: dict,
    p2_result: dict,
    fdr_result: dict,
    p4_result: dict | None = None,
) -> dict:
    """
    Evaluate overall gate status for H-M3 (SHOULD_WORK).

    Gate routing:
        PRIMARY_PASS: P1 AND P2 → PASS
        SECONDARY_PASS: P3 (LRT) → PASS (with note)
        MINIMUM_PASS: P1 OR P2 → EXPLORE
        ALL_FAIL: → PIVOT

    Returns full gate dict with route recommendation.
    """
    p1 = p1_result["passed"]
    p2 = p2_result["passed"]
    p3 = fdr_result["p3_passed"]
    p4 = p4_result.get("passed", False) if p4_result else None

    if p1 and p2:
        route = "PASS"
        status = "PRIMARY_PASS"
    elif p3:
        route = "PASS"
        status = "SECONDARY_PASS"
    elif p1 or p2:
        route = "EXPLORE"
        status = "MINIMUM_PASS"
    else:
        route = "PIVOT"
        status = "ALL_FAIL"

    return {
        "gate_type": "SHOULD_WORK",
        "status": status,
        "route": route,
        "P1_passed": p1,
        "P2_passed": p2,
        "P3_passed": p3,
        "P4_passed": p4,
        "n_lrt_significant": fdr_result["n_significant"],
    }
```

---

## Module A-7: Robustness Analysis (4 subtasks)

### Subtask A-7-1: `run_subgroup_regressions`

```python
def run_subgroup_regressions(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
    size_groups: dict[str, list[str]] | None = None,
) -> dict[str, dict[str, PanelEffectsResults]]:
    """
    Fit PanelOLS separately for small and large model subgroups.

    Default size_groups:
        small: ["70m", "160m", "410m"]
        large: ["1b", "1.4b", "2.8b", "6.9b", "12b"]
        (deduped variants assigned to same category as base)

    Returns:
        {"small": {benchmark: result, ...}, "large": {benchmark: result, ...}}

    Note: Small group N=3 entities — clustered SEs with N<10 are unreliable.
    Use heteroskedasticity-robust SEs for subgroups (cov_type='robust').
    """
    if size_groups is None:
        size_groups = {
            "small": ["70m", "160m", "410m", "70m-deduped", "160m-deduped", "410m-deduped"],
            "large": ["1b", "1.4b", "2.8b", "6.9b", "12b",
                      "1b-deduped", "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped"],
        }
    results = {}
    for group_name, sizes in size_groups.items():
        mask = panel_df.index.get_level_values('model_size').isin(sizes)
        sub_df = panel_df[mask]
        # Use robust (not clustered) for small N
        cov = 'robust' if len(sizes) < 10 else 'clustered'
        cluster_e = cov == 'clustered'
        results[group_name] = {}
        for bench in benchmarks:
            formula = f"{bench} ~ {' + '.join(domain_cols)} + EntityEffects"
            mod = PanelOLS.from_formula(formula, sub_df)
            results[group_name][bench] = mod.fit(cov_type=cov, cluster_entity=cluster_e)
    return results
```

### Subtask A-7-2: `test_p4_spearman`

```python
def test_p4_spearman(
    subgroup_results: dict[str, dict[str, PanelEffectsResults]],
    domain_cols: list[str],
    benchmarks: list[str],
    rho_threshold: float = 0.7,
) -> dict:
    """
    Test P4: Spearman ρ of domain coefficient rankings is consistent across model scales.

    For each benchmark: rank domain coefficients in small and large subgroups.
    Compute Spearman ρ between the two rank vectors.
    P4 passes if median ρ across benchmarks > rho_threshold.

    Returns:
        {"rho_per_benchmark": dict, "median_rho": float, "passed": bool}
    """
    from scipy.stats import spearmanr
    rho_per_bench = {}
    for bench in benchmarks:
        small_params = subgroup_results["small"][bench].params[domain_cols]
        large_params = subgroup_results["large"][bench].params[domain_cols]
        rho, pval = spearmanr(small_params.values, large_params.values)
        rho_per_bench[bench] = {"rho": float(rho), "pval": float(pval)}
    median_rho = float(np.median([v["rho"] for v in rho_per_bench.values()]))
    return {
        "rho_per_benchmark": rho_per_bench,
        "median_rho": median_rho,
        "threshold": rho_threshold,
        "passed": bool(median_rho > rho_threshold),
    }
```

### Subtask A-7-3: `run_permutation_null`

```python
def run_permutation_null(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    focal_domains: dict[str, str],   # {"wikipedia": "Wikipedia (en)", "books": "Books3"}
    benchmarks_focal: dict[str, str] = None,  # {"P1": "mmlu", "P2": "hellaswag"}
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Build permutation null distribution for |β_wiki - β_books| under H0.

    Permutation: shuffle domain column labels in panel_df (not rows).
    This destroys domain identity while preserving panel structure and variance.
    Refit minimal model (only focal domain columns) per permutation for speed.

    Returns:
        {
          "P1": {"null_dist": list[float], "observed": float, "empirical_p": float},
          "P2": {"null_dist": list[float], "observed": float, "empirical_p": float},
        }

    Note: numpy vectorized approach — pre-permute all column indices at once.
    """
    if benchmarks_focal is None:
        benchmarks_focal = {"P1": "mmlu", "P2": "hellaswag"}

    rng = np.random.default_rng(seed)
    wiki_name = focal_domains["wikipedia"]
    books_name = focal_domains["books"]

    # Get focal domain indices in domain_cols
    wiki_idx = domain_cols.index(wiki_name) if wiki_name in domain_cols else None
    books_idx = domain_cols.index(books_name) if books_name in domain_cols else None
    if wiki_idx is None or books_idx is None:
        return {"error": "Focal domains not in domain_cols (PCA may have been applied)"}

    null_dists = {test: [] for test in benchmarks_focal}
    # Pre-generate all permutation indices
    all_perms = [rng.permutation(len(domain_cols)) for _ in range(n_permutations)]

    for perm_idx in all_perms:
        permuted_cols = [domain_cols[i] for i in perm_idx]
        perm_df = panel_df.copy()
        perm_df.columns = [permuted_cols[domain_cols.index(c)] if c in domain_cols else c
                           for c in perm_df.columns]
        for test, bench in benchmarks_focal.items():
            # Minimal fit: only 2 focal domains
            formula = f"{bench} ~ {wiki_name} + {books_name} + EntityEffects"
            try:
                res = PanelOLS.from_formula(formula, perm_df).fit(
                    cov_type='clustered', cluster_entity=True)
                diff = abs(float(res.params[wiki_name]) - float(res.params[books_name]))
                null_dists[test].append(diff)
            except Exception:
                null_dists[test].append(np.nan)

    # Compute observed statistics from real fit
    output = {}
    for test, bench in benchmarks_focal.items():
        formula = f"{bench} ~ {wiki_name} + {books_name} + EntityEffects"
        res_obs = PanelOLS.from_formula(formula, panel_df).fit(
            cov_type='clustered', cluster_entity=True)
        obs = abs(float(res_obs.params[wiki_name]) - float(res_obs.params[books_name]))
        null = np.array([v for v in null_dists[test] if not np.isnan(v)])
        empirical_p = float(np.mean(null >= obs))
        output[test] = {
            "null_dist": null.tolist(),
            "observed": obs,
            "empirical_p": empirical_p,
        }
    return output
```

### Subtask A-7-4: `run_r2_decomposition`

```python
def run_r2_decomposition(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    benchmarks: list[str],
) -> dict:
    """
    R² decomposition: fit 3 models per benchmark and compare within-R².
        1. domain-only model: score ~ domain_cols + EntityEffects
        2. scale-only model: score ~ log_params + EntityEffects
        3. full model: score ~ domain_cols + log_params + EntityEffects

    Note: log_params is time-invariant (constant per entity) — with EntityEffects
    (entity demeaning), time-invariant variables are absorbed. Must use between
    estimator or drop EntityEffects for scale-only model.

    Returns:
        {benchmark: {"domain_only": float, "scale_only": float, "full": float}}
    """
    from linearmodels.panel import BetweenOLS, PooledOLS

    output = {}
    domain_formula = " + ".join(domain_cols) + " + EntityEffects"
    for bench in benchmarks:
        # Domain-only (entity demeaned)
        r2_domain = PanelOLS.from_formula(
            f"{bench} ~ {domain_formula}", panel_df
        ).fit(cov_type='clustered', cluster_entity=True).rsquared_within

        # Scale-only: use pooled OLS (entity effects would absorb log_params)
        r2_scale = PooledOLS.from_formula(
            f"{bench} ~ log_params", panel_df
        ).fit(cov_type='clustered', cluster_entity=True).rsquared

        # Full model (entity effects + domain only; log_params absorbed by entity dummies)
        r2_full = r2_domain  # entity effects subsume log_params variation; note this limitation

        output[bench] = {
            "domain_only_within": float(r2_domain),
            "scale_only_pooled": float(r2_scale),
            "full_within": float(r2_full),
            "note": "log_params is time-invariant; absorbed by EntityEffects in within-R². scale_only uses PooledOLS.",
        }
    return output
```

---

## Panel Quality Verification

```python
def verify_panel_quality(
    panel_df: pd.DataFrame,
    domain_cols: list[str],
    books3_col: str = "Books3",
    threshold: float = 1e-6,
) -> dict:
    """
    Verify domain columns have sufficient within-entity variation for entity-demeaned estimation.
    Critical check: Books3 must NOT be zero-variance (H-M2 root cause).
    """
    stats = {}
    for domain in domain_cols:
        grouped = panel_df[domain].groupby(level='model_size')
        within_var = grouped.transform(lambda x: x - x.mean()).var()
        stats[domain] = float(within_var.mean())

    low_var = [d for d, v in stats.items() if v < threshold]
    if low_var:
        logging.warning(f"Low within-variation domains: {low_var}")

    books3_var = stats.get(books3_col, 0.0)
    if books3_var < threshold:
        raise ValueError(
            f"Books3 within-variation {books3_var:.2e} < {threshold} — "
            "check H-E1 full output loading (H-M2 root cause: 600k-doc subsample)"
        )
    logging.info(f"Panel quality check passed. Books3 within-var: {books3_var:.4e}")
    return stats
```
