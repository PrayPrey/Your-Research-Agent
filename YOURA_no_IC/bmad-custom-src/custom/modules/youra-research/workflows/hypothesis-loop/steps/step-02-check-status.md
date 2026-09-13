---
name: 'step-02-check-status'
description: 'Check workflow status (STOPPED/COMPLETED/ACTIVE/ROUTED)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-02-check-status.md'
nextStepFile: '{workflow_path}/steps/step-03-get-ready.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 2: Check Workflow Status

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Check the current workflow status (STOPPED/COMPLETED/ACTIVE/ROUTED) and handle accordingly:
- **STOPPED**: Resume in AUTO mode, ask in STEP mode
- **COMPLETED**: Exit gracefully
- **ROUTED**: Exit with routing information (do NOT auto-convert to ACTIVE)
- **ACTIVE**: Continue processing

## MANDATORY EXECUTION RULES

- 📖 Read complete step file before action
- 🔄 Auto-proceed in UNATTENDED/AUTO mode
- ⏸️ Ask confirmation in STEP mode for STOPPED workflows

---

## EXECUTION SEQUENCE

### 1. Get Workflow Status

```python
workflow_status = state.workflow.status
stop_reason = state.workflow.get("stop_reason", None)
```

### 2. Handle STOPPED Status

```python
IF workflow_status == "STOPPED":
    display: f"⚠️ **Workflow STOPPED:** {stop_reason}"

    IF execution_mode == "AUTO":
        # Auto-resume in unattended mode
        display: "🔄 Auto-resuming workflow..."
        state.workflow.status = "ACTIVE"
        state.workflow.stop_reason = None
        save_verification_state(state)
    ELSE:
        # Ask user in STEP mode
        ask_user: "Continue anyway? [Y/N]"
        IF response == "N":
            display: "👋 Exiting. Run /hypothesis-loop to resume."
            GOTO EXIT
        state.workflow.status = "ACTIVE"
        state.workflow.stop_reason = None
        save_verification_state(state)
```

### 3. Handle ROUTED Status

<critical>
**ROUTED status indicates routing to another phase is required.**
Do NOT auto-convert to ACTIVE. The workflow must exit and let the parent pipeline handle routing.
</critical>

```python
IF workflow_status == "ROUTED":
    routing = state.workflow.get("routing", {})
    target = routing.get("target", "Unknown")
    source = routing.get("source", "Unknown")
    reason = routing.get("reason", "Unknown")

    display: f"""
🔄 **Workflow ROUTED**

Routing required from {source} to {target}.
Reason: {reason}

This workflow will exit. The parent pipeline (full-pipeline-unattended)
will handle the routing automatically.

If running standalone:
- Target Phase 0: Execute `/phase0-brainstorm`
- Target Phase 2A: Execute `/phase2a-dialogue`
"""
    GOTO EXIT
```

### 4. Handle COMPLETED Status

```python
IF workflow_status == "COMPLETED":
    display: """
🎉 **All hypothesis verification completed!**

Main hypothesis has been validated (or terminated).
Check verification_state.yaml for final results.

Next steps:
- If PASS: Proceed to Phase 6 (Paper Writing)
- If PARTIAL: Review failure context in Serena Memory
"""
    GOTO EXIT
```

### 5. Confirm ACTIVE Status

```python
# Only set to ACTIVE if not already ACTIVE and not ROUTED/COMPLETED
# (ROUTED and COMPLETED have their own exit paths above)
IF workflow_status not in ["ACTIVE", "ROUTED", "COMPLETED"]:
    state.workflow.status = "ACTIVE"
    save_verification_state(state)

display: "✅ Workflow status: ACTIVE"
```

---

## STEP COMPLETION

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-03-get-ready.md` to get ready hypotheses.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Status checked and handled appropriately
- STOPPED workflows resumed (with user consent in STEP mode)
- COMPLETED workflows exit gracefully

### ❌ FAILURE
- Ignoring STOPPED status
- Not saving state after status change
- Proceeding on COMPLETED without checking
