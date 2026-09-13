# Hypothesis Completion Snapshot: H-M1

**Date:** 2026-08-03T08:30:00Z
**Hypothesis:** H-M1
**Statement:** log_unique_paper_count_at_intro_z significantly predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1): LRT p < 0.05 AND |HR-1| ≥ 0.10
**Final Status:** VALIDATED (null result — see gate)
**Gate Result:** FAIL (meaningful null / H0)

## Results
- Validation: FAIL (meaningful null)
- Gate Type: MUST_WORK
- p-value: 0.9495 (threshold: < 0.05)
- HR: 1.0056, |HR-1|: 0.0056 (threshold: ≥ 0.10)
- Direction: H0 (null — community breadth does not predict displacement timing)
- Concordance (M1): 0.7363
- Panel rows: 258 (87 dropped for NaN)

## Scientific Interpretation
Clean null result: log_unique_paper_count_at_intro_z is well-measured (H-E1 validated, G1 partial_r²=0.6053) but explains no variance in displacement hazard. Routes to Phase 6 as publishable null finding.

## Key Lessons
- lifelines CI columns: "95% lower-bound" / "95% upper-bound" (not "lower 0.95")
- NaN pattern in panel reduces 345→258 rows — investigate in Phase 6
- Reuse fit_models(), run_lrt(), LRTResult for H-M2 (change diversity_col)

---
*Per-hypothesis snapshot for Phase 2A reference*
