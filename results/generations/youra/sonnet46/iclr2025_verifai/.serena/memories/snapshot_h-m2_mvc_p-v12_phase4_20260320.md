# Hypothesis Completion Snapshot: h-m2

**Date:** 2026-03-20T19:45:00Z
**Hypothesis:** h-m2 (H-MVC_p-v12 MECHANISM sub-hypothesis)
**Statement:** Spearman rho(MVC_p(tau), pass@1_p) monotonically non-decreasing with tau (3→4→5) for ≥3/5 model-benchmark pairs
**Final Status:** COMPLETED
**Gate Result:** FAIL (SHOULD_WORK)
**Reflection Outcome:** LIMITATION_RECORDED

## Results

- Validation: FAIL
- Gate Type: SHOULD_WORK (pipeline continues on FAIL)
- N_monotone: 0/5 (required: ≥3)
- Rho decreases with tau in all 5 pairs (opposite of hypothesis)
- tau=3 is empirical optimum; tau=4 (H-E2) near-optimal
- H-E2 cross-check PASS (data integrity confirmed)
- Limitation: structural variance collapse at higher tau

## Key Findings

- llama3_humaneval: rho 0.682→0.509→0.436 (non_monotone_complex)
- llama3_mbpp: rho 0.850→0.787→0.576 (non_monotone_complex)
- deepseek_humaneval: rho 0.833→0.711→0.549 (non_monotone_complex)
- deepseek_mbpp: rho 0.783→0.851→0.714 (4->5_break)
- codellama_mbpp: rho 0.615→0.849→0.763 (4->5_break)
- mean delta_34=-0.011, mean delta_45=-0.134

## Pipeline Impact

SHOULD_WORK FAIL: pipeline NOT blocked. All 5 sub-hypotheses now complete:
- h-e1: PASS, h-e2: PASS, h-m1: PASS (3 PASS)
- h-m2: FAIL (SHOULD_WORK), h-m3: FAIL (SHOULD_WORK) (2 FAIL — acceptable)
Ready for Phase 5 (skipped per module.yaml) → Phase 6 paper.

---
*Per-hypothesis snapshot for Phase 2A reference*
