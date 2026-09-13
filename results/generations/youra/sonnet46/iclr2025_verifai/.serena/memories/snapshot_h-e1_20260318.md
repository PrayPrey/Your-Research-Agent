# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-18T02:15:00+00:00
**Hypothesis:** h-e1
**Statement:** LLMs exhibit measurably higher ECE on hard-tier code problems vs. easy-tier using P(True) logprob elicitation
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results Summary

- P(True) mechanism: ACTIVATED (values 0.57–0.91, non-degenerate)
- Difficulty stratification: FAILED (all "unknown" — leaderboard CSV missing)
- ΔECE: NaN for all 3 LLM families
- n_hard=0, n_easy=0

## ECE Overall (valid)
- llama3-8b: 0.4895
- codellama-7b: 0.5218
- deepseek-coder: 0.1358 (lower — DeepSeek tends to be underconfident)

## Pass Rates (EvalPlus augmented tests)
- llama3-8b: 15.67%
- codellama-7b: 27.89%
- deepseek-coder: 6.37%

## Key Lesson
Self-contained difficulty tier definition required. Use bootstrap from experiment's own pass@1 data.
DO NOT depend on external CSVs for difficulty tier assignment.

## Cascade
h-m1, h-m2, h-m3 → CASCADE_FAILED

## Routing
→ Phase 0 (hypothesis redesign)

---
*Per-hypothesis snapshot for Phase 2A reference*
