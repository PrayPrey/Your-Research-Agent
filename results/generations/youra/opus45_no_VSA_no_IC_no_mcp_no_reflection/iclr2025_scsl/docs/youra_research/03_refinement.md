# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-29T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Tikitaka Loop (no external orchestrator)
- **Gap ID**: Gap-3-TrainingDynamics
- **Gap Title**: Training Dynamics Exploitation for Robustification
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Simplicity bias can be reframed as opportunity rather than obstacle
- Gradient-space intervention avoids neuron-level interpretability issues
- Progressive adaptation addresses timing sensitivity of saturation point

### Breakthrough Moments
- Exchange 4: Prof. Pax proposes gradient projection vs neuron freezing
- Exchange 7: Dr. Nova evolves single-point to progressive orthogonalization

---

## Final Hypothesis

### Title
Progressive Gradient Orthogonalization (PGO)

### Core Claim
Under standard supervised classification with spurious correlations, if we progressively project training gradients orthogonal to the cumulative "easy gradient" subspace, then worst-group accuracy improves relative to ERM, because the model is forced to learn features that generalize beyond majority-group shortcuts.

### Mechanism
1. **Early training**: Network follows "easy" gradients toward spurious features
2. **Subspace accumulation**: PGO accumulates these directions into subspace S via incremental SVD
3. **Orthogonal projection**: Later gradients projected orthogonal to S must find alternative (core) features

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | PGO improves worst-group accuracy by ≥5% over ERM on Waterbirds | PGO ≥ ERM + 5%, p < 0.05 | PGO ≤ ERM |
| P2 | PGO matches or exceeds JTT without two training runs | PGO ≥ JTT | PGO < JTT by >3% |
| P3 | PGO representations show higher core-feature alignment | Core probe > ERM | Core probe ≤ ERM |

---

## Novelty

**Key Innovation**: First method to exploit training dynamics through continuous gradient subspace projection. Unlike JTT (sample identification) or DFR (post-training), PGO directly engineers the training trajectory in a single run.

**Differentiation**:
- vs JTT: gradient space, not sample space; single run vs two runs
- vs DFR: during training, not post-training; no held-out groups needed
- vs Group DRO: no group annotations during training

---

## Experimental Design

**Dataset**: Waterbirds (primary), CelebA (secondary)

**Model**: ResNet-50 pretrained on ImageNet

**Baselines**: ERM, JTT, DFR

**Controlled Variables**: lr=0.001, batch=64, epochs=50, 5 random seeds

---

## Limitations

- Requires hyperparameter tuning for rank k and α_max
- Additional memory overhead (~5GB for ResNet-50)
- May not help if spurious and core features have similar complexity
- Early gradient subspace may contain some core feature directions

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (mitigations identified) |

---
