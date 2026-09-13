---
name: 'step-00-init-environment'
description: 'Initialize workflow environment, verify MCP services, and check pipeline status'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-00-init-environment.md'
nextStepFile: '{workflow_path}/steps/step-01-init-parsing.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Template References
outputTemplate: '{workflow_path}/template.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Input References
phase2aOutput: '{research_output_path}/03_refinement.yaml'
phase2aSynthesis: '{research_output_path}/02_synthesis.yaml'
---

# Step 0: Initialize Environment

## STEP GOAL:

Initialize workflow environment by verifying MCP services and checking pipeline status in Archon. This step establishes the foundation for the entire verification planning process.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on environment initialization and pipeline verification
- 🚫 FORBIDDEN to proceed without MCP service verification
- 💬 Approach: Systematic initialization with clear status reporting
- 📋 Store pipeline IDs for later steps

## EXECUTION PROTOCOLS:

- 🎯 Verify all required MCP services are available
- 💾 Check and store Pipeline Project ID from Archon
- 📖 Verify Phase 2B is the current pipeline phase
- 🚫 FORBIDDEN to skip pipeline status check

## CONTEXT BOUNDARIES:

- Available context: Config files, Archon project data
- Focus: Environment setup and pipeline verification
- Limits: No data parsing yet, only initialization
- Dependencies: MCP services must be verified before proceeding

---

## Actions

### 1. Verify MCP Services

Check MCP service availability:

```
✓ Archon MCP: {mcp_services.archon.enabled}
✓ ClearThought MCP: {mcp_services.clearthought.enabled}
✓ Exa MCP: {mcp_services.exa.enabled}
```

If any critical service is disabled, warn the user and ask whether to proceed.

### 2. Pipeline Status Check (Archon)

<pipeline-check>
<critical>
🔵 **PIPELINE TASK VERIFICATION - EXECUTE BEFORE PROCEEDING**

Verify Pipeline Project exists and Phase 2B is the current phase.
</critical>

<action>**Check Pipeline Status**

```python
# 1. Read Phase 0 output to get exact project title
phase0_files = glob("{research_folder}/**/00_brainstorm.md")
IF NOT phase0_files:
    STOP("Phase 0 output not found. Run Phase 0 first.")

phase0_content = Read(phase0_files[0])
pipeline_project_title = extract_frontmatter(phase0_content, "pipeline_project_title")

# 2. Search for Pipeline Project
IF pipeline_project_title:
    result = mcp__archon__find_projects(query=pipeline_project_title)
ELSE:
    # Fallback: Generic search (for older Phase 0 outputs)
    Log("⚠ pipeline_project_title not found, using generic search")
    result = mcp__archon__find_projects(query="Anonymous Pipeline")

IF result.success AND len(result.projects) > 0:
    pipeline_project_id = result.projects[0].id
    Log(f"Found Pipeline Project: {result.projects[0].title}")
ELSE:
    STOP("Pipeline Project not found. Run Phase 0 first.")
```

| Result | Action |
|--------|--------|
| **Found** | → Verify Phase 2B Task is "doing" |
| **Not Found** | → ERROR: Pipeline missing, ask user to run Phase 0 first |

```python
# 3. Verify Phase 2B is current (if Pipeline found)
mcp__archon__find_tasks(
    project_id="{pipeline_project_id}",
    filter_by="status",
    filter_value="doing"
)
```

| Result | Action |
|--------|--------|
| **"Phase 2B - Planning" doing** | ✅ Correct, proceed |
| **"Phase 2A - Dialogue" doing** | → Phase 2A not complete, redirect user |
| **Other phase doing** | → Pipeline out of sync, ask user |

</action>
</pipeline-check>

### 3. Store Pipeline IDs

<action>**Store Pipeline IDs for Step 10**

Save these for completion:
- `pipeline_project_id`: Project UUID
- `phase2b_task_id`: Phase 2B Task UUID
- `phase2c_task_id`: Phase 2C Task UUID
</action>

### 4. Display Initialization Status

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 2B INITIALIZATION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MCP Services:
  ✓ Archon MCP: Available
  ✓ ClearThought MCP: Available
  ✓ Exa MCP: Available

Pipeline Status:
  ✓ Pipeline Project: {pipeline_project_title}
  ✓ Current Phase: Phase 2B - Planning
  ✓ Status: doing

Ready to proceed with Phase 2A parsing.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [MCP services verified, pipeline status confirmed], will you then load and read fully `{nextStepFile}` to execute and begin Phase 2A parsing.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- MCP services verified (Archon, ClearThought, Exa)
- Pipeline Project found in Archon
- Phase 2B confirmed as current phase
- Pipeline IDs stored for later use
- User informed of initialization status
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Proceeding without MCP service verification
- Skipping pipeline status check
- Not storing pipeline IDs
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
