# Product Requirements Document: H-M1

**Hypothesis:** Granularity Effect on LLM Code Repair Success
**Date:** 2026-03-30
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: determining whether error feedback granularity (G0-G4) has a statistically significant effect on LLM repair success rate. This is a **MECHANISM** hypothesis that tests the core research question using one-way ANOVA analysis across 5 granularity levels.

**Success Metric:** ANOVA p < 0.05 (significant effect of granularity on repair success)

**Prerequisite:** H-E1 PASSED (Runtime error prevalence 60.8% - 304 runtime error cases available)

---

## Problem Statement

### Background
Self-debugging approaches for LLM code repair use execution feedback to guide error correction. The granularity of this feedback (from simple pass/fail to full stack traces) may significantly impact repair success. While prior work (Self-Debug, TraceFixer) uses various feedback levels, no systematic study has quantified the effect of granularity on repair outcomes.

### Goal
Determine whether error feedback granularity has a statistically significant effect on LLM repair success rate through controlled experiments comparing 5 granularity levels (G0-G4).

### Scope
- **In Scope:** Granularity-controlled repair prompts, repair execution, ANOVA analysis, pairwise comparisons
- **Out of Scope:** Multi-turn repair, model fine-tuning, alternative repair methods

---

## Functional Requirements

### FR-1: Load H-E1 Runtime Error Cases
**Priority:** P0 (Critical)

Load the 304 runtime error cases identified in H-E1 for granularity comparison.

**Acceptance Criteria:**
- Load from H-E1 execution results: `h-e1/results/execution_results.json`
- Filter to RUNTIME_ERROR category only
- Extract: task_id, generated_code, error_info (type, message, line, traceback)
- Verify 304 cases available (or actual count from H-E1)

**Implementation Notes:**
```python
import json

def load_runtime_errors(h_e1_results_path: str) -> list[dict]:
    with open(h_e1_results_path) as f:
        results = json.load(f)

    runtime_errors = [
        r for r in results
        if r["category"] == "runtime_error"
    ]
    return runtime_errors
```

### FR-2: Load MBPP Dataset
**Priority:** P0 (Critical)

Load MBPP dataset to retrieve original task descriptions and test cases.

**Acceptance Criteria:**
- Load via HuggingFace: `google-research-datasets/mbpp`
- Match task_ids from runtime error cases
- Provide task text and test_list for repair prompt construction

**Implementation Notes:**
```python
from datasets import load_dataset

dataset = load_dataset("google-research-datasets/mbpp", "full")
test_set = {item["task_id"]: item for item in dataset["test"]}
```

### FR-3: Load Model
**Priority:** P0 (Critical)

Load CodeLlama-7B-Instruct model (same as H-E1 for controlled comparison).

**Acceptance Criteria:**
- Load from HuggingFace: `codellama/CodeLlama-7b-Instruct-hf`
- Use float16 precision
- Configure for deterministic generation (temperature=0, seed=1)

**Implementation Notes:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)
```

### FR-4: Granularity-Controlled Feedback Formatter
**Priority:** P0 (Critical)

Implement feedback formatting at 5 granularity levels.

**Acceptance Criteria:**
- G0: Pass/fail only ("Test failed.")
- G1: Error type ("Test failed: {error_type}")
- G2: Error message ("Test failed: {error_type}: {message}")
- G3: Error + line ("Test failed: {error_type}: {message} at line {line}")
- G4: Full trace (Complete traceback)

**Implementation Notes:**
```python
GRANULARITY_LEVELS = ["G0", "G1", "G2", "G3", "G4"]

def format_feedback(error_info: dict, level: str) -> str:
    """Format error feedback at specified granularity level."""
    if level == "G0":
        return "Test failed."
    elif level == "G1":
        return f"Test failed: {error_info['type']}"
    elif level == "G2":
        return f"Test failed: {error_info['type']}: {error_info['message']}"
    elif level == "G3":
        msg = f"Test failed: {error_info['type']}: {error_info['message']}"
        if error_info.get('line'):
            msg += f" at line {error_info['line']}"
        return msg
    elif level == "G4":
        return f"Test failed:\n{error_info['traceback']}"
    else:
        raise ValueError(f"Unknown granularity level: {level}")
```

### FR-5: Self-Debug Style Repair Prompt
**Priority:** P0 (Critical)

Construct repair prompts following Self-Debug methodology with controlled granularity.

**Acceptance Criteria:**
- Include original buggy code
- Include task description for context
- Include granularity-controlled feedback
- Request corrected code

**Implementation Notes:**
```python
def construct_repair_prompt(
    code: str,
    task_text: str,
    error_info: dict,
    granularity: str
) -> str:
    feedback = format_feedback(error_info, granularity)

    prompt = f"""The following code was written to solve this task:
Task: {task_text}

```python
{code}
```

Execution feedback:
{feedback}

Please fix the bug and provide the corrected code. Only output the corrected Python code, nothing else.

```python
"""
    return prompt
```

### FR-6: Repair Execution Pipeline
**Priority:** P0 (Critical)

Execute repair attempts for all cases across all granularity levels.

**Acceptance Criteria:**
- Process all 304 runtime error cases
- Generate repair for each case at each granularity level (G0-G4)
- Total: 304 × 5 = 1,520 repair attempts
- Single repair attempt per case per granularity (no multi-turn)

**Implementation Notes:**
```python
def run_repair_experiment(
    runtime_errors: list[dict],
    model,
    tokenizer,
    mbpp_data: dict
) -> dict[str, list[int]]:
    results = {g: [] for g in GRANULARITY_LEVELS}

    for case in runtime_errors:
        task_id = case["task_id"]
        task_info = mbpp_data[task_id]

        for granularity in GRANULARITY_LEVELS:
            prompt = construct_repair_prompt(
                case["generated_code"],
                task_info["text"],
                case["error_info"],
                granularity
            )

            repaired_code = generate_repair(model, tokenizer, prompt)
            success = execute_and_verify(repaired_code, task_info["test_list"])
            results[granularity].append(1 if success else 0)

    return results
```

### FR-7: Code Execution and Verification
**Priority:** P0 (Critical)

Execute repaired code and verify against test cases.

**Acceptance Criteria:**
- Execute via subprocess with 10-second timeout
- Run all test assertions from MBPP
- Binary success: All tests pass = 1, any failure = 0

**Implementation Notes:**
```python
import subprocess

def execute_and_verify(code: str, test_list: list[str], timeout: int = 10) -> bool:
    """Execute code with tests and return success status."""
    full_code = code + "\n" + "\n".join(test_list)
    try:
        result = subprocess.run(
            ["python", "-c", full_code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
```

### FR-8: ANOVA Statistical Analysis
**Priority:** P0 (Critical)

Perform one-way ANOVA to test hypothesis.

**Acceptance Criteria:**
- One-way ANOVA comparing 5 groups (G0, G1, G2, G3, G4)
- Calculate F-statistic and p-value
- Calculate effect size (eta-squared: η²)
- Gate condition: p < 0.05

**Implementation Notes:**
```python
from scipy.stats import f_oneway
import numpy as np

def run_anova_analysis(results: dict[str, list[int]]) -> dict:
    """Run one-way ANOVA on granularity results."""
    groups = [results[g] for g in GRANULARITY_LEVELS]

    # One-way ANOVA
    f_stat, p_value = f_oneway(*groups)

    # Effect size (eta-squared)
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    ss_total = np.sum((all_data - grand_mean) ** 2)
    ss_between = sum(
        len(g) * (np.mean(g) - grand_mean) ** 2
        for g in groups
    )
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    return {
        "f_statistic": f_stat,
        "p_value": p_value,
        "eta_squared": eta_squared,
        "gate_passed": p_value < 0.05
    }
```

### FR-9: Post-hoc Pairwise Comparisons
**Priority:** P1 (High)

If ANOVA significant, perform Tukey's HSD for pairwise comparisons.

**Acceptance Criteria:**
- Execute only if ANOVA p < 0.05
- Compare all pairs of granularity levels
- Report significant differences with adjusted p-values

**Implementation Notes:**
```python
from scipy.stats import tukey_hsd

def run_posthoc_analysis(results: dict[str, list[int]]) -> dict:
    """Run Tukey's HSD post-hoc analysis."""
    groups = [np.array(results[g]) for g in GRANULARITY_LEVELS]

    tukey_result = tukey_hsd(*groups)

    pairwise = {}
    for i, g1 in enumerate(GRANULARITY_LEVELS):
        for j, g2 in enumerate(GRANULARITY_LEVELS):
            if i < j:
                pairwise[f"{g1}_vs_{g2}"] = {
                    "statistic": tukey_result.statistic[i, j],
                    "p_value": tukey_result.pvalue[i, j],
                    "significant": tukey_result.pvalue[i, j] < 0.05
                }
    return pairwise
```

### FR-10: Results Persistence
**Priority:** P1 (High)

Save all experimental results for reproducibility.

**Acceptance Criteria:**
- Save per-case, per-granularity results to JSON
- Save aggregate metrics and ANOVA results to YAML
- Save post-hoc analysis if applicable

**Output Files:**
- `h-m1/results/repair_results.json` - Per-case results
- `h-m1/results/metrics.yaml` - Aggregate metrics and ANOVA
- `h-m1/results/posthoc.yaml` - Tukey HSD results (if applicable)
- `h-m1/figures/` - Visualization outputs

### FR-11: Visualization
**Priority:** P1 (High)

Generate visualizations for results analysis.

**Required Figures:**
1. **Repair Success Rate by Granularity** - Bar chart with 95% CI error bars
2. **Granularity Effect Curve** - Line plot showing repair rate vs granularity level
3. **ANOVA Results Summary** - F-statistic, p-value, η² visualization
4. **Gate Metrics Comparison** - ANOVA p-value vs 0.05 threshold
5. **Pairwise Comparison Heatmap** - Tukey HSD p-values (if ANOVA significant)
6. **Per-Error-Type Breakdown** - Stratified analysis by error type

**Output Directory:** `h-m1/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Repair generation: ≤30 seconds per attempt
- Total runtime: ≤24 hours for 1,520 attempts (with batching)
- Execution timeout: 10 seconds per verification

### NFR-2: Reproducibility
- Fixed random seed: 1
- Deterministic generation: temperature=0
- Same model and configuration as H-E1
- All results saved with timestamps

### NFR-3: Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- Memory: ≤24GB GPU RAM (float16 inference)
- Storage: ≤2GB for results and figures

### NFR-4: Error Handling
- Graceful handling of generation failures
- Checkpoint/resume capability for long experiments
- Comprehensive logging for debugging

---

## Success Criteria

### Gate Condition (MUST_WORK)
| Metric | Target | Measurement |
|--------|--------|-------------|
| ANOVA p-value | < 0.05 | scipy.stats.f_oneway |
| Effect Size (η²) | > 0.02 | SS_between / SS_total |
| Sample Size | 304 per group | H-E1 runtime errors |

### Secondary Metrics
| Metric | Expected Range | Notes |
|--------|----------------|-------|
| G0 Repair Rate | 5-10% | Naive retry baseline |
| G2-G3 Repair Rate | 15-25% | Self-Debug expected |
| G4 Repair Rate | 15-20% | Potential cognitive overload |

### Gate Decision
- **PASS:** ANOVA p < 0.05 → Granularity has significant effect, proceed to H-M2/H-M3
- **FAIL:** ANOVA p ≥ 0.05 → Supports H0 (no effect), ABANDON hypothesis chain

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | ≥4.35.0 | Model loading |
| datasets | ≥2.14.0 | MBPP dataset |
| torch | ≥2.0.0 | GPU inference |
| scipy | ≥1.10.0 | ANOVA, Tukey HSD |
| numpy | ≥1.24.0 | Numerical operations |
| matplotlib | ≥3.7.0 | Visualization |
| seaborn | ≥0.12.0 | Statistical plots |

### Internal Dependencies
| Dependency | Status | Notes |
|------------|--------|-------|
| H-E1 Validation | COMPLETED | 304 runtime errors available |
| H-E1 Results | EXISTS | `h-e1/results/execution_results.json` |
| Phase 2C Brief | COMPLETED | `h-m1/02c_experiment_brief.md` |

---

## Data Specifications

### Input Data
| Field | Type | Source | Description |
|-------|------|--------|-------------|
| task_id | int | H-E1 | MBPP problem ID |
| generated_code | str | H-E1 | Original buggy code |
| error_info | dict | H-E1 | {type, message, line, traceback} |
| text | str | MBPP | Task description |
| test_list | list[str] | MBPP | Test assertions |

### Output Data
| Field | Type | Description |
|-------|------|-------------|
| task_id | int | Problem ID |
| granularity | str | G0, G1, G2, G3, or G4 |
| repaired_code | str | LLM repair output |
| success | bool | All tests passed |
| execution_time | float | Seconds |

### Aggregate Metrics
| Field | Type | Description |
|-------|------|-------------|
| success_rate_by_granularity | dict[str, float] | Per-level success rate |
| f_statistic | float | ANOVA F-value |
| p_value | float | ANOVA p-value |
| eta_squared | float | Effect size |
| gate_passed | bool | p < 0.05 |

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| No significant effect (H0 true) | HIGH | This is a valid scientific outcome; document and report |
| Insufficient sample size | MEDIUM | Using all 304 H-E1 runtime errors |
| Long experiment runtime | MEDIUM | Checkpoint/resume, batch processing |
| Model variance | LOW | Fixed seed, temperature=0 |
| Execution environment differences | LOW | Same setup as H-E1 |

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Granularity Levels (G0-G4) | Core Mechanism Implementation |
| ANOVA Analysis | Statistical Test section |
| Success Rate Metrics | Evaluation section |
| Gate Condition (p < 0.05) | Gate Condition section |
| Post-hoc (Tukey HSD) | Post-hoc Analysis section |
| Runtime Error Cases | Continuation Context (H-E1) |
| Model Configuration | Models section |
| Prompt Template | Core Mechanism Implementation |

---

## Appendix: Granularity Level Examples

### G0 (Pass/Fail Only)
```
Test failed.
```

### G1 (Error Type)
```
Test failed: IndexError
```

### G2 (Error Message)
```
Test failed: IndexError: list index out of range
```

### G3 (Error + Line)
```
Test failed: IndexError: list index out of range at line 7
```

### G4 (Full Trace)
```
Test failed:
Traceback (most recent call last):
  File "<string>", line 12, in <module>
  File "<string>", line 7, in solve
IndexError: list index out of range
```

---

*Generated for Phase 3 Implementation Planning*
*Source: h-m1/02c_experiment_brief.md*
*Prerequisite: H-E1 VALIDATED (60.8% runtime error prevalence)*
*Next: Architecture Design (03_architecture.md)*
