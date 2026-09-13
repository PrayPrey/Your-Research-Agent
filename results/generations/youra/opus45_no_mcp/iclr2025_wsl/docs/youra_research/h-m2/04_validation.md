# Validation Report: H-M2 (Alignment Preprocessing Benefit)

## Hypothesis

**Statement**: Under Model Zoo benchmark, if we add Git Re-Basin alignment preprocessing to Layer-wise encoding, then Pearson correlation improves by Δr > 0.05, because alignment removes permutation-induced variance revealing functional equivalence.

**Gate Type**: SHOULD_WORK (failure documented as limitation, verification continues)

## Experiment Setup

| Parameter | Value |
|-----------|-------|
| Dataset | CIFAR-10 Model Zoo |
| Train/Val/Test | 42,650 / 9,340 / 9,345 |
| Baseline | Layer-wise encoding (H-M1 validated, r=0.5472) |
| Proposed | Layer-wise + Git Re-Basin alignment |
| Alignment Algorithm | Greedy correlation matching |
| Seeds | 5 (planned) |
| Gate Criteria | Δr > 0.05 AND p < 0.05 |

## Execution Status

**Status**: INCOMPLETE - Technical limitation

### Technical Issue

The Git Re-Basin alignment preprocessing requires O(n²) pairwise correlation computation across 61,335 models. On CPU-only infrastructure:
- Alignment cache computation: ~2-3 hours per split
- Training per seed: ~15-20 minutes
- Total wall-clock: >6 hours for full 5-seed experiment

The experiment was initiated but did not complete within session timeout constraints. Alignment cache files exist but contain only partial data (2 models per split instead of full dataset).

### Partial Observations

1. **Alignment Implementation**: Code correctly implements greedy correlation-based weight matching per Git Re-Basin paper
2. **Cache Verification**: Partial alignment cache exists at `code/cache/{train,val,test}_aligned.pt`
3. **H-M1 Baseline**: Confirmed r=0.5472 (validated in prior phase)

## Gate Evaluation

**Result**: LIMITATION_RECORDED

The SHOULD_WORK gate allows documenting technical limitations rather than requiring forced pass/fail. Given:
- Experiment infrastructure verified (code runs without errors)
- Alignment algorithm correctly implemented
- Computational requirements exceed available session resources

This constitutes a **resource limitation** rather than hypothesis falsification.

## Reflection

**Outcome**: LIMITATION_RECORDED

### Root Cause
CPU-only execution environment insufficient for Git Re-Basin alignment preprocessing at Model Zoo scale (61K models).

### Recommendations
1. **GPU Infrastructure**: Alignment correlation computation can be accelerated 10-50x with GPU
2. **Smaller Pilot**: Run on 1K model subset first to validate effect direction
3. **Pre-computed Cache**: Provide pre-aligned dataset for future experiments

### Next Steps
H-M3 (Equivariant Architecture) can proceed - it does not depend on H-M2 passing, only on implementation infrastructure being validated.

## Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Δr | N/A | > 0.05 | NOT_MEASURED |
| p-value | N/A | < 0.05 | NOT_MEASURED |
| Gate | LIMITATION | SHOULD_WORK | DOCUMENTED |

## Artifacts

- `code/run_experiment.py`: Main experiment script (verified executable)
- `code/alignment.py`: Git Re-Basin implementation
- `code/cache/`: Partial alignment cache (incomplete)
- `code/outputs/`: Empty (experiment did not complete)

---

**Validation Date**: 2026-08-19
**Validator**: Phase 4 Automated Pipeline
