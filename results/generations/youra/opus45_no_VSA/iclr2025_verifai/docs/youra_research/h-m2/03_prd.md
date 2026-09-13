# Product Requirements Document: h-m2

**Version:** 1.0
**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis:** Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse) — fewer test regressions in static-first condition (p<0.05)

---

## 1. Executive Summary

This PRD defines the requirements for validating the h-m2 MECHANISM hypothesis through secondary analysis of h-e1 iteration logs. The experiment computes regression rates between iteration 1 and 2 for both feedback ordering conditions (static→exec vs exec→static) and tests for statistically significant differences using McNemar's test.

**Key Outcome:** Determine if static-first ordering reduces test regressions compared to execution-first ordering.

---

## 2. Problem Statement

**Context:** h-e1 demonstrated that static→execution ordering achieves better pass@1 than reverse ordering. h-m2 investigates the mechanism: does static-first reduce regressions (tests passing at iteration 1 but failing at iteration 2)?

**Hypothesis:** Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)

**Success Criteria:**
- Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
- McNemar p-value < 0.05

---

## 3. Functional Requirements

### FR-1: Log Data Loading
Load h-e1 iteration logs from `h-e1/code/results/h-e1_iteration_logs.jsonl`.

**Acceptance Criteria:**
- Parse JSONL format correctly
- Handle ~3,984 iteration outcome entries
- Filter by condition (static_first, exec_first)

### FR-2: Regression Rate Computation
Compute Regression Rate₁₂ for each condition.

**Formula:** (# tests passed at iter 1 but failed at iter 2) / (# tests passed at iter 1)

**Acceptance Criteria:**
- Compute for cascade (static→exec) condition
- Compute for reverse (exec→static) condition
- Handle edge case: passed_at_1 = 0 returns 0.0

### FR-3: Statistical Comparison
Compare regression rates using McNemar's test.

**Acceptance Criteria:**
- Build 2×2 contingency table of regression outcomes
- Use exact test (exact=True) for small sample sizes
- Report statistic and p-value

### FR-4: Hypothesis Verification
Verify h-m2 hypothesis based on computed metrics.

**Acceptance Criteria:**
- Return PASS if cascade_rate < reverse_rate AND p < 0.05
- Return PARTIAL if direction correct but not significant
- Return FAIL if cascade_rate >= reverse_rate

### FR-5: Visualization Generation
Generate required figures for results reporting.

**Required Figures:**
1. Regression Rate Comparison Bar Chart
2. Per-Iteration Pass Rate Trajectory (optional)
3. Contingency Table Heatmap (optional)

---

## 4. Data Specification

### 4.1 Input Data

| Dataset | Source | Type | Download Required |
|---------|--------|------|-------------------|
| h-e1 Iteration Logs | `../h-e1/code/results/h-e1_iteration_logs.jsonl` | JSONL | NO (local file) |

**Data Statistics:**
- Total problems: 664 (HumanEval 164 + MBPP 500)
- Iterations per problem: 3
- Conditions: 2 (static→exec, exec→static)
- Expected entries: ~3,984

### 4.2 Expected Log Format

```json
{
  "problem_id": "HumanEval/0",
  "condition": "static_first",
  "iteration_0": {"passed": false, "error_type": "assertion"},
  "iteration_1": {"passed": true, "error_type": null},
  "iteration_2": {"passed": true, "error_type": null},
  "iteration_3": {"passed": true, "error_type": null}
}
```

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Runtime: < 1 minute on CPU
- Memory: < 1 GB

### NFR-2: Reproducibility
- Fixed random seed (if applicable)
- Deterministic computation

### NFR-3: Output Format
- Results saved to `h-m2/code/results/`
- Figures saved to `h-m2/figures/`

---

## 6. Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse) | Required | P0 |
| McNemar p-value < 0.05 | Required | P0 |
| Code runs without error | Required | P0 |

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| statsmodels | >=0.13.0 | McNemar's test |
| numpy | >=1.21.0 | Numerical computation |
| pandas | >=1.3.0 | Data manipulation |
| matplotlib | >=3.4.0 | Visualization |
| seaborn | >=0.11.0 | Statistical plots |
| pyyaml | >=6.0 | YAML parsing |

### 7.2 External Dependencies

| Dependency | Source | Required |
|------------|--------|----------|
| h-e1 iteration logs | `../h-e1/code/results/h-e1_iteration_logs.jsonl` | YES |

---

## 8. Out of Scope

- New LLM API calls (this is log analysis only)
- Model training or fine-tuning
- New dataset collection
- Real-time execution
