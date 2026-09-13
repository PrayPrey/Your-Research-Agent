# Product Requirements Document: H-E1

**Hypothesis:** Runtime Error Prevalence in LLM-Generated Code
**Date:** 2026-03-30
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: measuring the prevalence of runtime errors with localizable stack traces in LLM-generated code on the MBPP benchmark. This is a **FOUNDATION** hypothesis that must pass (≥30% runtime error prevalence) before proceeding with granularity comparison experiments (H-M1, H-M2, H-M3).

**Success Metric:** Runtime error prevalence ≥ 30% (lower bound of 95% Wilson CI)

---

## Problem Statement

### Background
Self-debugging approaches for LLM code repair rely on execution feedback containing stack traces to localize errors. However, the prevalence of runtime errors (vs. wrong-output errors) in LLM-generated code has not been systematically measured. If runtime errors are rare (<30%), the entire granularity study loses scope.

### Goal
Measure the proportion of LLM code failures that are runtime errors with localizable stack traces on the MBPP benchmark using CodeLlama-7B-Instruct.

### Scope
- **In Scope:** Code generation, execution, error categorization, prevalence calculation
- **Out of Scope:** Error repair, granularity comparison (future hypotheses)

---

## Functional Requirements

### FR-1: Dataset Loading
**Priority:** P0 (Critical)

Load MBPP test dataset (500 problems, task IDs 11-510).

**Acceptance Criteria:**
- Load via HuggingFace Datasets API: `load_dataset("mbpp")`
- Extract test split with 500 problems
- Each problem contains: task_id, text (prompt), code (reference), test_list (assertions)

**Implementation Notes:**
```python
from datasets import load_dataset
dataset = load_dataset("mbpp")
test_data = [p for p in dataset["test"] if 11 <= p["task_id"] <= 510]
assert len(test_data) == 500
```

### FR-2: Model Loading
**Priority:** P0 (Critical)

Load CodeLlama-7B-Instruct model for code generation.

**Acceptance Criteria:**
- Load from HuggingFace: `codellama/CodeLlama-7b-Instruct-hf`
- Use float16 precision for memory efficiency
- Configure for deterministic generation (temperature=0)

**Implementation Notes:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "codellama/CodeLlama-7b-Instruct-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
```

### FR-3: Code Generation
**Priority:** P0 (Critical)

Generate code solutions for all 500 MBPP test problems.

**Acceptance Criteria:**
- Use MBPP standard prompt format
- Generate with temperature=0 (deterministic)
- Max new tokens: 512
- Extract code between [BEGIN] and [DONE] markers (or full response if markers absent)

**Prompt Template:**
```
You are an expert Python programmer, and here is your task: {text}
Your code should pass these tests:

{test_list}

[BEGIN]
```

### FR-4: Code Execution
**Priority:** P0 (Critical)

Execute generated code against test cases with safe sandboxing.

**Acceptance Criteria:**
- Execute via subprocess with 10-second timeout
- Capture stdout/stderr for analysis
- Return exit code for pass/fail determination

**Implementation Notes:**
```python
import subprocess

def execute_code(code: str, tests: str, timeout: int = 10):
    full_code = code + "\n" + tests
    result = subprocess.run(
        ["python", "-c", full_code],
        capture_output=True, text=True, timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr
```

### FR-5: Error Categorization
**Priority:** P0 (Critical)

Categorize execution results into error types.

**Acceptance Criteria:**
- Categories: PASS, RUNTIME_ERROR, WRONG_OUTPUT, SYNTAX_ERROR, TIMEOUT
- RUNTIME_ERROR: stderr contains "Traceback (most recent call last):"
- SYNTAX_ERROR: stderr contains "SyntaxError"
- WRONG_OUTPUT: Assertion failed without traceback
- TIMEOUT: Execution exceeded 10 seconds

**Error Category Enum:**
```python
from enum import Enum

class ErrorCategory(Enum):
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"
    WRONG_OUTPUT = "wrong_output"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
```

### FR-6: Prevalence Calculation
**Priority:** P0 (Critical)

Calculate runtime error prevalence with confidence interval.

**Acceptance Criteria:**
- Prevalence = runtime_errors / total_failures
- Use Wilson confidence interval (95%)
- Gate passes if CI lower bound ≥ 0.30

**Implementation Notes:**
```python
from scipy.stats import proportion_confint

def calculate_prevalence(runtime_errors: int, total_failures: int):
    if total_failures == 0:
        return 0.0, 0.0, 0.0
    prevalence = runtime_errors / total_failures
    ci_lower, ci_upper = proportion_confint(
        runtime_errors, total_failures,
        alpha=0.05, method='wilson'
    )
    return prevalence, ci_lower, ci_upper
```

### FR-7: Results Persistence
**Priority:** P1 (High)

Save all results for reproducibility and analysis.

**Acceptance Criteria:**
- Save per-problem results to JSON/CSV
- Include: task_id, generated_code, category, stderr (if error)
- Save aggregate metrics to YAML

**Output Files:**
- `h-e1/results/execution_results.json` - Per-problem results
- `h-e1/results/metrics.yaml` - Aggregate metrics
- `h-e1/figures/` - Visualization outputs

### FR-8: Visualization
**Priority:** P1 (High)

Generate visualizations for results analysis.

**Required Figures:**
1. **Error Distribution Pie Chart** - Breakdown by category
2. **Runtime Error Type Bar Chart** - TypeError, IndexError, KeyError, etc.
3. **Prevalence with CI** - Point estimate with error bars
4. **Gate Metrics Comparison** - Target vs actual

**Output Directory:** `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Code generation: ≤2 minutes per problem (batch processing acceptable)
- Execution: ≤10 seconds per problem (enforced timeout)
- Total runtime: ≤4 hours for 500 problems

### NFR-2: Reproducibility
- Fixed random seed where applicable
- Deterministic generation (temperature=0)
- All results saved with timestamps

### NFR-3: Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- Memory: ≤24GB GPU RAM (float16 inference)
- Storage: ≤1GB for results and figures

### NFR-4: Error Handling
- Graceful handling of model loading failures
- Retry logic for transient execution errors
- Comprehensive logging for debugging

---

## Success Criteria

### Gate Condition (MUST_WORK)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Runtime Error Prevalence | ≥30% | Wilson CI lower bound |
| Sample Size | ≥150 runtime errors | For statistical power |

### Secondary Metrics
| Metric | Expected Range |
|--------|----------------|
| Pass Rate | 40-60% |
| Syntax Error Rate | <5% |
| Timeout Rate | <5% |

### Gate Decision
- **PASS:** CI lower bound ≥ 0.30 → Proceed to H-M1
- **FAIL:** CI lower bound < 0.30 → PIVOT or ABANDON

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | ≥4.35.0 | Model loading |
| datasets | ≥2.14.0 | MBPP dataset |
| torch | ≥2.0.0 | GPU inference |
| scipy | ≥1.10.0 | Statistical calculations |
| matplotlib | ≥3.7.0 | Visualization |

### Internal Dependencies
| Dependency | Status |
|------------|--------|
| Phase 2C Experiment Brief | COMPLETED |
| verification_state.yaml | EXISTS |

---

## Data Specifications

### Input Data
| Field | Type | Description |
|-------|------|-------------|
| task_id | int | MBPP problem ID (11-510) |
| text | str | Task description |
| code | str | Reference solution |
| test_list | list[str] | Test assertions |

### Output Data
| Field | Type | Description |
|-------|------|-------------|
| task_id | int | Problem ID |
| generated_code | str | LLM output |
| category | ErrorCategory | Result category |
| stderr | str | Error output (if applicable) |
| execution_time | float | Seconds |

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Low runtime error prevalence | HIGH | Two-phase design with early gate |
| Model loading OOM | MEDIUM | Use float16, single GPU |
| Execution sandbox escape | LOW | Subprocess isolation, timeout |
| Non-deterministic results | LOW | Fixed seed, temperature=0 |

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Dataset (MBPP) | Dataset section |
| Model (CodeLlama) | Models section |
| Error Categories | Core Mechanism Implementation |
| Success Criteria | Gate Condition |
| Confidence Interval | Evaluation section |

---

*Generated for Phase 3 Implementation Planning*
*Source: h-e1/02c_experiment_brief.md*
*Next: Architecture Design (03_architecture.md)*
