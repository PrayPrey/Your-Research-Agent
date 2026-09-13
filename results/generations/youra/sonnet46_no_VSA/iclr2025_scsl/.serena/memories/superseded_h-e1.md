# Superseded Hypothesis Record

**Date:** 2026-08-03T20:00:00Z
**Hypothesis:** h-e1
**Superseded By:** h-e1-v2 (to be defined in /phase2a-dialogue)
**Status:** SUPERSEDED

## Supersede Reason

Gradient direction cosine similarity to within-group centroid does not discriminate minority from majority groups at AUROC ≥ 0.80. Core discriminator design is flawed (within-group centroid comparison measures cohesion, not between-group distinctiveness). The mechanism itself has partial merit (y=1 AUROC=0.732 at epoch 1), but the hypothesis formulation requires fundamental redesign — not a parameter tweak.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.35 |
| Recommendation | SUPERSEDED |
| Reasoning | Within-centroid cosine similarity is the wrong discriminator for minority detection. A between-centroid discriminator (does sample i align more with minority centroid or majority centroid within same class y?) is needed. Sign assumption was also inverted — minority groups showed slightly higher within-group alignment, not lower. |

## Key Experimental Findings

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AUROC overall (seed 0, epoch 1) | 0.4360 | ≥ 0.80 | FAIL |
| AUROC y=0 (seed 0, epoch 1) | 0.3450 | ≥ 0.70 | FAIL |
| AUROC y=1 (seed 0, epoch 1) | 0.7321 | ≥ 0.70 | PARTIAL PASS |
| Seeds passing primary | 0/1 | ≥ 4/5 | FAIL |
| Pipeline execution | ✓ | — | PASS |
| Mechanism correctness (shapes, normalization) | ✓ | — | PASS |

## Root Cause Analysis

1. **Wrong discriminator**: Within-group centroid similarity measures per-group coherence, not inter-group separability. Minority detection requires comparing each sample against minority vs. majority centroids within same class y.
2. **Inverted sign assumption**: Minority groups (N=56, N=184) showed slightly *higher* within-group alignment (0.845, 0.845) than majority group 0 (0.830) — opposite of hypothesis assumption.
3. **t*=1 not strongly predictive**: At epoch 1, ERM model barely diverges from pretrained weights; gradient direction signal is weak. Signal may strengthen at later checkpoints (epoch 10–50).
4. **Dominant spurious group**: Group 3 (majority y=1, water) has highest alignment (0.870), confirming ERM exploits spurious correlation — but this alone doesn't yield discriminative AUROC.

## What Showed Promise

- y=1 AUROC = 0.732 (above 0.70 secondary threshold) — gradient direction carries some class-1 discriminative signal
- Pipeline runs end-to-end without errors; all tensor shapes correct (N, 4096)
- Mechanism implementation is correct (unit-normalized, no NaN centroids, deterministic)
- Sign correction from negated to raw alignment → AUROC ≈ 0.564 (still insufficient but directionally informative)

## Redesign Recommendations for h-e1-v2

1. **Between-centroid discriminator**: For each sample i with class y, compute:
   - sim_minority = cosine(grad_i, centroid_minority_y)
   - sim_majority = cosine(grad_i, centroid_majority_y)
   - score = sim_minority - sim_majority (or ratio)
2. **Multi-checkpoint evaluation**: Test at epoch 1, 5, 10, 25, 50 to find optimal t*
3. **Remove sign assumption**: Let data determine direction (don't negate)
4. **Consider gradient norm**: Minority samples may have larger gradient norms due to higher loss — combine direction + magnitude

## Cascade Effects

No dependent hypotheses (h-e1 prerequisites: []).

## Timeline

1. Original hypothesis h-e1 formulated in Phase 2A
2. Implementation completed in Phase 3 (22/22 score)
3. Experiment executed: seed 0 only (early halt after AUROC 0.436)
4. Gate: FAIL (0/1 seeds passing primary threshold)
5. Reflection: SUPERSEDED (redesign discriminator, meaningful partial signal exists)
6. New direction: h-e1-v2 to be defined in /phase2a-dialogue

---
*Superseded at: 2026-08-03T20:00:00Z*
*For cross-phase reference*
