# Phase 4 Failure Record: h-e1_v4 (Run 1)

**Date:** 2026-03-19T17:00:00+00:00
**Hypothesis:** h-e1_v4
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| pcd_exceedance pairs passing | 0/5 | ≥3/5 | FAIL |
| pcd_exceedance (all pairs) | 0.0000 | ≥0.50 | FAIL |

## Root Cause Analysis

- **Fundamental identity:** PCD_obs == pass@1_p by construction. With binary pass/fail execution traces, the "dominant passing cluster" is simply all solutions that pass, which equals pass@1_p. There is no additional structural signal.
- **Null always exceeds observed:** Q_0.95(Binomial(5, theta)/5) >> theta for mid-theta (0.2≤theta≤0.8), so PCD_obs can never exceed the null threshold.
- **FCD inversion (negative control):** FCD > PCD for 4/5 pairs, demonstrating PCD has no specificity — it cannot distinguish passing from failing cluster structure.
- **D_p diagnostic OK (0.28-0.39):** Data quality confirmed, the failure is in the metric design, not the data pipeline.
- **Binary trace collapses cluster structure:** The PCD metric requires non-binary execution traces to capture genuine structural convergence.

## Lessons Learned

1. **Binary pass/fail traces collapse PCD to pass@1** — PCD needs richer trace representation (e.g., branch coverage vectors, output token sequences, execution path IDs).
2. **Null construction is too easy to satisfy from below** — Binomial null with theta=pass@1 sets a ceiling that binary PCD cannot exceed by construction.
3. **Negative control (FCD) should be strictly ≤ PCD** — If FCD consistently ≥ PCD, the metric has no specificity and the hypothesis is falsified.
4. **Redefine cluster structure:** PCD v5 should use multi-dimensional execution traces where "cluster dominance" measures something beyond pass rate alone.
5. **v3 calibration code is reusable** — The MC simulation infrastructure is sound; only the trace representation and PCD computation need redesign.

## Feedback for Phase 0 Redesign

### What NOT To Do
- Do not use binary pass/fail as the trace representation for PCD
- Do not define PCD as fraction of solutions matching dominant passing trace when "matching" means "passing"
- Do not expect MC Binomial null to be exceeded by a metric that is mathematically identical to pass@1

### What Showed Promise
- D_p (problem difficulty from pass@1) works well as a covariate (0.28-0.39)
- EvalPlus data pipeline is robust and reusable
- MC calibration infrastructure (calibration.py) is sound and reusable
- The core hypothesis (cluster structure → epistemic stability → pass@k) is conceptually sound

### Suggested Directions
- Use execution trace vectors (branch IDs, output tokens, coverage) for richer cluster representation
- Define PCD as dominant cluster fraction using cosine similarity or Hamming distance thresholds
- Consider ExecTraceDiversity (h-ExecTraceDiversity-v1) as a related successful approach for inspiration

---
*Routed to Phase 0 for fundamental redesign*
*Written at: 2026-03-19T17:00:00+00:00*
*For cross-phase reference*
