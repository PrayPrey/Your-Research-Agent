# Experiment Design: h-m2

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Post-breakpoint residual CoV has significantly lower variance than pre-breakpoint residual CoV (Brown-Forsythe p < 0.05, variance ratio post/pre < 1.0), confirming Goodhart saturation compression.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED, PASS), H-M1 (VALIDATED, PASS)
**Gate Status:** MUST_WORK — not yet evaluated (pending experiment execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (paper_count* detected), H-M1 (pre-segment high variance confirmed)

### Gate Condition
MUST_WORK: Brown-Forsythe p < 0.05 AND variance ratio (post/pre) < 1.0. If fails: PIVOT — change-point reflects mean shift only, not variance homogenization; Goodhart mechanism as described is not operating.

---

## Continuation Context

H-E1 (VALIDATED): paper_count* detected via PELT on N=111 PwC residual CoV, permutation p < 0.05.
H-M1 (VALIDATED): Pre-breakpoint variance 3.81× higher than global (F-test p=0.0009, BF p=0.0099). Pre-segment mean residual CoV is positive (above trend). Gate MUST_WORK satisfied.

**Reuse from H-E1/H-M1:**
- `residual_cov` array (OLS-detrended CoV values, N=111) — use directly
- `paper_count*` breakpoint value — fixed input from H-E1
- `pre_segment` and `post_segment` arrays — already defined by H-M1
- `ingest_pwc.py` + `derive.py` pipeline — confirmed working

### Previous Hypothesis Results (if applicable)

**H-E1:** PELT detected paper_count* ∈ [10, 120], permutation p < 0.05. Bootstrap 95% CI width ≤ 20 papers.
**H-M1:** Pre-segment variance 3.81× global variance. F-test p=0.0009, Brown-Forsythe p=0.0099. Pre-segment mean residual CoV > 0.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No domain-relevant results found for Brown-Forsythe variance testing or Goodhart saturation in the Archon KB. The KB is indexed primarily on diffusion model content (HuggingFace diffusers, Stable Diffusion). Proceeding with Exa and scipy documentation as primary sources.

### Archon Code Examples

No relevant code examples found in Archon KB for statistical variance testing. Proceeding with Exa sources.

### Exa GitHub Implementations

**Source 1:** scipy.stats.levene (SciPy official documentation + scipy/scipy source)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html
- **Relevance:** Brown-Forsythe test IS `scipy.stats.levene(..., center='median')` — no separate function needed
- **Key Code:**
  ```python
  from scipy import stats
  stat, p = stats.levene(pre_segment, post_segment, center='median')
  # center='median' → Brown-Forsythe variant (robust to non-normality)
  # H0: var(pre) == var(post); H1 (one-tailed): var(post) < var(pre)
  ```
- **Permutation variant (for small N):**
  ```python
  def statistic(a, b):
      return stats.levene(a, b, center='median').statistic
  ref = stats.permutation_test(
      (pre_segment, post_segment), statistic,
      permutation_type='independent', alternative='greater'
  )
  ```
- **Used for:** Core test implementation, p-value interpretation

**Source 2:** ruptures PELT (already used in H-E1, reused here for segment extraction)
- **URL:** https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/
- **Relevance:** paper_count* from PELT defines the split point; H-M2 reuses this result
- **Key Code:**
  ```python
  import ruptures as rpt
  algo = rpt.Pelt(model='l2', min_size=3, jump=5).fit(residual_cov_sorted)
  bkps = algo.predict(pen=bic_tuned)
  paper_count_star = paper_counts_sorted[bkps[0] - 1]
  pre_segment = residual_cov_sorted[:bkps[0]]
  post_segment = residual_cov_sorted[bkps[0]:-1]
  ```
- **Used for:** Segment definition (inherited from H-E1)

**Source 3:** Application Architect — Brown-Forsythe in Python
- **URL:** https://www.application-architect.com/posts/how-to-perform-the-brown-forsythe-test-in-python/
- **Key insight:** `center='median'` is the recommended choice for skewed distributions (CoV is right-skewed by nature)
- **Variance ratio pattern:**
  ```python
  var_pre = np.var(pre_segment, ddof=1)
  var_post = np.var(post_segment, ddof=1)
  variance_ratio = var_post / var_pre  # H1: ratio < 1.0
  ```

### 🎯 Implementation Priority Assessment

This is a purely statistical hypothesis — no ML paper author implementation to seek. The ground truth implementation is scipy's official levene function.

**Recommended Implementation Path:**
- Primary: `scipy.stats.levene(pre_segment, post_segment, center='median')` — Brown-Forsythe test
- Fallback: permutation test variant via `stats.permutation_test` for asymptotic approximation concern at small N
- Justification: scipy is the canonical scientific Python statistics library; center='median' is the standard Brown-Forsythe specification; confirmed by 3 independent sources

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a statistical analysis experiment; no complex neural architecture or unfamiliar code pattern requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard Data — N=111 CoV-computed benchmarks
**Type:** standard (derived programmatic output — no download required)
**Source:** paperswithcode/paperswithcode-data (GitHub, 932 stars) via ingest_pwc.py + derive.py
**Path:** `./data/` (auto-generated by ingest_pwc.py → derive.py pipeline, confirmed working in H-E1)

**Statistics:**
- N = 111 benchmarks (post-filtering: benchmarks with ≥ 3 results and valid CoV)
- Variables used: `paper_count` (integer count of result rows per benchmark), `cov` (coefficient of variation of best scores)
- Derived: `residual_cov` = OLS residuals of `cov ~ paper_count`
- Segments: `pre_segment` (paper_count < paper_count*), `post_segment` (paper_count ≥ paper_count*)
- Segment sizes: determined by paper_count* from H-E1 (variable; expect ~40-70 pre, ~41-71 post)

**Preprocessing:**
1. Load cov + paper_count arrays from derive.py output (already computed in H-E1)
2. Sort by paper_count ascending (already done in H-E1)
3. OLS detrend: fit `cov ~ paper_count`, extract residuals → `residual_cov`
4. Split at paper_count* (fixed from H-E1): `pre_segment = residual_cov[paper_count < paper_count*]`, `post_segment = residual_cov[paper_count >= paper_count*]`

**Augmentation:** None (statistical analysis, no augmentation applicable)

**Loading Information** (for Phase 4 download):
- Method: programmatic (ingest_pwc.py → derive.py pipeline)
- Identifier: `paperswithcode/paperswithcode-data` GitHub
- Code: `python ingest_pwc.py && python derive.py` — outputs `data/benchmarks_cov.csv`

### Models

#### Baseline Model

**Architecture:** No model (statistical null baseline)
**Description:** Null hypothesis: var(pre_segment) == var(post_segment). Represented by Brown-Forsythe W-statistic under H0 (no variance difference).

**Configuration:**
- Library: `scipy.stats` (scipy >= 1.7.0)
- Test: `stats.levene(pre_segment, post_segment, center='median')`
- Null distribution: F(1, N-2) asymptotic approximation

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `scipy`
- Code: `pip install scipy statsmodels ruptures numpy pandas`

#### Proposed Model

**Architecture:** Brown-Forsythe test (Levene with median center) + variance ratio analysis + piecewise linear regression F-test (independent confirmation)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Post-Breakpoint Variance Compression Detection
# Based on: scipy.stats.levene (Brown-Forsythe variant), scipy docs

import numpy as np
from scipy import stats
import statsmodels.api as sm

def test_variance_compression(pre_segment, post_segment, alpha=0.05):
    """
    Args:
        pre_segment:  residual CoV values for paper_count < paper_count*
        post_segment: residual CoV values for paper_count >= paper_count*
        alpha: significance level (default 0.05)
    Returns:
        dict with bf_stat, bf_p, variance_ratio, one_tailed_p, passed
    """
    # Step 1: Brown-Forsythe test (Levene with median center)
    # H0: var(pre) == var(post); H1: var(post) < var(pre) [one-tailed]
    bf_stat, bf_p_two = stats.levene(pre_segment, post_segment, center='median')

    # Step 2: One-tailed p-value (H1: post variance is LOWER)
    # Two-tailed BF reports |difference|; one-tailed = two_tailed/2 if direction confirmed
    bf_p_one_tailed = bf_p_two / 2  # valid only if var(post) < var(pre)

    # Step 3: Variance ratio
    var_pre = np.var(pre_segment, ddof=1)
    var_post = np.var(post_segment, ddof=1)
    variance_ratio = var_post / var_pre  # H1: ratio < 1.0

    # Step 4: Gate check
    direction_confirmed = variance_ratio < 1.0
    passed = (bf_p_two < alpha) and direction_confirmed

    return {
        'bf_stat': bf_stat,
        'bf_p_two_tailed': bf_p_two,
        'bf_p_one_tailed': bf_p_one_tailed if direction_confirmed else 1.0,
        'var_pre': var_pre, 'var_post': var_post,
        'variance_ratio': variance_ratio,
        'n_pre': len(pre_segment), 'n_post': len(post_segment),
        'direction_confirmed': direction_confirmed,
        'gate_passed': passed
    }
```

### Training Protocol

**Note:** No ML training. This is a deterministic statistical analysis.

**Execution Protocol:**
- **Step 1 — Load data:** Load derive.py output `data/benchmarks_cov.csv` (N=111)
- **Step 2 — OLS detrend:** `model = sm.OLS(cov, sm.add_constant(paper_count)).fit(); residual_cov = model.resid`
- **Step 3 — Sort:** Sort `residual_cov` and `paper_count` by paper_count ascending
- **Step 4 — Split at paper_count*:** Use paper_count* from H-E1 stored result
- **Step 5 — Brown-Forsythe test:** `stats.levene(pre_segment, post_segment, center='median')`
- **Step 6 — Variance ratio:** `np.var(post, ddof=1) / np.var(pre, ddof=1)`
- **Step 7 — Piecewise regression F-test:** Independent confirmation via statsmodels piecewise OLS
- **Step 8 — Report:** All statistics, gate verdict, and visualizations

**Computational resources:** Trivial (CPU only, <1 second)
**Seeds:** 1 (fixed; permutation test uses `np.random.seed(42)` if run)
**Reproducibility:** Fully deterministic given fixed paper_count* from H-E1

### Evaluation

**Primary Metrics:**
- `bf_p_two_tailed`: Brown-Forsythe p-value (two-tailed, threshold < 0.05)
- `variance_ratio`: var(post) / var(pre) (threshold < 1.0)

**Success Criteria (MUST_WORK Gate):**
1. `bf_p_two_tailed < 0.05` (statistically significant variance difference)
2. `variance_ratio < 1.0` (post-breakpoint variance is lower than pre-breakpoint)
3. Both conditions must hold simultaneously

**Secondary Metrics:**
- `bf_p_one_tailed`: One-tailed p-value (for reporting; = bf_p_two / 2 when direction confirmed)
- Piecewise regression F-test p-value (independent confirmation)
- `var_pre`, `var_post`: Absolute variance values
- `n_pre`, `n_post`: Segment sizes
- Effect size: variance ratio magnitude (smaller = stronger compression)

**Expected Performance (from H-M1 precedent and H1 theory):**
- H-M1 showed pre-segment variance is 3.81× global. If post-segment variance is near-global or below, variance_ratio ≈ var_post / (3.81 × var_global) → strong compression expected
- Predicted variance_ratio: 0.1–0.4 (strong Goodhart compression signal)
- BF p-value: < 0.01 (expected given strong prior from H-M1)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical hypothesis testing
- Library: `scipy.stats`, `numpy`, `statsmodels`
- Code:
  ```python
  from scipy import stats
  import numpy as np
  stat, p = stats.levene(pre_segment, post_segment, center='median')
  ratio = np.var(post_segment, ddof=1) / np.var(pre_segment, ddof=1)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — Brown-Forsythe p-value vs threshold (0.05), variance ratio vs threshold (1.0)

#### Additional Figures (LLM Autonomous)

1. **Variance Distribution Comparison:** Side-by-side box plots of pre-segment vs post-segment residual CoV — visually confirms compression
2. **Variance Ratio Magnitude Plot:** Horizontal bar showing var_pre vs var_post with ratio annotation
3. **Residual CoV Scatter with Regime Coloring:** All N=111 points colored by regime (pre=orange, post=blue) with variance bounds (mean ± 1 SD) overlaid — matches H-E1 visualization style
4. **F-distribution Reference:** Annotated F-distribution showing BF test statistic position vs critical value

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | residual_cov is OLS-detrended and available from H-E1 pipeline | TRUE — confirmed by H-E1 VALIDATED status |
| Mechanism Isolatable | Brown-Forsythe test can be run with/without paper_count* split | TRUE — split point is a single parameter |
| Baseline Measurable | Null distribution (equal variances) is analytically defined | TRUE — F(1, N-2) distribution |

### Architecture Compatibility Check

This is a statistical test experiment, not a neural architecture experiment.

**Required Components:**
- `scipy >= 1.7.0` — levene with center='median' parameter
- `numpy >= 1.20` — var, array slicing
- `statsmodels >= 0.13` — OLS for piecewise regression F-test
- `ruptures >= 1.1` — paper_count* from H-E1 (already installed)
- H-E1 output: paper_count* value stored (required as fixed input)

**Incompatible Configurations:**
- Using center='mean' instead of center='median' → Levene's test, NOT Brown-Forsythe (different robustness properties)
- Using one-tailed p directly from scipy (scipy returns two-tailed only; must divide by 2 when direction is confirmed)

> ⚠️ If paper_count* from H-E1 is not available, Phase 4 MUST fail early with clear error message!

---

### Mechanism Activation Indicators

**How to detect if the variance compression mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"Brown-Forsythe: stat={:.4f}, p={:.4f}, ratio={:.4f} — GATE PASS/FAIL"` | main experiment runner |
| Variance Values | `var_post < var_pre` (print both) | `test_variance_compression()` |
| Metric Delta | `variance_ratio < 1.0` (expected ~0.1-0.4) | `test_variance_compression()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    indicators = {
        "direction_confirmed": results['variance_ratio'] < 1.0,
        "statistically_significant": results['bf_p_two_tailed'] < 0.05,
        "effect_measured": results['var_pre'] != results['var_post'],
        "n_pre_nonzero": results['n_pre'] > 0,
        "n_post_nonzero": results['n_post'] > 0,
    }
    all_pass = all(indicators.values())
    print(f"Mechanism verification: {indicators}")
    print(f"Gate verdict: {'PASS' if all_pass else 'FAIL'}")
    return all_pass, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| paper_count* not found | H-E1 result file missing | FAIL EARLY: "H-E1 paper_count* required" |
| Empty post_segment | len(post_segment) == 0 | FAIL EARLY: bad split |
| Direction wrong | variance_ratio >= 1.0 | FAIL gate: mean shift only, not compression |
| p >= 0.05 | bf_p_two_tailed >= 0.05 | FAIL gate: insufficient evidence |
| scipy version issue | levene missing center param | Pin scipy >= 1.7.0 |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | variance_ratio < 1.0 AND p < 0.05 | `test_variance_compression()` return |
| Effect Measurable | variance_ratio ≠ 1.0 | Before/after comparison |
| Hypothesis Supported | bf_p_two_tailed < 0.05 AND variance_ratio < 1.0 | Combined gate check |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No domain-relevant results found. Archon KB indexed on diffusion model content; does not contain statistical variance testing or benchmark saturation literature.

### B. GitHub Implementations (Exa)

**Source B.1:** SciPy — scipy.stats.levene (Brown-Forsythe implementation)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html
- **Source code:** https://github.com/scipy/scipy/blob/main/scipy/stats/_morestats.py
- **Query Used:** "scipy.stats.levene Brown-Forsythe variance homogeneity test Python"
- **Relevance:** Canonical Python implementation of Brown-Forsythe test
- **Key Code:**
  ```python
  stat, p = stats.levene(a, b, center='median')  # Brown-Forsythe
  ```
- **Configuration Extracted:** center='median' for non-normal data (CoV distributions are right-skewed)
- **Used For:** Core test, primary metric computation

**Source B.2:** Application Architect — Brown-Forsythe in Python
- **URL:** https://www.application-architect.com/posts/how-to-perform-the-brown-forsythe-test-in-python/
- **Query Used:** "scipy.stats.levene Brown-Forsythe variance homogeneity test Python"
- **Relevance:** Shows variance ratio computation pattern and one-tailed interpretation
- **Key Code:**
  ```python
  bf_stat, bf_pval = stats.levene(*groups, center='median')
  var_ratio = np.var(post, ddof=1) / np.var(pre, ddof=1)
  ```
- **Used For:** Variance ratio pattern, gate check logic

**Source B.3:** ruptures — PELT change-point detection
- **URL:** https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/
- **Query Used:** "PELT change-point detection variance ratio pre post segment ruptures Python"
- **Relevance:** paper_count* extraction (inherited from H-E1); segment split definition
- **Used For:** Segment boundary definition (reused from H-E1 implementation)

**Source B.4:** Ciencia de Datos — Tests equality of variances with Python
- **URL:** https://cienciadedatos.net/documentos/pystats07-test-equality-of-variance-python
- **Relevance:** Confirms Levene/BF are the recommended non-parametric variance equality tests; Fligner-Killeen as additional non-parametric option
- **Used For:** Test selection justification (BF over Bartlett given CoV non-normality)

### C. Code Analysis (Serena)

Serena analysis not performed — statistical analysis with standard library functions; no complex code patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**H-E1 Contribution:**
- Paper_count* detected and stored
- `residual_cov` array computed (OLS-detrended)
- `paper_count_sorted` array computed
- All reused directly in H-M2

**H-M1 Contribution:**
- Pre-segment confirmed as high-variance (F-test p=0.0009, BF p=0.0099, 3.81× ratio)
- `pre_segment` and `post_segment` arrays already defined
- Results inform expected variance_ratio direction

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset (PwC N=111) | Phase 2B (02b_verification_plan.md) | Section 1.3 |
| Brown-Forsythe test choice | Exa / scipy docs | B.1, B.4 |
| center='median' parameter | Exa / Application Architect | B.2 |
| Variance ratio formula | Exa / Application Architect | B.2 |
| One-tailed interpretation | Exa / scipy docs | B.1 |
| Segment split (paper_count*) | Previous hypothesis H-E1 | D: H-E1 |
| pre_segment arrays | Previous hypothesis H-M1 | D: H-M1 |
| Piecewise regression F-test | Phase 2B (02b_verification_plan.md) | Section 2.2 H-M2 |
| Success criteria thresholds | Phase 2B (02b_verification_plan.md) | Section 2.2 H-M2 |
| Pseudo-code structure | Exa / scipy source | B.1, B.2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed via state blocks)
**Date:** 2026-08-21

### Workflow History for This Hypothesis

- 2026-08-21: Phase 2C experiment design COMPLETED for h-m2

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (scipy docs, Application Architect, ruptures docs, cienciadedatos)*
*All specifications grounded in scipy official documentation and H-E1/H-M1 validated results*
*Next Phase: Phase 3 - Implementation Planning*
