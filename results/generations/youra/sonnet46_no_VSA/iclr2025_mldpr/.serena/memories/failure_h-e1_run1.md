# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-02T00:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL (G1 threshold not met)

## Performance Gap

| Gate | Metric | Value | Threshold | Status |
|------|--------|-------|-----------|--------|
| G1 | Gini std across (task, year) cells | 0.0654 | ≥ 0.10 | FAIL |
| G2 | Panel coverage | 97.7% | ≥ 60% | PASS |
| G3 | Mean unique authors/cell | 164.1 | ≥ 5.0 | PASS |
| G4 | Authors non-null fraction | 97.8% | ≥ 80% | PASS |

## Root Cause Analysis

- Gini median = 0.0: More than half of (task, year) cells have Gini ≈ 0 — diffuse authorship, not concentrated
- Most authors contribute exactly one paper per task per year, yielding near-zero inequality within cells
- Low mean Gini (0.049): distribution heavily left-skewed near zero — the "star author" concentration pattern does not appear in PwC data at annual/task granularity
- Gini std (0.065) below 0.10 threshold because individual Gini values cluster near zero with few high-outlier cells

## Lessons Learned

1. PwC authorship is diffuse at (task, year) granularity — Gini coefficient is near-zero for majority of cells
2. G1 threshold of ≥0.10 Gini std was too optimistic; empirical distribution shows std=0.065
3. G2–G4 (coverage, author count, non-null fraction) all strongly pass — data pipeline is high quality
4. The failure is conceptual (insufficient Gini spread), not a data or pipeline problem
5. Mechanism activated correctly (Gini computable, variation present) — the hypothesis assumption about authorship concentration was incorrect

## Feedback for Next Phase

### Suggested Modifications
- Revise G1 threshold downward (0.065 may still be scientifically useful variation)
- Investigate alternative concentration measures: H-index per task, top-author share, or paper-count Gini per author
- Use finer time granularity (quarters instead of years) to reduce within-cell equality
- Consider task-level aggregation rather than (task, year) cells to increase per-cell author counts

### What NOT To Do
- Do not assume star-author concentration exists in PwC at annual resolution
- Do not set Gini std threshold above 0.08 without empirical calibration

### What Showed Promise
- G2 coverage (97.7%): PwC panel joins well to h-e2 task list
- G3 mean authors (164.1): Rich multi-author data available for survival analysis
- G4 non-null (97.8%): Author data quality is excellent

---
*Routing: MUST_WORK gate FAIL → ROUTED_TO_PHASE_0*
*Written at: 2026-08-02T00:00:00Z*
*For cross-phase reference*
