# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-12T14:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1-loss-trajectory
- **Gap Title**: Per-Sample Loss Trajectory Analysis for Spurious Detection
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 18

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 18

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) with genuine disagreement and resolution across all personas.

### Key Insights
- Loss trajectory SHAPE (onset delay) is distinct from loss landscape GEOMETRY, avoiding the H-M1 failure mode
- Onset delay captures the TIMING of when learning begins, not just whether learning occurs
- Single-run paradigm is more efficient than two-stage methods like JTT

### Breakthrough Moments
- Exchange 6: Distinguishing "delayed onset" from "slow throughout" resolved the apparent contradiction with LA-SSL findings
- Exchange 12: Two-phase single-run design (detect then intervene) addressed the intervention confound concern
- Exchange 15: Connection to bandit literature opened theoretical grounding for adaptive detection

---

## Final Hypothesis

### Title
Loss Trajectory Onset Delay for Spurious Detection (H-LT1)

### Core Claim
Under standard ERM training of image classifiers on datasets with spurious correlations, if onset delay $d_i$ (epochs until 10% loss reduction) exceeds the early detection threshold $T_{early}$ (20% of total training), then the sample is enriched for minority-group membership, because simplicity bias causes majority-group samples to converge first on easily-learned spurious correlations.

### Mechanism
1. **Simplicity bias**: Models learn "easy" patterns first
2. **Spurious features are easier**: Background correlations provide strong, consistent signal
3. **Majority samples have redundant cues**: Both spurious and core features predict the label
4. **Minority samples lack shortcuts**: Require core feature learning
5. **Result**: Majority samples show fast loss reduction; minority samples show delayed onset

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| P1 (Primary) | At $T_{early}=20$, samples with $d_i > T_{early}$ have minority-group enrichment | Precision > 0.5 AND Recall > 0.3 |
| P2 | Upweighting improves WGA over ERM baseline | WGA ≥ 3% improvement AND ≥ 50% of JTT |
| P3 | Threshold transfers across datasets | CelebA minority precision > 0.4 |
| P4 | Onset delay correlates with group, not difficulty | r(d_i, group) > 0.4 AND r(d_i, confidence) < r(d_i, group) |

---

## Novelty

**Paradigm:** Adaptive Single-Run (ASR) robustification

**Key Innovation:** Unlike JTT (two-stage), SPARE (fixed epoch threshold), or LA-SSL (aggregate speed), we propose per-sample adaptive detection using continuous onset delay, enabling intervention during training without a separate identification phase.

**Differentiation:**
- vs. JTT: Continuous signal (not binary), single run (not two-stage)
- vs. SPARE: Per-sample adaptive (not fixed epoch)
- vs. LA-SSL: Trajectory shape (not aggregate speed)

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| Dataset | Waterbirds (primary), CelebA (transfer) |
| Model | ResNet-18 (ImageNet pretrained) |
| Optimizer | SGD (lr=0.001, momentum=0.9) |
| Epochs | 100 total (detection: 1-20, intervention: 21-100) |
| Baselines | ERM, JTT, SPARE |

---

## Limitations

- Requires ground-truth group labels for evaluation (not for training)
- Detection threshold $T_{early}$ may need dataset-specific tuning
- Effect size may be modest (1-3% WGA improvement)
- More complex than JTT's simple two-stage approach
- May not generalize to NLP tasks (different trajectory dynamics)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 18 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (empirical uncertainties to be resolved by testing) |

---

## Previous Failure Context

**H-M1 FAILED:** Hessian trace analysis disproven (+363% increase, not decrease).

**Constraint Applied:** This hypothesis explicitly avoids loss landscape geometry, using observable loss VALUES (trajectory shape) instead of optimizer geometry properties.

---
