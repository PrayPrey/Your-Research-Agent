---
name: 'step-07-verify-documents'
description: 'Verify all 4 Phase 3 documents exist and are ready for Archon task extraction'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-07-verify-documents.md'
nextStepFile: '{workflow_path}/steps/step-08-archon-project.md'
workflowFile: '{workflow_path}/workflow.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 7: Verify Documents

**Progress: Step 7 of 10** | Next: Step 8 - Create Archon Project

---

## STEP GOAL:

Verify that all 4 required Phase 3 documents (PRD, Architecture, Logic, Config) exist in the hypothesis folder and are ready for Archon project creation and task extraction. This validation checkpoint ensures completeness before committing to Archon.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER proceed if ANY document is missing
- ✅ ALWAYS verify all 4 documents exist
- 📋 THIS IS A VALIDATION CHECKPOINT - verify before Archon operations

---

## EXECUTION PROTOCOLS:

- 🎯 Check existence of all 4 required documents in hypothesis folder
- 💾 Display document status summary
- 📖 Confirm documents are ready for task extraction
- 🚫 FORBIDDEN: Proceeding with missing documents

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, all previous step outputs
- Focus: Document existence validation
- Limits: No document modification; validation only
- Dependencies: All 4 documents must have been created in previous steps

---

## NOTE: PRP GENERATION REMOVED

```
┌────────────────────────────────────────────────────────────┐
│ PRP GENERATION REMOVED │
│ │
│ Reason: Archon tasks are now extracted directly from: │
│ - 03_prd.md (Data & Dependencies) │
│ - 03_architecture.md (Epic Tasks) │
│ - 03_logic.md (Implementation Details) │
│ - 03_config.md (Configuration Tasks) │
│ │
│ This eliminates redundant PRP generation step. │
└────────────────────────────────────────────────────────────┘
```

---

## EXECUTION SEQUENCE

### 1. Verify Required Documents Exist

Check all 4 documents exist in `{{hypothesis_folder}}`:

| Document | Purpose | Status |
|----------|---------|--------|
| 03_prd.md | Requirements, Data Spec, Dependencies | Required |
| 03_architecture.md | Module structure, Epic tasks | Required |
| 03_logic.md | API signatures, algorithms | Required |
| 03_config.md | Hyperparameters, settings | Required |

If ANY missing → STOP and inform user.

### 2. Display Document Summary

```
✓ Phase 3 Documents Ready

Documents for Archon Task Extraction:
1. 03_prd.md - Data preparation & environment setup tasks
2. 03_architecture.md - Epic implementation tasks
3. 03_logic.md - Logic subtasks (high complexity modules)
4. 03_config.md - Configuration subtasks

PRP generation skipped - tasks extracted directly from above documents.
```

### 3. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 8
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Document Status [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display detailed document status with file sizes, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all 4 documents are verified to exist in hypothesis folder, proceed to load and execute `{workflow_path}/steps/step-08-archon-project.md` for Archon project creation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- All 4 documents exist in hypothesis folder
- Documents are ready for Archon project creation
- Document summary displayed to user

### ❌ SYSTEM FAILURE:
- Missing any of the 4 required documents
- Proceeding without verification

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
