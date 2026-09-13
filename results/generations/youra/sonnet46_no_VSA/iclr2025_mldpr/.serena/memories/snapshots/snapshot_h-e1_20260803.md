# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-03T04:00:00+00:00
**Hypothesis:** h-e1
**Statement:** Fuzzy task name normalization (RapidFuzz token_sort_ratio ≥85) achieves ≥80% coverage mapping pwc-archive/evaluation-tables task_path to h-e2 task names (87 tasks).
**Final Status:** COMPLETED
**Gate Result:** PASS (coverage=0.920, threshold=0.80)

## Results

- Coverage at threshold=85: **0.920** (80/87 tasks matched)
- Baseline exact match: 0.874 (76/87)
- Gate criterion: coverage ≥ 0.80 — **satisfied**
- Leaf-path fallback: not triggered (primary coverage sufficient)
- Unmatched (7): Crowd Counting, Image Translation, Low-Light Image Enhancement, 3D Point Cloud, Deraining, Monocular Depth Estimation, Vehicle Detection

## Key Findings

- Dataset column is `task` not `task_path` (schema note for downstream)
- 87.4% baseline means pwc-archive vocabulary closely matches h-e2 panel
- Coverage robust across thresholds: ≥0.80 holds for all thresholds ≤ 90
- Use `threshold=85` for H-E2 join (pre-registered, passes gate with margin)

---
*Per-hypothesis snapshot for Phase 2A reference*
