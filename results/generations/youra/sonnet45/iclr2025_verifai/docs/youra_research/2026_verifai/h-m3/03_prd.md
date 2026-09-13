---
stepsCompleted: ['initialization', 'requirements-gathering', 'functional-requirements', 'non-functional-requirements', 'success-criteria', 'validation']
prd_completed: true
validation_status: PASSED
hypothesis_id: h-m3
hypothesis_type: MECHANISM
created_date: 2026-03-18
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document (PRD)
# Hypothesis h-m3: Conditional Execution Gating Token Efficiency

**Date:** 2026-03-18
**Author:** Claude (Implementation Planning Specialist)
**Hypothesis:** Under cascade routing conditions (N=20 from H-E1), if pytest execution is conditionally gated (run only when mypy clean) instead of always running (aggregation), then tokens-per-successful-task remains within 15% of aggregation baseline, because conditional gating skips expensive 5-10 second test execution when static errors exist without excessive verbosity trade-off.
**Phase:** Phase 3 - Implementation Planning
**Gate Type:** SHOULD_WORK

---

## Executive Summary

This PRD defines the implementation requirements for h-m3, a MECHANISM hypothesis that validates the token efficiency of conditional execution gating in cascade routing. The system will implement TWO feedback routers - CASCADE (conditional gating: mypy → if clean → pytest) and AGGREGATION (simultaneous: mypy + pytest always) - and compare tokens-per-successful-task between them.

**Core Objective:** Demonstrate that CASCADE routing achieves token efficiency within ≤15% overhead compared to AGGREGATION baseline (target ratio ≤1.15×).

**Success Criteria:** `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`

**Failure Impact:** SHOULD_WORK gate - failure documented as limitation, workflow continues. Alternative token normalization strategies would be explored.

**Prerequisite Context:** h-m1 COMPLETED with 99.6% mypy detection rate - validates that conditional gating can skip execution in vast majority of cases, justifying efficiency hypothesis.

---

## Problem Statement

### Research Gap
Current cascade routing research validates iteration reduction (h-m2) but lacks token efficiency validation. Without establishing that conditional gating maintains acceptable token overhead, cascade routing loses practical applicability despite iteration advantages.

### Hypothesis Context
- **Type:** MECHANISM (Token efficiency validation)
- **Prerequisites:** h-m1 (COMPLETED ✅ - 99.6% mypy detection rate)
- **Dependency Level:** 2 (depends on h-e1 task pool, h-m1 validation)
- **Blocks:** h-c1 (boundary condition testing)
- **Parallel with:** h-m2 (attention economy - iteration focus vs token focus)

### Expected Outcomes
- **Primary:** Cascade tokens-per-task ≤ 1.15 × Aggregation (≤15% overhead)
- **Secondary:** Gating efficiency (% iterations execution skipped in CASCADE)
- **Exploratory:** Token breakdown (mypy vs pytest contribution both conditions)

---

## Functional Requirements

### FR-1: Qualified Task Loading (from h-e1)
**Priority:** P0 (Critical)

**Requirements:**
- Load N=20 dual-sensitive tasks identified in H-E1 experiment
- Parse task metadata: task_id, prompt, entry_point, canonical_solution, test_cases
- Verify all tasks passed h-e1 qualification criteria

**Implementation Details:**
```python
# Load from h-e1 validation results
h_e1_validation = "{h-e1_folder}/04_validation.md"
dual_sensitive_task_ids = parse_dual_sensitive_tasks(h_e1_validation)  # N=20

# Load HumanEval+ dataset
from evalplus.data import get_human_eval_plus
all_problems = get_human_eval_plus()

# Filter to dual-sensitive subset
qualified_tasks = {
    tid: all_problems[tid]
    for tid in dual_sensitive_task_ids
}

assert len(qualified_tasks) == 20, "Must have exactly N=20 tasks"
```

**Acceptance Criteria:**
- Exactly N=20 tasks loaded (h-e1 output)
- All tasks confirmed dual-sensitive
- Task structure validated (prompt, tests, entry_point present)

---

### FR-2: Baseline Model Configuration (CodeLlama-7B)
**Priority:** P0 (Critical)

**Requirements:**
- Load CodeLlama-7B Base model (NOT instruction-tuned)
- Configure for code generation with controlled sampling
- Initialize tokenizer for token counting

**Model Configuration:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "codellama/CodeLlama-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()

# Generation hyperparameters
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "do_sample": True,
    "pad_token_id": tokenizer.eos_token_id
}

# Reproducibility
torch.manual_seed(42)
```

**Acceptance Criteria:**
- Model loads successfully on single GPU
- Tokenizer available for token counting
- Hyperparameters match Phase 2C specification

---

### FR-3: CASCADE Router Implementation
**Priority:** P0 (Critical)

**Requirements:**
- Implement conditional execution gating logic
- Run mypy --strict FIRST, skip pytest if mypy fails
- Track tokens per iteration separately (mypy vs pytest)

**Core Implementation:**
```python
class CascadeRouter:
    """
    Conditional feedback routing: mypy → (if clean) → pytest
    Tracks token efficiency vs aggregation baseline.
    """
    def __init__(self, model, tokenizer, max_iterations=10):
        self.model = model
        self.tokenizer = tokenizer
        self.max_iterations = max_iterations
        self.token_limit_per_source = 1000  # Enforced equally

    def solve_task(self, task_prompt: str, tests: list) -> dict:
        """
        Args:
            task_prompt: str - HumanEval problem description
            tests: list - Test cases for validation

        Returns:
            dict - {
                code: str,
                iterations: int,
                total_tokens: int,
                mypy_tokens: int,
                pytest_tokens: int,
                gating_skipped_count: int,  # Times pytest skipped
                success: bool
            }
        """
        iteration = 0
        total_tokens = 0
        mypy_tokens = 0
        pytest_tokens = 0
        gating_skipped = 0
        prompt = task_prompt

        while iteration < self.max_iterations:
            # Generate code
            code = self.model.generate(prompt, **self.generation_config)

            # Step 1: Run mypy --strict (ALWAYS)
            mypy_result = run_mypy_strict(code)
            mypy_feedback = format_mypy_output(mypy_result)
            mypy_tokens_iter = self.count_tokens(mypy_feedback)
            mypy_tokens += mypy_tokens_iter
            total_tokens += mypy_tokens_iter

            # Step 2: Conditional execution gating
            if mypy_result.success:  # Gate OPEN
                # Run pytest (only when mypy clean)
                pytest_result = run_pytest(code, tests)
                pytest_feedback = format_pytest_output(pytest_result)
                pytest_tokens_iter = self.count_tokens(pytest_feedback)
                pytest_tokens += pytest_tokens_iter
                total_tokens += pytest_tokens_iter

                if pytest_result.success:
                    # SUCCESS - both passed
                    return {
                        "code": code,
                        "iterations": iteration + 1,
                        "total_tokens": total_tokens,
                        "mypy_tokens": mypy_tokens,
                        "pytest_tokens": pytest_tokens,
                        "gating_skipped_count": gating_skipped,
                        "success": True
                    }
                else:
                    # Pytest failed - give pytest feedback
                    prompt = prompt + "\n\nTests failed:\n" + pytest_feedback
            else:
                # Gate CLOSED - skip pytest, increment gating counter
                gating_skipped += 1
                # Give only mypy feedback
                prompt = prompt + "\n\nMypy errors:\n" + mypy_feedback

            iteration += 1

        # Max iterations reached without success
        return {
            "code": code,
            "iterations": self.max_iterations,
            "total_tokens": total_tokens,
            "mypy_tokens": mypy_tokens,
            "pytest_tokens": pytest_tokens,
            "gating_skipped_count": gating_skipped,
            "success": False
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens using tokenizer"""
        return len(self.tokenizer.encode(text))
```

**Acceptance Criteria:**
- Conditional gating logic correct (skip pytest when mypy fails)
- Token counting accurate (mypy, pytest, total tracked separately)
- Gating efficiency metric tracked (skipped execution count)

---

### FR-4: AGGREGATION Router Implementation (Baseline)
**Priority:** P0 (Critical)

**Requirements:**
- Implement simultaneous multi-source feedback
- Run BOTH mypy + pytest every iteration (no gating)
- Concatenate feedback, track total tokens

**Core Implementation:**
```python
class AggregationRouter:
    """
    Baseline: Simultaneous multi-source aggregation.
    Both mypy + pytest every iteration, concatenated feedback.
    """
    def __init__(self, model, tokenizer, max_iterations=10):
        self.model = model
        self.tokenizer = tokenizer
        self.max_iterations = max_iterations
        self.token_limit_per_source = 1000  # Enforced equally

    def solve_task(self, task_prompt: str, tests: list) -> dict:
        """
        Args:
            task_prompt: str - HumanEval problem description
            tests: list - Test cases for validation

        Returns:
            dict - {
                code: str,
                iterations: int,
                total_tokens: int,
                mypy_tokens: int,
                pytest_tokens: int,
                success: bool
            }
        """
        iteration = 0
        total_tokens = 0
        mypy_tokens = 0
        pytest_tokens = 0
        prompt = task_prompt

        while iteration < self.max_iterations:
            # Generate code
            code = self.model.generate(prompt, **self.generation_config)

            # Run BOTH sources every iteration
            mypy_result = run_mypy_strict(code)
            pytest_result = run_pytest(code, tests)

            # Format and count tokens separately
            mypy_feedback = format_mypy_output(mypy_result)
            pytest_feedback = format_pytest_output(pytest_result)

            mypy_tokens_iter = self.count_tokens(mypy_feedback)
            pytest_tokens_iter = self.count_tokens(pytest_feedback)

            mypy_tokens += mypy_tokens_iter
            pytest_tokens += pytest_tokens_iter
            total_tokens += (mypy_tokens_iter + pytest_tokens_iter)

            # Check success (both must pass)
            if mypy_result.success and pytest_result.success:
                return {
                    "code": code,
                    "iterations": iteration + 1,
                    "total_tokens": total_tokens,
                    "mypy_tokens": mypy_tokens,
                    "pytest_tokens": pytest_tokens,
                    "success": True
                }

            # Concatenate feedback for next iteration
            combined_feedback = mypy_feedback + "\n\n" + pytest_feedback
            prompt = prompt + "\n\nFeedback:\n" + combined_feedback
            iteration += 1

        # Max iterations reached without success
        return {
            "code": code,
            "iterations": self.max_iterations,
            "total_tokens": total_tokens,
            "mypy_tokens": mypy_tokens,
            "pytest_tokens": pytest_tokens,
            "success": False
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens using tokenizer"""
        return len(self.tokenizer.encode(text))
```

**Acceptance Criteria:**
- Both sources run every iteration (no conditional logic)
- Token counting matches CASCADE methodology
- Feedback concatenation correct

---

### FR-5: Tokens-Per-Successful-Task Metric
**Priority:** P0 (Critical)

**Requirements:**
- Compute primary metric: tokens-per-successful-task
- Calculate separately for CASCADE and AGGREGATION
- Only count tasks that eventually succeeded (passed all tests)

**Metric Implementation:**
```python
def compute_tokens_per_task(results: list) -> dict:
    """
    Args:
        results: list of task result dicts from router

    Returns:
        dict - {
            tokens_per_task: float,
            successful_tasks: int,
            total_tokens: int,
            mean_iterations: float
        }
    """
    # Filter to successful tasks only
    successful = [r for r in results if r["success"]]

    if len(successful) == 0:
        return {
            "tokens_per_task": float('inf'),
            "successful_tasks": 0,
            "total_tokens": 0,
            "mean_iterations": 0
        }

    total_tokens = sum(r["total_tokens"] for r in successful)
    tokens_per_task = total_tokens / len(successful)
    mean_iterations = sum(r["iterations"] for r in successful) / len(successful)

    return {
        "tokens_per_task": tokens_per_task,
        "successful_tasks": len(successful),
        "total_tokens": total_tokens,
        "mean_iterations": mean_iterations
    }

# Gate validation
cascade_metrics = compute_tokens_per_task(cascade_results)
aggregation_metrics = compute_tokens_per_task(aggregation_results)

efficiency_ratio = cascade_metrics["tokens_per_task"] / aggregation_metrics["tokens_per_task"]
gate_passed = efficiency_ratio <= 1.15  # ≤15% overhead threshold
```

**Acceptance Criteria:**
- Only successful tasks counted (passed all tests)
- Separate metrics for CASCADE and AGGREGATION
- Gate ratio computed correctly (≤1.15 threshold)

---

### FR-6: Secondary Metrics (Analysis)
**Priority:** P1 (High)

**Requirements:**
- Gating Efficiency: % iterations execution skipped (CASCADE only)
- Token Breakdown: mypy vs pytest contribution (both conditions)
- Success Rate: % tasks solved (both conditions)

**Metric Implementation:**
```python
def compute_secondary_metrics(cascade_results: list, aggregation_results: list) -> dict:
    """
    Compute exploratory metrics for analysis.
    """
    # CASCADE-specific: Gating efficiency
    cascade_gating_skipped = sum(r["gating_skipped_count"] for r in cascade_results)
    cascade_total_iterations = sum(r["iterations"] for r in cascade_results)
    gating_efficiency = (cascade_gating_skipped / cascade_total_iterations) * 100

    # Token breakdown (both conditions)
    cascade_mypy_tokens = sum(r["mypy_tokens"] for r in cascade_results)
    cascade_pytest_tokens = sum(r["pytest_tokens"] for r in cascade_results)

    aggregation_mypy_tokens = sum(r["mypy_tokens"] for r in aggregation_results)
    aggregation_pytest_tokens = sum(r["pytest_tokens"] for r in aggregation_results)

    # Success rates
    cascade_success_rate = sum(1 for r in cascade_results if r["success"]) / len(cascade_results)
    aggregation_success_rate = sum(1 for r in aggregation_results if r["success"]) / len(aggregation_results)

    return {
        "gating_efficiency_pct": gating_efficiency,
        "cascade_token_breakdown": {
            "mypy": cascade_mypy_tokens,
            "pytest": cascade_pytest_tokens
        },
        "aggregation_token_breakdown": {
            "mypy": aggregation_mypy_tokens,
            "pytest": aggregation_pytest_tokens
        },
        "success_rates": {
            "cascade": cascade_success_rate,
            "aggregation": aggregation_success_rate
        }
    }
```

**Acceptance Criteria:**
- Gating efficiency computed correctly
- Token breakdown available for both conditions
- Success rates tracked

---

### FR-7: Controlled Experiment Execution
**Priority:** P0 (Critical)

**Requirements:**
- Run both conditions (CASCADE, AGGREGATION) on same N=20 tasks
- Use same model, same random seed, same hyperparameters
- Within-task paired comparison design

**Execution Protocol:**
```python
# Set random seed for reproducibility
import random
import numpy as np
torch.manual_seed(42)
random.seed(42)
np.random.seed(42)

# Initialize routers
cascade_router = CascadeRouter(model, tokenizer, max_iterations=10)
aggregation_router = AggregationRouter(model, tokenizer, max_iterations=10)

# Load tasks
qualified_tasks = load_qualified_tasks()  # N=20

# Run both conditions
cascade_results = []
aggregation_results = []

for task_id, task in qualified_tasks.items():
    print(f"Processing {task_id}...")

    # Condition 1: CASCADE
    cascade_result = cascade_router.solve_task(
        task_prompt=task["prompt"],
        tests=task["tests"]
    )
    cascade_result["task_id"] = task_id
    cascade_results.append(cascade_result)

    # Condition 2: AGGREGATION
    aggregation_result = aggregation_router.solve_task(
        task_prompt=task["prompt"],
        tests=task["tests"]
    )
    aggregation_result["task_id"] = task_id
    aggregation_results.append(aggregation_result)

# Compute metrics and gate validation
primary_metrics = {
    "cascade": compute_tokens_per_task(cascade_results),
    "aggregation": compute_tokens_per_task(aggregation_results)
}

efficiency_ratio = (
    primary_metrics["cascade"]["tokens_per_task"] /
    primary_metrics["aggregation"]["tokens_per_task"]
)

gate_validation = {
    "ratio": efficiency_ratio,
    "threshold": 1.15,
    "passed": efficiency_ratio <= 1.15
}
```

**Acceptance Criteria:**
- Both conditions run on same tasks
- Same model/hyperparameters/seed used
- Paired comparison data available

---

## Non-Functional Requirements

### NFR-1: Execution Time
**Priority:** P1 (High)

**Requirements:**
- Total experiment runtime < 2 hours on single GPU
- Per-task timeout: 10 minutes max

**Rationale:** N=20 tasks × 2 conditions × ~3 min/task = ~2 hours

---

### NFR-2: Reproducibility
**Priority:** P0 (Critical)

**Requirements:**
- Fixed random seed (42)
- Deterministic mypy/pytest execution
- Version pinning (transformers, torch, evalplus, mypy, pytest)

**Implementation:**
```python
# requirements.txt
transformers==4.36.0
torch==2.1.0
evalplus==0.2.0
mypy==1.7.0
pytest==7.4.3
```

---

### NFR-3: Resource Constraints
**Priority:** P0 (Critical)

**Requirements:**
- Single GPU execution (CUDA_VISIBLE_DEVICES set)
- Memory: <16GB GPU RAM (float16 model)
- Storage: <5GB (model + dataset)

---

### NFR-4: Logging and Observability
**Priority:** P1 (High)

**Requirements:**
- Log token counts per iteration
- Log gating decisions (CASCADE only)
- Save intermediate results (checkpoint every 5 tasks)

---

## Success Criteria

### Primary Success Criteria (Gate Validation)

**Gate Type:** SHOULD_WORK
**Threshold:** `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`

**Pass Criteria:**
1. Both routers execute successfully on N=20 tasks
2. ≥10 tasks solved successfully per condition (50% success rate minimum)
3. Efficiency ratio ≤ 1.15 (≤15% overhead)

**Failure Action:**
- Document as limitation in validation report
- Write Serena memory with findings
- Continue to h-c1 (boundary conditions) regardless

---

### Secondary Success Criteria

1. **Gating Efficiency:** CASCADE skips execution in ≥60% of iterations (expected from h-m1 99.6% mypy rate)
2. **Token Breakdown:** CASCADE mypy tokens < AGGREGATION mypy tokens (due to skipping)
3. **Success Parity:** CASCADE and AGGREGATION solve similar number of tasks (routing shouldn't harm correctness)

---

## Dependencies and Risks

### Dependencies
- **h-e1:** N=20 dual-sensitive task IDs (COMPLETED ✅)
- **h-m1:** Mypy detection validation (COMPLETED ✅ - 99.6% rate)

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Efficiency ratio > 1.15 (gate fail) | Medium | Low (SHOULD_WORK gate) | Document limitation, explore token normalization |
| Success rate < 50% both conditions | Low | High | Increase max_iterations or adjust hyperparameters |
| GPU OOM on CodeLlama-7B | Low | Medium | Use float16, single GPU, batch_size=1 |
| Token counting inconsistency | Low | High | Unit test tokenizer, validate against manual counts |

---

## Validation Checklist

Before Phase 4 implementation:
- [ ] N=20 dual-sensitive tasks loaded from h-e1
- [ ] CodeLlama-7B model configuration verified
- [ ] CASCADE router logic reviewed (conditional gating correct)
- [ ] AGGREGATION router logic reviewed (simultaneous execution)
- [ ] Token counting methodology validated
- [ ] Gate threshold confirmed (≤1.15 ratio)
- [ ] Random seed set for reproducibility
- [ ] Logging infrastructure planned

---

## Appendix: Prerequisite Context (h-m1)

**h-m1 Key Findings:**
- Mypy detection rate: 99.6% (697/700 iterations)
- Far exceeds 30% gate threshold
- Validates cascade gating justification: skip execution when mypy fails

**Impact on h-m3:**
- High mypy detection → CASCADE skips execution frequently
- Expected: CASCADE total tokens lower than AGGREGATION due to skipping
- But: CASCADE might have longer mypy feedback → slight overhead
- Net effect should be ≤15% overhead (hypothesis claim)

---

*Generated: 2026-03-18*
*Pipeline Phase: Phase 3 - Implementation Planning*
*Next: 03_architecture.md (Epic task breakdown)*
