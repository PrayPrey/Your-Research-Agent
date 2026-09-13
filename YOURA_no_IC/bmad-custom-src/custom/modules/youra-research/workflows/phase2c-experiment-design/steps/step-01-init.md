---
name: 'step-01-init'
description: 'Initialize workflow, validate state, select hypothesis, and prepare output file'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-archon-search.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Data References
verificationStateFile: '{research_folder}/verification_state.yaml'
phase2bContext: '{hypothesis_folder}/02b_context.md'
phase2bRoadmap: '{research_folder}/02b_verification_plan.md'

# Template References (EXTERNAL - not inline)
# NOTE: verification_state.yaml is created by Phase 2B step-10-finalize.md
# using verification_state_template.yaml. Phase 2C only LOADS, never creates.
contextTemplate: '{workflow_path}/templates/02b_context_template.md'
outputTemplate: '{workflow_path}/template.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 1: Initialize and Validate State

## STEP GOAL:

Initialize Phase 2C workflow by:
1. Validating MCP services
2. Loading/initializing verification state
3. Selecting target hypothesis
4. Loading per-hypothesis context
5. Preparing output file

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on state validation and hypothesis selection
- 🚫 FORBIDDEN to proceed without MCP verification
- 💬 Approach: Validate → Load → Select → Initialize
- 📋 State file must be updated before proceeding

## EXECUTION PROTOCOLS:

- 🎯 Validate all required MCP services first
- 💾 Load or initialize verification state properly
- 📖 Load per-hypothesis context (JIT generation if needed)
- 🚫 Never skip gate validation

## CONTEXT BOUNDARIES:

- Available context: verification_state.yaml, Phase 2B roadmap
- Focus: State initialization and hypothesis selection
- Limits: Do not begin research in this step
- Dependencies: MCP services must be available

---

## Sequence of Instructions

### 1. Display Welcome

```
🚀 Phase 2C: Research-Driven Experiment Design

Purpose: Transform Phase 2B hypothesis into executable experiment specification.
Target: Level 1.5 specification (concrete specs + 10-30 line pseudo-code)
```

### 2. Verify MCP Services

**MANDATORY:** Archon MCP, Exa MCP
**OPTIONAL:** Serena MCP (code analysis)

```
IF Archon OR Exa unavailable:
  ❌ STOP - Display: "Required MCP server unavailable"
  EXIT

IF Serena unavailable:
  ⚠️ Continue with warning
```

### 3. Load State File

Read `{verificationStateFile}`

**IF NOT EXISTS:**
```
❌ STOP - Display: "ERROR: verification_state.yaml not found.
   Phase 2B must complete before Phase 2C.
   Run Phase 2B step-10-finalize.md first to create verification_state.yaml."
EXIT
```

> **Note:** verification_state.yaml is created by Phase 2B step-10-finalize.md using
> verification_state_template.yaml. Phase 2C NEVER creates this file.

**IF EXISTS:**
- Load and parse YAML
- Validate state format version is >= 3.0 (required for sub_hypotheses structure)
- Display: "✅ State loaded. Progress: {completed}/{total} hypotheses"

### 4. Validate Workflow Status

```
IF workflow.status == "STOPPED":
  Display recovery options:
  [1] Review and retry failed hypothesis
  [2] Modify approach (restart from Phase 2A)
  [3] Override gate (NOT RECOMMENDED)
  [4] Abort verification
  EXIT
```

### 5. Select Hypothesis

**IF `{hypothesis_id}` was already passed as a workflow parameter (e.g., by the
hypothesis loop or an external launcher) OR running in UNATTENDED mode:**
- DO NOT ask the user.
- If `{hypothesis_id}` is set, use it directly.
- Otherwise auto-select the first hypothesis with status = IN_PROGRESS, else the
  first with status = READY (dependency order).
- Display: "✅ Hypothesis auto-selected: {hypothesis_id}" and skip to Handle Versioned Hypothesis.

**Otherwise (interactive mode):** display available hypotheses (status = READY or IN_PROGRESS):

```
📋 Available Hypotheses:

| ID | Type | Status | Prerequisites | Gate |
|----|------|--------|---------------|------|
[list]

Enter hypothesis ID (e.g., H-E1, H-M1):
```

Store: `{hypothesis_id}` = user input

**Handle Versioned Hypothesis (if version > 1):**
- Display previous version results
- Load lessons learned
- Store `previous_version_context` for experiment design

### 6. Load Per-Hypothesis Context

Construct path: `{phase2bContext}` = `{hypothesis_folder}/02b_context.md`

**IF EXISTS:** Load and display confirmation

**IF NOT EXISTS (JIT Generation):**
1. Read `{phase2bRoadmap}`
2. Extract for `{hypothesis_id}`:
   - Hypothesis info (statement, type, rationale, success criteria)
   - Experimental setup (dataset, model from Phase 2B Section 1.3)
   - Baseline & comparison targets
   - Dependencies and gate conditions
3. Generate using template: `{contextTemplate}`
4. Write to `{phase2bContext}`
5. Display: "✅ Context generated for {hypothesis_id}"

### 7. Validate Gate Conditions

```
FOR EACH prerequisite:
  IF MUST_WORK gate AND failed:
    → Update state to STOPPED
    → Block dependent hypotheses
    → EXIT

  IF SHOULD_WORK gate AND failed:
    → Log limitation, continue with warning

  IF passed:
    → Display: "✅ Prerequisite {prereq_id} satisfied"
```

### 8. Load Previous Context (If Continuation)

**IF hypothesis has prerequisites:**
- Load previous validation report (04_validation.md)
- Extract: proven components, optimal hyperparameters, lessons learned
- Store as `{previous_context}`

**IF first hypothesis:**
- Store: `{previous_context}` = null

### 9. Update State and Create Output

1. Update verification_state.yaml:
   - Set experiment_design.status = "IN_PROGRESS"
   - Set experiment_design.started_at = NOW
   - Log event in history

2. Create output file from `{outputTemplate}`

Display: "📝 State updated: {hypothesis_id} marked as IN_PROGRESS"

### 10. Present Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

```
**Select an Option:** [C] Continue to Research Phase
```

#### Menu Handling Logic:

- IF C: Load and execute `{nextStepFile}`
- IF other: Respond and redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution completes, redisplay the menu
- User can chat or ask questions - always respond and redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [state initialized, hypothesis selected, context loaded], will you then load and read fully `{nextStepFile}` to execute and begin Archon knowledge base search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- MCP services verified
- State file loaded/initialized
- Hypothesis selected
- Context file loaded/generated
- Gate conditions validated
- Output file created
- State updated to IN_PROGRESS

### ❌ FAILURE:
- Proceeding without MCP verification
- Skipping state/context initialization
- Ignoring MUST_WORK gate violations
- Not updating state file
- Loading next step before 'C' selected

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
