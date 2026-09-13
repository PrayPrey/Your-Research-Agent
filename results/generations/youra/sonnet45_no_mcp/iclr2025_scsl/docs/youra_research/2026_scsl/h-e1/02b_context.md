# Per-Hypothesis Context: H-E1

**Generated:** 2026-04-24
**Source:** Phase 2B Verification Plan (JIT-extracted)

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Statement:** Under standard ERM and Group-DRO training on Waterbirds, if we measure Marchenko-Pastur-defined curvature subspace alignment A(w), then ERM solutions will exhibit significantly higher alignment than Group-DRO solutions, because ERM exploits spurious features that create sharp, concentrated curvature.

**Rationale:** This hypothesis establishes that the geometric signature (curvature orientation difference) exists and is measurable. It validates that ERM and DRO solutions occupy geometrically distinct regions before testing the causal mechanism.

---

## Experimental Setup

### Dataset
- **Name:** Waterbirds (primary)
- **Type:** standard
- **Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)
- **Path:** Downloaded via group_DRO scripts
- **Justification:** Ground-truth spurious labels enable behavioral phenotyping (spurious vs core solutions). Waterbirds: background spurious correlation

### Model
- **Architecture:** ResNet-50
- **Type:** Standard CNN with skip connections
- **Source:** torchvision.models
- **Justification:** Li et al. show ResNets produce analyzable loss landscapes with skip connections creating flat minima. Sufficient over-parameterization for Marchenko-Pastur assumptions. Standard architecture enables reproducibility.

---

## Variables

**Independent Variable:** Training Method (ERM vs Group-DRO)
**Dependent Variable:** Curvature Subspace Alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
**Controlled Variables:**
- Batch size (32, 128, 512)
- Architecture (ResNet-50)
- Random seed (20 runs)

---

## Baselines & Comparison Targets

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard ERM | 85-90% average, 60-75% worst-group | Waterbirds |
| Group-DRO | 75-80% worst-group (requires group labels) | Waterbirds |

---

## Success Criteria (PoC: Direction-based)

**Primary:** ERM alignment > DRO alignment (p<0.01, Cohen's d>0.8)
**Secondary:** Effect stable across 3 batch sizes (32, 128, 512)

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)
**Blocks:** H-M1, H-M2, H-M3, H-M4

---

## Gate Condition

**Gate Type:** MUST_WORK
**Pass Condition:** ERM vs DRO alignment distributions significantly different (p<0.01, d>0.8)
**Fail Action:** STOP—geometric signature doesn't exist, abandon hypothesis

---

*Extracted from 02b_verification_plan.md Section 2.2*
