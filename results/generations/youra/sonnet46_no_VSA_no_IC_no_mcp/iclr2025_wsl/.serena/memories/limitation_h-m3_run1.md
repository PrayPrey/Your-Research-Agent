# Limitation Record: h-m3 (Run 1)

**Date:** 2026-08-27T07:30:00+00:00
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Canonicalization (Condition D: both scaling + sign-flip) before NFT encoding does not improve Spearman ρ over raw weights (Condition A) at N=500 zoo size. The random normalization control (Condition E) consistently outperforms Condition D on all 3/3 labels and 3/3 seeds, suggesting sign-flip canonicalization may destroy within-batch variance that NFT relies on for model discrimination.

## Failed Checks

- P1: Δρ_D-A in right direction (>0.05) but CIs do not exclude 0 (n=50 test set too small, CI width ~0.6)
- P2: ρ_D < ρ_E on all 3/3 tasks (0/3 pass, required 2/3)

## Partial Results

| Metric | Value |
|--------|-------|
| Δρ_D-A test_accuracy | +0.058 (CI: [-0.345, +0.241]) |
| Δρ_D-A gen_gap | +0.053 (CI: [-0.298, +0.327]) |
| Δρ_D-A learning_rate | +0.077 (CI: [-0.290, +0.346]) |
| ρ_E vs ρ_D (test_accuracy) | +0.068 vs +0.004 (E wins) |
| ρ_E vs ρ_D (gen_gap) | +0.034 vs +0.022 (E wins) |
| ρ_E vs ρ_D (learning_rate) | +0.154 vs +0.059 (E wins) |

## Experiment Summary

NFT trained from scratch on Schürholt MNIST zoo (N=500; train=400, val=50, test=50) across 3 seeds. All conditions produce Spearman ρ near 0 (range -0.21 to +0.15). Condition E (random normalization control) consistently outperforms Condition D (both canonicalizations). Consistent with H-M2: PCA EVR improves with canonicalization but downstream property regression does not improve at N=500.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to H-C1 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial (likely dataset size — N=500 too small)
3. Alternative approaches: larger zoo (N>5000), frozen pretrained NFT encoder, or ensemble approaches
4. The E>D finding: investigate whether sign-flip canonicalization reduces within-batch diversity

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-27T07:30:00+00:00*
*For cross-phase reference*
