# h-m4 MUST_WORK FAIL: Difficulty-Stratified ECE

**Pipeline:** YouRA | 20260316_verifia
**Date:** 2026-03-18
**Gate:** MUST_WORK FAIL (1/3 models pass; need >=2/3)
**Route:** Phase 0 (new hypothesis generation required)

## Hypothesis
DELTA_ECE = ECE(hard) - ECE(easy) >= 0.03 (bootstrap 95% CI excluding zero) in >=2/3 model families, AND persists after temperature scaling.

## Experiment Results
| Model | DELTA_ECE | CI | P1 Gate |
|---|---|---|---|
| deepseek_6.7b | +0.2979 | [0.2849, 0.3115] | PASS |
| llama3_8b | +0.0034 | [-0.0074, 0.0133] | FAIL |
| codellama_7b | -0.2490 | [-0.2589, -0.2391] | FAIL |

## Root Cause Analysis
1. **llama3_8b near-zero DELTA_ECE**: Confidence signal doesn't differentiate hard/easy tier calibration. Aggregate ECE is similar across tiers despite individual-level signal.
2. **codellama_7b INVERTED effect**: ECE(easy) >> ECE(hard) — opposite direction to hypothesis. CodeLlama appears better calibrated on hard problems. Probable cause: CodeLlama systematically overconfident on MBPP-style "easy" tasks; confidence on hard tasks happens to be lower and closer to actual accuracy.
3. **deepseek_6.7b confirms hypothesis direction**: Strong DELTA_ECE=0.2979 supports mechanism for some architectures, but not universal.

## Key Insight for Phase 0
The ECE stratification approach is model-architecture-dependent, not universal. Revised hypotheses should consider:
- Architecture-specific calibration behavior (why CodeLlama inverts)
- Calibration heterogeneity framing rather than assuming uniform direction
- Alternative metrics more robust across architectures
- Conditional analysis: does the effect depend on model training data distribution?

## Data / Code (reusable for revised hypothesis)
- Results: h-m4/results/delta_ece_results.json
- Figures: h-m4/figures/ (6 figures)
- Code: h-m4/code/src/h_m4/ (all correct, 30 tests pass)
- Tier assignments: h-m2/results/tier_assignments.csv
- P(True) confidence: h-m3/results/ptrue_checkpoint_{model}.json

## Cascade
- h-m4 is the final hypothesis; no dependents blocked
- All prerequisite experiments (h-e1, h-m1, h-m2, h-m3) PASSED
- Calibration data and tier assignments are reusable for revised hypothesis
