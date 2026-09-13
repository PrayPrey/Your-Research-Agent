# Phase 4 Failure Record: h-m2 (Run 2 — Step 06b Reflection)

**Date:** 2026-05-21T04:10:00Z
**Hypothesis:** h-m2
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Statement

Under weight space analysis on Small CNN Zoo checkpoint trajectories, if weight vectors are projected onto permutation orbit directions and GL orbit directions, then Var_perm / (Var_perm + Var_GL) > 0.60, because NFN's success (tau>0.93) using only permutation equivariance implies that permutation orbits capture the dominant functional variation in model zoo checkpoint geometry. GATE: if ratio < 0.60, pivot to hybrid orbit-PE + GL trace features before H-M3.

## Performance Data

| Metric | Measured | Threshold | Result |
|--------|----------|-----------|--------|
| var_ratio_mean (overall) | 0.3479 ± 0.054 | > 0.60 | FAIL |
| Conv2d layer ratio | 0.637 | > 0.60 | PASS |
| Linear layer ratio | 0.133 | > 0.60 | FAIL |
| n_models | 1000 | ≥ 100 | PASS |
| Epoch 0 ratio | ~0.49 | - | - |
| Epoch 50 ratio | ~0.28 | - | - |

## Root Cause Analysis

- **Primary failure:** Linear layers are dominated by GL orbit variance (ratio=0.133), not permutation orbits. The assumption that permutation equivariance explains NFN's success generalizes to linear layers was incorrect.
- **Layer asymmetry:** Conv2d layers (ratio=0.637) DO show permutation orbit dominance, validating orbit-PE for convolutional weights. The failure is localized to Linear/FC layers.
- **Training dynamics:** The ratio decreases monotonically during training (epoch 0: ~0.49 → epoch 50: ~0.28), suggesting that as linear layers learn, GL-type variation becomes increasingly dominant. This is a fundamental property of how FC weights optimize.
- **NFN vs this hypothesis:** NFN's success with permutation equivariance likely stems from operating on CNN checkpoints where Conv2d layers dominate parameter count, not from general orbit dominance across all layer types.

## Reflection Decision

**Gate Type:** MUST_WORK
**Gate Result:** FAIL (not PARTIAL)
**Reflection Outcome:** ROUTED_TO_PHASE_0

FAIL (not PARTIAL) → No self-modification possible. The fundamental assumption that permutation orbits dominate GL orbits across all layer types in CNN zoo is empirically false for Linear layers. This is not an implementation issue but a mathematical property of how FC weights distribute in orbit space.

## Key Insights for Phase 0 (Pivot Directions)

1. **Hybrid orbit-PE + GL trace features is the correct pivot** (as specified in h-m2 gate condition): incorporate both permutation orbit and GL orbit information into the positional encoding.
2. **Layer-specific encoding** may be needed: Conv2d layers → permutation orbit PE; Linear layers → GL orbit PE or hybrid.
3. **The Conv2d result (0.637) is a positive signal**: orbit-PE works for convolutional layers, which are the primary building block of CNN zoo. H-M3 may still be viable with hybrid approach.
4. **SVHN dataset had 0 models** — only CIFAR-10-GS was used. The stability check was inconclusive due to missing SVHN data.

## Dependent Hypotheses Cascade

- **h-m3**: BLOCKED by h-m2 FAIL — "Hybrid orbit-PE + GL trace features pivot required"
- **h-c1**: prerequisites include h-m2 (indirectly blocked)

## Lessons Learned

1. Do NOT assume NFN's permutation-equivariance success implies permutation orbit variance dominance for all layer types — NFN is primarily CNN-focused.
2. Linear/FC layers have fundamentally different orbit structure than convolutional layers — GL orbits dominate in trained FC layers.
3. Future hypotheses should decompose by layer type and measure orbit dominance separately.
4. The epoch-trajectory analysis (ratio decreases during training) is a novel finding worth preserving for Phase 6 paper.
5. The PIVOT condition was correctly specified in h-m2 gate: "if ratio < 0.60, pivot to hybrid orbit-PE + GL trace features" — this pre-specified pivot should guide Phase 0.

## For Phase 0 Brainstorming

- Preserve: h-e1 (PASS), h-m1 (PASS) results — orbit-PE is computable and efficient
- Incorporate: hybrid orbit-PE + GL trace features for Linear layers
- New hypothesis should replace h-m2's assumption with: "hybrid encoding captures dominant variance for both Conv2d and Linear layers"
- Consider: separate orbit-PE for Conv2d (permutation), and GL-trace PE for Linear layers

---
*Reflection recorded at: 2026-05-21T04:10:00Z*
*Step 06b executed after Phase 4 FAIL gate for h-m2*
*For cross-phase reference — primary reader: Phase 0 brainstorming*
