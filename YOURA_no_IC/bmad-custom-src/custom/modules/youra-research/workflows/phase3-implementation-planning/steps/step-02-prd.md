---
name: 'step-02-prd'
description: 'Invoke BMAD v6 PRD workflow to generate Product Requirements Document'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-02-prd.md'
nextStepFile: '{workflow_path}/steps/step-03-architecture-agent.md'
workflowFile: '{workflow_path}/workflow.md'
prdWorkflow: '{project-root}/_bmad/bmm/workflows/2-plan-workflows/prd/workflow.md'
bmadConfig: '{project-root}/_bmad/bmm/config.yaml'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 2: Invoke BMAD v6 PRD Workflow

**Progress: Step 2 of 10** | Next: Step 3 - Architecture Agent

---

## STEP GOAL:

Generate a comprehensive Product Requirements Document (PRD) by invoking the BMAD v6 PRD workflow. The PRD captures what needs to be implemented including functional requirements, data specifications, evaluation metrics, and dependencies derived from the Phase 2C experiment design.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER create PRD content yourself - invoke the BMAD workflow
- 🔄 DO NOT interrupt the PRD workflow once started
- ✅ ALWAYS wait for PRD workflow completion before proceeding

---

## EXECUTION PROTOCOLS:

- 🎯 Extract key information from Phase 2C experiment brief before PRD generation
- 💾 Ensure PRD is saved to hypothesis folder (03_prd.md)
- 📖 Verify PRD completeness against Phase 2C items
- 🚫 FORBIDDEN: Using Write tool to create PRD directly; using Task tool to spawn "PRD Agent"

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, Phase 2C experiment brief
- Focus: PRD generation via BMAD workflow orchestration
- Limits: Do not generate PRD content directly; do not modify Phase 2C inputs
- Dependencies: Step 1 completion (folder created, inputs validated)

---

## 🚨 UNATTENDED MODE ENFORCEMENT

```
┌────────────────────────────────────────────────────────────┐
│ REQUIRED (even in UNATTENDED): │
│ ✅ Read BMAD PRD workflow.md file │
│ ✅ Read bmm/config.yaml for variables │
│ ✅ Execute PRD workflow step-files sequentially │
│ ✅ Verify 03_prd.md was generated │
│ │
│ FORBIDDEN: │
│ ❌ Using Write tool to create 03_prd.md directly │
│ ❌ Using Task tool to spawn "PRD Agent" │
│ ❌ Generating PRD content in main session │
└────────────────────────────────────────────────────────────┘
```

---

## PRD GENERATION SEQUENCE

### 1. Extract Phase 2C Key Info (Pre-check)

Read `{{hypothesis_folder}}/02c_experiment_brief.md` and extract:

| Category | Items to Extract |
|----------|------------------|
| **Dataset** | Primary dataset, static baselines, preprocessing |
| **Models** | ALL baseline models (not just one!), proposed model |
| **Evaluation** | Standard metrics, hypothesis-specific metrics |
| **Ablation** | ALL ablation variants (often missed!) |

**Display summary** before invoking PRD workflow.

### 2. Inform User

```
Starting PRD generation using BMAD v6 PRD Workflow.

Hypothesis Type: {{hypothesis_type}}
Input: {{hypothesis_folder}}/02c_experiment_brief.md
Output: {{hypothesis_folder}}/03_prd.md

The workflow will guide you through collaborative discovery.
```

### 3. Load and Execute BMAD PRD Workflow

**A. Read** `{project-root}/_bmad/bmm/workflows/2-plan-workflows/prd/workflow.md`

**B. Load config** from `{project-root}/_bmad/bmm/config.yaml`

**C. Execute** PRD workflow step-01 and follow step-file architecture:
- Read each step file completely before execution
- Wait for user input at menus
- Do not skip or optimize steps
- Continue until workflow completes

### 4. Verify PRD and Move to Hypothesis Folder

After PRD workflow completes:

**A. Check locations and move file:**
```python
# BMAD PRD workflow saves to: {project-root}/docs/planning-artifacts/prd.md
bmad_output = "{project-root}/docs/planning-artifacts/prd.md"
target = f"{hypothesis_folder}/03_prd.md"

if exists(bmad_output):
    # Read content from BMAD output location
    content = read(bmad_output)
    # Write to hypothesis folder with correct name
    write(target, content)
    display: f"✓ PRD moved to {target}"
elif exists(target):
    display: f"✓ PRD already at {target}"
else:
    # Fallback: Search for *prd*.md in docs/planning-artifacts/
    search_path = "{project-root}/docs/planning-artifacts/*prd*.md"
    found = glob(search_path)
    if found:
        content = read(found[0])
        write(target, content)
    else:
        display: "❌ PRD not found - re-run BMAD PRD workflow"
        FAIL
```

**B. Verify completeness** - check for:
- Frontmatter with stepsCompleted
- Required sections: Executive Summary, Problem Statement, Functional Requirements, NFRs, Success Criteria

**C. Phase 2C completeness check:**

| Check | Look For |
|-------|----------|
| Baseline models | ALL models from Phase 2C in FRs |
| Static datasets | Benchmark datasets in FRs |
| Ablation variants | One FR per ablation variant |
| Custom metrics | Hypothesis-specific metrics in FRs |

If missing items → prompt user to add or re-run.

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 3
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review PRD Summary [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display PRD section summary and Phase 2C completeness check, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN BMAD PRD workflow completes successfully AND 03_prd.md exists in hypothesis folder AND Phase 2C completeness is verified, proceed to load and execute `{workflow_path}/steps/step-03-architecture-agent.md` for architecture design.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- BMAD PRD workflow executed completely
- 03_prd.md exists in hypothesis folder
- All Phase 2C items found in PRD (baselines, datasets, ablations, metrics)
- PRD path stored for subsequent steps

### ❌ SYSTEM FAILURE:
- Creating PRD directly with Write tool
- Skipping BMAD workflow execution
- PRD missing baseline models from Phase 2C
- PRD missing ablation variants
- Not verifying Phase 2C completeness

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
