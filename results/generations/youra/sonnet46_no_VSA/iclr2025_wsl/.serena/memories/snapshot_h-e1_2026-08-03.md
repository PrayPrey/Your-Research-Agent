# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-03T00:00:00Z
**Hypothesis:** h-e1
**Statement:** Under S_16³ functional permutations (coupled row-column across adjacent CNN layers), architecturally invariant weight encoders (DeepSets sum pooling, NFN structured equivariance) achieve mean OrbitVar < 1e-6 on ModelZooDataset CIFAR10-GS, contrasted with CISE (OrbitVar=0.010333).
**Final Status:** COMPLETED
**Gate Result:** PASS
**Gate Type:** MUST_WORK

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- Gate Satisfied: true

## Metrics
| Encoder | Mean OrbitVar | Max OrbitVar | Gate |
|---------|--------------|-------------|------|
| C2 (DeepSets doubly-invariant) | 1.002e-14 | 6.719e-14 | PASS |
| C3 (NFN structured equivariant) | 8.905e-08 | 3.306e-07 | PASS |
| CISE baseline | 0.010333 | — | FAIL |

## Key Architectural Findings
1. Dataset uses 28×28 input; CNN has no padding; FC1 receives 36 features (4×3×3)
2. Functional permutation must propagate to FC1 columns as block permutation of 9-element spatial chunks
3. C2 requires doubly-invariant architecture (sum over all C_out×C_in pairs) — row-only sum fails
4. NFN only accepts conv layers; FC layers handled separately with column-invariant aggregations

## Lessons Learned
- What Worked: DeepSets doubly-invariant encoder achieves machine-epsilon invariance (1e-14)
- Key Insight: Architectural invariance-by-construction eliminates within-orbit variance — C2 reduces OrbitVar by 12 orders of magnitude vs CISE
- NFN near-invariant (8.9e-08) is sufficient for MUST_WORK gate but not exact

---
*Per-hypothesis snapshot for Phase 2A reference*
