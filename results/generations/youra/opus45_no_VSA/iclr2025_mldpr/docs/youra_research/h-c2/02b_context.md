# Phase 2B Context: h-c2

**Generated:** 2026-08-09 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-c2

---

## Hypothesis Information

| Field | Value |
|-------|-------|
| **ID** | h-c2 |
| **Type** | CONDITION |
| **Gate** | SHOULD_WORK |
| **Statement** | The metadata-variance effect persists within RandomForest-only analysis, ruling out algorithm mix confound |
| **Prediction** | P6: Permuted effect <5% of observed effect |
| **Success Criterion** | 1000 permutations yield effect <5% of true effect; true effect >95th percentile of permutation distribution |
| **Falsification** | Shuffled effect ≥20% of observed |
| **Dependencies** | h-e1 (must pass) |

---

## Verification Protocol

1. Run 1000 permutations of metadata completeness scores
2. For each permutation, compute regression coefficient
3. Compare permutation distribution to true effect
4. True effect should be >95th percentile of permutation distribution

---

## Continuation Context

### Previous Hypothesis Results (h-e1)

**Status:** VALIDATED (PASS)

**Key Findings:**
- Relative IQR reduction: 42.1% (threshold: 20%)
- Absolute IQR reduction: 0.0197 (threshold: 0.01)
- 95% CI: [39.1%, 51.7%] excludes <10%
- p-value < 0.0001 (threshold: 0.05)
- Effect vastly exceeds null baseline (6.1% at 95th percentile)

**Proven Components from h-e1:**
- OpenML data collection pipeline
- Metadata completeness scoring (5-field checklist)
- IQR computation for reproducibility variance
- Mixed-effects regression framework
- Control variables: intrinsic stability, popularity, algorithm family, infrastructure

---

## Experimental Setup (from Phase 2B)

**Dataset:** OpenML benchmark datasets with ≥10 matched runs (2019-2024)
**Model:** Statistical analysis (regression with permutation test)
**Compute:** High (1000 permutations)

---

## Gate Conditions

- **Prerequisite:** h-e1 must pass → ✅ SATISFIED
- **Gate Type:** SHOULD_WORK (pipeline continues with warning if fail)
