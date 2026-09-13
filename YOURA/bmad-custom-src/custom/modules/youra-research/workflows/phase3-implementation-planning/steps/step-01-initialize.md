---
name: 'step-01-initialize'
description: 'Initialize Phase 3 by creating hypothesis output folder, validating inputs, verifying MCP services, and detecting hypothesis dependencies'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-01-initialize.md'
nextStepFile: '{workflow_path}/steps/step-02-prd.md'
workflowFile: '{workflow_path}/workflow.md'
commonRules: '{workflow_path}/steps/_common-rules.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 1: Initialize and Validate Input

**Progress: Step 1 of 10** | Next: Step 2 - Generate PRD

---

## Hypothesis State Check (verification_state.yaml)

<state-check>
<critical>
🔵 **HYPOTHESIS STATE VERIFICATION - EXECUTE BEFORE PROCEEDING**

Verify this hypothesis is ready for Phase 3 based on verification_state.yaml.
For Phase 3, we check:
1. This hypothesis has completed Phase 2C (experiment_design.status == "COMPLETED")
2. Prerequisites are satisfied (for dependent hypotheses)
</critical>

<action>**Step 1: Read verification_state.yaml**

```bash
Read: {research_folder}/verification_state.yaml
```

| Result | Action |
|--------|--------|
| **File exists** | → Proceed to Step 2 |
| **File not found** | → ERROR: verification_state.yaml missing. Run Phase 2B first. |

</action>

<action>**Step 2: Check Phase 2C Completion for THIS Hypothesis**

Extract hypothesis data from `hypotheses.{hypothesis_id}` in verification_state.yaml.

Check `experiment_design.status` field:

| Status Value | Result | Action |
|--------------|--------|--------|
| **COMPLETED** | ✅ Proceed | Display "✅ Phase 2C completed: {experiment_design.file}" |
| **IN_PROGRESS** | ❌ ERROR | Display "Complete Phase 2C first with /phase2c-experiment-design" → EXIT |
| **NOT_STARTED** or missing | ❌ ERROR | Display "Run /phase2c-experiment-design first" → EXIT |

</action>

<action>**Step 3: Check Prerequisites (for dependent hypotheses)**

Read `prerequisites` array from current hypothesis entry.

**If no prerequisites (empty array):**
- Display: "ℹ️ No prerequisites for this hypothesis (FOUNDATION type)"
- Proceed to next action

**If prerequisites exist:**
- Display: "Checking prerequisites for {hypothesis_id}..."
- For each prerequisite ID, check its validation status:

| Prerequisite Status | Gate Type | Result | Action |
|---------------------|-----------|--------|--------|
| `validation.status` ≠ COMPLETED | MUST_WORK | ❌ ERROR | "Complete {prereq_id} through Phase 4 first" → EXIT |
| `validation.status` ≠ COMPLETED | SHOULD_WORK | ⚠️ WARNING | "Proceeding with limitation noted" → CONTINUE |
| `validation.status` = COMPLETED | MUST_WORK + `gate.satisfied` = false | ❌ ERROR | "Prerequisite {prereq_id} (MUST_WORK) failed" → EXIT |
| `validation.status` = COMPLETED | SHOULD_WORK + `gate.satisfied` = false | ⚠️ WARNING | Load limitations from `{prereq_id}/04_validation.md` → CONTINUE |
| `validation.status` = COMPLETED | `gate.satisfied` = true | ✅ OK | Continue to next prerequisite |

After all prerequisites checked successfully:
- Display: "✅ All prerequisites satisfied"

</action>

<action>**Step 4: Pipeline Status**

**Note:** This is primarily for display/tracking - NOT a blocking check.

**Step 4a:** Get Pipeline Project ID from verification_state.yaml (loaded in Step 1):
```python
# Priority 1: metadata.pipeline_project_id
pipeline_project_id = verification_state.get("metadata", {}).get("pipeline_project_id")

# Priority 2: pipeline.project_id
if not pipeline_project_id:
    pipeline_project_id = verification_state.get("pipeline", {}).get("project_id")

# Note: No search fallback - pipeline_project_id should already exist from Phase 2B
```

**Step 4b:** If found, get current doing tasks using `mcp__archon__find_tasks` with status filter "doing"

**Step 4c:** Store IDs for Step 10 conditional update:
- `pipeline_project_id`
- `phase3_task_id`
- `phase4_task_id`

Display:
```
ℹ️ **Pipeline Status (Reference)**
• Pipeline Project: {pipeline_project_id}
• Current Pipeline Phase: {current_doing_phase}
• Note: Individual hypothesis may proceed independently of pipeline status
```
</action>

<action>**Display State Check Result**

```
✅ **Hypothesis State Verified for Phase 3**
• Hypothesis: {hypothesis_id}
• Phase 2C: COMPLETED ✓
• Prerequisites: {len(prerequisites)} checked, all satisfied
• Pipeline Phase: {current_doing_phase} (informational)
• Ready for: Implementation Planning
```
</action>
</state-check>

---

## STEP GOAL:

Initialize Phase 3 by validating MCP services, collecting hypothesis ID, calculating task budget, creating the hypothesis output folder, and verifying Phase 2C inputs. This step ensures all prerequisites are met and the workspace is prepared before invoking downstream workflows and agents.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER proceed without validating Phase 2C input
- ✅ ALWAYS verify MCP services before starting
- 📋 THIS IS AN ORCHESTRATION WORKFLOW - you coordinate other workflows

---

## EXECUTION PROTOCOLS:

- 🎯 Verify Archon MCP availability before any other action
- 💾 Create hypothesis output folder structure
- 📖 Parse verification_state.yaml to determine hypothesis type and dependencies
- 🚫 FORBIDDEN: Proceeding without MCP verification or folder creation

---

## CONTEXT BOUNDARIES:

- Available context: User-provided hypothesis ID, system configuration
- Focus: Environment setup, input validation, folder creation
- Limits: No content generation, no PRD creation yet
- Dependencies: Phase 2C experiment brief must exist

---

## INITIALIZATION SEQUENCE

### 1. Welcome User

```
Welcome {user_name} to Phase 3: Implementation Planning

Purpose: Transform Phase 2C experiment design into:
- PRD (what to implement)
- Architecture (how to structure)
- Logic (API signatures, algorithms)
- Config (hyperparameters, settings)
- Tasks file (03_tasks.yaml)
```

### 2. Verify MCP Services

Call `mcp__archon__health_check()` to verify Archon MCP is available.

**If NOT available** → STOP and inform user.
**If available** → Display "✓ Archon MCP: Available"

### 3. Get Hypothesis ID

<critical>
**UNATTENDED MODE CHECK:**
```python
state = load_yaml(verification_state_file)
is_unattended = (state.workflow.execution_mode == "UNATTENDED")

IF is_unattended OR hypothesis_id is already passed from invoke-workflow:
    # Use the passed hypothesis_id directly (from hypothesis-loop)
    hypothesis_id = "{{hypothesis_id}}" # Already set by invoke-workflow
    DO NOT ask user
ELSE:
    # Interactive mode
    Ask user: "Which hypothesis do you want to plan implementation for?"
```
</critical>

**In UNATTENDED mode:** Use `{{hypothesis_id}}` passed from hypothesis-loop
**In Interactive mode:** Ask user for hypothesis ID
- Expected format: H-E1, H-M1, H-M2, etc.
- Store as `{{hypothesis_id}}` and `{{hypothesis_id_lower}}`

### 4. Read Verification State

Read: `{research_output_path}/youra_research/verification_state.yaml`

**Extract from `hypotheses.{{hypothesis_id}}`:**
- `type` → `{{hypothesis_type_field}}` (EXISTENCE/MECHANISM/COMPARISON)
- `prerequisites` → determine FOUNDATION vs INCREMENTAL
- `gate.type` → `{{gate_type}}`

**Determine hypothesis type based on prerequisites:**

| Prerequisites | Hypothesis Type | Base Hypothesis |
|---------------|-----------------|-----------------|
| Empty array | FOUNDATION | None |
| Non-empty array | INCREMENTAL | First prerequisite ID |

### 5. Calculate Task Budget (2-Tier System)

Reference `workflow.yaml → task_constraints.budget_by_hypothesis_type`:

| Tier | Type | Total Max | Epic Range | Infrastructure |
|------|------|-----------|------------|----------------|
| **LIGHT** | EXISTENCE | 15 | 4-8 | minimal |
| **FULL** | MECHANISM | 30 | 6-12 | standard |
| **FULL** | COMPARISON | 30 | 6-12 | standard |

Store: `{{task_budget_tier}}`, `{{task_budget_total_max}}`, `{{task_budget_epic_range}}`, `{{task_budget_infrastructure_level}}`

### 6. Create Hypothesis Output Folder

**CRITICAL**: Create the hypothesis-specific subfolder BEFORE any output operations.

**Folder path construction:**
- Base path: `{research_output_path}/youra_research/`
- Hypothesis subfolder: `{hypothesis_id_lower}` (lowercase version of hypothesis ID)
- Full path: `{research_output_path}/youra_research/{hypothesis_id_lower}`

**Action:** Create folder using `mkdir -p` command (creates parent directories if needed)

**Store:** Save full path as `{{hypothesis_folder}}` variable

**Display:** "✓ Output folder created/verified: {hypothesis_folder}"

### 7. Verify Phase 2C Input

Check file exists: `{{hypothesis_folder}}/02c_experiment_brief.md`
- If NOT FOUND → STOP with error
- If FOUND → Display path and continue

### 8. Verify Prerequisites (If Incremental)

**Only execute if hypothesis_type = "INCREMENTAL"**

**Prerequisite folder path:** `{research_output_path}/youra_research/{base_hypothesis_id_lower}`

**Required files to verify:**

| File | Path |
|------|------|
| PRD | `{prereq_folder}/03_prd.md` |
| Architecture | `{prereq_folder}/03_architecture.md` |
| Logic | `{prereq_folder}/03_logic.md` |
| Config | `{prereq_folder}/03_config.md` |

> **Note**: `03_prp.md` - no longer required for prerequisites

**Verification result:**

| Result | Action |
|--------|--------|
| All files exist | ✅ Proceed |
| Any file missing | ❌ STOP with list of missing files |

### 9. Display Execution Plan

```
================================================================
PHASE 3 EXECUTION PLAN
================================================================

Hypothesis: {{hypothesis_id}} ({{hypothesis_type}})
Task Budget: {{task_budget_total_max}} tasks ({{hypothesis_type_field}})
Output Folder: {{hypothesis_folder}}
Input: {{hypothesis_folder}}/02c_experiment_brief.md

Steps:
1. ✓ Initialize (Current)
   - MCP verified
   - Output folder created: {{hypothesis_folder}}
2. Generate PRD (BMAD workflow)
3. Architecture Agent (Task agent)
4. Subtask Budget Allocation
5. Parallel Agents: Logic + Config
6. Overall Complexity Assessment
7. Verify Documents
8. Create Archon Project
9. Create Archon Tasks
10. Validation & Summary
================================================================
```

### 10. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 2
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Setup [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display initialization summary, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all initialization checks pass (MCP verified, folder created, Phase 2C input validated, prerequisites checked if incremental), proceed to load and execute `{workflow_path}/steps/step-02-prd.md` for PRD generation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Archon MCP verified and available
- Hypothesis ID collected from user
- verification_state.yaml parsed correctly
- Task budget calculated based on hypothesis type
- **Output folder created** in hypothesis-specific path
- Phase 2C input file verified
- Prerequisites validated (if incremental)

### ❌ SYSTEM FAILURE:
- Proceeding without MCP verification
- Hardcoding hypothesis dependencies
- **Not creating output folder before proceeding**
- Not validating ALL prerequisites for incremental hypotheses
- Skipping verification_state.yaml read

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
