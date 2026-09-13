---
name: limitation_h-e1_20260317
description: Phase 4 PARTIAL result for h-e1 - scale constraint limitation recorded for LONGEST-MATCH contamination detection
type: project
---

# Limitation Record: h-e1 (Phase 4 PARTIAL)

**Date:** 2026-03-17
**Hypothesis:** h-e1 - Cross-Benchmark × Cross-Corpus Contamination Matrix Existence
**Gate Type:** MUST_WORK
**Gate Result:** PARTIAL
**Reflection Outcome:** LIMITATION_RECORDED

## Root Cause

Scale constraint: n=13, mincount=5 requires full-scale corpus streaming (>100M docs).
PoC 10k-doc sample produces all-zero contamination z-scores (normality check fails for all cells).
ROOTS corpus (bigscience/roots) is gated — institutional access required.

## What Worked

- Algorithm mechanism validated: 53/53 unit tests pass
- Full contamination matrix infrastructure complete (12 cells computed)
- LONGEST-MATCH n-gram algorithm correct with z-score normalization
- Checkpointing, error isolation, all output formats functional
- Corpus fallback: monology/pile-uncopyrighted substituted for EleutherAI/pile

## What Failed

- contaminated_cells_count = 0 (required: ≥3)
- All 8 non-ROOTS cells: normality check = False (insufficient variance at 10k docs)
- ROOTS: 4/12 cells empty (corpus access gated)

## Lessons for Future Hypotheses

1. **Full-scale streaming required**: Use corpus streaming with 100M+ docs for reliable z-score statistics
2. **Lower n/mincount for PoC**: Use n=8, mincount=1 for proof-of-concept validation
3. **ROOTS alternative**: Use mC4 or CC-100 as ROOTS substitute
4. **Validation strategy**: Run pilot with small n first, then scale up
5. **Infrastructure is reusable**: All code modules ready for h-e2, h-m1, h-m2

## Impact on Dependent Hypotheses

- h-m1 (prerequisite: h-e1): Infrastructure reusable; full-scale matrix needed for Spearman ρ computation
- h-m2 (prerequisite: h-m1): Same scale constraint applies

## Status

Limitation recorded. Algorithm validated. Pipeline continues to h-e2.

---
*Limitation record for cross-phase learning*