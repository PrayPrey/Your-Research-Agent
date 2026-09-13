# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-09T17:55:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Epoch-Level Temporal Characterization of Feature Separability
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met: SPECIFIC core claim (DCR mechanism), MECHANISM explained (5-step causal chain), PREDICTIONS with criteria (P1-P5 pre-registered), NOVELTY articulated (paradigm shift, M1/M2/M3 framework), FEASIBILITY established (~20-30 GPU-hours), OBJECTIONS addressed.

### Key Insights
- Orthogonality between group Hessian eigenspaces is a CONSEQUENCE of gradient dynamics, not a root cause
- Differential convergence rate (majority converges faster) is the operative variable
- Per-sample gradient normalization isolates geometric effects from frequency weighting
- Update-norm parity is a cleaner intervention than representation alignment

### Breakthrough Moments
- Exchange 5: Dr. Ally refined causal chain with gradient misalignment as upstream
- Exchange 9: Dr. Nova proposed differential convergence rate as root cause
- Exchange 10: Prof. Vera formalized M1/M2/M3 competing model framework
- Exchange 14: Prof. Vera required per-sample normalization and SR→WGA mediation

---

## Final Hypothesis

### Title
Differential Convergence Rate (DCR) Mechanism for Group Curvature Disparity

### Hypothesis ID
H-DCR-v1

### Core Claim
Under ERM training on group-imbalanced data, if majority groups converge faster (lower per-sample gradient norms earlier), then minority groups maintain higher local curvature (SR > 1.0), because majority-dominated updates smooth curvature only in majority-relevant parameter directions, leaving minority-relevant directions untraversed and sharp.

### Mechanism
1. Sample imbalance causes majority gradient dominance
2. Majority-dominated updates traverse majority-relevant parameter directions
3. Majority loss landscape flattens (low curvature) through repeated traversal
4. Minority-relevant directions remain untraversed and sharp (high curvature)
5. Result: SR > 1.0, higher minority loss, lower worst-group accuracy

---

## Predictions

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Per-sample gradient ratio decay precedes SR divergence | τ_r→SR > 0, 95% CI excludes 0 | τ_r→SR ≤ 0 |
| P2 | Update-norm parity attenuates SR | SR ≤ 1.1 vs SR > 1.2 baseline | SR unchanged |
| P3 | SR ≈ 1 at initialization | SR₀ ∈ [0.9, 1.1], CI includes 1.0 | SR₀ > 1.1 significantly |
| P4 | SR reduction improves WGA | ΔSR ≤ -0.2 → ΔWGA ≥ +2pp | No correlation |
| P5 | SR → 1 in NTK regime | Monotonic decrease with width | SR stable |

---

## Novelty

**Key Innovation**: Reframes Hessian eigenspace orthogonality (from h-c1 failure) as a consequence of differential convergence, not a dead end. Shifts intervention paradigm from post-hoc correction (Group DRO, JTT, last-layer retraining) to early gradient steering.

**Differentiation from Prior Work**:
- vs Kirichenko 2022: They show core features exist; we explain WHY minority curvature stays high
- vs LaBonte 2026: They prove theoretical SGD prioritization; we provide empirical mechanism
- vs Group DRO: They reweight uniformly; we target specific gradient dynamics

---

## Experimental Design

**Dataset**: Waterbirds (primary), CelebA (validation)
**Model**: ResNet-50 pretrained on ImageNet
**Baselines**: Standard ERM, Group DRO, Update-Norm Parity

**Minimal Viable Experiment (MVE)**:
1. Compute SR₀ at initialization (5 seeds)
2. Track per-sample gradient norms, SR, WGA per epoch
3. Apply update-norm parity intervention
4. Compute lagged cross-correlations
5. (Optional) NTK width sweep {64, 1024}

**Estimated Compute**: ~20-30 GPU-hours

---

## Limitations

- Tested on Waterbirds; generalization to CelebA/ColorMNIST requires validation
- Assumes pretrained ResNet-50; training from scratch may differ
- Hessian eigenvalues approximated via power iteration (PyHessian)
- Update-norm parity may trade off average accuracy (monitor Pareto frontier)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 15 exchanges, all criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Per-sample normalization implementation; accuracy trade-off |

---

## Previous Failure Context

This hypothesis explicitly addresses failure modes from prior attempts:

| Hypothesis | Failure | How DCR Addresses |
|------------|---------|-------------------|
| h-c1 | Assumed shared eigenspaces | Treats orthogonality as consequence, not cause |
| h-e1 run1 | Expected CKA inversion | No CKA assumptions; focuses on gradient dynamics |
| h-e1 run2 | Expected background attribution | No attribution assumptions; focuses on curvature |
| h-m1 | Gradient direction opposite to predicted | Uses gradient MAGNITUDE, not direction |

---

*Phase: 2A - Hypothesis Generation via 6-Perspective Tikitaka Discussion*
*Total discussion time: ~15 exchanges*
*Ready for: Phase 2B - Research Planning*
