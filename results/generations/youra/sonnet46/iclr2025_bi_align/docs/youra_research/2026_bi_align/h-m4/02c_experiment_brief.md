# Experiment Design: h-m4

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** PM-score proxy (chosen/rejected preference) positively predicts C_sem^H←A (beta > 0, p < 0.05) after controlling for surface-feature controls (response length, bullet/list structure, politeness marker density, syntactic complexity), because the epistemic quality encoded in RLHF training drives accommodation above and beyond formatting signals.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m1 (VALIDATED, MUST_WORK PASS), h-m2 (VALIDATED, SHOULD_WORK PASS), h-m3 (FAILED, SHOULD_WORK FAIL — proceeding with reduced causal claim: no within-prompt Δ support)
**Gate Status:** SHOULD_WORK — β_PM > 0 and p < 0.05 in full mediation model with surface-feature controls

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (MUST_WORK PASS), h-m2 (SHOULD_WORK PASS), h-m3 (SHOULD_WORK FAIL)

### Gate Condition
**SHOULD_WORK:** β_PM > 0 and p < 0.05 in full mediation model with surface-feature controls (response_length, bullet_density, politeness_freq, syntactic_complexity + tier).
If Fail: Document mechanism as formatting-driven rather than epistemic; publish existence + tier + directional asymmetry results with mechanism caveat.

---

## Continuation Context

This is a continuation experiment (4th in chain), building on h-m1/h-m2/h-m3.

**Proven from prior hypotheses:**
- C_sem^H←A > 0: confirmed (h-e1, C_sem=0.3292, d=1.998)
- Tier monotonicity: confirmed (h-m1, J-T p=0.001, d=0.18–0.25 across all 3 SBERT models)
- Directional asymmetry H←A > A←H: confirmed (h-m2, 3/3 models × 3/3 tiers, p<0.05)
- Within-prompt Δ-cosine probe: FAILED (h-m3, Δ<0 in 25/27 tier×op; H_next more similar to rejected, d up to -0.74)

**H-m3 failure impact on H-m4:**
- H-m4 proceeds with reduced causal claim
- Tests: Does PM-score proxy predict C_sem above surface-feature controls at tier-aggregate level?
- This is a between-conversation regression (not within-prompt), orthogonal to h-m3's within-prompt test

### Previous Hypothesis Results (if applicable)
- **Reused hyperparameters from h-m1/h-m2:** bootstrap_resamples=1000, seed=42, knn_k=5, significance_level=0.05
- **h-m2 C_sem values (MiniLM):** H←A = [0.0853, 0.0923, 0.0876] across tiers; A←H = [0.0395, 0.0535, 0.0718]
- **Code reuse:** sbert_encoder.py, c_sem_calculator.py, data_loader.py from h-m1/h-m2 codebase
- **Critical note from h-m3:** bootstrap uses `rng.choice` (not `rng.integers`)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Queries Executed:** 5
**Relevant Results:** 0 (all Archon KB content is diffusion model domain; no semantic accommodation/NLP/regression content)

**Query 1:** "OLS regression surface feature mediation NLP" → 0 relevant (diffusion models)
**Query 2:** "PM score RLHF quality prediction regression" → 0 relevant (diffusion models)
**Query 3:** "semantic accommodation conversation analysis regression" → 0 relevant (diffusion models)
**Query 4:** "statsmodels OLS regression mediation" → 0 relevant (diffusion/image models)
**Query 5:** "SBERT cosine similarity bootstrap pandas" → 0 relevant (diffusion/image models)

**Fallback:** Specifications derived from Phase 2B verification protocol + prior hypothesis validated codebase (h-m1/h-m2) + standard statsmodels.api documentation practices.

### Archon Code Examples

**Queries Executed:** 2
**Relevant Results:** 0 (diffusion model code only)

Specifications grounded in: statsmodels.api OLS documentation, scipy.stats standard practices, prior h-m1/h-m2 validated codebase, Phase 2B verification protocol Section H-M4.

### Exa GitHub Implementations

**Status:** Unavailable (HTTP 402) — consistent with all prior Phase 2C runs in this pipeline (h-e1, h-m1, h-m2, h-m3).

**Fallback approach:** Specifications derived from:
1. Phase 2B verification protocol (02b_verification_plan.md, Section H-M4)
2. Prior validated codebase (h-m1/h-m2/h-m3 code/) — reusable SBERT pipeline
3. Standard statsmodels/scipy practices for OLS mediation analysis

### 🎯 Implementation Priority Assessment

**This is an analytical pipeline extension, not a paper reproduction experiment.**

Implementation priority hierarchy for h-m4:
1. **Reuse validated h-m2 codebase** (HIGHEST PRIORITY) — SBERT embeddings, C_sem computation, tier stratification already validated
2. **Extend with surface-feature extraction module** — new code needed for response feature computation
3. **Add OLS mediation regression module** — new code using statsmodels.api

**Recommended Implementation Path:**
- Primary: Extend h-m2 codebase (h-m2/code/) with PM-proxy construction + surface-feature extraction + OLS regression
- Fallback: Build from h-m1 codebase with additional feature engineering
- Justification: Controlled comparison — only adding PM-proxy regression layer; all C_sem computation identical to h-m2

### Code Analysis (Serena MCP)

*Skipped* — Analytical pipeline extending h-m1/h-m2/h-m3. No complex model architecture; OLS regression with statsmodels is a standard, well-documented operation. No custom layers or unfamiliar patterns requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Anthropic/hh-rlhf (helpful-base, helpful-rejection-sampled, helpful-online)
**Type:** standard
**Source:** HuggingFace datasets
**Cache:** `/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf` (verified from h-m1/h-m2/h-m3)

**Statistics:**
- Total: ~273,617 conversation turns across 3 splits
- helpful-base: ~43,835 conversations (train + test)
- helpful-rejection-sampled: ~44,037 conversations (train + test)
- helpful-online: ~22,384 conversations (train + test)
- Each conversation: multi-turn, each turn = (human, AI) pair
- Chosen/rejected pairs: verified ≥14,426 per tier (from h-m3 empirical check), used for PM-proxy construction

**Preprocessing:**
- Parse raw HH-RLHF format: extract `(H_{t+1}, A_t)` adjacent pairs per conversation
- Tier assignment: based on data_dir split (helpful-base=T1, helpful-rejection-sampled=T2, helpful-online=T3)
- Filter: drop pairs where either turn is empty or < 5 tokens
- SBERT encoding: batch_size=256, device=CPU (consistent with h-m1/h-m2)
- No fine-tuning; inference-only

**Augmentation:** None (observational study)

**PM-proxy construction:**
- Source: chosen/rejected pairs in HH-RLHF format
- `pm_proxy` = binary {0=rejected, 1=chosen} mapped to quality (chosen=higher PM-score)
- For each paired conversation: both branches (chosen + rejected) share the same prompt/context
- Extract `A_t` response text from chosen and rejected branches separately
- Compute C_sem^H←A for responses from each branch
- Join: each (conversation_id, branch) observation has both C_sem value and pm_proxy label
- Final dataset: N rows × (tier, pm_proxy, C_sem, response_length, bullet_density, politeness_freq, ttr, mean_sent_len)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"Anthropic/hh-rlhf"`
- Code:
  ```python
  from datasets import load_dataset
  ds_base = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")
  ds_rs   = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-rejection-sampled")
  ds_online = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-online")
  # Cache verified at: .data_cache/datasets/hh-rlhf
  ```

### Models

#### Baseline Model

**Architecture:** all-MiniLM-L6-v2 (primary SBERT model)
**Type:** sentence-transformers (pre-trained, inference-only)
**Role:** Encode conversation turns to compute C_sem^H←A per conversation branch
**Configuration:**
- Input: raw text utterance (string)
- Output: 384-dimensional L2-normalized sentence embedding
- Batch: 256 utterances per batch
- Device: CPU (consistent with h-e1/h-m1/h-m2/h-m3)

**Robustness models:**
- paraphrase-MiniLM-L6-v2 (384-dim)
- all-mpnet-base-v2 (768-dim)

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers
- Identifier: `"all-MiniLM-L6-v2"`, `"paraphrase-MiniLM-L6-v2"`, `"all-mpnet-base-v2"`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer
  model_primary  = SentenceTransformer('all-MiniLM-L6-v2')
  model_para     = SentenceTransformer('paraphrase-MiniLM-L6-v2')
  model_mpnet    = SentenceTransformer('all-mpnet-base-v2')
  ```

#### Proposed Model

**Architecture:** Baseline SBERT pipeline + PM-proxy regression layer + surface-feature extraction

**Core Mechanism:** OLS Mediation Regression — tests whether PM-score proxy (chosen/rejected) predicts C_sem^H←A above surface-feature controls

**Core Mechanism Implementation:**

```python
# Core Mechanism: PM-Score OLS Mediation Regression
# Based on: statsmodels.api OLS + Phase 2B verification protocol
# Purpose: Test β_PM > 0 after controlling for surface features

import statsmodels.api as sm
import numpy as np

def extract_surface_features(response_text: str) -> dict:
    """Extract surface-level formatting features from AI response."""
    words = response_text.split()
    sentences = response_text.split('.')
    word_count = len(words)
    # bullet/list density: fraction of lines starting with - or *
    lines = response_text.split('\n')
    bullet_density = sum(1 for l in lines if l.strip().startswith(('-', '*', '•'))) / max(len(lines), 1)
    # politeness markers
    politeness_tokens = {'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'}
    politeness_freq = sum(1 for w in words if w.lower() in politeness_tokens) / max(word_count, 1)
    # type-token ratio (lexical diversity)
    ttr = len(set(words)) / max(word_count, 1)
    mean_sent_len = word_count / max(len([s for s in sentences if s.strip()]), 1)
    return {'length': word_count, 'bullet_density': bullet_density,
            'politeness_freq': politeness_freq, 'ttr': ttr,
            'mean_sent_len': mean_sent_len}

def run_mediation_ols(df, c_sem_col='c_sem', pm_col='pm_proxy',
                      surface_cols=None, tier_col='tier'):
    """Full mediation OLS: C_sem ~ PM + surface_features + tier."""
    if surface_cols is None:
        surface_cols = ['length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
    # Encode tier as dummy (T1=ref)
    tier_dummies = pd.get_dummies(df[tier_col], prefix='tier', drop_first=True)
    X_cols = [pm_col] + surface_cols
    X = pd.concat([df[X_cols], tier_dummies], axis=1)
    X = sm.add_constant(X)
    y = df[c_sem_col]
    model = sm.OLS(y, X).fit(cov_type='HC3')  # heteroscedasticity-robust SE
    beta_pm = model.params[pm_col]
    p_pm    = model.pvalues[pm_col]
    return model, beta_pm, p_pm

# Gate: beta_pm > 0 AND p_pm < 0.05
```

### Training Protocol

**No neural network training** — this is a statistical regression study.

**Reused from h-m1/h-m2 (controlled comparison):**
- bootstrap_resamples: 1000
- bootstrap_seed: 42
- knn_k: 5 (matched-shuffle baseline)
- significance_level: 0.05
- min_n_pairs: 1000 per tier

**Regression Protocol:**
- **Step 1 (PM-only model):** `C_sem ~ PM_proxy + tier` → get β_PM_reduced
- **Step 2 (Full model):** `C_sem ~ PM_proxy + response_length + bullet_density + politeness_freq + ttr + mean_sent_len + tier` → get β_PM_full, p_PM_full
- **Step 3 (Robustness check):** Replace PM_proxy with tier_rank (ordinal 1/2/3); confirm tier effect also survives controls
- **Step 4 (Mediation proportion):** Compute `(β_PM_reduced - β_PM_full) / β_PM_reduced` → fraction mediated by surface features
- **Heteroscedasticity:** Use HC3 robust standard errors (White correction)
- **Observation unit:** Per (conversation_id, branch) pair — one row per chosen/rejected response
- **N expected:** ~28,000–70,000 observations per model (2 branches × pairs per tier)

**Seeds:** 1 (fixed, seed=42 for bootstrap and matched-shuffle)

**Loss Function:** N/A (OLS analytical solution, no gradient descent)

**Optimizer:** N/A (closed-form OLS)

### Evaluation

**Task Type:** Regression (observational mediation analysis)

**Primary Metrics:**
- **β_PM (full model):** OLS coefficient for PM_proxy in full mediation model — main gate criterion
- **p_PM (full model):** Two-tailed p-value for β_PM under HC3 robust SE
- **β_PM_reduced vs β_PM_full:** Ratio reveals how much surface features mediate the PM→C_sem relationship
- **R² (full model):** Variance explained by full model (diagnostic, not gate criterion)
- **β_PM robustness:** β_PM across 3 SBERT models (primary + paraphrase + mpnet)

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** β_PM > 0 AND p_PM < 0.05 in full model with surface-feature controls
- **Secondary:** β_PM does not shrink to zero when surface features added (|β_PM_full / β_PM_reduced| > 0.5)
- **Robustness:** β_PM direction consistent across ≥2/3 SBERT models

**Failure Interpretation:**
- If β_PM ≤ 0 or p_PM ≥ 0.05: PM-score effect fully mediated by surface features → formatting hypothesis supported
- If β_PM > 0 and p_PM < 0.05: Epistemic quality drives accommodation above formatting → epistemic hypothesis supported

**Expected Effect Size (from prior validated hypotheses):**
- C_sem^H←A mean ≈ 0.085–0.092 per tier (from h-m2 MiniLM)
- PM-proxy β expected small but positive if epistemic quality hypothesis holds
- No prior benchmark for exact β_PM magnitude (first regression test in this pipeline)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: observational regression
- Library: `statsmodels.api`, `scipy.stats`, `pandas`, `numpy`
- Code:
  ```python
  import statsmodels.api as sm
  model = sm.OLS(y, X).fit(cov_type='HC3')
  beta_pm = model.params['pm_proxy']
  p_pm    = model.pvalues['pm_proxy']
  gate_pass = (beta_pm > 0) and (p_pm < 0.05)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** β_PM (full model) with 95% CI across 3 SBERT models (bar chart with error bars)

#### Additional Figures (LLM Autonomous)
Based on this regression/mediation analysis, the following additional figures are appropriate:

1. **Mediation decomposition bar chart:** β_PM_reduced vs β_PM_full per model — shows surface feature mediation proportion
2. **Coefficient plot (forest plot):** All OLS coefficients (PM_proxy + 5 surface features + tier dummies) with 95% CI per model
3. **Scatter plot:** C_sem^H←A vs PM_proxy (chosen=1 / rejected=0) per tier, with regression line overlay
4. **Partial regression plot:** C_sem residuals (after surface features) vs PM_proxy residuals — direct epistemic effect visualization
5. **Tier × PM interaction:** C_sem by tier × branch (chosen/rejected) grouped bar chart

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | OLS regression is supported by statsmodels; PM-proxy available from HH-RLHF chosen/rejected structure | TRUE |
| Mechanism Isolatable | PM-proxy coefficient can be isolated by including/excluding surface features (two-model comparison) | TRUE |
| Baseline Measurable | PM-only model (Step 1) provides baseline β_PM before surface-feature controls | TRUE |

### Architecture Compatibility Check

**Compatibility:** Full — OLS regression has no architectural constraints.
- **Required components:** statsmodels.api, pandas DataFrame with C_sem + pm_proxy + surface features
- **Required data:** HH-RLHF chosen/rejected pairs verified ≥14,426 per tier (from h-m3)
- **Incompatible architectures:** N/A (statistical model, not neural)

> ⚠️ Pre-check: Verify N_pairs ≥ 1000 per tier before running regression (empirically confirmed in h-m3: ≥14,426 per tier).

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `"OLS fit complete: beta_PM={val:.4f}, p={val:.4f}"` | regression.py:run_mediation_ols() |
| Coefficient Sign | β_PM_full > 0 (positive PM effect after controls) | model.params['pm_proxy'] |
| Metric Delta | β_PM_full > 0 AND p < 0.05 → gate PASS | evaluate.py:check_gate() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(model_result, beta_pm, p_pm):
    """Verify OLS mediation mechanism actually runs and produces valid output."""
    indicators = {
        "model_fitted": model_result is not None,
        "beta_pm_nonzero": abs(beta_pm) > 1e-10,
        "p_value_valid": 0.0 <= p_pm <= 1.0,
        "n_obs_sufficient": model_result.nobs >= 1000,
        "surface_controls_included": all(
            col in model_result.model.exog_names
            for col in ['length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
        )
    }
    all_ok = all(indicators.values())
    return all_ok, indicators

# Gate evaluation
def check_gate(beta_pm, p_pm, significance_level=0.05):
    gate_pass = (beta_pm > 0) and (p_pm < significance_level)
    return gate_pass, {
        "beta_pm_positive": beta_pm > 0,
        "p_significant": p_pm < significance_level,
        "beta_pm_value": beta_pm,
        "p_value": p_pm
    }
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| β_PM ≤ 0 | model.params['pm_proxy'] ≤ 0 | FAIL: PM not positive predictor |
| p_PM ≥ 0.05 | model.pvalues['pm_proxy'] ≥ 0.05 | FAIL: Effect not significant |
| Surface features fully mediate | β_PM_full ≈ 0 while β_PM_reduced > 0 | FAIL: Formatting mechanism |
| Regression singularity | statsmodels rank deficiency warning | FAIL: Feature collinearity |
| N_pairs < 1000 | len(df) < 1000 per tier | FAIL: Insufficient data |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 5 verify_mechanism_activated indicators = True | Log/coefficient check |
| β_PM Positive | β_PM > 0 | model.params['pm_proxy'] |
| Statistical Significance | p_PM < 0.05 (HC3 robust) | model.pvalues['pm_proxy'] |
| Hypothesis Supported | β_PM > 0 AND p < 0.05 in ≥2/3 SBERT models | Cross-model check |

**Hypothesis Support Threshold:** β_PM > 0 AND p_PM < 0.05 in full model with HC3 robust SE, consistent across ≥2/3 SBERT models
**Hypothesis Support Metric:** model.params['pm_proxy'] (sign + significance after surface controls)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** 0 relevant results across 5 queries (Archon KB contains diffusion model content only)

**Queries executed:**
1. "OLS regression surface feature mediation NLP" → irrelevant (diffusion models)
2. "PM score RLHF quality prediction regression" → irrelevant (diffusion models)
3. "semantic accommodation conversation analysis regression" → irrelevant (diffusion models)
4. "statsmodels OLS regression mediation" → irrelevant (image/diffusion models)
5. "SBERT cosine similarity bootstrap pandas" → irrelevant (image/diffusion models)

### Archon Code Examples

**Status:** 0 relevant results across 2 queries (diffusion model code only)

### B. GitHub Implementations (Exa)

**Status:** Unavailable (HTTP 402) — all Phase 2C runs in this pipeline affected.

**Specifications grounded in instead:**
- statsmodels.api OLS documentation (standard practice)
- Phase 2B verification protocol (02b_verification_plan.md, Section H-M4)
- Prior validated codebase: h-m1/h-m2/h-m3 code/ (SBERT pipeline, C_sem, bootstrap)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from prior validated hypotheses (h-m1/h-m2/h-m3) is clear and well-understood. OLS regression is standard statsmodels operation requiring no semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — h-m1, h-m2, h-m3

**Reused Components:**
- **Dataset cache:** `/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf` — verified stable
- **SBERT pipeline:** batch_size=256, CPU, all-MiniLM-L6-v2 primary
- **C_sem computation:** matched-shuffle baseline, knn_k=5
- **Bootstrap:** rng.choice (NOT rng.integers — critical note from h-m3)
- **Hyperparameters:** seed=42, bootstrap_resamples=1000, significance_level=0.05
- **IPW correction:** KS-triggered inverse probability weighting (from h-m1 — apply if distribution shift detected)

**Why Reused:** Enables controlled comparison — only adds PM-proxy + surface-feature extraction + OLS regression on top of proven h-m2 codebase. All C_sem computation is identical.

**h-m3 failure lesson for h-m4:**
- Within-prompt Δ was falsified — H_next more similar to rejected in SBERT space
- H-m4 tests a DIFFERENT mechanism: between-conversation tier-aggregate regression, orthogonal to within-prompt probe
- h-m3 failure does NOT invalidate h-m4's approach

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset selection | Phase 2B protocol + h-m1/h-m2/h-m3 validation | 02b_verification_plan.md §H-M4 |
| PM-proxy construction | Phase 2B protocol | 02b_context.md §Variables |
| SBERT encoding | Prior validation | h-m1/h-m2 code/sbert_encoder.py |
| C_sem computation | Prior validation | h-m1/h-m2 code/c_sem_calculator.py |
| Surface feature extraction | Standard NLP practice | statsmodels docs + Phase 2B §H-M4 |
| OLS regression | statsmodels.api standard | Phase 2B verification protocol |
| HC3 robust SE | Econometrics standard (White correction) | Phase 2B §H-M4 verification protocol |
| Hyperparameters | Prior validation (h-m1/h-m2) | 04_validation.md h-m1, h-m2 |
| Bootstrap (rng.choice) | Critical fix from h-m3 | h-m3 code/ |
| Gate criterion (β>0, p<0.05) | Phase 2B | 02b_context.md §Success Criteria |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T15:30:00Z

### Workflow History for This Hypothesis
- h-m1: VALIDATED (MUST_WORK PASS) — J-T p=0.001, C_sem monotonically increases with tier
- h-m2: VALIDATED (SHOULD_WORK PASS) — C_sem^H←A > C_sem^A←H in all 9 tier×model cells
- h-m3: FAILED (SHOULD_WORK FAIL) — Δ-cosine within-prompt probe falsified; H_next closer to rejected
- h-m4: IN_PROGRESS — PM-proxy OLS mediation regression above surface-feature controls

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — 0 relevant), Exa (GitHub — unavailable 402), Serena (skipped — analytical pipeline)*
*All specifications grounded in: Phase 2B protocol + prior validated codebase (h-m1/h-m2/h-m3)*
*Next Phase: Phase 3 - Implementation Planning*
