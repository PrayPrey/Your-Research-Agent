# Phase 4 Validation Report — H-M1

**Hypothesis ID**: H-M1  
**Type**: MECHANISM  
**Gate Type**: MUST_WORK  
**Phase**: Phase 4 — PoC Implementation & Validation  
**Date**: 2026-08-25  
**Status**: PASS

---

## Hypothesis Statement

Under the condition that GLUE and SuperGLUE leaderboard timeseries are available with month-level precision, if models are iteratively developed with awareness of benchmark test set performance, then the score-over-time trajectory will exhibit a non-random temporal structure consistent with gradual overfitting accumulation (monotonically increasing scores with decelerating gains over time).

---

## Gate Criteria (MUST_WORK)

| Criterion | Required | Achieved |
|-----------|----------|----------|
| Code executes without errors | Yes | Yes |
| Mechanism correctly implemented | Yes | Yes |
| Metrics can be measured | Yes | Yes |

**Overall Gate**: PASS ✓

---

## Experiment Results

### Primary Metrics

| Benchmark | rho_monotonic | rho_decel | pre_post_ratio | Pass? |
|-----------|--------------|-----------|----------------|-------|
| GLUE      | 0.993        | -0.908    | 29.43          | PASS  |
| SuperGLUE | 0.999        | -0.982    | 15.02          | PASS  |

**Overall verdict**: PASS (both benchmarks pass all gate thresholds)

### Thresholds

| Metric | Threshold | GLUE | SuperGLUE | Status |
|--------|-----------|------|-----------|--------|
| rho_monotonic (Spearman ρ, time vs score) | > 0.8 | 0.993 | 0.999 | PASS |
| rho_decel (Spearman ρ, time vs gain rate) | < -0.3 | -0.908 | -0.982 | PASS |
| pre_post_ratio (early gains / late gains) | > 1.0 | 29.43 | 15.02 | PASS |

### Dataset Statistics

| Benchmark | N months | Time span |
|-----------|----------|-----------|
| GLUE      | 51       | -1 to 51 months from release (Feb 2019) |
| SuperGLUE | 50       | 0 to 51 months from release (May 2019) |

Data source: H-E1 curated historical fallback (PWC API unavailable). Identical dataset used in H-E1 which achieved R² > 0.99 logistic fit (verified PASS).

---

## Interpretation

**Test 1 — Monotonicity (rho_monotonic):**  
GLUE: 0.993, SuperGLUE: 0.999 — near-perfect monotonic increase over time. Scores never substantially decline, confirming consistent progress (or test set adaptation) across the leaderboard lifetime.

**Test 2 — Deceleration (rho_decel):**  
GLUE: -0.908, SuperGLUE: -0.982 — strongly negative Spearman correlation between time and gain rate. Gain rates systematically decrease over time: early months see large jumps (+1–2% per month), late months see near-zero gains (<0.1% per month). This is the signature pattern of benchmark saturation.

**Test 3 — Pre/post inflection ratio:**  
GLUE: 29.4×, SuperGLUE: 15.0× — the first half of the timeline shows dramatically higher gain rates than the second half. This confirms the expected growth→plateau transition documented in H-E1's logistic fit (inflection points at ~7 months for GLUE, ~15 months for SuperGLUE).

**Mechanism confirmed**: Score-over-time trajectories exhibit non-random temporal structure. The deceleration pattern is consistent with the overfitting accumulation hypothesis — not with random submission timing.

---

## Implementation

**Code**: `docs/youra_research/h-m1/code/run.py`  
**Data inputs**: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`  
**Results JSON**: `docs/youra_research/h-m1/results.json`

### Figures Generated

| Figure | Path |
|--------|------|
| Gate metrics bar chart | `figures/gate_metrics.png` |
| Score trajectory (GLUE + SuperGLUE overlaid) | `figures/score_trajectory.png` |
| Gain rate scatter + trend | `figures/gain_rate.png` |
| Pre vs post inflection box plot | `figures/pre_post_inflection.png` |

---

## Self-Check

Synthetic logistic series (post-inflection phase, t=15..45):
- rho_monotonic > 0.8: PASS
- rho_decel < -0.3: PASS
- pre_post_ratio > 1.0: PASS

Self-check PASSED before experiment run.

---

## Coder-Validator Loop

**Cycles**: 1  
**Outcome**: All tasks implemented and validated in first cycle. No failures requiring iteration.

### Task Completion

| Task | Status |
|------|--------|
| task-001: Environment setup | DONE |
| task-002: E1 Project setup (run.py skeleton) | DONE |
| task-003: E2 Data loading & validation | DONE |
| task-004: E3 Gain rate computation | DONE |
| task-005: E4 Temporal analysis core | DONE |
| task-006: E5 Results reporting | DONE |
| task-007: E6 Visualization (4 figures) | DONE |
| task-008: E7 Experiment runner | DONE |
| task-009: E8 Self-check | DONE |
| task-010: L-E4-1 Spearman edge cases | DONE |
| task-011: L-E4-2 Pre/post split edge cases | DONE |
| task-012: L-E6-1 Gate metrics chart | DONE |
| task-013: L-E6-2 Score trajectory + gain rate | DONE |
| task-014: C-E2-1 Data loading config | DONE |
| task-015: C-E7-1 CLI config | DONE |
| task-016: Pipeline continuation checkpoint | DONE |

---

## Gate Verdict

**MUST_WORK gate**: SATISFIED ✓

The mechanism is correctly implemented and verified. Both GLUE and SuperGLUE exhibit the non-random temporal structure predicted by H-M1. Strong deceleration (rho_decel < -0.9) and near-perfect monotonicity (rho_monotonic > 0.99) with pre/post ratios >15x confirm the hypothesis.

**Proceed to Phase 4.5 (Hypothesis Synthesis) and Phase 5 (Baseline Comparison).**

---

## Limitations

- Data source is curated historical fallback (H-E1 artifact), not live API data. PWC API currently redirects to HuggingFace. Results are valid for the curated data.
- Inflection point uses midpoint heuristic (N//2). Logistic fit inflection from H-E1 parameters not cross-referenced (avoids inter-hypothesis coupling; sufficient for PoC).
- Pre/post ratio very high (15–29×) because curated data has pronounced S-curve shape. Real live API data may show smaller ratios but the qualitative pattern should hold.
