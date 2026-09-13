# PRD: Static Analysis Tool Coverage Validation (H-E1)

**Generated:** 2026-08-24
**Hypothesis:** H-E1 (EXISTENCE)
**Gate:** MUST_WORK

---

## Executive Summary

Validate that pylint, mypy, and radon produce valid numeric outputs on ≥95% of LLM-generated code samples. This is a foundational existence test to confirm static analysis tools work reliably on synthetic code before using them as feedback signals.

---

## Problem Statement

Before integrating static analysis feedback into an LLM code generation pipeline, we must verify the tools themselves operate reliably on LLM-generated code. Tool crashes, timeouts, or null outputs would invalidate downstream metrics.

---

## Functional Requirements

### FR-1: Dataset Preparation
- Load HumanEval (164 samples) from `openai/human-eval`
- Load MBPP test split (500 samples, task_ids 11-510) from HuggingFace
- Extract canonical solutions as standalone Python files
- Validate syntax with `ast.parse`
- Total: 664 samples

### FR-2: Pylint Wrapper
- Version: ≥2.17
- Output: JSON format (`--output-format=json`)
- Metric: Score (0-10 float)
- Timeout: 30 seconds
- Success: Returns numeric score, no crash, no timeout

### FR-3: Mypy Wrapper
- Version: ≥1.0
- Output: JSON format (`--output=json`)
- Metric: Error count (int)
- Timeout: 30 seconds
- Success: Returns numeric count, no crash, no timeout

### FR-4: Radon Wrapper
- Version: ≥6.0
- Command: `radon cc --json`
- Metric: Cyclomatic complexity (int/float average)
- Timeout: 30 seconds
- Success: Returns numeric complexity, no crash, no timeout

### FR-5: Result Aggregation
- Per-tool valid rate: `count(success) / N`
- Overall valid rate: `count(all_three_success) / N`
- Output files:
  - `results/h_e1_coverage.json` (per-sample)
  - `results/h_e1_summary.json` (aggregate)
  - `results/h_e1_failures.json` (error details)

---

## Non-Functional Requirements

### NFR-1: Performance
- Process 664 samples in <1 hour
- 30-second timeout per tool per sample

### NFR-2: Reliability
- Handle malformed code gracefully
- UTF-8 encoding enforcement
- Exception capture for all subprocess calls

### NFR-3: Reproducibility
- Pin tool versions in requirements.txt
- Deterministic sample ordering

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Pylint valid rate | ≥95% | count(success) / 664 |
| Mypy valid rate | ≥95% | count(success) / 664 |
| Radon valid rate | ≥95% | count(success) / 664 |
| **Pass condition** | **All three ≥95%** | `min(rates) ≥ 0.95` |

---

## Dependencies

- Python ≥3.9
- pylint ≥2.17
- mypy ≥1.0
- radon ≥6.0
- datasets (HuggingFace)

---

## Out of Scope

- Model training
- Comparative analysis
- GPU resources
- Baseline comparisons (EXISTENCE test)
