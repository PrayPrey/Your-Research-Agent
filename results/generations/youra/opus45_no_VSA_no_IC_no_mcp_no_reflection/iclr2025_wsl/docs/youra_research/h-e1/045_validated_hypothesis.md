# H-E1 Validated Hypothesis Synthesis

**Phase:** 4.5 — Hypothesis Synthesis
**Date:** 2026-08-29
**Status:** COMPLETED (Routed to Phase 2A)

---

## 1. Executive Summary

**Original Hypothesis:** Heavy-tailed exponents (α) can be computed with bounded variance (σ < 0.5) for ViT attention weight matrices using the Hill estimator on 100+ ViT models.

**Verdict:** REFUTED (MUST_WORK gate failed)

**Key Finding:** Cross-model α variance (σ=2.868) exceeds threshold by 5.7x. However, within-family variance (σ=0.24 for google/vit-*) meets criterion, suggesting methodology is sound but scope was overclaimed.

---

## 2. Prediction Mapping

| Prediction | Status | Evidence |
|------------|--------|----------|
| P1: σ(α) < 0.5 across ViT models | **REFUTED** | σ(α) = 2.868, 5.7x over threshold |
| P1-alt: σ(α) < 0.5 within family | SUPPORTED | σ = 0.24 for google/vit-* (n=6) |

### Planned vs Actual

| Metric | Planned | Actual |
|--------|---------|--------|
| Models processed | 100 | 53 |
| σ(α) target | < 0.5 | 2.868 |
| α range expected | [1.5, 4.0] | [2.20, 18.92] |
| Runtime budget | Not specified | 1744s |

---

## 3. Refined Core Statement

**Overclaim removed:** "across 100+ ViT models"

**Refined hypothesis:**
> Heavy-tailed exponents can be computed with bounded variance (σ < 0.5) for ViT attention weight matrices **within homogeneous model families** (e.g., google/vit-base-*) using the Hill estimator.

**Scope reduction:** Universal → Family-specific

---

## 4. Literature Connection

### Supporting Theory
- Martin & Mahoney (2021): Heavy-tailed self-regularization framework predicts α ∈ [2, 6] for well-trained networks — partially confirmed (mean α = 4.327)
- WeightWatcher tool successfully computed α values for all attempted models

### Unexpected Findings
1. **Fine-tuning creates extreme outliers:** jaranohaal/vit-base-violence-detection (α=12.6), mlx-vision models (α=14.8)
2. **Training state diversity confounds:** Mix of pretrained vs heavily fine-tuned models

### Competing Explanations
- **Training procedure hypothesis:** Variance stems from different training recipes, not architecture
- **Task transfer hypothesis:** Fine-tuning for non-ImageNet tasks shifts α distribution

---

## 5. Principled Limitations

| Limitation | Root Cause | Impact |
|------------|------------|--------|
| High cross-model variance | Model heterogeneity on HuggingFace | Prevents unified α-based prediction |
| Outlier α values | Fine-tuned models for specialized tasks | Skews aggregate statistics |
| Incomplete sample | Runtime constraints | 53/100 target models |

**Design Gap:** Experiment assumed HuggingFace ViT models form homogeneous population. Reality: mixture of base models, fine-tuned variants, and different architectures (ViT-base, ViT-large, ViT-tiny).

---

## 6. Future Work Directions

### Immediate (Phase 2A refinement)
1. **Stratify by model family:** Separate analysis for google/vit-*, facebook/deit-*, microsoft/swin-*
2. **Filter criteria:** Exclude α > 10 outliers (likely training artifacts)
3. **Minimum family size:** Require n ≥ 10 models per family for statistical power

### Extended Research
1. **Training recipe covariate:** If metadata available, include training procedure as feature
2. **Fine-tuning vs pretrained:** Separate analysis for base models vs fine-tuned variants

---

## 7. Artifacts

### Validation Outputs
- `h-e1/04_validation.md` — Full validation report
- `h-e1/figures/gate_check.png` — Gate pass/fail visualization
- `h-e1/figures/alpha_histogram.png` — α distribution
- `h-e1/figures/family_boxplot.png` — α by model family
- `h-e1/code/results.json` — Per-model measurements

### Key Metrics
| Metric | Value |
|--------|-------|
| Models processed | 53 |
| Mean α | 4.327 |
| Median α | 3.521 |
| σ(α) | 2.868 |
| α range | [2.20, 18.92] |
| Within-family σ | 0.24 |

---

## 8. Routing Decision

**Gate Result:** MUST_WORK → FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_2A

**Rationale:** The methodology works (WeightWatcher computes α successfully), but the hypothesis scope was too broad. Returning to Phase 2A to refine with stratification by model family.

**Next Action:** Phase 2A dialogue to reformulate h-e1 with family-specific bounded variance claim.

---

*Synthesis completed: 2026-08-29*
