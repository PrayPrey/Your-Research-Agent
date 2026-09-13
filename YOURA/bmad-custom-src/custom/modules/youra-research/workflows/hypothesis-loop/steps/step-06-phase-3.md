---
name: 'step-06-phase-3'
description: 'Execute Phase 3 - Implementation Planning'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'
workflow_base_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows'

# File References
thisStepFile: '{workflow_path}/steps/step-06-phase-3.md'
nextStepFile: '{workflow_path}/steps/step-07-phase-4.md'
workflowFile: '{workflow_path}/workflow.md'

# Phase workflow
phase3_workflow: '{workflow_base_path}/phase3-implementation-planning/workflow.yaml'
---

# Step 6: Phase 3 - Implementation Planning

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Execute Phase 3 (Implementation Planning) for the current hypothesis. This phase generates PRD, Architecture, Logic, and Config documents.

## MANDATORY EXECUTION RULES

<critical>
**INVOKE-WORKFLOW IS MANDATORY**

❌ DO NOT manually implement Phase 3 logic
❌ DO NOT skip the invoke-workflow call
✅ ALWAYS use invoke-workflow to execute the phase
</critical>

---

## EXECUTION SEQUENCE

### 1. Display Phase Start

```
▶️ [{hypothesis_id}] Phase 3 (Implementation Planning) starting...
```

### 2. Update Archon Phase Task Status

```python
update_hypothesis_phase_status(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    phase="Phase 3",
    status="doing",
    is_first_hypothesis=first
)
```

### 3. Execute Phase 3 Workflow

<invoke-workflow path="{phase3_workflow}" mode="unattended" with: hypothesis_id="{{hypothesis_id}}" />

### 4. Verify Outputs

```python
required_outputs = [
    "03_prd.md",
    "03_architecture.md",
    "03_logic.md",
    "03_config.md"
]

missing = []
for output in required_outputs:
    if NOT file_exists(f"{hypothesis_folder}/{output}"):
        missing.append(output)

IF missing:
    display: f"⚠️ Phase 3 missing outputs: {missing} - Attempting retry..."
    invoke_workflow(phase3_workflow, recovery=True)

    # Re-check
    still_missing = [f for f in missing if NOT file_exists(f"{hypothesis_folder}/{f}")]

    IF still_missing:
        IF hypothesis.gate.type == "MUST_WORK":
            display: f"❌ Phase 3 failed for MUST_WORK hypothesis - Stopping"
            state.workflow.status = "STOPPED"
            state.workflow.stop_reason = f"Phase 3 failed for {hypothesis_id}: missing {still_missing}"
            save_verification_state(state)
            GOTO EXIT
        ELSE:
            display: f"⚠️ Phase 3 incomplete but gate is SHOULD_WORK - Continuing with limitations"
```

### 5. Update State

```python
state.sub_hypotheses[hypothesis_id].implementation_planning.status = "COMPLETED"
save_verification_state(state)

display: "✓ Phase 3 complete"
display: f" Created: {', '.join(required_outputs)}"
```

### 6. Update Archon Phase Task

```python
update_hypothesis_phase_status(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    phase="Phase 3",
    status="done",
    is_first_hypothesis=first
)
```

---

## STEP COMPLETION

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-07-phase-4.md` to begin Phase 4.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Phase 3 workflow executed via invoke-workflow
- All 4 output files created (PRD, Architecture, Logic, Config)
- State updated to COMPLETED
- Archon task updated

### ❌ FAILURE
- Skipping invoke-workflow
- Not verifying all output files
- Not updating state
- Proceeding without implementation plans
