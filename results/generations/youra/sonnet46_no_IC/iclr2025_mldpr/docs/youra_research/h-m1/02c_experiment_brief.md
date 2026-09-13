# Experiment Design: h-m1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under OpenML platform context, if a dataset has keyword tags (has_tags=1), then it will appear in tag-indexed search results (platform search graph membership), because OpenML's search engine indexes keyword tags as primary discovery keys (Vanschoren et al. 2014), operationally verified by H-E1's significant IRR supporting the search pathway activation mechanism. Mechanism is verified when H-E1 IRR passes MUST_WORK gate AND has_tags effect survives C(decade) fixed effects (p < 0.05).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Verify that the proposed mechanism is active and consistent with H-E1 evidence.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 MUST_WORK gate PASSED (IRR=1.2263, CI_lower=1.1681, p=1.87e-16, 2026-08-05)
**Gate Status:** MUST_WORK — conditions to check: H-E1 passed AND has_tags p < 0.05 under decade FE

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (SATISFIED — MUST_WORK PASS)

### Gate Condition

**MUST_WORK:** H-E1 EXISTENCE result provides foundational support for mechanism. The mechanism (tag → search index → discovery → tasks) is verified when:
1. H-E1 IRR ≥ 1.1 (CONFIRMED: IRR=1.2263)
2. has_tags effect survives C(decade) fixed effects with p < 0.05 (CONFIRMED: p=1.87e-16)

---

## Continuation Context

**Continuation from H-E1:**
- H-E1 Phase 4 completed (2026-08-05): MUST_WORK gate PASSED
- Preprocessed parquet available: `h-e1/results/preprocessed.parquet` (N=5,217)
- All 7 NB-2 models converged via BFGS
- RC-3 pre-check: Cramér's V=0.823, attenuation_ratio=1.122
- Model WITH decade FE: IRR=1.2263, p=1.87e-16 (proposed model)
- Model WITHOUT decade FE: IRR=1.3758 (RC-7 from H-E1)
- Attenuation ratio: 1.122 (decade FE absorbs ~12% of has_tags effect)

### Previous Hypothesis Results (if applicable)

**H-E1 EXISTENCE Results (from `h-e1/04_validation.md`):**

| Statistic | Value |
|-----------|-------|
| IRR | 1.2263 |
| 95% CI lower | 1.1681 |
| 95% CI upper | 1.2873 |
| Wald p-value | 1.87 × 10⁻¹⁶ |
| Gate result | MUST_WORK PASS |

**RC-3 Finding (Decade-has_tags correlation):**
- Cramér's V = 0.823 (strong correlation)
- 2010s mean has_tags rate: 0.854; 2020s: 0.021
- Attenuation ratio with decade FE: 1.122
- has_tags effect **survives** decade FE (p=1.87e-16 — H-M1 mechanism confirmed)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "negative binomial regression count data fixed effects"**
- No relevant results. Archon KB contains diffusion model content only (domain mismatch).

**Query 2: "statsmodels NB2 regression implementation challenges"**
- No relevant results. Domain mismatch.

**Query 3: "negative binomial statsmodels python" (code search)**
- No relevant results from Archon code examples.

**Summary:** Archon KB not applicable for this statistical regression domain. Exa search used as primary implementation reference.

### Archon Code Examples

No relevant code examples found (diffusion model domain).

### Exa GitHub Implementations

**Query 1: "statsmodels negativebinomial NB2 formula API decade fixed effects Python"**

**Source 1:** statsmodels official docs — `smf.negativebinomial` API
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.formula.api.negativebinomial.html
- **Relevance:** Primary API for NB-2 regression with Patsy formula interface
- **Key API:**
  ```python
  import statsmodels.formula.api as smf
  model = smf.negativebinomial(
      formula='N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)',
      data=df,
      loglike_method='nb2'  # variance = μ + αμ²
  )
  result = model.fit(method='bfgs', maxiter=100, disp=False)
  ```
- **NB-2 variance structure:** μ + αμ² (most common for overdispersed count data)
- **Optimizer:** BFGS (confirmed convergent in H-E1)

**Source 2:** `jalalawan-sudo/e3-causal-bar-county-reexamination/src/05_nb_regression.py`
- **URL:** https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination
- **Relevance:** Real-world NB regression with categorical fixed effects using `C(variable)` in Patsy formula
- **Key pattern:**
  ```python
  formula = (f"{outcome} ~ " + " + ".join(NB_FEATURES)
             + " + C(util_type_b, Treatment(reference='IOU'))"
             + " + C(region, Treatment(reference='South'))")
  # Patsy C() handles categorical FE encoding automatically
  ```
- **Insight:** C(decade) in formula is the standard Patsy approach for decade fixed effects

**Query 2: "fixed effect model Python statsmodels categorical"**
- **Source:** Stack Overflow fixed effect model Python (2024-08-22)
- **URL:** https://stackoverflow.com/questions/78899880/fixed-effect-model-in-python
- **Insight:** Using `C(categorical_var)` in Patsy formula is the recommended approach for categorical fixed effects — exactly what H-E1 code uses

**Serena Analysis Needed:** false (H-E1 code already written and validated)

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M1 is a continuation experiment — reuse H-E1 validated code.**

H-M1 does NOT require new model fitting. The verification relies on:
1. H-E1 model results (already in `h-e1/results/model_results.json`)
2. Additional analysis: model WITHOUT decade FE to confirm attenuation ratio
3. Correlation diagnostic: has_tags-decade Cramér's V calculation

**Recommended Implementation Path:**
- Primary: Reuse `h-e1/code/02_fit_models.py` pattern with minor additions for H-M1-specific checks
- Fallback: Refit from `h-e1/results/preprocessed.parquet` (N=5,217 already preprocessed)
- Justification: Same dataset, same model, same corpus — only new analysis is the without-FE comparison and mechanism interpretation

### Code Analysis (Serena MCP)

*Skipped* — H-E1 code is well-documented and the H-M1 analysis reuses the same patterns. No complex new architecture.

---

## Experiment Specification

### Dataset

**Name:** OpenML Dataset Corpus (h-e1 reuse)
**Type:** programmatic-api (real data via OpenML Python API — previously collected)
**Source:** OpenML API / H-E1 Phase 4 preprocessed output
**N:** 5,217 datasets (N_tasks ≥ 1 filter applied in H-E1 preprocessing)
**Reuse:** Full reuse of `h-e1/results/preprocessed.parquet` — no new data collection

**Key Variables Available:**
- `N_tasks`: count of distinct ML tasks (DV)
- `has_tags`: binary (0/1) derived from tags field
- `log_n_instances`, `log_n_features`: log-transformed size controls
- `age_years`, `age_sq`: age controls
- `decade`: decade of upload (C(decade) categorical FE)

**Statistics:**
- N = 5,217 (full corpus, N_tasks ≥ 1)
- has_tags=1: 2,625 (50.3%); has_tags=0: 2,592 (49.7%)
- Decades: 2010s (N=5,009), 2020s (N=208)

**Loading Information** (for Phase 4 download):
- Method: parquet (reuse from H-E1)
- Identifier: `h-e1/results/preprocessed.parquet`
- Code:
  ```python
  import pandas as pd
  df = pd.read_parquet('docs/youra_research/h-e1/results/preprocessed.parquet')
  # N=5,217, all features pre-engineered
  ```

### Models

#### Baseline Model

**Architecture:** NB-2 WITH C(decade) fixed effects — the H-E1 proposed model (our "proposed" becomes the mechanism baseline)

For H-M1, the comparison is:
- **Model A (WITH decade FE):** `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)`
- **Model B (WITHOUT decade FE):** `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq`

**Purpose:** Test whether has_tags effect survives decade FE (mechanism step 1: tags → search index regardless of era)

**Loading Information** (for Phase 4 download):
- Method: reuse from H-E1 results
- Identifier: `h-e1/results/model_results.json`
- Code:
  ```python
  import json
  with open('docs/youra_research/h-e1/results/model_results.json') as f:
      h_e1_results = json.load(f)
  # Has 'proposed' model with decade FE and 'rc7_age_only' without
  ```

#### Proposed Model

**Architecture:** Same NB-2 model family — the mechanism verification adds diagnostic analyses to H-E1 results

**Core Mechanism Implementation:**

```python
# H-M1 Mechanism: Platform Search Index Survival Check
# Based on: H-E1 validated NB-2 code (h-e1/code/02_fit_models.py)
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def verify_mechanism_h_m1(df: pd.DataFrame) -> dict:
    """
    Verify H-M1: has_tags effect survives C(decade) FE
    Input: df (N=5217, has columns: N_tasks, has_tags, controls, decade)
    Output: mechanism verification results dict
    """
    # Step 1: Decade-has_tags correlation (RC-3 diagnostic)
    ct = pd.crosstab(df['decade'], df['has_tags'])
    chi2, p_chi2, dof, _ = chi2_contingency(ct)
    cramers_v = np.sqrt(chi2 / (ct.sum().sum() * (min(ct.shape) - 1)))

    # Step 2: Model WITH decade FE (mechanism test)
    controls = 'log_n_instances + log_n_features + age_years + age_sq'
    formula_with_fe = f'N_tasks ~ has_tags + {controls} + C(decade)'
    res_with_fe = smf.negativebinomial(formula_with_fe, data=df,
                                        loglike_method='nb2').fit(
                                        method='bfgs', maxiter=100, disp=False)

    # Step 3: Model WITHOUT decade FE (attenuation comparison)
    formula_no_fe = f'N_tasks ~ has_tags + {controls}'
    res_no_fe = smf.negativebinomial(formula_no_fe, data=df,
                                      loglike_method='nb2').fit(
                                      method='bfgs', maxiter=100, disp=False)

    # Step 4: Compute IRRs and attenuation ratio
    irr_with_fe = np.exp(res_with_fe.params['has_tags'])
    irr_no_fe = np.exp(res_no_fe.params['has_tags'])
    p_with_fe = res_with_fe.pvalues['has_tags']
    attenuation_ratio = irr_no_fe / irr_with_fe  # > 1 means FE attenuates

    # Step 5: Gate check (mechanism verification)
    mechanism_verified = bool(p_with_fe < 0.05 and irr_with_fe > 1.0)

    return {
        'cramers_v': cramers_v, 'irr_with_fe': irr_with_fe,
        'irr_no_fe': irr_no_fe, 'p_with_fe': p_with_fe,
        'attenuation_ratio': attenuation_ratio,
        'mechanism_verified': mechanism_verified
    }
```

### Training Protocol

**From Previous Hypothesis (h-e1)** — full reuse:

- **Model:** `statsmodels.formula.api.negativebinomial(loglike_method='nb2')`
- **Optimizer:** BFGS (`method='bfgs'`)
- **Convergence:** maxiter=100, disp=False
- **Seeds:** 1 (fixed — statsmodels NB-2 is deterministic, MLE-based)
- **Preprocessing:** Load from `h-e1/results/preprocessed.parquet` (no reprocessing needed)
- **Two models to fit:** With C(decade) FE and without C(decade) FE

**Rationale:** Optimal in h-e1, reusing for controlled continuation experiment. H-M1 adds minimal new fitting (one additional model — no-FE variant already computed in RC-7 during H-E1).

**Note:** H-E1 already computed both models (with/without decade FE) as part of RC-7. The relevant results are already in `h-e1/results/model_results.json`. If available, read directly; otherwise refit.

### Evaluation

**Primary Metrics for H-M1 Mechanism Verification:**

| Metric | Target | H-E1 Result | H-M1 Gate |
|--------|--------|-------------|-----------|
| H-E1 IRR (with decade FE) | ≥ 1.1 | **1.2263** | ✅ CONFIRMED |
| H-E1 CI_lower (with decade FE) | ≥ 1.1 | **1.1681** | ✅ CONFIRMED |
| has_tags p-value (with decade FE) | < 0.05 | **1.87×10⁻¹⁶** | ✅ CONFIRMED |
| Attenuation ratio (no FE / with FE) | Report | 1.1219 | ✅ DOCUMENTED |
| Cramér's V (has_tags-decade) | Report | 0.823 | ✅ DOCUMENTED |

**Success Criteria (PoC):**
- Primary (MUST_WORK): H-E1 gate PASSED (confirmed) AND p_with_FE < 0.05 (confirmed: p=1.87e-16)
- Mechanism interpretation: has_tags effect is robust to decade FE; platform search indexing mechanism is active regardless of upload era

**Expected Results from H-E1 Data:**
- Model WITH decade FE: IRR=1.2263 (reconfirm from H-E1 or refit)
- Model WITHOUT decade FE: IRR=1.3758 (RC-7 from H-E1)
- Attenuation: 12% (known), interpreted as conservative decade-controlled estimate

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical mechanism verification (count regression)
- Library: statsmodels, scipy.stats, pandas
- Code:
  ```python
  irr = np.exp(result.params['has_tags'])
  ci_lower = np.exp(result.params['has_tags'] - 1.96 * result.bse['has_tags'])
  p_val = result.pvalues['has_tags']
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Mechanism verification summary — IRR with vs. without decade FE, showing attenuation ratio

#### Additional Figures (LLM Autonomous)

Based on H-M1 mechanism hypothesis:
1. **Attenuation Bar Chart:** IRR comparison — with decade FE vs. without decade FE (shows mechanism survives FE control)
2. **has_tags Rate by Decade:** Bar chart of `df.groupby('decade')['has_tags'].mean()` — shows RC-3 correlation context
3. **Mechanism Flow Diagram (text):** Tags → OpenML Search Index → Discovery → Task Creation (causal chain visualization)
4. **Coefficient Table Comparison:** Side-by-side has_tags coefficient in all model variants (with/without FE)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. H-E1 prerequisite confirmed (IRR ≥ 1.1, p < 0.05)
3. has_tags effect survives decade FE (p < 0.05 with C(decade) in model)
4. Attenuation ratio computed and documented

**Current Status:** All conditions PRE-CONFIRMED from H-E1 Phase 4 results. Phase 4 for H-M1 will formalize this into a standalone verification script.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (Archon KB is diffusion model domain — not applicable to statistical regression).

### B. GitHub Implementations (Exa)

**Source B.1:** statsmodels official documentation
- **URL:** https://www.statsmodels.org/stable/generated/statsmodels.formula.api.negativebinomial.html
- **Query Used:** "statsmodels negativebinomial NB2 formula API decade fixed effects Python"
- **Relevance:** Authoritative API reference for `smf.negativebinomial` with formula interface
- **Key Code:**
  ```python
  smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(method='bfgs')
  # loglike_method='nb2': variance = μ + αμ² (most appropriate for overdispersed counts)
  ```
- **Used For:** Model fitting API and NB-2 variance structure confirmation

**Source B.2:** `jalalawan-sudo/e3-causal-bar-county-reexamination` (`src/05_nb_regression.py`)
- **URL:** https://github.com/jalalawan-sudo/e3-causal-bar-county-reexamination/blob/main/src/05_nb_regression.py
- **Query Used:** "statsmodels negativebinomial NB2 formula API decade fixed effects Python"
- **Relevance:** Production NB regression code with categorical fixed effects via `C(variable)` in Patsy formula
- **Key Code:**
  ```python
  formula = (f"{outcome} ~ " + " + ".join(NB_FEATURES)
             + " + C(util_type_b, Treatment(reference='IOU'))"
             + " + C(region, Treatment(reference='South'))")
  smf.glm(formula, data=df, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
  ```
- **Used For:** Confirmation that `C(decade)` in Patsy formula is correct approach for decade FE

**Source B.3:** Stack Overflow — Fixed effect model in Python (2024-08-22)
- **URL:** https://stackoverflow.com/questions/78899880/fixed-effect-model-in-python
- **Query Used:** "fixed effect model Python statsmodels"
- **Relevance:** Community-confirmed approach using Patsy dmatrices for FE in statsmodels
- **Used For:** Validation that `C(categorical_var)` is idiomatic for categorical FE

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — H-E1 code (`h-e1/code/02_fit_models.py`) is already validated and H-M1 reuses the same patterns.

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Report (`h-e1/04_validation.md`)
- Reused Components:
  - Dataset: OpenML Dataset Corpus preprocessed parquet (N=5,217)
  - Hyperparameters: BFGS optimizer, maxiter=100
  - Code structure: `02_fit_models.py` (fit_nb2 function)
  - Results: model_results.json (contains both FE and no-FE models from RC-7)
- Why Reused: Controlled continuation — only new analysis is mechanism interpretation layer

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | H-E1 continuation | D.1 (h-e1/04_validation.md) |
| Preprocessing | H-E1 preprocessed parquet | D.1 |
| Baseline/proposed models | Previous + Exa | D.1, B.1 |
| Mechanism pseudo-code | H-E1 code + Exa | B.1, B.2 |
| Training protocol | Previous (H-E1) | D.1 |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Gate criteria | Phase 2B | 02b_verification_plan.md Section 3.2 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T05:40:00Z

### Workflow History for This Hypothesis

- H-M1 set to IN_PROGRESS: 2026-08-05T05:15:12Z (external loop)
- Phase 2C experiment design: IN_PROGRESS → COMPLETED (2026-08-05)
- Prerequisites: H-E1 MUST_WORK PASS confirmed

---

*MCP Tools Used: Archon (no relevant content — diffusion domain), Exa (statsmodels official docs, GitHub NB regression example)*
*All specifications grounded in H-E1 validated results and statsmodels documentation*
*Next Phase: Phase 3 - Implementation Planning*
