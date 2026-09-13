# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-08-03T06:00:00+00:00
**Hypothesis:** h-m1
**Statement:** C_t (cumulative evaluation-table submission count at plurality introduction year) is a meaningful proxy for accumulated community investment
**Final Status:** COMPLETED
**Gate Result:** MUST_WORK gate FAILED — partial_r2=0.0011 (<0.05 threshold)

## Results

- Validation: FAIL
- Gate Type: MUST_WORK
- Failed Condition: partial_r2 (0.0011 < 0.05)
- Passed Conditions: r_ct_age=0.447 (<0.80 ✓), r_ct_year=0.447 (<0.80 ✓), VIF(C_t)=1.25 (<5.0 ✓)
- N: 87 benchmarks (full dataset)
- Coder-Validator Cycles: 1/5 (passed first cycle)
- Tests: 17/17 passing

## Reflection

- Reflection Outcome: ROUTED_TO_PHASE_0
- Root Cause: log_publication_volume proxy (papers_linked_count, total_submissions) has r=-0.045 with log_C_t — circular measurement from same PWC source
- Secondary: task_age = 2026 - benchmark_introduction_year creates perfect collinearity (VIF=∞ for both confounders)
- Data gap: h-e1 pipeline never collected independent publication volume metric

## Key Lessons for Phase 2A Reference

1. C_t is NOT multicollinear with temporal confounders (VIF=1.25) — mechanism driver is sound
2. Outcome variable must be independently measured (not from same PWC source)
3. Use only ONE temporal confounder (task_age OR benchmark_introduction_year, not both)
4. Arxiv YYMM date decoder `(raw_yr % 100) > 12` pattern — reusable in h-m2, h-e2

## Reusable Components (from code/)

- `data_loader.py:58-60` — arxiv YYMM decoder
- `analysis.py:compute_aux_ols_residuals` — OLS residualization
- `analysis.py:compute_partial_r2` — partial r² computation
- `gates.py:evaluate_gates` — parameterizable gate logic
- `figures.py` — headless matplotlib figure generation

## Next Steps

- Phase 0: find independent community-engagement proxy (Semantic Scholar citations, CrossRef, arXiv downloads)
- H-M2 blocked until h-m1 passes

---
*Per-hypothesis snapshot for Phase 2A reference*
