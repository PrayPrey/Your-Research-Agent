# H-C1 SHOULD_WORK Gate: NULL Result (Limitation)

**Date:** 2026-08-02  
**Gate type:** SHOULD_WORK  
**Gate satisfied:** False  
**Verdict:** NULL — informative null result, does NOT block pipeline

## Finding

η²_7B (0.9772) > η²_1.3B (0.9119) on HumanEval. Scale attenuation NOT confirmed by η² criterion.

## Root Cause

At 7B scale, within-seed variance collapsed to near-zero (σ² ≈ 0.00043 vs 0.01655 at 1.3B). Seeds produce near-identical pass@1 per condition. This inflates η² even with smaller absolute between-condition spread:
- Absolute spread 7B: 0.055 (0.341–0.396)
- Absolute spread 1.3B: 0.319 (0.031–0.350)

## Action

SHOULD_WORK gate failure → continue with limitation note (per workflow.yaml gate semantics). Pipeline proceeds to Phase 5.

## Impact on Dependents

Any hypothesis using h-c1 scale-attenuation evidence should note:
- Use absolute spread as primary metric alongside η²
- 7B model shows preserved but deterministic source identity effect
- MBPP evaluation incomplete (4/12 parse failures); HumanEval 12/12 complete
