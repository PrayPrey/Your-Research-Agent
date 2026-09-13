# Phase 2A Extended: Hypothesis Summary (Phase 2B Ready)

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-AETR-DP-01
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Adaptive event-triggered recalibration with dynamic differential privacy budget allocation reduces computational cost by 40-60% compared to periodic recalibration while maintaining Expected Calibration Error (ECE) ≤ 0.05 and satisfying (ε, δ)-differential privacy guarantees with ε ≤ 1.0 under resource-constrained deep learning deployments with distribution shift.

**Core Innovation:**
Cross-domain transfer of Event-Triggered Model Predictive Control (Gräfe 2025) to ML calibration, combined with adaptive threshold mechanism τ(t) = τ₀ · (1 + α · budget_depletion_ratio) that preserves privacy budget for severe shifts.

**Gap Addressed:** Gap 2 from Phase 1 - Calibration-Privacy Trade-Off Under Computational Constraints

**Confidence Level:** 0.82 (FEASIBLE - from Phase 2A Judge)

---

## Research Variables

### Independent Variables (Manipulated)
- **τ₀:** Initial ECE trigger threshold [0.01, 0.10]
- **α:** Budget depletion sensitivity [0.1, 2.0]
- **ε₂:** Privacy budget for recalibration [0.1, 0.8]
- **ΔD:** Shift severity (KL divergence) [0.0, 2.0] nats

### Dependent Variables (Measured)
- **ECE_final:** Expected Calibration Error [0.0, 1.0]
- **C:** Computational cost (FLOPs or wall-clock time)
- **k:** Trigger count (number of recalibrations)
- **ε_used:** Total privacy budget consumed

### Controlled Variables
- ε₁ = 0.5 (training budget), ε_monitor = 0.05, δ = 10⁻⁵
- Model architecture (ResNet-50, VGG-16)
- Datasets (CIFAR-10, CIFAR-100)
- DP mechanism (Gaussian), Calibration method (DUC from Xie 2023)

---

## Testable Predictions

**P1 (Primary): Computational Cost Reduction**
- Adaptive achieves C_adaptive / C_periodic ∈ [0.4, 0.6] (40-60% reduction)
- While maintaining ECE ≤ 0.05 for moderate shifts (ΔD ∈ [0.5, 1.5] nats)

**P2 (Secondary): Adaptive Threshold Effectiveness**
- Late-stage trigger rate ≤ 50% of early-stage trigger rate
- k_late ≤ 0.5 × k_early when α ≥ 0.5

**P3 (Secondary): Privacy-Calibration Trade-off**
- ECE decreases monotonically with ε₂ for severe shifts (ΔD ≥ 1.0)
- ∂(ECE_final) / ∂(ε₂) < 0

**Falsification Criteria:**
- Cost reduction < 30% (C_adaptive / C_periodic > 0.7)
- ECE > 0.08 in >20% of scenarios
- Privacy violation (ε_used > ε_total) in any run
- No adaptive benefit (τ(t) doesn't increase with budget depletion)

---

## Causal Mechanism

```
Distribution Shift (ΔD)
    ↓
Calibration Degradation (ECE↑)
    ↓
Private ECE Monitoring (ε_monitor)
    ↓
ECE > τ(t)? ──NO──→ No action (save budget)
    │
    YES
    ↓
DP-Recalibration (consume ε₂/k)
    ↓
Budget Depletion ↑
    ↓
τ(t) ← τ₀ · (1 + α · depletion_ratio)
    ↓
Higher threshold for future triggers
    ↓
Budget preserved for severe shifts
```

**Key Evidence:**
- **Shift → ECE degradation:** Kebir & Tabia 2024
- **Event-triggering → 40-80% cost savings:** Gräfe 2025 (ET-MPC control theory)
- **DUC → ECE < 0.05:** Xie et al. 2023 (43 citations)
- **DP noise → calibration degradation:** Seif et al. 2025

**Key Tension:** Privacy budget scarcity - frequent recalibrations improve calibration but risk exhaustion

---

## Contributions

**Theoretical:**
1. First characterization of privacy-calibration-computation three-way trade-off
2. Formal analysis of event-triggered DP composition

**Methodological:**
3. Cross-domain transfer: Event-Triggered MPC → ML calibration (novel)
4. Adaptive budget-aware threshold τ(t) mechanism (novel)

**Practical:**
5. Deployable system for privacy-preserving edge calibration
6. 40-60% computational cost reduction vs. periodic baselines

---

## Experimental Design

**Design:** 3-Factor Factorial (Shift × τ₀ × α)
- **Conditions:** 36 (4 shift levels × 3 τ₀ × 3 α)
- **Replications:** 10 runs per condition
- **Total Experiments:** 360 runs

**Statistical Tests:**
1. **Cost Reduction:** Two-sided t-test on C_adaptive / C_periodic, α = 0.05
2. **Calibration Quality:** One-sample t-test against ECE = 0.05, α = 0.05
3. **Adaptive Effect:** Paired t-test on k_late vs. k_early
4. **Budget Effect:** Linear regression ECE ~ ε₂ for high-shift conditions

**Success Criteria:**
- Test 1: p < 0.05 AND mean cost ratio ∈ [0.4, 0.6]
- Test 2: p < 0.05 AND mean ECE ≤ 0.05
- Test 3: p < 0.05 (k_late < k_early)
- No privacy violations (ε_used ≤ ε_total in 100% of runs)

---

## Scope & Boundaries

**In-Scope:**
- Models: CNNs (ResNet-50, VGG-16, MobileNet)
- Datasets: CIFAR-10, CIFAR-100, ImageNet subset
- Shift: Gradual covariate/label shift (ΔD ≤ 2.0 nats)
- Context: Edge devices (C < 10 GFLOPs per recalibration)
- Privacy: (ε, δ)-DP with ε ∈ [0.1, 1.0], δ = 10⁻⁵

**Out-of-Scope:**
- Transformers, LSTMs, GANs
- Sudden adversarial shifts
- Cloud/datacenter (no resource constraints)
- Federated learning
- Other trustworthiness dimensions (fairness, robustness)

**Baselines:**
1. Periodic recalibration (fixed interval)
2. No recalibration (one-time calibration)
3. Oracle recalibration (infinite budget, perfect detection)

---

## Phase 2B Decomposition Preview

**SH1 (Existence):** Event-triggered recalibration reduces cost by 40-60% under moderate shift
- **Verification:** Compare trigger count and FLOPs between adaptive and periodic
- **Complexity:** LOW

**SH2 (Mechanism):** Adaptive τ(t) reduces late-stage recalibration rate by ≥50%
- **Verification:** Measure k_late / k_early ratio for adaptive vs. fixed threshold
- **Complexity:** MEDIUM

**SH3 (Comparison):** DP-recalibration maintains ECE ≤ 0.05
- **Verification:** Ablation study - DUC with DP vs. without DP vs. no recalibration
- **Complexity:** MEDIUM-HIGH

---

## Key Assumptions

1. **Distribution shift is gradual and detectable** (not sudden jumps)
2. **Privacy budget is pre-allocated** (ε₁ + ε₂ + ε_monitor ≤ ε_total)
3. **DUC is effective under moderate shift** (ΔD ≤ 1.5 nats)
4. **Computational cost model is accurate** (FLOPs reflect device constraints)
5. **ECE monitoring privacy leakage is bounded** (ε_monitor = 0.05 sufficient)

---

## Open Questions

**Technical:**
- Q1: Optimal privacy budget allocation ratio (ε₁ : ε₂ : ε_monitor)?
- Q2: Exact ℓ₂ sensitivity of ECE for Gaussian mechanism?
- Q3: Formal proof of control theory → ML calibration transfer?

**Methodological:**
- Q4: CIFAR-10-C (realistic) vs. synthetic shift (controlled)?
- Q5: How to set k_max without prior shift knowledge?

**Experimental:**
- Q6: Is N=10 replications sufficient for power=0.80?

**Practical:**
- Q7: Are real-world shifts gradual (assumption) or sudden?
- Q8: Does monitoring overhead negate FLOPs savings on specific hardware?

**Resolution Plan:**
- Q2, Q5: Resolve in Phase 2B (required for experiment design)
- Q3: Empirical validation acceptable if formal proof is hard
- Q6: Pilot study → adjust to N=15 if needed
- Q7, Q8: Discuss as limitations

---

## Related Work Summary

**Core Methods:**
- **Xie 2023 (DUC):** Calibration under shift (no DP, no triggering) - our base method
- **Gräfe 2025 (ET-MPC):** Event-triggered control - our inspiration (cross-domain)
- **Seif 2025:** DP efficiency techniques - our computational optimization
- **Kebir 2024:** Calibration on edge devices - our deployment context validation

**Theoretical Foundations:**
- **Razeghi 2022 (CLUB):** Complexity-leakage-utility framework - our theoretical lens
- **Zhao 2023 (MUST):** Privacy amplification - potential future enhancement

**Implementations:**
- **Opacus (Meta):** DP training framework - our ε₁ phase
- **DUC (Xie 2023):** Calibration method - our recalibration core

**Our Novelty:**
- First to combine event-triggering + DP + calibration
- Novel adaptive threshold τ(t) for budget preservation
- First three-way privacy-calibration-computation characterization

---

## Readiness Assessment

**✅ Ready:**
- Datasets available (CIFAR-10/100, CIFAR-10-C)
- DP framework ready (Opacus - 1600+ stars)
- Calibration method ready (DUC from Xie 2023)
- Theoretical foundations solid

**⚠️ Implementation Needed:**
- Event-triggering logic (cross-domain transfer from Gräfe 2025)
- Adaptive threshold mechanism (novel - implement from scratch)
- Integration of Opacus + DUC + triggering (3 codebases)

**Overall:** ✅ **READY for Phase 2B**
- Minor implementation risks
- Strong foundations (control theory + DP theory + calibration methods)
- Clear decomposition path (SH1 → SH2 → SH3)

---

## Next Steps

**Phase 2B Tasks:**
1. Decompose into 3-5 sub-hypotheses (SH1: existence, SH2: mechanism, SH3: comparison)
2. Resolve Q2 (ECE sensitivity bound) and Q5 (k_max selection) via formal analysis
3. Create verification roadmap with detailed experiment plans
4. Conduct power analysis to confirm N=10 replications sufficient

**Phase 2C Preparation:**
- Identify DUC reference implementation (GitHub)
- Draft pseudocode for adaptive threshold τ(t)
- Specify hardware requirements (GPU + Jetson Nano)
- Plan Opacus-DUC integration architecture

**Command to proceed:** `/phase2b-planning` with this document as input

---

**Full Details:** See `02a_extended_hypothesis_full.md` for complete scientific specification

*Generated using YouRA Phase 2A Extended Workflow (YOLO Mode)*
*Date: 2026-02-06*
*Session: Batch Processing - Task: iclr2023_trustml*
