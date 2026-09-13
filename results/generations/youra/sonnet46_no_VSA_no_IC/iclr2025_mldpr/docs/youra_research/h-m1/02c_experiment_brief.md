# Experiment Design: H-M1

**Date:** 2026-08-21
**Author:** Anonymous
**Hypothesis Statement:** Under PwC benchmark data, if benchmarks are split at detected paper_count*, then pre-breakpoint residual CoV will exhibit significantly higher variance than the overall CoV distribution baseline, confirming the early-phase exploration regime of the Goodhart saturation mechanism.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis Template** — Tests whether the early-phase (pre-breakpoint) regime is genuinely high-variance relative to the full series baseline.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** H-E1 VALIDATED (PASS) — paper_count* detected, permutation p < 0.05
**Gate Status:** MUST_WORK (pre-segment variance > global variance, F-test p < 0.10 one-tailed)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (paper_count* as fixed input)

### Gate Condition
MUST_WORK — pre-breakpoint residual CoV variance must exceed full-series variance (one-sample F-test p < 0.10, one-tailed). Pre-segment mean residual CoV must be positive (directional confirmation).

---

## Continuation Context

H-M1 directly depends on H-E1. The paper_count* value detected by H-E1 is used as a fixed input (not re-estimated). The residual_CoV series (linearly detrended, sorted by paper_count ascending) produced by H-E1 is reused as the input series.

### Previous Hypothesis Results (H-E1)
- H-E1 VALIDATED: PELT detected structural break (paper_count*) in N=111 PwC residual CoV series
- paper_count* confirmed in range [10, 120]
- Permutation test p < 0.05 (PASS)
- residual_CoV series: OLS-detrended CoV sorted by paper_count ascending (N=111 observations)
- Source: docs/youra_research/h-e1/04_validation.md (Phase 4 output)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB searched with queries:
1. "variance regime analysis change-point detection experiment design" → No domain-relevant results (KB is image-diffusion focused)
2. "F-test variance comparison pre-post breakpoint statistical analysis" → No domain-relevant results
3. "benchmark saturation CoV paper count statistical analysis" → No domain-relevant results

**Assessment:** Archon KB does not contain benchmark saturation or statistical variance comparison cases. All implementation grounding sourced from Exa.

### Archon Code Examples

Queries for "PELT change-point detection ruptures scipy variance test" and "scipy levene Brown-Forsythe variance comparison F-test" returned no relevant domain content from Archon KB.

### Exa GitHub Implementations

**Query 1: PELT ruptures change-point pre/post segment variance**

**Source 1**: deepcharles/ruptures (⭐ 2042)
- **URL**: https://github.com/deepcharles/ruptures
- **Relevance**: Official ruptures library — PELT implementation used in H-E1; segment indexing from PELT output used to split residual_CoV into pre/post segments
- **Key Code**:
  ```python
  import ruptures as rpt
  algo = rpt.Pelt(model='l2', min_size=3, jump=5).fit(signal)
  breakpoints = algo.predict(pen=bic_tuned)
  # breakpoints[-1] == n_samples (sentinel); breakpoints[0] == paper_count* index
  pre_segment = signal[:breakpoints[0]]
  post_segment = signal[breakpoints[0]:]
  ```
- **Source**: https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/

**Source 2**: PELT regime shift example (sesen.ai blog)
- **URL**: https://sesen.ai/blog/changepoint-detection-regime-shifts
- **Relevance**: Demonstrates post-PELT regime characterization pattern — compute statistics per regime after detection
- **Key Pattern**: After `breakpoints = algo.predict(pen=20)`, segment series by breakpoint index and compute per-regime statistics (mean, variance)

**Query 2: scipy levene Brown-Forsythe variance test**

**Source 3**: SciPy official docs — scipy.stats.levene
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html
- **Key Code**:
  ```python
  from scipy import stats
  stat, p = stats.levene(pre_segment, post_segment, center='median')
  # center='median' = Brown-Forsythe variant (robust to non-normality)
  ```
- **Relevance**: Brown-Forsythe test is the primary H-M2 tool; for H-M1, one-sample F-test variant used

**Source 4**: statology.org Brown-Forsythe example
- **URL**: https://www.statology.org/brown-forsythe-test-in-python/
- **Relevance**: Confirms `scipy.stats.levene(*groups, center='median')` is the correct Brown-Forsythe call

**Serena Analysis Needed**: false — all code is <50 lines and clearly understood from documentation

### 🎯 Implementation Priority Assessment

H-M1 is a pure statistical analysis — no ML model, no paper to reproduce. Implementation uses standard Python scientific stack (scipy, numpy, ruptures) with no official "author implementation" to prioritize.

**Recommended Implementation Path:**
- Primary: scipy.stats + ruptures (official libraries, well-documented)
- Fallback: Manual variance ratio computation (numpy only)
- Justification: H-M1 tests pre-segment variance vs. global variance using a one-sample F-ratio; scipy provides all required tools natively

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. All required operations (PELT segment indexing, scipy variance tests) are well-documented in official library docs.

---

## Experiment Specification

### Dataset

**Name**: PwC Leaderboard Benchmark Data — N=111 CoV-computed benchmarks
**Type**: custom (derive.py output from H-E1)
**Source**: paperswithcode/paperswithcode-data (GitHub, 932 stars)

| Field | Value |
|-------|-------|
| N | 111 benchmarks |
| Variables | paper_count (int), cov (float), residual_cov (float, OLS-detrended) |
| Split | None — full N=111 used (no train/test split; statistical analysis) |
| Preprocessing | Applied upstream in H-E1: OLS detrending (CoV ~ paper_count), sorted by paper_count ascending |
| Augmentation | None |

**Synthetic Data Check**: PASS — real PwC leaderboard data (API/scrape via ingest_pwc.py, confirmed working in H-E1)

**Loading Information** (for Phase 4):
- Method: custom (derive.py output)
- Identifier: `./data/pwc_cov_computed.csv` or equivalent derive.py output path
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv('data/pwc_cov_computed.csv')
  # Columns: benchmark_name, paper_count, cov, residual_cov
  # Already sorted by paper_count ascending (from H-E1)
  ```

### Models

#### Baseline Model

**Architecture**: Statistical baseline — OLS linear regression (CoV ~ paper_count, no change-point)
**Type**: Statistical (no ML model)
**Configuration**: Smooth monotonic relationship (rho=−0.28, R²≈0.08)

**Loading Information** (for Phase 4):
- Method: statsmodels OLS
- Code:
  ```python
  import statsmodels.formula.api as smf
  ols_result = smf.ols('cov ~ paper_count', data=df).fit()
  residual_cov = ols_result.resid
  ```

**Baseline (Global Variance)**:
- global_variance = np.var(residual_cov, ddof=1)  ← full N=111 series variance

#### Proposed Model

**Architecture**: H-E1 PELT segmentation + Pre-segment variance characterization

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pre-Breakpoint Variance Characterization for H-M1
# Based on: deepcharles/ruptures (PELT), scipy.stats (F-test)
# Input: residual_cov (np.array, N=111, sorted by paper_count ascending)
#        paper_count_star_idx (int, breakpoint index from H-E1)

import numpy as np
from scipy import stats

def analyze_pre_segment_variance(residual_cov, paper_count_star_idx):
    """
    Args:
        residual_cov: 1D array, N=111, OLS-detrended CoV sorted by paper_count
        paper_count_star_idx: breakpoint index from H-E1 PELT output
    Returns:
        dict with variance ratio, F-stat, p-value, mean pre-segment
    """
    n = len(residual_cov)
    global_var = np.var(residual_cov, ddof=1)

    # Split at breakpoint
    pre = residual_cov[:paper_count_star_idx]    # early-phase benchmarks
    post = residual_cov[paper_count_star_idx:]   # post-saturation benchmarks

    pre_var = np.var(pre, ddof=1)
    pre_mean = np.mean(pre)

    # One-sample F-test: pre_var / global_var ~ F(n_pre-1, n-1)
    # One-tailed: H1 = pre_var > global_var
    F_stat = pre_var / global_var
    df1 = len(pre) - 1
    df2 = n - 1
    # p-value for one-tailed test (right tail)
    p_one_tailed = 1 - stats.f.cdf(F_stat, df1, df2)

    # Brown-Forsythe pre vs post (for H-M2 preview)
    bf_stat, bf_p = stats.levene(pre, post, center='median')

    return {
        'pre_n': len(pre), 'post_n': len(post),
        'global_var': global_var,
        'pre_var': pre_var, 'pre_mean': pre_mean,
        'F_stat': F_stat, 'p_one_tailed': p_one_tailed,
        'bf_stat': bf_stat, 'bf_p': bf_p,
        'variance_ratio_pre_global': pre_var / global_var,
    }
```

### Training Protocol

H-M1 is a statistical analysis — no model training. "Protocol" = analysis execution plan.

**Execution Protocol:**

| Step | Operation | Tool |
|------|-----------|------|
| 1 | Load residual_cov series from H-E1 derive.py output | pandas |
| 2 | Load paper_count* index (breakpoint index) from H-E1 validation output | pickle/json |
| 3 | Compute global variance (full N=111 series) | numpy |
| 4 | Split series at breakpoint index → pre_segment, post_segment | numpy slicing |
| 5 | Compute pre-segment variance and mean | numpy |
| 6 | One-sample F-test: pre_var / global_var ~ F(n_pre-1, N-1), one-tailed | scipy.stats.f |
| 7 | Confirm pre-segment mean > 0 (directional check) | numpy |
| 8 | Report: N_pre, N_post, global_var, pre_var, pre_mean, F_stat, p_one_tailed | — |

**Seeds**: 1 (fixed; deterministic statistical analysis — no randomness)
**Compute**: Trivial (N=111, single-core CPU, <1 second)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Pass Threshold |
|--------|-----------|----------------|
| `p_one_tailed` | One-tailed F-test p-value: pre_var > global_var | p < 0.10 |
| `pre_mean_positive` | Sign of pre-segment mean residual_CoV | > 0 (directional) |
| `variance_ratio_pre_global` | pre_var / global_var | > 1.0 |

**Success Criteria (PoC):**
- PRIMARY: F-test p_one_tailed < 0.10 AND variance_ratio_pre_global > 1.0
- SECONDARY: pre_mean > 0 (above-trend early-phase behavior confirmed)

**Expected Performance (from Phase 2B):**
- Goodhart theory predicts pre-segment is genuinely high-variance (exploration regime)
- H-E1 confirmed a structural break exists, so pre-segment should differ from global
- Expected pre_n ≈ paper_count* index value (range 10-120 benchmarks)

**Metrics Loading Information:**
- Task Type: statistical hypothesis test
- Library: `scipy.stats` (built-in scipy)
- Code:
  ```python
  from scipy import stats
  import numpy as np
  F_stat = pre_var / global_var
  p = 1 - stats.f.cdf(F_stat, df1=len(pre)-1, df2=len(residual_cov)-1)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing global_var vs pre_var vs post_var with F-test p annotation

#### Additional Figures (LLM Autonomous)
Recommended based on H-M1 mechanism:
1. **Variance comparison bar chart**: global_var, pre_var, post_var side-by-side with error bars
2. **Scatter plot**: residual_CoV vs paper_count with vertical line at paper_count*, colored pre/post
3. **Distribution overlay**: KDE of pre-segment vs post-segment residual_CoV distributions
4. **Box plots**: pre-segment vs post-segment vs full-series residual_CoV distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `pre_var > global_var` (F-test p_one_tailed < 0.10)
3. `pre_mean > 0` (directional confirmation)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 paper_count* index is available as fixed input | TRUE — H-E1 VALIDATED |
| Mechanism Isolatable | Pre/post split controlled by paper_count_star_idx; toggling idx changes result | TRUE |
| Baseline Measurable | Global variance of full N=111 series computable independently | TRUE |

### Architecture Compatibility Check

H-M1 requires:
- residual_cov series (N=111, sorted by paper_count ascending) from H-E1 derive.py output
- paper_count_star_idx (breakpoint index, integer) from H-E1 PELT prediction output

**Required Features:**
- H-E1 PELT breakpoint index available (not just paper_count* value — need array index)
- scipy >= 1.7.0 for `stats.f.cdf` and `stats.levene`

**Incompatible Configurations:**
- paper_count* value alone without array index (need to map value back to index)
- Series not sorted by paper_count ascending (violates segmentation assumption)

> ⚠️ If paper_count_star_idx not saved by H-E1, Phase 4 must recompute from H-E1 code.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Pre-segment N={n_pre}, variance={pre_var:.4f}, global_var={global_var:.4f}" | analyze_pre_segment_variance() |
| Value Check | pre_var > global_var (ratio > 1.0) | results['variance_ratio_pre_global'] |
| Metric Delta | F_stat > 1.0 indicates pre-segment more variable than global | results['F_stat'] |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    indicators = {
        "pre_var_computed": results.get('pre_var') is not None,
        "global_var_computed": results.get('global_var') is not None,
        "ratio_above_one": results.get('variance_ratio_pre_global', 0) > 1.0,
        "f_stat_computed": results.get('F_stat') is not None,
        "p_value_computed": results.get('p_one_tailed') is not None,
    }
    activated = all(indicators.values())
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| paper_count_star_idx missing | KeyError on loading H-E1 output | FAIL: Rerun H-E1 with idx export |
| pre_segment empty (idx=0) | len(pre) == 0 | FAIL: paper_count* at boundary |
| pre_var == global_var | ratio == 1.0 exactly | Warn: degenerate case |
| F_stat < 1.0 | pre_var < global_var | FAIL gate (MUST_WORK not satisfied) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | pre_var and global_var both computed |
| Effect Measurable | pre_var > global_var | variance_ratio_pre_global > 1.0 |
| Hypothesis Supported | F-test p_one_tailed < 0.10 | `results['p_one_tailed']` |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB searched with 5 queries (3 knowledge base + 2 code examples). No domain-relevant content found — KB is focused on image generation / diffusion models. All statistical analysis grounding from Exa/official documentation.

### B. GitHub Implementations (Exa)

**Repository 1**: deepcharles/ruptures (⭐ 2042)
- **URL**: https://github.com/deepcharles/ruptures
- **Query Used**: "PELT ruptures change-point detection pre-post segment variance F-test Python"
- **Relevance**: Official ruptures library; segment indexing from PELT predict() output used to define pre/post split
- **Key Code** (annotated):
  ```python
  # PELT predict() returns list of breakpoint indices (1-indexed, sorted)
  # Last element == n_samples (sentinel end)
  breakpoints = algo.predict(pen=bic_tuned)
  paper_count_star_idx = breakpoints[0]  # first (and only) breakpoint for single-break model
  pre_segment = residual_cov[:paper_count_star_idx]
  post_segment = residual_cov[paper_count_star_idx:]
  ```
- **Used For**: Segment splitting logic in core mechanism pseudo-code

**Repository 2**: PELT regime shift blog (sesen.ai)
- **URL**: https://sesen.ai/blog/changepoint-detection-regime-shifts
- **Query Used**: same as above
- **Key Pattern**: Post-PELT per-regime statistics (mean, variance) computation pattern
- **Used For**: Protocol step 3-7 (per-regime statistics)

**Repository 3**: SciPy docs — scipy.stats.levene
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html
- **Query Used**: "scipy levene Brown-Forsythe variance homogeneity test pre-post segment"
- **Key Code**:
  ```python
  stat, p = stats.levene(pre_segment, post_segment, center='median')
  # center='median' = Brown-Forsythe test (robust to non-normality)
  ```
- **Used For**: H-M2 preview computation embedded in H-M1 function (brown_forsythe result)

**Repository 4**: application-architect.com Brown-Forsythe example
- **URL**: https://www.application-architect.com/posts/how-to-perform-the-brown-forsythe-test-in-python/
- **Used For**: Confirmed `center='median'` is the correct Brown-Forsythe parameter

### C. Code Analysis (Serena)

Serena Analysis: Not performed — code from search results was sufficiently clear (all operations <50 lines, standard scipy/ruptures API).

### D. Previous Hypothesis Context

**Source**: H-E1 Phase 4 Validation Report
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Reused Components**:
  - residual_cov series (N=111, OLS-detrended, sorted by paper_count ascending)
  - paper_count_star_idx (PELT breakpoint index — must be exported by H-E1 Phase 4)
- **Why Reused**: H-M1 tests the pre-breakpoint regime defined by H-E1's result; controlled comparison requires identical residual_cov and breakpoint

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (N=111 PwC) | Phase 2B / H-E1 | 02b_verification_plan.md §1.3 |
| paper_count_star_idx input | Previous hypothesis (H-E1) | H-E1 Phase 4 validation output |
| Pre/post segment split | GitHub | deepcharles/ruptures B.1 |
| One-sample F-test formula | Phase 2B protocol | 02b_verification_plan.md H-M1 §Verification Protocol |
| Brown-Forsythe (preview) | SciPy docs | scipy.stats.levene B.3 |
| Pseudo-code structure | GitHub + SciPy docs | B.1, B.3 |
| Success threshold p<0.10 | Phase 2B gate condition | 02b_verification_plan.md §3.2 |

---

## Quality Validation Results

```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified (F-test formula from Phase 2B; p<0.10 from gate condition)
✅ Dataset choice justified (PwC N=111, same as H-E1, custom type — real data confirmed)
✅ Mechanism grounded in code (ruptures PELT indexing + scipy.stats.f documented)
✅ No unsupported assumptions (all claims reference Phase 2B or H-E1)
✅ Full traceability (Traceability matrix in §E covers all specs)
✅ Synthetic data check: PASS (custom real PwC data, not simulated)

Overall: PASSED
```

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in ```state block)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- H-M1 set to IN_PROGRESS (2026-08-21): External loop starting Phase 2C → 3 → 4
- H-M1 experiment_design.status = COMPLETED (2026-08-21): Phase 2C complete

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant domain content), Exa (GitHub + web search — ruptures, scipy), Serena (Skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
