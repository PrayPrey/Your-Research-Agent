# Product Requirements Document: H-M4 PM-Score OLS Mediation Regression

**Hypothesis:** H-M4
**Title:** PM-Score Proxy Predicts C_sem^H←A Above Surface-Feature Controls (OLS Mediation Analysis)
**Pipeline Phase:** 3 — Implementation Planning
**Date:** 2026-03-15
**Gate Type:** SHOULD_WORK
**Task Tier:** FULL (Budget: 30 tasks)
**Base Hypothesis:** h-m1 (INCREMENTAL)

---

## 1. Executive Summary

H-M4 tests whether PM-score proxy (chosen/rejected RLHF preference label) **positively predicts** human semantic accommodation toward AI (C_sem^H←A = β > 0, p < 0.05) **after controlling for surface-level formatting features** (response length, bullet/list density, politeness marker frequency, syntactic complexity). This is an OLS mediation regression study at the between-conversation tier-aggregate level.

The core question: Is the relationship between RLHF quality and human accommodation driven by **epistemic content quality** (PM-score), or is it fully explained by **surface formatting signals** (length, bullet density, politeness markers, lexical diversity)?

This hypothesis is orthogonal to H-M3's failed within-prompt Δ-cosine probe: H-M4 operates at the tier-aggregate regression level (between-conversation), not within-prompt pairwise comparison.

```
H-E1: C_sem > 0 (VALIDATED ✅)
  └─ H-M1: tier-monotonicity (VALIDATED ✅)
       └─ H-M2: C_sem^H←A > C_sem^A←H (VALIDATED ✅)
            └─ H-M3: within-prompt Δ > 0 (FAILED ✗) — surface formatting drives within-prompt similarity
                 └─ H-M4: β_PM > 0 after surface controls [THIS WORK] — epistemic quality mechanism specificity
```

**Success Criterion (SHOULD_WORK Gate):** β_PM > 0 AND p_PM < 0.05 in full OLS model with HC3 robust SE, consistent across ≥2/3 SBERT models.

---

## 2. Research Context and Motivation

### 2.1 Position in Hypothesis Chain

H-M4 is the final mechanism-specificity test in the causal chain:
- H-E1 confirmed semantic accommodation exists (C_sem = 0.3292, d = 1.998)
- H-M1 confirmed tier-monotonicity (J-T p=0.001, Cohen d=0.18–0.25 across 3 models)
- H-M2 confirmed directional asymmetry H←A > A←H (3/3 models × 3/3 tiers)
- H-M3 FAILED to confirm within-prompt Δ-cosine probe (Δ < 0 in 25/27 cells; H_next more similar to rejected — unexpected finding)

H-M4 tests a **different causal pathway**: Does the RLHF preference score (PM-proxy: chosen=1 / rejected=0) predict C_sem above surface-level formatting signals? This asks whether **epistemic quality** (not just response formatting) drives accommodation.

### 2.2 Scientific Rationale

H-M3's failure revealed that within-prompt cosine similarity favors rejected responses in SBERT space — potentially because rejected responses use more informal, conversational language that semantically overlaps with human follow-up text. This doesn't rule out that PM-score quality drives accommodation at the tier-aggregate level via a different mechanism.

H-M4's regression approach:
- Uses **between-conversation** comparisons (not within-prompt pairwise)
- Controls for surface features that H-M3 showed may dominate SBERT similarity
- Tests whether RLHF quality effect survives when formatting confounds are partialed out
- Consistent with Danescu-Niculescu-Mizil et al.'s (2011) power-asymmetry framework

### 2.3 Continuation from Prior Validated Codebase

**Reused from h-m1/h-m2 (controlled comparison):**
- SBERT encoding pipeline (sbert_encoder.py)
- C_sem computation (c_sem_calculator.py, matched-shuffle baseline, knn_k=5)
- Data loader (data_loader.py, HH-RLHF cache verified)
- Bootstrap (rng.choice — critical: NOT rng.integers, per h-m3 fix)
- Hyperparameters: seed=42, bootstrap_resamples=1000, significance_level=0.05

**New for h-m4:**
- PM-proxy construction from chosen/rejected pairs
- Surface-feature extraction module
- OLS mediation regression with HC3 robust SE
- Two-stage regression analysis (PM-only → full model)

---

## 3. Functional Requirements

### 3.1 Data Requirements

| Requirement | Detail |
|-------------|--------|
| **Dataset** | Anthropic/hh-rlhf (HuggingFace) |
| **Splits** | helpful-base (T1), helpful-rejection-sampled (T2), helpful-online (T3) |
| **Pair structure** | Each sample: `{chosen: str, rejected: str}` — full conversation with paired AI responses |
| **Parsing** | Extract H_next (last human turn), A_t from both chosen and rejected branches |
| **Chosen/rejected pairs** | ≥14,426 per tier (empirically verified in h-m3) |
| **Cache** | `.data_cache/datasets/hh-rlhf` (verified from h-m1/h-m2/h-m3) |
| **Observation unit** | Per (conversation_id, branch) pair — one row per chosen/rejected response |
| **Expected N** | ~28,000–70,000 rows per SBERT model (2 branches × pairs per tier) |

### 3.2 PM-Proxy Construction

| Requirement | Detail |
|-------------|--------|
| **PM-proxy label** | Binary: chosen=1 (higher PM-score), rejected=0 (lower PM-score) |
| **Mapping** | Each (conversation_id, branch) row gets pm_proxy ∈ {0, 1} |
| **Join** | Merge pm_proxy with C_sem and surface features per row |
| **Final columns** | `tier`, `pm_proxy`, `c_sem`, `response_length`, `bullet_density`, `politeness_freq`, `ttr`, `mean_sent_len` |

### 3.3 Surface-Feature Extraction Requirements

Five surface features extracted from AI response text (A_t):

| Feature | Formula | Purpose |
|---------|---------|---------|
| `response_length` | `len(words)` | Controls for length advantage of chosen responses |
| `bullet_density` | `Σ(lines starting '-','*','•') / total_lines` | Detects list/structured formatting |
| `politeness_freq` | `Σ(words in politeness_set) / word_count` | Detects politeness markers |
| `ttr` | `len(unique_words) / word_count` | Lexical diversity (type-token ratio) |
| `mean_sent_len` | `word_count / sentence_count` | Syntactic complexity proxy |

Politeness token set: `{'please', 'thank', 'sorry', 'appreciate', 'certainly', 'happy'}`

### 3.4 OLS Regression Requirements

#### Stage 1: PM-Only Model (Baseline)
```
C_sem ~ β_0 + β_PM × pm_proxy + β_T2 × tier_T2 + β_T3 × tier_T3
```
- Purpose: Establish β_PM baseline before surface controls
- Produces: β_PM_reduced, p_PM_reduced

#### Stage 2: Full Mediation Model (Gate Model)
```
C_sem ~ β_0 + β_PM × pm_proxy
       + β_len × response_length
       + β_bul × bullet_density
       + β_pol × politeness_freq
       + β_ttr × ttr
       + β_msl × mean_sent_len
       + β_T2 × tier_T2 + β_T3 × tier_T3
```
- Standard errors: HC3 (heteroscedasticity-robust, White correction)
- Tier encoding: dummy variables, T1 (helpful-base) = reference
- Produces: β_PM_full, p_PM_full, R², all coefficients with CIs

#### Stage 3: Robustness Check
- Replace pm_proxy with tier_rank (ordinal 1/2/3)
- Confirm tier effect also survives surface-feature controls
- Report tier_rank β and p-value

#### Stage 4: Mediation Proportion
```
mediation_ratio = (β_PM_reduced - β_PM_full) / β_PM_reduced
```
- Reports fraction of PM→C_sem effect mediated by surface features
- Secondary check: |β_PM_full / β_PM_reduced| > 0.5

### 3.5 Multi-Model Robustness Requirements

Run full regression pipeline for each SBERT model:
- all-MiniLM-L6-v2 (primary)
- paraphrase-MiniLM-L6-v2 (robustness)
- all-mpnet-base-v2 (robustness)

Gate: β_PM_full > 0 AND p < 0.05 in ≥2/3 models.

### 3.6 Mechanism Activation Verification

For each model's OLS fit, verify:

| Indicator | Check |
|-----------|-------|
| `model_fitted` | OLS model result is not None |
| `beta_pm_nonzero` | `|β_PM| > 1e-10` |
| `p_value_valid` | `0.0 ≤ p_PM ≤ 1.0` |
| `n_obs_sufficient` | `model.nobs ≥ 1000` |
| `surface_controls_included` | All 5 surface features in model exog_names |

### 3.7 Visualization Requirements

| Figure | Description | Priority |
|--------|-------------|----------|
| **Fig 1** | β_PM (full model) with 95% CI across 3 SBERT models (bar chart + error bars) | MANDATORY |
| **Fig 2** | Mediation decomposition: β_PM_reduced vs β_PM_full per model | MANDATORY |
| **Fig 3** | Coefficient forest plot: all OLS coefficients per model with 95% CI | MANDATORY |
| **Fig 4** | Scatter: C_sem vs PM_proxy (chosen/rejected) per tier with regression line | AUTONOMOUS |
| **Fig 5** | Partial regression plot: C_sem residuals vs PM_proxy residuals | AUTONOMOUS |
| **Fig 6** | Tier × PM interaction: C_sem by tier × branch (grouped bar) | AUTONOMOUS |

All figures saved to `h-m4/figures/`.

### 3.8 Output Requirements

| Output | Path | Description |
|--------|------|-------------|
| Main results | `h-m4/results/regression_results.json` | All OLS coefficients, p-values, gate evaluation per model |
| Figures | `h-m4/figures/` | 6 figures (3 mandatory, 3 autonomous) |
| Validation report | `h-m4/04_validation.md` | Gate result, key findings |
| Checkpoint | `h-m4/04_checkpoint.yaml` | Phase 4 task tracking |

---

## 4. Technical Constraints

### 4.1 Codebase Reuse (INCREMENTAL from h-m1, base_hypothesis=h-m1)

| Module | Location | Reuse Strategy |
|--------|----------|----------------|
| `data_loader.py` | `h-m1/code/` or `h-m2/code/` | Reuse HH-RLHF loader; extend with chosen/rejected branch handling |
| `sbert_encoder.py` | `h-m1/code/` or `h-m2/code/` | Reuse batch encoding (batch_size=256, CPU) |
| `c_sem_calculator.py` | `h-m1/code/` or `h-m2/code/` | Reuse matched-shuffle C_sem computation (knn_k=5) |
| `statistics.py` | `h-e1/code/` or `h-m1/code/` | Reuse bootstrap_ci (rng.choice — NOT rng.integers) |

**New modules required:**
- `h-m4/code/surface_features.py` — Extract 5 surface-feature measures from response text
- `h-m4/code/regression.py` — run_mediation_ols(), HC3 robust SE, 4-stage regression protocol
- `h-m4/code/evaluate.py` — check_gate(), verify_mechanism_activated(), gate_summary report
- `h-m4/code/run_experiment.py` — Main entry point, orchestrates full pipeline for all 3 SBERT models
- `h-m4/code/visualize.py` — 6 figures generation

### 4.2 Hyperparameters (Reused from h-m1/h-m2, no changes)

```python
BATCH_SIZE = 256
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_SEED = 42
KNN_K = 5
SIGNIFICANCE_LEVEL = 0.05
MIN_N_PAIRS = 1000  # Pre-condition check per tier
```

### 4.3 Environment

- Python ≥ 3.8
- sentence-transformers ≥ 2.2.0
- datasets (HuggingFace)
- statsmodels ≥ 0.14.0
- pandas, scipy, numpy
- matplotlib, seaborn
- Single GPU/CPU (consistent with h-m1/h-m2/h-m3; experiments run on CPU for SBERT)
- Reuse existing conda/venv from h-m1/h-m2

### 4.4 Critical Implementation Notes

| Note | Description |
|------|-------------|
| `rng.choice` | Use `rng.choice` for bootstrap (NOT `rng.integers`) — per h-m3 fix |
| HC3 robust SE | `sm.OLS(y, X).fit(cov_type='HC3')` — required for heteroscedasticity |
| Tier dummies | T1 (helpful-base) = reference category, use `pd.get_dummies(drop_first=True)` |
| H-M3 failure context | H-M4 is between-conversation regression — orthogonal to h-m3's within-prompt probe |
| IPW correction | Apply KS-triggered IPW from h-m1 if distribution shift detected across branches |

---

## 5. Success Criteria

### 5.1 Gate Evaluation (SHOULD_WORK)

**Primary gate:** β_PM_full > 0 AND p_PM_full < 0.05 in ≥2/3 SBERT models

**Secondary gate:** |β_PM_full / β_PM_reduced| > 0.5 (PM effect not fully mediated by surface features)

| Outcome | Interpretation | Action |
|---------|---------------|--------|
| **PASS** | β_PM > 0, p < 0.05, ≥2/3 models | Epistemic quality drives accommodation above formatting |
| **FAIL (β≤0)** | PM-proxy negatively or non-predictive | Formatting hypothesis supported |
| **FAIL (p≥0.05)** | Effect not significant after surface controls | Accommodation fully formatting-driven |
| **PARTIAL (1/3 models)** | Weak/inconsistent evidence | Document as inconclusive, formatting alternative |

**Failure interpretation (if gate fails):**
"PM-score effect on C_sem fully mediated by surface-feature controls (formatting hypothesis). Accommodation mechanism driven by response length/structure rather than epistemic quality."

### 5.2 Expected Effect

- C_sem^H←A ≈ 0.085–0.092 per tier (from h-m2 MiniLM)
- β_PM_full: small positive if epistemic hypothesis holds; ≈0 or negative if formatting dominates
- No prior benchmark for exact β magnitude — first regression test in this pipeline

---

## 6. Implementation Phases (Epic Structure)

### Phase A: Environment + Data Setup
- Verify h-m2/h-m1 code availability and copy/link reusable modules
- Set up h-m4 code directory structure
- Verify data cache (hh-rlhf already downloaded for h-m1/h-m2/h-m3)
- Implement chosen/rejected pair parser (extract H_next, A_chosen, A_rejected, pm_proxy)
- Validate N_pairs ≥ 1000 per tier (pre-condition check)

### Phase B: Surface-Feature Extraction
- Implement `surface_features.py` with all 5 features
- Unit tests for each feature extractor (edge cases: empty text, single word, no bullets)
- Batch processing for all conversation branches
- Validate feature distributions (no NaN, reasonable ranges)

### Phase C: C_sem Computation with PM-proxy
- Extend data_loader to handle chosen/rejected branch structure
- Compute C_sem for each (conversation_id, branch) pair using h-m2 pipeline
- Build regression DataFrame: (tier, pm_proxy, c_sem, 5 surface features)
- Validate DataFrame: check for nulls, N per tier

### Phase D: OLS Regression Pipeline
- Implement `regression.py` with 4-stage protocol (PM-only, full, robustness, mediation)
- HC3 robust SE enforcement
- Implement `evaluate.py` with gate check + mechanism activation verification
- Per-model regression (3 SBERT models)

### Phase E: Multi-Model Robustness + Gate Evaluation
- Run pipeline for paraphrase-MiniLM-L6-v2
- Run pipeline for all-mpnet-base-v2
- Cross-model consistency check: ≥2/3 gate criterion
- Generate regression_results.json with full coefficients

### Phase F: Visualization + Reporting
- 3 mandatory figures: β_PM bar chart, mediation decomposition, forest plot
- 3 autonomous figures: scatter, partial regression, tier×PM interaction
- 04_validation.md generation with full gate result + key findings
- Checkpoint archiving

### Phase G: Integration + Failsafe
- End-to-end pipeline run (all splits, all models)
- Error handling: singularity check, N_pairs < 1000 warning
- Graceful degradation if statsmodels convergence issues
- Checkpoint and results JSON saved

---

## 7. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PM-proxy fully mediated by surface features | Medium | FAIL gate | Report as formatting hypothesis supported; publish existence + tier + directional asymmetry results with mechanism caveat |
| Feature multicollinearity (length × ttr) | Low-Medium | Unstable coefficients | Check VIF; report condition number; HC3 handles heteroscedasticity |
| Regression singularity | Low | FAIL | Validate feature rank before fitting; log statsmodels rank deficiency warnings |
| H-M3's reverse finding affects h-m4 | No | None | h-m4 is orthogonal (between-conversation, not within-prompt) |
| SBERT cache miss | Low | Delay | Re-encode with h-m2's verified pipeline |
| N_pairs < 1000 any tier | Very Low | Gate flag | Empirically confirmed ≥14,426 per tier in h-m3 |

---

## 8. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| H-E1 code (statistics.py, accommodation.py) | ✅ VALIDATED | Reuse bootstrap_ci, cohens_d |
| H-M1 code (data_loader.py, run_experiment.py) | ✅ VALIDATED | Reuse SBERT pipeline, adapt for chosen/rejected |
| H-M2 code (bidirectional, c_sem for both directions) | ✅ VALIDATED | Reference C_sem values; use same encoding |
| HH-RLHF dataset cache | ✅ Available | `.data_cache/datasets/hh-rlhf` |
| SBERT models (3) | ✅ Available | `~/.cache/huggingface/hub/sentence-transformers` |
| statsmodels ≥ 0.14.0 | ✅ Standard | OLS with HC3 robust SE |

---

## 9. Out of Scope

- Neural network training of any kind
- Fine-tuning SBERT models
- Cross-dataset generalization (focused on HH-RLHF)
- Within-prompt Δ analysis (that was H-M3, which failed)
- Implementing causal mediation analysis (Baron-Kenny or do-calculus) — OLS regression is sufficient for this gate
- RLHF training pipeline

---

## 10. Acceptance Criteria Summary

| Criterion | Requirement |
|-----------|-------------|
| Code runs end-to-end | ✅ No crash, full results for all 3 SBERT models |
| N_pairs ≥ 1000 verified | ✅ Empirically confirmed per tier (≥14,426 from h-m3) |
| Surface features extracted | ✅ All 5 features per AI response |
| OLS fits complete | ✅ 4-stage protocol per model, HC3 robust SE |
| Gate evaluated | ✅ β_PM_full sign + significance + robustness check |
| ≥ 2/3 models for gate | ✅ Cross-model consistency reported |
| 3 mandatory figures generated | ✅ β_PM bar chart, mediation decomposition, forest plot |
| 04_validation.md complete | ✅ Gate result (PASS/FAIL) + key findings |
| Results JSON saved | ✅ regression_results.json with full coefficients |
| Builds on h-m2 codebase | ✅ Controlled comparison — only adds regression layer |
