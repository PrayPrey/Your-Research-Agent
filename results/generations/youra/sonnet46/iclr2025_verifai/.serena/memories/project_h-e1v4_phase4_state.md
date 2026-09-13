---
name: h-e1_v4 Phase 4 completion state
description: Phase 4 COMPLETE 2026-03-19. gate FAIL (MUST_WORK). PCD_obs==pass@1_p by construction (binary trace collapses). 0/5 pairs exceed null. reflection_outcome=ROUTED_TO_PHASE_0. CASCADE_FAILED: h-m1_v4, h-m2_v4, h-m3_v4.
type: project
---

# Hypothesis Completion Snapshot: h-e1_v4

**Date:** 2026-03-19T17:00:00+00:00
**Hypothesis:** h-e1_v4
**Statement:** Under the PCD v4 framework (k=5, temperature=0.8, EvalPlus binary evaluation), observed PCD for problems in the partial-competence tier (0.2 ≤ pass@1 ≤ 0.8) significantly exceeds the MC Bernoulli null distribution (i.i.d. draws at empirical θ=pass@1), demonstrating that PCD reflects genuine structural convergence rather than sampling noise. Success: ≥50% of mid-θ problems exceed both thresholds (Q_0.95 AND ES≥0.5) in ≥3/5 model-benchmark pairs.
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results

- pcd_exceedance: 0/5 pairs pass (all 0.0000)
- PCD_obs ≡ pass@1_p by construction (binary trace collapse)
- FCD exceedance (9.52%) > PCD exceedance (0%) for llama3_mbpp — negative control inverted
- D_p diagnostic: 0.28–0.39 (data quality OK)
- n_mc_simulations: 100,000 (correct)

## Cascade

- h-m1_v4: CASCADE_FAILED
- h-m2_v4: CASCADE_FAILED
- h-m3_v4: CASCADE_FAILED

## Reflection

- Reflection: ROUTED_TO_PHASE_0 — PCD_obs equals pass@1_p by construction with binary trace representation
- Root cause: Mathematical identity: PCD(binary k=5) = fraction passing = pass@1 estimate
- Serena memory: failure_h-e1_v4_run1

## Phase 4 Files

- 04_validation.md: Complete
- reflection_report.md: Written (step-06b complete)
- code/: ~2,456 lines (config, pcd, calibration, gate, metrics, main, visualization)
- figures/: 5 PNG files generated

---
*Per-hypothesis snapshot for Phase 2A/Phase 0 reference*
*step-08 completion: 2026-03-19T17:00:00+00:00*
