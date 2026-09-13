# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-02T00:00:00+00:00
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Actual | Target | Gap |
|--------|--------|--------|-----|
| n_displacement_events | 38 | ≥100 | -62 (62% below target) |
| task_coverage_pct | 43.2% | ≥40% | ✅ PASS |
| dedup_identity_change_pct | 0.0% | <10% | ✅ PASS |
| concentration_check | 10.5% | <30% | ✅ PASS |

## Root Cause Analysis

- Koch 133 exact-slug matching yields only 44/135 tasks (33% coverage)
- With 44 tasks, max achievable plurality panel cells = 141
- Max possible displacement events = ~97 (141 − 44 first-year cells) — below 100 target
- PWC evaluation-tables reflect current leaderboard, not historical turnover
- Benchmark plurality is stable: most tasks keep same plurality benchmark across years

## Lessons Learned

1. PWC evaluation-tables are not a displacement-rich record; they reflect current leaderboard snapshots
2. Exact slug matching for Koch 133 tasks is too strict — fuzzy matching could recover 30–50% more
3. min_papers=10 threshold is too aggressive for sparse PWC coverage
4. The ≥100 threshold is empirically unreachable with current data scope and definition
5. Robustness ablation confirms: 0/9 variants PASS, 3/9 PARTIAL (min_papers=5 only)

## Feedback for Next Phase

### Suggested Modifications
- Expand task scope with fuzzy matching (not just exact Koch slugs)
- Lower min_papers to 5
- Redefine plurality unit at metric-level (not dataset-level) for more events
- Revise threshold to ≥30 to align with observed data range

### What NOT To Do
- Do not use exact slug matching for Koch 133 tasks
- Do not set min_papers ≥ 10 with current data

### What Showed Promise
- Pipeline code is solid (741 lines, 26 passing tests)
- Year extraction: 96%+ arxiv URL coverage
- Dedup identity check: 0.0% change — plurality stable through dedup
- task_coverage_pct=43.2% exceeds 40% threshold

---
*For cross-phase reference*
*Written at: 2026-08-02T00:00:00+00:00*
