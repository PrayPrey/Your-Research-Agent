# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-04-19T21:08:33.524484
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| HumanEval Enrichment | ≥1.67× | 1.00× | ✗ FAIL |
| HumanEval Q4 Coverage | ≥50% | 25.0% | ✗ FAIL |
| MBPP Enrichment | ≥1.67× | 1.00× | ✗ FAIL |
| MBPP Q4 Coverage | ≥50% | 25.1% | ✗ FAIL |

## Root Cause Analysis

- Divergence signal (Tier-2, k=3) shows no stratification - all quartiles have similar defect density
- Defect density extremely high (97.6% humaneval, 99.8% mbpp) - little room for ranking
- Unit test + Z3 labeling may be overly strict, marking nearly all generated code as defective
- Core assumption violated: defects do NOT concentrate in high-divergence regions

## Lessons Learned

1. Tier-2 bounded symbolic execution (k=3) does not provide discriminative signal for LLM-generated code
2. Near-universal defect rates (97-99%) indicate either overly strict labeling or fundamental dataset issues
3. Quartile-based enrichment analysis requires meaningful signal variance - uniform distributions yield 1.0× enrichment
4. EXISTENCE hypotheses must validate core signal stratification before proceeding to MECHANISM hypotheses

## Suggested Revisions for Phase 0

### Recommended Changes
- Reconsider divergence metric - Tier-2 k=3 may not capture semantic uncertainty effectively
- Review defect labeling methodology - 97-99% defect rate suggests overly strict criteria or test suite issues
- Consider alternative signals: AST complexity metrics, test coverage analysis, or learned code embeddings
- Investigate transfer learning approaches rather than pure symbolic execution

### What NOT To Do
- Do not proceed with MECHANISM hypotheses (h-m1 through h-m4) based on this failed signal
- Do not simply increase symbolic execution depth (k) without validating signal quality
- Do not relax gate thresholds - the core signal is not stratified

### What Showed Promise
- Pipeline infrastructure successfully executed all stages (data loading, generation, analysis, evaluation)
- Experimental design was sound - failure reveals hypothesis issue, not implementation issue
- Visualization and metrics collection worked as intended

---
*For cross-phase reference*
*Written at: 2026-04-19T21:08:33.524489*
