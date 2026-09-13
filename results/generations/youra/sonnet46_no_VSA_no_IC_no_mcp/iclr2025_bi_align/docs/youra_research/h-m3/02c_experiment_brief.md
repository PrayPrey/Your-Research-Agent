# Experiment Design: H-M3

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Coste et al. 2023 digitized data, if a linear regression is fit with KL budget as predictor and calibration-alignment divergence gap as outcome, then the regression slope β is significantly positive (β > 0, p < 0.05, R² > 0.5), because the divergence gap formed in H-M2 increases linearly (or super-linearly) with optimization pressure as RLHF compounds proxy-gold divergence.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Statistical regression test; no neural network training.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (MUST_WORK PASS ✓)
**Gate Status:** MUST_WORK — β > 0, p < 0.05, R² > 0.5 required; failure = ABANDON H-BiAlign-v1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2

### Gate Condition

MUST_WORK gate: β > 0 AND p < 0.05 AND R² > 0.5 on Coste et al. digitized data (N=10).
Failure action: ABANDON H-BiAlign-v1; route to Phase 0 for new hypothesis.

---

## Continuation Context

This is a continuation experiment. H-M2 (PASS, 2026-08-26) validated that the calibration-alignment divergence gap is strictly positive at all 5 high-KL levels and monotonically growing (Spearman ρ=1.000, p=6.6e-64). H-M3 now formally tests the linear relationship via OLS regression using the same 10-observation dataset output by H-M2.

### Previous Hypothesis Results (H-M2)

- **Output file:** h-m2/results/h_m2_normalized_gap.csv (10 KL-level observations)
- **Key result:** Gap ranges from −0.520 (KL=0) to +0.620 (KL=8); Spearman ρ=1.000
- **Validated data (KL, gap) pairs:**

| KL Budget | gap |
|-----------|-----|
| 0.0 | -0.5200 |
| 0.5 | -0.3963 |
| 1.0 | -0.2580 |
| 2.0 | -0.0586 |
| 3.0 | +0.1196 |
| 4.0 | +0.2769 |
| 5.0 | +0.3884 |
| 6.0 | +0.4843 |
| 7.0 | +0.5598 |
| 8.0 | +0.6200 |

- **Reuse:** Same dataset (h_m2_normalized_gap.csv) enables controlled, direct continuation — only the regression analysis is new.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon MCP unavailable in this session (ablation mode). Research conducted via WebSearch.

**Query 1: RLHF overoptimization regression / slope analysis**
- Gao et al. 2023 (arXiv 2210.10760) establish that proxy scores are "roughly linear in √KL"; the difference in slope between proxy and gold score is the key Goodhart's-law signal. Their empirical functional forms directly motivate OLS regression as the appropriate test for H-M3.
- Coste et al. 2023 (arXiv 2310.02743) demonstrate monotone proxy rise + gold preference reversal, establishing the data structure that generates the divergence gap used here.
- Source: proceedings.mlr.press/v202/gao23h/gao23h.pdf

**Query 2: OLS implementation for small samples**
- scipy.stats.linregress returns (slope, intercept, r_value, p_value, std_err). R² = r_value². p_value tests H0: β=0 via Wald t-test. Ideal for n=10.
- For small samples where normality assumption may be strained, bootstrap CI (n_boot=10,000) supplements the parametric t-test.
- Source: docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html

**Query 3: Digitized-data regression best practices**
- WebPlotDigitizer exports CSV; typical precision ±2-5%. For n=10 with large effect size (expected β≈0.15 per nat KL), standard OLS is adequate. Bootstrap CI provides robustness to outliers.
- Source: automeris.io/docs/data/

### Archon Code Examples

**scipy.stats.linregress pattern (from documentation):**
```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(kl_values, gap_values)
r_squared = r_value**2
```

**statsmodels OLS for full summary:**
```python
import statsmodels.api as sm
X = sm.add_constant(kl_values)
model = sm.OLS(gap_values, X).fit()
print(model.summary())
```

### Exa GitHub Implementations

Exa MCP unavailable in this session. WebSearch used as fallback.

**Repository 1: tlc4418/llm_optimization** (GitHub)
- **URL:** https://github.com/tlc4418/llm_optimization
- **Relevance:** Companion code for Coste et al. 2023 — likely contains the RM score / gold preference data in tabular form or as figure source
- **Key insight:** If raw data is available here, it avoids digitization imprecision; Phase 4 should check this repo before relying solely on digitized CSV
- **Priority:** ⭐⭐⭐ HIGHEST — official Coste et al. implementation; check for raw experimental data

**Repository 2: Gao et al. data (MLIR proceedings)**
- **URL:** https://proceedings.mlr.press/v202/gao23h/gao23h.pdf
- **Relevance:** Gao et al. 2023 main reference; supplementary materials may contain CSV data
- **Dataset used:** Synthetic RM proxy + gold score at varying KL budgets; different model scales
- **Key insight:** Proxy scores are empirically linear in √KL; gold scores peak then decline — same structural pattern as Coste et al.

**Serena Analysis Needed:** false — no neural network architecture; pure statistical pipeline

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M3 is a pure OLS regression pipeline with no complex model architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Coste et al. 2023 Calibration-Alignment Divergence Gap Series (H-M2 output)
**Type:** custom (real digitized data, validated by H-M2)
**Source:** H-M2 validated output — h-m2/results/h_m2_normalized_gap.csv
**Path:** `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv`
**N:** 10 KL-level observations (KL ∈ {0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0})
**Variables:** kl_budget (float), gap (float = rm_norm − gold_preference)
**Hypothesis Fit:** Dataset directly operationalizes H-M3 variables (KL = IV, gap = DV). H-M2 confirmed data integrity.
**Synthetic Data Check:** NOT synthetic — real digitized empirical data from Coste et al. 2023 paper figures, validated by H-M1 and H-M2.

**Loading Information** (for Phase 4 download):
- Method: local file read (no download needed — output of H-M2)
- Identifier: `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv`
- Code: `df = pd.read_csv('docs/youra_research/h-m2/results/h_m2_normalized_gap.csv')`

**Secondary Dataset (Gao et al. preliminary check):**
- Source: arXiv 2210.10760 figures (WebPlotDigitizer digitization to be done in Phase 4 if not already available)
- Path: `docs/youra_research/h-m4/` (primary home for Gao data; H-M3 uses it only as secondary check)
- Check repo: github.com/tlc4418/llm_optimization or paper supplementary for raw CSV

### Models

#### Baseline Model

**Architecture:** Null model (H0: β=0) — intercept-only OLS
**Configuration:** `sm.OLS(gap, sm.add_constant(np.ones(N))).fit()` — predicts mean gap at all KL levels
**Purpose:** Establishes MSE_null for R² computation

**Loading Information** (for Phase 4 download):
- Method: statsmodels (stdlib-equivalent; no download)
- Identifier: `statsmodels.api.OLS`
- Code: `import statsmodels.api as sm`

#### Proposed Model

**Architecture:** OLS linear regression — gap ~ β₀ + β₁·KL_budget + ε

**Core Mechanism Implementation:**

```python
# Core Mechanism: OLS regression slope significance test
# Based on: scipy.stats.linregress documentation + Gao et al. 2023 functional form motivation

import numpy as np
from scipy import stats
import statsmodels.api as sm

def fit_ols_regression(kl_values, gap_values):
    """
    Args:
        kl_values:  (N,) array of KL budget levels (predictor)
        gap_values: (N,) array of calibration-alignment gap (outcome)
    Returns:
        dict with slope β, p_value, R², 95% CI, std_err, t_stat
    """
    # Step 1: scipy parametric OLS (Wald t-test on slope)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        kl_values, gap_values
    )
    r_squared = r_value ** 2
    t_stat = slope / std_err

    # Step 2: statsmodels OLS for full summary + confidence intervals
    X = sm.add_constant(kl_values)
    model = sm.OLS(gap_values, X).fit()
    ci_low, ci_high = model.conf_int(alpha=0.05)[1]  # 95% CI for slope

    # Step 3: Bootstrap CI (n_boot=10000, resample with replacement)
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
        "slope": slope, "intercept": intercept, "r_squared": r_squared,
        "p_value": p_value, "std_err": std_err, "t_stat": t_stat,
        "ci_parametric": (ci_low, ci_high), "ci_bootstrap": boot_ci,
        "n": len(kl_values)
    }

# Gate check
def check_gate(results):
    return (results["slope"] > 0 and
            results["p_value"] < 0.05 and
            results["r_squared"] > 0.5)
```

### Training Protocol

**Note:** No model training (OLS has closed-form solution). "Training protocol" = analysis pipeline.

**Reused from H-M2:** Same dataset, same conda environment (youra-h-m2 or new youra-h-m3), same Python 3.10.

**Pipeline:**
- Step 1: Load h_m2_normalized_gap.csv → (kl_values, gap_values) arrays (N=10)
- Step 2: Run fit_ols_regression() → extract β, p, R², CI
- Step 3: Check gate conditions (β > 0, p < 0.05, R² > 0.5)
- Step 4: (Secondary) Digitize Gao et al. data if available; run same regression
- Step 5: Generate 4 required figures
- Step 6: Save results JSON + CSV; emit exit code 0 (pass) or 1 (fail)

**Key Libraries:**
- scipy >= 1.10 (stats.linregress)
- statsmodels >= 0.14 (OLS, conf_int)
- numpy >= 1.24
- matplotlib >= 3.7 (figures)
- pandas >= 2.0 (CSV I/O)

**Seeds:** fixed random seed = 42 (bootstrap only)
**Runtime:** < 5 seconds (no GPU required)

### Evaluation

**Primary Metrics (Gate):**

| Metric | Symbol | Threshold | Source |
|--------|--------|-----------|--------|
| Regression slope | β | > 0 | H-M3 gate condition |
| p-value (t-test H0: β=0) | p | < 0.05 | H-M3 gate condition |
| Coefficient of determination | R² | > 0.5 | H-M3 gate condition |

**Secondary Metrics (reported, not gated):**

| Metric | Description |
|--------|-------------|
| Standard error of slope | SE(β) |
| t-statistic | β / SE(β) |
| 95% CI (parametric) | statsmodels conf_int |
| 95% CI (bootstrap, n=10k) | percentile method |
| Intercept β₀ | Fitted intercept value |
| N | 10 (Coste et al. observations) |
| Secondary: β_Gao | Preliminary Gao et al. slope (sign check only) |

**Success Criteria:**
- PoC Pass: β > 0 AND p < 0.05 AND R² > 0.5

**Expected Performance (from H-M2 data):**
The 10-point data series shows near-perfect monotone growth (ρ=1.000). Expected β ≈ 0.145 per nat KL (estimated from gap range 1.14 over 8 nats). Expected R² near 0.98. Expected p << 0.05.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (OLS slope significance test)
- Library: scipy.stats + statsmodels
- Code: `slope, intercept, r_value, p_value, std_err = stats.linregress(kl, gap); r2 = r_value**2`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing β, p_value, R² vs. thresholds (0, 0.05, 0.5)

#### Additional Figures (LLM Autonomous)

Recommended based on H-M3 experiment type:
1. **Regression Plot:** Scatter of (KL_budget, gap) with OLS best-fit line; annotate β, R², p-value; shade 95% CI band
2. **Residuals Plot:** Residuals vs. fitted values; check homoscedasticity
3. **Bootstrap Distribution:** Histogram of 10,000 bootstrap slopes; mark observed β and 95% CI bounds
4. **Dual Overlay (optional):** Extend H-M2 dual-line figure with regression fit overlay

All figures saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Context:** H-M3 has no neural network mechanism to verify. The "mechanism" is the OLS regression itself — the test must confirm the statistical procedure activates correctly (not just that the script runs).

### Pre-conditions (Must be TRUE before analysis)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-M2 validated gap data exists at h-m2/results/h_m2_normalized_gap.csv | TRUE — verified by H-M2 PASS |
| Mechanism Isolatable | Regression can be run with and without intercept for comparison | TRUE |
| Baseline Measurable | Null model (intercept-only) MSE provides R² denominator | TRUE |

### Architecture Compatibility Check

This experiment uses OLS regression, not a neural network. All required components:
- scipy.stats.linregress: standard library, available in any scientific Python env ✓
- statsmodels.api.OLS: pip-installable, no hardware dependency ✓
- Input data: 10-row CSV, already exists from H-M2 ✓

**Incompatible scenarios (would cause early failure):**
- h_m2_normalized_gap.csv missing or corrupted → assert file exists + shape == (10, 2) before regression
- N < 5 after loading → fail early; regression with N < 5 has insufficient power

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "OLS regression fitted: slope=X.XXX, p=X.XXX, R2=X.XXX" | run_experiment.py:main() |
| Data Shape | kl_values.shape == (10,), gap_values.shape == (10,) | data_loader.py |
| Metric Delta | R² computed from 1 − SS_res/SS_tot; != 0 | metrics.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    """Verify OLS regression executed and produced valid statistical output."""
    indicators = {
        "data_loaded": results.get("n") == 10,
        "slope_computed": results.get("slope") is not None and not np.isnan(results["slope"]),
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
| Data file missing | `assert Path(csv_path).exists()` | FAIL early: "H-M2 output not found" |
| N < 10 after load | `assert len(df) == 10` | FAIL: check H-M2 run completed |
| NaN in data | `assert not df.isnull().any().any()` | FAIL: data corruption |
| p_value > 0.05 | Gate check returns False | GATE FAIL: β not significant → ABANDON |
| R² < 0.5 | Gate check returns False | GATE FAIL: poor linear fit → ABANDON |
| β ≤ 0 | Gate check returns False | GATE FAIL: slope wrong sign → ABANDON |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (all indicators pass) | verify_mechanism_activated() |
| Effect Measurable | R² > 0 (regression explains variance) | r_value**2 from linregress |
| Hypothesis Supported | β > 0, p < 0.05, R² > 0.5 | check_gate(results) |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. β > 0 AND p < 0.05 AND R² > 0.5

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (WebSearch)

**Source A.1:** Gao et al. 2023 — Scaling Laws for Reward Model Overoptimization
- **URL:** https://proceedings.mlr.press/v202/gao23h/gao23h.pdf
- **Query Used:** "Gao 2023 scaling laws reward model overoptimization KL budget proxy gold score"
- **Key Insight:** Proxy scores are roughly linear in √KL; the slope difference between proxy and gold scores is the Goodhart's-law signal. Motivates OLS regression as the correct test for monotone divergence.
- **Used For:** Motivation for H-M3 OLS regression design; Gao et al. dataset as secondary check in H-M3

**Source A.2:** Coste et al. 2023 — Reward Model Ensembles Help Mitigate Overoptimization
- **URL:** https://arxiv.org/abs/2310.02743
- **Query Used:** "Coste 2023 reward model overoptimization arXiv 2310.02743"
- **Key Insight:** Paper from which figure data was digitized; shows proxy RM score rise + gold preference reversal at KL > 3 nats.
- **Used For:** Primary dataset origin; companion GitHub (tlc4418/llm_optimization) flagged as priority data source

**Source A.3:** scipy.stats.linregress documentation
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html
- **Query Used:** "scipy.stats linregress OLS regression slope significance p-value R-squared Python"
- **Key Insight:** linregress returns (slope, intercept, r_value, p_value, std_err); R² = r_value²; p_value from Wald t-test on H0: β=0. Standard for n=10 regression.
- **Used For:** Core regression implementation in pseudo-code

**Source A.4:** Bootstrap regression for small samples
- **URL:** https://www.linkedin.com/pulse/linear-regression-bootstrapping-ali-mirzaei
- **Query Used:** "WebPlotDigitizer digitized data OLS regression small sample n=10 confidence interval bootstrap Python"
- **Key Insight:** Bootstrap (n_boot=10,000, resample with replacement) gives CI without normality assumption — appropriate for n=10.
- **Used For:** Bootstrap CI in pseudo-code; robustness supplement to parametric t-test

### B. GitHub Implementations (WebSearch/Exa fallback)

**Repository B.1:** tlc4418/llm_optimization
- **URL:** https://github.com/tlc4418/llm_optimization
- **Query Used:** "Coste 2023 reward model overoptimization arXiv 2310.02743"
- **Relevance:** Official Coste et al. 2023 companion code; may contain raw RM score / gold preference tables that supersede digitization
- **Priority:** ⭐⭐⭐ HIGHEST — Phase 4 must check this repo for raw data before relying on WebPlotDigitizer CSV
- **Used For:** Flagged as primary data source to verify against h_m2_normalized_gap.csv

### C. Code Analysis (Serena)

*Skipped* — H-M3 is a pure OLS statistical pipeline. No complex architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M2 Phase 4 Validation Report — docs/youra_research/h-m2/04_validation.md
- **Reused Components:**
  - Dataset: h_m2_normalized_gap.csv (10 KL-level observations, N=10)
  - Conda environment: youra-h-m2 (Python 3.10, scipy, numpy, matplotlib, pandas)
  - Normalization protocol: RM_norm = (RM − 0.12) / (1.96)
- **Why Reused:** Enables direct continuation — H-M3 is the regression test on H-M2's output; only the statistical analysis code is new
- **H-M2 Key Stats (carry-forward):** gap range [−0.520, +0.620]; Spearman ρ=1.000; max_gap=0.620

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Coste et al. gap CSV) | H-M2 output | h-m2/results/h_m2_normalized_gap.csv |
| OLS regression implementation | scipy docs | A.3 |
| Bootstrap CI | LinkedIn/academic | A.4 |
| Hypothesis motivation (Goodhart slope) | Gao et al. 2023 | A.1 |
| Data origin (paper) | Coste et al. 2023 | A.2 |
| Official code repo | GitHub | B.1 |
| Training protocol (env reuse) | H-M2 validation | D |
| Success criteria | Phase 2B plan | Section 2.2 H-M3 |

---

## State Information

**State File:** verification_state.yaml (ablation mode — not written directly)
**Date:** 2026-08-26T00:00:00Z

### Workflow History for This Hypothesis

- H-M3 set to IN_PROGRESS (2026-08-26T01:05:09Z)
- Phase 2C experiment design started (2026-08-26)
- Phase 2C experiment design COMPLETED (2026-08-26)

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable — ablation mode)*
*All specifications grounded in H-M2 validated output + published RLHF literature*
*Next Phase: Phase 3 — Implementation Planning*
