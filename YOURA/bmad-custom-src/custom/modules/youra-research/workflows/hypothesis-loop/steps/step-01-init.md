---
name: 'step-01-init'
description: 'Parse execution mode and load verification state'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'
config_source: '{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-check-status.md'
workflowFile: '{workflow_path}/workflow.md'

# State file
verification_state_file: '{research_folder}/verification_state.yaml'

# Helper References
state_management_helper: '{workflow_path}/helpers/state_management.md'
archon_hypothesis_phase_helper: '{workflow_path}/helpers/archon_hypothesis_phase.md'
---

# Step 1: Initialize - Parse Mode & Load State

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Parse the execution mode (AUTO/STEP/SINGLE) and load the verification state from verification_state.yaml. This is the entry point for the hypothesis loop.

## MANDATORY EXECUTION RULES

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 Auto-proceed after completion (no user menu in init step)
- 🚫 NEVER skip state loading

### Role Reinforcement

- ✅ You are an autonomous pipeline orchestrator
- ✅ This step runs without user interaction
- ✅ Parse mode from state file OR arguments

## EXECUTION PROTOCOLS

- 🎯 Parse execution mode from verification_state.yaml or arguments
- 💾 Store mode in memory for subsequent steps
- 🚫 FORBIDDEN to proceed without loading state

---

## EXECUTION SEQUENCE

### 1. Load Configuration

```python
config = load_yaml(config_source)
research_output_path = config.research_output_path
research_folder = f"{research_output_path}/youra_research"
verification_state_file = f"{research_folder}/verification_state.yaml"
```

### 2. Check State File Exists

```python
IF NOT file_exists(verification_state_file):
    display: "❌ **verification_state.yaml not found** - Run `/phase2b-planning` first."
    GOTO EXIT
```

### 3. Load Verification State

```python
state = load_yaml(verification_state_file)
display: f"📁 Loaded: {verification_state_file}"
```

### 4. Parse Execution Mode

```python
arguments = "{{user_input}}"

# Priority: 1) verification_state.yaml 2) arguments 3) default AUTO
IF state.workflow.execution_mode == "UNATTENDED":
    execution_mode = "AUTO"
    display: "🤖 Auto mode (from state): Execute all READY hypotheses"
ELIF "--mode=auto" IN arguments OR arguments == "auto":
    execution_mode = "AUTO"
    display: "🤖 Auto mode (from args): Execute all READY hypotheses"
ELIF "--mode=step" IN arguments OR arguments == "step":
    execution_mode = "STEP"
    display: "👤 Step mode: Confirm after each hypothesis"
ELIF "--mode=single" IN arguments OR arguments == "single":
    execution_mode = "SINGLE"
    display: "1️⃣ Single mode: Execute only next READY hypothesis"
ELSE:
    execution_mode = "AUTO"
    display: "🤖 Auto mode (default): Execute all READY hypotheses"
```

### 5. Display State Summary

```
📊 **Hypothesis Loop Initialized**
   Mode: {{execution_mode}}
   State File: {{verification_state_file}}
   Workflow Status: {{state.workflow.status}}
```

---

## STEP COMPLETION

This is an auto-proceed initialization step.

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-02-check-status.md` to check workflow status.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Verification state loaded successfully
- Execution mode parsed correctly
- State summary displayed

### ❌ FAILURE
- State file not found (→ exit with error)
- Failed to parse mode (→ default to AUTO)
- Proceeding without loading state
