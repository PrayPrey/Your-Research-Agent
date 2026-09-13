# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-04T03:40:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1
- **Gap Title**: No Per-Sample Hessian Trace Trajectory Methodology for Spurious Feature Detection
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Recursive Entry**: YES — 8 prior failure/superseded records loaded from Serena memories

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC (H-E3 existence + DFR application), MECHANISM (transient curvature asymmetry via margin polarization), PREDICTIONS (P1/P2/P3 pre-registered), NOVELTY (first per-sample trace trajectory + annotation-free curvature DFR), FEASIBILITY (h-e2-k reusable, K=50 confirmed), OBJECTIONS (epoch-0 control, independence, specificity all addressed)

### Key Insights
1. The scalar magnitude family (gradient norm + Hessian trace) consistently produces discriminative signals; directional and temporal-variance signals are exhausted by prior failures.
2. Per-sample fc Hessian trace decomposes algebraically as Tr(H_i^fc) ∝ ‖x_i‖² × p_i(1-p_i), connecting two independent signal channels: feature diversity (LaBonte 2024 spectral imbalance) and differential confidence (Phase I shortcut learning).
3. The trace ratio peak at t* is simultaneously the mechanism prediction AND the annotation-free t* selection criterion — no group labels needed.
4. Epoch-0 control is the decisive first gate (h-e2's pretrained artifact lesson applies).
5. 50-epoch training required to observe full rise-peak-decline trajectory.

### Breakthrough Moments
- **Exchange 5**: LaBonte 2024 spectral imbalance predicts per-sample trace asymmetry via feature diversity (‖x_i‖² channel), distinguishing from "high loss = high trace" confound.
- **Exchange 9**: Algebraic decomposition reframed as explanation of signal channel (not falsifier).
- **Exchange 15**: Trace ratio PEAK (not monotonic rise) identified as mechanism prediction — minority must be near boundary, not confidently wrong.
- **Exchange 13**: 50-epoch training requirement established to capture Phase I→II inflection.

---

## Final Hypothesis

### Title
**H-E3**: Per-Sample Last-FC Hessian Trace Trajectory as Annotation-Free DFR Proxy

### Core Claim
Under ERM training with SGD on Waterbirds (ResNet-50, ImageNet pretrained, 95% spuriosity, SGD, 50 epochs, checkpoints at t∈{0,1,5,10,20,50}), IF per-sample last-fc Hessian trace (K=50 Hutchinson via torch.func vmap+vjp) is measured at each checkpoint, THEN the trace ratio R(t) = mean_minority_trace(t) / mean_majority_trace(t) rises from ≈1.0 at initialization, reaches a peak at t* (argmax_t R(t)), and provides a predictive signal (AUROC ≥ 0.85 at t*, epoch-0 AUROC < 0.70), BECAUSE ERM spurious feature exploitation creates differential loss landscape curvature: majority samples gain confidence (low p(1-p), flat loss surface) while minority samples remain near the decision boundary (high p(1-p), curved loss surface).

### Mechanism
ERM spurious feature exploitation (Phase I, LaBonte 2026) causes majority samples to gain confidence rapidly (p→1, low p(1-p)), while minority samples remain near the decision boundary (p≈0.5, high p(1-p)). Combined with minority feature diversity advantage (LaBonte 2024 spectral imbalance: λ₁^min > λ₁^maj), trace Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) is systematically elevated for minority samples. Peak at t* identifies Phase I/II boundary; top-k% trace at t* provides annotation-free DFR proxy.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| **P1 (PRIMARY)** | AUROC ≥ 0.85 at t* (argmax R(t)); epoch-0 AUROC < 0.70; Spearman ρ ≥ 0.8 | All three in ≥4/5 seeds | epoch-0 AUROC ≥ 0.70 OR AUROC(t*) < 0.80 in ≥2 seeds OR ρ < 0.6 |
| **P2** | ΔAUROC ≥ 0.10 over loss-only within confidence bins (width 0.02); KS p < 0.01 | Both in ≥4/5 seeds | ΔAUROC < 0.05 or KS non-significant across all bins |
| **P3** | Trace-guided DFR WGA ≥ 85% AND > loss-DFR by ≥5% absolute | Both in ≥4/5 seeds | WGA < 80% in ≥2 seeds OR no improvement over loss-DFR |

---

## Novelty

**New contribution**: First per-sample Hessian trace trajectory measurement across ERM training checkpoints for minority/majority discrimination. First annotation-free DFR proxy using second-order curvature statistics.

**How it differs from prior work**:
- vs DFR (Kirichenko 2022): No balanced validation with implicit group annotations required
- vs JTT/AFR/SELF/EVaLS: First second-order proxy; all others use first-order loss/gradient
- vs LaBonte 2024 (spectral imbalance): Dynamic per-sample training signal vs static group-level covariance
- vs LaBonte 2026 (SGD Phase I/II theory): First empirical validation on real Waterbirds data with ResNet-50

---

## Experimental Design

**Dataset**: Waterbirds v1.0 at `/home/PrayPrey/data/waterbirds_v1.0/` (4795 train, 4 groups, 5% minority)

**Model**: ResNet-50 (IMAGENET1K_V1), fc replaced to nn.Linear(2048,2) before load_state_dict

**Checkpoints**: t ∈ {0, 1, 5, 10, 20, 50}; 5 seeds

**Trace computation**: K=50 Rademacher Hutchinson via torch.func vmap+vjp on last-fc only; h-e2-k pipeline reusable

**DFR pipeline**: izmailovpavel/spurious_feature_learning; C_OPTIONS=[1.,0.7,...,0.01]; REG="l1"; top-k% trace selector replacing balanced validation

**Baselines**: ERM, Oracle DFR, Loss-DFR, Gradient-norm-DFR, JTT

**Implementation reference**: `src/h_e2_k/run_experiment.py` (h-e2-k validated pipeline)

---

## Limitations

- Limited to Waterbirds 95% spuriosity; generalization to other datasets deferred to Phase 5
- Last-fc trace only; full-network trace extension deferred
- Mechanism contingency: minority must remain near decision boundary (p∈[0.3,0.7]) during Phase I
- 95% spuriosity may be a special case; lower spuriosity behavior unknown
- Background-swap augmentation approximates "clean" condition using existing Waterbirds metadata

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-E3 |
| **Discussion Convergence** | All 6 criteria met at exchange 15 |
| **Clarity Verified** | YES |
| **Remaining Concerns** | epoch-0 AUROC control (FIRST GATE); minority confidence pilot; 50-epoch training |
| **Pilot Recommended** | YES — 1 seed, 5 epochs before committing to full 5-seed 50-epoch run |

---

*Phase 2A Complete — Ready for Phase 2B*
