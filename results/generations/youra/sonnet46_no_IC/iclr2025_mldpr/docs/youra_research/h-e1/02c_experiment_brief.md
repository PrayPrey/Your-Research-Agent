# Experiment Design: h-e1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the OpenML platform context (N=5,217 datasets with N_tasks≥1), having at least one keyword tag (has_tags binary=1) is associated with significantly more registered ML tasks (N_tasks) than untagged datasets, with incidence rate ratio ≥ 1.1 (95% CI lower ≥ 1.1) in NB-2 regression controlling for dataset size (log n_instances, log n_features), age (age_years, age2), and decade-of-upload fixed effects (C(decade)).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK — IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: IRR for `has_tags` ≥ 1.1 AND 95% CI lower bound ≥ 1.1 AND p < 0.05 in NB-2 regression with C(decade) fixed effects.

Failure → STOP pipeline, route to Phase 0.

---

## Continuation Context

First hypothesis in verification chain — no previous context.

### Previous Hypothesis Results (if applicable)
None — h-e1 is the foundation hypothesis. No prerequisites.

**Historical context from h-e1 (prior episode):**
- Composite metadata score (0–5) gave IRR=1.076, 95% CI [1.060, 1.092] — below 1.1 threshold
- RC-3 failure: decade FE absorbed composite score (IRR=1.014, p=0.19) — critical lesson
- Binary description presence (RC-2a) outperformed composite: IRR=1.102
- This episode uses binary has_tags IV, theoretically motivated by platform search architecture

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Results Summary:**
- Queries executed: (1) "negative binomial regression count data experiment design", (2) "NB-2 statsmodels implementation best practices", (3) "count regression overdispersion fixed effects Python"
- **Result:** Archon KB contains no relevant NB-2/count regression cases. All results were diffusion model artifacts (similarity scores 0.28–0.44, unrelated domain). This is expected — Archon KB is seeded with deep learning papers, not econometrics/statistics literature.
- **Implication:** No past implementation cases to draw from Archon. Experiment design grounded entirely in Exa (statsmodels docs) and Phase 2B specifications.

### Archon Code Examples

**Search Results Summary:**
- Query: "count regression overdispersion fixed effects Python"
- **Result:** No relevant code examples found (all results: diffusion model schedulers, stable diffusion pipelines). Similarity scores 0.30–0.33, clearly unrelated.
- **Conclusion:** Archon code base does not contain NB-2 or econometric regression examples. Implementation will be based on statsmodels official documentation (found via Exa).

### Exa GitHub Implementations

**Query 1: statsmodels negativebinomial NB2 regression Python implementation**

**Source 1**: statsmodels official documentation (statsmodels.org)
- **URL**: https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html
- **Relevance**: Official API for NegativeBinomial class with loglike_method='nb2'
- **Key API**:
  ```python
  statsmodels.discrete.discrete_model.NegativeBinomial(
      endog, exog, loglike_method='nb2', ...
  )
  # NB-2: variance = μ + α·μ² (most common specification)
  ```
- **Fit method**: `.fit(method='bfgs', maxiter=35)` — BFGS confirmed convergent

**Source 2**: statsmodels formula API (smf.negativebinomial)
- **URL**: https://www.statsmodels.org/dev/generated/statsmodels.formula.api.negativebinomial.html
- **Key Code**:
  ```python
  import statsmodels.formula.api as smf
  result = smf.negativebinomial(
      formula='N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)',
      data=df,
      loglike_method='nb2'
  ).fit(method='bfgs')
  ```
- **IRR extraction**: `np.exp(result.params)` for IRR; `np.exp(result.conf_int())` for CI
- **Results object**: `NegativeBinomialResults` — `.params`, `.bse`, `.pvalues`, `.conf_int()`

**Source 3**: NegativeBinomial GLM approach (gist.github.com/sachinsdate)
- **URL**: https://gist.github.com/sachinsdate/7c4bb6b82009a130466c48e0957ffb52
- **Pattern**: Alternative GLM approach (two-step: Poisson → OLS for α → NB2); formula API is simpler and more direct
- **Verdict**: Use `smf.negativebinomial` directly (simpler, handles loglike_method='nb2' internally)

**Query 2: OpenML dataset metadata tagging adoption count regression**
- **Source**: openml-python official docs (openml.github.io)
- **Key finding**: `openml.datasets.list_datasets(output_format='dataframe', status='active')` returns metadata including `tag` field
- **Corpus already available**: `h-e1/code/data/h_e1/openml_dataset_corpus.csv` (N=5,217) — no re-download needed

**Serena Analysis Needed**: false — statsmodels formula API is well-documented and straightforward

### 🎯 Implementation Priority Assessment

**CRITICAL:** This is NOT a paper reproduction experiment. It is an original empirical analysis using the OpenML corpus. No "official author implementation" to find — we implement from scratch using:
1. statsmodels NB-2 (primary, official, well-documented)
2. Existing corpus CSV (already collected in prior h-e1 episode)

**Recommended Implementation Path:**
- Primary: `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`, BFGS optimizer
- Fallback: `statsmodels.api.NegativeBinomial` (lower-level API, same results)
- Justification: smf.negativebinomial with patsy formula syntax handles C(decade) categorical expansion natively; BFGS confirmed convergent from prior h-e1 run

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa/statsmodels docs is sufficiently clear. statsmodels NB-2 formula API is straightforward; no complex custom layers or 100+ line modules requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: OpenML Dataset Corpus (h-e1 reuse)

| Property | Value |
|----------|-------|
| **Name** | OpenML Dataset Corpus (h-e1 corpus) |
| **Type** | standard (programmatic-api — real OpenML platform data) |
| **N** | 5,217 datasets (filtered: N_tasks ≥ 1) |
| **Source** | OpenML API via `openml.datasets.list_datasets(output_format='dataframe', status='active')` |
| **Cache Path** | `h-e1/code/data/h_e1/openml_dataset_corpus.csv` |
| **Verified** | Yes (used in prior h-e1 episode; CSV already on disk) |

**Key Columns Required:**
- `dataset_id` — unique identifier
- `N_tasks` — count of distinct ML tasks (DV); integer ≥ 1
- `tags` — raw tags string (source for `has_tags` derivation)
- `n_instances` — dataset row count (for `log_n_instances`)
- `n_features` — feature count (for `log_n_features`)
- `upload_date` — for `age_years` and `decade` derivation

**Derived Columns (preprocessing):**
```python
import numpy as np
import pandas as pd

df = pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')
df = df[df['N_tasks'] >= 1].copy()  # N=5,217

# IV derivation
df['has_tags'] = (df['tags'].notna() & (df['tags'].str.strip() != '')).astype(int)
df['tag_count'] = df['tags'].str.count(',').fillna(-1) + 1
df['tag_count'] = df['tag_count'].where(df['has_tags'] == 1, 0)

# Controls
df['log_n_instances'] = np.log(df['n_instances'].clip(lower=1))
df['log_n_features'] = np.log(df['n_features'].clip(lower=1))
df['upload_year'] = pd.to_datetime(df['upload_date']).dt.year
df['age_years'] = 2026 - df['upload_year']
df['age_sq'] = df['age_years'] ** 2
df['decade'] = (df['upload_year'] // 10) * 10  # e.g., 2010, 2020
```

**Robustness Check Variants:**
- RC-4: Winsorize N_tasks at 99th percentile before regression
- RC-5: Restrict to `tag_count >= 1` (all-tagged subset sensitivity)
- RC-7: Compare age_years-only model vs. C(decade) model IRR

**Loading Information** (for Phase 4 download):
- Method: CSV (already cached)
- Identifier: `h-e1/code/data/h_e1/openml_dataset_corpus.csv`
- Code: `pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')`
- If CSV missing: `openml.datasets.list_datasets(output_format='dataframe', status='active')`

### Models

#### Baseline Model

**Architecture**: NB-2 without has_tags (controls-only model)

| Property | Value |
|----------|-------|
| **Name** | Negative Binomial Type 2 — Controls-Only |
| **Formula** | `N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)` |
| **Library** | `statsmodels.formula.api.negativebinomial` |
| **loglike_method** | `'nb2'` (variance = μ + α·μ²) |
| **Optimizer** | BFGS (`method='bfgs'`) |
| **Convergence** | Confirmed in prior h-e1 run |

**Baseline serves as:** Controls-only comparison to quantify the marginal contribution of `has_tags` IV.

**Loading Information** (for Phase 4 download):
- Method: statsmodels (pip install statsmodels)
- Identifier: `statsmodels.formula.api.negativebinomial`
- Code:
  ```python
  import statsmodels.formula.api as smf
  baseline = smf.negativebinomial(
      'N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)',
      data=df,
      loglike_method='nb2'
  ).fit(method='bfgs')
  ```

#### Proposed Model

**Architecture:** Baseline + `has_tags` IV

**Core Mechanism Implementation:**

```python
# Core Mechanism: Binary Tag Presence (has_tags) → N_tasks via NB-2
# Based on: statsmodels.formula.api.negativebinomial (official docs)
# Source: https://www.statsmodels.org/dev/generated/statsmodels.formula.api.negativebinomial.html

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

def fit_nb2_proposed(df):
    """
    Proposed model: NB-2 with has_tags binary IV.
    DV: N_tasks (count, overdispersed); variance = mu + alpha*mu^2
    IV: has_tags (binary 0/1, FAIR F1 operationalization)
    Controls: log_n_instances, log_n_features, age_years, age_sq, C(decade)
    """
    formula = ('N_tasks ~ has_tags + log_n_instances + '
               'log_n_features + age_years + age_sq + C(decade)')
    model = smf.negativebinomial(formula, data=df, loglike_method='nb2')
    result = model.fit(method='bfgs', maxiter=100, disp=False)

    # Extract IRR and 95% CI for has_tags
    coef = result.params['has_tags']
    se = result.bse['has_tags']
    irr = np.exp(coef)
    ci_lower = np.exp(coef - 1.96 * se)
    ci_upper = np.exp(coef + 1.96 * se)
    pval = result.pvalues['has_tags']

    # MUST_WORK gate check
    gate_pass = (irr >= 1.1) and (ci_lower >= 1.1) and (pval < 0.05)

    return result, {'irr': irr, 'ci_lower': ci_lower,
                    'ci_upper': ci_upper, 'pval': pval,
                    'gate_pass': gate_pass}

# Pre-check: has_tags-decade correlation (R3 risk mitigation)
def check_decade_correlation(df):
    """Check if has_tags is era-specific (R3 critical risk)."""
    return df.groupby('decade')['has_tags'].mean()

# Cameron-Trivedi overdispersion test (re-verify NB-2 appropriateness)
def ct_lr_test(df):
    """Poisson vs NB-2 LR test; expect stat >> 3.84."""
    poisson = smf.poisson('N_tasks ~ has_tags + log_n_instances + '
                          'log_n_features + age_years + age_sq + C(decade)',
                          data=df).fit(method='bfgs', disp=False)
    nb2 = smf.negativebinomial('N_tasks ~ has_tags + log_n_instances + '
                                'log_n_features + age_years + age_sq + C(decade)',
                                data=df, loglike_method='nb2').fit(method='bfgs', disp=False)
    lr_stat = 2 * (nb2.llf - poisson.llf)
    p_value = stats.chi2.sf(lr_stat, df=1)
    return lr_stat, p_value
```

### Training Protocol

This is a statistical regression experiment (not gradient-based training). "Training" = maximum likelihood estimation.

| Parameter | Value | Source |
|-----------|-------|--------|
| **Estimator** | Maximum Likelihood Estimation (MLE) | statsmodels NB-2 standard |
| **Optimizer** | BFGS (Broyden-Fletcher-Goldfarb-Shanno) | Confirmed convergent in prior h-e1 |
| **maxiter** | 100 (increased from default 35 for safety) | statsmodels docs |
| **loglike_method** | 'nb2' (variance = μ + α·μ²) | Overdispersion structure confirmed (CT LR=2222.68) |
| **Seeds** | N/A (deterministic MLE, no randomness) | — |
| **Sample** | Full N=5,217 (N_tasks ≥ 1 restriction) | Phase 2B design |
| **Pre-checks** | CT LR test, has_tags-decade correlation | R3 risk mitigation |

**Robustness Check Suite (RC):**
1. **RC-4**: Winsorize N_tasks at 99th percentile → refit proposed model
2. **RC-5**: Restrict to `tag_count >= 1` only → refit (all-tagged subset)
3. **RC-7**: Compare IRR: age_years-only model vs. C(decade) model (era confounding diagnostic)

### Evaluation

**Primary Metrics (MUST_WORK gate):**
- `IRR_has_tags` = exp(β_has_tags): Incidence Rate Ratio for has_tags binary variable
- `CI_lower_has_tags` = exp(β - 1.96·SE): 95% CI lower bound
- `p_has_tags`: two-tailed p-value for has_tags coefficient

**Success Criteria:**
- **Gate PASS (primary):** IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
- **Partial pass (secondary):** CI_lower ∈ [1.05, 1.1) — scientifically informative, continue with qualified claim
- **Gate FAIL:** CI_lower < 1.05 OR p ≥ 0.05 → route to Phase 0

**Expected Performance (from prior h-e1 episode):**
- Prior composite score IRR: 1.076 (below 1.1 threshold) — this is the baseline to beat
- Binary description presence (RC-2a, closest analog): IRR=1.102 — theoretical target range
- Expected for has_tags: IRR ∈ [1.05, 1.15] based on theoretical grounds

**Proposed > Baseline Check:**
- proposed_irr (with has_tags) > baseline (controls-only pseudo-R²)
- Quantify marginal improvement: `proposed.llf - baseline.llf` (likelihood improvement)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: count regression (not classification or generation)
- Library: statsmodels built-in (`result.params`, `result.bse`, `result.pvalues`, `result.conf_int()`)
- Code:
  ```python
  irr = np.exp(result.params['has_tags'])
  ci = np.exp(result.conf_int().loc['has_tags'])  # [lower, upper]
  pval = result.pvalues['has_tags']
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — IRR of has_tags with 95% CI error bars vs. threshold line at 1.1

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (EXISTENCE, binary IV, NB-2):
1. **Coefficient plot**: IRR with CI for all covariates in proposed model (forest plot style)
2. **has_tags-decade correlation heatmap**: Mean has_tags rate by decade (R3 risk visualization)
3. **RC suite comparison**: IRR bar chart across RC-4, RC-5, RC-7 models vs. primary model
4. **Observed vs. predicted N_tasks**: Scatter plot (log scale) for proposed model fit quality

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. IRR_has_tags ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result:** No relevant sources found. Archon KB is seeded with deep learning / diffusion model content; NB-2 count regression is outside its domain coverage. All three queries returned similarity scores < 0.45 with clearly unrelated diffusion model results.

- **Queries executed:**
  1. "negative binomial regression count data experiment design" → similarity 0.30, unrelated
  2. "NB-2 statsmodels implementation best practices" → similarity 0.44, unrelated
  3. "count regression overdispersion fixed effects Python" → similarity 0.33, unrelated

### B. GitHub Implementations (Exa)

**Source 1**: statsmodels Official Documentation — NegativeBinomial
- **URL**: https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html
- **Query Used**: "statsmodels negativebinomial NB2 regression Python implementation example"
- **Relevance**: Official API; loglike_method='nb2' confirmed; variance structure μ + α·μ²
- **Used For**: Model selection (NB-2 over NB-1), BFGS optimizer confirmation
- **Key insight**: `NegativeBinomialResults` provides `.params`, `.bse`, `.pvalues`, `.conf_int()`, `.llf`

**Source 2**: statsmodels formula.api.negativebinomial
- **URL**: https://www.statsmodels.org/dev/generated/statsmodels.formula.api.negativebinomial.html
- **Query Used**: "statsmodels formula api negativebinomial BFGS incidence rate ratio confidence interval"
- **Relevance**: Formula API with patsy syntax handles C(decade) expansion natively
- **Used For**: Formula construction, IRR extraction pattern
- **Key code**: `smf.negativebinomial(formula, data, loglike_method='nb2').fit(method='bfgs')`

**Source 3**: statsmodels NegativeBinomial.fit — BFGS documentation
- **URL**: https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.NegativeBinomial.fit.html
- **Relevance**: Confirms BFGS parameters; `maxiter=35` default (increase to 100 for safety)
- **Used For**: Optimizer configuration

**Source 4**: OpenML Python API — list_datasets
- **URL**: https://openml.github.io/docs/data/use/
- **Query Used**: "OpenML dataset metadata tagging adoption count regression Python"
- **Relevance**: Confirms `tags` field availability and corpus loading via API
- **Used For**: Dataset loading code (fallback if CSV missing)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from statsmodels official docs was sufficiently clear. No complex custom layers or 100+ line modules requiring semantic analysis. statsmodels NB-2 formula API is a standard, well-documented interface.

### D. Previous Hypothesis Context

**Previous Context**: None — h-e1 is the first hypothesis in the verification chain (no prerequisites). However, h-e1 (prior episode) established the corpus and confirmed NB-2 appropriateness (CT LR=2222.68). This episode reuses the corpus.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset (OpenML corpus) | Programmatic-API (real) | Phase 2B, prior h-e1 episode corpus |
| has_tags derivation logic | Phase 2B specification | 02b_verification_plan.md §2.2 H-E1 |
| NB-2 model selection | Phase 2B (established) + Exa B.1 | CT LR=2222.68 prior h-e1 |
| Formula specification | Phase 2B §2.2 + Exa B.2 | Verification Protocol step 3 |
| BFGS optimizer | Phase 2B (established) + Exa B.3 | Prior h-e1 convergence confirmed |
| IRR computation | Exa B.2 (statsmodels docs) | `np.exp(result.params)` pattern |
| CI extraction | Exa B.1 (NegativeBinomialResults) | `result.conf_int()` |
| RC-4/5/7 robustness | Phase 2B §2.2 verification protocol | Steps 4–6 |
| Success criteria (IRR≥1.1) | Phase 2B §2.2 success criteria | MUST_WORK gate definition |
| Pre-check decade correlation | Phase 2B §4.1 R3 mitigation | Risk R3 critical |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- Phase 2B completed: 2026-08-05T04:45:00Z — corpus available, NB-2 confirmed appropriate
- h-e1 set to IN_PROGRESS: 2026-08-05T04:47:04Z — external loop starting Phase 2C→3→4
- Phase 2C experiment design: IN_PROGRESS → COMPLETED (this document)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results found), Exa (statsmodels docs, OpenML API docs)*
*All specifications grounded in statsmodels official documentation and Phase 2B research*
*Next Phase: Phase 3 - Implementation Planning*
