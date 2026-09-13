# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T12:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Temporal Dynamics of Spurious vs Core Feature Learning
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All six convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed)

### Key Insights
- The "when" question is as important as "what" and "why" for intervention design
- Second derivative of worst-group accuracy provides a simple, measurable crystallization signal
- LR schedule may modulate but not cause crystallization — control experiment distinguishes
- Weak form (accelerating decline) equally useful even without sharp phase transition

### Breakthrough Moments
- Dr. Nova's reframing from "what features" to "when they dominate"
- Prof. Pax's suggestion of second derivative as transition detector
- Prof. Rex's LR confound challenge leading to constant-LR control experiment design

---

## Final Hypothesis

### Title
Shortcut Crystallization Zone: Temporal Dynamics of Spurious Feature Dominance

### Core Claim
Under standard SGD training on spurious-correlation benchmarks (Waterbirds, CelebA, ColoredMNIST), if we track worst-group accuracy across training epochs, then we will observe a localized training phase (the "Shortcut Crystallization Zone") where classifier reliance on spurious features accelerates, because simplicity bias creates initial spurious feature advantage and gradient starvation amplifies this through self-reinforcing feedback.

### Mechanism
1. Simplicity bias creates early spurious feature advantage (Shah et al. 2020)
2. Gradient starvation amplifies dominance through feedback (Pezeshki et al. 2021)
3. Crystallization marks when feedback becomes self-reinforcing
4. Post-crystallization, classifier commits to spurious features

---

## Predictions

| ID | Statement | Success Criterion | Primary |
|----|-----------|-------------------|---------|
| P1 | d²(WGA)/d(epoch)² shows significant negative peak in first 50% of training | p<0.05 negative peak in ≥2/3 benchmarks | Yes |
| P2 | Effect persists under constant LR | Significant peak with constant LR | No |
| P3 | Peak timing is benchmark-relative (20-40% of training) | All benchmarks within range | No |

---

## Novelty

**Key Innovation**: Moving from static descriptions ("DNNs prefer simple features") to dynamic temporal characterization ("shortcuts crystallize at epoch X under conditions Y"). Second derivative of WGA as crystallization detector is novel.

**Differentiation from Prior Work**:
- Shah et al. 2020: Describes WHAT, not WHEN
- Pezeshki et al. 2021: Explains WHY, not WHEN
- Kirichenko et al. 2023: Post-hoc correction; we characterize WHEN to intervene

---

## Experimental Design

**Model**: ResNet-50 (primary), ViT-B/16 (generality test)

**Datasets**: Waterbirds, CelebA, ColoredMNIST (WILDS benchmark suite)

**Baselines**:
- ERM (standard training)
- Oracle (group-balanced from epoch 0)

**Procedure**:
1. Train with dense checkpointing (every epoch)
2. Compute worst-group accuracy at each checkpoint
3. Apply 5-epoch rolling average smoothing
4. Compute second derivative d²WGA/dt²
5. Test for significant negative peak in first 50% of training
6. Repeat with constant LR for control

---

## Limitations

- Smoothing window choice (5 epochs) requires sensitivity analysis
- Three benchmarks may not establish universality
- NLP domain (CivilComments) deferred to future work
- Architecture generality limited to ResNet-50/ViT-B/16

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---
