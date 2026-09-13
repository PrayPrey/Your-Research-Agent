---
name: 'step-05-phase-2c'
description: 'Execute Phase 2C - Experiment Design'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'
workflow_base_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows'

# File References
thisStepFile: '{workflow_path}/steps/step-05-phase-2c.md'
nextStepFile: '{workflow_path}/steps/step-06-phase-3.md'
workflowFile: '{workflow_path}/workflow.md'

# Phase workflow
phase2c_workflow: '{workflow_base_path}/phase2c-experiment-design/workflow.yaml'
---

# Step 5: Phase 2C - Experiment Design

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Execute Phase 2C (Experiment Design) for the current hypothesis. This phase generates the experiment brief that guides implementation.

## MANDATORY EXECUTION RULES

<critical>
**INVOKE-WORKFLOW IS MANDATORY**

❌ DO NOT manually implement Phase 2C logic
❌ DO NOT skip the invoke-workflow call
✅ ALWAYS use invoke-workflow to execute the phase
</critical>

---

## EXECUTION SEQUENCE

### 1. Display Phase Start

```
▶️ [{hypothesis_id}] Phase 2C (Experiment Design) starting...
```

### 2. Update Archon Phase Task Status

```python
update_hypothesis_phase_status(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    phase="Phase 2C",
    status="doing",
    is_first_hypothesis=first
)
```

### 3. Execute Phase 2C Workflow

<invoke-workflow path="{phase2c_workflow}" mode="unattended" with: hypothesis_id="{{hypothesis_id}}" />

### 4. Verify Output

```python
expected_output = f"{hypothesis_folder}/02c_experiment_brief.md"

IF NOT file_exists(expected_output):
    display: "⚠️ Phase 2C output missing - Attempting retry..."
    invoke_workflow(phase2c_workflow, recovery=True)

    IF NOT file_exists(expected_output):
        IF hypothesis.gate.type == "MUST_WORK":
            display: "❌ Phase 2C failed for MUST_WORK hypothesis - Stopping"
            state.workflow.status = "STOPPED"
            state.workflow.stop_reason = f"Phase 2C failed for {hypothesis_id}"
            save_verification_state(state)
            GOTO EXIT
        ELSE:
            display: "⚠️ Phase 2C failed but gate is SHOULD_WORK - Continuing with limitations"
```

### 5. Update State

```python
state.sub_hypotheses[hypothesis_id].experiment_design.status = "COMPLETED"
save_verification_state(state)

display: "✓ Phase 2C complete"
```

### 6. Update Archon Phase Task

```python
update_hypothesis_phase_status(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    phase="Phase 2C",
    status="done",
    is_first_hypothesis=first
)
```

---

## STEP COMPLETION

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-06-phase-3.md` to begin Phase 3.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Phase 2C workflow executed via invoke-workflow
- 02c_experiment_brief.md created
- State updated to COMPLETED
- Archon task updated

### ❌ FAILURE
- Skipping invoke-workflow
- Not verifying output file
- Not updating state
- Proceeding without experiment brief
