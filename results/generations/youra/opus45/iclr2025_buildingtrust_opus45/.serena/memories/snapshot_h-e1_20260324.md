# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-24T15:00:00Z
**Hypothesis:** h-e1
**Statement:** Under instruction-tuned LLMs evaluated on standard QA benchmarks (MMLU, TruthfulQA, GSM8K), if token-level p_max is used for selective prediction with threshold τ, then AURC(p_max) is significantly lower than AURC(random abstention), because p_max encodes genuine epistemic uncertainty about answer correctness.

**Final Status:** FAILED
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results Summary
- **Pass Rate:** 5/9 (55.6%)
- **MMLU:** 3/3 PASS
- **TruthfulQA:** 2/3 PASS  
- **GSM8K:** 0/3 FAIL

## Key Findings
1. p_max selective prediction works well for multiple-choice QA (MMLU, TruthfulQA)
2. Complete failure on mathematical reasoning (GSM8K) due to task-prompt mismatch
3. p_max requires single-token answers; GSM8K requires chain-of-thought

## Cascade Effects
- h-m1: CASCADE_FAILED (direct dependent)
- h-m2: CASCADE_FAILED (transitive)
- h-m3: CASCADE_FAILED (transitive)

## Routing Decision
Route to Phase 0 for new research direction.

---
*Per-hypothesis snapshot for Phase 0/2A reference*
*Serena Memory: global/phase45/failure_h-e1_pmax_selective_prediction*