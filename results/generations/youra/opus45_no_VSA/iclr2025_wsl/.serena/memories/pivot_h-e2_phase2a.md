# Hypothesis Pivot Record: h-e2

**Date:** 2026-08-09T18:45:00Z
**Hypothesis:** h-e2
**Gate Result:** PARTIAL
**Reflection Outcome:** REQUIRES_REDESIGN
**Route To:** Phase 2A

## Original Hypothesis

CISE shows OrbitVar > 0.1 and permutation variance accounts for >15% of total embedding variance

## What Worked

1. Permutation mechanism correctly implemented (weight L2 diff = 14.15)
2. CISE encoder produces different embeddings for permuted weights (embedding L2 diff = 0.29)
3. OrbitVar is measurable with the implemented methodology

## What Failed

1. OrbitVar threshold not met: 0.000158 vs required 0.1
2. Permutation variance ratio: 0.017% vs required 15%

## Root Cause Analysis

The hypothesis assumes a **trained** CISE encoder. Random-init encoders exhibit near-equivariant behavior due to:
1. Mean pooling inherently reduces sensitivity to token order
2. Random weights lack the learned asymmetric structure that creates OrbitVar
3. Untrained Transformer weights don't have directional biases

## Redesign Recommendations

1. **Option A:** Train CISE encoder on ModelZooDataset before measuring OrbitVar
2. **Option B:** Adjust hypothesis to compare random-init vs trained encoder OrbitVar
3. **Option C:** Use pretrained CISE weights from Schürholt NeurIPS 2021

## Preserved Elements

- Code infrastructure for OrbitVar measurement
- Synthetic CNN zoo generation
- Permutation application mechanism
- Variance decomposition methodology

## Lessons for Phase 2A

- Random-init encoders are near-equivariant by construction
- OrbitVar measurement requires trained encoder to show meaningful variance
- Mean pooling architecture contributes to low OrbitVar

---
*Pivot recorded at: 2026-08-09T18:45:00Z*
*For cross-phase reference*