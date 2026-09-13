# Limitation Record: H-M2 (Run 1)

## Hypothesis
Under the HumanEval baseline failure cases (problems that fail in no-feedback single-pass generation with Llama 3.1 8B), if pylint+mypy is run on the failing code without execution, then fewer than 50% of failure cases receive at least one pylint/mypy warning or error.

## Gate Type
SHOULD_WORK

## Gate Result
NULL_RESULT (coverage=1.00 >= 0.50 threshold)

## Reflection Outcome
LIMITATION_RECORDED

## Limitation Description
H-M2 NULL RESULT: pylint flags 100% of baseline failures but 94.3% are Convention/style flags (C0304: Final newline missing, C0114: Missing module docstring). These fire universally on LLM-generated code snippets that lack trailing newlines and module docstrings. The measurement spec included ALL pylint categories per PRD definition (flagged = pylint_count > 0), so this result is technically correct.

**Functional-only coverage (E+W categories): 8/64 = 12.5%** — this WOULD satisfy the hypothesis.

Mypy detected 0% of failures (mypy_coverage=0.0%).

## Failed Checks
- coverage=1.00 >= 0.50 threshold (gate not satisfied)
- Dominant detection: C (Convention) 94.3% — style flags, not functional errors

## Experiment Results
- n_total: 64
- coverage: 1.0
- pylint_coverage: 1.0
- mypy_coverage: 0.0
- n_pylint_only: 64
- n_mypy_only: 0
- n_both_flagged: 0
- n_neither: 0
- pylint_category_totals: E=1, W=7, C=283, R=8, I=0

## Lessons Learned
1. When measuring pylint "coverage," ALL pylint messages must be filtered by category to separate style (C/R/I) from functional (E/W) detections
2. Pylint C-category flags (C0304, C0114) are universal on isolated code snippets — they cannot be used to assess functional error detection
3. Mypy detects 0% of HumanEval logic failures (confirmed: all failures are runtime/assertion errors, not type errors)
4. The causal mechanism from H-M1 is still supported: functional pylint coverage = 12.5%, while execution feedback solved 100% of its unique cases

## Pipeline Impact
- SHOULD_WORK gate: pipeline continues regardless
- H-M3 can proceed (no cascade blocking)
- This null result is publishable: shows pylint detection dominated by style, not function

## Date
2026-08-05T09:35:00Z
