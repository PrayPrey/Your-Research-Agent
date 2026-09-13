# Phase 2B: Verification Plan
## H-DCR-v1: Differential Convergence Rate Mechanism

**Generated:** 2026-08-09T18:00:00Z  
**Main Hypothesis:** Under ERM training on group-imbalanced data, majority groups converge faster, leaving minority groups in sharper regions (SR > 1.0).  
**Archon Project:** `eeeba21b-74de-43ac-8faf-357356ae48bb`

---

## Sub-Hypotheses

### H-E1: SR ≈ 1 at Initialization (MUST_WORK)
- **Statement:** No intrinsic curvature asymmetry at random initialization
- **Test:** Compute SR₀ at random init, average over 5 seeds
- **Success:** SR₀ ∈ [0.9, 1.1] with 95% CI including 1.0
- **Falsification:** SR₀ > 1.1 with CI excluding 1.0
- **Status:** READY (no prerequisites)
- **Archon Task:** `752aa498-bfb4-4815-b686-6ef0531478b0`

### H-M1: Gradient Ratio Decay Precedes SR Divergence (MUST_WORK)
- **Statement:** Per-sample gradient ratio decay precedes SR divergence
- **Test:** Lagged cross-correlation τ_r→SR over epochs [-5, +5]
- **Success:** τ_r→SR > 0 with 95% CI excluding zero across seeds
- **Falsification:** τ_r→SR ≤ 0 or CI includes zero
- **Prerequisites:** H-E1
- **Archon Task:** `b149124e-1a26-4a37-86a8-e03a05ff4644`

### H-M2: Update-Norm Parity Attenuates SR (SHOULD_WORK)
- **Statement:** Update-norm parity intervention reduces SR divergence
- **Test:** Compare SR trajectories: baseline vs parity-enforced training
- **Success:** SR ≤ 1.1 sustained under parity vs SR > 1.2 baseline
- **Falsification:** SR remains > 1.2 despite parity intervention
- **Prerequisites:** H-E1
- **Archon Task:** `b2df4bdf-4012-48c3-b21b-6789a7e8168f`

### H-M3: SR Reduction Improves WGA (SHOULD_WORK)
- **Statement:** SR reduction correlates with worst-group accuracy improvement
- **Test:** Mediation analysis correlating ΔSR with ΔWGA
- **Success:** ΔSR ≤ -0.2 corresponds to ΔWGA ≥ +2pp (95% CI)
- **Falsification:** No significant correlation between ΔSR and ΔWGA
- **Prerequisites:** H-M2
- **Archon Task:** `e1dff7e4-3013-481b-8bc6-c809b39f3c01`

---

## Dependency Graph

```
H-E1 (READY) ──┬──► H-M1 (NOT_STARTED)
               │
               └──► H-M2 (NOT_STARTED) ──► H-M3 (NOT_STARTED)
```

## Risk Analysis

| Hypothesis | Risk Level | Mitigation |
|------------|------------|------------|
| H-E1 | LOW | Single measurement, 5 seeds sufficient |
| H-M1 | MEDIUM | Requires per-epoch gradient logging infrastructure |
| H-M2 | MEDIUM | Intervention implementation complexity |
| H-M3 | LOW | Mediation analysis on H-M2 data |

## Timeline Estimate

| Phase | Hypothesis | Duration |
|-------|------------|----------|
| 2C | H-E1 | 1 day |
| 2C | H-M1 | 1 day |
| 2C | H-M2 | 1 day |
| 2C | H-M3 | 1 day |
| 3-4 | All | 5-7 days |
| 5 | Baseline comparison | 2 days |

## Experimental Setup

- **Dataset:** Waterbirds (kohpangwei/group_DRO)
- **Model:** ResNet-50 pretrained on ImageNet
- **Optimizer:** SGD with momentum
- **Seeds:** 5
- **Evaluation samples:** Full test set (~5,000 samples)

## Dialectical Analysis

- **Thesis (M2):** Differential convergence rate causes SR > 1.0
- **Antithesis (M3):** Intrinsic data geometry causes SR > 1.0
- **Synthesis:** H-E1 discriminates; if SR₀ ≈ 1, intrinsic geometry ruled out

---

**Next Step:** Phase 2C with H-E1 (first READY hypothesis)
