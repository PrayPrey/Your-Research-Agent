---
name: 'step-06-gate-processing'
description: 'Gate Processing - Evaluate experiment results and route based on gate type'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# File References
thisStepFile: '{workflow_path}/steps/step-06-gate-processing.md'
reflectionStepFile: '{workflow_path}/steps/step-06b-reflection.md'
nextStepFile: '{workflow_path}/steps/step-07-report-generation.md'
workflowFile: '{workflow_path}/workflow.md'

# Helper References
gate_evaluation: '{helpers_path}/gate_evaluation.md'
checkpoint_helpers: '{helpers_path}/checkpoint_helpers.md'
archon_cascade: '{helpers_path}/archon_cascade.md'

# Input Files
verification_state: '{research_folder}/verification_state.yaml'
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
results_file: '{hypothesis_folder}/experiment_results.json'
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 6:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, experiment_status={checkpoint.experiment_status}")
```

---

## Section 0.6: Pre-Gate Experiment Verification

**Check `checkpoint.partial_results.experiment_status` and judge:**

- If `"skipped"` → Experiment was skipped (Step 5C detected this)
- If `"pending"` → Experiment never started
- If `"completed"` or contains actual results → OK to proceed

**Your judgment:**

1. **If experiment_status is "skipped" or "pending":**

   ```python
   skip_retry_count = checkpoint.get("experiment_skip_retries", 0)
   max_skip_retries = 4 # 4 retries before FAIL

   IF skip_retry_count < max_skip_retries:
       # Route to Step 5B for re-execution
       checkpoint.experiment_skip_retries = skip_retry_count + 1
       SAVE checkpoint
       print(f"🔄 Experiment skipped - routing to Step 5B for re-execution (attempt {skip_retry_count + 1}/{max_skip_retries})")
       Load, read entire file, then execute: step-05b-execution.md
       EXIT

   ELSE:
       # Max retries (4+) reached - FAIL the gate → triggers ROUTE_TO_0
       print(f"🚨 Experiment skip max retries ({max_skip_retries}) reached - marking as FAIL")
       gate_result = "FAIL"
       gate_failure_reason = "Experiment did not run after 4 retry attempts"
       # Continue to FAIL path → reflection → ROUTE_TO_0 for MUST_WORK gates
   ```

2. **If experiment_status is "completed" or has valid results:**
   - Print: "✅ Experiment execution verified - proceeding to gate evaluation"
   - Continue to Section 1

---

# Step 6: Gate Processing (UNATTENDED Mode)

> **Mode:** UNATTENDED | **Purpose:** Evaluate results, route based on gate type

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- Evaluate experiment results against gate criteria
- Route based on gate type (MUST_WORK, SHOULD_WORK; DETERMINES_SUCCESS is Phase 5 only)
- Handle PARTIAL results with reflection if needed
- Update verification_state.yaml with gate results

---

### 📖 File Information:
- 📏 Total length: ~486 lines (under 2000 lines)
- 📂 Read entire file before execution

**Required Reading Method**:
```python
# ✅ Correct Method (Recommended)
Read(file_path="{thisStepFile}") # Without limit/offset parameters

# ❌ Incorrect Method (Prohibited)
Read(file_path="{thisStepFile}", offset=0, limit=200) # Partial reading
Read(file_path="{thisStepFile}", offset=200, limit=200)
```

**⚠️ Critical Warning**: Read the entire file before execution.

---

## STEP GOAL

Evaluate experiment results against gate criteria and route appropriately.

---

## GATE TYPES

| Type | On PASS | On PARTIAL | On FAIL | Reflection? |
|------|---------|------------|---------|-------------|
| `MUST_WORK` | Phase 5 | Route to Phase 2A-Dialogue | Route to Phase 0 | Yes (may route) |
| `SHOULD_WORK` | Phase 5 | Self-recovery (up to 3x) | Self-recovery (up to 3x) | **Yes (self-recovery only)** |

> - Up to 3 self-recovery attempts allowed
> - Does NOT route to Phase 0/2A (optional gate)
> - After max retries → records limitation and continues to Phase 5

> Reflection may result in SUPERSEDED status (hypothesis redesign needed) vs SELF_MODIFY.

> 📖 **Detailed gate logic:** `{gate_evaluation}`

---

## MANDATORY RULES

| Rule | Requirement |
|------|-------------|
| Read from CENTRAL | `{verification_state}` at `{research_folder}/` |
| Read-Modify-Write | For all verification_state updates |
| Evaluate ALL criteria | Before determining result |
| Route correctly | Based on gate type and result |

---

## EXECUTION SEQUENCE

### 1. Load Gate Configuration

```python
verification_state = read_yaml("{research_folder}/verification_state.yaml")
hypothesis_data = verification_state["hypotheses"][hypothesis_id]
gate_config = hypothesis_data["gate"]
results = read_json(results_file)
```

### 1b. Verify Checkpoint Completion

```python
# checkpoint already loaded in Section 0.5 (context loss prevention)

# Verify all tasks are in "review" or "done" status
tasks = checkpoint.get("tasks", {}).get("items", [])
incomplete_tasks = [t for t in tasks if t["status"] not in ["review", "done"]]

IF len(incomplete_tasks) > 0:
    # Tasks still pending - should not reach gate processing
    raise ValueError(f"Gate processing called with {len(incomplete_tasks)} incomplete tasks")

# Get checkpoint summary for gate evaluation context
task_summary = {
    "total": checkpoint["tasks"]["summary"]["total"],
    "completed": checkpoint["tasks"]["summary"]["completed"],
    "validation_errors": len([t for t in tasks if t.get("validation_error")]),
    "sdd_phases": checkpoint.get("sdd_phases", {})
}
```

### 2. Handle Skip/Failed Execution

```python
IF results.status == "skipped":
    gate_result = "INCOMPLETE" if code_quality_ok else "FAIL"
IF results.status == "failed":
    gate_result = "FAIL"
```

### 3. Mechanism Activation Verification

> 📖 **Reference:** `_references/mechanism-verification-guide.md`

```python
# Load mechanism protocol from 02c_experiment_brief.md
mechanism_protocol = extract_section("Mechanism Verification Protocol")
experiment_log = Read("{code_folder}/experiment.log")

mechanism_check = verify_mechanism_activation(
    protocol=mechanism_protocol,
    log=experiment_log,
    metrics=results.metrics
)

# CRITICAL: Mechanism failure overrides metric-based result!
IF NOT mechanism_check.activated:
    gate_result = "FAIL"
    gate_failure_reason = f"MECHANISM_NOT_ACTIVATED: {mechanism_check.failure_reason}"
    checkpoint.mechanism_verification = mechanism_check
    SAVE checkpoint
```

### 4. Evaluate Gate Criteria

> 📖 **Reference:** `{gate_evaluation}` - calculate_pass_rate(), evaluate_gate()

```python
from gate_evaluation import calculate_pass_rate, evaluate_gate

# Evaluate each criterion
validation_results = []
FOR criterion in gate.criteria:
    passed = evaluate_criterion(results.metrics[criterion.metric], criterion.operator, criterion.value)
    validation_results.append({
        "name": criterion.metric,
        "passed": passed,
        "critical": criterion.get("critical", False),
        "actual": results.metrics[criterion.metric],
        "target": criterion.value
    })

# Calculate summary
validation_summary = calculate_pass_rate(validation_results)

# Determine gate result
gate_result_obj = evaluate_gate(gate.type, validation_summary)
gate_result = gate_result_obj["outcome"] # PASS, PARTIAL, FAIL
gate_satisfied = gate_result_obj["satisfied"] # bool
gate_action = gate_result_obj["action"] # proceed_to_phase5, route_to_phase0, etc.
```

### 5. Check Reflection Trigger

```python
# After self-recovery retries exhaust, LLM decides: SELF_MODIFY (Phase 2C) or FAIL (record limitation)

# MUST_WORK: Reflection triggers routing (Phase 0/2A)
# SHOULD_WORK: Self-recovery first, then LLM assessment for SELF_MODIFY option
IF gate_result in ["PARTIAL", "FAIL"]:

    IF gate.type == "MUST_WORK":
        # MUST_WORK: Standard reflection → may route to Phase 0/2A
        reflection_needed = True
        checkpoint.reflection_may_route = True # Can route to Phase 0/2A

    ELIF gate.type == "SHOULD_WORK":

        should_work_retry_count = checkpoint.get("should_work_retry_count", 0)
        max_retries = GATE_TYPES["SHOULD_WORK"]["max_retries"] # 3

        IF should_work_retry_count < max_retries:
            # First: Attempt self-recovery via reflection (existing behavior)
            reflection_needed = True
            checkpoint.reflection_may_route = False # Cannot route to Phase 0/2A
            checkpoint.should_work_retry_count = should_work_retry_count + 1
            checkpoint.reflection_type = "self_recovery"
            print(f"SHOULD_WORK PARTIAL - attempting self-recovery ({should_work_retry_count + 1}/{max_retries})")

        ELSE:

            # LLM decides: SELF_MODIFY (route to Phase 2C) or FAIL (record limitation)
            IF GATE_TYPES["SHOULD_WORK"].get("llm_assessment_available", False):
                reflection_needed = True
                checkpoint.reflection_may_route = True # Can route to Phase 2C (not 0/2A)
                checkpoint.reflection_type = "llm_assessment_should_work"
                checkpoint.allow_phase2c_route = True # NEW: Can route to Phase 2C
                print(f"SHOULD_WORK max retries reached - triggering LLM assessment for SELF_MODIFY decision")
            ELSE:
                # Fallback: Record limitation and continue (original behavior)
                reflection_needed = False
                checkpoint.should_work_failed = True
                checkpoint.limitation_note = f"{hypothesis_id}: SHOULD_WORK gate failed after {max_retries} self-recovery attempts"
                checkpoint.should_work_limitation_recorded = True
                print(f"SHOULD_WORK max retries reached - recording limitation, continuing to Phase 5")

    # Note: DETERMINES_SUCCESS is Phase 5 only (not used in Phase 4)
    # If an unexpected gate type appears, treat as reflection-needed
    ELSE:
        reflection_needed = True
        checkpoint.reflection_may_route = True

ELSE:
    reflection_needed = False

IF reflection_needed AND checkpoint.modification_attempt < 3:
    checkpoint.reflection_pending = True
    checkpoint.next_step_after_report = "step-06b-reflection.md"
```

### 6. Update Verification State

> 📖 **Reference:** `{gate_evaluation}` - update_gate_status()

```python
from gate_evaluation import update_gate_status

verification_state = update_gate_status(
    verification_state, hypothesis_id, gate_result_obj, verification_state_path
)

# Log status history if MUST_WORK failure
IF NOT gate_satisfied AND gate.type == "MUST_WORK":
    verification_state["status_history"].append({
        "status": "STOPPED",
        "phase": "Phase 4",
        "trigger": "Gate violation",
        "hypothesis_id": hypothesis_id,
        "gate_result": gate_result
    })
    write_yaml(verification_state_path, verification_state)
```

### 7. Handle Cascade (If Failure)

> 📖 **Reference:** `{archon_cascade}`

```python
IF gate_result in ["FAIL", "PARTIAL"]:
    from archon_cascade import find_dependent_hypotheses, update_verification_state_cascade

    dependents = find_dependent_hypotheses(verification_state, hypothesis_id)

    IF len(dependents) > 0:
        IF gate_result == "FAIL":
            # CASCADE_FAILED
            update_verification_state_cascade(verification_state, "FAILED", hypothesis_id, dependents)
        ELIF gate_result == "PARTIAL":
            # BLOCKED
            update_verification_state_cascade(verification_state, "MODIFIED", hypothesis_id, dependents)

        write_yaml(verification_state_path, verification_state)
```

### 8. Update Checkpoint & Route

> 📖 **Reference:** `{checkpoint_helpers}`

```python
from checkpoint_helpers import update_checkpoint

update_checkpoint(checkpoint, {
    "current_step": 6,
    "partial_results.gate_result": gate_result,
    "partial_results.gate_type": gate.type
}, checkpoint_file)
```

### 8b. Update Hypothesis Task in Archon

> Implementation tasks are tracked locally in `04_checkpoint.yaml`.

```python
# Get Hypothesis Task ID from verification_state
hypothesis_task_id = verification_state.get("metadata", {}).get("hypothesis_task_mapping", {}).get(hypothesis_id)

IF hypothesis_task_id:
    # Determine Archon task status based on gate result
    IF gate_result == "PASS":
        archon_status = "done" # Phase 4 complete, validated for Phase 5
        title_prefix = "[VALIDATED] "
    ELIF gate_result == "PARTIAL":
        archon_status = "review" # Pending reflection decision
        title_prefix = "[PARTIAL] "
    ELSE: # FAIL
        archon_status = "review" # Failed, pending reroute
        title_prefix = "[FAILED] "

    # Get current task to preserve title
    current_task = mcp__archon__find_tasks(task_id=hypothesis_task_id)
    current_title = current_task.get("title", hypothesis_id)

    # Remove existing prefix if present (e.g., "[PARTIAL] ", "[FAILED] ")
    for prefix in ["[VALIDATED] ", "[PARTIAL] ", "[FAILED] "]:
        if current_title.startswith(prefix):
            current_title = current_title[len(prefix):]
            break

    # Apply new title prefix
    new_title = f"{title_prefix}{current_title}"

    # Update Hypothesis Task in Archon (ONLY this task, not implementation tasks)
    mcp__archon__manage_task(
        action="update",
        task_id=hypothesis_task_id,
        status=archon_status,
        title=new_title,
        description=f"Gate Result: {gate_result}\nReason: {gate_result_obj['reason']}"
    )

    checkpoint.archon.hypothesis_task_updated = True
    checkpoint.archon.hypothesis_task_status = archon_status
    SAVE checkpoint
ELSE:
    # Log warning - Hypothesis Task not found
    print(f"⚠ Hypothesis Task ID not found for {hypothesis_id}")
    checkpoint.archon.hypothesis_task_updated = False
    SAVE checkpoint
```

### 8c. Checkpoint-Verification State Synchronization

> This addresses the gap where checkpoint tasks remain in "review" status after gate is satisfied.

```python
from checkpoint_helpers import finalize_checkpoint_tasks, sync_checkpoint_from_verification_state

# 1. Finalize all checkpoint tasks based on gate result
finalize_checkpoint_tasks(
    checkpoint,
    checkpoint_file,
    gate_result=gate_result,
    gate_type=gate.type
)
print(f"✓ Checkpoint tasks finalized with gate result: {gate_result}")

# 2. Sync checkpoint from verification_state (canonical source)
sync_checkpoint_from_verification_state(
    checkpoint,
    checkpoint_file,
    verification_state,
    hypothesis_id
)
print(f"✓ Checkpoint synced from verification_state")
```

---

## 9. PROCEED TO NEXT STEP

### UNATTENDED Conditional Auto-Proceed

Display: "**Routing based on gate result...**"

#### Menu Handling Logic:

Based on gate evaluation result, immediately load, read entire file, then execute ONE of the following:

| Condition | Next Step |
|-----------|-----------|
| PASS | `{nextStepFile}` (step-07) |
| FAIL/PARTIAL + reflection_pending | `{reflectionStepFile}` (step-06b) |
| SHOULD_WORK failure | `{nextStepFile}` (step-07 with limitation) |

#### EXECUTION RULES:

- This is an UNATTENDED gate processing step with no user choices
- Route to appropriate step based on gate result
- **Failure to load next step = SYSTEM FAILURE**

---

## ROUTING SUMMARY

| Gate Result | Gate Type | Next Step | Reflection? | Possible Outcomes |
|-------------|-----------|-----------|-------------|-------------------|
| PASS | Any | Step 7 | No | → Phase 5 |
| FAIL | MUST_WORK | Step 6b | Yes | → Phase 0 |
| PARTIAL | MUST_WORK | Step 6b | Yes | → SUPERSEDED or SELF_MODIFY |
| FAIL/PARTIAL | SHOULD_WORK (retry < 3) | Step 6b | Yes | → Self-recovery (re-run validation) |
| FAIL/PARTIAL | SHOULD_WORK (retry ≥ 3) | Step 6b | **Yes** | → **LLM: SELF_MODIFY or FAIL** |
| ~~FAIL/PARTIAL~~ | ~~DETERMINES_SUCCESS~~ | ~~Step 6b~~ | — | *Moved to Phase 5* |

> - Up to 3 retry attempts via reflection (self_recovery)
> - After max retries → **LLM assessment** (llm_assessment_should_work)
> - LLM decides: **SELF_MODIFY** (route to Phase 2C) or **FAIL** (record limitation)
> - Does NOT route to Phase 0/2A (optional gate)

> - **SELF_MODIFY**: Minor issues, can retry within hypothesis
> - **SUPERSEDED**: Fundamental issues, hypothesis needs redesign → Phase 2A-Dialogue with new hypothesis ID

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| verification_state not found | Create with defaults |
| Invalid gate type | Default to SHOULD_WORK |
| Missing metric | Mark criterion as UNKNOWN |
| Write fails | Retry 3 times |
| Checkpoint incomplete | Log error, halt gate processing |
| Hypothesis Task ID missing | Log warning, continue without Archon update |
| Archon MCP call fails | Log warning, continue (checkpoint is source of truth) |

> Archon Hypothesis Task update is informational; failure does not block pipeline.
