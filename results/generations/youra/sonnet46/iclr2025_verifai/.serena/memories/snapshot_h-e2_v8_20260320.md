# Hypothesis Completion Snapshot: h-e2_v8

**Date:** 2026-03-20T04:45:00Z
**Hypothesis:** h-e2_v8
**Statement:** Under OLS regression with HC3 robust SE and bootstrap CI (n=1000, seed=42), D_p and difficulty_covariate regressed against pass@1_p for 5 model-benchmark pairs yields β(D_p) > 0, one-sided p < 0.05, ΔR² ≥ 0.02, and bootstrap 95% CI lower bound > 0 for ≥4/5 pairs.
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)

## Results
- Validation: FAIL
- Gate Type: MUST_WORK
- Pairs Passing ALL 4 criteria: 0/5

## Per-Pair Results
| Pair | β(D_p) | p_one_sided | ΔR² | CI_lower | Pass |
|------|--------|-------------|-----|----------|------|
| llama3/humaneval | -0.051 | 0.846 | 0.001 | -0.138 | ✗ |
| llama3/mbpp | -0.089 | 0.951 | 0.002 | -0.175 | ✗ |
| deepseek/humaneval | +0.130 | 0.003 | 0.011 | 0.057 | ✗ (ΔR²<0.02) |
| deepseek/mbpp | -0.126 | 0.994 | 0.004 | -0.208 | ✗ |
| codellama/mbpp | +0.106 | 0.037 | 0.005 | 0.001 | ✗ (ΔR²<0.02) |

## Reflection
- Reflection: Fundamental methodological failure. Negative beta in 3/5 pairs. ΔR²<0.02 universally. No parameter tuning can fix.
- Lessons:
  1. Pass@1 under strict all-tests-pass (T=1000) is near-zero, dominated by difficulty covariate leaving D_p residual negative
  2. ΔR² universally < 0.02 — D_p adds ≤1.1% incremental variance
  3. Alternatives: pass@k (k>1), soft Hamming (fraction T tests), entropy-based outcomes, solution-level diversity
  4. OLS framing may not be appropriate — ranking/calibration metric may be better

## Cascade Effects
- H-M1_v8: CASCADE_FAILED
- H-M2_v8: CASCADE_FAILED
- H-M3_v8: CASCADE_FAILED

## Routing
- ROUTED_TO_PHASE_0: Brainstorm alternative outcome metrics and D_p formulations

---
*Per-hypothesis snapshot for Phase 2A reference*
