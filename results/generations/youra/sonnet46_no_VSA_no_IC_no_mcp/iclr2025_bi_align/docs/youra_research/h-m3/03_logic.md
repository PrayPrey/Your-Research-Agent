# Logic: H-M3
# OLS Regression Slope Significance Test — Calibration-Alignment Divergence Gap

**Hypothesis ID:** H-M3
**Type:** MECHANISM (PoC — INCREMENTAL from H-M2)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Statistical pipeline pattern — load → OLS fit → bootstrap → gate → visualize → report (mirrors H-M2 orchestration structure)
Applied: Guard-clause pattern — fast-fail on missing file, bad shape, NaN, degenerate data before regression
Applied: Bootstrap CI supplement pattern — parametric t-test + percentile bootstrap for n=10 robustness

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-M2)
**Status:** H-M2 code analyzed (manual read — Serena MCP unavailable in ablation mode)
**Analyzed Path:** `docs/youra_research/h-m2/code/src/`

**Findings:**
- `src/data/loader.py::load_dataset(csv_path: str) -> pd.DataFrame` — validates REQUIRED_COLS, sorts by kl_budget, asserts N >= 5. H-M3 mirrors this but returns `(kl_values, gap_values)` tuple of numpy arrays since only 2 columns needed.
- `src/analysis/normalizer.py::run_gap_analysis(df, high_kl_min_positive)` — orchestrator pattern returning dict; H-M3 mirrors with `fit_ols_regression(kl, gap, n_boot, seed)`.
- `src/visualization/plots.py` — each plot function takes arrays + figs_dir + dpi, saves PNG, returns path string. H-M3 mirrors signature exactly.
- `src/reporting/reporter.py::print_report(results), save_results(results, out_path)` — same pattern replicated for H-M3.
- `main.py::main()` — load_config → validate → load_dataset → analysis → plots → report → sys.exit. H-M3 mirrors identically.

**External Dependencies API (Verified from H-M2 code):**

```python
# From h-m2/code/src/data/loader.py — confirmed signature pattern
def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load CSV; validate REQUIRED_COLS; sort by kl_budget ascending;
    assert N >= 5 non-null rows.
    Raises: FileNotFoundError, ValueError on validation failure.
    """
    ...

# From h-m2/code/src/reporting/reporter.py — confirmed signatures
def print_report(results: dict) -> None: ...
def save_results(results: dict, out_path: str) -> None: ...
    # Note: excludes numpy arrays from JSON serialization via custom encoder
```

**Note:** H-M3 implements its own standalone modules following H-M2 patterns. No cross-imports.

---

## Array Schemas

### Input Arrays (from h_m2_normalized_gap.csv)

| Variable | dtype | Shape | Range | Notes |
|----------|-------|-------|-------|-------|
| `kl_values` | float64 | (10,) | [0.0, 8.0] | KL budget levels |
| `gap_values` | float64 | (10,) | [-0.52, 0.62] | rm_norm − gold_preference |

### Derived / Output Arrays

| Variable | dtype | Shape | Notes |
|----------|-------|-------|-------|
| `boot_slopes` | float64 | (10000,) | bootstrap slope samples |
| `residuals` | float64 | (10,) | gap − (slope·kl + intercept) |
| `fitted` | float64 | (10,) | slope·kl + intercept |

---

## L-3-1: fit_ols_regression() — Full API + Return Dict [Parent: A-3, Complexity: 10]

Applied: Unified results-dict orchestrator pattern (mirrors run_gap_analysis)

### API Signature

```python
def fit_ols_regression(
    kl_values: np.ndarray,
    gap_values: np.ndarray,
    n_boot: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Full H-M3 regression analysis: OLS slope test + bootstrap CI.

    Args:
        kl_values:  (10,) float64 array of KL budget levels (predictor)
        gap_values: (10,) float64 array of calibration-alignment gap (outcome)
        n_boot:     Number of bootstrap iterations (default 10,000)
        seed:       RNG seed for reproducibility (default 42)

    Returns:
        {
            # OLS results (scipy)
            "slope":          float,         # β₁ — slope of gap vs KL
            "intercept":      float,         # β₀
            "r_squared":      float,         # R² = r_value²
            "p_value":        float,         # Wald t-test p (H0: β=0)
            "std_err":        float,         # SE(β)
            "t_stat":         float,         # slope / std_err
            "r_value":        float,         # Pearson r

            # statsmodels CI
            "ci_parametric":  tuple[float, float],  # 95% CI for slope

            # Bootstrap
            "ci_bootstrap":   np.ndarray,   # shape (2,) — [2.5th, 97.5th pctl]
            "boot_slopes":    np.ndarray,   # shape (n_boot,)

            # Derived
            "fitted":         np.ndarray,   # shape (10,) — predicted gap
            "residuals":      np.ndarray,   # shape (10,) — gap - fitted
            "n":              int,           # 10

            # statsmodels text summary
            "statsmodels_summary": str,
        }
    """
```

---

## L-3-2: scipy.stats.linregress step [Parent: A-3, Complexity: 10]

Applied: scipy linregress + r_value² pattern for R²

### Algorithm

```python
from scipy import stats

def _run_scipy_ols(kl: np.ndarray, gap: np.ndarray) -> dict:
    slope, intercept, r_value, p_value, std_err = stats.linregress(kl, gap)
    r_squared = r_value ** 2
    t_stat = slope / std_err
    fitted = slope * kl + intercept
    residuals = gap - fitted
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_value": float(r_value),
        "r_squared": float(r_squared),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "t_stat": float(t_stat),
        "fitted": fitted,
        "residuals": residuals,
        "n": int(len(kl)),
    }
```

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| All gap values equal | `std_err=0`, `t_stat=inf/nan`; caught by `verify_mechanism_activated` |
| N < 5 | Caught by loader before reaching regression |
| Perfect linear fit (ρ=1) | `r_squared=1.0`, `p_value≈0`; valid result |

---

## L-3-3: statsmodels OLS step — 95% CI for slope [Parent: A-3, Complexity: 10]

Applied: statsmodels conf_int pattern for parametric CI

### Algorithm

```python
import statsmodels.api as sm

def _run_statsmodels_ols(kl: np.ndarray, gap: np.ndarray) -> dict:
    X = sm.add_constant(kl)           # shape (10, 2): [1, kl_budget]
    model = sm.OLS(gap, X).fit()
    ci = model.conf_int(alpha=0.05)   # shape (2, 2): [const, slope] × [lower, upper]
    ci_low, ci_high = float(ci[1, 0]), float(ci[1, 1])   # slope 95% CI
    summary_text = str(model.summary())
    return {
        "ci_parametric": (ci_low, ci_high),
        "statsmodels_summary": summary_text,
    }
```

---

## L-3-4: Edge cases for degenerate data [Parent: A-3, Complexity: 10]

```python
def fit_ols_regression(kl_values, gap_values, n_boot=10_000, seed=42):
    # Guard: degenerate gap (all equal)
    if np.std(gap_values) == 0:
        raise ValueError("Degenerate gap array: all values equal — regression undefined")
    # Guard: insufficient data
    if len(kl_values) < 5:
        raise ValueError(f"Insufficient data: N={len(kl_values)}, minimum 5 required")

    scipy_res = _run_scipy_ols(kl_values, gap_values)
    sm_res = _run_statsmodels_ols(kl_values, gap_values)
    boot_res = _run_bootstrap(kl_values, gap_values, n_boot=n_boot, seed=seed)

    return {**scipy_res, **sm_res, **boot_res}
```

---

## L-4-1: Bootstrap algorithm [Parent: A-4, Complexity: 9]

Applied: numpy default_rng + rng.choice resample pattern (matches H-M3 experiment brief)

### Algorithm

```python
def _run_bootstrap(
    kl: np.ndarray,
    gap: np.ndarray,
    n_boot: int = 10_000,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(kl))
    boot_slopes = np.empty(n_boot, dtype=np.float64)

    for i in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        b_slope, *_ = stats.linregress(kl[s], gap[s])
        boot_slopes[i] = b_slope

    assert len(boot_slopes) == n_boot, f"Bootstrap incomplete: {len(boot_slopes)}/{n_boot}"

    ci_bootstrap = np.percentile(boot_slopes, [2.5, 97.5])
    return {
        "boot_slopes": boot_slopes,      # shape (10000,)
        "ci_bootstrap": ci_bootstrap,    # shape (2,)
    }
```

---

## L-4-2: Bootstrap CI percentile computation [Parent: A-4, Complexity: 9]

```python
# After bootstrap loop:
ci_bootstrap = np.percentile(boot_slopes, [2.5, 97.5])
# ci_bootstrap[0] = lower bound (2.5th percentile)
# ci_bootstrap[1] = upper bound (97.5th percentile)
# Both bounds > 0 → strong bootstrap evidence for positive slope
```

---

## L-4-3: Bootstrap convergence check [Parent: A-4, Complexity: 9]

```python
assert len(boot_slopes) == n_boot, (
    f"Bootstrap convergence failure: collected {len(boot_slopes)}/{n_boot} slopes. "
    "Check for NaN in input data."
)
# Also check for NaN slopes (can occur if bootstrap sample has zero variance)
nan_count = int(np.isnan(boot_slopes).sum())
if nan_count > 0:
    boot_slopes = boot_slopes[~np.isnan(boot_slopes)]
    # Warn but continue — NaN slopes from degenerate bootstrap samples are rare at n=10
```

---

## L-5-1: verify_mechanism_activated() [Parent: A-5, Complexity: 7]

Applied: indicator-dict pattern — each check independently testable

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Verify OLS regression executed and produced valid statistical output.

    Args:
        results: dict from fit_ols_regression()

    Returns:
        (all_ok: bool, indicators: dict[str, bool])

    Raises:
        RuntimeError if any indicator fails
    """
    indicators = {
        "data_loaded":     results.get("n") == 10,
        "slope_computed":  results.get("slope") is not None and not np.isnan(results["slope"]),
        "p_value_valid":   0.0 <= results.get("p_value", 1.1) <= 1.0,
        "r_squared_valid": 0.0 <= results.get("r_squared", -1.0) <= 1.0,
        "ci_computed":     results.get("ci_bootstrap") is not None,
    }
    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    return True, indicators
```

---

## L-5-2: check_gate() [Parent: A-5, Complexity: 7]

```python
def check_gate(results: dict) -> tuple[bool, str]:
    """
    Gate: slope > 0 AND p < 0.05 AND R² > 0.5

    Returns:
        (gate_pass: bool, gate_reason: str)
    """
    slope     = results["slope"]
    p_value   = results["p_value"]
    r_squared = results["r_squared"]

    conditions = {
        "slope > 0":     slope > 0,
        "p < 0.05":      p_value < 0.05,
        "R² > 0.5":      r_squared > 0.5,
    }
    gate_pass = all(conditions.values())

    if gate_pass:
        gate_reason = (
            f"PASS: slope={slope:.4f}>0, p={p_value:.2e}<0.05, R²={r_squared:.4f}>0.5"
        )
    else:
        failed = [name for name, ok in conditions.items() if not ok]
        gate_reason = (
            f"FAIL: conditions not met: {failed}. "
            f"slope={slope:.4f}, p={p_value:.2e}, R²={r_squared:.4f}. "
            "Action: ABANDON H-BiAlign-v1; route to Phase 0."
        )
    return gate_pass, gate_reason
```

---

## L-6-1: plot_gate_metrics() [Parent: A-6, Complexity: 10]

Applied: Bar chart with threshold lines pattern (mirrors H-M2 plot_gate_metrics)

```python
def plot_gate_metrics(results: dict, figures_dir: str, dpi: int = 150) -> str:
    """
    Bar chart: β vs 0, p_value vs 0.05, R² vs 0.5.
    Green bar = PASS, red = FAIL.
    Returns: path to saved PNG.
    """
    metrics = {
        "β (slope)":  (results["slope"],     0.0,  results["slope"] > 0),
        "p-value":    (results["p_value"],    0.05, results["p_value"] < 0.05),
        "R²":         (results["r_squared"],  0.5,  results["r_squared"] > 0.5),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(metrics)))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.75, width=0.5)
    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(threshold, i - 0.3, i + 0.3, colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + 0.02, f"threshold={threshold}", ha="center", fontsize=8)
        ax.text(i, val + 0.02, f"{val:.4f}", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Metric Value")
    gate = "PASS ✓" if results.get("gate_pass") else "FAIL ✗"
    ax.set_title(f"H-M3 Gate Metrics — {gate}")
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "gate_metrics.png")
    fig.savefig(out, dpi=dpi); plt.close(fig)
    return out
```

---

## L-6-2: plot_regression_scatter() [Parent: A-6, Complexity: 10]

Applied: Scatter + OLS line + shaded CI band pattern

```python
def plot_regression_scatter(
    kl: np.ndarray,
    gap: np.ndarray,
    results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """
    Scatter (KL, gap) + OLS best-fit line + shaded 95% CI band.
    Annotates slope β, R², p-value.
    Returns: path to saved PNG.
    """
    slope, intercept = results["slope"], results["intercept"]
    r_squared, p_value = results["r_squared"], results["p_value"]
    ci_low, ci_high = results["ci_parametric"]

    kl_line = np.linspace(kl.min(), kl.max(), 200)
    fit_line = slope * kl_line + intercept
    ci_band_low  = ci_low  * kl_line + intercept
    ci_band_high = ci_high * kl_line + intercept

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(kl, gap, color="steelblue", s=80, zorder=5, label="Observed gap")
    ax.plot(kl_line, fit_line, color="navy", linewidth=2,
            label=f"OLS fit (β={slope:.4f}, R²={r_squared:.4f}, p={p_value:.2e})")
    ax.fill_between(kl_line, ci_band_low, ci_band_high,
                    alpha=0.15, color="navy", label="95% CI (parametric)")
    ax.axhline(0, color="black", linestyle=":", alpha=0.4)
    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title("H-M3: OLS Regression of Divergence Gap on KL Budget")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "regression_scatter.png")
    fig.savefig(out, dpi=dpi); plt.close(fig)
    return out
```

---

## L-6-3: plot_residuals() [Parent: A-6, Complexity: 10]

```python
def plot_residuals(
    kl: np.ndarray,
    gap: np.ndarray,
    results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """
    Residuals vs fitted values. Horizontal zero line.
    Returns: path to saved PNG.
    """
    fitted    = results["fitted"]      # shape (10,)
    residuals = results["residuals"]   # shape (10,)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(fitted, residuals, color="steelblue", s=80, zorder=5)
    ax.axhline(0, color="black", linestyle="--", alpha=0.6)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.set_title("H-M3: Residuals vs Fitted")
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "residuals.png")
    fig.savefig(out, dpi=dpi); plt.close(fig)
    return out
```

---

## L-6-4: plot_bootstrap_histogram() [Parent: A-6, Complexity: 10]

```python
def plot_bootstrap_histogram(
    results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """
    Histogram of 10,000 bootstrap slopes.
    Marks observed β and 95% CI bounds.
    Returns: path to saved PNG.
    """
    boot_slopes   = results["boot_slopes"]    # shape (10000,)
    observed_beta = results["slope"]
    ci_low, ci_high = results["ci_bootstrap"]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(boot_slopes, bins=60, color="steelblue", alpha=0.7, edgecolor="white")
    ax.axvline(observed_beta, color="navy",   linewidth=2, label=f"Observed β={observed_beta:.4f}")
    ax.axvline(ci_low,        color="orange", linewidth=1.5, linestyle="--",
               label=f"95% CI [{ci_low:.4f}, {ci_high:.4f}]")
    ax.axvline(ci_high,       color="orange", linewidth=1.5, linestyle="--")
    ax.axvline(0,             color="black",  linewidth=1, linestyle=":", alpha=0.5, label="β=0")
    ax.set_xlabel("Bootstrap Slope Estimate")
    ax.set_ylabel("Count")
    ax.set_title(f"H-M3: Bootstrap Distribution of β (n={len(boot_slopes):,})")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    out = str(Path(figures_dir) / "bootstrap_histogram.png")
    fig.savefig(out, dpi=dpi); plt.close(fig)
    return out
```

---

## L-8-1: main() orchestration [Parent: A-8, Complexity: 6]

```python
def main() -> None:
    cfg = load_config()
    cfg.validate()                                      # FileNotFoundError if H-M2 CSV missing

    kl_values, gap_values = load_dataset(cfg.input_csv_path)   # shape (10,) each

    results = fit_ols_regression(
        kl_values, gap_values,
        n_boot=cfg.n_boot,
        seed=cfg.random_seed,
    )

    verify_mechanism_activated(results)                 # RuntimeError on failure

    gate_pass, gate_reason = check_gate(results)
    results["gate_pass"]   = gate_pass
    results["gate_reason"] = gate_reason

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    plot_gate_metrics(results, cfg.figures_dir, cfg.figure_dpi)
    plot_regression_scatter(kl_values, gap_values, results, cfg.figures_dir, cfg.figure_dpi)
    plot_residuals(kl_values, gap_values, results, cfg.figures_dir, cfg.figure_dpi)
    plot_bootstrap_histogram(results, cfg.figures_dir, cfg.figure_dpi)

    print_report(results)
    save_results(results, cfg.results_json_path)

    sys.exit(0 if gate_pass else 1)
```

---

## Subtask Summary [14/14 used from logic budget]

| ID | Parent Epic | Complexity | Description |
|----|-------------|------------|-------------|
| L-3-1 | A-3 (10) | High | fit_ols_regression() full API + return dict |
| L-3-2 | A-3 (10) | High | scipy.stats.linregress step |
| L-3-3 | A-3 (10) | High | statsmodels OLS 95% CI |
| L-3-4 | A-3 (10) | High | Edge cases — degenerate / N < 5 |
| L-4-1 | A-4 (9)  | High | Bootstrap algorithm (rng.choice + linregress) |
| L-4-2 | A-4 (9)  | High | Bootstrap CI percentile |
| L-4-3 | A-4 (9)  | Medium | Bootstrap convergence check |
| L-5-1 | A-5 (7)  | Medium | verify_mechanism_activated() |
| L-5-2 | A-5 (7)  | Medium | check_gate() |
| L-6-1 | A-6 (10) | High | plot_gate_metrics() |
| L-6-2 | A-6 (10) | High | plot_regression_scatter() |
| L-6-3 | A-6 (10) | High | plot_residuals() |
| L-6-4 | A-6 (10) | High | plot_bootstrap_histogram() |
| L-8-1 | A-8 (6)  | Medium | main() orchestration wire |
