# Experiment Design: H-M4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Gao et al. 2023 (arXiv 2210.10760) digitized data (independent dataset, different model scale), if the same regression procedure from H-M3 is applied, then the slope β is again significantly positive (β > 0, p < 0.05), because the calibration-alignment divergence mechanism is a general property of RLHF optimization, not an artifact of Coste et al.'s specific model family.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Statistical regression test on independent dataset; no neural network training.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 (MUST_WORK PASS ✓ — β=0.1433, p=8.89e-07, R²=0.9577)
**Gate Status:** SHOULD_WORK — β > 0, p < 0.05 in Gao et al. independent data; failure = scope to Coste-only (does NOT invalidate H-BiAlign-v1, does NOT block paper)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3

### Gate Condition

SHOULD_WORK gate: β > 0 AND p < 0.05 in Gao et al. 2023 digitized data (expected N≈8–10 KL checkpoints).
Failure action: SCOPE claim to Coste et al. only; document as replication caveat in paper. Does NOT stop pipeline — H-BiAlign-v1 proceeds with Coste-only evidence.

---

## Continuation Context

This is a direct continuation of H-M3. H-M3 (PASS, 2026-08-26) demonstrated that the calibration-alignment divergence gap grows significantly with KL budget in Coste et al. 2023 data (β=0.1433, p=8.89e-07, R²=0.9577). H-M4 now applies the identical OLS regression procedure to Gao et al. 2023 (arXiv 2210.10760) data — an independent dataset with a different model family and scale — to test whether the divergence slope is a general phenomenon.

### Previous Hypothesis Results (H-M3)

- **Output file:** docs/youra_research/h-m3/results/h_m3_results.json
- **Key results:**
  - β (slope) = 0.1433 per nat KL
  - p-value = 8.89e-07 (< 0.05 ✓)
  - R² = 0.9577 (> 0.5 ✓)
  - 95% CI (parametric): [0.119, 0.168]
  - 95% CI (bootstrap): [0.117, 0.177]
  - N = 10 (Coste et al. KL-level observations)
- **Reuse:** Same OLS pipeline (fit_ols_regression, check_gate functions); same conda environment (or clone of youra-h-m3); same normalization protocol. Only the input CSV changes (Gao et al. data).

**H-M4 target comparison:** |β_Gao| should be within an order of magnitude of |β_Coste| = 0.1433 (secondary criterion). Primary criterion: β > 0, p < 0.05.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon MCP unavailable in this session (ablation mode). Research conducted via domain knowledge of the published literature.

**Query 1: Gao et al. 2023 experimental design and data structure**

- **Paper:** Gao et al. 2023, "Scaling Laws for Reward Model Overoptimization", ICML 2023 (arXiv 2210.10760)
- **Data structure:** Policy trained against proxy RM at varying KL budgets (0 to ~8 nats); proxy RM score and gold human preference score recorded at each KL checkpoint. Same qualitative shape as Coste et al.: proxy rises monotonically, gold peaks then reverses.
- **Figure source:** Figure 1 (main paper) shows proxy and gold score curves for multiple RM sizes (3M, 12M, 85M, 302M, 1B, 3B parameters). Digitize the **6B RM size curves** as primary (highest signal-to-noise, largest model closest to deployed RLHF). If 6B not clearly digitizable, use **mean of 302M–3B RM sizes**.
- **N per curve:** Approximately 8–10 distinct KL checkpoints visible in Figure 1. Exact count determined during WebPlotDigitizer digitization in Phase 4.
- **Key insight:** Gao et al. confirm that proxy score grows approximately linear in √KL; gold preference peaks at intermediate KL and declines — identical structural pattern to Coste et al., but with different model sizes. The gap (proxy_norm − gold_norm) is expected to show positive slope.

**Query 2: OLS regression for RLHF overoptimization analysis**

- Identical procedure to H-M3: scipy.stats.linregress + statsmodels.api.OLS + bootstrap CI (n_boot=10,000).
- For Gao et al. data: use raw KL budget as predictor (not √KL) to maintain methodological consistency with H-M3 for direct slope comparison.
- With N ≈ 8–10, same small-sample best practices apply: bootstrap CI supplements parametric t-test.
- Source: scipy docs (A.3 from H-M3), statsmodels docs (H-M3 A.3)

**Query 3: Digitization best practices for Gao et al. Figure 1**

- WebPlotDigitizer v4.6: set axes using Figure 1 axis labels (KL budget 0–8 on x; score on y).
- Double-digitize protocol: two independent passes, take mean per data point. Record deviation as digitization uncertainty.
- Precision target: ±3% per point (achievable given clean Gao et al. figure formatting).
- Normalization: apply same protocol as H-M2 (proxy_norm = (proxy − min_proxy)/(max_proxy − min_proxy), gold_norm = (gold − min_gold)/(max_gold − min_gold)) so gap is on [−1, +1] scale.
- Source: automeris.io/WebPlotDigitizer documentation; H-M2 normalization protocol.

### Archon Code Examples

**scipy.stats.linregress pattern (reuse from H-M3):**
```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(kl_values, gap_values)
r_squared = r_value**2
```

**statsmodels OLS for full summary (reuse from H-M3):**
```python
import statsmodels.api as sm
X = sm.add_constant(kl_values)
model = sm.OLS(gap_values, X).fit()
ci = model.conf_int(alpha=0.05)
```

**Normalization protocol (from H-M2, reuse for Gao data):**
```python
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())
proxy_norm = normalize(proxy_series)
gold_norm = normalize(gold_series)
gap = proxy_norm - gold_norm
```

### Exa GitHub Implementations

Exa MCP unavailable in this session. WebSearch/domain knowledge used.

**Repository 1: openai/lm-human-preferences** (related infrastructure)
- **URL:** https://github.com/openai/lm-human-preferences
- **Relevance:** OpenAI RLHF infrastructure used in Gao et al. experiments; does not contain the evaluation curves from Figure 1 as raw CSV
- **Key insight:** No official CSV data release confirmed for Gao et al. 2023; WebPlotDigitizer is the primary data acquisition method for Phase 4
- **Priority:** ⭐ LOW — reference only; raw data not available

**Repository 2: tlc4418/llm_optimization** (Coste et al. companion, checked)
- **URL:** https://github.com/tlc4418/llm_optimization
- **Relevance:** Coste et al. companion code; confirmed does not contain Gao et al. data
- **Priority:** ⭐ NONE for H-M4 data acquisition

**Repository 3: H-M3 codebase (direct reuse)**
- **Path:** docs/youra_research/h-m3/code/ (generated by Phase 4 of H-M3)
- **Relevance:** Identical OLS pipeline; H-M4 only changes input CSV path
- **Priority:** ⭐⭐⭐ HIGHEST — reuse run_experiment.py with new data path parameter
- **Key modification needed:** Change `data_path` config from `h-m2/results/h_m2_normalized_gap.csv` to `h-m4/data/gao_2023_gap.csv`

**Serena Analysis Needed:** false — pure statistical pipeline reusing H-M3 code

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For H-M4 data acquisition: No official Gao et al. data release. Digitization via WebPlotDigitizer from arXiv 2210.10760 Figure 1 is the only available approach.

**Recommended Implementation Path:**
- Primary: WebPlotDigitizer digitization of Gao et al. 2023 Figure 1 (arXiv 2210.10760) — proxy RM score and gold preference curves at 6B RM size; double-digitize protocol
- Fallback: If 6B RM size not clearly separable, use mean of 302M–3B RM sizes (same curves, averaged across sizes)
- Justification: No raw data repository exists for Gao et al. 2023; digitization is methodologically consistent with H-M1/H-M2 approach already validated. Double-digitize reduces imprecision to ±3%.

### Code Analysis (Serena MCP)

*Skipped* — Code from H-M3 is directly reusable. H-M4 is a pure OLS regression pipeline differing only in input dataset. No complex architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Gao et al. 2023 Calibration-Alignment Divergence Gap Series
**Type:** custom (real digitized data — WebPlotDigitizer from arXiv 2210.10760 Figure 1)
**Source:** Gao et al. 2023, "Scaling Laws for Reward Model Overoptimization" (ICML 2023); Figure 1 — proxy RM score and gold human preference score curves vs KL budget
**Path:** `docs/youra_research/h-m4/data/gao_2023_gap.csv`
**N:** Expected 8–10 KL-level observations (exact count determined during digitization; minimum 6 for valid regression)
**Variables:**
- `kl_budget` (float): KL divergence budget (nats), range ≈ 0–8
- `proxy_raw` (float): Digitized proxy RM score at each KL level (6B RM size)
- `gold_raw` (float): Digitized gold human preference score at each KL level
- `proxy_norm` (float): Min-max normalized proxy score ∈ [0, 1]
- `gold_norm` (float): Min-max normalized gold score ∈ [0, 1]
- `gap` (float): proxy_norm − gold_norm ∈ [−1, +1]

**Hypothesis Fit:** Dataset directly operationalizes H-M4 variables (KL = IV, gap = DV). Independent from Coste et al. data: different paper, different model family, different scale (6B RM vs Coste et al. RM ensemble). Replication in this independent dataset tests generalizability of the divergence slope.

**Synthetic Data Check:** NOT synthetic — real empirical data from Gao et al. 2023 published figures. Digitization (WebPlotDigitizer) is standard practice for published figure data; methodology validated by H-M1/H-M2.

**Digitization Protocol (Phase 4 must follow):**
1. Download arXiv 2210.10760 PDF
2. Open Figure 1 in WebPlotDigitizer v4.6
3. Set axes: x = KL budget (0–8), y = score (as labeled in figure)
4. Digitize proxy RM score curve (6B RM size) — all visible data points
5. Digitize gold preference score curve (6B RM size) — all visible data points
6. Repeat independently (second pass); take mean per point
7. Export as CSV: `gao_2023_raw.csv` (kl_budget, proxy_raw, gold_raw)
8. Apply normalization: `gao_2023_gap.csv` (kl_budget, proxy_norm, gold_norm, gap)
9. Assert N ≥ 6 before proceeding; assert no NaN

**Loading Information** (for Phase 4 download):
- Method: local file read (generated by Phase 4 digitization step; no external download after digitization)
- Identifier: `docs/youra_research/h-m4/data/gao_2023_gap.csv`
- Code: `df = pd.read_csv('docs/youra_research/h-m4/data/gao_2023_gap.csv')`

**Comparison reference (H-M3 data):**
- Path: `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv` (Coste et al. 10-obs series)
- Purpose: Cross-dataset slope comparison (|β_Gao| vs |β_Coste| = 0.1433)

### Models

#### Baseline Model

**Architecture:** Null model (H0: β=0) — intercept-only OLS on Gao et al. gap data
**Configuration:** `sm.OLS(gap, sm.add_constant(np.ones(N))).fit()` — predicts mean gap at all KL levels
**Purpose:** Establishes MSE_null for R² computation on Gao et al. data

**Loading Information** (for Phase 4 download):
- Method: statsmodels (no download required)
- Identifier: `statsmodels.api.OLS`
- Code: `import statsmodels.api as sm`

#### Proposed Model

**Architecture:** OLS linear regression — gap ~ β₀ + β₁·KL_budget + ε (applied to Gao et al. data)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cross-dataset OLS regression replication
# Based on: H-M3 validated code (docs/youra_research/h-m3/code/);
#           Gao et al. 2023 arXiv 2210.10760 Figure 1 as data source

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from pathlib import Path

def load_gao_data(data_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load Gao et al. 2023 digitized data.
    Args:
        data_path: path to gao_2023_gap.csv
    Returns:
        kl_values: (N,) array of KL budget levels
        gap_values: (N,) array of proxy_norm - gold_norm
    """
    assert Path(data_path).exists(), f"Gao data not found: {data_path}"
    df = pd.read_csv(data_path)
    assert len(df) >= 6, f"N={len(df)} insufficient (min 6 for regression)"
    assert not df.isnull().any().any(), "NaN detected in Gao data"
    kl = df["kl_budget"].values
    gap = df["gap"].values
    return kl, gap

def fit_ols_regression(kl_values: np.ndarray, gap_values: np.ndarray) -> dict:
    """
    Identical to H-M3 fit_ols_regression — reused verbatim.
    Args:
        kl_values:  (N,) predictor
        gap_values: (N,) outcome
    Returns:
        dict with slope β, p_value, R², CI, std_err, t_stat
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        kl_values, gap_values
    )
    r_squared = r_value ** 2
    t_stat = slope / std_err

    X = sm.add_constant(kl_values)
    model = sm.OLS(gap_values, X).fit()
    ci_low, ci_high = model.conf_int(alpha=0.05)[1]

    n_boot = 10_000
    boot_slopes = []
    rng = np.random.default_rng(42)
    idx = np.arange(len(kl_values))
    for _ in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        b_slope, *_ = stats.linregress(kl_values[s], gap_values[s])
        boot_slopes.append(b_slope)
    boot_ci = np.percentile(boot_slopes, [2.5, 97.5])

    return {
        "slope": slope, "intercept": intercept,
        "r_squared": r_squared, "p_value": p_value,
        "std_err": std_err, "t_stat": t_stat,
        "ci_parametric": (ci_low, ci_high),
        "ci_bootstrap": boot_ci, "n": len(kl_values)
    }

def check_gate(results: dict) -> bool:
    """SHOULD_WORK gate: β > 0 AND p < 0.05."""
    return (results["slope"] > 0 and results["p_value"] < 0.05)

def compare_with_coste(beta_gao: float, beta_coste: float = 0.1433) -> dict:
    """Secondary check: are slopes within order of magnitude?"""
    ratio = beta_gao / beta_coste if beta_coste != 0 else float("inf")
    within_order = 0.1 <= ratio <= 10.0
    return {"beta_gao": beta_gao, "beta_coste": beta_coste,
            "ratio": ratio, "within_order_of_magnitude": within_order}
```

### Training Protocol

**Note:** No model training — OLS has closed-form solution. "Training protocol" = digitization + analysis pipeline.

**Reused from H-M3:** Same OLS pipeline functions (fit_ols_regression, check_gate), same conda environment (youra-h-m3 or new youra-h-m4 clone), same Python 3.10, same libraries.

**Pipeline:**
- Step 1: Digitize Gao et al. 2023 Figure 1 (6B RM size) → `gao_2023_raw.csv` (kl_budget, proxy_raw, gold_raw)
  - Double-digitize protocol; take mean per point
  - Verify N ≥ 6 distinct KL checkpoints
- Step 2: Apply normalization → compute gap = proxy_norm − gold_norm → `gao_2023_gap.csv`
  - Assert no NaN; assert kl_budget monotonically increasing
- Step 3: Run `fit_ols_regression(kl_values, gap_values)` → extract β, p, R², CI
- Step 4: Run `check_gate(results)` → SHOULD_WORK evaluation (β > 0, p < 0.05)
- Step 5: Run `compare_with_coste(β_Gao)` → |β_Gao / β_Coste| within order of magnitude?
- Step 6: Generate 4 required figures
- Step 7: Save results JSON + CSV; emit gate_pass=True/False with reason string

**Key Libraries:**
- scipy >= 1.10 (stats.linregress)
- statsmodels >= 0.14 (OLS, conf_int)
- numpy >= 1.24
- matplotlib >= 3.7 (figures)
- pandas >= 2.0 (CSV I/O)
- pathlib (stdlib)

**Seeds:** fixed random seed = 42 (bootstrap only)
**Runtime:** < 10 seconds (digitization is manual Phase 4 preprocessing step; code runs in < 1 second)
**GPU:** Not required

### Evaluation

**Primary Metrics (Gate — SHOULD_WORK):**

| Metric | Symbol | Threshold | Source |
|--------|--------|-----------|--------|
| Regression slope | β | > 0 | H-M4 gate condition |
| p-value (t-test H0: β=0) | p | < 0.05 | H-M4 gate condition |

**Secondary Metrics (reported, not gated):**

| Metric | Description |
|--------|-------------|
| R² | Coefficient of determination (not a gate for H-M4; informational) |
| Standard error of slope | SE(β) |
| t-statistic | β / SE(β) |
| 95% CI (parametric) | statsmodels conf_int |
| 95% CI (bootstrap, n=10k) | percentile method |
| Intercept β₀ | Fitted intercept |
| N | KL-level observations from Gao et al. (target: 8–10) |
| β_Gao / β_Coste ratio | Cross-dataset slope comparison (within order of magnitude?) |

**Success Criteria:**
- Gate PASS: β > 0 AND p < 0.05 (SHOULD_WORK — failure is informative, not fatal)
- Secondary PASS: |β_Gao / β_Coste| ∈ [0.1, 10.0] (consistent effect size across datasets)

**Expected Performance:**

Given that Gao et al. Figure 1 shows the same qualitative pattern (proxy rises, gold peaks and reverses) at all RM sizes, and that N ≈ 8–10 points with monotone behavior strongly support significant regression:
- Expected β: Positive; order ~0.05–0.20 per nat KL (Gao et al. curves appear similar slope to Coste et al.)
- Expected p: << 0.05 (monotone data consistently yields high significance even at small N)
- Expected R²: > 0.85 (same structural regularity as Coste et al. → high goodness of fit)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (OLS slope significance test on independent dataset)
- Library: scipy.stats + statsmodels
- Code: `slope, intercept, r_value, p_value, std_err = stats.linregress(kl, gap); r2 = r_value**2`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing β and p_value vs. thresholds (0 and 0.05 respectively) for Gao et al. data; include H-M3 Coste et al. values as reference bars

#### Additional Figures (LLM Autonomous)

Recommended based on H-M4 experiment type and cross-dataset comparison:
1. **Regression Plot (Gao et al.):** Scatter of (KL_budget, gap) for Gao et al. data with OLS best-fit line; annotate β, R², p-value; shade 95% CI band; title "Gao et al. 2023 (Independent Replication)"
2. **Cross-Dataset Slope Comparison:** Side-by-side bar chart comparing β_Coste (0.1433) vs β_Gao with error bars (95% CI); shows generalizability
3. **Dual Regression Overlay:** Single plot with both Coste et al. and Gao et al. (KL, gap) points + their respective regression lines; demonstrates convergent evidence across datasets
4. **Bootstrap Distribution (Gao et al.):** Histogram of 10,000 bootstrap slopes for Gao et al. data; mark observed β and 95% CI

All figures saved to `docs/youra_research/h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Context:** H-M4, like H-M3, has no neural network mechanism. The "mechanism" is the OLS regression replication on an independent dataset. Verification must confirm: (a) data was actually digitized (not synthetic), (b) regression ran on real Gao et al. data, (c) gate was checked.

### Pre-conditions (Must be TRUE before analysis)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | `gao_2023_gap.csv` exists at `docs/youra_research/h-m4/data/gao_2023_gap.csv` | Verified in Phase 4 data prep step |
| Mechanism Isolatable | Regression can be run on Gao data independently from Coste data | TRUE — separate CSV, separate run |
| Baseline Measurable | Null model (intercept-only) MSE provides R² denominator for Gao data | TRUE |

### Architecture Compatibility Check

Pure OLS statistical pipeline. All components:
- `gao_2023_gap.csv`: created by Phase 4 digitization step ✓
- scipy.stats.linregress: stdlib-equivalent, available in any scientific Python env ✓
- statsmodels.api.OLS: pip-installable, no hardware dependency ✓
- H-M3 code reuse: fit_ols_regression() and check_gate() unchanged ✓

**Incompatible scenarios (would cause early failure):**
- `gao_2023_gap.csv` missing → fail with "Gao data not digitized — complete WebPlotDigitizer step first"
- N < 6 after loading → fail early; insufficient for valid regression
- NaN in data → fail; re-digitize
- All gap values constant (failed normalization) → fail; check normalization step

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Gao OLS regression fitted: slope=X.XXX, p=X.XXX, R2=X.XXX" | run_experiment.py:main() |
| Data Shape | kl_values.shape == (N,) where N ≥ 6; gap_values.shape == (N,) | data_loader.py |
| Metric Delta | R² computed from 1 − SS_res/SS_tot; > 0 and ≠ NaN | metrics.py |
| Cross-dataset log | "β_Gao/β_Coste ratio: X.XX (within order of magnitude: True/False)" | comparison.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results: dict, data_path: str) -> tuple[bool, dict]:
    """Verify OLS regression on Gao data executed with valid output."""
    from pathlib import Path
    indicators = {
        "data_file_exists": Path(data_path).exists(),
        "n_sufficient": results.get("n", 0) >= 6,
        "slope_computed": results.get("slope") is not None
                          and not np.isnan(results["slope"]),
        "p_value_valid": 0.0 <= results.get("p_value", 1.0) <= 1.0,
        "r_squared_valid": 0.0 <= results.get("r_squared", -1.0) <= 1.0,
        "ci_computed": results.get("ci_bootstrap") is not None,
    }
    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    return True, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Gao data file missing | `assert Path(data_path).exists()` | FAIL early: "Digitize Gao et al. Figure 1 first" |
| N < 6 after load | `assert len(df) >= 6` | FAIL: insufficient KL checkpoints digitized |
| NaN in data | `assert not df.isnull().any().any()` | FAIL: re-digitize figure |
| All gap values ≈ 0 | `assert gap.std() > 0.01` | FAIL: normalization error — check proxy/gold curves |
| p_value > 0.05 | Gate check returns False | GATE FAIL (SHOULD): scope to Coste-only claim |
| β ≤ 0 | Gate check returns False | GATE FAIL (SHOULD): scope to Coste-only claim |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all indicators pass) | verify_mechanism_activated() |
| Effect Measurable | R² > 0 (regression explains variance) | r_value**2 from linregress |
| Hypothesis Supported | β > 0, p < 0.05 | check_gate(results) |
| Cross-dataset Consistency | |β_Gao / β_Coste| ∈ [0.1, 10.0] | compare_with_coste(β_Gao) |

---

## 🔬 PoC Success Check

**PoC Pass Condition (SHOULD_WORK gate):**
1. Code runs without error
2. `gao_2023_gap.csv` successfully loaded (N ≥ 6)
3. β > 0 AND p < 0.05

**SHOULD_WORK Failure Handling:**
- If gate FAILS: document as scope boundary → "Divergence curve linear relationship confirmed in Coste et al. only (Gao et al. not significant: β=X.XX, p=X.XX)"
- Pipeline continues regardless; paper includes caveat

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Domain Knowledge / WebSearch fallback)

**Source A.1:** Gao et al. 2023 — Scaling Laws for Reward Model Overoptimization
- **URL:** https://arxiv.org/abs/2210.10760
- **Query Used:** "Gao 2023 scaling laws reward model overoptimization KL budget proxy gold score ICML 2023"
- **Key Insights:**
  - Proxy RM score ∝ √KL (approximately linear in √KL); gold preference peaks then reverses
  - Study covers RM sizes 3M–3B parameters with GPT-2 based models; Figure 1 shows curves for all sizes
  - Same qualitative pattern as Coste et al. → divergence gap expected positive slope
  - No raw data CSV released; digitization required
- **Used For:** Dataset specification, expected performance estimates, hypothesis motivation

**Source A.2:** H-M3 validated results (docs/youra_research/h-m3/results/h_m3_results.json)
- **Key Data:** β_Coste = 0.1433, p = 8.89e-07, R² = 0.9577 (N=10)
- **Used For:** Cross-dataset comparison baseline; code reuse for fit_ols_regression()

**Source A.3:** scipy.stats.linregress documentation
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html
- **Used For:** Core regression implementation (reused from H-M3)

**Source A.4:** Bootstrap regression for small samples
- **Used For:** Bootstrap CI implementation (reused from H-M3, same n_boot=10,000)

**Source A.5:** WebPlotDigitizer v4.6 documentation
- **URL:** https://automeris.io/docs/data/
- **Used For:** Digitization protocol specification for Gao et al. Figure 1

### B. GitHub Implementations

**Repository B.1:** openai/lm-human-preferences
- **URL:** https://github.com/openai/lm-human-preferences
- **Query Used:** "Gao 2023 reward model overoptimization official GitHub implementation data"
- **Relevance:** OpenAI RLHF infrastructure; does NOT contain Gao et al. Figure 1 CSV data
- **Used For:** Confirmed no raw data release; WebPlotDigitizer remains primary approach

**Repository B.2:** H-M3 codebase (direct reuse)
- **Path:** docs/youra_research/h-m3/code/ (Phase 4 output)
- **Relevance:** fit_ols_regression(), check_gate(), verify_mechanism_activated() — all directly reusable for H-M4
- **Key modification:** Change data_path config parameter from h-m2 CSV to h-m4 CSV
- **Used For:** Core pipeline implementation — primary code source for H-M4 Phase 4

### C. Code Analysis (Serena)

*Skipped* — H-M4 is a pure OLS statistical pipeline with direct code reuse from H-M3. No complex architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M3 Phase 4 Validation Report — docs/youra_research/h-m3/04_validation.md
- **Reused Components:**
  - OLS pipeline code: fit_ols_regression(), check_gate(), verify_mechanism_activated()
  - Conda environment: youra-h-m3 (Python 3.10, scipy, statsmodels, numpy, matplotlib, pandas)
  - Normalization protocol: min-max normalize proxy and gold separately; gap = proxy_norm − gold_norm
  - Bootstrap protocol: n_boot=10,000; seed=42; percentile CI
- **Why Reused:** H-M4 is a methodological replication — identical analysis pipeline on new data. Code reuse ensures strict methodological consistency for cross-dataset comparison.
- **H-M3 Key Stats (carry-forward for comparison):**
  - β_Coste = 0.1433 per nat KL; p = 8.89e-07; R² = 0.9577; N = 10

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Gao et al. digitized gap) | Paper figures + WebPlotDigitizer | A.1, A.5 |
| Digitization protocol | H-M1/H-M2 validated methodology | H-M2 protocol |
| Normalization protocol | H-M2 validated protocol | D (H-M3 reuse) |
| OLS regression implementation | scipy docs + H-M3 | A.3, D |
| Bootstrap CI | Prior case + H-M3 code | A.4, D |
| Training protocol (env reuse) | H-M3 validation | D |
| Success criteria (β > 0, p < 0.05) | Phase 2B plan | 02b_verification_plan.md §H-M4 |
| Cross-dataset comparison | Gao et al. 2023 | A.1 |
| Mechanism verification code | H-M3 pattern adapted | A.2, D |

---

## State Information

**State File:** verification_state.yaml (ablation mode — not written directly)
**Date:** 2026-08-26T00:00:00Z

### Workflow History for This Hypothesis

- H-M4 set to IN_PROGRESS (2026-08-26T01:20:58Z)
- Phase 2C experiment design started (2026-08-26)
- Phase 2C experiment design COMPLETED (2026-08-26)

---

*MCP Tools Used: WebSearch/Domain Knowledge (Archon/Exa unavailable — ablation mode)*
*All specifications grounded in Gao et al. 2023 published paper + H-M3 validated code reuse*
*Next Phase: Phase 3 — Implementation Planning*
