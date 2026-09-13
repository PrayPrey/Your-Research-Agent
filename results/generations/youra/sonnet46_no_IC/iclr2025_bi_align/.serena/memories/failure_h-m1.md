# H-M1: Phase 4 MUST_WORK Gate FAIL — Failure Record

**Date:** 2026-08-04
**Hypothesis:** h-m1 (MECHANISM)
**Gate:** MUST_WORK → FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Statement
Under AlpacaEval 2.0 models with known training type, if training_type = RLHF vs SFT, then mean(Δ|RLHF) < 0 and mean(Δ|RLHF) < mean(Δ|SFT) [Mann-Whitney p < 0.05] because RLHF reward modeling produces verbosity inflation that inflates raw human win_rate relative to length-neutral LC evaluation.

## Experiment Results
- N=58 models: N_RLHF=20, N_SFT=10, N_DPO=8, N_Unknown=20
- mean(Δ|RLHF) = -16.72 pp (C1 PASS: < 0)
- mean(Δ|SFT) = -18.24 pp (wrong direction — SFT MORE negative than RLHF)
- Mann-Whitney U stat=109.0, p=0.662 (C2 FAIL: >> 0.05)
- Cohen's d (RLHF vs SFT) = 0.136 (negligible, wrong direction)

## Root Causes
1. Evaluator gap is training-type-agnostic — all types show Δ ≈ -12 to -18 pp
2. Model capability confound: high-quality RLHF (GPT-4: -8.8 pp) < low-quality SFT (recycled-wizardlm: -32 pp)
3. SFT models on chat data also produce verbose outputs — verbosity is dataset-driven, not RLHF-specific
4. AlpacaEval task incentivizes verbosity universally across training paradigms

## Lessons Learned
- The evaluator gap (H-E1) is a dataset-wide phenomenon, not RLHF-specific
- Model capability/quality is a stronger predictor of evaluator gap than training paradigm
- RLHF verbosity hypothesis needs controlling for model quality to be testable
- H-M2 (length correlation) and H-M3 (family variation) are more informative mechanism analyses
- With N=58 and std ~11 pp, Mann-Whitney has insufficient power for small effects — but point estimate also wrong direction

## Impact on Dependents
- h-m2 (SHOULD_WORK): prerequisites satisfied, proceed
- h-m3 (SHOULD_WORK): prerequisites satisfied, proceed
- H-E1 core finding preserved: population-level gap mean(Δ)=-16.37 pp is robust

## Files
- Report: h-m1/04_validation.md
- Results: h-m1/code/results/h-m1_results.json
- Reflection: h-m1/reflection_report.md
