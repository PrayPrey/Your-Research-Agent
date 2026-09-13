# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T00:05:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap3
- **Gap Title**: Weight-Space Methods for Model Behavior Prediction
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 13

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 13

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC claim, MECHANISM explained, PREDICTIONS defined with criteria, NOVELTY articulated, FEASIBILITY confirmed, OBJECTIONS addressed

### Key Insights
- Behavioral prediction is qualitatively different from accuracy prediction—structured output, not scalar
- Cross-metric transfer is the key novelty that distinguishes from prior work
- Existing model zoos contain sufficient behavioral variation for learning

### Breakthrough Moments
- Exchange 7: Cross-metric transfer protocol proposed to address circularity concern
- Exchange 11: Final hypothesis synthesized with all concerns addressed

---

## Final Hypothesis

### Title
Behavioral Fingerprinting via Weight-Space Neural Functionals

### Hypothesis ID
H-BehavioralFingerprint-v1

### Core Claim
Under the scope of CNN model zoos (Small CNN Zoo, CIFAR-10), if we train a permutation-equivariant neural functional (NF-Layer) to predict class-wise accuracy profiles from weights, then the learned behavioral embedding will (1) explain ≥5% more variance in class-wise accuracy than a stratified baseline AND (2) correlate with confusion matrix similarity (r ≥ 0.30) despite never being trained on confusion matrices, because NF-Layers capture functionally salient weight directions that scalar predictions miss.

### Mechanism
1. Weight matrices encode behavioral information beyond aggregate accuracy
2. NF-Layer's equivariant aggregation captures cross-layer weight correlations relevant to per-class behavior
3. Low-dimensional embedding bottleneck forces compression to shared behavioral factors
4. These factors transfer to unseen behavioral metrics (confusion similarity)

### Null Hypothesis (H0)
Class-wise accuracy profiles are fully predictable from overall accuracy + class baseline difficulty. NF-Layer behavioral embeddings add no additional explanatory power.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | NF-Layer embeddings explain more variance in class-wise accuracy than stratified baseline | ΔR² > 0.05 (p < 0.05) | ΔR² ≤ 0.05 or p ≥ 0.05 |
| P2 | Embedding distance correlates with confusion matrix similarity | r ≥ 0.30 (p < 0.01) | r < 0.30 |
| P3 (Ablation) | Full NF-Layer outperforms pointwise NF-Layer | Full R² > Pointwise R² (p < 0.05) | No significant difference |

---

## Novelty

**Key Innovation**: Shift from scalar property prediction (accuracy) to behavioral profile prediction (class-wise accuracy) with transfer to confusion matrices

**Differentiation from Prior Work**:
- Zhou et al. (2023): Predicts scalar accuracy; we predict structured behavioral profiles
- SANE (Schürholt et al. 2024): Predicts scalar properties; we validate cross-metric transfer
- Herrmann et al. (2024): Focuses on RNN task identification; we extend to CNN behavioral prediction
- Meynent et al. (2025): Uses behavioral loss for reconstruction; we use it as prediction target

---

## Experimental Design

**Dataset**: Small CNN Zoo (CIFAR-10, ~3000 models)
**Model**: NF-Layer neural functional (16-dim embedding)
**Baselines**:
- SANE embeddings + linear probe
- Stratified baseline (overall accuracy + per-class difficulty)
- Pointwise NF-Layer (ablation)

**Evaluation Protocol**:
- 10-fold cross-validation
- Hyperparameter holdout (train on 80% configs, test on 20%)
- Seed variation holdout

---

## Limitations

- Behavioral definition constrained to class-wise accuracy profiles (not OOD, not adversarial)
- Cross-metric transfer tested only on confusion matrices
- Embedding dimension (16) is arbitrary; may require tuning
- Results may not generalize to larger models (ResNet-18+) without additional validation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase: 2A - Research Dialogue*
*Ready for: Phase 2B - Research Planning*
