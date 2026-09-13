# Experiment Design: H-M3

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under OpenML context, if datasets are grouped by tag count categories (0, 1-2, 3-5, 6+), then each higher tag count category will have significantly more N_tasks than the previous category (monotonic dose-response), because the Discovery → Task Creation pathway amplifies with additional search pathways. Success: monotonic IRR ordering AND ≥ 2/3 adjacent contrasts p < 0.0167.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (Dose-Response) Template** — Categorical binning to test full dose-response structure of FAIR F1 mechanism.

---

## Workflow Status

**Verification State:** ACTIVE (UNATTENDED mode)
**Prerequisites Satisfied:** H-E1 PASS (MUST_WORK), H-M1 PASS (MUST_WORK), H-M2 PASS (SHOULD_WORK)
**Gate Status:** SHOULD_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM (Dose-Response Categorical)
- **Prerequisites:** H-E1 ✅, H-M1 ✅, H-M2 ✅

### Gate Condition
**SHOULD_WORK gate:** Monotonic IRR ordering of all 4 category IRRs AND ≥2/3 adjacent contrasts p < 0.0167 (Bonferroni-corrected for 3 tests, α=0.05/3).

---

## Continuation Context

H-M3 is the 4th and final mechanism sub-hypothesis. All prerequisites passed:
- H-E1: IRR=1.2263 (CI=[1.1681,1.2873], p=1.87e-16) — binary tag presence → adoption confirmed
- H-M1: has_tags survives C(decade) FE; attenuation_ratio=1.122 — platform search mechanism confirmed
- H-M2: IRR_P2=1.5332 (CI=[1.4680,1.6014], p=1.28e-82) on tagged subset — continuous dose gradient confirmed

H-M3 tests categorical dose-response on the FULL corpus (N=5,217) using bins (0, 1-2, 3-5, 6+). This tests whether the adoption effect scales monotonically with increasing tag counts — the strongest structural evidence for the Discovery → Task Creation pathway.

**Key reuse:** H-E1 preprocessed.parquet at `h-e1/results/preprocessed.parquet` contains all needed columns (N_tasks, tag_count, has_tags, log_n_instances, log_n_features, age_years, age_sq, decade). No new data download required.

### Previous Hypothesis Results
- H-E1: IRR=1.2263, CT LR=7356.36 (NB-2 appropriate), all 7 models converged BFGS
- H-M2: IRR_P2=1.5332 on tagged subset; attenuation_ratio=1.0007 (decade FE absorbs <0.1%)
- BFGS optimizer confirmed convergent on this corpus

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "negative binomial categorical dummy variables dose-response experiment design"**
- No relevant results (Archon KB is diffusion model domain; similarity ~0.28)

**Query 2: "ordered categorical regression count data pairwise contrasts Bonferroni"**
- No relevant results (similarity ~0.32 — unrelated domain)

**Summary:** Archon KB contains no content relevant to this econometric/statistics domain. Proceeding with Exa and prior hypothesis knowledge.

### Archon Code Examples

**Query: "statsmodels negativebinomial categorical dummies regression"**
- No relevant results (diffusion model domain only)

### Exa GitHub Implementations

**Query: "statsmodels negative binomial NB2 categorical dummy variable pairwise contrast Python"**

**Source 1: statsmodels Official Documentation — NegativeBinomialResults.t_test_pairwise**
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.NegativeBinomialResults.t_test_pairwise.html
- **Relevance:** Direct API for pairwise contrasts on NB-2 fitted model with multiple-testing correction
- **Key API:**
  ```python
  res = smf.negativebinomial('N_tasks ~ C(tag_count_cat) + controls', data=df).fit(method='bfgs')
  pw = res.t_test_pairwise("C(tag_count_cat)", method='hs')  # Holm-Sidak correction
  pw.result_frame  # contains coef, p-values, corrected p-values
  ```
- **Note:** method='hs' (Holm-Sidak) is the default; Bonferroni is also available via method='bonferroni'

**Source 2: statsmodels Official Documentation — NegativeBinomialResults.wald_test_terms**
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomialResults.wald_test_terms.html
- **Relevance:** Joint Wald test across all categorical levels (overall effect significance)
- **Key API:**
  ```python
  wt = res.wald_test_terms()  # tests all terms jointly
  ```

**Source 3: Andrew Wheeler Blog — Wald Tests and Pairwise Contrasts in statsmodels NB**
- **URL:** https://andrewpwheeler.com/2021/06/18/wald-tests-via-statsmodels-python/
- **Relevance:** Exact pattern matching H-M3: NB-2 with categorical IV + pairwise contrasts
- **Key Code Pattern:**
  ```python
  import itertools
  nb_mod = smf.negativebinomial('N_tasks ~ C(tag_count_cat) + controls', data_long).fit(method='bfgs')
  # Pairwise contrasts
  x_vars = list(nb_mod.params.index)
  cat_vars = [v for v in x_vars if 'tag_count_cat' in v]
  wald_li = []
  for a, b in itertools.combinations(cat_vars, 2):
      wald_li.append(a + ' - ' + b + ' = 0')
  wald_dif = ' , '.join(wald_li)
  dif = nb_mod.t_test(wald_dif)
  res_contrast = dif.summary_frame()
  ```
- **Adjacent Contrast Pattern:** Only test adjacent pairs (0 vs 1-2, 1-2 vs 3-5, 3-5 vs 6+), not all combinations

**Source 4: statsmodels Contrasts Overview**
- **URL:** https://www.statsmodels.org/dev/contrasts.html
- **Relevance:** Treatment coding documentation — C(tag_count_cat) uses reference="0" by default in patsy

**Serena Analysis Needed:** false — code from statsmodels documentation is sufficiently clear

### 🎯 Implementation Priority Assessment

H-M3 is a statistical analysis (not a DL model), so standard library implementation applies:

**Recommended Implementation Path:**
- Primary: statsmodels smf.negativebinomial with C(tag_count_cat) dummies (treatment coding, reference="0")
- Fallback: Manual contrast matrix construction via np.array + res.t_test(r_matrix)
- Justification: statsmodels t_test_pairwise() provides direct pairwise testing with Bonferroni correction; Wheeler (2021) provides exact NB-2 pairwise contrast pattern

### Code Analysis (Serena MCP)

*Skipped* — Code from statsmodels documentation and Wheeler (2021) was sufficiently clear. No complex >100-line custom architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** OpenML Dataset Corpus — Full Corpus with Categorical Tag Bins
**Type:** standard (programmatic-api reuse from H-E1)
**Version/Source:** OpenML API; corpus already cached from H-E1

**Statistics:**
- Full corpus: N=5,217 datasets (N_tasks ≥ 1)
- Expected bin distribution (from H-M2 context):
  - Bin "0" (has_tags=0): ~2,592 datasets (49.7%)
  - Bin "1-2": subset of tagged 2,625 datasets with tag_count 1-2
  - Bin "3-5": subset with tag_count 3-5
  - Bin "6+": subset with tag_count ≥ 6
- Full split used: all N=5,217 rows (no train/val/test — cross-sectional regression)

**Preprocessing:**
1. Load from cache: `pd.read_parquet('h-e1/results/preprocessed.parquet')` — contains all preprocessed columns
2. Derive tag_count from tags column: `df['tag_count'] = df['tags'].str.count(',') + 1` (for non-null rows; 0 for null/empty)
3. Derive categorical bins:
   ```python
   df['tag_count_cat'] = pd.cut(
       df['tag_count'],
       bins=[-1, 0, 2, 5, float('inf')],
       labels=["0", "1-2", "3-5", "6+"]
   ).astype(str)
   ```
4. Verify bin counts and report per-category N
5. Confirm controls present: log_n_instances, log_n_features, age_years, age_sq, decade
6. Set reference category: C(tag_count_cat, Treatment(reference="0")) in formula (patsy default)

**Synthetic Data Policy:** COMPLIANT — uses real OpenML corpus (programmatic-api type). No synthetic data.

**Loading Information:**
- Method: parquet cache reuse (no download needed)
- Identifier: `h-e1/results/preprocessed.parquet`
- Code:
  ```python
  import pandas as pd
  df = pd.read_parquet('h-e1/results/preprocessed.parquet')
  # Fallback if parquet unavailable:
  # df = pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')
  ```

### Models

#### Baseline Model

**Architecture:** NB-2 with binary has_tags IV (from H-E1, for reference comparison)
- Result: IRR=1.2263 (CI=[1.1681,1.2873]), p=1.87e-16 — cached in h-e1/results/model_results.json
- Used as reference point to compare categorical IRRs against binary threshold effect

**Loading Information:**
- Method: JSON cache reuse
- Identifier: `h-e1/results/model_results.json`
- Code: `import json; results = json.load(open('h-e1/results/model_results.json'))`

#### Proposed Model

**Architecture:** NB-2 with C(tag_count_cat) dummies (4-level categorical, reference="0")

**Core Mechanism Implementation:**

```python
# Core Mechanism: Categorical Dose-Response NB-2
# Based on: statsmodels smf.negativebinomial + Wheeler (2021) pairwise contrasts
# Source: statsmodels.org/dev + andrewpwheeler.com/2021/06/18/wald-tests-via-statsmodels-python/

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import itertools

def fit_categorical_nb2(df):
    """
    Fit NB-2 with categorical tag bins; return model + pairwise contrasts.
    IV: tag_count_cat (0, 1-2, 3-5, 6+); reference = "0"
    DV: N_tasks; Controls: log_n_instances, log_n_features, age_years, age_sq, C(decade)
    """
    formula = ('N_tasks ~ C(tag_count_cat) + log_n_instances + '
               'log_n_features + age_years + age_sq + C(decade)')
    model = smf.negativebinomial(formula, data=df, loglike_method='nb2')
    result = model.fit(method='bfgs', maxiter=200, disp=False)
    return result

def extract_irr_by_category(result):
    """Extract IRR and CI for each tag_count_cat level vs reference "0"."""
    params = result.params
    conf = result.conf_int()
    cat_params = {k: v for k, v in params.items() if 'tag_count_cat' in k}
    irr = {k: np.exp(v) for k, v in cat_params.items()}
    ci = {k: (np.exp(conf.loc[k, 0]), np.exp(conf.loc[k, 1]))
          for k in cat_params}
    return irr, ci

def test_adjacent_contrasts(result):
    """Test 3 adjacent contrasts with Bonferroni α=0.0167."""
    # Build contrast strings for adjacent pairs
    adjacent = [
        ('C(tag_count_cat)[T.1-2]', 'C(tag_count_cat)[T.0]'),  # actually ref=0, compare T.1-2 vs intercept implied
        ('C(tag_count_cat)[T.3-5]', 'C(tag_count_cat)[T.1-2]'),
        ('C(tag_count_cat)[T.6+]',  'C(tag_count_cat)[T.3-5]'),
    ]
    contrasts = [f'{a} - {b} = 0' for a, b in adjacent if b in result.params.index]
    # Use t_test_pairwise for Bonferroni-corrected p-values
    pw = result.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
    return pw.result_frame  # columns: coef, std err, t, P>|t|, pvalue-bonferroni, reject-bonferroni

def check_monotonicity(irr_dict):
    """Verify IRR(1-2) > IRR(3-5) > IRR(6+) > 0 (all vs reference "0" → all should be >1 and ordered)."""
    keys = ['C(tag_count_cat)[T.1-2]', 'C(tag_count_cat)[T.3-5]', 'C(tag_count_cat)[T.6+]']
    values = [irr_dict.get(k, 1.0) for k in keys]
    return all(values[i] < values[i+1] for i in range(len(values)-1))
```

### Training Protocol

**This is a statistical estimation, not ML training.** Reusing H-E1 BFGS optimizer configuration.

**Optimizer:** BFGS (confirmed convergent in H-E1 and H-M1/H-M2 on same corpus)
- Parameters: `method='bfgs', maxiter=200, disp=False`
- Source: H-E1 validation report (all 7 models converged BFGS)

**Models to Fit (in order):**
1. **Primary:** NB-2 with C(tag_count_cat) + full controls
2. **RC-6 (decade interaction):** NB-2 with C(tag_count_cat)*C(decade) interaction (verify dose-response is not decade-specific)
3. **RC-7 (no decade FE):** NB-2 without C(decade) to measure attenuation from categorical bins

**Seeds:** N/A (deterministic MLE optimization, no stochastic elements)

**Regularization:** None (standard MLE for count regression)

**Overdispersion Test:** Re-run Cameron-Trivedi LR test with categorical model:
```python
from scipy.stats import chi2
poisson_res = smf.poisson(formula, data=df).fit(method='bfgs')
lr_stat = 2 * (nb2_res.llf - poisson_res.llf)
p_ct = 1 - chi2.cdf(lr_stat, df=1)  # Should be << 0.05
```

### Evaluation

**Primary Metrics:**

| Metric | Target (Primary) | Target (Partial) | Source |
|--------|-----------------|------------------|--------|
| Monotonic IRR ordering | IRR(0) < IRR(1-2) < IRR(3-5) < IRR(6+) | Same | H-M3 gate def |
| Adjacent contrasts significant | All 3 p < 0.0167 (Bonferroni) | ≥2/3 p < 0.0167 | H-M3 gate def |
| Overall categorical effect (Wald) | p < 0.05 for C(tag_count_cat) joint test | — | Quality check |

**Success Criteria (SHOULD_WORK gate):**
- **Full Pass:** Monotonic IRR ordering AND all 3 adjacent contrasts p < 0.0167
- **Partial Pass (document):** Monotonic ordering with exactly 2/3 contrasts significant
- **Fail (document):** Non-monotonic ordering OR <2/3 contrasts p < 0.0167

**Expected Performance** (from H-M2 evidence):
- H-M2 showed IRR_P2=1.5332 for log(tag_count+1) on tagged subset → strong continuous dose signal
- Expected categorical IRRs vs reference "0": IRR(1-2) ~1.4-1.7, IRR(3-5) ~1.8-2.5, IRR(6+) ~2.5-4.0
- Adjacent contrast significance expected: high (given H-M2's strong p=1.28e-82)
- RC-3 risk: Cramér's V=0.823 decade-has_tags correlation documented; test whether categorical bins also correlate with decade

**Metrics Loading Information:**
- Task Type: count regression / hypothesis testing
- Library: statsmodels (built-in model results)
- Code:
  ```python
  irr = np.exp(result.params)
  ci = np.exp(result.conf_int())
  pvalues = result.pvalues
  pw_contrasts = result.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing IRR per category (0, 1-2, 3-5, 6+) with 95% CI error bars; horizontal reference line at IRR=1.0 and IRR=1.1 (H-E1 threshold)

#### Additional Figures (LLM Autonomous)
1. **Dose-Response Plot:** IRR by category with error bars, colored by significance of adjacent contrast (green=significant, orange=marginal, red=not significant)
2. **Category Distribution:** Bar chart showing N per tag_count_cat bin
3. **Adjacent Contrast Forest Plot:** Forest plot of 3 adjacent contrasts with Bonferroni-corrected CIs
4. **Attenuation Comparison:** IRR estimates with vs. without C(decade) FE to quantify RC-3 impact on categorical model

**Output Location:** `docs/youra_research/h-m3/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (NB-2 converges with categorical IV)
2. Monotonic IRR ordering observed: IRR(1-2) > IRR(3-5) is FALSE — must be IRR(1-2) < IRR(3-5) < IRR(6+) ← CORRECTED
3. ≥2/3 adjacent contrasts pass Bonferroni threshold p < 0.0167

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (Archon KB is diffusion model domain). All specifications derived from Exa + prior hypothesis results.

### B. GitHub/Web Implementations (Exa)

**Source B.1: statsmodels NegativeBinomialResults.t_test_pairwise (Official Docs)**
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.NegativeBinomialResults.t_test_pairwise.html
- **Query Used:** "statsmodels negative binomial NB2 categorical dummy variable pairwise contrast Python"
- **Key Code** (annotated):
  ```python
  # Direct pairwise testing with multiple-testing correction
  pw = res.t_test_pairwise("C(tag_count_cat)", method='bonferroni')
  # result_frame columns: coef, std err, t, P>|t|, pvalue-bonferroni, reject-bonferroni
  pw.result_frame
  ```
- **Used For:** Adjacent contrast testing (Step 5 of verification protocol); Bonferroni correction

**Source B.2: Andrew Wheeler — Wald Tests via statsmodels**
- **URL:** https://andrewpwheeler.com/2021/06/18/wald-tests-via-statsmodels-python/
- **Query Used:** same
- **Key Code** (annotated):
  ```python
  # NB-2 with categorical IV — exact H-M3 pattern
  nb_mod = smf.negativebinomial('OffN ~ C(OffCat) + CFS1:C(OffCat) - 1', data_long).fit(
      cov_type='cluster', cov_kwds=covp)
  # Pairwise contrasts via t_test string interface
  wald_li = [f'{a} - {b} = 0' for a, b in itertools.combinations(x_vars, 2)]
  dif = nb_mod.t_test(' , '.join(wald_li))
  ```
- **Adaptation for H-M3:** Adjacent pairs only (3 contrasts), not all combinations; use t_test_pairwise for cleaner output

**Source B.3: statsmodels NegativeBinomialResults.wald_test_terms**
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomialResults.wald_test_terms.html
- **Used For:** Joint Wald test for C(tag_count_cat) term significance

**Source B.4: statsmodels Contrast Coding Documentation**
- **URL:** https://www.statsmodels.org/dev/contrasts.html
- **Used For:** Treatment coding (patsy default); reference="0" for tag_count_cat

### C. Code Analysis (Serena)

Not performed — statsmodels API is standard library with clear documentation.

### D. Previous Hypothesis Context

**Source:** H-E1, H-M1, H-M2 validation reports
- **H-E1 reuse:** preprocessed.parquet contains all needed columns; BFGS optimizer confirmed; CT LR=7356 (NB-2 appropriate)
- **H-M2 reuse:** IRR_P2=1.5332 on tagged subset establishes strong dose-signal expectation for H-M3
- **RC-3 context:** Cramér's V=0.823 (decade-has_tags); attenuation_ratio=1.122 for H-E1, 1.0007 for H-M2; expect intermediate attenuation for categorical model

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (full corpus N=5,217) | Prior hypothesis | H-E1 verification_state.yaml |
| Dataset loading (parquet cache) | Prior hypothesis | H-E1 04_validation.md |
| Categorical binning (0,1-2,3-5,6+) | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-M3 |
| NB-2 model (loglike_method='nb2') | Prior hypothesis | H-E1 02c_experiment_brief.md |
| BFGS optimizer | Prior hypothesis | H-E1 04_validation.md |
| Pairwise contrast API | Exa | Source B.1 (statsmodels docs) |
| Adjacent contrast pattern | Exa | Source B.2 (Wheeler 2021) |
| Bonferroni correction (α/3=0.0167) | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-M3 |
| IRR extraction | Prior hypothesis | H-E1 02c_experiment_brief.md |
| Expected IRR range | Prior hypothesis | H-M2 04_validation.md (IRR_P2=1.5332) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T06:00:00Z

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS: 2026-08-05T05:59:32Z
- Phase 2C experiment design: IN_PROGRESS → 2026-08-05T06:00:00Z

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (statsmodels docs + Wheeler 2021), Serena (skipped — code sufficiently clear)*
*All specifications grounded in prior hypothesis results and statsmodels official documentation*
*Next Phase: Phase 3 - Implementation Planning*
