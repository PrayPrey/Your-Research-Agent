---
name: 'checkpoint_helpers'
description: 'Reusable functions for 04_checkpoint.yaml management across Phase 4 steps'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions (11 functions)
exports:
  # Basic checkpoint operations
  - update_checkpoint
  - increment_retry
  - check_retry_limit
  - set_checkpoint_error
  - set_return_reason
  # Checkpoint-Verification State Sync
  - finalize_checkpoint_tasks
  - sync_checkpoint_from_verification_state
  - validate_checkpoint_verification_sync
  # Context Loss Recovery
  - detect_recovery_context
  - verify_archon_task_alignment
  # Validation Failure Handling
  - handle_validation_failure

# Called By
called_by:
  - 'phase4-coding/steps/step-01-initialize.md'
  - 'phase4-coding/steps/step-02-coder-loop.md'
  - 'phase4-coding/steps/step-03-validator.md'
  - 'phase4-coding/steps/step-05b-execution.md'
  - 'phase4-coding/steps/step-05c-post-validation.md'
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-08-completion.md'
---

# Checkpoint Helper Functions

> Reusable functions for 04_checkpoint.yaml management across Phase 4 steps.
> Reduces code duplication and ensures consistent checkpoint handling.

---

## Functions

### 1. update_checkpoint

```python
def update_checkpoint(checkpoint: dict, updates: dict, checkpoint_file: str, save: bool = True) -> dict:
    """
    Update checkpoint with multiple fields at once.

    Args:
        checkpoint: Current checkpoint dictionary
        updates: Dictionary of updates (supports nested keys with dot notation)
        checkpoint_file: Path to checkpoint file
        save: Whether to save immediately (default: True)

    Returns:
        Updated checkpoint dictionary

    Usage:
        update_checkpoint(checkpoint, {
            "current_step": 5,
            "experiment_status": "running",
            "partial_results.validation_passed": True
        }, checkpoint_file)
    """
    def set_nested(d, key, value):
        keys = key.split(".")
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    for key, value in updates.items():
        if "." in key:
            set_nested(checkpoint, key, value)
        else:
            checkpoint[key] = value

    checkpoint["updated_at"] = datetime.now().isoformat()

    if save:
        write_yaml(checkpoint_file, checkpoint)

    return checkpoint
```

### 2. increment_retry

```python
def increment_retry(checkpoint: dict, retry_type: str, checkpoint_file: str) -> int:
    """
    Increment a retry counter in checkpoint.

    Args:
        checkpoint: Current checkpoint dictionary
        retry_type: One of: "coder_validator_cycles", "mock_data_retries",
                    "mock_model_retries", "training_sufficiency_retries",
                    "quick_fix_attempts", "step2_retries"
        checkpoint_file: Path to checkpoint file

    Returns:
        New retry count
    """
    current = checkpoint.get(retry_type, 0)
    checkpoint[retry_type] = current + 1
    checkpoint["updated_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    return checkpoint[retry_type]

# Retry limit constants
RETRY_LIMITS = {
    "coder_validator_cycles": 5,
    "mock_data_retries": 3,
    "mock_model_retries": 3,
    "training_sufficiency_retries": 3,
    "quick_fix_attempts": 5,
    "step2_retries": 1,
    "task_retry_per_task": 3
}
```

### 3. check_retry_limit

```python
def check_retry_limit(checkpoint: dict, retry_type: str, max_retries: int) -> tuple:
    """
    Check if retry limit has been exceeded.

    Returns:
        Tuple of (is_exceeded: bool, current_count: int, max_count: int)
    """
    current = checkpoint.get(retry_type, 0)
    return (current >= max_retries, current, max_retries)
```

### 4. set_checkpoint_error

```python
def set_checkpoint_error(
    checkpoint: dict, step: str, task_id: str, message: str,
    checkpoint_file: str, error_type: str = None, traceback: str = None
) -> dict:
    """Record error information in checkpoint."""
    checkpoint["last_error"] = {
        "step": step, "task_id": task_id, "message": message,
        "error_type": error_type, "traceback": traceback,
        "timestamp": datetime.now().isoformat()
    }
    checkpoint["updated_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    return checkpoint
```

### 5. set_return_reason

```python
def set_return_reason(
    checkpoint: dict, checkpoint_file: str, reason: str,
    target_step: int, return_after: str = None
) -> dict:
    """Set return reason when routing back to earlier step."""
    checkpoint["return_reason"] = reason
    checkpoint["current_step"] = target_step
    if return_after:
        checkpoint["after_fix_goto"] = return_after
    checkpoint["updated_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    return checkpoint
```

---

## Checkpoint-Verification State Synchronization

### 6. finalize_checkpoint_tasks

```python
def finalize_checkpoint_tasks(
    checkpoint: dict, checkpoint_file: str, gate_result: str, gate_type: str = None
) -> dict:
    """
    Mark all checkpoint tasks as "done" after gate evaluation.
    Addresses sync gap where tasks remain in "review" after gate is satisfied.

    Usage:
        finalize_checkpoint_tasks(checkpoint, checkpoint_file, "PASS", "MUST_WORK")
    """
    tasks = checkpoint.get("tasks", {})
    task_items = tasks.get("items", [])

    finalized_count = 0
    for task in task_items:
        if task.get("status") in ["review", "doing"]:
            task["status"] = "done"
            task["gate_result"] = gate_result
            task["finalized_at"] = datetime.now().isoformat()
            finalized_count += 1

    tasks["summary"] = tasks.get("summary", {})
    tasks["summary"]["completed"] = len([t for t in task_items if t["status"] == "done"])
    tasks["summary"]["pending"] = len([t for t in task_items if t["status"] != "done"])

    checkpoint["finalization"] = {
        "gate_result": gate_result, "gate_type": gate_type,
        "tasks_finalized": finalized_count, "finalized_at": datetime.now().isoformat()
    }
    checkpoint["tasks"] = tasks
    checkpoint["updated_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    return checkpoint
```

### 7. sync_checkpoint_from_verification_state

```python
def sync_checkpoint_from_verification_state(
    checkpoint: dict, checkpoint_file: str, verification_state: dict, hypothesis_id: str
) -> dict:
    """
    Sync checkpoint fields from verification_state after gate processing.
    Ensures checkpoint reflects canonical state, preventing drift.

    Usage:
        sync_checkpoint_from_verification_state(checkpoint, checkpoint_file, verification_state, "h-e1")
    """
    h_data = verification_state.get("sub_hypotheses", {}).get(hypothesis_id, {})
    if not h_data:
        return checkpoint

    gate = h_data.get("gate", {})
    checkpoint["synced_from_verification_state"] = {
        "hypothesis_status": h_data.get("status"),
        "gate_type": gate.get("type"),
        "gate_satisfied": gate.get("satisfied"),
        "validation_status": h_data.get("validation", {}).get("status"),
        "synced_at": datetime.now().isoformat()
    }
    checkpoint["modification_attempt"] = h_data.get("modification_attempt", 0)

    h_status = h_data.get("status")
    if h_status in ["VALIDATED", "COMPLETED"]:
        checkpoint["hypothesis_validated"] = True
    elif h_status == "FAILED":
        checkpoint["hypothesis_failed"] = True
    elif h_status in ["SUPERSEDED", "CASCADE_SUPERSEDED"]:
        checkpoint["hypothesis_superseded"] = True

    checkpoint["updated_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    return checkpoint
```

### 8. validate_checkpoint_verification_sync

```python
def validate_checkpoint_verification_sync(
    checkpoint: dict, verification_state: dict, hypothesis_id: str
) -> dict:
    """
    Validate checkpoint and verification_state are in sync.
    Returns discrepancies that need resolution before archiving.

    Usage:
        sync_result = validate_checkpoint_verification_sync(checkpoint, verification_state, "h-e1")
        if not sync_result["synced"]:
            sync_checkpoint_from_verification_state(...)
    """
    discrepancies = []
    h_data = verification_state.get("sub_hypotheses", {}).get(hypothesis_id, {})

    if not h_data:
        return {"synced": False, "discrepancies": [f"Hypothesis {hypothesis_id} not found"], "recommendations": []}

    # Check gate result consistency
    cp_gate = checkpoint.get("partial_results", {}).get("gate_result")
    vs_gate = h_data.get("gate", {}).get("satisfied")
    if cp_gate and vs_gate != (cp_gate == "PASS"):
        discrepancies.append({"field": "gate.satisfied", "checkpoint": cp_gate, "verification_state": vs_gate})

    # Check modification attempt
    cp_mod = checkpoint.get("modification_attempt", 0)
    vs_mod = h_data.get("modification_attempt", 0)
    if cp_mod != vs_mod:
        discrepancies.append({"field": "modification_attempt", "checkpoint": cp_mod, "verification_state": vs_mod})

    return {"synced": len(discrepancies) == 0, "discrepancies": discrepancies, "recommendations": []}
```

---

## Context Loss Recovery

> Use `detect_recovery_context()` INSTEAD OF `find_tasks(status="doing")` for session recovery.
> Option B creates multiple "doing" tasks (Pipeline + [H-XX] + Step tasks).

### 9. detect_recovery_context

```python
def detect_recovery_context(verification_state_path: str, hypothesis_folder: str = None) -> dict:
    """
    Detect recovery context after context loss using cached task IDs.

    Returns:
        - success, hypothesis_id, current_phase, current_step
        - hypothesis_phase_task_id, pipeline_project_id
        - checkpoint, resume_step_file, error

    """
    try:
        verification_state = read_yaml(verification_state_path)
        if not verification_state:
            return {"success": False, "error": "verification_state.yaml not found"}

        # Find IN_PROGRESS hypothesis
        hypotheses = verification_state.get("hypotheses", {})
        hypothesis_id = None
        current_hypothesis = None

        for h_id, h_data in hypotheses.items():
            if h_data.get("status") == "IN_PROGRESS":
                hypothesis_id = h_id
                current_hypothesis = h_data
                break

        if not hypothesis_id:
            ready = [h for h, d in hypotheses.items() if d.get("status") == "READY"]
            if ready:
                return {"success": True, "hypothesis_id": None, "resume_action": "START_NEXT_HYPOTHESIS", "ready_hypotheses": ready, "error": None}
            return {"success": False, "error": "No IN_PROGRESS or READY hypotheses"}

        # Determine current phase
        validation = current_hypothesis.get("validation", {})
        impl = current_hypothesis.get("implementation_planning", {})
        exp = current_hypothesis.get("experiment_design", {})

        if validation.get("status") == "IN_PROGRESS":
            current_phase = "Phase 4"
        elif impl.get("status") == "IN_PROGRESS":
            current_phase = "Phase 3"
        else:
            current_phase = "Phase 2C"

        # Read checkpoint
        if hypothesis_folder is None:
            research_folder = verification_state_path.replace("/verification_state.yaml", "")
            hypothesis_folder = f"{research_folder}/{hypothesis_id.lower()}"

        checkpoint = None
        current_step = 1

        try:
            checkpoint = read_yaml(f"{hypothesis_folder}/04_checkpoint.yaml")
            if checkpoint:
                current_step = checkpoint.get("current_step", 1)
        except:
            pass

        # Get cached task IDs (Option B)
        metadata = verification_state.get("metadata", {})
        h_tasks = metadata.get("hypothesis_phase_tasks", {}).get(hypothesis_id.lower(), {})

        step_file_map = {
            1: "step-01-initialize.md", 2: "step-02-coder-loop.md",
            3: "step-03-validator.md", 4: "step-04-experiment-confirm.md",
            5: "step-05b-execution.md", 6: "step-06-gate-processing.md",
            7: "step-07-report-generation.md", 8: "step-08-completion.md"
        }

        return {
            "success": True,
            "hypothesis_id": hypothesis_id,
            "current_phase": current_phase,
            "current_step": current_step,
            "hypothesis_phase_task_id": h_tasks.get(current_phase),
            "pipeline_project_id": metadata.get("pipeline_project_id"),
            "checkpoint": checkpoint,
            "resume_step_file": step_file_map.get(current_step, "step-01-initialize.md"),
            "hypothesis_folder": hypothesis_folder,
            "error": None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 10. verify_archon_task_alignment

```python
def verify_archon_task_alignment(recovery_context: dict) -> dict:
    """
    Verify cached task IDs match Archon state using direct task_id lookup.

    Usage:
        recovery = detect_recovery_context(path)
        alignment = verify_archon_task_alignment(recovery)
        if not alignment["aligned"]:
            print(f"Discrepancies: {alignment['discrepancies']}")

    """
    discrepancies = []
    phase_task_status = None

    # Verify phase task
    phase_task_id = recovery_context.get("hypothesis_phase_task_id")
    if phase_task_id:
        response = mcp__archon__find_tasks(task_id=phase_task_id)
        if response.get("success") and response.get("tasks"):
            phase_task_status = response["tasks"][0].get("status")
            if phase_task_status != "doing":
                discrepancies.append({"type": "phase_task", "task_id": phase_task_id, "expected": "doing", "actual": phase_task_status})
        else:
            discrepancies.append({"type": "phase_task", "task_id": phase_task_id, "error": "Not found"})

    return {"aligned": len(discrepancies) == 0, "phase_task_status": phase_task_status, "discrepancies": discrepancies}
```

---

## Usage Example

```python
# Post-validation failure handling (step-05c) - using handle_validation_failure
from checkpoint_helpers import update_checkpoint, handle_validation_failure

failure = handle_validation_failure(
    checkpoint, checkpoint_file, results,
    retry_type="mock_data_retries", max_retries=3,
    blocked_field="mock_data_blocked",
    status_field="mock_data_status",
    results_key="mock_data_detection",
    detection_result=mock_result,
    fix_task_id_prefix="fix-mock-",
    fix_task_title="[POST-CHECK MOCK FIX] Remove mock data usage",
    fix_task_description="...",
    fix_task_source="step-05c-mock-detection",
    return_reason="MOCK_DATA_DETECTED"
)
if failure["action"] == "ROUTE_TO_STEP2":
    # Load and execute step-02-coder-loop.md
    pass
# else: BLOCKED → continue to Step 6
```

---

## Validation Failure Handling

### 11. handle_validation_failure

```python
def handle_validation_failure(
    checkpoint: dict,
    checkpoint_file: str,
    results: dict,
    retry_type: str,
    max_retries: int,
    blocked_field: str,
    status_field: str,
    results_key: str,
    detection_result: dict,
    fix_task_id_prefix: str,
    fix_task_title: str,
    fix_task_description: str,
    fix_task_source: str,
    return_reason: str
) -> dict:
    """
    Shared handler for post-validation failure escalation (Section 3, 3.5, 3.7).

    Implements the common pattern:
    1. Check retry limit
    2. If exceeded → mark BLOCKED, continue to Step 6
    3. If not exceeded → increment retry, create fix task, route to Step 2

    Args:
        checkpoint: Current checkpoint dictionary
        checkpoint_file: Path to checkpoint file
        results: Experiment results dict (to store detection result)
        retry_type: Checkpoint retry counter field name (e.g., "mock_data_retries")
        max_retries: Maximum retry attempts (typically 3)
        blocked_field: Checkpoint field to set when blocked (e.g., "mock_data_blocked")
        status_field: Checkpoint field for status (e.g., "mock_data_status")
        results_key: Key in results dict to store detection (e.g., "mock_data_detection")
        detection_result: The detection/verification result dict
        fix_task_id_prefix: Prefix for fix task ID (e.g., "fix-mock-")
        fix_task_title: Title for the fix task
        fix_task_description: Description for the fix task
        fix_task_source: Source identifier (e.g., "step-05c-mock-detection")
        return_reason: Reason string for set_return_reason (e.g., "MOCK_DATA_DETECTED")

    Returns:
        Dictionary containing:
            - action: str - "BLOCKED" (continue to Step 6) or "ROUTE_TO_STEP2" (EXIT needed)
            - exceeded: bool - Whether retry limit was exceeded
            - current: int - Current retry count
            - max_count: int - Maximum retry count

    Usage:
        result = handle_validation_failure(
            checkpoint, checkpoint_file, results,
            retry_type="mock_data_retries", max_retries=3,
            blocked_field="mock_data_blocked",
            status_field="mock_data_status",
            results_key="mock_data_detection",
            detection_result=mock_result,
            fix_task_id_prefix="fix-mock-",
            fix_task_title="[POST-CHECK MOCK FIX] Remove mock data usage",
            fix_task_description="...",
            fix_task_source="step-05c-mock-detection",
            return_reason="MOCK_DATA_DETECTED"
        )
        if result["action"] == "ROUTE_TO_STEP2":
            Load, read entire file, then execute: {coderStepFile}
            EXIT
    """
    exceeded, current, max_count = check_retry_limit(checkpoint, retry_type, max_retries)

    if exceeded:
        print(f"🚨 Max {retry_type} ({max_count}) exceeded - marking as BLOCKED")
        update_checkpoint(checkpoint, {
            blocked_field: True,
            status_field: "BLOCKED_MAX_RETRIES"
        }, checkpoint_file)
        results[results_key] = detection_result

        return {
            "action": "BLOCKED",
            "exceeded": True,
            "current": current,
            "max_count": max_count
        }

    else:
        increment_retry(checkpoint, retry_type, checkpoint_file)

        fix_task = {
            "id": f"{fix_task_id_prefix}{str(uuid4())[:8]}",
            "title": fix_task_title,
            "description": fix_task_description,
            "status": "todo",
            "priority": 100,
            "created_at": now(),
            "source": fix_task_source
        }
        checkpoint["tasks"]["items"].append(fix_task)
        checkpoint["tasks"]["summary"]["remaining"] += 1

        set_return_reason(checkpoint, checkpoint_file,
                         reason=return_reason, target_step=2)

        print(f"🔄 Returning to Step 2 (attempt {current+1}/{max_count})")

        return {
            "action": "ROUTE_TO_STEP2",
            "exceeded": False,
            "current": current,
            "max_count": max_count
        }
```

---

## Integration Notes

1. **Import in step files**: Reference helper functions in pseudo-code
2. **Consistent timestamps**: All functions use ISO8601 format
3. **Auto-save**: Most functions save immediately (pass `save=False` to batch)
4. ** Sync**: Use `finalize_checkpoint_tasks()` in step-06, `validate_checkpoint_verification_sync()` before step-08
5. ** Recovery**: Use `detect_recovery_context()` instead of `find_tasks(status="doing")` - Option B compatible
