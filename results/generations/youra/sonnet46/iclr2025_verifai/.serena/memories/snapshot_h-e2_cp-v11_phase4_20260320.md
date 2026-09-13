---
name: h-e2 A_p-v11 Phase 4 completion
description: Phase 4 COMPLETE 2026-03-20: H-E2 (H-AgreePredict-v11) EXISTENCE gate FAIL (MUST_WORK). 0/5 pairs pass. A_p partial rho near-zero or negative. ROUTED_TO_PHASE_0. h-m1/m2/m3 CASCADE_FAILED.
type: project
---

# H-E2 Phase 4 Results (H-AgreePredict-v11)

**Completed:** 2026-03-20
**Gate:** MUST_WORK FAIL
**Routing:** ROUTED_TO_PHASE_0

## Gate Results

| Pair | N | partial_rho | p_perm | Gate |
|------|---|------------|--------|------|
| llama3_humaneval | 164 | -0.0186 | 0.5915 | FAIL |
| llama3_mbpp | 378 | -0.0231 | 0.6782 | FAIL |
| deepseek_humaneval | 164 | -0.1050 | 0.9106 | FAIL |
| deepseek_mbpp | 378 | +0.0507 | 0.1592 | FAIL |
| codellama_mbpp | 378 | -0.0041 | 0.5321 | FAIL |

**n_pairs_passing:** 0/5 (need >=3) → FAIL
**n_arch_passing:** 0/3 (need >=2) → FAIL

## Root Cause

A_p (mean pairwise 4-gram Jaccard) does NOT positively correlate with pass@1 after LOOM adjustment:
- High A_p = convergence to ANY solution (correct or incorrect)
- Easy problems: diverse but all-correct solutions → LOW A_p, HIGH pass@1
- Hard problems: identical wrong solutions → HIGH A_p, LOW pass@1
- This creates null-to-negative relationship, opposite of hypothesis direction

## Cascade Effects

- h-m1: CASCADE_FAILED (prerequisite h-e2 FAIL)
- h-m2: CASCADE_FAILED (via h-m1)
- h-m3: CASCADE_FAILED (via h-m1)

## Archon Updates

- h-e2 task 6473b121: status=done
- h-m1 task c85f0aa0: status=done (CASCADE_FAILED)
- h-m2 task 0e7323cd: status=done (CASCADE_FAILED)
- h-m3 task 31a94a39: status=done (CASCADE_FAILED)

## Files

- verification_state.yaml: h-e2 status=COMPLETED, gate=FAIL
- h-e2/04_validation.md: complete report
- h-e2/code/results/results.json: per-pair results
- h-e2/code/results/gate_result.json: gate summary
- h-e2/figures/: 4 figures generated
