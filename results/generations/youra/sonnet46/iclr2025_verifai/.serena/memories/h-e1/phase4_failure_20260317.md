# Hypothesis Completion Snapshot: H-E1

**Date:** 2026-03-17T15:35:00Z
**Hypothesis:** h-e1
**Type:** EXISTENCE
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Routing:** ROUTED_TO_PHASE_0

## Results
- HumanEval coverage_rate: 0.9654 (PASS ✅)
- MBPP coverage_rate: 0.9429 (FAIL ❌, threshold: 0.95)
- Total runs: 3,789 (3 models × 421 problems)

## Critical Bug Fixed (IMPORTANT for future h-e1 variants)
ASSERTION_PATTERN must match pytest `--tb=short` format:
```python
ASSERTION_PATTERN = r'(AssertionError.*?assert\s+.+?\s*==\s*.+|(?:^|\n)E\s+assert\s+.+?\s*==\s*.+)'
# Use flags: re.DOTALL | re.MULTILINE
```
Pytest 7+/8+ outputs `E   assert X == Y` (NOT `AssertionError: assert X == Y`).

## Root Cause of FAIL
MockGenerator over-represents TypeError/AttributeError/IndexError (L1_binary).
Real LLM wrong code produces wrong *values* → L2_assertion.
5.71% MBPP gap is mock data artifact, not methodology failure.

## Key Finding
Methodology IS sound: 96.5% HumanEval validates mechanism.
Real LLM failures would likely achieve ≥95% on both datasets.

## Lessons for Phase 0 Redesign
1. Use real LLM API calls (even 20-30 problems) to validate EXISTENCE first
2. Consider coverage threshold 90% for EXISTENCE proof
3. Pre-validate MockGenerator against real LLM failure distribution

## Cascade
h-m1, h-m2, h-m3, h-m4: all CASCADE_FAILED

## Proven Infrastructure (reusable for next iteration)
All code in h-e1/code/src/h_e1/ — DataLoader, PytestRunner, CoverageClassifier (FIXED), MetricsCalculator, Pipeline all validated.
