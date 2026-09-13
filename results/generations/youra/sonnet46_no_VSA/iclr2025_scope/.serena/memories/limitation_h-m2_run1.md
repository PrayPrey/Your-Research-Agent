# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-03T17:45:00Z
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Proxy experiment used identical base LLaMA-3.1-8B for both MOHAWK-SSM and LAWCAT because
H-E1 distillation failed (EADDRINUSE port conflict during MOHAWK Stage 1 training).
Statistical pipeline validated end-to-end but under null-hypothesis proxy conditions:
β_SSM = β_LAWCAT = 0.1814, ratio = 1.0. No differential depth-slope signal was detectable.
The actual hypothesis (differential depth-slope between genuinely converted models) remains untested.

## Failed Checks

- β ratio |β_depth^SSM| / |β_depth^LAWCAT| ≥ 2.0 (observed: 1.0 — identical proxy models)
- MOHAWK-SSM vs LAWCAT model checkpoints unavailable (H-E1 prerequisite incomplete)

## Partial Results

| Metric | Value |
|--------|-------|
| β_SSM | 0.1814 |
| β_LAWCAT | 0.1814 |
| ratio | 1.0 |
| gate_satisfied | false |
| retrieval_examples_loaded | 158 |
| depth_percentile_mean | 0.96 |

## Experiment Summary

Statistical pipeline successfully validated: 158 retrieval examples from LongBench v2 loaded,
depth percentiles computed (mean=0.96, fallback=0.6%), statsmodels MixedLM regression fitted
(rpy2 unavailable — Python fallback used). 4 figures generated. The limitation is NOT a
statistical pipeline failure — it is a prerequisite data failure (H-E1 models not available).

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Re-run H-M2 after H-E1 distillation produces valid MOHAWK-SSM and LAWCAT checkpoints
2. Fix H-E1 EADDRINUSE port conflict (ensure no other distributed training process occupies the port)
3. The depth-slope differential mechanism is still theoretically sound — only the proxy data prevented measurement

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-03T17:45:00Z*
*For cross-phase reference*
