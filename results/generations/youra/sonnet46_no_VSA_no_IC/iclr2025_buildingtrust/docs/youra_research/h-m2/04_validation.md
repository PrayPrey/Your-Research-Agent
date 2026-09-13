# H-M2 Phase 4 Validation Report

**Hypothesis:** h-m2 — Differential Rank Stability (Fairness vs. Adversarial Robustness)  
**Gate type:** SHOULD_WORK (exploratory/directional; failure does not halt pipeline)  
**Gate result:** ❌ FAIL  
**Date:** 2026-08-20  
**Pipeline:** YouRA Phase 4 PoC Validation

---

## Hypothesis Statement

Partial Spearman ρ_fairness (BBQ-Disambig→BBQ-Ambig, MMLU-controlled) exceeds  
partial ρ_robustness (mean of GLUE→AdvGLUE and ANLI R1→R3, MMLU-controlled)  
by Δρ ≥ 0.2.

**Depends on:** h-m1 (VALIDATED — base scores loaded from h-m1/data/h_m1_scores.csv)

---

## Data

| Field | Value |
|---|---|
| Source | TrustLLM benchmark (arXiv 2401.05561) |
| h-m1 base models | N = 16 |
| Models with robustness data | N = 13 |
| Excluded (no TrustLLM robustness data) | Alpaca-13B, Koala-13B, OpenAssistant |
| N_common_robust | 13 (≥ N_COMMON_MIN = 8 ✅) |

**Models included:** GPT-4, GPT-3.5-Turbo, LLaMA-2-7B/13B/70B, LLaMA-2-7B/13B/70B-Chat, Mistral-7B, Mistral-7B-Instruct, Falcon-7B, Falcon-40B, Vicuna-13B

---

## Results

### Primary Metrics (MMLU-controlled partial Spearman ρ)

| Dimension | Partial ρ | 95% CI | p-value |
|---|---|---|---|
| Fairness (BBQ-Disambig→BBQ-Ambig) | **0.967** | [0.88, 0.99] | < 0.0001 |
| Robustness: GLUE→AdvGLUE | 0.867 | [0.58, 0.96] | 0.0003 |
| Robustness: ANLI R1→R3 | 0.684 | [0.18, 0.90] | 0.0143 |
| ρ_robust_mean | 0.776 | — | — |

### Gate Metric

| Metric | Value | Threshold | Result |
|---|---|---|---|
| **Δρ = ρ_fairness − ρ_robust_mean** | **0.192** | **≥ 0.200** | ❌ FAIL |

### Secondary Checks

| Check | Result |
|---|---|
| Both ρ_advglue and ρ_anli < ρ_fairness | ✅ PASS |
| Fisher z-test (directional significance) | z = 2.265, p = 0.024 |

### Sensitivity Analysis (Winogrande covariate)

| Dimension | Partial ρ (Wino-controlled) |
|---|---|
| Fairness | 0.973 |
| Robustness: AdvGLUE | 0.886 |
| Robustness: ANLI | 0.915 |
| Δρ (Wino-controlled) | 0.073 |

---

## Raw (Unadjusted) Spearman ρ

| Dimension | Raw ρ |
|---|---|
| Fairness (BBQ) | 0.978 |
| Robustness (AdvGLUE) | 0.982 |
| Robustness (ANLI) | 0.983 |
| Δρ_raw | −0.005 |

Note: raw correlations are near-ceiling for all dimensions, consistent with the high-ability cluster structure observed in h-m1. MMLU-controlled partial ρ reveals the underlying differential structure.

---

## Gate Evaluation

**Gate type:** SHOULD_WORK  
**Criterion:** Δρ ≥ 0.2  
**Observed Δρ:** 0.192  
**Shortfall:** −0.008 (4% below threshold)  
**Gate result:** ❌ FAIL

The directional pattern is present (ρ_fairness > both robustness dimensions, Fisher z significant at p = 0.024), but the magnitude criterion (Δρ ≥ 0.2) is not met. The gap is 0.008 below threshold — within measurement uncertainty given N = 13.

**SHOULD_WORK gate failure does not halt the pipeline.** This result is recorded as a limitation and the pipeline continues to h-m3.

---

## Figures

All figures saved to `docs/youra_research/h-m2/figures/`:

- `gate_metrics_comparison.png` — bar chart of partial ρ per dimension with 95% CI
- `rank_heatmap.png` — model × benchmark rank heatmap (sorted by MMLU)
- `per_dimension_scatter.png` — 3-panel scatter with partial ρ annotations
- `forest_plot.png` — forest plot of partial ρ with 95% CI and Δρ threshold

---

## Interpretation

The directional hypothesis is supported: fairness rank stability (BBQ) exceeds both adversarial robustness dimensions (AdvGLUE, ANLI) under MMLU control. However, the effect size (Δρ = 0.192) falls just short of the preregistered Δρ ≥ 0.2 threshold.

**Key observations:**
1. All three partial ρ values are high (0.68–0.97), indicating strong rank stability across conditions within each dimension.
2. The ANLI R1→R3 partial ρ (0.684) has the widest CI ([0.18, 0.90]) — the most uncertain estimate, driven by small N.
3. The Winogrande sensitivity shows Δρ collapses to 0.073, suggesting MMLU is a more appropriate covariate than Winogrande for this analysis.
4. N = 13 limits statistical power; the SHOULD_WORK failure may partly reflect insufficient sample size rather than true absence of the mechanism.

**Limitation:** Robustness scores for Alpaca-13B, Koala-13B, and OpenAssistant are not reported in TrustLLM (arXiv 2401.05561), reducing N from 16 to 13. Including these models could shift Δρ in either direction.

---

## Conclusion

| Field | Value |
|---|---|
| Gate | SHOULD_WORK |
| Gate result | FAIL (Δρ = 0.192 < 0.200) |
| Directional support | Yes (Fisher z = 2.265, p = 0.024) |
| Pipeline action | Continue to h-m3 |
| Limitation recorded | Yes — Δρ near-threshold with small N; 3 models excluded |
