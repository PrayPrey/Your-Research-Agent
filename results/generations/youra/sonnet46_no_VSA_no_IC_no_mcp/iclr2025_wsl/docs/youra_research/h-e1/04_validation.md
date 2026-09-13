---
title: "Validation Report: H-E1 — Orbit Diameter Characterization"
hypothesis_id: H-E1
date: 2026-08-26
status: COMPLETED
gate_result: PASS
---

# Phase 4 Validation Report: H-E1

## Hypothesis

> Under the Schürholt MNIST zoo (2-layer MLPs, ~50k models), scaling and sign-flip symmetry orbits have non-negligible diameter (within-orbit cosine distance > 0.05 for ≥90% of oracle-constructed orbit pairs), confirming that within-orbit variance is geometrically substantial and canonicalization has measurable effect.

## Gate: MUST_WORK

**Result: PASS**

All three gate conditions satisfied:

| Condition | Threshold | Actual | Pass |
|-----------|-----------|--------|------|
| mean cosine distance (scaling) > 0.05 | > 0.05 | **0.3232** | ✓ |
| frac_above_0.05 (scaling) ≥ 0.90 | ≥ 0.90 | **1.0000** (100%) | ✓ |
| bootstrap CI lower bound > 0 | > 0 | **0.3226** | ✓ |

## Experiment Configuration

- Dataset: Schürholt MNIST MLP Zoo (local archive), MNIST split
- Models sampled: N=500
- Orbit members per model per symmetry type: K=5
- Total orbit pairs measured: 2,500 per symmetry type
- Weight dimension: D=50,890 (784×64+64+64×10+10)
- Seed: 42

## Results by Symmetry Type

| Symmetry Type | Mean Cosine Dist | Std | P5 | P95 | Frac > 0.05 | 95% CI |
|---------------|-----------------|-----|-----|-----|-------------|--------|
| **scaling** | 0.3232 | — | — | — | 1.000 | [0.3226, 0.3238] |
| **signflip** | 1.0750 | — | — | — | 1.000 | [1.0705, 1.0789] |
| **combined** | 1.0462 | — | — | — | 1.000 | [1.0425, 1.0499] |

## Key Findings

1. **Scaling symmetry**: Mean cosine distance 0.3232 — far above the 0.05 threshold. Every single one of 2,500 orbit pairs exceeds the threshold. This confirms that log-uniform scaling by factors up to 10× produces substantial geometric displacement in weight space.

2. **Sign-flip symmetry**: Mean cosine distance 1.075 — near the theoretical maximum for this transform. Flipping ±1 signs on 64 hidden neurons with probability 0.5 produces near-orthogonal or anti-correlated weight vectors, making these orbits geometrically enormous.

3. **Combined symmetry**: Mean cosine distance 1.046 — similar to sign-flip, as the sign-flip component dominates.

4. **Zero failures**: 100% of all 2,500 orbit pairs per symmetry type exceed the 0.05 threshold with zero exceptions. The CI is tight (width ~0.001 for scaling), indicating stable estimation.

## Mechanism Verification

The transforms are implemented as oracle symmetry operations:
- **Scaling**: W1 scaled by α∈[0.1,10] per column, b1 scaled, W2 divided (functionally equivalent)
- **Sign-flip**: W1 columns, b1, W2 rows all flipped by same ±1 signs (ReLU invariance)
- Non-triviality check: all transforms verified to produce cosine_dist > 1e-6

The large cosine distances are mathematically expected: scaling by α=10 in one neuron and 1/10 in another creates large angular displacement despite functional equivalence.

## Conclusion

**H-E1 CONFIRMED.** Symmetry orbit diameters are not merely non-negligible — they are large (0.32–1.08 cosine distance). This strongly validates the motivation for canonicalization: without it, functionally identical models occupy very different regions of weight space, and any metric or representation learning on raw weights must contend with this enormous within-orbit variance.

H-E1 gate PASSES, unblocking H-M1, H-M2, H-M3, H-C1.

## Figures

- `figures/fig_gate_metrics.png` — bar chart: mean cosine distance per symmetry type vs threshold
- `figures/fig_orbit_distribution.png` — cosine distance histograms, all symmetry types
- `figures/fig_l2_vs_cosine.png` — L2 vs cosine scatter by symmetry type
- `figures/fig_scale_vs_diameter.png` — max scale magnitude vs orbit diameter (scaling only)

## Runtime

~60 seconds on CPU (N=500, K=5, D=50890).
