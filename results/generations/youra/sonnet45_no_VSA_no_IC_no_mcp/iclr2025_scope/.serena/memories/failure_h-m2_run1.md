# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-25T12:21:00Z
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| data_realness correlation | -0.363 | 0.800 (target) | -1.163 (145.4% below target) |
| eval_automation correlation | undefined | 0.800 (target) | N/A (constant scores) |
| infra_readiness correlation | undefined | 0.800 (target) | N/A (constant scores) |
| Sample size | 4 benchmarks | 20 benchmarks (expected) | -16 benchmarks (80% data loss) |

## Root Cause Analysis

- **Benchmark naming mismatch:** BCVF extraction (h-e2) uses different benchmark identifiers than expert ratings gold standard (imagenet vs imagenet-1k, squad vs squad2, glue vs glue-mnli, wmt_translation vs wmt14)
- **Data pipeline misalignment:** Only 4/20 benchmark names overlap between BCVF and expert datasets, reducing statistical power from n=20 to n=4
- **Signal extraction failure:** eval_automation and infra_readiness axes have zero variance (constant scores) across 4 common benchmarks, suggesting missing metadata or extraction bug in h-e2
- **Insufficient statistical power:** Fisher z correlation CI with n=4 produces extremely wide confidence intervals (CI width ≈ 1.9), making validation unreliable even if alignment fixed
- **Negative correlation on data_realness:** r=-0.36 with p=0.64 suggests BCVF signals do not measure expert-perceived data quality in current form

## Lessons Learned

1. **Benchmark identifier normalization is critical:** Machine-extracted benchmark names (from papers, GitHub repos) do not match canonical names used by human experts → fuzzy matching or canonical mapping layer required before validation
2. **Zero-variance detection needed:** h-e2 signal extraction should validate that all axes have non-constant scores before passing gate (detect missing metadata early)
3. **Sample size validation:** Correlation analysis requires n≥10 for robust Fisher z CI → data pipeline should verify overlap count before proceeding to validation
4. **Expert dataset integration:** Expert ratings gold standard should be consulted during h-e2 extraction (not just h-m2 validation) to ensure benchmark naming consistency
5. **Gate type mismatch:** MUST_WORK gate was appropriate — this failure indicates fundamental framework issue (BCVF signals do not correlate with expert judgment), not just implementation bug

## Feedback for Next Phase

### Suggested Modifications
- Implement benchmark name normalization layer (fuzzy matching + canonical mapping) before h-e2 extraction
- Extend h-e2 signal extraction to debug why eval_automation and infra_readiness have constant scores (missing README sections? PDF extraction bug?)
- Re-run h-e2 with corrected benchmark naming to increase overlap from 4 to 20 benchmarks
- Add zero-variance check to h-e2 gate criteria (reject if any axis has constant scores across ≥50% benchmarks)
- Validate sample size n≥10 before proceeding to h-m2 correlation analysis

### What NOT To Do
- Do not attempt to re-validate h-m2 without fixing h-e2 data alignment → same failure will recur
- Do not lower gate criteria (r>0.8) to accommodate weak correlation → expert agreement is non-negotiable for framework validation
- Do not use imputation or synthetic expert ratings to increase sample size → introduces bias and invalidates validation
- Do not proceed to Phase 5 baseline comparison → BCVF framework invalid until h-m2 passes

### What Showed Promise
- h-m1 continuous scoring mechanism works correctly (confidence-weighted aggregation + bootstrap CI)
- 04_validation.md report structure effectively visualizes correlation failure (scatter plots, Bland-Altman, per-benchmark error)
- Fisher z confidence intervals correctly quantify uncertainty (wide CI for n=4 signals unreliable validation)

---
*For cross-phase reference*
*Written at: 2026-08-25T12:21:00Z*
