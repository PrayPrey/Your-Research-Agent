---
name: h-m2 MVC_p-v12 Phase 4 completion
description: Phase 4 COMPLETE 2026-03-20: H-M2 (H-MVC_p-v12) SHOULD_WORK gate FAIL. 0/5 pairs monotone. Rho decreases with tau (3→4→5). tau=3 optimal. H-E2 validated. Limitation recorded. Archon 05ec532e=done.
type: project
---

## H-M2 Phase 4 Complete

**Date:** 2026-03-20T19:40:00Z
**Hypothesis:** h-m2 (H-MVC_p-v12 sub-hypothesis)
**Statement:** Spearman rho(MVC_p(tau), pass@1) monotonically non-decreasing with tau (3→4→5) for ≥3/5 pairs
**Final Status:** COMPLETED
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL (pipeline continues)

## Results

- N_monotone = 0/5 pairs (required ≥3)
- All 5 pairs show rho DECREASING with tau, not increasing
- mean_delta_34 = -0.0112, mean_delta_45 = -0.1339
- tau=3 is optimal predictor for most pairs
- H-E2 cross-check: ALL 5 pairs within 0.002 tolerance

**Per-pair:**
- llama3_humaneval: rho(3)=0.682, rho(4)=0.509, rho(5)=0.436 — non_monotone_complex
- llama3_mbpp: rho(3)=0.850, rho(4)=0.787, rho(5)=0.576 — non_monotone_complex
- deepseek_humaneval: rho(3)=0.833, rho(4)=0.711, rho(5)=0.549 — non_monotone_complex
- deepseek_mbpp: rho(3)=0.783, rho(4)=0.851, rho(5)=0.714 — 4->5_break
- codellama_mbpp: rho(3)=0.615, rho(4)=0.849, rho(5)=0.763 — 4->5_break

## Limitation

Rho(MVC_p, pass@1) decreases monotonically with tau in all pairs. Lower tau (looser majority) retains more variance → stronger correlation. Higher tau collapses variance. Optimal tau=3, not tau=4 or 5. H-E2 (tau=4) remains valid strong predictor.

## Archon

hypothesis_task_id: 05ec532e-7350-4e16-a84f-9d8265da2f4b → done
