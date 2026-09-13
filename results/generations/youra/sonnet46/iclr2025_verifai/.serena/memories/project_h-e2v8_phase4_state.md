---
name: h-e2_v8 Phase 4 completion
description: Phase 4 COMPLETE 2026-03-20: H-E2_v8 EXISTENCE gate FAIL (MUST_WORK). 0/5 pairs pass ALL 4 OLS criteria. ROUTED_TO_PHASE_0. H-M1/M2/M3_v8 CASCADE_FAILED.
type: project
---

Phase 4 COMPLETE 2026-03-20: H-E2_v8 gate FAIL (MUST_WORK). ROUTED_TO_PHASE_0.

**Why:** D_p does not universally positively predict pass@1 via OLS. 0/5 pairs pass all 4 criteria (β>0, p<0.05, ΔR²≥0.02, CI_lower>0) simultaneously. Negative beta in 3/5 pairs. ΔR²<0.02 in ALL pairs (max 0.011). Root cause: strict all-tests-pass criterion with large T (up to T=1000 for HumanEval) means pass@1_p is near-0 for most problems and dominated by difficulty rather than D_p diversity signal.

**How to apply:** The D_p → pass@1 OLS approach from H-DpOLS-v8 is fundamentally flawed. Phase 0 should explore alternative diversity metrics or different prediction targets (e.g., pass@k for k>1, or softened pass criterion).

**Key results (5 pairs):**
- llama3/humaneval: β=-0.051, p=0.846, ΔR²=0.001, CI_lower=-0.138 → FAIL
- llama3/mbpp: β=-0.089, p=0.951, ΔR²=0.002, CI_lower=-0.175 → FAIL
- deepseek/humaneval: β=0.130, p=0.003, ΔR²=0.011, CI_lower=0.057 → FAIL (ΔR²<0.02)
- deepseek/mbpp: β=-0.126, p=0.994, ΔR²=0.004, CI_lower=-0.208 → FAIL
- codellama/mbpp: β=0.106, p=0.037, ΔR²=0.005, CI_lower=0.001 → FAIL (ΔR²<0.02)

**Cascade:** H-M1_v8, H-M2_v8, H-M3_v8 → CASCADE_FAILED
**Pipeline:** STOPPED, ROUTED_TO_PHASE_0
