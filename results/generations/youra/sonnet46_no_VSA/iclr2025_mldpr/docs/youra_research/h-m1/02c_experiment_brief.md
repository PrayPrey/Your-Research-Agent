# Experiment Design: H-M1

**Date:** 2026-08-03
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** log_unique_paper_count_at_intro_z significantly predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1) on h-e2 panel: LRT p < 0.05 AND |HR-1| ≥ 0.10
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis Template** — Primary Cox Regression, LRT model comparison, HR direction interpretation.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** H-E1 VALIDATED (all 5 gates G0-G4 passed)
**Gate Status:** MUST_WORK — LRT p≥0.05 or |HR-1|<0.10 = meaningful null (publishable), routes to Phase 6

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (MUST_WORK, satisfied — G0=0.862, G1 partial_r²=0.6053, G2=0.9751, G3 std=0.2462, G4 VIF=2.14)

### Gate Condition
MUST_WORK: LRT p < 0.05 AND |HR-1| ≥ 0.10. Failure = meaningful null (H0), still routes to Phase 6 paper writing.

---

## Continuation Context

H-E1 produced `h_e2_panel_with_diversity.csv` (345 rows, 12 columns). All covariates validated. Panel is the primary input — no additional data loading required.

### Previous Hypothesis Results (H-E1)
- G0 coverage=0.862 ✅
- G1 partial_r²=0.6053 (log_unique_paper_count time-independence) ✅
- G2 partial_r²=0.9751 (diversity_ratio time-independence) ✅
- G3 std=0.2462 ✅
- G4 max_VIF=2.14 ✅
- Collinearity r=-0.324 (no failsafe triggered, both predictors usable)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB contains primarily diffusion/NLP model documentation — no relevant survival analysis or scientometrics cases found. All implementation guidance derived from Exa searches below.

**Query 1:** "Cox proportional hazards survival analysis experiment design" — results irrelevant (diffusion models)
**Query 2:** "lifelines CoxPHFitter implementation best practices penalizer" — results irrelevant

### Archon Code Examples

No relevant code examples in Archon KB for this domain.

### Exa GitHub Implementations

**Source 1: lifelines Official Documentation** (CamDavidsonPilon/lifelines)
- **URL:** https://lifelines.readthedocs.io/en/stable/fitters/regression/CoxPHFitter.html
- **Relevance:** Canonical API reference for CoxPHFitter, log_likelihood_, confidence_intervals_
- **Key API:**
  - `cph.fit(df, duration_col='duration', event_col='event')` — fits Cox PH model
  - `cph.log_likelihood_` — partial log-likelihood at fitted coefficients
  - `cph.params_` — fitted coefficients (log HR scale)
  - `cph.hazard_ratios_` — exp(params_), the HR values
  - `cph.confidence_intervals_` — CIs on log-HR scale, need exp() for HR CIs
  - `cph.log_likelihood_ratio_test()` — compares fitted model vs null (all coeffs=0)
- **Training Config:** penalizer=0.1 (L2, per Phase 2B spec)
- **Relevance:** ⭐⭐⭐ PRIMARY — official library reference

**Source 2: tooluniverse/cox_regression.md** (mims-harvard/tooluniverse)
- **URL:** https://github.com/mims-harvard/tooluniverse
- **Relevance:** Complete worked example for nested Cox LRT
- **Key Code (LRT between two nested Cox models):**
  ```python
  from scipy import stats
  from lifelines import CoxPHFitter

  cph_reduced = CoxPHFitter(penalizer=0.1)
  cph_reduced.fit(df[['duration','event','task_age','log_publication_volume',
                       'benchmark_introduction_year']],
                  duration_col='duration', event_col='event')

  cph_full = CoxPHFitter(penalizer=0.1)
  cph_full.fit(df[['duration','event','task_age','log_publication_volume',
                    'benchmark_introduction_year','log_unique_paper_count_at_intro_z']],
               duration_col='duration', event_col='event')

  lr_stat = -2 * (cph_reduced.log_likelihood_ - cph_full.log_likelihood_)
  df_diff = 1  # one additional predictor
  p_value = stats.chi2.sf(lr_stat, df_diff)
  ```
- **HR extraction:**
  ```python
  HR = cph_full.hazard_ratios_['log_unique_paper_count_at_intro_z']
  CI_lower = np.exp(cph_full.confidence_intervals_.loc[
      'log_unique_paper_count_at_intro_z', 'lower 0.95'])
  CI_upper = np.exp(cph_full.confidence_intervals_.loc[
      'log_unique_paper_count_at_intro_z', 'upper 0.95'])
  ```

**Source 3: lifelines GitHub Issue #448** (CamDavidsonPilon/lifelines)
- **URL:** https://github.com/CamDavidsonPilon/lifelines/issues/448
- **Key insight:** `log_likelihood_ratio_test()` on a single model compares to null (all β=0). For nested model comparison (M0 vs M1), use the manual scipy chi2 approach above. LR test preferred over Wald for small samples (Cox 2008).

**Source 4: lifelines Survival Regression docs**
- **URL:** https://lifelines.readthedocs.io/en/stable/Survival%20Regression.html
- **Key insight:** Concordance index available as `cph.concordance_index_`. check_assumptions() available for PH assumption diagnostics.

**Serena Analysis Needed:** false — lifelines API is well-documented, code structure clear.

### 🎯 Implementation Priority Assessment

This is NOT a paper reproduction experiment — it is an original empirical analysis using the h-e2 panel.

**Recommended Implementation Path:**
- Primary: lifelines CoxPHFitter (canonical Python survival analysis library)
- Fallback: statsmodels PHReg (if lifelines penalizer causes issues with log_likelihood_ extraction)
- Justification: lifelines is the standard Python Cox PH implementation, actively maintained, confirmed working API for nested LRT via scipy chi2.

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results (lifelines docs + tooluniverse example) was sufficiently clear for pseudo-code generation. No complex novel codebase to analyze.

---

## Experiment Specification

### Dataset

**Dataset:** h-e2 panel with diversity covariates (output of H-E1 pipeline)
**Type:** programmatic-api (derived from pwc-archive/evaluation-tables, HuggingFace)
**Source:** `/docs/youra_research/h-e1/h_e2_panel_with_diversity.csv`
**License:** CC-BY-SA-4.0

**Statistics:**
- 345 rows (benchmark-year events), 87 unique benchmarks
- 12 columns: task_path, duration, event, task_age, log_publication_volume, benchmark_introduction_year, unique_count, total_rows, paper_diversity_ratio_at_intro, log_unique_paper_count_at_intro, log_unique_paper_count_at_intro_z, paper_diversity_ratio_at_intro_z
- Events (displacement): 345 (all rows are events in this panel design)
- EPV (events per variable) = 115 with 3 covariates in M0 → well-powered

**Hypothesis Fit:** Panel directly encodes plurality-benchmark displacement events with all required predictors pre-validated (G0-G4 passed).

**Loading Information** (for Phase 4):
- Method: local CSV (output of H-E1)
- Identifier: `h_e2_panel_with_diversity.csv`
- Code:
  ```python
  import pandas as pd
  panel_df = pd.read_csv('docs/youra_research/h-e1/h_e2_panel_with_diversity.csv')
  ```

### Models

#### Baseline Model (M0)

**Architecture:** CoxPHFitter(penalizer=0.1) with covariates [task_age, log_publication_volume, benchmark_introduction_year]
**Library:** lifelines (Python)
**Purpose:** Null model — temporal/publication controls only, no diversity predictor

**Loading Information:**
- Method: pip install lifelines
- Identifier: `lifelines.CoxPHFitter`
- Code:
  ```python
  from lifelines import CoxPHFitter
  M0 = CoxPHFitter(penalizer=0.1)
  M0.fit(panel_df[['duration','event','task_age','log_publication_volume',
                    'benchmark_introduction_year']],
         duration_col='duration', event_col='event')
  ```

#### Proposed Model (M1)

**Architecture:** M0 + log_unique_paper_count_at_intro_z (primary diversity predictor)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cox LRT — Diversity Predictor Significance Test
# Based on: lifelines docs + tooluniverse/cox_regression.md

from lifelines import CoxPHFitter
from scipy import stats
import numpy as np

def run_cox_lrt(panel_df):
    """
    Fit M0 (controls) and M1 (controls + diversity predictor).
    Compute nested LRT: H0 = diversity coeff is zero.

    Input:  panel_df (345 rows) — h_e2_panel_with_diversity.csv
    Output: dict with HR, CI, p_value, lrt_stat
    """
    base_cols = ['duration','event','task_age',
                 'log_publication_volume','benchmark_introduction_year']
    div_col   = 'log_unique_paper_count_at_intro_z'

    # Step 1: Fit null model (M0)
    M0 = CoxPHFitter(penalizer=0.1)
    M0.fit(panel_df[base_cols], duration_col='duration', event_col='event')

    # Step 2: Fit full model (M1)
    M1 = CoxPHFitter(penalizer=0.1)
    M1.fit(panel_df[base_cols + [div_col]],
           duration_col='duration', event_col='event')

    # Step 3: Nested LRT (chi2, df=1)
    lrt_stat = -2 * (M0.log_likelihood_ - M1.log_likelihood_)
    p_value  = stats.chi2.sf(lrt_stat, df=1)

    # Step 4: Extract HR and 95% CI
    HR       = float(M1.hazard_ratios_[div_col])
    ci_log   = M1.confidence_intervals_.loc[div_col]
    CI_lower = float(np.exp(ci_log['lower 0.95']))
    CI_upper = float(np.exp(ci_log['upper 0.95']))

    return {
        'lrt_stat': lrt_stat, 'p_value': p_value,
        'HR': HR, 'CI_lower': CI_lower, 'CI_upper': CI_upper,
        'M0_ll': M0.log_likelihood_, 'M1_ll': M1.log_likelihood_
    }
```

### Training Protocol

Not applicable — this is a statistical estimation task, not iterative gradient training.

**Fitting Protocol:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Library | lifelines | Phase 2B spec |
| penalizer | 0.1 (L2) | Phase 2B spec |
| l1_ratio | 0.0 (pure L2) | lifelines default |
| baseline_estimation_method | 'breslow' | lifelines default |
| duration_col | 'duration' | h-e2 panel schema |
| event_col | 'event' | h-e2 panel schema |
| Seed | N/A (deterministic MLE) | — |

**Covariates:**
- M0: task_age, log_publication_volume, benchmark_introduction_year
- M1: M0 + log_unique_paper_count_at_intro_z

**Direction-interpretation protocol (pre-specified, prevents HARKing):**
- HR < 1.0 AND p < 0.05 → H1 lock-in: breadth → stakeholder network → resistance (Ott 2022)
- HR > 1.0 AND p < 0.05 → H2 saturation: diversity → overuse signal → replacement (Koch 2021, ICLR 2025)
- p > 0.05 (gates pass) → H0 null: community-breadth predictor class does not predict displacement timing

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| LRT p-value | chi2(df=1).sf(-2*(M0.ll - M1.ll)) | p < 0.05 |
| \|HR-1\| | abs(exp(M1.params_[div_col]) - 1) | ≥ 0.10 |
| HR | exp(M1.params_[div_col]) | Report direction |
| 95% CI | exp(M1.confidence_intervals_[div_col]) | Report exclusion of 1.0 |
| Concordance (M1) | M1.concordance_index_ | Report (diagnostic) |

**Success Criteria (MUST_WORK gate):**
- LRT p < 0.05 AND |HR-1| ≥ 0.10 → PASS (effect confirmed)
- p ≥ 0.05 OR |HR-1| < 0.10 → meaningful null (H0), publishable as null result

**Expected Range (from prior run documented in 02b_verification_plan.md):**
- h-m1 Run 2 directional baseline: HR=0.871, p=0.565 — did not meet threshold
- Current improved panel (h-e1 VALIDATED): stronger predictor, different coverage

**Metrics Loading Information:**
- Task Type: survival regression / hypothesis test
- Library: lifelines, scipy.stats
- Code:
  ```python
  from scipy import stats
  p_value = stats.chi2.sf(lrt_stat, df=1)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing LRT p-value vs 0.05 threshold, |HR-1| vs 0.10 threshold

#### Additional Figures (LLM Autonomous)
Based on the hypothesis type (Cox regression, hazard ratio interpretation):
1. **Kaplan-Meier by diversity quartile** — Q1 vs Q4 log_unique_paper_count_at_intro, visual survival separation
2. **Partial effects plot** — `M1.plot_partial_effects_on_outcome('log_unique_paper_count_at_intro_z', values=[-2,-1,0,1,2])` showing survival curves across diversity levels
3. **Forest plot** — HR with 95% CI for all M1 covariates, color-coded by significance
4. **Schoenfeld residuals** — M1 PH assumption check via `M1.check_assumptions(panel_df)`

**Output Location:** `docs/youra_research/h-m1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (lifelines fits M0 and M1 without convergence issues)
2. LRT p < 0.05 AND |HR-1| ≥ 0.10 (PASS) OR p ≥ 0.05 (meaningful null, also valid outcome)

**Mechanism Verification:**
- mechanism_exists: YES — CoxPHFitter(penalizer=0.1) is verified lifelines API
- mechanism_isolatable: YES — single predictor added (M0 → M1) isolates diversity effect
- baseline_measurable: YES — M0.log_likelihood_ extracted deterministically
- architecture_compatibility: CONFIRMED — h-e2 panel has all required columns (verified shape: 345×12)

**Activation Indicators:**
- Log message: "M1 fitted: HR={HR:.4f}, p={p:.4f}, |HR-1|={abs(HR-1):.4f}"
- No tensor shape change (tabular data, not neural)
- metric_delta_expected: M1.log_likelihood_ > M0.log_likelihood_ (full model should fit better)

**Mechanism Verification Code:**
```python
assert 'log_unique_paper_count_at_intro_z' in panel_df.columns
assert len(panel_df) == 345
assert M1.log_likelihood_ >= M0.log_likelihood_, "M1 should not be worse than M0"
print(f"HR={result['HR']:.4f}, p={result['p_value']:.4f}, |HR-1|={abs(result['HR']-1):.4f}")
```

**hypothesis_support_threshold:** LRT p < 0.05 AND |HR-1| ≥ 0.10
**hypothesis_support_metric:** LRT p-value + |HR-1|

**Failure Detection:**
- Convergence warning from lifelines → increase penalizer to 0.5, refit
- p_value is NaN → check panel_df for NaN rows, drop and refit
- M1.log_likelihood_ < M0.log_likelihood_ → penalizer too strong, try penalizer=0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (Archon KB contains diffusion/NLP documentation only).
- Query 1: "Cox proportional hazards survival analysis experiment design" → diffusion model results
- Query 2: "lifelines CoxPHFitter implementation best practices penalizer" → diffusion model results

### B. GitHub Implementations (Exa)

**Source B.1: lifelines Official Documentation** (CamDavidsonPilon/lifelines)
- **URL:** https://lifelines.readthedocs.io/en/stable/fitters/regression/CoxPHFitter.html
- **Query Used:** "lifelines CoxPHFitter LRT likelihood ratio test hazard ratio"
- **Key API extracted:** log_likelihood_, hazard_ratios_, confidence_intervals_, penalizer parameter
- **Used For:** Core mechanism pseudo-code, training protocol, evaluation metrics

**Source B.2: tooluniverse/cox_regression.md** (mims-harvard/tooluniverse)
- **URL:** https://github.com/mims-harvard/tooluniverse/blob/main/plugin/skills/tooluniverse-statistical-modeling/references/cox_regression.md
- **Query Used:** "lifelines CoxPHFitter log_likelihood_ LRT test two models nested scipy chi2"
- **Key Code:**
  ```python
  lr_stat = -2 * (cph_reduced.log_likelihood_ - cph_full.log_likelihood_)
  df_diff = cph_full.params_.shape[0] - cph_reduced.params_.shape[0]
  p_value = stats.chi2.sf(lr_stat, df_diff)
  ```
- **Used For:** Nested LRT pattern in core mechanism pseudo-code

**Source B.3: lifelines GitHub Issue #448**
- **URL:** https://github.com/CamDavidsonPilon/lifelines/issues/448
- **Query Used:** same as B.1
- **Key insight:** LR test preferred over Wald for small-to-medium N; scipy chi2.sf is the correct implementation for nested model comparison
- **Used For:** Justification for LRT methodology over Wald test

**Source B.4: lifelines Survival Regression Tutorial**
- **URL:** https://lifelines.readthedocs.io/en/stable/Survival%20Regression.html
- **Key insight:** concordance_index_, check_assumptions() for PH diagnostics
- **Used For:** Evaluation metrics specification, visualization requirements

**Source B.5: Papers With Code Survival Analysis page**
- **URL:** https://paperswithcode.com/task/survival-analysis/latest
- **Relevance:** Confirmed lifelines is the standard Python library for this domain (no superior alternative)

### C. Code Analysis (Serena)

*Skipped* — Code from Exa results was sufficiently clear. lifelines API is fully documented and the nested LRT pattern is a standard 5-line implementation.

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation (completed)
- **File:** `docs/youra_research/h-e1/04_validation.md`
- **Reused Components:**
  - Dataset: `h_e2_panel_with_diversity.csv` (345 rows, 12 columns) — validated
  - All covariates pre-standardized (z-scores applied)
  - VIF < 10 confirmed, collinearity r=-0.324 (safe)
- **Why Reused:** H-M1 directly consumes H-E1 output as its input

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (h-e2 panel) | H-E1 output | `h_e2_panel_with_diversity.csv` |
| CoxPHFitter(penalizer=0.1) | Phase 2B spec | 02b_verification_plan.md §H-M1 |
| Nested LRT (scipy chi2) | GitHub | B.2 tooluniverse/cox_regression.md |
| HR extraction | GitHub/Docs | B.1 lifelines docs + B.2 |
| CI extraction | StackOverflow | Exa result: lifelines #448 |
| LRT over Wald | GitHub issue | B.3 lifelines issue #448 |
| Direction protocol | Phase 2B | 02b_verification_plan.md §H-M1 |
| Evaluation metrics | Phase 2B | Success criteria §H-M1 |
| Visualization (KM) | Phase 2B | §H-M2 procedure P3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — updated via state block)
**Date:** 2026-08-03T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-03: H-E1 VALIDATED (all G0-G4 gates passed)
- 2026-08-03: H-M1 experiment_design IN_PROGRESS → COMPLETED (Phase 2C)

---

*MCP Tools Used: Archon (KB + Code — no relevant results), Exa (GitHub + docs — lifelines API confirmed)*
*All specifications grounded in lifelines official documentation and real nested LRT patterns*
*Next Phase: Phase 3 - Implementation Planning*
