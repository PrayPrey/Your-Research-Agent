# Product Requirements Document: H-M2

**Hypothesis:** Execution-detailed feedback yields higher pass@1 than execution-binary (pass/fail only) because detailed error traces enable targeted code edits rather than global rewrites.
**Type:** MECHANISM
**Date:** 2026-08-28
**Author:** PrayPrey

---

## Executive Summary

This experiment tests the causal mechanism between feedback granularity and edit behavior in code refinement. By comparing execution-detailed (full error traces) vs execution-binary (pass/fail only) feedback, we measure whether detailed localization enables more targeted edits.

**Key Metric:** edit_scope_ratio = lines_changed(detailed) / lines_changed(binary) < 0.9

---

## Problem Statement

Code LLMs can refine failed code, but the relationship between feedback granularity and edit scope is uncharacterized. H-E1 validated that execution feedback works; H-M2 tests WHY by isolating the localization component.

**Research Question:** Does detailed error trace information cause more targeted code edits compared to binary pass/fail feedback?

---

## Functional Requirements

### FR-01: Feedback Formatting System

**Description:** Format execution results into two granularity levels.

**Detailed Feedback Format:**
```
Error: {error_type} at line {line_number}
Message: {error_message}
Expected: {expected}
Actual: {actual}
Traceback: {last_3_lines}
```

**Binary Feedback Format:**
```
Test passed.
```
or
```
Test failed.
```

**Acceptance:** Both formatters produce valid prompts.

---

### FR-02: Edit Scope Measurement

**Description:** Measure edit scope per refinement iteration.

**Metrics:**
- `lines_changed`: Count of added/removed lines (difflib)
- `change_ratio`: lines_changed / total_lines
- `is_global_rewrite`: change_ratio > 0.5

**Implementation:** Python difflib.unified_diff

**Acceptance:** Metrics computed for every refinement iteration.

---

### FR-03: Refinement Loop with Condition Assignment

**Description:** Run refinement loop for both feedback conditions.

**Parameters:**
- max_iterations: 3
- feedback_type: "detailed" | "binary"
- temperature: 0.2
- max_tokens: 512

**Acceptance:** Each problem run twice (once per condition).

---

### FR-04: Dataset Integration

**Description:** Load and process standard benchmarks.

**Datasets:**
- HumanEval: 164 problems (full test set)
- MBPP: 500 problems (standard test split)

**Loading:**
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp", split="test")
```

**Acceptance:** All problems accessible and formatted.

---

### FR-05: Model Loading (Reused from H-E1)

**Description:** Load CodeLlama-7B-Instruct.

**Source:** `codellama/CodeLlama-7b-Instruct-hf`

**Acceptance:** Model generates valid completions.

---

### FR-06: Execution Sandbox (Reused from H-E1)

**Description:** Execute generated code safely.

**Constraints:**
- Timeout: 10 seconds
- Memory: 512MB

**Acceptance:** Code executes without host system impact.

---

### FR-07: Results Aggregation

**Description:** Compute aggregate metrics by feedback type.

**Outputs:**
- detailed_avg_lines_changed
- binary_avg_lines_changed
- detailed_global_rewrite_rate
- binary_global_rewrite_rate
- edit_scope_ratio

**Acceptance:** All metrics computed and logged.

---

### FR-08: Visualization

**Description:** Generate experiment figures.

**Required Figures:**
1. Edit scope comparison (box plot by feedback type)
2. Change ratio distribution (histogram)
3. Global rewrite rate (bar chart)

**Output:** `h-m2/figures/`

**Acceptance:** Figures generated and saved.

---

## Non-Functional Requirements

### NFR-01: Reproducibility
- Fixed seed: 42
- Deterministic execution order

### NFR-02: Performance
- Full experiment completes in <24 hours on single GPU
- Progress logging every 50 problems

### NFR-03: Logging
- All edit metrics saved to JSONL
- Per-problem results stored

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Active | edit_scope_ratio < 0.9 | Detailed edits 10%+ smaller |
| Statistical Significance | p < 0.05 | t-test on lines_changed |
| Code Runs | No runtime errors | Full dataset completion |

---

## Dependencies

### From H-E1 (Reused)
- Execution sandbox
- Model loading utilities
- Dataset handling
- Prompt templates

### New Components
- Binary feedback formatter
- Edit scope metrics
- Visualization pipeline

---

## Out of Scope

- Training/fine-tuning (inference only)
- Alternative models (CodeLlama-7B only)
- Alternative datasets (HumanEval/MBPP only)
- AST-based edit distance (optional extension)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No difference in edit scope | Mechanism not supported | Document null result |
| Binary feedback causes generation failure | Invalid comparison | Ensure both conditions produce valid code |
| H-E1 code incompatible | Delays | Standalone implementation fallback |

---

*Source: h-m2/02c_experiment_brief.md*
*Next: 03_architecture.md*
