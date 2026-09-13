# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Architecture-Family-Specific Normalization of Geometric Signatures
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 14

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 14

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC (CV < -0.3 threshold), MECHANISM (spectral shape explanation), PREDICTIONS (P1-P3 defined), NOVELTY (estimator variance as quality signal), FEASIBILITY (existing tools), OBJECTIONS (effect size and confounds addressed)

### Key Insights

1. CV of participation ratio captures spectral SHAPE, not just condition number
2. Randomized SVD variance comes from estimator seeds, not input probe sets
3. GroupNorm stability (CV=0 in prior attempts) may reflect better matrix conditioning
4. Architecture-aware analysis may reveal stronger within-family correlations

### Breakthrough Moments

- **Exchange 7**: Shift from accuracy prediction to reliability/conditioning estimation
- **Exchange 10**: Prof. Pax's clarification that CV measures SVD seed variance
- **Exchange 13**: Dr. Nova's argument that CV captures spectral shape beyond condition number

---

## Final Hypothesis

### Title
CV of Participation Ratio as Model Quality Signal

### Hypothesis ID
H-CVPR-v1

### Core Claim
Under pretrained image classification models from timm (n ≥ 100), if we compute the coefficient of variation (CV) of participation ratio across 20 randomized SVD seeds and aggregate layer-wise metrics via mean, then CV_PR correlates negatively with model accuracy (r < -0.3, p < 0.05), because CV reflects spectral shape — flatter decay enables better generalization.

### Mechanism

1. Model training shapes weight matrix spectral properties (Martin & Mahoney 2019)
2. Spectral shape (flat vs peaked decay) affects randomized SVD convergence rate
3. Flat spectra → consistent SVD across seeds → low CV
4. Flat spectra indicate smooth loss landscapes → better generalization (Li et al. 2018)

---

## Predictions

| ID | Primary | Statement | Success Criterion | Falsification |
|----|---------|-----------|-------------------|---------------|
| P1 | Yes | CV_PR correlates negatively with accuracy | r < -0.3, p < 0.05 | r ≥ 0 or p ≥ 0.05 |
| P2 | No | Partial correlation remains significant after controlling for κ | partial r significant, \|r\| > 0.1 | partial r non-significant |
| P3 | No | Within-family correlation stronger than cross-family | \|r_ResNet\| > \|r_pooled\| | within-family weaker |

---

## Novelty

**Key Innovation**: First use of SVD estimator variance (CV) as model quality signal

**Prior Work Differentiation**:
- Unterthiner et al. (2020): Used direct weight statistics; we use variance of spectral estimators
- Martin & Mahoney (2019): Computed spectral properties directly; we measure how stable those computations are
- WeightWatcher: Computes alpha; we focus on PR variance which showed promise in h-m1 limitation

---

## Experimental Design

### Dataset
- **Name**: timm Model Zoo
- **Models**: 100+ pretrained models (ResNet, ViT, EfficientNet, ConvNeXt)
- **Ground Truth**: ImageNet top-1 accuracy

### Metrics
- CV_PR: std(PR across 20 SVD seeds) / mean(PR), averaged over layers
- Condition number: max/min singular value ratio
- ImageNet accuracy: from timm metadata

### Baselines
- Unterthiner et al. features (mean, variance, spectral properties)
- Condition number only

### Tools
- WeightWatcher (spectral analysis foundation)
- sklearn/scipy (randomized SVD)
- timm (pretrained models)

---

## Limitations

### Scope Boundaries
- **Applies to**: Pretrained image classification models from timm
- **Does not apply to**: Language models, randomly initialized models, models < 1M parameters

### Known Limitations
- Effect size may be moderate (r ~ -0.3 explains 9% variance)
- Layer-wise mean aggregation requires empirical validation
- n=1 for original GroupNorm observation (needs replication)
- Fine-tuning behavior not directly tested

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Effect size, aggregation ablation, parameter count control |

---

## Phase 2B Readiness

- **H-E1 (Existence)**: CV_PR negatively correlates with accuracy
- **H-M1 (Mechanism)**: CV reflects spectral shape beyond condition number
- **H-C1 (Condition)**: Within-family correlation stronger than cross-family

**Status**: READY FOR PHASE 2B

---

*Phase: 2A - Hypothesis Generation (Tikitaka Self-Contained Loop)*
*Failure Context: ROUTE_TO_0 recovery from 7 prior failures*
*Avoids: Random projections, alpha metric, learned encoders, architecture-agnostic thresholds*
