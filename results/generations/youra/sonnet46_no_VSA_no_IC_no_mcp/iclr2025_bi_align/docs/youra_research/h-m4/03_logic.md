# Logic Document: H-M4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 — Cross-dataset OLS Replication (Gao et al. 2023)
**Phase:** 3 — Implementation Planning

---

## 1. Core Logic Summary

H-M4 logic is identical to H-M3 with one input substitution: Gao et al. 2023 digitized data replaces Coste et al. data. The OLS pipeline is reused verbatim. New logic: `compare_with_coste()` cross-dataset slope ratio check.

---

## 2. Pseudo-code: Complete Pipeline

```
FUNCTION main():
    # Phase 4 pre-step: manual WebPlotDigitizer digitization
    # OUTPUT: gao_2023_raw.csv
    
    # Step 1: Load and validate raw data
    df_raw = load_raw(DATA_RAW)
    ASSERT df_raw has columns {kl_budget, proxy_raw, gold_raw}
    ASSERT len(df_raw) >= 6
    ASSERT no NaN in df_raw

    # Step 2: Normalize and compute gap
    proxy_norm = (proxy_raw - min(proxy_raw)) / (max(proxy_raw) - min(proxy_raw))
    gold_norm = (gold_raw - min(gold_raw)) / (max(gold_raw) - min(gold_raw))
    gap = proxy_norm - gold_norm
    ASSERT std(gap) > 0.01  # non-trivial variance
    ASSERT kl_budget is monotonically non-decreasing
    SAVE df[kl_budget, proxy_norm, gold_norm, gap] → gao_2023_gap.csv

    # Step 3: OLS regression
    slope, intercept, r_value, p_value, std_err = linregress(kl_budget, gap)
    r_squared = r_value^2
    t_stat = slope / std_err
    X = [1 | kl_budget]  # design matrix with intercept
    ci_parametric = statsmodels.OLS(gap, X).conf_int(alpha=0.05)[1]
    
    # Bootstrap CI
    boot_slopes = []
    FOR i in range(10_000):
        idx = rng.choice(N, size=N, replace=True)
        b_slope = linregress(kl_budget[idx], gap[idx]).slope
        boot_slopes.append(b_slope)
    ci_bootstrap = percentile(boot_slopes, [2.5, 97.5])

    results = {slope, intercept, r_squared, p_value, std_err, t_stat,
               ci_parametric, ci_bootstrap, n=N}

    # Step 4: Gate check (SHOULD_WORK)
    gate_pass = (slope > 0) AND (p_value < 0.05)
    IF gate_pass:
        print "GATE PASS: β > 0, p < 0.05"
    ELSE:
        print "GATE FAIL (SHOULD_WORK): scope to Coste-only — continue pipeline"

    # Step 5: Cross-dataset comparison
    ratio = slope / 0.1433  # β_Gao / β_Coste
    within_order = 0.1 <= |ratio| <= 10.0
    print f"β_Gao/β_Coste = {ratio:.3f} (within order of magnitude: {within_order})"

    # Step 6: Mechanism verification
    verify_mechanism_activated(results, DATA_GAP)
    # Raises RuntimeError if any indicator fails

    # Step 7: Figures (5 total)
    generate fig1_gate_metrics(results, gate)
    generate fig2_regression_gao(df_gap, results)
    generate fig3_cross_dataset_slopes(results, comparison)
    generate fig4_dual_overlay(df_gap, results)
    generate fig5_bootstrap_histogram(boot_slopes, slope, ci_bootstrap)

    # Step 8: Save
    SAVE results + gate + comparison → h_m4_results.json
    SAVE df_gap → results/gao_2023_gap_final.csv
    PRINT summary table
```

---

## 3. Tensor / Array Shapes

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| kl_budget | (N,) | float64 | N ≈ 8–10; range 0–8 nats |
| proxy_raw | (N,) | float64 | Digitized proxy RM scores |
| gold_raw | (N,) | float64 | Digitized gold preference scores |
| proxy_norm | (N,) | float64 | ∈ [0, 1] after min-max |
| gold_norm | (N,) | float64 | ∈ [0, 1] after min-max |
| gap | (N,) | float64 | ∈ [-1, +1] |
| X (OLS design) | (N, 2) | float64 | [ones, kl_budget] |
| boot_slopes | (10000,) | float64 | Bootstrap distribution |

---

## 4. Key Invariants

1. **N ≥ 6** before any regression — fail fast otherwise
2. **No NaN** at any stage — digitization error if triggered
3. **gap.std() > 0.01** — proxy and gold curves must diverge after normalization
4. **kl_budget monotone** — data points ordered by KL level
5. **Seed = 42** — bootstrap reproducible
6. **Methodology identical to H-M3** — no algorithm modifications permitted; cross-dataset comparison validity requires this

---

## 5. API Specifications

### `load_raw(data_raw_path) → pd.DataFrame`
- Input: path string or Path to gao_2023_raw.csv
- Output: DataFrame with columns [kl_budget, proxy_raw, gold_raw]
- Raises: AssertionError if file missing, columns wrong, N < 6, or NaN

### `compute_gap(df) → pd.DataFrame`
- Input: raw DataFrame
- Output: DataFrame with added columns [proxy_norm, gold_norm, gap]
- Raises: AssertionError if gap.std() ≤ 0.01

### `fit_ols_regression(kl_values, gap_values, n_boot, seed) → dict`
- Input: (N,) arrays for kl and gap; n_boot=10000; seed=42
- Output: dict with keys [slope, intercept, r_squared, p_value, std_err, t_stat, ci_parametric, ci_bootstrap, n]
- No exceptions expected given valid inputs

### `check_gate(results, beta_min=0.0, p_max=0.05) → dict`
- Input: results dict from fit_ols_regression
- Output: dict {gate_pass: bool, gate_type: str, reason: str}

### `compare_with_coste(beta_gao, beta_coste=0.1433) → dict`
- Input: scalar floats
- Output: dict {beta_gao, beta_coste, ratio, within_order_of_magnitude}

### `verify_mechanism_activated(results, data_path) → tuple[bool, dict]`
- Input: results dict; path string to gap CSV
- Output: (True, indicators_dict) or raises RuntimeError

---

## 6. Digitization Pre-Step Logic (Manual — Phase 4)

```
MANUAL STEP (WebPlotDigitizer v4.6):
1. Download arXiv 2210.10760 PDF
2. Open Figure 1; set axes: x ∈ [0, 8] (KL budget), y (score)
3. Target 6B RM size curves (proxy RM score + gold preference)
   Fallback: if 6B not clearly separable → use mean of 302M, 1B, 3B curves
4. Pass 1: digitize all visible data points for proxy curve
5. Pass 1: digitize all visible data points for gold curve
6. Pass 2: repeat independently
7. Per point: mean of pass1 and pass2
8. Export CSV: gao_2023_raw.csv (columns: kl_budget, proxy_raw, gold_raw)
9. Assert N ≥ 6 rows
```

This step produces the only input to the automated code pipeline.

---

## 7. Gate Failure Handling

```
IF gate_pass == False:
    results["gate_outcome"] = "FAIL"
    results["failure_note"] = (
        "SHOULD_WORK gate failed. "
        "Scope divergence linearity claim to Coste et al. only. "
        f"Gao et al.: β={slope:.4f}, p={p_value:.4f}. "
        "H-BiAlign-v1 paper proceeds with Coste-only evidence."
    )
    # Still generate figures, save results, write validation report
    # Pipeline continues — no blocking
```

---

## 8. Cross-Dataset Slope Comparison Logic

```python
# Secondary criterion — informational, not gated
ratio = beta_gao / beta_coste  # beta_coste = 0.1433 from H-M3
within_order = 0.1 <= abs(ratio) <= 10.0

# Interpretation:
#   ratio ~1.0: near-identical slopes across datasets (strong replication)
#   ratio 0.1–10: same order of magnitude (consistent effect)
#   ratio < 0.1 or > 10: effect size inconsistent (but gate already handles β direction)
```

---

## 9. Figure Generation Logic

### fig1: Gate Metrics Bar Chart
```python
# Two bar groups: β comparison and p comparison
# β bar: β_Gao (blue); threshold bar: β=0 (red dashed)
# H-M3 reference: β_Coste = 0.1433 (orange)
# p bar: p_Gao (blue); threshold bar: p=0.05 (red dashed)
# H-M3 reference: p_Coste = 8.89e-7 (orange, log scale)
```

### fig2: Regression Scatter (Gao data)
```python
# Scatter: kl_budget (x) vs gap (y) — Gao et al. points
# Line: OLS fit over kl range
# Shading: 95% parametric CI band
# Annotation: f"β={slope:.4f}, R²={r2:.4f}, p={p:.2e}, N={n}"
# Title: "Gao et al. 2023 (Independent Replication)"
```

### fig3: Cross-Dataset Slope Comparison
```python
# Two bars: β_Coste=0.1433, β_Gao=slope
# Error bars: 95% CI (parametric) for each
# x-axis: ["Coste et al. 2023", "Gao et al. 2023"]
# y-axis: "OLS Slope β (proxy_norm − gold_norm per nat KL)"
```

### fig4: Dual Regression Overlay
```python
# Both datasets on one plot
# Coste et al. points (squares) + regression line (dashed)
# Gao et al. points (circles) + regression line (solid)
# Legend showing both β values
# Note: Coste et al. KL range ~0–1.5; Gao et al. ~0–8 — normalize x for overlay
```

### fig5: Bootstrap Histogram (Gao)
```python
# Histogram of 10k bootstrap slopes (Gao data)
# Vertical line: observed β
# Shaded region: 95% CI from percentile
# Title: "Bootstrap Slope Distribution — Gao et al. 2023"
```
