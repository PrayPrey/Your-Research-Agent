---
name: 'step-05c-post-validation'
description: 'Post-Experiment Validation - Result parsing, mock data/model verification, training sufficiency check, and result collection'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References (order-independent references)
thisStepFile: '{workflow_path}/steps/step-05c-post-validation.md'
nextStepFile: '{workflow_path}/steps/step-06-gate-processing.md'
prevStepFile: '{workflow_path}/steps/step-05b-execution.md'
coderStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
workflowFile: '{workflow_path}/workflow.md'

# Step 5 Sub-steps (for cross-reference)
step5a: '{workflow_path}/steps/step-05a-pre-validation.md'
step5b: '{workflow_path}/steps/step-05b-execution.md'
step5c: '{workflow_path}/steps/step-05c-post-validation.md'

# Input Files
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
code_folder: '{hypothesis_folder}/code'

# Output Files
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
results_file: '{hypothesis_folder}/experiment_results.json'
experiment_log: '{code_folder}/experiment.log'
terminal_log: '{code_folder}/terminal.log'

# Error Escalation Limits
max_quick_fix_attempts: 5
max_step2_retries: 1
max_mock_model_retries: 3
max_mock_data_retries: 3
max_training_sufficiency_retries: 3

# Helper References
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'
mock_detection: '{helpers_path}/mock_detection.md'
training_sufficiency: '{helpers_path}/training_sufficiency.md'
checkpoint_helpers: '{helpers_path}/checkpoint_helpers.md'
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 5:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, experiment_status={checkpoint.experiment_status}")
```

---

# Step 5C: Post-Experiment Validation (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Part:** 3 of 3 (5A → 5B → 5C)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- Parse experiment results and extract metrics
- Detect mock data/model usage patterns
- Validate against expected outputs from 02c experiment brief
- Save verified results to experiment_results.json

### Universal Rules

- 🔄 CRITICAL: When proceeding to next step, load and read entire file first
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Save checkpoint after each major action

### Step-Specific Rules

- MUST verify experiment.log exists before parsing
- MUST perform post-experiment mock data verification
- MUST follow Error Escalation Protocol (5 quick fixes → 1 Step 2 retry)
- MUST verify this was FULL experiment, not smoke test
- NEVER proceed to Step 6 with smoke test results
- NEVER proceed if `execution_plan.is_full_run == False`

---

## STEP GOAL

Post-experiment validation and result collection:
1. Verify experiment.log exists and parse results
2. Detect mock/synthetic data usage in experiment output
3. Verify training sufficiency (epochs, dataset scale, duration)
4. Collect and structure experiment results
5. Handle persistent errors with escalation protocol
6. Proceed to Gate Processing

---

## EXECUTION SEQUENCE

### 1. Verify Experiment Log & Parse Results

##### Step 0: Verify Experiment Log (LLM Judgment) - MANDATORY

Read `{code_folder}/experiment.log` and **judge whether the experiment actually ran**.

**Signs of a REAL experiment (should see most of these):**
- Model loading messages (e.g., "Loading model", "Downloading weights")
- GPU/CUDA initialization
- Training progress (epochs, batches, loss values)
- Memory usage or profiling data
- Actual metrics being computed
- Duration logs showing reasonable execution time

**Signs of SKIPPED/INCOMPLETE experiment:**
- Only initialization messages ("LOG INITIALIZED") with no actual content
- Very short log (< 20 meaningful lines)
- No evidence of model execution or training
- Only error messages without recovery
- Log ends abruptly after setup

**Your judgment:**

1. **If experiment appears SKIPPED or INCOMPLETE:**
   - Update checkpoint: `checkpoint.partial_results.experiment_status = "skipped"`
   - Add reason: `checkpoint.partial_results.skip_reason = "<your assessment>"`
   - Increment skip retry counter: `checkpoint.experiment_skip_retries += 1`
   - Save checkpoint
   - Print: "🔄 Experiment skipped - routing to Step 5B for re-execution"
   - Load, read entire file, then execute: `{step5b}` (step-05b-execution.md)
   - EXIT

2. **If experiment ran normally:**
   - Print: "✅ Experiment log verified - real experiment executed"
   - Append completion footer to log (optional, for tracking)
   - Continue to next section

##### Step 1: Find Output Files

```python
# Find output files/logs
mcp__serena__list_dir(
    relative_path=f"{code_folder}/outputs",
    recursive=True
)

# OR search for result patterns
mcp__serena__search_for_pattern(
    substring_pattern="accuracy|loss|f1|auc|precision|recall",
    relative_path=code_folder,
    paths_include_glob="*.json,*.yaml,*.csv,*.log"
)

# Parse metrics from output
IF json_yaml_found:
    Read and parse directly
ELIF metrics_in_stdout:
    Parse using regex patterns
```

---

### 2. Collect Results

```python
results = {
    "execution_mode": "auto",
    "status": "completed",
    "timestamp": ISO8601,
    "hypothesis_id": hypothesis_id,
    "entry_point": execution_plan.entry_point,
    "command_used": execution_plan.command,
    "conda_env": conda_env_name,

    # 🚨 MANDATORY: Log file info for user visibility
    "experiment_log": {
        "path": f"{code_folder}/experiment.log",
        "exists": True, # MUST be True
        "line_count": log_lines
    },

    "hardware": {
        "gpu_available": checkpoint.gpu.available,
        "gpu_info": checkpoint.gpu.info,
        "gpu_count": checkpoint.gpu.count
    },

    "metrics": {
        "accuracy": value,
        "loss": value,
        # ... etc
    },
    "training": {
        "epochs_completed": n,
        "final_loss": value,
        "duration_seconds": n
    },
    "hyperparameters_final": {
        # Extracted from config/logs
    },
    "components_validated": [
        # List of validated components
    ]
}

# Log path for user reference
print(f"🎉 Experiment completed: {code_folder}/experiment.log")
```

---

### 3. Mock Data Detection (LLM-Based Verification) - MANDATORY

> **LLM-Based Verification:** The LLM reads checkpoint and experiment log to determine if real data was used
> **Reference:** `helpers/mock_detection.md` - LLM-based reality verification
> **Trigger:** Always runs (not gated on PASS/FAIL)

🚨 **CRITICAL:** Experiments using fake data are INVALID regardless of gate result.
If mock data detected → Return to Step 2 immediately (max 3 retries).

**Note:** Test files (`tests/`, `test_*.py`) are ALLOWED to use mock data.

```python
# ============================================================================
# 🔍 LLM-BASED MOCK DATA VERIFICATION (Using helpers/mock_detection.md)
# ============================================================================
# Reference: helpers/mock_detection.md, helpers/checkpoint_helpers.md

from mock_detection import detect_mock_usage
from checkpoint_helpers import update_checkpoint, handle_validation_failure

print("🔍 LLM verifying experiment used real data...")

# LLM-based verification with "Expected vs Actual" comparison
mock_result = detect_mock_usage(
    code_folder=code_folder,
    detection_type="data",
    checkpoint_file=f"{hypothesis_folder}/04_checkpoint.yaml",
    experiment_log_file=f"{code_folder}/experiment.log",
    experiment_results_file=f"{hypothesis_folder}/experiment_results.json",
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
)

IF mock_result["detected"]:
    print(f"🚨 MOCK DATA DETECTED! (Severity: {mock_result['severity']})")

    failure = handle_validation_failure(
        checkpoint, checkpoint_file, results,
        retry_type="mock_data_retries", max_retries=3,
        blocked_field="mock_data_blocked",
        status_field="mock_data_status",
        results_key="mock_data_detection",
        detection_result=mock_result,
        fix_task_id_prefix="fix-mock-",
        fix_task_title="[POST-CHECK MOCK FIX] Remove mock data usage",
        fix_task_description=f"""🚨 Mock data detected in experiment output!
Violations: {mock_result['violation_count']}
Severity: {mock_result['severity']}
Required dataset from 02c: {dataset_info.get('name', 'N/A')}
FIX: Remove mock/synthetic data, ensure real dataset loaded.""",
        fix_task_source="step-05c-mock-detection",
        return_reason="MOCK_DATA_DETECTED"
    )

    IF failure["action"] == "ROUTE_TO_STEP2":
        Load, read entire file, then execute: {coderStepFile}
        EXIT
    # BLOCKED → continue to Step 6

ELSE:
    print("✅ No mock data detected - using real dataset")
    update_checkpoint(checkpoint, {"mock_data_status": "PASSED"}, checkpoint_file)
    results["mock_data_detection"] = mock_result
```

---

### 3.5 🔬 Reality Check (LLM-Based Model Verification) - MANDATORY

> **Purpose:** LLM-based verification to detect fake/mock MODELS
> **Reference:** `helpers/mock_detection.md` - LLM-based reality verification
> **Full reference:** `_references/reality-check-guide.md`

🚨 **CRITICAL:** This detects CODE problems (mock model), NOT hypothesis problems.
If Reality Check fails → Return to Step 2 immediately (don't proceed to Step 6).

```python
# ============================================================================
# 🔬 LLM-BASED MODEL VERIFICATION (Using helpers/mock_detection.md)
# ============================================================================
# Reference: helpers/mock_detection.md, helpers/checkpoint_helpers.md

from mock_detection import detect_mock_model_runtime
from checkpoint_helpers import update_checkpoint, handle_validation_failure

print("🔬 LLM verifying experiment used real model...")

reality_check = results.get("mechanism_reality_check", {})
critical_tests = ["determinism", "sensitivity", "smoothness"]

# Case 1: Reality Check was not executed
IF NOT reality_check:
    print("⚠️ WARNING: Reality check was not executed!")
    results["reality_check_warning"] = "NOT_EXECUTED"
    update_checkpoint(checkpoint, {"reality_check_status": "NOT_EXECUTED"}, checkpoint_file)
    # Continue to Step 6 - Gate Processing will handle this

# Case 2: Reality Check FAILED - Mock Model Detected
ELIF NOT all(reality_check.get("tests", {}).get(t, False) for t in critical_tests):
    failed_tests = [t for t in critical_tests if not reality_check.get("tests", {}).get(t, False)]
    print(f"🚨 REALITY CHECK FAILED - Mock model suspected! Failed: {failed_tests}")

    # LLM-based verification
    model_check = detect_mock_model_runtime(
        model_info={},
        code_folder=code_folder,
        checkpoint_file=f"{hypothesis_folder}/04_checkpoint.yaml",
        experiment_log_file=f"{code_folder}/experiment.log",
        experiment_results_file=f"{hypothesis_folder}/experiment_results.json",
        experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
    )

    failure = handle_validation_failure(
        checkpoint, checkpoint_file, results,
        retry_type="mock_model_retries", max_retries=3,
        blocked_field="mock_model_blocked",
        status_field="reality_check_status",
        results_key="reality_check_result",
        detection_result={"verdict": "BLOCKED", "failed_tests": failed_tests, "model_check": model_check},
        fix_task_id_prefix="fix-model-",
        fix_task_title="[REALITY CHECK FIX] Replace mock model with real implementation",
        fix_task_description=f"""🚨 Reality Check FAILED - Mock model detected!
Failed tests: {failed_tests}
FIX: Implement real neural network layers, ensure model weights affect output,
verify gradient flow, check forward pass processes input.""",
        fix_task_source="step-05c-reality-check",
        return_reason="MOCK_MODEL_DETECTED"
    )

    IF failure["action"] == "ROUTE_TO_STEP2":
        Load, read entire file, then execute: {coderStepFile}
        EXIT
    # BLOCKED → continue to Step 6

# Case 3: Reality Check PASSED
ELSE:
    print("✅ Reality Check PASSED - Real model confirmed")
    supplementary_tests = ["gradient_flow", "weight_influence"]
    failed_supplementary = [t for t in supplementary_tests
                           if not reality_check.get("tests", {}).get(t, True)]

    update_checkpoint(checkpoint, {"reality_check_status": "PASSED"}, checkpoint_file)
    results["reality_check_result"] = {
        "verdict": "REAL_MODEL", "critical_tests": "ALL_PASSED",
        "supplementary_warnings": failed_supplementary if failed_supplementary else None
    }
```

---

### 3.7 📏 Training Sufficiency Check (LLM-Based Verification) - MANDATORY

> **Purpose:** LLM-based verification to ensure the experiment ran at sufficient scale for PoC conclusions
> **Reference:** `helpers/training_sufficiency.md` - LLM-based sufficiency verification
> **Trigger:** Always runs after mock checks pass (not gated on PASS/FAIL)

🚨 **CRITICAL:** Experiments with insufficient training scale produce unreliable results.
If insufficient training detected → Return to Step 2 immediately (max 3 retries).

**This check catches DIFFERENT problems than mock detection:**
- Mock detection: "Is this fake data/model?" (e.g., `torch.randn()`)
- Sufficiency check: "Is this real but inadequate?" (e.g., real CIFAR-10 but only 50 samples, or only 2 epochs)

```python
# ============================================================================
# 📏 LLM-BASED TRAINING SUFFICIENCY VERIFICATION
# ============================================================================
# Reference: helpers/training_sufficiency.md, helpers/checkpoint_helpers.md

from training_sufficiency import verify_training_sufficiency
from checkpoint_helpers import update_checkpoint, handle_validation_failure

print("📏 LLM verifying training sufficiency...")

# Call helper (uses already-available context from Sections 1-3)
sufficiency_result = verify_training_sufficiency(
    results=results,
    experiment_log_content=log_content, # From Section 1 Step 0
    experiment_brief_content=brief_content # From Section 3 (mock detection read)
)

IF NOT sufficiency_result["sufficient"]:
    print(f"🚨 TRAINING INSUFFICIENT! Issues: {sufficiency_result['issues']}")

    failure = handle_validation_failure(
        checkpoint, checkpoint_file, results,
        retry_type="training_sufficiency_retries", max_retries=3,
        blocked_field="training_sufficiency_blocked",
        status_field="training_sufficiency_status",
        results_key="training_sufficiency",
        detection_result=sufficiency_result,
        fix_task_id_prefix="fix-sufficiency-",
        fix_task_title="[TRAINING SUFFICIENCY FIX] Increase experiment scale",
        fix_task_description=f"""🚨 Training sufficiency check FAILED!
Issues: {sufficiency_result['issues']}
Epochs: {sufficiency_result['epochs_completed']} (expected: {sufficiency_result['epochs_expected']})
Duration: {sufficiency_result['duration_seconds']}s
FIX: See helpers/training_sufficiency.md for criteria.
Reference 02c_experiment_brief.md Training Protocol for expected values.""",
        fix_task_source="step-05c-training-sufficiency",
        return_reason="TRAINING_INSUFFICIENT"
    )

    IF failure["action"] == "ROUTE_TO_STEP2":
        Load, read entire file, then execute: {coderStepFile}
        EXIT
    # BLOCKED → continue to Step 6

ELSE:
    print("✅ Training sufficiency verified - adequate scale for PoC")
    update_checkpoint(checkpoint, {"training_sufficiency_status": "PASSED"}, checkpoint_file)
    results["training_sufficiency"] = sufficiency_result
```

---

### 4. Persistent Error Escalation Protocol

🚨 **MANDATORY: Read `_references/error-escalation-protocol.md`**

**Limits:** `max_quick_fix_attempts: 5`, `max_step2_retries: 1`

```python
IF persistent_error:
    # 1. Initialize error tracking (use template-defined error_escalation field)
    checkpoint.error_escalation = {
        "quick_fix_attempts": 0,
        "step2_retries": 0,
        "error_history": [],
        "tasks_created": []
    }

    # 2. Quick Fix (up to 5 attempts)
    WHILE quick_fix_attempts < 5:
        Search Archon KB
        Try auto-fix
        IF fixed: break

    # 3. Step 2 Escalation (if quick fix fails)
    IF quick_fix_attempts >= 5 AND step2_retries < 1:
        # Create error task in Archon
        hypothesis_feature = checkpoint.get("archon", {}).get("hypothesis_feature")
        mcp__archon__manage_task(
            action="create",
            project_id=archon_project_id,
            title=f"[RUNTIME ERROR] {error_type} in {file}",
            description=f"Error: {error_message}\nTraceback: {traceback}",
            feature=hypothesis_feature,
            status="todo"
        )

        # Return to Step 2
        checkpoint.return_to_step5_after_coder = True
        SAVE checkpoint
        # MANDATORY: Load Step 2 immediately

    # 4. If all attempts exhausted
    IF quick_fix_attempts >= 5 AND step2_retries >= 1:
        # Mark as BLOCKED and proceed
        results.status = "blocked"
        results.block_reason = error_message
```

---

### 5. Save Results

```python
Write results to {results_file}

checkpoint.current_step = 5
checkpoint.partial_results.experiment_status = results.status
checkpoint.partial_results.experiment_results = results
checkpoint.updated_at = now()
SAVE checkpoint
```

---

### 6. Proceed to Next Step

🚨 **CRITICAL: Verify this was FULL EXPERIMENT, not smoke test**

```python
# MUST check if this was full run before proceeding to Gate Processing
IF NOT execution_plan.is_full_run:
    # Still in smoke test phase - should have been caught by Step 5B
    STOP("ERROR: Attempting to proceed to Gate Processing with smoke test results")

IF checkpoint.experiment_status == "smoke_test_passed":
    # Smoke test completed but full experiment not run yet
    STOP("ERROR: Full experiment not executed. Return to Step 5B.")

# Only proceed if full experiment completed
checkpoint.current_step = 6
checkpoint.full_experiment_completed = True # Mark for Gate Processing verification
SAVE checkpoint
```

---

## ERROR HANDLING

🚨 **MANDATORY: Read `_references/error-handling-patterns.md`**

| Error | Action |
|-------|--------|
| pip install fails | Try conda → uv → pip3 → per-package |
| Import error | Search KB for package mapping |
| Runtime error | Quick Fix (5x) → Step 2 Escalation (1x) |
| GPU OOM | Reduce batch size, retry |
| Timeout | Kill process, mark as blocked |

---

## STEP COMPLETION

**Auto-proceed when ALL conditions met:**
1. ✅ **FULL** experiment executed (NOT smoke test) - `execution_plan.is_full_run == True`
2. ✅ Results saved to `{results_file}`
3. ✅ Checkpoint updated with `full_experiment_completed = True`
4. ✅ Experiment status is "completed" or "blocked" (not "smoke_test_passed")
5. ✅ Post-experiment mock data check completed
6. ✅ Reality Check evaluated (Section 3.5)
7. ✅ Training Sufficiency Check evaluated (Section 3.7)

🚨 **NEVER proceed to Step 6 if:**
- `execution_plan.is_full_run == False`
- `checkpoint.experiment_status == "smoke_test_passed"`
- Duration < 60 seconds without explicit verification

### UNATTENDED Conditional Auto-Proceed

Display: "**Routing based on post-validation results...**"

#### Menu Handling Logic:

**Routing Logic (use this, NOT ASCII diagrams):**

```python
# Step 5C → Next Step Decision
IF checkpoint.return_reason == "MOCK_MODEL_DETECTED":
    # Already routed in Section 3.5 - Reality Check failed
    # This case should not reach here (EXIT called)
    NEXT = "step-02-coder-loop.md"

ELIF checkpoint.return_reason == "TRAINING_INSUFFICIENT":
    # Already routed in Section 3.7 - Training Sufficiency failed
    # This case should not reach here (EXIT called)
    NEXT = "step-02-coder-loop.md"

ELIF step2_escalation_triggered:
    # Runtime error escalation
    NEXT = "step-02-coder-loop.md"

ELIF checkpoint.partial_results.experiment_status == "skipped":
    # Already handled in Section 1 Step 0, but backup check here
    NEXT = "step-05b-execution.md"

ELIF NOT execution_plan.is_full_run:
    # Smoke test only
    NEXT = "step-05b-execution.md"

ELSE:
    # FULL experiment completed (success or blocked)
    NEXT = "step-06-gate-processing.md"
```

Based on post-validation results, immediately load, read entire file, then execute ONE of the following:

| Condition | Action |
|-----------|--------|
| Reality Check FAILED (Section 3.5) | Already routed to `{coderStepFile}` (step-02) |
| Training Sufficiency FAILED (Section 3.7) | Already routed to `{coderStepFile}` (step-02) |
| Step 2 escalation triggered | Read and execute `{coderStepFile}` (step-02) |
| **Experiment SKIPPED** | Read and execute `{step5b}` (step-05b) - re-run experiment |
| Smoke test only (no full run) | Read and execute `{step5b}` (step-05b) |
| **FULL** experiment completed (success or blocked) | Read and execute `{nextStepFile}` (step-06) |

#### EXECUTION RULES:

- This is an UNATTENDED post-validation step with no user choices
- 🚨 **NEVER proceed to Step 6 with smoke test results, mock model, or insufficient training!**
- Route to appropriate step based on validation results
- **Failure to load next step = SYSTEM FAILURE**

---

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-06-gate-processing.md)
