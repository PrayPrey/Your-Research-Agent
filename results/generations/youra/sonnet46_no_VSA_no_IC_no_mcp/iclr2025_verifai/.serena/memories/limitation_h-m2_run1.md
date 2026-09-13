# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-26T12:35:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Ceiling effect: type-error problems in HumanEval+ are repaired at 90.9% under both Condition A (execution-only) and Condition B (execution+mypy), leaving no differential room for mypy to demonstrate type-specificity advantage. The SHOULD_WORK gate (delta_type > 0) was not met. Mechanism h-m2 was not activated. Route: EXPLORE (extra-context-length confound identified as primary alternative explanation for any observed differences).

## Failed Checks

- delta_type <= 0 (expected > 0)
- differential <= 0 (expected > 0)
- mechanism_activated = False

## Partial Results

| Metric | Value |
|--------|-------|
| type_error_n | 22 |
| repair_rate_A_type | 0.909 |
| repair_rate_B_type | 0.909 |
| delta_type | 0.000 |
| non_type_error_n | 142 |
| repair_rate_A_non_type | 0.838 |
| repair_rate_B_non_type | 0.844 |
| differential | -0.006 |

## Experiment Summary

HumanEval+ (164 problems, k=5): type_error n=22, rate_A=90.9%, rate_B=90.9%, delta_type=0.000; non_type_error n=142, rate_A=83.8%, rate_B=84.4%, delta_non=+0.006; differential=-0.006 (gate threshold: >0 not met). Ceiling effect: both conditions repair type-error problems at 90.9% — no room for mypy differential. Mechanism activated: False.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with EXPLORE routing noting this limitation.

Future research attempts should consider:
1. The ceiling effect — type errors are largely correctable by execution feedback alone
2. Whether the mypy differential is detectable only on harder type-system problems (generics, overloads, Protocol)
3. Extra-context-length as a confound — Condition B provides more tokens; controlling for this is the EXPLORE target

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming to avoid similar ceiling-effect designs
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-26T12:35:00+00:00*
*For cross-phase reference*
