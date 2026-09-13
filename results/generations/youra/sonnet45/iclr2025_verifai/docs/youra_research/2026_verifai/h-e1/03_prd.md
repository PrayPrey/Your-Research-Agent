---
stepsCompleted: ['initialization', 'requirements-gathering', 'functional-requirements', 'non-functional-requirements', 'success-criteria', 'validation']
prd_completed: true
validation_status: PASSED
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_date: 2026-03-18
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document (PRD)
# Hypothesis h-e1: Dual-Sensitive Task Classification System

**Date:** 2026-03-18
**Author:** Claude (Implementation Planning Specialist)
**Hypothesis:** Under HumanEval benchmark conditions with K=20 baseline sample classification, dual-sensitive programming tasks exist in sufficient quantity (N ≥ 20) with adequate within-task paired variance (SD ≤ 1.0) to support paired-comparison experimental design for feedback routing causality testing.
**Phase:** Phase 3 - Implementation Planning
**Gate Type:** MUST_WORK

---

## Executive Summary

This PRD defines the implementation requirements for h-e1, an EXISTENCE hypothesis that validates the foundational assumption for feedback routing research. The system will classify HumanEval programming tasks as "dual-sensitive" by generating K=20 code solutions per task using CodeLlama-7B, then evaluating each solution with both mypy --strict (static analysis) and pytest (execution testing).

**Core Objective:** Demonstrate that ≥20 HumanEval tasks exhibit dual-sensitivity (where ≥1 solution fails mypy but passes pytest AND ≥1 passes mypy but fails pytest) with within-task variance SD ≤ 1.0.

**Success Criteria:** N ≥ 20 qualifying tasks identified from 164 total HumanEval tasks.

**Failure Impact:** MUST_WORK gate - failure blocks all downstream hypotheses (h-m1, h-m2, h-m3, h-c1).

---

## Problem Statement

### Research Gap
Current code generation research lacks systematic understanding of task sensitivity to different feedback modalities (static vs execution). Without establishing a pool of dual-sensitive tasks, we cannot:
1. Test feedback routing causality
2. Design controlled experiments for cascade vs aggregation policies
3. Validate attention economy hypotheses for LLM feedback processing

### Hypothesis Context
- **Type:** EXISTENCE (PoC validation)
- **Prerequisites:** None (Level 0 - Foundation hypothesis)
- **Dependency Level:** 0 (root hypothesis)
- **Blocks:** h-m1, h-m2, h-m3, h-c1

### Expected Outcomes
- Primary: N = 30-50 dual-sensitive tasks (target minimum: 20)
- Secondary: Within-task variance SD ≤ 1.0 for power analysis
- Exploratory: Task difficulty distribution, mypy/pytest failure patterns

---

## Functional Requirements

### FR-1: Dataset Loading and Management
**Priority:** P0 (Critical)

**Requirements:**
- Load 164 HumanEval tasks from evalplus package (HumanEval+ augmented tests)
- Alternative fallback: Original human-eval package if evalplus unavailable
- Parse task structure: prompt, entry_point, test cases
- Store task metadata for classification pipeline

**Implementation Details:**
```python
from evalplus.data import get_human_eval_plus, write_jsonl
problems = get_human_eval_plus()  # Returns dict of 164 tasks

# Fallback:
from human_eval.data import read_problems
problems = read_problems()  # Original HumanEval
```

**Acceptance Criteria:**
- All 164 tasks loaded successfully
- Task structure validated (prompt, entry_point, test fields present)
- No preprocessing or augmentation applied

---

### FR-2: Code Generation System
**Priority:** P0 (Critical)

**Requirements:**
- Load CodeLlama-7B base model (NOT instruction-tuned) from HuggingFace
- Generate K=20 samples per task with fixed configuration
- Use deterministic sampling with seed=1 for reproducibility
- Save completions in JSON Lines format

**Model Configuration:**
- Model ID: `codellama/CodeLlama-7b-hf`
- Precision: FP16 (torch.float16)
- Device: Auto-assign single GPU
- Temperature: 0.8
- Top-p: 0.95
- Top-k: 40
- Max tokens: 256
- Seed: 1 (fixed)

**Generation Protocol:**
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)

# Generate K=20 samples per task
for task_id, problem in problems.items():
    for sample_idx in range(20):
        completion = model.generate(
            problem["prompt"],
            temperature=0.8,
            top_p=0.95,
            top_k=40,
            max_length=256,
            do_sample=True
        )
```

**Acceptance Criteria:**
- K=20 samples generated per task (164 × 20 = 3,280 total completions)
- All samples saved with task_id and sample_idx
- Generation time: 4.5-9 hours on single GPU (acceptable)

---

### FR-3: Static Analysis Verification (Mypy)
**Priority:** P0 (Critical)

**Requirements:**
- Run mypy --strict on each generated code sample
- Capture pass/fail status (binary classification)
- Use JSON output format for structured parsing
- Handle mypy errors gracefully (timeout, crashes)

**Mypy Configuration:**
```bash
mypy --strict --json-report /tmp/mypy-report <code_file.py>
```

**Implementation:**
```python
def run_mypy(code_str: str) -> bool:
    """
    Run mypy --strict on code sample.
    Returns True if passes, False if fails.
    """
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_str)
        temp_path = f.name

    # Run mypy
    result = subprocess.run(
        ["mypy", "--strict", "--json-report", "/tmp/mypy-report", temp_path],
        capture_output=True,
        timeout=10
    )

    # Clean up
    os.unlink(temp_path)

    return result.returncode == 0
```

**Acceptance Criteria:**
- Mypy status recorded for all 3,280 samples
- JSON output parsed correctly
- Timeout handling: 10 seconds per sample
- Error cases logged (mypy crashes, invalid syntax)

---

### FR-4: Execution Testing (Pytest)
**Priority:** P0 (Critical)

**Requirements:**
- Run pytest with HumanEval+ augmented tests (80+ tests per task)
- Capture pass/fail status (binary classification)
- Use sandboxed execution (timeout: 3 seconds per test)
- Handle pytest errors gracefully (timeouts, exceptions)

**Pytest Configuration:**
```bash
pytest --json-report --json-report-file=report.json -x <test_file.py>
```

**Implementation:**
```python
def run_pytest(code_str: str, test_code: str) -> bool:
    """
    Run pytest with HumanEval+ tests.
    Returns True if all tests pass, False otherwise.
    """
    # Create test file with code + tests
    test_content = f"{code_str}\n\n{test_code}"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_path = f.name

    # Run pytest with timeout
    result = subprocess.run(
        ["pytest", "--json-report", "--json-report-file=/tmp/report.json", "-x", temp_path],
        capture_output=True,
        timeout=120  # 3s per test × 40 tests
    )

    # Clean up
    os.unlink(temp_path)

    return result.returncode == 0
```

**Acceptance Criteria:**
- Pytest status recorded for all 3,280 samples
- JSON output parsed correctly
- Timeout handling: 120 seconds per sample
- Test execution isolated (no cross-contamination)

---

### FR-5: Dual-Sensitivity Classification
**Priority:** P0 (Critical)

**Requirements:**
- Classify each task based on K=20 sample results
- Apply dual-sensitivity criteria:
  - ≥1 solution fails mypy but passes pytest (mypy_fail_pytest_pass ≥ 1)
  - ≥1 solution passes mypy but fails pytest (mypy_pass_pytest_fail ≥ 1)
- Compute within-task variance (SD) across K=20 samples
- Apply variance threshold: SD ≤ 1.0

**Classifier Implementation:**
```python
class DualSensitivityClassifier:
    def __init__(self, k_samples=20, variance_threshold=1.0):
        self.k = k_samples
        self.sd_threshold = variance_threshold

    def classify_task(self, task_id: str, mypy_results: List[bool],
                      pytest_results: List[bool]) -> Dict:
        """
        Classify task as dual-sensitive.

        Returns:
            {
                "dual_sensitive": bool,
                "mypy_only_fails": int,
                "pytest_only_fails": int,
                "variance": float,
                "qualifies": bool  # dual_sensitive AND variance ≤ threshold
            }
        """
        # Count failure patterns
        mypy_fail_pytest_pass = sum([
            (not m) and p
            for m, p in zip(mypy_results, pytest_results)
        ])
        mypy_pass_pytest_fail = sum([
            m and (not p)
            for m, p in zip(mypy_results, pytest_results)
        ])

        # Dual-sensitivity check
        dual_sensitive = (mypy_fail_pytest_pass >= 1) and (mypy_pass_pytest_fail >= 1)

        # Compute within-task variance
        # Convert bool results to numeric for variance computation
        numeric_results = [
            int(m) + int(p)
            for m, p in zip(mypy_results, pytest_results)
        ]
        variance = np.std(numeric_results)

        # Final qualification
        qualifies = dual_sensitive and (variance <= self.sd_threshold)

        return {
            "task_id": task_id,
            "dual_sensitive": dual_sensitive,
            "mypy_only_fails": mypy_fail_pytest_pass,
            "pytest_only_fails": mypy_pass_pytest_fail,
            "variance": variance,
            "qualifies": qualifies
        }
```

**Acceptance Criteria:**
- All 164 tasks classified
- Qualifying tasks (N) counted
- Variance computed for all tasks
- Classification results saved to JSON

---

### FR-6: Success Gate Validation
**Priority:** P0 (Critical)

**Requirements:**
- Count qualifying tasks: N = tasks with dual_sensitive=True AND SD≤1.0
- Check MUST_WORK gate: N ≥ 20
- If N < 20: Apply risk mitigation (relax threshold to 0.2)
- Generate gate validation report

**Gate Logic:**
```python
def validate_gate(classification_results: List[Dict]) -> Dict:
    """
    Validate MUST_WORK gate condition.

    Returns:
        {
            "gate_satisfied": bool,
            "qualifying_count": int,
            "threshold_used": float,
            "action": str  # "PASS" | "RETRY_RELAXED" | "FAIL"
        }
    """
    qualifying = [r for r in classification_results if r["qualifies"]]
    N = len(qualifying)

    if N >= 20:
        return {
            "gate_satisfied": True,
            "qualifying_count": N,
            "threshold_used": 1.0,
            "action": "PASS"
        }

    # Risk Mitigation R1: Relax threshold
    print(f"N={N} < 20. Applying risk mitigation: relax SD threshold to 0.2")
    relaxed_qualifying = [
        r for r in classification_results
        if r["dual_sensitive"] and r["variance"] <= 0.2
    ]
    N_relaxed = len(relaxed_qualifying)

    if N_relaxed >= 20:
        return {
            "gate_satisfied": True,
            "qualifying_count": N_relaxed,
            "threshold_used": 0.2,
            "action": "PASS"
        }

    return {
        "gate_satisfied": False,
        "qualifying_count": N_relaxed,
        "threshold_used": 0.2,
        "action": "FAIL"
    }
```

**Acceptance Criteria:**
- Gate status determined (PASS/FAIL)
- If FAIL: Clear error message with mitigation attempts logged
- If PASS: N value and threshold reported

---

### FR-7: Visualization and Reporting
**Priority:** P1 (High)

**Requirements:**
- Generate 4 figures as specified in Phase 2C
- Save all figures to `{hypothesis_folder}/figures/`
- Include gate metrics comparison (mandatory)

**Figure 1: Gate Metrics Comparison (Mandatory)**
- Bar chart: Target (N=20) vs Actual (N=X)
- Color: Green if pass, red if fail

**Figure 2: Task Classification Distribution**
- Bar chart: Dual-sensitive vs Not dual-sensitive (164 tasks total)
- Show breakdown by classification

**Figure 3: Variance Distribution Histogram**
- Histogram of SD values for qualifying tasks
- Mark SD=1.0 threshold line
- Show median SD

**Figure 4: Dual-Sensitivity Patterns**
- Scatter plot: mypy_only_fails vs pytest_only_fails
- Highlight qualifying tasks (both ≥1)
- Quadrant visualization

**Acceptance Criteria:**
- All 4 figures generated
- Figures saved as PNG (300 DPI)
- Figure filenames: `fig1_gate_metrics.png`, `fig2_classification.png`, etc.

---

## Non-Functional Requirements

### NFR-1: Performance
- **Generation Time:** 4.5-9 hours on single GPU (acceptable for EXISTENCE PoC)
- **Mypy Execution:** ~1-2 hours total (timeout: 10s per sample)
- **Pytest Execution:** ~1-2 hours total (timeout: 120s per sample)
- **Total Runtime:** 6-11 hours on single GPU

### NFR-2: Reproducibility
- **Fixed Seed:** seed=1 for all random operations
- **Model Version:** Pin CodeLlama-7B version (codellama/CodeLlama-7b-hf)
- **Dataset Version:** Pin evalplus version in requirements.txt
- **Configuration Logging:** Save all hyperparameters to config.json

### NFR-3: Resource Requirements
- **GPU:** Single GPU with ≥16GB VRAM (for FP16 CodeLlama-7B)
- **RAM:** ≥32GB system RAM (for dataset + sample storage)
- **Storage:** ~5GB (model weights + samples + results)

### NFR-4: Error Handling
- **Mypy Timeout:** 10 seconds per sample, mark as "timeout" if exceeded
- **Pytest Timeout:** 120 seconds per sample, mark as "timeout" if exceeded
- **GPU OOM:** Reduce batch size to 1, retry generation
- **Model Loading:** Retry up to 3 times with 15-second delay

### NFR-5: Code Quality
- **Type Hints:** All functions must have type annotations
- **Documentation:** Docstrings for all public classes/functions
- **Testing:** Unit tests for classifier logic (variance computation, dual-sensitivity check)
- **Logging:** INFO level for progress, DEBUG for detailed results

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)
1. ✅ N ≥ 20 dual-sensitive tasks identified
2. ✅ Median SD ≤ 1.0 across qualifying tasks
3. ✅ All 164 tasks processed without fatal errors

### Secondary Success Criteria
1. Expected N = 30-50 qualifying tasks (nominal performance)
2. Mypy-only failure rate: 10-30% across qualifying tasks
3. Pytest-only failure rate: 10-30% across qualifying tasks
4. Classification completion time: ≤12 hours on single GPU

### Validation Criteria
1. Reproducible results with fixed seed
2. All figures generated successfully
3. Gate validation report completed
4. Results saved to `{hypothesis_folder}/04_validation.md`

---

## Dependencies

### External Dependencies
- **evalplus** (Python package) - HumanEval+ augmented tests
- **human-eval** (Python package, fallback) - Original HumanEval
- **transformers** (HuggingFace) - CodeLlama-7B model loading
- **torch** - PyTorch for model inference
- **mypy** - Static type checking
- **pytest** - Test execution framework
- **numpy** - Variance computation
- **matplotlib** - Visualization

### System Dependencies
- **Python:** 3.8+
- **CUDA:** 11.0+ (for GPU support)
- **GPU Driver:** Compatible with CUDA version

### Data Dependencies
- **HumanEval dataset:** 164 tasks from evalplus package
- **CodeLlama-7B weights:** Downloaded from HuggingFace Hub

---

## Risk Mitigation

### Risk R1: N < 20 with SD ≤ 1.0 threshold
**Probability:** Medium
**Impact:** Critical (MUST_WORK gate failure)
**Mitigation:** Relax SD threshold to 0.2 (Phase 2B Risk Mitigation R1)
**Fallback:** If still N < 20, STOP pipeline and report insufficient task pool

### Risk R2: GPU OOM during generation
**Probability:** Low
**Impact:** High (generation failure)
**Mitigation:** Reduce batch size to 1, generate samples sequentially
**Fallback:** Use CPU generation (slower but functional)

### Risk R3: Mypy/Pytest timeout for complex tasks
**Probability:** Medium
**Impact:** Low (individual sample failure)
**Mitigation:** Mark as "timeout" and continue, exclude from classification
**Fallback:** Increase timeout limits if >10% samples timeout

---

## Out of Scope

1. **Model Fine-Tuning:** CodeLlama-7B used as-is (no training)
2. **Dataset Augmentation:** HumanEval used without modification
3. **Multi-GPU Parallelization:** Single GPU sufficient for PoC
4. **Baseline Comparison:** Deferred to Phase 5 (pipeline-wide comparison)
5. **Feedback Routing Implementation:** Not part of h-e1 (deferred to h-m1, h-m2, h-m3)

---

## Implementation Notes

### Phase 2C Traceability
All specifications trace to Phase 2C experiment brief:
- Dataset: Section "Dataset" (lines 208-243)
- Model: Section "Models" (lines 245-298)
- Evaluation: Section "Evaluation" (lines 403-453)
- Training Protocol: Section "Training Protocol" (lines 367-401)
- Visualization: Section "Visualization Requirements" (lines 455-482)

### Architecture Hints for Phase 3
1. **Modular Design:** Separate modules for dataset, generation, mypy, pytest, classifier
2. **Pipeline Orchestration:** Main script coordinates 5 stages (load → generate → mypy → pytest → classify)
3. **Checkpoint Support:** Save intermediate results after each stage (generation, mypy, pytest)
4. **Configuration Management:** YAML config file for all hyperparameters

### Known Constraints
- **LIGHT Budget:** 15 tasks maximum (EXISTENCE hypothesis)
- **Epic Range:** 4-8 tasks for architecture design
- **No Baseline Comparison:** Phase 5 deferred (skip_baseline_comparison=true)

---

## Appendix: Phase 2C References

### Repository References
1. **openai/human-eval** - Official HumanEval implementation
2. **evalplus/evalplus** - HumanEval+ augmented tests
3. **codellama/CodeLlama-7b-hf** - HuggingFace model
4. **MindStudio workflow** - Mypy/pytest integration pattern

### Implementation Research Sources
- Phase 2C Archon KB searches: No directly relevant past cases (novel implementation)
- Phase 2C Exa GitHub searches: 5 repositories analyzed
- Phase 2C Serena analysis: Skipped (HumanEval API well-documented)

---

*Generated by Phase 3 Implementation Planning (Step 02: PRD Generation)*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Phase 3 Step 03 - Architecture Design*
