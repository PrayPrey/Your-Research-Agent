---
name: 'step-09-generate-tasks'
description: 'Extract tasks from 03_*.md documents and generate 03_tasks.yaml (Local Checkpoint-Based Task Management)'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-09-generate-tasks.md'
nextStepFile: '{workflow_path}/steps/step-10-validation.md'
workflowFile: '{workflow_path}/workflow.md'
verification_state_path: '{research_folder}/verification_state.yaml'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Output file reference
tasks_output_file: '{hypothesis_folder}/03_tasks.yaml'
tasks_template: '{workflow_path}/templates/03_tasks_template.yaml'

# Code examples extracted for file size optimization (BMAD v6 compliance)
examples_file: '{workflow_path}/templates/task-generation-examples.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 9: Generate Implementation Tasks File

**Progress: Step 9 of 10** | Next: Step 10 - Validation & Summary

---

## STEP GOAL:

Extract tasks from all 4 Phase 3 documents and generate `03_tasks.yaml` for Phase 4 consumption. Data preparation and environment setup tasks come first, followed by Epic implementation tasks and subtasks. Apply budget rebalancing exclusions if applicable.

> - Tasks are written to local `03_tasks.yaml` file (NOT created in Archon)
> - **NEW: Each task has `reference_files` linking to Phase 3 document sections**
> - Phase 4 Coder reads these references before implementing each task
> - This ensures implementation follows Phase 3 design specifications

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 MUST extract tasks from 4 documents - never invent tasks
- 🔄 Generate tasks in priority order (data prep → environment → implementation)
- ✅ Verify task count matches complexity level
- ⚠️ CHECK `{{excluded_subtasks}}` from Step 6 - skip excluded subtasks
- 📁 Output goes to `03_tasks.yaml`, NOT Archon MCP

---

## EXECUTION PROTOCOLS:

- 🎯 Parse all 4 documents (PRD, Architecture, Logic, Config) for tasks
- 💾 Generate `03_tasks.yaml` with prioritized task list
- 📖 Update verification_state.yaml with generation status
- 🚫 FORBIDDEN: Creating Archon tasks; inventing tasks without reading documents; skipping data prep tasks

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, all 03_*.md files, excluded_subtasks list, tier (LIGHT/FULL)
- Focus: Task extraction and 03_tasks.yaml generation
- Limits: Only create tasks found in documents; do not invent
- Dependencies: Phase 3 documents (03_prd.md, 03_architecture.md, etc.) exist

---

## 🚨 UNATTENDED MODE ENFORCEMENT

```
┌────────────────────────────────────────────────────────────┐
│ REQUIRED: Read and parse ALL 4 documents: │
│ - 03_prd.md (Data Spec, Dependencies) │
│ - 03_architecture.md (Epic Tasks) │
│ - 03_logic.md (Subtasks for high-complexity modules) │
│ - 03_config.md (Configuration subtasks) │
│ │
│ REQUIRED: Generate 03_tasks.yaml with all extracted tasks │
│ REQUIRED: Validate task count against tier budget │
│ │
│ FORBIDDEN: Creating Archon tasks (mcp__archon__manage_task)│
│ FORBIDDEN: Inventing tasks without reading documents │
│ FORBIDDEN: Skipping data preparation tasks │
└────────────────────────────────────────────────────────────┘
```

---

## EXECUTION SEQUENCE

### 0. Initialize Task Generation Context

> 📄 **Code Example:** See `templates/task-generation-examples.md#initialize-task-generation-context`

Get hypothesis context from workflow state and set budget based on tier (LIGHT=15, FULL=30).

---

### 1. Parse 03_prd.md for Data & Environment Tasks

Read `{{hypothesis_folder}}/03_prd.md` and extract:

#### A. Data Specification Section (Section 4)

Find datasets that require **manual download** (not auto-download like PyG Planetoid):

> 📄 **Code Example:** See `templates/task-generation-examples.md#parse-03_prdmd---data-tasks`

**Auto-download datasets (NO task needed):**
- PyG Planetoid (Cora, CiteSeer, PubMed) - auto-downloads

#### B. Dependencies Section (Section 7)

Extract Python packages and create environment setup task:

> 📄 **Code Example:** See `templates/task-generation-examples.md#parse-03_prdmd---environment-setup`

### 2. Parse 03_architecture.md for Epic Tasks

Read `{{hypothesis_folder}}/03_architecture.md` and find Epic Tasks section.

Extract for each Epic:
- ID, Title, Description
- Complexity score (if available)
- Module/Feature assignment
- **Section anchor for reference_files** (e.g., `#Epic-E1-DataLoader`)

> 📄 **Code Example:** See `templates/task-generation-examples.md#parse-03_architecturemd---epic-tasks`

### 3. Parse 03_logic.md for Subtasks (Optional)

Read `{{hypothesis_folder}}/03_logic.md` for high-complexity modules.

Only extract subtasks if module complexity > 10/20:
- API implementation tasks
- Algorithm implementation tasks

### 4. Parse 03_config.md for Config Tasks (Optional)

Read `{{hypothesis_folder}}/03_config.md` if separate config tasks needed.

Usually integrated into implementation tasks, so this may yield 0 tasks.

### 4.2 Link reference_files to Epic Tasks

**After parsing all documents, link logic and config references to Epic tasks:**

> 📄 **Code Example:** See `templates/task-generation-examples.md#link-reference_files-to-epic-tasks`

### 4.5 Apply Exclusion List (Budget Rebalancing)

**Check if `{{excluded_subtasks}}` exists from Step 6:**

> 📄 **Code Example:** See `templates/task-generation-examples.md#apply-exclusion-list-budget-rebalancing`

### 5. Consolidate and Prioritize Tasks

> 📄 **Code Example:** See `templates/task-generation-examples.md#consolidate-and-prioritize-tasks`

**Priority Order (highest first):**
1. Data preparation tasks (priority 100-95)
2. Environment setup (priority 94)
3. Epic implementation tasks (priority 93-50)
4. Subtasks (priority 49-2)
5. Failsafe task (priority 1) - Pipeline continuation checkpoint

### 6. Generate 03_tasks.yaml

> 📄 **Code Example:** See `templates/task-generation-examples.md#generate-03_tasksyaml`

Output: `{hypothesis_folder}/03_tasks.yaml` with version 1.1 schema (includes reference_files).

### 7. Verify Task File Generation

> 📄 **Code Example:** See `templates/task-generation-examples.md#verify-task-file`

Verify file was created and is valid YAML with correct budget summary.

### 8. Update verification_state.yaml

> 📄 **Code Example:** See `templates/task-generation-examples.md#update-verification_stateyaml`

Update `sub_hypotheses.{hypothesis_id}.implementation_planning` with COMPLETED status and task_breakdown.

### 9. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 10
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Task Summary [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display task breakdown and budget status, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all tasks are extracted from 4 documents AND written to 03_tasks.yaml AND task count is within budget AND verification_state.yaml is updated, proceed to load and execute `{workflow_path}/steps/step-10-validation.md` for final validation.

---

## TASK EXTRACTION REFERENCE

### From 03_prd.md

| Section | What to Extract | Task Type |
|---------|-----------------|-----------|
| 4. Data Specification | Manual download datasets | data-preparation |
| 7.1 Python Packages | Package list | setup |
| 7.2 External Repositories | Reference repos | (info only) |

### From 03_architecture.md

| Section | What to Extract | Task Type |
|---------|-----------------|-----------|
| Epic Tasks | Module implementation | data-pipeline, model, training, evaluation |
| File Structure | Target files | (info only) |

### From 03_logic.md

| Section | What to Extract | Task Type |
|---------|-----------------|-----------|
| API Signatures | Implementation details | subtask |
| Algorithms | Pseudo-code | subtask |

### From 03_config.md

| Section | What to Extract | Task Type |
|---------|-----------------|-----------|
| Hyperparameters | Config implementation | (usually merged into epic) |

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- All 4 documents parsed for task extraction
- Data preparation tasks extracted (for manual download datasets)
- Environment setup task extracted
- All Epic tasks from architecture extracted with **reference_files**
- Subtasks extracted (excluding Step 6 exclusions if applicable)
- **03_tasks.yaml generated with correct schema**
- **reference_files linked to logic/config sections**
- **Task count within tier budget**
- verification_state.yaml updated with COMPLETED status

### ❌ SYSTEM FAILURE:
- **Creating Archon tasks (mcp__archon__manage_task)**
- Skipping 03_tasks.yaml generation
- Skipping data preparation tasks
- Not reading 03_prd.md for data/dependency tasks
- Creating only implementation tasks (missing data prep)
- Wrong priority order (implementation before data prep)
- Exceeding tier budget without warning
- Inventing tasks without document source
- Not updating verification_state.yaml

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

