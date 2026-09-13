# Failure Record: H-E1

**Date:** 2026-08-12
**Hypothesis:** Contrastively-learned functional probes produce discriminative fingerprints that distinguish networks with different accuracy levels
**Gate Type:** MUST_WORK
**Result:** FAILED

## Metrics
- Learned R²: 0.499 (target: > 0.7)
- Random baseline R²: 0.472
- Delta: 0.028 (target: >= 0.15)

## Root Cause
Contrastive probe learning provided minimal improvement over random probes. Small zoo size (100 models) and limited accuracy diversity (10-57%) likely insufficient for learning discriminative probes.

## Lessons
- PoC scale (100 models) insufficient for weight-space learning
- Contrastive binning by accuracy may not capture property relationships
- Consider supervised probe learning directly on accuracy labels

## Impact on Downstream
- H-M1, H-M2, H-M3, H-M4 dependent on H-E1 success
- Per MUST_WORK fail_action: ABANDON hypothesis chain

## References
- `mem:hypothesis_h-e1`
- Validation report: h-e1/04_validation.md
