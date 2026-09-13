# Reflection Report: h-m1

**Hypothesis ID:** h-m1  
**Gate Type:** MUST_WORK  
**Gate Result:** FAIL  
**Reflection Outcome:** ROUTED_TO_PHASE_0  
**Date:** 2026-08-28

---

## Gate Failure Summary

**Hypothesis Statement:** Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns, measurable via symmetry differential (GNN >30% gap between within-layer vs across-layer perturbations, Transformer <10%)

**Gate Criteria:**
- ✓ Transformer differential < 10%: **PASS** (0.0%)
- ✗ GNN differential > 30%: **FAIL** (20.0%)

**Overall Result:** FAIL (1/2 criteria met, critical criterion failed)

---

## Experiment Analysis

### What Succeeded
1. **Transformer Global Behavior:** Achieved 0% differential, demonstrating perfect global uniformity (insensitive to both perturbation types equally)
2. **Directional Signal:** GNN showed 20% differential (within: 40%, across: 20%), indicating some local bias exists
3. **Implementation Validation:** Both models trained successfully and produced measurable results

### What Failed
1. **GNN Differential Magnitude:** 20% < 30% threshold
2. **Critical PoC Limitation:** Simplified GNN (linear layers) instead of true E(n)-Equivariant GNN
3. **Small Dataset:** 30 models may be insufficient for robust signal
4. **Simulated Labels:** Used parameter count proxy instead of real test accuracy

### Root Cause
**Primary:** PoC implementation lacks equivariance guarantees. Simplified linear GNN cannot enforce permutation-symmetric message passing required for local pattern specialization.

**Contributing Factors:**
- Dataset size (30 vs 100+ recommended)
- Training duration (10 epochs vs 50 recommended)
- Label quality (simulated vs real)

---

## Reflection Decision: ROUTED_TO_PHASE_0

**Rationale:**

MUST_WORK gate failure indicates fundamental implementation gap. While directional evidence exists (20% differential shows GNN has local bias), the magnitude shortfall suggests the hypothesis may require:

1. **Architectural Correction:** True EGNN implementation with verified equivariance
2. **Experimental Scale:** Larger dataset + extended training for robust validation
3. **Hypothesis Refinement:** Lower threshold (>15%) OR reframe mechanism claim

**Decision:** Route to Phase 0 for hypothesis redesign.

Per MUST_WORK gate protocol, complete failure (1/2 critical criteria) triggers Phase 0 brainstorming to:
- Re-assess hypothesis feasibility
- Explore alternative mechanisms
- Consider threshold adjustments based on PoC findings

---

## Lessons Learned

1. **PoC Simplification Risk:** Simplified architectures can mask true mechanism properties
2. **Equivariance Critical:** GNN local bias requires provable permutation equivariance, not approximation
3. **Directional Evidence ≠ Validation:** 20% signal suggests mechanism plausible but needs proper implementation
4. **Gate Threshold Calibration:** 30% may be optimistic for PoC-level validation

---

## Recommendations for Phase 0

**Option 1: Strengthen Implementation (Preferred)**
- Use torch_geometric.nn.EGNNConv (true equivariance)
- Scale to 100+ models
- Train 50 epochs
- Re-validate with same 30% threshold

**Option 2: Adjust Hypothesis**
- Lower gate threshold to >15% (evidence-based)
- Reframe claim: "GNN shows measurable local bias (>15%)" vs "strong local specialization (>30%)"
- Keep PoC-level implementation

**Option 3: Pivot Mechanism**
- Explore alternative architectural comparisons
- Consider graph-free local pattern detectors
- Investigate attention pattern analysis instead

---

**Next Phase:** Phase 0 - Hypothesis Brainstorming  
**Status:** FAILED  
**Route:** /phase0-brainstorm
