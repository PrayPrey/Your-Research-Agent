# Results

## Main Finding: Hypothesis Refuted

The CV-based detection mechanism achieves **AUC = 0.0**, decisively failing the ≥0.75 gate.

## CV Distribution

| Feature Type | CV Value | Expected |
|--------------|----------|----------|
| Background (spurious) | 0.0393 | Low (< 0.15) |
| Bird Type (core) | 0.0360 | High (> 0.20) |
| **Difference** | 0.0033 | — |

Both feature types show nearly identical CV values (~0.04). The hypothesized separation — spurious features with lower CV due to uniform emergence — does not manifest.

**Figure 2** shows the CV distribution: both features cluster in the same region with no separation.

## Direction Reversal

The hypothesis predicted: CV(spurious) < CV(core)

Observed: CV(spurious) = 0.0393 > CV(core) = 0.0360

The direction is marginally reversed, though the 0.0033 difference is within noise. With only 2 feature types, this reversal yields AUC = 0.0 (worse than random).

## Probe Trajectory Analysis

**Figure 4** shows probe accuracy trajectories across C values for each subset.

| Feature Type | Trajectory Pattern |
|--------------|-------------------|
| Background | Flat at ~100% across all C |
| Bird Type | Flat at ~100% across all C |

Both probes achieve near-perfect accuracy at all regularization strengths. There are no "early epochs" to observe — features are already learned. The C-sweep produces flat trajectories where CV captures only sampling variance.

## Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUC | 0.0 | ≥ 0.75 | **FAIL** |
| Best F1 | 0.667 | — | — |

**Figure 3** shows the ROC curve: it hugs the diagonal, indicating no discriminative power.

## Why AUC = 0.0 (Not Just Low)

AUC can be exactly 0.0 (rather than near 0.5) when:
1. There are only 2 classes
2. The ranking is inverted (positive class has higher values than negative)

Here, bird\_type (core, negative class) has *lower* CV than background (spurious, positive class), causing complete inversion.

## Blocked Downstream Hypotheses

Per the verification plan, H-E1 failure blocks:

| Hypothesis | Status | Reason |
|------------|--------|--------|
| H-M1 | NOT\_STARTED | Requires H-E1 (monotonic trajectories) |
| H-M2 | NOT\_STARTED | Requires H-M1 (threshold classification) |
| H-M3 | NOT\_STARTED | Requires H-M2 (gradient regularization) |

The EUR intervention mechanism remains untested because the detection foundation failed.

## Summary

The existence hypothesis H-E1 is **refuted**. CV of probe accuracy trajectories on frozen CLIP features shows no discriminative power for spurious vs. core features (AUC = 0.0). The mechanism fails because pretrained features are saturated — both concepts are already learned, eliminating emergence dynamics.
