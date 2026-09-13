---
name: 'step-10-validation'
description: 'Run validation checklist and display Phase 3 completion summary'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-10-validation.md'
workflowFile: '{workflow_path}/workflow.md'
validationChecklist: '{workflow_path}/checklist.md'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 10: Validation and Summary

**Progress: Step 10 of 10** | Final Step

---

## STEP GOAL:

Run comprehensive validation of all Phase 3 outputs, calculate validation score, and display the completion summary with Phase 4 guidance. This final step ensures all artifacts are correct and ready for implementation.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER skip validation - all outputs must be verified
- ✅ ALWAYS display comprehensive completion summary
- 📋 THIS IS THE FINAL STEP - ensure everything is complete

---

## EXECUTION PROTOCOLS:

- 🎯 Validate file existence for all 4 documents
- 💾 Validate Archon project, documents, and tasks
- 📖 Calculate validation score using scorecard
- 🚫 FORBIDDEN: Skipping validation; not providing Phase 4 guidance

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, project_id, all IDs from previous steps
- Focus: Comprehensive validation and summary
- Limits: No creation or modification; validation only
- Dependencies: All previous steps must have completed successfully

---

## VALIDATION SEQUENCE

### 1. Validate File Existence

| File | Path | Check |
|------|------|-------|
| PRD | {{hypothesis_folder}}/03_prd.md | ✓/✗ |
| Architecture | {{hypothesis_folder}}/03_architecture.md | ✓/✗ |
| Logic | {{hypothesis_folder}}/03_logic.md | ✓/✗ |
| Config | {{hypothesis_folder}}/03_config.md | ✓/✗ |
| Tasks | {{hypothesis_folder}}/03_tasks.yaml | ✓/✗ |

### 2. Validate Archon Artifacts

**Verify the following using Archon MCP:**

| Artifact | MCP Call | Expected |
|----------|----------|----------|
| Project | `mcp__archon__find_projects(project_id=project_id)` | Project exists |
| Documents | `mcp__archon__find_documents(project_id=project_id)` | 5 documents |

### 2b. Validate Local Tasks File

**Read and validate 03_tasks.yaml:**

```python
import yaml

# Read tasks file
with open(f"{hypothesis_folder}/03_tasks.yaml", 'r') as f:
    tasks_data = yaml.safe_load(f)

# Validate task format version
assert tasks_data.get("version") == "1.0", "Invalid task format version"

# Validate metadata
metadata = tasks_data.get("metadata", {})
assert metadata.get("hypothesis_id"), "Missing hypothesis_id"
assert metadata.get("tier") in ["LIGHT", "FULL"], "Invalid tier"

# Validate tasks list
tasks = tasks_data.get("tasks", [])
assert len(tasks) > 0, "No tasks defined"

# Validate budget compliance
budget_summary = tasks_data.get("budget_summary", {})
total_budget = metadata.get("total_budget", 30)
actual_count = budget_summary.get("total", 0)
assert actual_count <= total_budget, f"Task count {actual_count} exceeds budget {total_budget}"

# Validate required fields for each task
for task in tasks:
    assert task.get("id"), "Task missing id"
    assert task.get("title"), "Task missing title"
    assert task.get("priority") is not None, "Task missing priority"
```

| Check | Expected | Status |
|-------|----------|--------|
| File exists | ✓ | ✓/✗ |
| Valid YAML | ✓ | ✓/✗ |
| Tasks defined | > 0 | ✓/✗ |
| Within budget | tasks ≤ total_budget | ✓/✗ |
| Required fields | id, title, priority | ✓/✗ |

### 3. Validate Complexity Alignment

```
Expected: {{task_count_range[0]}}-{{task_count_range[1]}} tasks
Actual: {{tasks_created}} tasks
Status: [✓ Within range | ⚠️ Outside range]
```

### 4. Calculate Validation Score

```
Scorecard:
1. File Existence: /5 (PRD, Architecture, Logic, Config, Tasks YAML)
2. File Completeness: /4
3. Archon Project: /2
4. Archon Documents: /5 (4 outputs + Experiment Brief)
5. Tasks File Valid: /3 (schema, budget, required fields)
6. Complexity Alignment: /1
7. Document Consistency: /2
========================
Total: /22

Status:
- 20-22: ✅ EXCELLENT
- 16-19: ✅ GOOD
- 11-15: ⚠️ ACCEPTABLE
- <11: ❌ INCOMPLETE
```

### 5. Display Completion Summary

```
================================================================
🎉 PHASE 3 IMPLEMENTATION PLANNING - COMPLETE
================================================================

Hypothesis: {{hypothesis_id}}
Validation Score: {{total}}/22 ({{status}})

OUTPUT FOLDER: {{hypothesis_folder}}

FILES CREATED:
1. PRD: {{hypothesis_folder}}/03_prd.md
2. Architecture: {{hypothesis_folder}}/03_architecture.md
3. Logic: {{hypothesis_folder}}/03_logic.md
4. Config: {{hypothesis_folder}}/03_config.md
5. Tasks: {{hypothesis_folder}}/03_tasks.yaml

ARCHON PROJECT:
- Project ID: {{project_id}}
- Documents: 5 uploaded (4 outputs + Experiment Brief)
- Note: Tasks are in LOCAL file (03_tasks.yaml), not Archon

LOCAL TASKS FILE:
- File: {{hypothesis_folder}}/03_tasks.yaml
- Task count: {{tasks_count}} tasks
- Tier: {{tier}} (max {{total_budget}})
- Within budget: {{within_budget}}

NEXT STEPS - PHASE 4:

Option 1: /phase4-coding (Recommended - reads 03_tasks.yaml automatically)
Option 2: Manual execution using 03_tasks.yaml task list
Option 3: Reference 03_*.md documents for implementation details

Note: Phase 4 will track progress via local 04_checkpoint.yaml file.

================================================================
✅ Phase 3 Complete - Ready for Phase 4!
================================================================
```

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- All 5 files validated (PRD, Architecture, Logic, Config, Tasks YAML)
- Archon project verified with 5 documents
- **03_tasks.yaml validated** (schema, budget, required fields)
- Validation score calculated (scorecard completed)
- Comprehensive summary displayed
- Phase 4 guidance provided (with local task file reference)

### ❌ SYSTEM FAILURE:
- Skipping validation steps
- Score < 11/22 without warning to user
- **Not validating 03_tasks.yaml**
- **Expecting tasks in Archon**
- Not providing Phase 4 guidance
- Missing hypothesis folder path in summary
- Not displaying completion message

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

## Pipeline Task Update (Archon) - Current Hypothesis Only

<pipeline-completion>
<critical>
🔵 **PIPELINE TASK UPDATE - CURRENT HYPOTHESIS ONLY**

Update `verification_state.yaml` for the **current hypothesis** (`{{hypothesis_id}}`) only.
Do NOT check or report on other hypotheses' status — cross-hypothesis orchestration
is handled by `run_hypothesis_loop.py`, not by Phase 3.
</critical>

<action>**Update Current Hypothesis Status**

Update `{research_folder}/verification_state.yaml` for `{{hypothesis_id}}`:
- Set `implementation_planning.status` = "COMPLETED"
- Set `implementation_planning.completed_at` = current timestamp

Display:
```
Phase 3 Complete for {{hypothesis_id}}
  implementation_planning.status = COMPLETED
```

> **IMPORTANT:** Do NOT read or display other hypotheses' Phase 3 status.
> The hypothesis loop orchestrator manages cross-hypothesis progress tracking.
</action>
</pipeline-completion>

---

## WORKFLOW COMPLETE

Phase 3 ends here. All planning documents and Archon project are ready for Phase 4 implementation.
