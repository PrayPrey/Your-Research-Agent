---
name: 'step-01b-continue'
description: 'Resume Phase 4 workflow from existing checkpoint'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-01b-continue.md'
workflowFile: '{workflow_path}/workflow.md'

# Step Files for Resume
step1a: '{workflow_path}/steps/step-01a-data-setup.md'
step2: '{workflow_path}/steps/step-02-coder-loop.md'
step3: '{workflow_path}/steps/step-03-validator.md'
step4: '{workflow_path}/steps/step-04-experiment-confirm.md'
step5a: '{workflow_path}/steps/step-05a-pre-validation.md'
step5b: '{workflow_path}/steps/step-05b-execution.md'
step5c: '{workflow_path}/steps/step-05c-post-validation.md'
step6: '{workflow_path}/steps/step-06-gate-processing.md'
step7: '{workflow_path}/steps/step-07-report-generation.md'
step8: '{workflow_path}/steps/step-08-completion.md'

# Checkpoint File
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
---

# Step 1b: Resume from Checkpoint (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## STEP GOAL

Resume Phase 4 workflow from existing checkpoint, restoring state and continuing from last saved position.

---

## EXECUTION SEQUENCE

### 1. Load Checkpoint

```python
checkpoint = read_yaml(checkpoint_file)

# Key fields to restore:
# - current_step: {1-8}
# - current_task_id: "{task-uuid|null}"
# - tasks: {total, completed, in_progress, remaining}
# - coder_validator_cycles: {int}
# - task_retry_counts: {task-id: count}
# - partial_results: {code_files_generated, validation_passed, experiment_status}
# - last_error: {...}
# - unattended_mode: {bool}
# - error_escalation: {quick_fix_attempts, step2_retries, ...}
# - return_to_step5_after_coder: {bool}
```

### 2. Verify Current State (Local Checkpoint)

> Only Step-Level Tasks (4-01, 4-02, etc.) remain in Archon.

```python
tasks = checkpoint.tasks.items

# Count task statuses
done_count = len([t for t in tasks if t["status"] == "done"])
review_count = len([t for t in tasks if t["status"] == "review"])
todo_count = len([t for t in tasks if t["status"] == "todo"])

# Verify counts match checkpoint.tasks summary
IF checkpoint.tasks.completed != done_count:
    checkpoint.tasks.completed = done_count
IF checkpoint.tasks.remaining != (review_count + todo_count):
    checkpoint.tasks.remaining = review_count + todo_count

# Check Generated Files
FOR file in checkpoint.partial_results.code_files_generated:
    IF NOT exists(file):
        Add to re_generation_list
```

### 3. Handle State Inconsistencies (Auto)

```python
IF count_mismatch:
    # Counts already corrected in Section 2
    SAVE checkpoint

IF file_missing:
    # Mark related task for redo
    FOR task in tasks:
        IF task["target_file"] in re_generation_list:
            task["status"] = "todo"
            task["validation_error"] = "File missing - needs regeneration"
    SAVE checkpoint
```

### 4. Check Retry Limits

```python
IF checkpoint.coder_validator_cycles >= 5:
    # Max cycles reached - skip to experiment
    target_step = 4

IF task_retry_counts[current_task_id] >= 3:
    # Max retries - skip this task
    skip_task(current_task_id)
```

### 5. Determine Resume Point

```python
target_step = checkpoint.current_step

# Check if data setup was interrupted
IF checkpoint.data_setup.status == "pending" OR checkpoint.data_setup.status == "failed":
    # Need to run/re-run data setup first
    target_file = step1_5
    print("📦 Resuming from data setup...")

ELSE:
    step_files = {
        2: step2, # Coder Loop
        3: step3, # Validator
        4: step4, # Experiment Confirm
        5: step5a, # Pre-validation (was step5)
        6: step6, # Gate Processing
        7: step7, # Report Generation
        8: step8 # Completion
    }

    target_file = step_files.get(target_step, step2)
```

### 6. Restore Context Variables

```python
hypothesis_id = checkpoint.hypothesis_id
archon_project_id = checkpoint.archon.project_id
hypothesis_feature = checkpoint.archon.get("hypothesis_feature") # 
pipeline_mode = checkpoint.archon.get("pipeline_mode", False) # 
unattended_mode = checkpoint.unattended_mode
coder_validator_cycles = checkpoint.coder_validator_cycles
task_retry_counts = checkpoint.task_retry_counts
conda_env_name = checkpoint.conda.env_name # For validation/execution
conda_path = checkpoint.conda.conda_path # For conda activation
```

### 7. Resume Workflow

```python
checkpoint.updated_at = now()
SAVE checkpoint

# Load and execute target step
Load, read entire file, then execute: {target_file}
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Checkpoint corrupted | Delete and restart from step-01 |
| Step file not found | Log error, stop |
| Count mismatch | Auto-correct from task items |
| File missing | Mark related task for regeneration |

---

## STEP COMPLETION

**Resume routing:**

| Condition | Target File |
|-----------|-------------|
| `data_setup.status == "pending"` | step-01a-data-setup.md |
| `data_setup.status == "failed"` | step-01a-data-setup.md |
| `current_step == 2` | step-02-coder-loop.md |
| `current_step == 3` | step-03-validator.md |
| `current_step == 4` | step-04-experiment-confirm.md |
| `current_step == 5` | step-05a-pre-validation.md |
| `current_step == 6` | step-06-gate-processing.md |
| `current_step == 7` | step-07-report-generation.md |
| `current_step == 8` | step-08-completion.md |

**On completion:** Load, read entire file, then execute target step file.
