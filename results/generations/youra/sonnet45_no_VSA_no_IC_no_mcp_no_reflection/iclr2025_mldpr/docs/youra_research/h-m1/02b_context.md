# Phase 2B Context: H-M1

**Date:** 2026-08-28
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Source:** 02b_verification_plan.md

---

## Hypothesis Statement

Under active leaderboard conditions (PWC 2018-2024), IF leaderboard top-5 scores show convergence (std <0.5% for 6 months), THEN this signal precedes community migration, BECAUSE architectural exploration plateaus as remaining gains require exponentially more effort (diminishing returns).

---

## Rationale

First causal step in saturation mechanism. Score convergence is observable plateau visible before velocity decay. ImageNet 2015-2017 rapid convergence (6.7%→2.3%) followed by slow creep (2017-2020: 2.3%→1.8%) demonstrates measurable signal.

---

## Variables

- **Independent:** Rolling 6-month window of top-5 scores
- **Dependent:** Standard deviation of top-5 scores
- **Controlled:** Benchmark (ImageNet, GLUE), Score metric (top-5 error, avg score)

---

## Success Criteria (PoC)

- **Primary:** Convergence detected (std <0.5%) aligns with expert consensus ±1 year for ≥2/3 benchmarks
- **Secondary:** Convergence precedes velocity decay detection

---

## Gate Condition

- **Type:** MUST_WORK
- **Pass:** Convergence detected and aligned with expert consensus
- **Fail:** Explore single-metric baseline, convergence alone may be insufficient

---

## Verification Protocol

1. Extract top-5 scores per month from PWC leaderboards (6-month rolling windows)
2. Compute std(top-5) for each window, identify first window where std <0.5%
3. Record convergence date (first detection), compare with expert consensus dates (±1 year)
4. Verify convergence precedes velocity decay (H-M2) by ≥1 month

---

## Prerequisites

- **H-E1:** VALIDATED (PASS) — PWC data exists with timestamps, expert consensus achievable

---

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Leaderboard Snapshots (2018-2024) (standard) | Provides historical leaderboard data for saturation detection (ImageNet, GLUE, SQuAD). Timestamped submissions enable score convergence + velocity decay analysis. |
| **Model** | Saturation Detection Algorithm (Dual-Metric Threshold) | Operationalizes saturation as score convergence (std <0.5% for 6mo) AND velocity decay (<0.1/mo for 6mo). Thresholds justified by ImageNet historical data (2015-2020 convergence patterns). |

---

## Dependencies & Context

- **Depends on:** H-E1 (PWC data + expert consensus existence)
- **Feeds into:** H-M2 (velocity decay detection)
- **Position in Chain:** H-E1 → **H-M1** → H-M2 → H-M3

---

*Context auto-generated from 02b_verification_plan.md*
