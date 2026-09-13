# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-18T10:30:00+00:00
**Hypothesis:** h-m1
**Statement:** Under EvalPlus augmented test execution, if k=5 solutions are generated per problem per model using temperature sampling and evaluated via EvalPlus check_correctness, then pass@1 values are reliably computed with >=95% problem coverage, because the Run 3 infrastructure is validated and reusable.
**Final Status:** COMPLETED
**Gate Result:** PASS
**Gate Type:** MUST_WORK

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- Coverage: 1.0000 (all 3 models, 542/542 problems)
- Tests: 63/63 pass
- Coder-Validator Cycles: 1/5

## Key Findings
- All 3 models achieve 100% coverage on EvalPlus (HumanEval+ 164 + MBPP+ 378)
- Non-trivial pass@1 distributions (std > 0 for all models)
- llama3_8b: mean=0.3100, std=0.3310
- codellama_7b: mean=0.1229, std=0.1948 (weakest model)
- deepseek_6.7b: mean=0.3808, std=0.3450 (strongest model)
- h-m1 is purely a verification wrapper — no model inference required, runs in <30s
- pass_at_1_hm1_verified.json generated with FR-5.1 schema compliance
- h-m2 UNBLOCKED

## Output Files
- h-m1/results/pass_at_1_hm1_verified.json (FR-5.1 schema)
- h-m1/results/coverage_report.json
- h-m1/results/coverage_report.csv
- h-m1/figures/ (4 PNGs: coverage_rates, coverage_heatmap, pass_at_1_histograms, pass_at_1_cdf)

## Lessons for Phase 2A
- INCREMENTAL hypothesis setup (h-m1 based on h-e1) eliminates redundant work
- PATH 1 load chain: h-e1 pass_at_1 files are directly reusable
- CodeLlama-7b has very low pass@1 (mean=0.123); hard tier will be very large for h-m2

---
*Per-hypothesis snapshot for Phase 2A reference*
