# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play (Claude ALL personas)
- **Gap ID**: Gap-1
- **Gap Title**: No Systematic Cross-Benchmark Ranking Stability Analysis
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Ranking stability is more practically relevant than absolute accuracy drops for model selection
- Top-K overlap addresses practitioner concerns about choosing the "right" model
- Temporal analysis can reveal whether benchmark overfitting is worsening over time
- Architecture-benchmark interaction may reveal systematic biases in evaluation

### Breakthrough Moments
- Exchange 1: Shift from accuracy focus to ranking focus (Dr. Nova)
- Exchange 5: Dual-metric approach combining Kendall-τ and Top-K overlap (Dr. Ally)
- Exchange 6: Selection bias reframed as strengthening factor (Prof. Rex)

---

## Final Hypothesis

### Title
Cross-Benchmark Ranking Stability Analysis

### Hypothesis ID
H-RankingStability-v1

### Core Claim
Under controlled evaluation conditions (same models, same task semantics),
if we evaluate ImageNet models on an independently-collected benchmark variant (ImageNet-V2),
then model rankings will shift significantly (Kendall-τ < 0.90),
because iterative community optimization on popular benchmarks creates benchmark-specific
adaptations that don't transfer to novel test distributions.

### Mechanism
1. Popular benchmarks receive concentrated research attention (top 10% = 90% usage)
2. Iterative model development optimizes for benchmark-specific features
3. These optimizations don't transfer to independently-collected test sets
4. Result: Rankings shift when evaluated on alternative benchmarks

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Kendall-τ < 0.90 between ImageNet/V2 rankings | τ < 0.90, p < 0.001 | τ ≥ 0.95 |
| P2 | Top-10 overlap < 80% | ≤7 of 10 in both lists | Overlap ≥ 90% |
| P3 | Negative year coefficient in regression | β_year < 0, p < 0.05 | β_year ≥ 0 or p ≥ 0.05 |

---

## Novelty

**Key Innovation**: First systematic analysis of ranking stability (vs accuracy drops) between benchmark variants

**Differentiation from Prior Work**:
- Recht et al. (2019): Measured accuracy drops; we measure ranking correlations
- Dehghani et al. (2021): Analyzed task selection in NLU; we analyze model rankings across benchmark variants
- Reduced/Reused/Recycled (2021): Documented concentration; we test if it causes ranking instability

---

## Experimental Design

### Dataset
- ImageNet (original validation set)
- ImageNet-V2 (Recht et al. 2019)
- Source: Papers With Code + published papers

### Models
- ImageNet classification models 2015-2024
- Architectures: ResNet, ViT, ConvNeXt, EfficientNet, others
- Estimated 100+ models with both ImageNet and V2 results

### Baselines
- Random ranking correlation (τ ≈ 0)
- Perfect correlation (τ = 1.0)

---

## Limitations

### Scope Boundaries
- Limited to vision classification (ImageNet/V2 pair)
- Models must have published V2 results (selection bias)
- ImageNet-V2 is one specific alternative; other variants may differ

### Known Limitations
- Selection bias: Models with V2 results may be biased toward generalization-aware research
- V2 difficulty: May affect some architectures differently than others
- Temporal confounds: Year correlated with architecture, parameters, pretraining

### Mitigations
- Selection bias likely understates true effect (strengthens findings)
- Architecture-specific effects addressed by stratified analysis
- Temporal confounds addressed by multivariate regression with controls

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 8 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Selection bias (mitigated), architecture-specific difficulty (mitigated) |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Rankings shift significantly (τ < 0.90)
- **SH2 (Mechanism)**: Iterative benchmark-specific optimization causes non-uniform degradation
- **SH3 (Comparison)**: Deferred to Phase 5 baseline analysis

**Status**: READY for Phase 2B
