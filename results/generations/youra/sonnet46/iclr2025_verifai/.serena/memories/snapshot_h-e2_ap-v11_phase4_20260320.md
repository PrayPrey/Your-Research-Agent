# Hypothesis Completion Snapshot: h-e2

**Date:** 2026-03-20T12:30:00
**Hypothesis:** h-e2 (H-AgreePredict-v11 sub-hypothesis H-E2)
**Statement:** Partial Spearman rho(A_p, pass@1 | LOOM_difficulty) >= 0.10, positive direction, with bootstrap p < 0.05 for at least 3/5 model-benchmark pairs on EvalPlus; rho >= 0.15 in at least 2/3 distinct model architectures.
**Final Status:** COMPLETED (gate FAIL)
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0
**n_pairs_passing:** 0/5
**n_arch_passing:** 0/3

## Key Results

| Pair | partial_rho | p_perm |
|------|------------|--------|
| llama3_humaneval | -0.0186 | 0.5915 |
| llama3_mbpp | -0.0231 | 0.6782 |
| deepseek_humaneval | -0.1050 | 0.9106 |
| deepseek_mbpp | +0.0507 | 0.1592 |
| codellama_mbpp | -0.0041 | 0.5321 |

## Reflection

- Reflection triggered: true
- Outcome: ROUTED_TO_PHASE_0
- Reason: MUST_WORK gate FAIL (0/5 pairs). A_p negatively/nullly correlated with pass@1 after LOOM adjustment. Core mechanism (high agreement → high pass@1) is empirically invalid.
- Cascade: h-m1/m2/m3 CASCADE_FAILED

## Lessons Learned

- N-gram Jaccard agreement (A_p) is NOT a predictor of pass@1 correctness — syntactic consensus ≠ semantic correctness
- Agreement among LLM solutions reflects shared failure modes, not concentrated correct probability mass
- LOOM difficulty adjustment confirmed useful but could not rescue absent signal
- Full H-AgreePredict-v11 hypothesis is TERMINATED; route to Phase 0 for new direction

---
*Per-hypothesis snapshot for Phase 2A/Phase 0 reference*
*Phase 4 step-08-completion.md*
