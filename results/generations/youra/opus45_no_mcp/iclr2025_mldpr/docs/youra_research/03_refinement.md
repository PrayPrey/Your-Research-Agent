# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T02:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1
- **Gap Title**: Cross-Repository Dataset Usage Frequency Quantification
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Benchmark overuse is ecosystem co-evolution, not just data memorization
- Architecture design carries benchmark artifacts separate from training effects
- Popular datasets shape the entire model design space over time

### Breakthrough Moments
- Dr. Nova's "co-evolution" framing shifted discussion from overfitting to ecosystem-level phenomenon
- Prof. Vera's three-condition design enabled causal mechanism testing
- Prof. Pax confirmed all conditions achievable with standard tools

---

## Final Hypothesis

### Title
Benchmark Co-Evolution and Generalization Gap

### Core Claim
Under conditions where domain pairing uses established taxonomies (OpenML task types + modality) and controlling for dataset size and age, IF models are trained on high-popularity datasets (top quartile by run-rate) compared to low-popularity datasets (bottom quartile) from the same domain, THEN the generalization gap to held-out same-domain test sets will be significantly larger (Cohen's d > 0.3), BECAUSE high-popularity datasets have been over-optimized by the ML architecture and hyperparameter search ecosystem (benchmark co-evolution effect).

### Mechanism
1. Popular benchmarks attract intensive architecture/hyperparameter search → optimized for benchmark specifics
2. Dataset-specific optimization creates features that exploit artifacts → underspecification
3. Held-out datasets lack these artifacts → performance drop

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | High-use datasets show larger gaps than low-use same-domain | Cohen's d > 0.3, p < 0.05 | d < 0.2 or no significant difference |
| P2 | Modern architectures show larger gaps than legacy | ResNet gap > VGG gap | VGG equal or larger |
| P3 | Pretrained models show larger gaps than random-init | Pretrained > random-init | Random-init equal or larger |

---

## Novelty

**Key Innovation**: Cross-repository systematic quantification linking popularity metrics to generalization failure, with causal mechanism investigation via architecture era comparison

**Differentiation**:
- Recht et al. (2019): Single dataset → Cross-repository systematic study
- D'Amour et al. (2020): Theoretical → Empirical with popularity as predictor
- Dataset documentation studies: Qualitative → Quantitative correlation

---

## Experimental Design

**Datasets**:
- High-use pair: CIFAR-10 / CINIC-10
- Low-use pair: SVHN / SVHN-Extra
- Reference: ImageNet / ImageNetV2

**Architectures**:
- Modern: ResNet-18
- Legacy: VGG-11 (capacity-matched)

**Conditions**:
1. Baseline: High-use vs low-use dataset comparison
2. Mechanism: ResNet vs VGG on same high-use dataset
3. Pretraining: ImageNet-pretrained vs random-init

---

## Limitations

- Survivorship bias: datasets in repositories are already "notable"
- Vision-focused: may not generalize to NLP/audio
- Run-rate metric sensitivity to repository practices
- Single domain pair insufficient (require 3+ for replication)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (addressed via design) |

---

*Phase 2A Complete - Ready for Phase 2B*
