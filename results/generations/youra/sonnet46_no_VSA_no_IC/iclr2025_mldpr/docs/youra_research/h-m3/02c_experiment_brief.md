# Experiment Design: H-M3

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under PwC N=111 data, if post-breakpoint variance compression is confirmed (H-M2), then the reduction is directional (post-segment CoV values are concentrated near the lower end of the CoV distribution, not randomly distributed), consistent with ceiling-optimization rather than general convergence.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** - Tests directional specificity of variance reduction.

---

## Workflow Status

**Verification State:** ACTIVE — H-M2 VALIDATED (prerequisite satisfied)
**Prerequisites Satisfied:** H-E1 ✅ PASS, H-M1 ✅ PASS, H-M2 ✅ PASS
**Gate Status:** SHOULD_WORK — failure narrows mechanism claim but does not invalidate H-E1/H-M2

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-E1, H-M1, H-M2

### Gate Condition
SHOULD_WORK — post-segment skewness consistent with ceiling compression (downward concentration). Failure response: EXPLORE — variance reduction exists but distribution shape is symmetric; Goodhart ceiling pressure not primary driver; document as scope limitation.

---

## Continuation Context

H-M3 is the final hypothesis in chain H-E1 → H-M1 → H-M2 → H-M3. All prerequisite results confirmed:
- **paper_count\*** detected and confirmed (H-E1: permutation p < 0.05)
- **Pre-breakpoint high-variance regime** confirmed (H-M1: F-test p=0.0009, BF p=0.0099, variance 3.81× global)
- **Post-breakpoint variance compression** confirmed (H-M2: BF p=0.0099, variance ratio post/pre = 0.1981 — 5× lower)

H-M3 asks: is the post-breakpoint compression *directional* (downward skew, ceiling pressure) or merely symmetric (general convergence)? This distinguishes Goodhart saturation from benign standardization.

### Previous Hypothesis Results (if applicable)
- **H-M2 paper_count\***: inherited from H-E1 (confirmed stable across all hypotheses)
- **Pre-segment**: higher variance, higher 10th percentile, higher mean residual CoV
- **Post-segment**: 5× lower variance (variance_ratio = 0.1981), confirmed by Brown-Forsythe
- **Key reuse**: same data pipeline, same split at paper_count\*, same residual_CoV series

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB is a diffusion-model focused knowledge base — no relevant results found for statistical distribution shape analysis or benchmark saturation CoV analysis. This is expected: H-M3 is a pure statistical hypothesis requiring scipy/numpy, not a DL experiment. Archon findings: not applicable.

**Implication:** All implementation patterns drawn from scipy official documentation and ruptures library (Exa sources).

### Archon Code Examples

No relevant code examples found in Archon KB for this domain. See Exa findings below.

### Exa GitHub Implementations

**Query 1: scipy distribution shape analysis**

**Source 1**: SciPy Official Documentation — `scipy.stats.skew`, `scipy.stats.describe`, `scipy.stats.skewtest`
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
- **Relevance**: Direct API for computing sample skewness (Fisher-Pearson coefficient), with bias correction option
- **Key Code**:
  ```python
  from scipy.stats import skew, describe, skewtest
  
  # Compute skewness (Fisher-Pearson)
  skew_pre = skew(pre_segment, bias=False)   # bias=False = adjusted G1
  skew_post = skew(post_segment, bias=False)
  
  # Full distributional moments
  desc_pre = describe(pre_segment, bias=False)
  # Returns: nobs, minmax, mean, variance, skewness, kurtosis
  
  # Test if skewness significantly differs from zero
  res_post = skewtest(post_segment, alternative='less')  # H1: post is left-skewed
  ```
- **Key Insight**: `bias=False` uses adjusted Fisher-Pearson G1 = G1 * sqrt(N(N-1))/(N-2) — appropriate for small N

**Source 2**: SciPy Official Documentation — `scipy.stats.permutation_test`
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Relevance**: Permutation-based testing of distribution differences — robust for small N and non-normal data
- **Key Code**:
  ```python
  from scipy.stats import permutation_test
  
  def skewness_diff(pre, post, axis=0):
      return skew(post, axis=axis) - skew(pre, axis=axis)
  
  res = permutation_test(
      (pre_segment, post_segment),
      skewness_diff,
      permutation_type='independent',
      n_resamples=9999,
      alternative='greater'  # H1: post_skew > pre_skew (downward concentration)
  )
  ```
- **Key Insight**: permutation_test handles small N correctly; alternative='greater' tests H1: post is more right-skewed relative to pre (residuals concentrated downward)

**Source 3**: SciPy Official Documentation — `scipy.stats.mannwhitneyu`, `scipy.stats.bws_test`
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bws_test.html
- **Relevance**: Nonparametric test of distributional differences emphasizing tails — BWS test weights by variance of CDF differences, more powerful for tail differences
- **Key Insight**: BWS test better captures lower-tail concentration than Kolmogorov-Smirnov

**Query 2: ruptures change-point detection Python**

**Source 4**: deepcharles/ruptures (GitHub, 2000+ stars)
- **URL**: https://github.com/deepcharles/ruptures
- **Relevance**: Confirms PELT implementation used in H-E1; paper_count* already computed — reused as input
- **Key Code** (reuse pattern from H-E1/H-M2):
  ```python
  import ruptures as rpt
  algo = rpt.Pelt(model='l2', min_size=3).fit(residual_cov_sorted)
  breakpoints = algo.predict(pen=bic_tuned)
  paper_count_star = paper_count_sorted[breakpoints[0] - 1]
  ```
- **Key Insight**: paper_count* is a fixed input for H-M3 — no re-detection needed

**Serena Analysis Needed**: false — no complex ML code; analysis is pure scipy statistical functions on N=111 array

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT a paper reproduction experiment — it is an original statistical analysis.**

No author implementation exists. Implementation path:

**Recommended Implementation Path:**
- Primary: Direct scipy.stats implementation (skew, describe, permutation_test, mannwhitneyu, np.percentile)
- Fallback: R-equivalent (moments package) if scipy small-N warnings require alternative
- Justification: scipy.stats provides all required distribution shape statistics; permutation_test is robust to small N (N_pre ~varies, N_post ~varies depending on paper_count*); no external library needed

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. scipy.stats functions are well-documented; no complex custom code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard Data (PwC N=111)
**Type:** custom (real, pre-computed from ingest_pwc.py)
**Source:** paperswithcode/paperswithcode-data (GitHub, 932 stars)
**Confirmed from H-E1/H-M1/H-M2:** Same dataset, same derive.py output

**Details:**
- N = 111 benchmarks with confirmed CoV and paper_count
- Variables used: `residual_CoV` (linearly detrended), `paper_count` (sorted ascending)
- Split: at `paper_count*` (fixed from H-E1) into pre and post segments
- No new data loading required — reuse derive.py output from H-E1

**Loading Information** (for Phase 4 download):
- Method: custom (reuse existing)
- Identifier: `docs/youra_research/h-e1/` derive.py output CSV/pickle
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv('data/pwc_cov_computed.csv')  # from H-E1 pipeline
  df_sorted = df.sort_values('paper_count').reset_index(drop=True)
  residual_cov = df_sorted['residual_cov'].values
  paper_count = df_sorted['paper_count'].values
  ```

### Models

#### Baseline Model

**No ML model.** Statistical baseline: assume post-breakpoint CoV distribution is symmetric (null hypothesis: skewness(post) = skewness(pre), i.e., directional compression absent).

**Baseline statistic:**
- skewness(pre-segment residual CoV) — characterizes pre-breakpoint distribution shape
- 10th percentile(pre-segment) — lower-tail reference

**Loading Information** (for Phase 4 download):
- Method: scipy.stats (stdlib)
- Identifier: N/A
- Code:
  ```python
  from scipy.stats import skew, describe
  import numpy as np
  # Split at paper_count* from H-E1
  paper_count_star = <value from H-E1>  # e.g., 25 (loaded from H-E1 results)
  mask_pre = paper_count < paper_count_star
  mask_post = paper_count >= paper_count_star
  pre_segment = residual_cov[mask_pre]
  post_segment = residual_cov[mask_post]
  ```

#### Proposed Model

**Architecture:** Distribution shape analysis — directional skewness test

**Core Mechanism: Directional Skewness + Lower-Tail Concentration Test**

```python
# Core Mechanism: Goodhart Directional Specificity Analysis
# Based on: scipy.stats official documentation (SciPy v1.18.0)
# H-M3: Test that post-breakpoint CoV is directionally compressed (downward)

import numpy as np
from scipy.stats import skew, describe, permutation_test, mannwhitneyu

def directional_specificity_analysis(pre_segment, post_segment):
    """
    Test Goodhart saturation directional specificity.
    H1: post-segment CoV concentrated at lower end (ceiling pressure)
    vs H0: symmetric variance reduction (general convergence)
    
    Args:
        pre_segment: residual_CoV values for paper_count < paper_count*
        post_segment: residual_CoV values for paper_count >= paper_count*
    Returns:
        dict of test results
    """
    # Step 1: Compute full distributional moments for both segments
    desc_pre  = describe(pre_segment,  bias=False)
    desc_post = describe(post_segment, bias=False)
    # desc.skewness: Fisher-Pearson G1 (adjusted for small N)
    # desc.kurtosis: excess kurtosis (0 = normal)

    # Step 2: Skewness direction test (primary)
    # Goodhart ceiling pressure → post skewness more negative (values pile at low end)
    # OR post values cluster below pre lower tail
    skew_pre  = desc_pre.skewness
    skew_post = desc_post.skewness

    # Step 3: Permutation test on skewness difference (robust for small N)
    def skew_diff_stat(x, y, axis=0):
        return skew(y, axis=axis) - skew(x, axis=axis)
    perm_result = permutation_test(
        (pre_segment, post_segment),
        skew_diff_stat,
        permutation_type='independent',
        n_resamples=9999,
        alternative='two-sided'   # test directional difference
    )

    # Step 4: Lower-tail concentration (10th percentile comparison)
    p10_pre  = np.percentile(pre_segment,  10)
    p10_post = np.percentile(post_segment, 10)
    # Success indicator: p10_post < p10_pre (post values extend further left)

    # Step 5: Mann-Whitney U (stochastic dominance direction)
    mw_result = mannwhitneyu(pre_segment, post_segment,
                             alternative='greater')  # pre > post stochastically

    return {
        'skew_pre': skew_pre, 'skew_post': skew_post,
        'kurt_pre': desc_pre.kurtosis, 'kurt_post': desc_post.kurtosis,
        'perm_p_skew_diff': perm_result.pvalue,
        'p10_pre': p10_pre, 'p10_post': p10_post,
        'mw_pvalue': mw_result.pvalue
    }
```

### Training Protocol

**No training.** Pure statistical analysis — deterministic execution.

| Parameter | Value | Source |
|-----------|-------|--------|
| paper_count* input | Fixed from H-E1 results | H-E1 validation report |
| Pre-segment | residual_CoV[paper_count < paper_count*] | H-E1 split |
| Post-segment | residual_CoV[paper_count >= paper_count*] | H-E1 split |
| Permutation iterations | 9,999 | scipy.stats.permutation_test default |
| Skewness bias correction | bias=False (adjusted G1) | scipy docs — recommended for small N |
| Percentile method | np.percentile (linear interpolation) | numpy default |
| Seed | 42 (for permutation test reproducibility) | Fixed |

**Execution time:** < 5 seconds (N=111, pure statistical analysis)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Direction |
|--------|------------|-------------------|
| skew_post vs skew_pre | Fisher-Pearson G1 skewness of post vs pre segment | Directional consistency with ceiling compression |
| p10_post < p10_pre | 10th percentile of post-segment below pre-segment | Confirms lower-tail concentration |
| perm_p_skew_diff | Permutation test p-value for skewness difference | p < 0.10 (SHOULD_WORK threshold) |
| mw_pvalue | Mann-Whitney U one-sided p-value (pre > post stochastically) | Confirms directional ordering |

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** Post-segment skewness direction is consistent with ceiling compression (negative shift or lower-tail concentration visible in distribution moments)
- **Secondary:** Post-segment 10th percentile < pre-segment 10th percentile
- **Gate pass:** At least 2 of 4 metrics show directional consistency with H1

**Expected ranges (from H-M2 context):**
- Post-segment residual CoV: compressed, lower variance (variance_ratio=0.1981 confirmed)
- Pre-segment: likely right-skewed (high-variance exploration, few papers per benchmark)
- Post-segment: likely more symmetric or left-skewed (ceiling saturation)

**Failure Response:** IF metrics do not show directional pattern → EXPLORE — variance reduction exists (H-M2 confirmed) but is symmetric; Goodhart ceiling pressure not primary driver; document as scope limitation. H-E1 and H-M2 remain valid.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical distribution comparison
- Library: scipy.stats, numpy
- Code:
  ```python
  from scipy.stats import skew, describe, permutation_test, mannwhitneyu
  import numpy as np
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — skewness pre vs post, 10th percentile pre vs post

#### Additional Figures (LLM Autonomous)
- **Figure 1**: Histogram overlay — pre-segment vs post-segment residual_CoV distribution (same x-axis, semi-transparent, with KDE overlay)
- **Figure 2**: Distribution moments table — mean, variance, skewness, kurtosis for pre and post segments (side-by-side)
- **Figure 3**: Empirical CDF — pre vs post residual_CoV (highlight lower-tail region p10-p25)
- **Figure 4**: Q-Q plot — pre-segment vs post-segment quantiles (deviation from diagonal shows directional asymmetry)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least 2 of 4 directional metrics consistent with Goodhart ceiling compression hypothesis

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result:** No relevant sources found in Archon KB for statistical distribution shape analysis (KB is diffusion-model focused). All implementation patterns sourced from official scipy documentation and ruptures library.

### B. GitHub Implementations (Exa)

**Source 1**: SciPy Official Docs — scipy.stats.skew, scipy.stats.describe
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
- **Query Used**: "scipy distribution shape skewness comparison pre post breakpoint Python"
- **Relevance**: Direct API for sample skewness with small-N bias correction
- **Key Insight**: `bias=False` applies adjusted G1 formula — appropriate for N_post which may be ~50-70 samples
- **Used For**: Primary skewness metric in core mechanism pseudocode

**Source 2**: SciPy Official Docs — scipy.stats.permutation_test
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Query Used**: "permutation test distribution shape skewness comparison two samples Python scipy"
- **Relevance**: Robust non-parametric testing for small N; handles non-normal distributions
- **Key Insight**: `permutation_type='independent'` for two independent segments; vectorized statistic improves speed
- **Used For**: Permutation p-value for skewness difference test

**Source 3**: SciPy Official Docs — scipy.stats.bws_test, scipy.stats.mannwhitneyu
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bws_test.html
- **Query Used**: "permutation test distribution shape skewness comparison two samples Python scipy"
- **Relevance**: BWS test emphasizes tail differences — relevant for lower-tail concentration detection
- **Used For**: Backup test if Mann-Whitney insufficient for tail detection

**Source 4**: deepcharles/ruptures (2000+ stars)
- **URL**: https://github.com/deepcharles/ruptures
- **Query Used**: "Papers With Code benchmark saturation CoV coefficient of variation analysis Python ruptures change point"
- **Relevance**: PELT implementation confirmed; paper_count* is pre-computed input for H-M3
- **Used For**: Confirmation that H-E1 paper_count* value is the authoritative split point

**Source 5**: ruptures arxiv paper [1801.00826]
- **URL**: https://arxiv.org/abs/1801.00826
- **Relevance**: Confirms PELT's O(n) expected complexity, BIC penalty calibration
- **Used For**: Justification for reusing H-E1 paper_count* without re-detection

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. scipy.stats functions are standard with well-documented APIs; no custom architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: H-E1, H-M1, H-M2 validation reports
- **Reused Components**:
  - `paper_count*` — fixed split point from H-E1
  - `residual_CoV` series — detrended CoV from H-E1 pipeline
  - Pre/post segment masks — same as H-M2
  - Data pipeline — derive.py output, confirmed stable
- **Why Reused**: H-M3 directly extends H-M2 result; only distributional shape analysis changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (PwC N=111) | Previous hypothesis | H-E1 validation report |
| paper_count* split | Previous hypothesis | H-E1 validated result |
| residual_CoV series | Previous hypothesis | H-E1 derive.py output |
| Skewness metric | Exa (scipy docs) | Source B.1 |
| Permutation test | Exa (scipy docs) | Source B.2 |
| Lower-tail (p10) | Exa (scipy docs) | Source B.1 (numpy.percentile) |
| Mann-Whitney backup | Exa (scipy docs) | Source B.3 |
| Training protocol | Phase 2B | 02b_verification_plan.md H-M3 section |
| Success criteria | Phase 2B | 02b_verification_plan.md H-M3 section |

---

## State Information

**State File:** verification_state.yaml (managed via ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-21T00:00:00+00:00

### Workflow History for This Hypothesis
- 2026-08-21: Phase 2C initiated for H-M3 (prerequisites H-E1, H-M1, H-M2 all VALIDATED)
- 2026-08-21: Archon KB search — no relevant results (diffusion-model KB)
- 2026-08-21: Exa search — scipy.stats documentation and ruptures library found
- 2026-08-21: Experiment design synthesized — pure statistical analysis, no ML training
- 2026-08-21: Phase 2C COMPLETED

---

*MCP Tools Used: Archon (no relevant results), Exa (scipy docs + ruptures GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
