---
name: 'step-04-loop-start'
description: 'Loop entry - Gate validation, status update, and Archon task creation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-04-loop-start.md'
nextStepFile: '{workflow_path}/steps/step-05-phase-2c.md'
workflowFile: '{workflow_path}/workflow.md'

# Helper References
archon_hypothesis_phase_helper: '{workflow_path}/helpers/archon_hypothesis_phase.md'
---

# Step 4: Loop Start - Gate Validation & Status Update

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Entry point for the hypothesis loop. For the current hypothesis:
1. Re-check execution mode (context loss prevention)
2. Validate prerequisite gates
3. Update status to IN_PROGRESS
4. Get or create Archon Phase Tasks

## MANDATORY EXECUTION RULES

<critical>
**UNATTENDED MODE CHECK (MANDATORY AT EVERY HYPOTHESIS TRANSITION)**

Before processing each hypothesis, RE-READ execution_mode from verification_state.yaml:
```python
state = load_yaml(verification_state_file)
execution_mode = "AUTO" if state.workflow.execution_mode == "UNATTENDED" else execution_mode
```
This prevents "forgetting" the mode during long workflow execution.
</critical>

---

## EXECUTION SEQUENCE

### 1. Re-Read Execution Mode (Context Loss Prevention)

```python
# MANDATORY: Re-read from verification_state.yaml at EVERY hypothesis transition
state = load_yaml(verification_state_file)
is_unattended = (state.workflow.execution_mode == "UNATTENDED")

IF is_unattended:
    execution_mode = "AUTO"
    display: "🤖 Confirmed: UNATTENDED mode active"
```

### 2. Get Current Hypothesis

```python
hypothesis_id = hypothesis_queue[current_hypothesis_index]
hypothesis = state.sub_hypotheses[hypothesis_id]
hypothesis_folder = f"{research_folder}/{hypothesis_id.lower()}"

display: f"""
🔬 **Processing: {hypothesis_id}**
   Type: {hypothesis.type}
   Gate: {hypothesis.gate.type}
   Prerequisites: {hypothesis.get('prerequisites', [])}
"""
```

### 3. Validate Prerequisite Gates

```python
def validate_prerequisites(hypothesis_id, state):
    """Check all prerequisites are satisfied."""
    result = {
        "valid": True,
        "has_must_pass_failure": False,
        "has_should_pass_failure": False,
        "failed_prerequisite": None,
        "limitation_files": []
    }

    hypothesis = state.sub_hypotheses[hypothesis_id]
    for prereq_id in hypothesis.get("prerequisites", []):
        prereq = state.sub_hypotheses.get(prereq_id)

        IF NOT prereq OR prereq.status NOT IN ["COMPLETED", "VALIDATED"]:
            result["valid"] = False
            result["failed_prerequisite"] = prereq_id
            display: f"❌ Prerequisite {prereq_id} not completed"
            CONTINUE

        IF prereq.gate.type == "MUST_WORK" AND NOT prereq.gate.satisfied:
            result["has_must_pass_failure"] = True
            result["failed_prerequisite"] = prereq_id

        ELIF prereq.gate.type == "SHOULD_WORK" AND NOT prereq.gate.satisfied:
            result["has_should_pass_failure"] = True
            result["limitation_files"].append(f"{prereq_id.lower()}/04_validation.md")

    return result

gate_result = validate_prerequisites(hypothesis_id, state)
```

### 4. Handle Gate Failures

```python
IF gate_result["has_must_pass_failure"]:
    failed = gate_result["failed_prerequisite"]
    display: f"""
🛑 **MUST_WORK Gate Failed:** {failed}
   → {hypothesis_id} is BLOCKED

Updating workflow status to STOPPED...
"""
    state.sub_hypotheses[hypothesis_id].status = "BLOCKED"
    state.workflow.status = "STOPPED"
    state.workflow.stop_reason = f"MUST_WORK prerequisite {failed} failed"
    save_verification_state(state)
    GOTO EXIT

IF gate_result["has_should_pass_failure"]:
    display: f"""
⚠️ **SHOULD_WORK Gate Failed:** Proceeding with limitations
   Loading context from: {gate_result['limitation_files']}
"""
    # Load limitation context for Phase 2C
    for limitation_file in gate_result["limitation_files"]:
        load_file(f"{research_folder}/{limitation_file}")
```

### 5. Update Status to IN_PROGRESS

```python
state.sub_hypotheses[hypothesis_id].status = "IN_PROGRESS"
save_verification_state(state)

display: f"✅ {hypothesis_id} status: IN_PROGRESS"
```

### 6. Get or Create Archon Phase Tasks

<critical>
**Option A Strategy:**
- First hypothesis (H-E1): Reuse existing Phase 2C/3/4 tasks (no prefix)
- Subsequent hypotheses (H-M1, H-M2, etc.): Create new `[H-XX] Phase 2C/3/4` tasks
</critical>

```python
# Determine if this is the first hypothesis
def is_first_hypothesis(hypothesis_id, state):
    all_ids = list(state.sub_hypotheses.keys())
    return hypothesis_id == all_ids[0]

first = is_first_hypothesis(hypothesis_id, state)
display: f"📋 Hypothesis {hypothesis_id.upper()}, is_first={first}"

# Get or create Phase Tasks for this hypothesis
pipeline_project_id = state.metadata.pipeline_project_id
phase_tasks_result = get_or_create_hypothesis_phase_tasks(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    is_first_hypothesis=first,
    verification_state=state
)

IF phase_tasks_result["success"]:
    display: f"✓ Phase Tasks ready: {phase_tasks_result['task_ids']}"
    IF phase_tasks_result["created_new"]:
        # Save new task IDs to verification_state
        IF "hypothesis_phase_tasks" NOT IN state.metadata:
            state.metadata["hypothesis_phase_tasks"] = {}
        state.metadata["hypothesis_phase_tasks"][hypothesis_id.lower()] = phase_tasks_result["task_ids"]
        save_verification_state(state)
ELSE:
    display: f"⚠️ Phase Tasks issue: {phase_tasks_result['message']}"
```

---

## STEP COMPLETION

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-05-phase-2c.md` to begin Phase 2C.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Execution mode re-verified
- Prerequisites validated correctly
- BLOCKED status set for gate failures
- IN_PROGRESS status set
- Archon tasks ready

### ❌ FAILURE
- Skipping mode re-check
- Ignoring prerequisite failures
- Not updating status
- Proceeding with BLOCKED prerequisites
