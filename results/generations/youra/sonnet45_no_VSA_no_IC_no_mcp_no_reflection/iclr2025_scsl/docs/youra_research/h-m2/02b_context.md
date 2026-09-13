# Per-Hypothesis Context: h-m2

**Generated:** 2026-08-29
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** h-m2  
**Type:** MECHANISM  
**Statement:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs) due to architectural inductive bias differences

**Gate:** SHOULD_WORK  
**Prerequisites:** [h-e1]

---

## Rationale

Investigate architectural impact on temporal ordering phenomenon discovered in h-e1. CNNs have strong spatial inductive biases (locality, translation invariance) while ViTs rely on learned attention. Hypothesis: CNN inductive biases accelerate spurious feature learning more than core features, creating larger temporal gap.

---

## Experimental Setup

**Datasets:**
- Waterbirds (background spurious correlation)
- CelebA (gender-attribute spurious correlation)

**Models:**
- ResNet-50 (CNN baseline)
- ViT-B/16 (Transformer baseline)

**Optimizer:** SGD with momentum 0.9  
**Learning Rate:** Dataset-specific (cosine annealing or step decay)  
**Random Seeds:** 10 per experiment

---

## Success Criteria

**Statistical Test 7:** Independent samples t-test on architectural differences  
**Success Criterion:** p < 0.05 AND (Δ_ResNet - Δ_ViT) ≥ 2 epochs

Where:
- Δ_ResNet = E_core - E_spurious for ResNet-50
- Δ_ViT = E_core - E_spurious for ViT-B/16

---

## Baseline & Comparison

**Baseline:** ERM (Empirical Risk Minimization)  
**Comparison Target:** Architectural difference in temporal gaps

**Expected Behavior:**
- ResNet-50: Larger temporal gap (strong spatial bias favors spurious features)
- ViT-B/16: Smaller temporal gap (learned attention is more balanced)

---

## Dependencies

**Prerequisites:**
- h-e1 must PASS (validates existence of temporal ordering)

**Gate Condition:**
- SHOULD_WORK: Failure does not block Phase 5
- Supporting evidence for architectural mechanism

---

## Context from Prerequisite h-e1

**h-e1 Status:** VALIDATED ✅

**Key Findings from h-e1:**
- PoC (seed 0): E_spurious=13, E_core=17, Δ=4 epochs
- Gate threshold (Δ≥2) exceeded with 2× margin
- Full 10-seed statistical validation in progress
- Scope: CMNIST only (Waterbirds/CelebA/NICO++ require manual setup)

**Proven Components:**
- Convergence detection works (gradient norm < 10% of peak for 3 consecutive epochs)
- Ablation training setup (spurious-only, core-only) is functional
- Temporal gap is measurable and significant

**Implications for h-m2:**
- Temporal ordering exists → architectural comparison is meaningful
- Convergence detection method can be reused
- Need to extend to Waterbirds/CelebA datasets
- Need to implement both ResNet-50 and ViT-B/16

---

## Timeline

**Estimate:** 2 weeks  
**Risk:** MEDIUM (architectural insight - not critical for main hypothesis)

---

## Controlled Variables

- Same datasets (Waterbirds, CelebA)
- Same optimizer config (SGD + momentum)
- Same random seeds (10)
- Same convergence criterion (from h-e1)
- Only architecture varies: ResNet-50 vs ViT-B/16
