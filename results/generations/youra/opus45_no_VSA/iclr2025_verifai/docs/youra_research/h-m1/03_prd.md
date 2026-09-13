# Product Requirements Document: H-M1
## Early Iteration Gain Analysis (ΔPass₁₂ Trajectory)

**Generated**: 2026-08-09  
**Hypothesis**: h-m1  
**Type**: MECHANISM (SHOULD_WORK gate)
**Prerequisite**: h-e1 (VALIDATED)

---

## 1. Executive Summary

Analyze h-e1 iteration logs to test whether static-first ordering produces larger early iteration gains (ΔPass₁₂) than reverse ordering. This is a post-hoc statistical analysis of existing data, not a new experiment.

---

## 2. Problem Statement

H-e1 demonstrated that static→execution ordering achieves 29% relative improvement over reverse ordering. H-m1 investigates the mechanism: does static-first scaffolding produce faster convergence in early iterations?

**Hypothesis Statement**: ΔPass₁₂(cascade) > ΔPass₁₂(reverse) with p<0.05

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load h-e1 iteration logs from `h-e1/code/results/h-e1_iteration_logs.jsonl`
- Expected format: `{problem_id, condition, iteration, passed}`
- Total records: 3,984 (664 problems × 2 conditions × 3 iterations)

### FR-2: Data Validation
- Verify required fields: problem_id, condition, iteration, passed
- Verify conditions: "static_first", "exec_first"
- Verify iterations: {1, 2, 3}
- Fail fast if log format incompatible

### FR-3: ΔPass₁₂ Computation
- For each condition:
  - Compute cumulative pass@1 at iteration 1 (problems solved by iter 1)
  - Compute cumulative pass@1 at iteration 2 (problems solved by iter 1 OR 2)
  - ΔPass₁₂ = pass@1_iter2 - pass@1_iter1

### FR-4: Statistical Comparison
- Compare ΔPass₁₂(static_first) vs ΔPass₁₂(exec_first)
- McNemar's test on newly solved problems at iteration 2
- Report p-value and effect direction

### FR-5: Visualization
- **Required**: ΔPass₁₂ bar chart with error bars
- **Optional**: Iteration trajectory plot (cumulative pass@1 vs iteration)
- Save to `h-m1/figures/`

---

## 4. Non-Functional Requirements

### NFR-1: No API Calls
- Pure post-hoc analysis of existing logs
- No LLM inference required
- No external data downloads

### NFR-2: Reproducibility
- Deterministic computation (no random sampling)
- Results byte-identical across runs

### NFR-3: Performance
- Complete analysis in <10 seconds
- Single-threaded sufficient for 3,984 records

---

## 5. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| ΔPass₁₂(static_first) > ΔPass₁₂(exec_first) | True |
| McNemar p-value | < 0.05 |
| Code runs without error | True |

---

## 6. Output Artifacts

| File | Description |
|------|-------------|
| `results/h-m1_analysis.json` | ΔPass₁₂ values, p-value, effect direction |
| `figures/delta_pass_12_comparison.png` | Bar chart with error bars |
| `figures/iteration_trajectory.png` | Cumulative pass@1 vs iteration |

---

## 7. Dependencies

- Python 3.8+
- scipy (McNemar's test)
- matplotlib (visualization)
- h-e1/code/results/h-e1_iteration_logs.jsonl (prerequisite data)

---

## 8. Relationship to H-E1

This hypothesis EXTENDS h-e1 by analyzing its iteration trajectory:
- **h-e1**: Proved static-first ordering is better (29% improvement)
- **h-m1**: Investigates WHY — are gains concentrated in early iterations?

If h-m1 confirms, it supports the "scaffolding" mechanism: static feedback fixes surface issues early, enabling execution feedback to address deeper semantic bugs.
