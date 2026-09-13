---
name: 'step-07-phase-4'
description: 'Execute Phase 4 - Coding & Validation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'
workflow_base_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows'

# File References
thisStepFile: '{workflow_path}/steps/step-07-phase-4.md'
nextStepFile: '{workflow_path}/steps/step-08-phase4-gate.md'
workflowFile: '{workflow_path}/workflow.md'

# Phase workflow
phase4_workflow: '{workflow_base_path}/phase4-coding/workflow.yaml'
---

# Step 7: Phase 4 - Coding & Validation

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Execute Phase 4 (Coding & Validation) for the current hypothesis. This phase implements the code and validates the hypothesis with the MUST_WORK gate.

## MANDATORY EXECUTION RULES

<critical>
**INVOKE-WORKFLOW IS MANDATORY**

❌ DO NOT manually implement Phase 4 logic
❌ DO NOT skip the invoke-workflow call
❌ DO NOT stop after invoke-workflow returns
✅ ALWAYS use invoke-workflow to execute the phase
✅ ALWAYS proceed to gate processing after completion
</critical>

---

## EXECUTION SEQUENCE

### 1. Display Phase Start

```
▶️ [{hypothesis_id}] Phase 4 (Coding & Validation) starting...
```

### 2. Update Archon Phase Task Status

```python
update_hypothesis_phase_status(
    pipeline_project_id=pipeline_project_id,
    hypothesis_id=hypothesis_id,
    phase="Phase 4",
    status="doing",
    is_first_hypothesis=first
)
```

### 3. Execute Phase 4 Workflow

<invoke-workflow path="{phase4_workflow}" mode="unattended" with: hypothesis_id="{{hypothesis_id}}" />

<critical>
**INVOKE-WORKFLOW COMPLETED - MANDATORY CONTINUATION**

Phase 4 workflow has finished execution and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

Phase 4 is now COMPLETE. **IMMEDIATELY proceed to Step 4 (Verify Output) below.**

- ❌ DO NOT stop here
- ❌ DO NOT ask user what to do next
- ❌ DO NOT lose context
- ✅ CONTINUE to verification NOW
</critical>

### 4. Verify Output

```python
expected_outputs = [
    "04_validation.md",
    "04_checkpoint.yaml"
]

for output in expected_outputs:
    if NOT file_exists(f"{hypothesis_folder}/{output}"):
        display: f"⚠️ Phase 4 missing: {output} - Attempting retry..."
        invoke_workflow(phase4_workflow, recovery=True)
        break

display: "✓ Phase 4 execution complete"
display: "→ Continuing to Step 8 (Phase 4 Gate Processing)..."
```

---

## STEP COMPLETION

<critical>
**MANDATORY: Proceed to gate processing immediately**

Phase 4 execution is complete. The gate result (PASS/PARTIAL/FAIL) is in 04_checkpoint.yaml.
Gate processing determines the next action (continue, route to Phase 0, or route to Phase 2A-Dialogue).
</critical>

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-08-phase4-gate.md` to process the MUST_WORK gate.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Phase 4 workflow executed via invoke-workflow
- 04_validation.md and 04_checkpoint.yaml created
- Immediately proceeded to gate processing

### ❌ FAILURE
- Skipping invoke-workflow
- Stopping after Phase 4 without gate processing
- Asking user what to do next
- Not proceeding to step-08
