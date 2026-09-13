# Phase 4 Validation Report — h-m4

**Hypothesis:** H-M4 — PM-Proxy Mediation of CSEM Asymmetry
**Date:** 2026-03-15
**Gate Type:** SHOULD_WORK
**Gate Verdict:** **FAIL (0/3 models passed)**

---

## 1. Hypothesis Summary

H-M4 tests whether conversational politeness markers (PM-proxy: cosine similarity to a politeness centroid computed from the assistant turn) mediate the directional CSEM asymmetry found in H-M2.

**Formal claim:** In a 4-stage OLS mediation regression predicting `Δ_csem = C_sem(H←A) − C_sem(A←H)`, the PM-proxy coefficient `β_PM` should be statistically significant (p < 0.05) with positive sign (β_PM > 0) in ≥2/3 SBERT models after controlling for surface features (response_length, bullet_density, politeness_freq, ttr, mean_sent_len) and tier fixed effects.

**Implementation approach:** INCREMENTAL build on H-M2 codebase. New modules:
- `surface_features.py` — 5 surface feature extractors
- `regression.py` — 4-stage OLS mediation with HC3 robust standard errors
- `evaluate.py` — cross-model gate evaluation (≥2/3 criterion)
- `visualize_m4.py` — 6 diagnostic figures
- `run_experiment_m4.py` — main orchestrator

---

## 2. Implementation Verification

### 2.1 Code Status

All 30 SDD tasks implemented and 150/150 tests passing prior to experiment execution:

| Epic | Tasks | Status |
|------|-------|--------|
| ENV-1 | Environment setup | COMPLETE |
| A-1..A-12 | Architecture tasks | COMPLETE |
| L-5-1..3 | surface_features.py | COMPLETE |
| L-6-1..4 | regression.py | COMPLETE |
| L-10-1..4 | evaluate.py | COMPLETE |
| C-3-1..2 | visualize_m4.py | COMPLETE |
| C-4-1 | run_experiment_m4.py | COMPLETE |
| C-8-1..2 | Integration tests | COMPLETE |
| C-12-1..2 | Output validation | COMPLETE |

### 2.2 Dry Run Verification

Dry run passed (3-sample subset): code executes without errors, all modules imported correctly, regression pipeline runs end-to-end.

### 2.3 Key Implementation Notes

- **sys.path ordering**: h-m4 code directory inserted at `sys.path[0]` BEFORE h-m2 append, preventing h-m2 `config.py` from shadowing h-m4 `config.py`
- **`__pycache__` cleared** to prevent stale h-m2 `.pyc` from loading
- **HC3 robust standard errors**: `sm.OLS(y, X).fit(cov_type='HC3')` via statsmodels
- **rng.choice bootstrap**: used for sampling (not rng.integers)

---

## 3. Experiment Results

### 3.1 Dataset

- **Source:** Anthropic/hh-rlhf (full dataset, 3 tiers)
- **Tiers:** helpful-base (127,708 rows), helpful-rejection-sampled (130,726 rows), helpful-online (52,352 rows)
- **Regression sample per model:** n=3,000 (sampled for computational feasibility)

### 3.2 CSEM Embedding Results (pre-regression)

| Tier | Branch | N | Mean C_sem (MiniLM) |
|------|--------|---|---------------------|
| helpful-base | chosen | 63,830 | 0.0853 |
| helpful-base | rejected | 63,878 | 0.0855 |
| helpful-rejection-sampled | chosen | 65,359 | 0.0923 |

### 3.3 OLS Mediation Regression Results

#### Model 1: all-MiniLM-L6-v2

| Stage | β_PM | p(β_PM) | R² | N |
|-------|------|---------|-----|---|
| Stage 1 (PM-only) | −2.52e−05 | 0.9969 | 0.0003 | 3000 |
| Stage 2 (full + surface controls) | −1.46e−05 | 0.9982 | 0.0071 | 3000 |
| Stage 3 (robustness + tier_rank) | — | — | 0.0071 | 3000 |

**Gate pass:** NO (β_PM ≈ 0, p = 0.998)

#### Model 2: paraphrase-MiniLM-L6-v2

| Stage | β_PM | p(β_PM) | R² | N |
|-------|------|---------|-----|---|
| Stage 1 (PM-only) | −5.12e−06 | 0.9994 | — | 3000 |
| Stage 2 (full + surface controls) | −1.26e−06 | 0.9998 | 0.0122 | 3000 |
| Stage 3 (robustness + tier_rank) | — | — | 0.0122 | 3000 |

**Gate pass:** NO (β_PM ≈ 0, p = 0.9998)

#### Model 3: all-mpnet-base-v2

| Stage | β_PM | p(β_PM) | R² | N |
|-------|------|---------|-----|---|
| Stage 1 (PM-only) | +6.43e−05 | 0.9919 | — | 3000 |
| Stage 2 (full + surface controls) | +6.76e−05 | 0.9914 | 0.0101 | 3000 |
| Stage 3 (robustness + tier_rank) | — | — | 0.0096 | 3000 |

**Gate pass:** NO (β_PM near zero, p = 0.991)

### 3.4 Gate Evaluation Summary

| Model | β_PM | p | β_PM > 0 | p < 0.05 | PASS |
|-------|------|---|----------|----------|------|
| all-MiniLM-L6-v2 | −1.46e−05 | 0.998 | ✗ | ✗ | ✗ |
| paraphrase-MiniLM-L6-v2 | −1.26e−06 | 0.9998 | ✗ | ✗ | ✗ |
| all-mpnet-base-v2 | +6.76e−05 | 0.991 | ✓ | ✗ | ✗ |

**Models passing:** 0/3
**Required:** ≥2/3
**SHOULD_WORK Gate:** **FAIL**

---

## 4. Mechanism Activation Indicators

| Indicator | Status | Notes |
|-----------|--------|-------|
| Both CSEM directions computed | ✓ PASS | C_sem(H←A) and C_sem(A←H) computed for all tiers |
| Regression pipeline executed | ✓ PASS | 4-stage OLS ran to completion for all 3 models |
| Surface features extracted | ✓ PASS | 5 features computed per response |
| PM-proxy computed | ✓ PASS | Cosine similarity to politeness centroid |
| PM-proxy has variance | ✓ PASS | Non-degenerate distribution observed |
| β_PM statistically significant | ✗ FAIL | p ≈ 0.99 across all models |
| Cross-model consistency | ✗ FAIL | All 3 models fail gate |

---

## 5. Figures Generated

| Figure | File | Description |
|--------|------|-------------|
| Fig 1 | `figures/fig1_beta_pm_comparison.png` | β_PM point estimates + 95% CI across models |
| Fig 2 | `figures/fig2_mediation_decomposition.png` | Mediation decomposition by tier |
| Fig 3 | `figures/fig3_coefficient_forest.png` | Forest plot of all Stage 2 coefficients |
| Fig 4 | `figures/fig4_csem_vs_pm_scatter.png` | ΔCSEM vs PM-proxy scatter by tier |
| Fig 5 | `figures/fig5_partial_regression.png` | Partial regression plot (PM-proxy effect) |
| Fig 6 | `figures/fig6_tier_pm_interaction.png` | Tier × PM-proxy interaction |

All 6 figures generated successfully.

---

## 6. Limitation Analysis and Reflection

### 6.1 Why did H-M4 fail?

The PM-proxy (cosine similarity to a politeness centroid) shows essentially zero effect on ΔCSEM after controlling for surface features. Several potential explanations:

1. **PM-proxy validity**: The politeness centroid may not capture the relevant politeness signal. The proxy is computed as cosine similarity in SBERT embedding space to a centroid of politeness-marker phrases — this may be too coarse-grained to isolate politeness as distinct from general semantic similarity.

2. **Surface features absorb PM signal**: `politeness_freq` (fraction of explicit politeness tokens) and `response_length` may already capture most of the variance attributable to politeness markers. When these are included, residual PM-proxy variance is negligible.

3. **Mediation path not present**: CSEM asymmetry (H-M2) may not be mediated by conversational style/politeness at all. The asymmetry (C_sem(H←A) > C_sem(A←H)) could be a structural property of the RLHF data collection process rather than a content-driven effect.

4. **n=3,000 vs. full data**: The regression sample is 3,000 rows (from ~150,000+ total). While this is sufficient for OLS power at medium effect sizes, the near-zero β_PM coefficients suggest the effect size is essentially zero regardless of sample size.

5. **Operationalization of Δ_csem**: The dependent variable (ΔCSEM per response pair) may have high noise that PM-proxy cannot explain.

### 6.2 Non-blocking nature

H-M4 is a SHOULD_WORK gate. Per pipeline rules, SHOULD_WORK FAIL is **non-blocking** — the pipeline can continue to subsequent hypotheses.

### 6.3 Implications for future hypotheses

- The politeness/conversational-style mediation mechanism is not supported by this evidence
- Future work should consider alternative mediators (e.g., semantic specificity, factual density, instruction-following signals)
- The H-M2 CSEM asymmetry finding remains valid and unexplained by PM

---

## 7. Final Verdict

```
GATE TYPE:    SHOULD_WORK
VERDICT:      FAIL
MODELS PASS:  0/3
REASON:       β_PM ≈ 0 (|β| < 1e-4), p ≈ 0.99 across all models.
              PM-proxy does not mediate CSEM directional asymmetry.
BLOCKING:     NO (SHOULD_WORK FAIL is non-blocking)
```

---

## 8. Step 06b Reflection Outcome

| Field | Value |
|-------|-------|
| **Reflection Triggered** | Yes (SHOULD_WORK FAIL) |
| **Reflection Outcome** | LIMITATION_RECORDED |
| **Self-Modify Identified** | No |
| **Routing** | None (SHOULD_WORK never routes to Phase 0/2A) |
| **Pipeline Continuation** | Proceeds to Phase 5 (non-blocking) |
| **Serena Memory** | `limitation_h-m4_run1.md` |
| **Reflection Report** | `h-m4/reflection_report.md` |

**Limitation Note:** PM-proxy (cosine similarity to politeness centroid) has zero predictive power for CSEM directional asymmetry after controlling for surface features. β_PM ≈ 0 across all 3 SBERT models with p ≈ 0.99. This limitation is recorded for cross-phase learning; the null result is scientifically informative.

---

*Generated by Phase 4 Validation — Anonymous Pipeline v3.5*
*Date: 2026-03-15 | Hypothesis: h-m4 | Experiment PID: 3412834*
*Step 06b Reflection executed: 2026-03-15T16:40:00*
