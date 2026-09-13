# Experiment Design: h-m2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under OpenML context (has_tags=1 subset, N~2,625), if a dataset has more keyword tags (higher log(tag_count+1)), then it will have more registered ML tasks (N_tasks), because more tags create more search pathways leading to higher discovery probability, with NB-2 IRR for log(tag_count+1) having 95% CI lower >= 1.05 and p < 0.05.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Tests dose-response effect of tag count above binary threshold.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (MUST_WORK PASS, IRR=1.2263), H-M1 COMPLETED (MUST_WORK PASS, attenuation_ratio=1.122)
**Gate Status:** SHOULD_WORK (informative negative acceptable)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (COMPLETED), h-m1 (COMPLETED)

### Gate Condition

SHOULD_WORK: IRR_P2 95% CI lower >= 1.05 AND p < 0.05 in NB-2 fitted on has_tags=1 subset with IV=log(tag_count+1). Failure is scientifically informative (binary threshold is the full FAIR F1 signal).

---

## Continuation Context

**Previous Hypothesis Results (H-E1 and H-M1):**

H-E1 established: IRR=1.2263 (95% CI: [1.1681, 1.2873]), p=1.87e-16 for has_tags binary IV. NB-2 highly appropriate (CT LR=7356.36). Cramér's V=0.823 for decade-has_tags correlation; attenuation_ratio=1.122 (decade FE absorbs 12.2% of effect). N=5,217 with has_tags=1: 50.3% (N~2,625).

H-M1 established: has_tags survives C(decade) FE with p=1.87e-16; mechanism support STRONG. Attenuation documented but non-fatal.

**Reuse from previous:**
- Dataset: OpenML corpus CSV reused (h-e1/code/data/h_e1/openml_dataset_corpus.csv)
- Preprocessed parquet: h-e1/results/preprocessed.parquet (has feature engineering already done)
- Optimizer: BFGS confirmed convergent for this corpus
- Controls: log_n_instances, log_n_features, age_years, age_sq, C(decade) — same as H-E1/H-M1

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "negative binomial regression tag count continuous predictor count data"**
- No relevant results. Archon KB contains diffusion model / image generation domain content (UniPC, LCM, Lumina-T2X). Zero relevance to count regression or OpenML metadata analysis.

**Query 2: "statsmodels negativebinomial log transformation predictor NB2"**
- No relevant results. Same diffusion model domain mismatch.

**Conclusion:** Archon KB not relevant for this statistical experiment domain. Proceeding with Exa/statsmodels official documentation.

### Archon Code Examples

**Query: "NB-2 count regression subset analysis statsmodels"**
- No relevant code examples found (diffusion domain mismatch).

### Exa GitHub Implementations

**Query 1: "statsmodels smf.negativebinomial log transformed predictor subset Python"**

**Source 1: statsmodels official documentation (statsmodels.org)**
- URL: https://www.statsmodels.org/dev/generated/statsmodels.formula.api.negativebinomial.html
- Relevance: HIGHEST — canonical API for our exact model class
- Key API: `smf.negativebinomial(formula, data, subset=None)` — subset parameter supports boolean array for filtering
- loglike_method='nb2': Variance = μ + αμ² (Greene 2008) — confirmed appropriate
- fit(method='bfgs'): confirmed convergent for our corpus in H-E1

**Source 2: jalalawan-sudo/e3-causal-bar-county-reexamination (GitHub)**
- URL: https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination/blob/main/src/05_nb_regression.py
- Relevance: HIGH — real-world NB-2 regression with log-transformed predictors (log_pop, log_bldg, log_bb, etc.) and categorical fixed effects (C(util_type_b), C(region)) — structurally analogous to our formula
- Key pattern: log-transformed covariates as array of feature names, smf.glm with NegativeBinomial family
- IRR computation: `np.exp(b)`, CI via `np.exp(ci.loc[name, 0])` / `np.exp(ci.loc[name, 1])` — exact pattern we use
- Training config: BFGS optimizer via smf.negativebinomial(...).fit(method='bfgs')
- Their approach: log10 transformation with floor=1; we use natural log: log(tag_count+1)

**Serena Analysis Needed:** false (code is sufficiently clear from official docs + GitHub example)

### 🎯 Implementation Priority Assessment

This experiment is a continuation from H-E1/H-M1 — NOT a paper reproduction experiment.

**Recommended Implementation Path:**
- Primary: Direct statsmodels smf.negativebinomial with subset restriction (df_tagged = df[df.has_tags==1])
- Fallback: Full formula with has_tags==1 boolean mask passed to subset= parameter
- Justification: H-E1 code infrastructure (preprocess.py, fit_models.py pattern) provides the exact template. H-M2 is a minimal extension: filter to has_tags=1, derive log(tag_count+1), refit NB-2.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. This is a continuation experiment reusing H-E1 infrastructure with minimal modifications (subset filter + new IV).

---

## Experiment Specification

### Dataset

**Name:** OpenML Dataset Corpus — Tagged Subset (has_tags=1)
**Type:** standard (programmatic-api, reuse from H-E1)
**Source:** OpenML API via openml-python; cached at h-e1/code/data/h_e1/openml_dataset_corpus.csv

**Statistics:**
- Full corpus: N=5,217 (N_tasks ≥ 1, confirmed in H-E1)
- Tagged subset (has_tags=1): N≈2,625 (50.3% of corpus, confirmed in H-E1 validation)
- tag_count distribution: min=1 (by definition, has_tags=1 means ≥1 tag); max unknown (to be reported at runtime)
- Derived IV: log_tag_count_p1 = log(tag_count + 1); tag_count derived as tags.str.count(',') + 1

**Sample Restriction:**
- Filter: `df_tagged = df[df['has_tags'] == 1]`
- Rationale: Removes zero-tag datasets to isolate continuous dose-response above binary threshold; eliminates collinearity between log(tag_count+1) and has_tags

**Loading Information** (for Phase 4 download):
- Method: CSV reuse (no download needed)
- Identifier: h-e1/code/data/h_e1/openml_dataset_corpus.csv OR h-e1/results/preprocessed.parquet
- Code:
```python
import pandas as pd
import numpy as np

# Option A: Load from preprocessed parquet (preferred — has_tags already derived)
df = pd.read_parquet('h-e1/results/preprocessed.parquet')
df_tagged = df[df['has_tags'] == 1].copy()

# Option B: Load from raw CSV
df = pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')
df['has_tags'] = df['tags'].apply(lambda x: 1 if (pd.notna(x) and str(x).strip() != '') else 0)
df_tagged = df[df['has_tags'] == 1].copy()

# Derive continuous IV
df_tagged['tag_count'] = df_tagged['tags'].str.count(',') + 1
df_tagged['log_tag_count_p1'] = np.log(df_tagged['tag_count'] + 1)

print(f"Tagged subset N={len(df_tagged)}")
print(f"tag_count stats: {df_tagged['tag_count'].describe()}")
print(f"log_tag_count_p1 stats: {df_tagged['log_tag_count_p1'].describe()}")
```

### Models

#### Baseline Model

**Architecture:** NB-2 controls-only (no tag count IV) — tagged subset
**Purpose:** Establishes counterfactual adoption rate for tagged datasets without tag count effect
**Formula:** `N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)`
**Data:** df_tagged (has_tags=1 subset, N≈2,625)

**Loading Information** (for Phase 4 download):
- Method: statsmodels smf.negativebinomial (no pretrained model)
- Identifier: N/A (fit from scratch on df_tagged)
- Code:
```python
import statsmodels.formula.api as smf

baseline_formula = 'N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)'
baseline_model = smf.negativebinomial(
    baseline_formula, data=df_tagged, loglike_method='nb2'
).fit(method='bfgs', disp=False)
print(f"Baseline LLF={baseline_model.llf:.2f}, AIC={baseline_model.aic:.2f}")
```

#### Proposed Model

**Architecture:** NB-2 with log(tag_count+1) IV — tagged subset

**Core Mechanism Implementation:**

```python
# Core Mechanism: Tag Count Dose-Response (H-M2)
# Based on: statsmodels official docs + H-E1 NB-2 pattern
# IV: log_tag_count_p1 = log(tag_count + 1)
# Sample: has_tags=1 subset (N≈2,625)

import statsmodels.formula.api as smf
import numpy as np

def fit_hm2_model(df_tagged: pd.DataFrame):
    """
    NB-2 with continuous tag-count IV on tagged-only subset.
    Args:
        df_tagged: DataFrame filtered to has_tags==1
    Returns:
        result: fitted NegativeBinomialResults
    """
    formula = ('N_tasks ~ log_tag_count_p1 '
               '+ log_n_instances + log_n_features '
               '+ age_years + age_sq + C(decade)')

    result = smf.negativebinomial(
        formula, data=df_tagged, loglike_method='nb2'
    ).fit(method='bfgs', disp=False)

    # Extract IRR and CI for IV
    irr = np.exp(result.params['log_tag_count_p1'])
    ci = result.conf_int()
    ci_lower = np.exp(ci.loc['log_tag_count_p1', 0])
    ci_upper = np.exp(ci.loc['log_tag_count_p1', 1])
    p_val = result.pvalues['log_tag_count_p1']

    return result, {'IRR': irr, 'CI_lower': ci_lower,
                    'CI_upper': ci_upper, 'p': p_val}

# Integration: standalone NB-2, no prior model reuse needed
# Gate check: IRR_P2 >= 1.05 AND CI_lower >= 1.05 AND p < 0.05
```

### Training Protocol

**Reusing from H-E1 (optimal, confirmed convergent):**

- **Optimizer:** BFGS (`method='bfgs'`) — confirmed convergent for OpenML corpus in H-E1 (all 7 models)
- **Dispersion:** loglike_method='nb2' — confirmed appropriate (CT LR=7356.36 >> 3.84)
- **Convergence:** disp=False (suppress iteration output), maxiter default (35)
- **Seeds:** N/A — NB-2 MLE is deterministic (no stochastic optimization)
- **Loss:** Negative log-likelihood (maximized automatically by statsmodels)
- **Regularization:** None (standard MLE)

**Collinearity Pre-check (MANDATORY before model fit):**
```python
# Check tag_count-decade correlation in tagged subset
from scipy.stats import spearmanr
decade_numeric = df_tagged['decade'].astype(int)
rho, p = spearmanr(df_tagged['log_tag_count_p1'], decade_numeric)
print(f"Spearman rho(log_tag_count_p1, decade)={rho:.3f}, p={p:.3e}")

# Also report mean tag count by decade
print(df_tagged.groupby('decade')['tag_count'].agg(['mean','median','count']))
```

**Source:** H-E1 Phase 4 validation (confirmed BFGS convergence); statsmodels official docs

### Evaluation

**Primary Metrics:**
- IRR_P2 = exp(coef['log_tag_count_p1']) — incidence rate ratio for 1-unit increase in log(tag_count+1)
- CI_lower_P2 = exp(conf_int.loc['log_tag_count_p1', 0]) — 95% CI lower bound
- CI_upper_P2 = exp(conf_int.loc['log_tag_count_p1', 1]) — 95% CI upper bound
- p_value_P2 = pvalues['log_tag_count_p1'] — Wald p-value

**Success Criteria (SHOULD_WORK gate):**
- PASS: IRR_P2 CI_lower >= 1.05 AND p < 0.05 → dose gradient confirmed
- INFORMATIVE NEGATIVE: CI_lower < 1.05 → binary threshold is the full FAIR F1 signal (document, do not re-route)

**Secondary Diagnostics:**
- Attenuation ratio for tagged subset: IRR without C(decade) / IRR with C(decade)
- Overdispersion check: CT LR test on tagged subset (expect similar overdispersion to full corpus)
- Sample size confirmation: N (tagged subset) reported explicitly

**Expected Performance Range (from research):**
- IRR_P2: Expected in range 1.05–1.20 if dose-response exists (based on H-E1 IRR=1.23 for binary threshold)
- If CI_lower < 1.05: Informative null consistent with FAIR F1 operating as 0/1 gate

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: count regression (not classification/ranking)
- Library: statsmodels (results object provides params, pvalues, conf_int directly)
- Code:
```python
def evaluate_gate(result, gate_irr_lower=1.05, gate_p=0.05):
    irr = np.exp(result.params['log_tag_count_p1'])
    ci = result.conf_int()
    ci_lower = np.exp(ci.loc['log_tag_count_p1', 0])
    p_val = result.pvalues['log_tag_count_p1']

    passed = (ci_lower >= gate_irr_lower) and (p_val < gate_p)
    return {
        'gate': 'SHOULD_WORK',
        'passed': passed,
        'IRR': round(irr, 4),
        'CI_lower': round(ci_lower, 4),
        'p_value': float(p_val),
        'result': 'PASS' if passed else 'INFORMATIVE_NEGATIVE'
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart with IRR_P2, CI_lower_P2, CI_upper_P2 vs. gate threshold (1.05)

#### Additional Figures (LLM Autonomous)

Recommended based on MECHANISM hypothesis type:
1. **Fig 1: Tag Count Distribution** — Histogram of tag_count in has_tags=1 subset; log scale on x-axis if skewed
2. **Fig 2: log(tag_count+1) vs log(N_tasks) scatter** — partial regression plot controlling for confounders (added variable plot)
3. **Fig 3: IRR comparison across models** — Forest plot showing IRR for log_tag_count_p1 with/without decade FE (attenuation check)
4. **Fig 4: Mean N_tasks by tag count decile** — Non-parametric dose-response visualization (raw data pattern)

**Output Location:** `docs/youra_research/h-m2/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on df_tagged (N≈2,625)
2. IRR_P2 95% CI lower >= 1.05 AND p < 0.05

**Informative Negative Condition:**
1. Code runs without error
2. CI_lower < 1.05 OR p >= 0.05 → binary threshold captures full FAIR F1 effect; document and proceed to H-M3

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Finding:** No relevant content in Archon KB. KB indexed for diffusion model / image generation domain (UniPC, HuggingFace diffusers, Lumina-T2X). Queries for NB-2 count regression and statsmodels returned diffusion model results with similarity scores ~0.35 (below relevance threshold).

### B. GitHub Implementations (Exa)

**Source 1: statsmodels official documentation**
- URL: https://www.statsmodels.org/dev/generated/statsmodels.formula.api.negativebinomial.html
- Query: "statsmodels smf.negativebinomial log transformed predictor subset Python"
- Relevance: HIGHEST — canonical API reference
- Key API confirmed:
  - `smf.negativebinomial(formula, data, subset=None, loglike_method='nb2')`
  - `.fit(method='bfgs', maxiter=35)`
  - loglike_method='nb2': variance = μ + αμ² (Greene 2008)
- Used For: Formula specification, optimizer choice, IRR computation

**Source 2: jalalawan-sudo/e3-causal-bar-county-reexamination (GitHub)**
- URL: https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination/blob/main/src/05_nb_regression.py
- Query: "statsmodels negativebinomial log transformed covariates categorical fixed effects Python"
- Relevance: HIGH — structurally analogous NB-2 with log-transformed features and categorical fixed effects
- Key code pattern:
```python
# Their IRR extraction pattern (adopted for H-M2):
ci = model.conf_int()
for name, b, p in zip(model.params.index, model.params.values, model.pvalues.values):
    irr = np.exp(b)
    ci_lo = np.exp(ci.loc[name, 0])
    ci_hi = np.exp(ci.loc[name, 1])
```
- Used For: IRR/CI computation pattern, coefficient table structure

### C. Code Analysis (Serena)

*Skipped* — Code from search results was sufficiently clear. H-E1 existing codebase (fit_models.py, evaluate_gate.py) provides the exact template for H-M2 with minimal modifications.

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Report (docs/youra_research/h-e1/04_validation.md)
**Source:** H-M1 Phase 4 Validation Report (docs/youra_research/h-m1/04_validation.md)

**Reused Components:**
- Dataset: OpenML corpus CSV + preprocessed.parquet — proven stable, N=5,217 confirmed
- Optimizer: BFGS — all 7 H-E1 models converged; reliable for this corpus
- Controls: log_n_instances, log_n_features, age_years, age_sq, C(decade) — optimal specification
- CT LR test: NB-2 confirmed appropriate (LR=7356.36) — no need to retest on subset (expected to hold)
- IRR computation: np.exp(params) + np.exp(conf_int) pattern — validated in H-E1

**Why Reused:** Enables controlled experiment — only IV changes (binary has_tags → continuous log(tag_count+1)) and sample restriction (has_tags=1 subset). All other components identical for methodological continuity.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B / H-E1 cache | 02b_verification_plan.md §H-M2; h-e1/code/data/ |
| Subset restriction (has_tags=1) | Phase 2B protocol | 02b_verification_plan.md H-M2 Verification Protocol step 1 |
| IV: log(tag_count+1) derivation | Phase 2B protocol | 02b_verification_plan.md H-M2 step 2 |
| NB-2 formula | H-E1 validated pattern | h-e1/04_validation.md + statsmodels docs |
| BFGS optimizer | H-E1 confirmed convergent | h-e1/04_validation.md (all 7 models converged) |
| IRR/CI computation | GitHub + H-E1 | jalalawan-sudo repo + h-e1 evaluate_gate.py |
| Gate threshold (CI_lower ≥ 1.05) | Phase 2B success criteria | 02b_verification_plan.md H-M2 Success Criteria |
| Figures pattern | H-E1/H-M1 precedent | h-e1/figures/, h-m1/figures/ |
| Collinearity pre-check | Phase 2B risk R3 | 02b_verification_plan.md §Risk R3 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T05:50:00Z

### Workflow History for This Hypothesis

- h-m2 IN_PROGRESS: 2026-08-05T05:38:06Z (external loop trigger)
- Phase 2C experiment design: IN_PROGRESS → COMPLETED (2026-08-05)
- Prerequisites confirmed: H-E1 PASS, H-M1 PASS

---

*MCP Tools Used: Archon (no relevant content — diffusion domain), Exa (statsmodels official docs + GitHub NB-2 example), Serena (skipped — code clear)*
*All specifications grounded in H-E1 validated infrastructure + statsmodels official documentation*
*Next Phase: Phase 3 - Implementation Planning*
