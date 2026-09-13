# Hypothesis Context: h-e2

**Date:** 2026-08-28
**Hypothesis ID:** h-e2
**Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Improvement velocity <0.1 improvement/month sustained for 6 months is measurable via linear regression on leaderboard submission timestamps

---

## Rationale

This validates that velocity decay detection (second half of dual-metric saturation detector) is technically feasible. Without measurable velocity decay signal, the saturation detection mechanism collapses to convergence-only detection.

---

## Variables

- **Independent Variable (IV):** Monthly score improvement (linear regression slope score vs. time)
- **Dependent Variable (DV):** Improvement velocity (points/month)
- **Controlled Variables (CV):** Benchmark, Regression window (6 months)

---

## Success Criteria (PoC)

- **Primary:** Velocity decay detected (<0.1/mo) can be measured via linear regression for ≥1 benchmark
- **Secondary:** Measurement method produces stable, reproducible results across multiple rolling windows

---

## Gate Condition

- **Type:** MUST_WORK
- **If Fail:** Saturation detector cannot use velocity decay metric, must pivot to convergence-only detection or abandon dual-metric approach

---

## Prerequisites

None (foundation hypothesis)

---

## Verification Protocol

1. Extract timestamped submissions from Papers With Code API (ImageNet, GLUE, or SQuAD)
2. Fit linear regression (score vs. time) for 6-month rolling windows
3. Extract slope (improvement/month) from regression
4. Identify windows where slope <0.1/mo
5. Validate measurement stability across multiple windows

---

## Experimental Setup (from Phase 2B Section 1.3)

**Dataset:**
- **Name:** Papers With Code Leaderboard Snapshots (2018-2024)
- **Type:** standard
- **Source:** Papers With Code public API + manual scraping for missing timestamps
- **Path:** https://paperswithcode.com/api/v1/benchmarks/
- **Justification:** Provides historical leaderboard data for saturation detection (ImageNet, GLUE, SQuAD). Timestamped submissions enable score convergence + velocity decay analysis.

**Model:**
- **Name:** Saturation Detection Algorithm (Dual-Metric Threshold)
- **Type:** rule-based + statistical
- **Source:** Custom implementation: rolling window std(top-5 scores) + linear regression (score vs. time)
- **Justification:** Operationalizes saturation as score convergence (std <0.5% for 6mo) AND velocity decay (<0.1/mo for 6mo). Thresholds justified by ImageNet historical data (2015-2020 convergence patterns).

---

## Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Velocity-Only Saturation Detection | Single metric: velocity <0.1/mo for 6mo (ignore convergence) | Historical benchmarks |
| Manual Inspection | Human analyst identifies velocity decay via visual inspection | Historical benchmarks |

---

## Dependencies

None

---

## Source

Phase 2B Verification Plan Section 2.2 (adapted from H-M2: Velocity Decay Detection)
