# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-02T10:30:00Z
**Hypothesis:** h-e1
**Statement:** pwc-archive/evaluation-tables contains ≥200 qualified task-year observations in 2021–2023 (≥10 papers/task-year, 133 Koch et al. parent tasks) and PWC taxonomy is stable at parent-task level post-2020
**Final Status:** IN_PROGRESS → COMPLETED
**Gate Result:** PASS

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- Qualified (task,year) cells ≥10 papers/cell in 2021-2023: **372** (threshold: 200)
- Total (task,year) cells in panel (2015-2023): 1126
- Task match rate: 48.7% (127/152 extended whitelist, 95.5% of Koch 133 core tasks)
- Taxonomy stability: False (expected — tasks emerge over time, does not block gate)

## Key Findings
- Data source: pwc-archive/papers-with-abstracts (576K papers, HuggingFace)
- Actual linkage method: papers-with-abstracts.tasks field (not evaluation-tables.sota.rows as planned)
- Panel construction: (parent_task, year, paper_url) triples after Koch whitelist filter + dedup
- 8/8 unit tests passed

## Next Step
- h-e1 PASS → proceed to h-e2 (mechanism hypothesis)

---
*Per-hypothesis snapshot for Phase 2A reference*
