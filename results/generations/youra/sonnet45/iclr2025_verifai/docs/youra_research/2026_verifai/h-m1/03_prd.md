---
stepsCompleted: ['initialization', 'requirements-gathering', 'functional-requirements', 'non-functional-requirements', 'success-criteria', 'validation']
prd_completed: true
validation_status: PASSED
hypothesis_id: h-m1
hypothesis_type: MECHANISM
created_date: 2026-03-18
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document (PRD)
# Hypothesis h-m1: Static Analysis Cascade Routing Mechanism

**Date:** 2026-03-18
**Author:** Claude (Implementation Planning Specialist)
**Hypothesis:** Under dual-sensitive programming task conditions (N=20 from H-E1), if mypy --strict static analysis is applied before execution feedback in cascade routing, then ~30-40% of errors are caught instantly with zero execution cost, because mypy provides compositional type safety guarantees (type errors, null safety, signature mismatches) without requiring test execution.
**Phase:** Phase 3 - Implementation Planning
**Gate Type:** MUST_WORK

---

## Executive Summary

This PRD defines the implementation requirements for h-m1, a MECHANISM hypothesis that validates the foundational assumption for cascade routing: whether static analysis provides sufficient early error detection to justify sequential feedback routing. The system will implement a cascade feedback router that runs mypy --strict FIRST (zero execution cost), then conditionally runs pytest execution tests ONLY if mypy passes.

**Core Objective:** Demonstrate that mypy --strict catches ≥30% of errors before execution testing, validating the cascade routing mechanism's primary value proposition.

**Success Criteria:** Mypy error detection rate ≥30% (target: 30-40%) across N=35 dual-sensitive tasks from h-e1.

**Failure Impact:** MUST_WORK gate - failure indicates static analysis provides minimal value, requiring PIVOT to execution-first routing or abandoning cascade hypothesis entirely.

---

## Problem Statement

### Research Gap
Current LLM code generation research lacks systematic evaluation of static analysis effectiveness in feedback loops. Without establishing that mypy catches a meaningful proportion of errors before expensive test execution, cascade routing loses its primary efficiency justification.

### Hypothesis Context
- **Type:** MECHANISM (Sequential feedback routing validation)
- **Prerequisites:** h-e1 (COMPLETED ✅ - N=35 dual-sensitive tasks validated)
- **Dependency Level:** 1 (depends on h-e1 task pool)
- **Blocks:** h-m2 (sequential presentation), h-m3 (conditional gating efficiency), h-c1 (boundary conditions)

### Expected Outcomes
- **Primary:** Mypy error detection rate = 30-40%
- **Secondary:** Execution cost savings (mypy ~10s vs pytest ~120s timeout)
- **Exploratory:** Error type distribution (type errors, null safety, signature mismatches)

---

## Functional Requirements

### FR-1: Qualified Task Loading (from h-e1)
**Priority:** P0 (Critical)

**Requirements:**
- Load N=35 qualified dual-sensitive tasks from h-e1 validation results
- Parse task metadata: task_id, prompt, entry_point, tests
- Verify all tasks passed h-e1 qualification (dual-sensitive + variance ≤1.0)

**Implementation Details:**
```python
# Load h-e1 validation results
validation_file = "{h-e1_folder}/04_validation.md"
qualified_tasks = parse_qualified_tasks(validation_file)  # N=35

# Alternative: Load from h-e1 checkpoint if available
checkpoint_file = "{h-e1_folder}/04_checkpoint.yaml"
if exists(checkpoint_file):
    tasks = load_checkpoint(checkpoint_file)
    qualified_task_ids = [t for t in tasks if t["qualified"]]
```

**Acceptance Criteria:**
- Exactly N=35 tasks loaded (h-e1 validation output)
- All tasks have dual-sensitivity confirmed
- Task structure validated (prompt, entry_point, test fields present)

---

### FR-2: Baseline Model Configuration (Inherited from h-e1)
**Priority:** P0 (Critical)

**Requirements:**
- Use identical CodeLlama-7B configuration from h-e1 for controlled comparison
- Reuse K=20 samples per task from h-e1 (baseline-controlled sampling)
- Load model with same hyperparameters (temperature=0.8, top-p=0.95, top-k=40, max_tokens=256)

**Model Configuration:**
```python
# Reuse h-e1 configuration
model_id = "codellama/CodeLlama-7b-hf"
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_length": 256,
    "do_sample": True,
    "seed": 42  # Reproducibility
}

# Load from h-e1 if available to save time
h_e1_samples_file = "{h-e1_folder}/samples.jsonl"
if exists(h_e1_samples_file):
    samples = load_jsonl(h_e1_samples_file)
else:
    # Regenerate with identical config
    samples = generate_samples(model_id, qualified_tasks, k=20, **generation_config)
```

**Acceptance Criteria:**
- K=20 samples per task (35 × 20 = 700 total)
- Identical configuration to h-e1 (controlled experiment)
- Samples available for cascade routing evaluation

---

### FR-3: Cascade Feedback Router (Core Mechanism)
**Priority:** P0 (Critical)

**Requirements:**
- Implement StaticAnalysisFeedbackRouter with cascade logic:
  1. Generate code (initial or retry)
  2. Run mypy --strict FIRST
  3. If mypy fails → Give ONLY mypy feedback, skip pytest
  4. If mypy passes → Run pytest
  5. If pytest fails → Give ONLY pytest feedback
  6. Repeat until success or max_retries (5 iterations)

**Core Implementation:**
```python
class StaticAnalysisFeedbackRouter:
    """
    Sequential single-source feedback routing with static analysis first.
    Tests whether mypy provides sufficient early error detection.
    """
    def __init__(self, model, tokenizer, max_retries=5):
        self.model = model
        self.tokenizer = tokenizer
        self.max_retries = max_retries
        self.mypy_timeout = 10  # seconds
        self.pytest_timeout = 120  # seconds

    def generate_with_feedback(self, task_prompt: str) -> dict:
        """
        Args:
            task_prompt: str - HumanEval problem prompt
        Returns:
            dict - {
                code: str,
                iterations: int,
                mypy_caught: bool,
                pytest_caught: bool,
                mypy_error_count: int,
                pytest_error_count: int,
                success: bool
            }
        """
        iteration = 0
        code = None
        mypy_error_count = 0
        pytest_error_count = 0

        while iteration < self.max_retries:
            # Step 1: Generate code
            code = self.model.generate(task_prompt, **self.generation_config)

            # Step 2: Run mypy --strict (FIRST, zero execution cost)
            mypy_result = run_mypy_strict(code, timeout=self.mypy_timeout)

            if mypy_result.has_errors:
                mypy_error_count += 1
                # Sequential feedback: ONLY mypy errors this iteration
                feedback_prompt = format_mypy_feedback(mypy_result.errors)
                task_prompt = task_prompt + "\n\nPrevious attempt failed mypy:\n" + feedback_prompt
                iteration += 1
                continue  # Skip pytest, give mypy-only feedback

            # Step 3: Run pytest (ONLY if mypy clean)
            pytest_result = run_pytest(code, timeout=self.pytest_timeout)

            if pytest_result.has_failures:
                pytest_error_count += 1
                # Sequential feedback: ONLY pytest errors this iteration
                feedback_prompt = format_pytest_feedback(pytest_result.failures)
                task_prompt = task_prompt + "\n\nTests failed:\n" + feedback_prompt
                iteration += 1
                continue

            # Success - both mypy and pytest passed
            break

        return {
            "code": code,
            "iterations": iteration,
            "mypy_caught": mypy_error_count > 0,
            "pytest_caught": pytest_error_count > 0,
            "mypy_error_count": mypy_error_count,
            "pytest_error_count": pytest_error_count,
            "mypy_error_rate": mypy_error_count / max(iteration, 1),
            "success": iteration < self.max_retries and pytest_result.passed
        }
```

**Acceptance Criteria:**
- Mypy runs BEFORE pytest in every iteration
- Pytest SKIPPED when mypy fails (conditional gating)
- Feedback is single-source per iteration (sequential)
- All 700 samples (35 tasks × 20 samples) evaluated

---

### FR-4: Static Analysis Verification (Mypy --strict)
**Priority:** P0 (Critical)

**Requirements:**
- Run mypy --strict on each generated code sample
- Capture detailed error types (type errors, null safety, signature mismatches)
- Use JSON output format for structured parsing
- Track error detection metrics per task

**Mypy Configuration:**
```python
def run_mypy_strict(code_str: str, timeout=10) -> dict:
    """
    Run mypy --strict with JSON output.
    Returns: {has_errors: bool, errors: List[dict], error_types: List[str]}
    """
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_str)
        temp_path = f.name

    # Run mypy --strict with JSON report
    result = subprocess.run(
        ["mypy", "--strict", "--no-error-summary", temp_path],
        capture_output=True,
        timeout=timeout,
        text=True
    )

    # Parse errors
    errors = []
    error_types = []
    if result.returncode != 0:
        for line in result.stdout.split('\n'):
            if ':' in line:
                # Parse: file.py:10: error: <message> [error-code]
                error_match = re.match(r'.*:(\d+): error: (.*) \[(.*)\]', line)
                if error_match:
                    errors.append({
                        "line": int(error_match.group(1)),
                        "message": error_match.group(2),
                        "code": error_match.group(3)
                    })
                    error_types.append(error_match.group(3))

    # Clean up
    os.unlink(temp_path)

    return {
        "has_errors": result.returncode != 0,
        "errors": errors,
        "error_types": list(set(error_types)),  # Unique error types
        "execution_time": time.time() - start_time
    }
```

**Acceptance Criteria:**
- Mypy status recorded for all samples
- Error types categorized (type-arg, arg-type, return-value, var-annotated, etc.)
- Execution time tracked (expected ~10s per sample)
- Timeout handling: 10 seconds per sample

---

### FR-5: Execution Testing (Pytest with HumanEval+)
**Priority:** P0 (Critical)

**Requirements:**
- Run pytest ONLY when mypy passes (conditional gating)
- Use HumanEval+ augmented tests (80+ tests per task)
- Capture pass/fail status and failure details
- Track execution time for cost comparison

**Pytest Configuration:**
```python
def run_pytest(code_str: str, test_code: str, timeout=120) -> dict:
    """
    Run pytest with HumanEval+ tests.
    Only called when mypy passes (cascade gating).
    Returns: {passed: bool, failures: List[str], execution_time: float}
    """
    start_time = time.time()

    # Create test file with code + tests
    test_content = f"{code_str}\n\n{test_code}"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_path = f.name

    # Run pytest
    result = subprocess.run(
        ["pytest", "-v", "--tb=short", temp_path],
        capture_output=True,
        timeout=timeout,
        text=True
    )

    # Parse failures
    failures = []
    if result.returncode != 0:
        # Extract failure messages from output
        for line in result.stdout.split('\n'):
            if 'FAILED' in line or 'AssertionError' in line:
                failures.append(line.strip())

    # Clean up
    os.unlink(temp_path)

    return {
        "passed": result.returncode == 0,
        "failures": failures,
        "execution_time": time.time() - start_time
    }
```

**Acceptance Criteria:**
- Pytest ONLY runs when mypy passes (conditional gating verified)
- Execution time tracked for cost comparison
- Failure details captured for feedback formatting
- Timeout handling: 120 seconds per sample

---

### FR-6: Mypy Error Detection Rate Calculation
**Priority:** P0 (Critical - MUST_WORK gate metric)

**Requirements:**
- Calculate error detection rate per task: (mypy error iterations) / (total iterations)
- Aggregate across N=35 tasks for overall detection rate
- Compare against gate threshold (≥30%)
- Generate task-level and overall statistics

**Metric Implementation:**
```python
def calculate_error_detection_rate(results: List[dict]) -> dict:
    """
    Calculate mypy error detection rate.

    Args:
        results: List of generation results from cascade router

    Returns:
        {
            "overall_detection_rate": float,  # Percentage
            "per_task_rates": List[float],
            "gate_satisfied": bool,  # ≥30%
            "mean_iterations": float,
            "mypy_only_errors": int,
            "pytest_only_errors": int,
            "both_clean": int
        }
    """
    total_iterations = 0
    total_mypy_errors = 0
    per_task_rates = []

    for task_results in results:  # One per task
        task_iterations = task_results["iterations"]
        task_mypy_errors = task_results["mypy_error_count"]

        total_iterations += task_iterations
        total_mypy_errors += task_mypy_errors

        if task_iterations > 0:
            task_rate = (task_mypy_errors / task_iterations) * 100
            per_task_rates.append(task_rate)

    # Overall detection rate
    overall_rate = (total_mypy_errors / total_iterations * 100) if total_iterations > 0 else 0

    # Gate check
    gate_satisfied = overall_rate >= 30.0  # MUST_WORK threshold

    return {
        "overall_detection_rate": overall_rate,
        "per_task_rates": per_task_rates,
        "gate_satisfied": gate_satisfied,
        "mean_iterations": total_iterations / len(results),
        "total_mypy_errors": total_mypy_errors,
        "total_pytest_errors": sum(r["pytest_error_count"] for r in results),
        "samples_evaluated": len(results)
    }
```

**Acceptance Criteria:**
- Overall detection rate calculated and displayed
- Gate threshold comparison (≥30%)
- Per-task rates available for variance analysis
- Statistics saved to validation report

---

### FR-7: Baseline Comparison (Aggregation Routing)
**Priority:** P1 (Important)

**Requirements:**
- Implement aggregation routing for comparison:
  - Run BOTH mypy + pytest in EVERY iteration
  - Concatenate both feedback sources
  - Compare iterations-to-solution vs cascade
- Track token consumption for both approaches
- Measure total execution time

**Aggregation Router Implementation:**
```python
class AggregationFeedbackRouter:
    """
    Baseline: Both-source aggregation feedback.
    Runs mypy AND pytest every iteration, concatenates feedback.
    """
    def generate_with_feedback(self, task_prompt: str) -> dict:
        iteration = 0
        code = None

        while iteration < self.max_retries:
            # Generate code
            code = self.model.generate(task_prompt, **self.generation_config)

            # Run BOTH mypy and pytest (aggregation)
            mypy_result = run_mypy_strict(code)
            pytest_result = run_pytest(code)

            # Concatenate feedback from both sources
            if mypy_result.has_errors or not pytest_result.passed:
                feedback = ""
                if mypy_result.has_errors:
                    feedback += format_mypy_feedback(mypy_result.errors)
                if not pytest_result.passed:
                    feedback += "\n" + format_pytest_feedback(pytest_result.failures)

                task_prompt = task_prompt + "\n\nFeedback:\n" + feedback
                iteration += 1
                continue

            # Success
            break

        return {
            "code": code,
            "iterations": iteration,
            "success": iteration < self.max_retries
        }
```

**Acceptance Criteria:**
- Aggregation baseline implemented
- Iterations comparison: cascade vs aggregation
- Token count comparison available
- Execution time comparison (mypy+pytest vs conditional)

---

## Non-Functional Requirements

### NFR-1: Performance
- **Execution Time:** Complete all N=35 tasks evaluation in <6 hours on single GPU
- **Mypy Performance:** <10s per sample average
- **Pytest Performance:** <120s per sample average
- **Memory Usage:** <24GB GPU memory for CodeLlama-7B

### NFR-2: Reproducibility
- **Seed:** Fixed seed=42 for all random operations
- **Model Version:** Pin CodeLlama-7B version from HuggingFace
- **Environment:** Document Python version, library versions (transformers, torch, mypy, pytest)

### NFR-3: Error Handling
- **Mypy Crashes:** Graceful handling, mark as "failed" and continue
- **Pytest Timeouts:** 120s timeout, mark as "timeout" and continue
- **GPU OOM:** Batch size=1, FP16 precision, clear cache between tasks

### NFR-4: Logging
- **Level:** INFO for progress, DEBUG for detailed error traces
- **Format:** JSON Lines for structured logging
- **Content:** Task ID, iteration, mypy/pytest status, execution time

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)
1. **Mypy Error Detection Rate ≥30%**
   - Measured across N=35 tasks
   - Aggregated from all K=20 samples per task
   - Gate threshold: 30% (hypothesis claim: 30-40%)

2. **Zero Execution Cost Validation**
   - Mypy execution time << pytest execution time
   - Expected: mypy ~10s vs pytest ~120s (12x faster)

### Secondary Success Criteria
1. **Computational Advantage**
   - Cascade shows lower total cost (time or tokens) than aggregation
   - Iterations-to-solution comparable between cascade and aggregation

2. **Task Success Rate**
   - Success rate remains comparable to h-e1 baseline
   - No degradation in solution quality

### Failure Criteria (MUST_WORK Gate)
- **Mypy detection rate <30%** → PIVOT required
  - Action: Abandon cascade routing, consider execution-first routing
  - Impact: Blocks h-m2, h-m3, h-c1

---

## Evaluation Metrics

### Primary Metrics
1. **Mypy Error Detection Rate (%):**
   - Definition: (# iterations with mypy errors) / (total iterations until success or max_retries)
   - Target: 30-40%
   - Gate: ≥30%

2. **Execution Cost Savings:**
   - Definition: Total time saved by skipping pytest when mypy fails
   - Calculation: (mypy_only_iterations × pytest_timeout_saved)
   - Expected: Significant savings if detection rate >30%

### Secondary Metrics
1. **Mean Iterations-to-Solution:**
   - Cascade vs Aggregation comparison
   - Expected: Comparable (±15%)

2. **Token Consumption:**
   - Total tokens for cascade vs aggregation
   - Measured: prompt tokens + completion tokens

3. **Error Type Distribution:**
   - Breakdown: type-arg, arg-type, return-value, var-annotated, etc.
   - Analysis: Which error types mypy catches most effectively

### Exploratory Metrics
1. **Task-Level Heatmap:**
   - N=35 tasks × {mypy_caught, pytest_caught} binary matrix
   - Visualization: Dual-sensitivity patterns

2. **Iteration Distribution:**
   - Histogram: iterations-to-solution for cascade vs aggregation
   - Box plot: variance comparison

---

## Visualization Requirements

### Required Figures (Phase 4 Must Generate)

#### Figure 1: Gate Metrics Comparison (Mandatory)
- **Type:** Bar chart with error bars
- **X-axis:** [Target (30%), Actual]
- **Y-axis:** Mypy error detection rate (%)
- **Purpose:** Validate MUST_WORK gate threshold

#### Figure 2: Error Detection Breakdown
- **Type:** Stacked bar chart
- **Categories:** Mypy-only errors, Pytest-only errors, Both clean, Both failed
- **Purpose:** Show proportion of errors caught by each feedback source

#### Figure 3: Iteration Comparison
- **Type:** Box plot
- **Groups:** Cascade routing, Aggregation routing
- **Y-axis:** Iterations-to-solution
- **Purpose:** Compare efficiency of feedback routing strategies

#### Figure 4: Execution Cost Analysis
- **Type:** Grouped bar chart
- **X-axis:** [Cascade, Aggregation]
- **Y-axis:** Total time consumed (mypy + pytest)
- **Purpose:** Validate zero execution cost claim

#### Figure 5: Task-Level Heatmap
- **Type:** Binary heatmap
- **Rows:** N=35 tasks
- **Columns:** {mypy_caught, pytest_caught}
- **Purpose:** Visualize dual-sensitivity patterns across task pool

**Output Location:** All figures saved to `h-m1/figures/`

---

## Dependencies

### Software Dependencies
- **Python:** ≥3.10
- **PyTorch:** ≥2.0 (CUDA support)
- **Transformers:** ≥4.30.0
- **Mypy:** ≥1.5.0
- **Pytest:** ≥7.0.0
- **Pytest-json-report:** For structured output
- **evalplus:** For HumanEval+ dataset
- **Matplotlib/Seaborn:** For visualization

### Data Dependencies
- **h-e1 Validation Results:**
  - Qualified task list (N=35)
  - Optional: Reuse K=20 samples per task
- **HumanEval+ Dataset:**
  - 164 tasks with augmented tests
  - Load from evalplus package

### Compute Dependencies
- **GPU:** 1× A100/H100 (24GB+ VRAM)
- **CPU:** 8+ cores for parallel mypy/pytest execution
- **Storage:** 50GB for model weights + intermediate results

---

## Risks and Mitigations

### Risk 1: Mypy Detection Rate <30% (MUST_WORK Failure)
- **Probability:** Medium
- **Impact:** Critical (blocks all downstream hypotheses)
- **Mitigation:**
  - Pilot run on N=5 tasks before full evaluation
  - If <20%, stop and PIVOT immediately
  - Document findings for reflection

### Risk 2: CodeLlama-7B Generates Mypy-Clean Code
- **Probability:** Low (h-e1 showed dual-sensitivity)
- **Impact:** High (invalidates cascade mechanism)
- **Mitigation:**
  - Use base model (NOT instruction-tuned)
  - Reuse h-e1 samples to ensure consistency

### Risk 3: Pytest Timeouts Dominate Execution Time
- **Probability:** Medium
- **Impact:** Low (still validates mechanism)
- **Mitigation:**
  - Set pytest timeout to 120s (3s per test × 40 tests)
  - Log timeout cases separately
  - Focus on error detection rate, not absolute time

---

## Implementation Plan (High-Level)

### Phase 1: Environment Setup (Epic 1)
- Install dependencies (mypy, pytest, evalplus, transformers)
- Configure GPU environment (CUDA_VISIBLE_DEVICES)
- Load CodeLlama-7B model

### Phase 2: Data Loading (Epic 2)
- Load N=35 qualified tasks from h-e1
- Verify dual-sensitivity for all tasks
- Prepare HumanEval+ test suite

### Phase 3: Core Implementation (Epic 3-5)
- Implement StaticAnalysisFeedbackRouter (cascade)
- Implement AggregationFeedbackRouter (baseline)
- Integrate mypy --strict runner
- Integrate pytest runner with HumanEval+ tests

### Phase 4: Evaluation (Epic 6-7)
- Run cascade routing on N=35 tasks × K=20 samples
- Run aggregation baseline for comparison
- Calculate mypy error detection rate
- Generate all required figures

### Phase 5: Validation (Epic 8)
- Verify MUST_WORK gate (≥30%)
- Generate validation report (04_validation.md)
- Update verification_state.yaml

---

## Appendix: Reference Implementations

### Primary Reference: LLMLOOP Framework
- **Paper:** "LLMLOOP: Improving LLM-Generated Code and Tests through Feedback Loops" (Ravi et al., ICSME 2025)
- **URL:** https://valerio-terragni.github.io/assets/pdf/ravi-icsme-2025.pdf
- **GitHub:** https://github.com/ravinravi03/LLMLOOP
- **Relevance:** Implements static analysis feedback loop (Loop 2) with mypy/PMD
- **Key Pattern:** LLM → Code Generation → Static Analysis → Feedback → Refinement
- **Adaptation:** Use sequential (cascade) instead of aggregation feedback

### Secondary Reference: ACE Playbook
- **URL:** https://github.com/jmanhype/ace-playbook
- **Relevance:** Production LLM system with mypy pre-commit hooks
- **Key Pattern:** mypy integrated into continuous validation pipeline

---

## Output Files

### Generated Artifacts
1. **03_prd.md** - This document
2. **03_architecture.md** - System architecture (Step 3)
3. **03_logic.md** - API signatures and algorithms (Step 5)
4. **03_config.md** - Hyperparameters and settings (Step 5)
5. **03_tasks.yaml** - Implementation tasks (Step 9)

### Runtime Artifacts (Phase 4)
1. **samples.jsonl** - Generated code samples (700 total)
2. **cascade_results.jsonl** - Cascade routing results
3. **aggregation_results.jsonl** - Aggregation baseline results
4. **metrics.json** - All evaluation metrics
5. **figures/** - All visualization outputs
6. **04_validation.md** - Validation report with gate result

---

*Generated by Phase 3 Implementation Planning - Step 2 (PRD Generation)*
*Source: h-m1/02c_experiment_brief.md*
*MUST_WORK Gate: Mypy error detection rate ≥30%*
