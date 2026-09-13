# H-M1 Validation Report

**Hypothesis:** Static Analysis Detects Structural Errors
**Type:** MECHANISM
**Gate:** MUST_WORK (>60% structural coverage)
**Status:** PASS

---

## Executive Summary

H-M1 validates that pylint+mypy static analysis detects structural errors in test-failing code. The mechanism successfully identified structural errors in **98.6%** of failing problems, far exceeding the 60% threshold.

---

## Gate Evaluation

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Structural Coverage | 98.6% | >60% | **PASS** |
| Failing Problems | 74 | - | - |
| With Structural Errors | 73 | - | - |

---

## Per-Benchmark Breakdown

| Benchmark | Failing | With Structural | Coverage |
|-----------|---------|-----------------|----------|
| HumanEval+ | 24 | 24 | 100.0% |
| MBPP+ | 50 | 49 | 98.0% |
| **Total** | **74** | **73** | **98.6%** |

---

## Structural Error Category Distribution

| Category | Count |
|----------|-------|
| syntax-error | 73 |
| unused-import | 8 |
| return-type-error | 3 |
| type-mismatch | 3 |
| unused-variable | 1 |

---

## Mechanism Verification

- Total structural errors detected: 88
- All category labels are valid (verified against STRUCTURAL_ERROR_CODES)
- Mechanism operates correctly: static analysis reliably detects structural errors in LLM-generated code

---

## Files Generated

- `code/outputs/results.json` - Full experiment results
- `figures/gate_metrics.png` - Coverage vs threshold bar chart
- `figures/category_breakdown.png` - Error category pie chart
- `figures/per_benchmark.png` - Per-benchmark coverage bar chart

---

## Conclusion

H-M1 **PASS**: Static analysis (pylint+mypy) successfully detects structural errors in nearly all (98.6%) test-failing LLM-generated code. The mechanism is validated and ready for H-M2 (Execution Detects Behavioral Errors).

---

*Generated: 2026-08-19*
*Phase: 4 (PoC Implementation & Validation)*
