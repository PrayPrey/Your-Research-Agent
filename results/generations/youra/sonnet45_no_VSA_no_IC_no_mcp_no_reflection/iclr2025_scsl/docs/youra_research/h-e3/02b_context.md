# Hypothesis Context: h-e3

**Generated:** 2026-08-28T23:29:00Z
**Source:** 02b_verification_plan.md (Phase 2B)

---

## Hypothesis Information

**ID:** h-e3  
**Type:** EXISTENCE  
**Statement:** GradCAM temporal ratio R_temporal(t) decreases monotonically from epoch 5 to 50 (Kendall τ < -0.7, p < 0.05)

**Gate:** SHOULD_WORK  
**Prerequisites:** [h-e1]

---

## Experimental Approach (from Phase 2B)

- Compute GradCAM saliency maps at each epoch on Waterbirds, CelebA, NICO++
- R_temporal(t) = A_spurious / (A_spurious + A_core) where A = pixel attribution in respective regions
- Statistical Test 5: Kendall τ correlation between R_temporal(t) and epoch t
- Statistical Test 6: Cross-method consistency (R_temporal vs E_s from ablation training)

**Timeline:** 2 weeks  
**Risk:** MEDIUM (novel diagnostic method - may require calibration)

---

## Dataset Selection (from Phase 2B Section)

**Controlled Variables:**
- Datasets: Waterbirds (background), CelebA (gender), NICO++ (context)
- Models: ResNet-50
- Optimizer: SGD with momentum 0.9
- Learning Rate: Dataset-specific (cosine annealing or step decay per standard)
- Random Seeds: 10 per experiment (statistical power)

---

## Success Criteria

**Statistical Tests:**
- Test 5: Kendall τ < -0.7 AND p < 0.05
- Test 6: Spearman ρ > 0.7 (cross-method consistency)

**Gate Logic:**
- SHOULD_WORK: Failure does not block Phase 5 progression
- Supporting evidence for temporal gradient hypothesis

---

## Prerequisite Context

**h-e1 Status:** VALIDATED  
**h-e1 Results:**
- Temporal ordering confirmed: E_spurious=13, E_core=17, Δ=4 epochs (CMNIST)
- Gate threshold exceeded with 2× margin
- Proven: Spurious features converge earlier than core features

**Implication for h-e3:**
- h-e1 validated temporal ordering via gradient convergence
- h-e3 extends to continuous monitoring via GradCAM saliency
- Cross-method consistency test links both approaches

---

## Dependencies

**Depends on:** h-e1 (VALIDATED ✓)  
**Enables:** None (leaf hypothesis)  
**Blocks if Failed:** None (SHOULD_WORK gate)

---

*This context file is auto-generated from Phase 2B verification plan.*
*Used by Phase 2C experiment design workflow.*
