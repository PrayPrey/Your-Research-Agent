# Hypothesis Completion Snapshot: h-m1 (Updated 2026-03-17)

**Date:** 2026-03-17T00:00:00Z
**Hypothesis:** h-m1
**Statement:** Under FeedbackEval benchmark conditions with 5 model families, compiler-only feedback (pyflakes) yields significantly higher Repair@1 improvement over no-feedback baseline than type-checker-only (mypy) or linter-only (pylint) feedback, and signal type is a significant predictor of Repair@1 in mixed-effects logistic regression (χ² p < 0.05, ΔRepair@1 ≥ 5pp, consistent across ≥4/5 models).
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results
- Validation: FAIL
- Gate Type: MUST_WORK
- Best ΔRepair@1: +0.4pp (combined) — far below 5pp threshold
- Signal type predictor: NOT significant (all p > 0.89)
- Cross-model consistency: 1/5 models
- Root cause: ~85% of FeedbackEval instances have semantic bugs undetectable by static analysis

## Reflection Triggered
- Reflection outcome: ROUTED_TO_PHASE_0
- Fundamental mechanism mismatch: static analysis cannot detect FeedbackEval semantic bugs
- Cascade: h-m2, h-m3, h-m4 → CASCADE_FAILED

## Cascade Effects
- h-m2: CASCADE_FAILED (depends on h-m1 signal-type effect)
- h-m3: CASCADE_FAILED (depends on h-m2)
- h-m4: CASCADE_FAILED (depends on h-m3)

## Key Lessons
1. FeedbackEval has ~85% semantic bugs — static analysis tools are largely ineffective
2. h-e1 extractability warning (pyflakes 8.9%, mypy 9.6%) directly predicted this failure
3. Model identity (which LLM) dominates — NOT feedback signal type
4. Verify mechanism operability on target dataset before hypothesis commitment

---
*Per-hypothesis snapshot for Phase 2A/Phase 0 reference*
*Updated: 2026-03-17 (step-06b reflection executed)*
