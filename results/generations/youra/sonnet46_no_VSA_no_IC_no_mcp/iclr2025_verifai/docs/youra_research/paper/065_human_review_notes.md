# Human Review Notes — Phase 6.5 Minor Issues

**Generated:** 2026-08-26
**For:** Manual review before final submission — do NOT auto-fix these.

---

## MINOR Issues

### M1: Related Work Coverage (Section 2)
**Location:** 06_paper_final.md, Section 2 (Related Work)
**Issue:** Only 4 related work families covered. For main-track ICML, a reviewer may expect:
- LLM-generated unit tests (ChatUniTest, CodaMosa) as an alternative structured feedback approach
- Broader program repair benchmarks (SWE-bench, LiveCodeBench) for context
**Suggestion:** Add 2–3 sentence paragraph on test-based repair as alternative structured feedback, contrasting with static analysis feedback.

### M2: Table 1 approximate values
**Location:** 06_paper_final.md, Results Section, Table 1, non-type-error row
**Issue:** "~78%" and "~79%" used for Condition A and B non-type-error rates. Exact values from h-m2 validation: Condition A = 83.8%, Condition B = 84.4%.
**Note:** Ground truth records these as exact: `repair_rate_condition_a: 0.909` (type) and `differential_non_type: 0.006`. The 83.8%/84.4% exact values are in h-m2/04_validation.md line 37.
**Suggestion:** Replace "~78%" with "83.8%" and "~79%" with "84.4%" for precision. Verify against results/analysis.json before changing.

### M3: "general diagnostic context enricher" terminology
**Location:** Abstract, Introduction, Discussion
**Issue:** Term "general diagnostic context enricher" may be unclear to non-NLP reviewers.
**Suggestion:** Consider adding a one-clause definition on first use: "...general diagnostic context enricher — a feedback channel that improves repair quality broadly rather than for a specific error type."

---

## Verified-Correct Items (Do Not Change)

- All seed values (Table 2): verified exact against ground truth
- Spearman ρ=−0.707: verified from h-m1 source
- p=0.182: correctly reported in sections/05_results.md after R1 fix
- 91.1% Z3 validity: verified 112/123 from h-z1 source
- All MUST_WORK/SHOULD_WORK gate results: match verification_state.yaml
