# PRD: SA Metric Correlation with Functional Correctness (H-M1)

**Generated:** 2026-08-24
**Hypothesis:** H-M1 (MECHANISM)
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (VALIDATED)

---

## Executive Summary

Determine whether static analysis metrics (pylint score, mypy error count, radon cyclomatic complexity) correlate with functional correctness (pass@1) on LLM-generated code. This is a mechanism test to validate SA metrics as potential proxy signals for code quality before integrating them into training feedback loops.

---

## Problem Statement

SA tools reliably produce numeric outputs on LLM code (H-E1 validated). The next question: do these metrics actually predict whether code will pass functional tests? If at least one SA metric shows meaningful correlation (r ≥ 0.35), it becomes a candidate for feedback signal in code generation systems.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval (164 problems) from `openai/human-eval`
- Load MBPP sanitized (427 problems) from HuggingFace `google-research-datasets/mbpp`
- Deduplicate to 591 unique problem-solution pairs
- Use canonical solutions (ground truth) for SA metric extraction

### FR-2: LLM Code Samples
- Option A: Load pre-generated LLM completions (e.g., GPT-4, CodeLlama)
- Option B: Generate fresh samples via API (single completion per problem)
- Format: JSONL with `task_id`, `completion`, `passed` fields
- Total: 591 samples (1 per problem, pass@1 setting)

### FR-3: Pass@1 Evaluation
- Execute test cases from HumanEval/MBPP for each completion
- Binary outcome: passed (1) or failed (0)
- Timeout: 5 seconds per test execution
- Store in `passed` column

### FR-4: SA Metric Extraction
- Reuse H-E1 wrappers (pylint, mypy, radon)
- Extract for each LLM completion:
  - `pylint_score`: float (0-10)
  - `mypy_errors`: int (error count)
  - `radon_cc`: float (avg cyclomatic complexity)
  - `loc`: int (lines of code, covariate)

### FR-5: Point-Biserial Correlation
- Compute raw point-biserial r for each SA metric vs `passed`
- Library: `scipy.stats.pointbiserialr`
- Output: r value, p-value per metric

### FR-6: Partial Correlation (LOC Control)
- Compute partial correlation controlling for `loc`
- Library: `pingouin.partial_corr`
- Output: r_partial, p_partial per metric
- Purpose: Remove code length as confounding variable

### FR-7: Result Aggregation
- Output files:
  - `results/h_m1_correlations.json` (per-metric r, p values)
  - `results/h_m1_data.csv` (per-sample metrics)
  - `results/h_m1_summary.json` (max r, pass/fail determination)

### FR-8: Visualization
- Bar chart: r values for pylint, mypy, radon with r=0.35 threshold line
- Scatter plots: SA metric vs passed (jittered) with regression line
- Correlation matrix heatmap
- Save to `figures/`

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Sample size N ≥ 500 for adequate power
- Report 95% confidence intervals for correlations
- Use two-tailed tests with α = 0.05

### NFR-2: Performance
- SA extraction: <1 hour for 591 samples (reuse H-E1 pipeline)
- Correlation computation: <1 minute

### NFR-3: Reproducibility
- Pin scipy, pingouin versions
- Fixed random seed where applicable
- Document LLM source for samples

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Sample count | ≥ 500 | len(df) after processing |
| Max partial r | ≥ 0.35 | max(\|r_pylint\|, \|r_mypy\|, \|r_radon\|) |
| P-value | < 0.05 | p for the max r metric |
| **Pass condition** | **r ≥ 0.35 AND p < 0.05** | At least one SA metric |

---

## Dependencies

- Python ≥3.9
- scipy ≥1.10
- pingouin ≥0.5
- pandas ≥2.0
- matplotlib ≥3.7
- pylint, mypy, radon (from H-E1)
- datasets (HuggingFace)
- human-eval package

---

## Out of Scope

- Model training or fine-tuning
- Multiple LLM comparison
- Causality analysis (correlation only)
- SA metric optimization
