# Phase 1 Research Data: h-m3

**Hypothesis ID:** h-m3  
**Date:** 2026-08-19  
**Research Question:** How does test coverage quality moderate feedback granularity requirements in code generation?

---

## Literature Review Summary

**Key Finding:**  
Test suite quality varies widely across code generation benchmarks. HumanEval provides comprehensive test suites (avg 7.5 tests/problem) while MBPP provides minimal coverage (3 tests/problem). No prior work systematically analyzes how test coverage moderates feedback design effectiveness.

---

## Reference Papers

**None explicitly cited** (This is a novel mechanism hypothesis building on h-e1's empirical findings)

**Related Work:**
- HumanEval benchmark (Chen et al., 2021): Established comprehensive test suite design
- MBPP benchmark (Austin et al., 2021): Entry-level problems with minimal test coverage
- Coverage.py documentation: Branch coverage measurement methodology

---

## Research Gap

**Identified Gap:**  
While prior work establishes that error-type feedback outperforms binary feedback (h-e1), no studies examine **when** this advantage emerges. Test coverage quality is a candidate moderator:
- High coverage → binary signal is sufficient (test suite exercises most code paths)
- Low coverage → error-type semantic hints compensate for weak test signals

**Hypothesis Origin:**  
Emerged from h-e1 validation analysis. Observed variance in per-problem feedback advantage suggested benchmark-level moderators. HumanEval vs MBPP differ systematically in test suite design → coverage quality is testable moderator.

---

## Datasets

**Primary: HumanEval**  
- Source: `openai/human-eval` (github.com/openai/human-eval)
- Problems: 164 hand-written Python functions
- Test suite: Comprehensive (avg 7.5 tests/problem)
- Expected coverage: 75-85% branch coverage

**Secondary: MBPP**  
- Source: `google-research-datasets/mbpp` (huggingface.co/datasets/mbpp)
- Problems: 974 entry-level Python problems
- Test suite: Minimal (3 tests/problem)
- Expected coverage: 45-60% branch coverage

**Coverage Measurement Tool:**  
- coverage.py v7.15+ (branch coverage mode)
- Source: `coveragepy/coveragepy` (github.com/coveragepy/coveragepy, 3393 stars)

---

## Methodology Extracted from Literature

**Coverage Measurement Protocol (from coverage.py documentation):**
1. Instrument code with `Coverage(branch=True)` 
2. Execute code + tests
3. Extract branch statistics: `total_branches`, `covered_branches`
4. Compute: `branch_coverage_pct = (covered / total) * 100`

**Per-Problem Pass@1 Evaluation (from HumanEval paper):**
1. Generate N samples per problem (standard: N=20)
2. Execute against test suite
3. Compute unbiased pass@k estimator: `1 - C(n-c, k) / C(n, k)`

**Correlation Analysis (standard statistical methodology):**
1. Compute per-problem feedback advantage: Δ = error-type pass@1 - binary pass@1
2. Test Pearson correlation: coverage vs Δ
3. Success criterion: r ≥ 0.77 (R² ≥ 0.6)

---

## Implementation Resources (from Exa Search)

**Coverage Measurement:**
- coveragepy/coveragepy (3393 stars): Official branch coverage implementation
- microsoft/coverage-eval (25 stars): HumanEval with coverage annotations (reference)

**Evaluation Harnesses:**
- openai/human-eval (3345 stars): Standard pass@k estimator
- bigcode-project/bigcode-evaluation-harness (500+ stars): Multi-benchmark evaluation

**Documentation:**
- coverage.readthedocs.io/en/latest/branch.html: Branch coverage measurement guide

---

## Expected Contribution

**Novel Contribution:**  
First systematic analysis of test coverage as moderator of feedback granularity requirements. Informs when lightweight binary feedback suffices vs when semantic error-type hints are needed, enabling benchmark-adaptive feedback design.
