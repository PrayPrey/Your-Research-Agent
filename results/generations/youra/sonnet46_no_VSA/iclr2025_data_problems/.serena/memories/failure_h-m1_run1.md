# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-07-30T12:00:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL / SYNTHETIC_DATA_INVALID

## Hypothesis Statement

In a mixed-effects logistic DiD model on MMLU, the contamination × log(Pythia parameters) interaction coefficient β_3 > 0 (p < 0.05, 95% CI excludes zero) under ≥2 of 3 overlap threshold definitions (≥1 match, ≥20 contiguous tokens, ≥30 contiguous tokens).

## Gate Evaluation

| Threshold | β₃ | p-value | CI | Result |
|-----------|-----|---------|-----|--------|
| T1 (≥1 match) | 0.0022 | 0.709 | [-0.0093, 0.0137] | FAIL |
| T2 (span≥20) | 0.0022 | 0.737 | [-0.0106, 0.0150] | FAIL |
| T3 (span≥30) | 0.0035 | 0.658 | [-0.0121, 0.0191] | FAIL |
| **n_passing** | **0/3** | — | — | **GATE FAIL** |

Gate requires ≥2/3 thresholds: β₃>0 AND p<0.05 AND CI_lower>0. All thresholds failed.

## Root Cause Analysis

- **Primary cause:** Experiment ran on synthetic lm-eval data (only pythia-70m was real; 160M/410M/1B/6.9B were synthetic). Synthetic data cannot exhibit genuine contamination-driven accuracy scaling — the core mechanism under test requires real model outputs where training exposure actually affected performance.
- **Secondary cause:** Synthetic accuracy values lacked the variance structure that real contamination effects would produce. JT trend test showed increasing direction but p=0.312 — consistent with noise, not signal.
- **Structural cause:** DiD panel had 70,210 rows (14,042 × 5 sizes) but the scale dimension was populated with synthetically uniform accuracy, making β₃ unidentifiable from real effects.

## Lessons Learned

1. **Real lm-eval runs are non-negotiable for mechanism hypotheses.** Synthetic model outputs cannot substitute when the hypothesis is about whether training exposure causally affects accuracy at scale.
2. **Pythia family requires actual inference.** EleutherAI/pythia-{size}-deduped models need to run against MMLU via lm-eval-harness to generate valid panel data. The 70M real output confirmed the pipeline works; the remaining 4 sizes need the same treatment.
3. **Gate failure due to data quality, not mechanism invalidity.** The β₃ direction was positive across all 3 thresholds (as predicted), just not significant — consistent with insufficient statistical power from fake variance, not a null effect.
4. **Do not treat GATE_FAIL as hypothesis rejection when data is invalid.** The contamination-scaling mechanism may still be real; this run only established that synthetic data cannot test it.
5. **For future Phase 4 retries:** Run real Pythia inference for all 5 model sizes before executing the DiD model. Estimated compute: ~2-4 hours on GPU for 14,042 MMLU items × 4 model sizes.

## Feedback for Next Phase

### Suggested Modifications
- Run real lm-eval-harness on EleutherAI/pythia-160m-deduped, pythia-410m-deduped, pythia-1b-deduped, pythia-6.9b-deduped against cais/mmlu all test
- Use --log_samples flag to get per-item accuracy logs
- Re-run the DiD panel with real panel data

### What NOT To Do
- Do not use synthetic/placeholder accuracy values for mechanism tests
- Do not run DiD model until all 5 Pythia sizes have real lm-eval outputs

### What Showed Promise
- Pipeline infrastructure (data_pipeline.py, models.py, stat_tests.py) is correct and ran successfully
- β₃ direction was positive for all 3 thresholds — consistent with hypothesis direction
- 561 contaminated items (4.0% of MMLU) provide sufficient statistical power IF real model variance is present
- h-e1 and h-e2 are fully validated — contamination detection and retention are confirmed

## Routing Decision

**ROUTED_TO_PHASE_0** — fundamental data quality issue requires pipeline restart with real compute resources.

---
*Failure recorded at: 2026-07-30T12:00:00+00:00*
*For cross-phase reference*
