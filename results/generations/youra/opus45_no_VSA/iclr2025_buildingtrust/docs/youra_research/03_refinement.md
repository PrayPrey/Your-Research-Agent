# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-08T08:15:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Cross-Dimensional Correlation Analysis Framework
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- High cross-benchmark correlation (ρ = 0.80-0.87) is not a nuisance but a signature of a latent coherence factor
- Eigenvalue dominance framing connects to psychometric 'g-factor' methodology (Spearman, 1904)
- Instruction-tuning provides a natural quasi-intervention for mechanism testing
- BSI must be computed on independent datasets (PAWS, QQP) to avoid circularity with trustworthiness benchmarks

### Breakthrough Moments
- Dr. Nova's reframing: "What latent variable must exist for all pairs to show strong positive correlation?"
- Dr. Ally's cascade design with layered existence tests avoiding magnitude thresholds
- Prof. Rex's discriminant validity demand: GRC must differ from capability PC1
- Dr. Nova's instruction-tuning as natural experiment proposal

---

## Final Hypothesis

### Title
Generalized Representational Coherence (GRC) as Latent Factor in LLM Trustworthiness

### Hypothesis ID
H-GRC-v1

### Core Claim
Under conditions where LLMs are evaluated on multiple trustworthiness benchmarks (truthfulness, robustness, calibration), if a dominant latent factor (PC1,residual) exists after controlling for model scale and training confounds, then this factor reflects a shared representational stability mechanism, because training procedures that increase internal consistency simultaneously improve all trustworthiness dimensions.

### Mechanism
Training procedures shape internal representation geometry. Higher representation stability reduces sensitivity to input perturbations and improves calibration. This stability simultaneously boosts truthfulness (better epistemic discrimination), robustness (less activation drift), and reliability (consistent predictions). The shared mechanism induces positive correlation across all trustworthiness benchmarks, creating a dominant latent factor analogous to psychometric 'g'.

---

## Predictions

| ID | Statement | Test Method | Success Criterion |
|----|-----------|-------------|-------------------|
| P1 (Primary) | λ₁,residual > permutation 95th percentile | PCA + permutation test (1000 shuffles) | p < 0.05 |
| P2 | ρ(PC1,residual, BSI) > 0 | Pearson correlation; BSI on independent datasets | p < 0.05 |
| P3 | New benchmark loading ≥ 0.3 on frozen PC1 | Out-of-sample factor scoring | ≥2 benchmarks meet criterion |
| P4 | Instruction-tuning increases BSI and PC1 | Paired t-test on matched base/instruct pairs | Both Δ > 0, p < 0.05 |

---

## Novelty

**Key Innovation**: First systematic factor-analytic framework for understanding cross-trustworthiness-benchmark correlation with explicit mechanism hypothesis linking to representation stability.

**Differentiation from Prior Work**:
- Trust-RAG Compass (Zhou et al., 2024): Proposes 6 dimensions but does not test cross-correlation
- CCPS (Khanmohammadi et al., 2025): Shows stability improves calibration on single dimension; we extend to multi-benchmark
- h-m2 (prior failure): Assumed construct divergence causes low correlation; we explain HIGH correlation

---

## Experimental Design

**Dataset**: HELM/Open LLM Leaderboard (~100+ models)

**Benchmarks**: TruthfulQA, MMLU, AdvGLUE, BBH, calibration metrics (5-6 dimensions)

**Baselines**:
- Permutation null distribution
- Scale-only regression
- Capability PC1 for discriminant validity

**Tools**: lm-eval-harness, scikit-learn PCA, statsmodels SEM

---

## Limitations

- Closed-source models limit activation-level analysis; BSI restricted to behavioral proxies
- Instruction-tuning quasi-intervention is not randomized; confounding possible
- HELM benchmark selection may not span all trustworthiness dimensions
- Release date confounded with engineering improvements beyond RLHF

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met (16 exchanges) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (addressed via cascade design) |

---

## How This Avoids Prior Failures

| Prior Failure | What Failed | How H-GRC-v1 Avoids |
|---------------|-------------|---------------------|
| h-e1 | Magnitude threshold (β₁ ≤ -0.10) was unrealistic | Uses existence tests (λ₁ > permutation), no magnitude thresholds |
| h-m1 | Underpowered (42 models, 12 categories) | Uses ~100 models with 5-6 benchmarks |
| h-m2 | Assumed low correlation; premise invalid | Explains HIGH correlation via shared mechanism |
