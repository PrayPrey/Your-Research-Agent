---
name: 'step-08-archon-project'
description: 'Upload 5 documents to Pipeline Project (Unified Archon Management)'
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase3-implementation-planning'
thisStepFile: '{workflow_path}/steps/step-08-archon-project.md'
nextStepFile: '{workflow_path}/steps/step-09-generate-tasks.md'
workflowFile: '{workflow_path}/workflow.md'
verification_state_path: '{research_folder}/verification_state.yaml'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Task References: N/A - Orchestration workflow using Task agents instead of A/P elicitation
---

# Step 8: Upload Documents to Pipeline Project

**Progress: Step 8 of 10** | Next: Step 9 - Create Archon Tasks

---

## STEP GOAL:

Upload all 5 documents (4 Phase 3 outputs + Phase 2C experiment brief) to the unified Pipeline Project. Store real document_ids for subsequent task creation and future reference.

> All hypothesis tasks and documents are managed in the unified Pipeline Project.
> See: `workflows/helpers/archon_hypothesis_tasks.md` for implementation details.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:
- 🛑 NEVER skip document uploads - all 5 required
- 🔄 Use Archon MCP tools directly (mcp__archon__*)
- ✅ Use Pipeline Project ID from verification_state.yaml (NOT create new project)
- ✅ Store REAL document_ids in verification_state.yaml

---

## EXECUTION PROTOCOLS:

- 🎯 Get Pipeline Project ID from verification_state.yaml (metadata.pipeline_project_id)
- 💾 Upload all 5 documents via mcp__archon__manage_document
- 📖 Update verification_state.yaml with real document IDs
- 🚫 FORBIDDEN: Creating separate project per hypothesis
- 🚫 FORBIDDEN: Using fake/placeholder IDs; skipping any document upload

---

## CONTEXT BOUNDARIES:

- Available context: hypothesis_id, hypothesis_folder, all 03_*.md files, 02c_experiment_brief.md
- Focus: Document upload to unified Pipeline Project
- Limits: No task creation yet; documents only (tasks already exist from Phase 2B)
- Dependencies: All 4 documents verified in Step 7; Pipeline Project exists from Phase 0

---

## 🚨 UNATTENDED MODE ENFORCEMENT

```
┌────────────────────────────────────────────────────────────┐
│ REQUIRED: Get pipeline_project_id from verification_state │
│ REQUIRED: mcp__archon__manage_document × 5 (all docs) │
│ REQUIRED: Update verification_state.yaml with REAL IDs │
│ │
│ FORBIDDEN: Creating new project (use existing Pipeline) │
│ FORBIDDEN: Fake/placeholder IDs │
│ FORBIDDEN: Skipping any document upload │
└────────────────────────────────────────────────────────────┘
```

---

## EXECUTION SEQUENCE

### 1. Get Pipeline Project ID

> The hypothesis task already exists (created in Phase 2B).

```python
# Get Pipeline Project ID from verification_state.yaml

# Priority 1: metadata.pipeline_project_id
pipeline_project_id = verification_state.get("metadata", {}).get("pipeline_project_id")

# Priority 2: pipeline.project_id
if not pipeline_project_id:
    pipeline_project_id = verification_state.get("pipeline", {}).get("project_id")
    if pipeline_project_id:
        print(f"⚠ Using fallback location: pipeline.project_id")

# Priority 3: Remove search fallback - raise explicit error
# Note: find_projects(query="Anonymous Pipeline") is unreliable because:
# - Project name is dynamic: "Anonymous Pipeline: {research_topic}"
# - Multiple pipelines may exist, causing wrong project selection
if not pipeline_project_id:
    raise ValueError(
        "Pipeline Project ID not found in verification_state.yaml.\n"
        "Expected locations:\n"
        " - metadata.pipeline_project_id\n"
        " - pipeline.project_id\n"
        "\n"
        "Resolution:\n"
        " 1. Run Phase 0 to create Pipeline Project, OR\n"
        " 2. Add pipeline_project_id manually to verification_state.yaml"
    )

# Verify hypothesis task exists (created in Phase 2B)
hypothesis_task_id = verification_state.get("metadata", {}).get("hypothesis_task_mapping", {}).get(hypothesis_id)
if hypothesis_task_id:
    print(f"✓ Hypothesis task exists: {hypothesis_task_id}")
else:
    print(f"⚠ Hypothesis task not found - will be created in Step 9")
```

Store: `project_id = pipeline_project_id`

### 2. Upload 5 Documents

| # | Document | Type | Tags |
|---|----------|------|------|
| 1 | PRD | spec | [prd, requirements, phase3] |
| 2 | Architecture | design | [architecture, design, phase3] |
| 3 | Logic | design | [logic, api, tensor_shapes, phase3] |
| 4 | Config | design | [config, yaml, dataclass, phase3] |
| 5 | Experiment Design | spec | [experiment_design, phase2c, research] |

For each document:
```python
mcp__archon__manage_document(
    action="create",
    project_id=project_id,
    title=f"{DocType}: {hypothesis_id}",
    document_type=type,
    content={"markdown": file_content},
    tags=tags,
    author=user_name
)
```

### 3. Update verification_state.yaml

> Use `metadata.pipeline_project_id` for the unified project.
> Document IDs are still stored per hypothesis for reference.

```yaml
# Note: pipeline_project_id is already set in metadata (from Phase 0/2B)
sub_hypotheses:
  {{hypothesis_id}}:
    implementation_planning:
      status: "IN_PROGRESS"
      # archon_project_id: - use metadata.pipeline_project_id
      archon_document_ids:
        prd: "{{doc_id}}"
        architecture: "{{doc_id}}"
        logic: "{{doc_id}}"
        config: "{{doc_id}}"
        experiment_design: "{{doc_id}}"
```

### 4. Display Summary

```
✓ Documents Uploaded to Pipeline Project

Pipeline Project ID: {{pipeline_project_id}}
Hypothesis: {{hypothesis_id}}
Documents: 5/5 uploaded
- PRD ✓
- Architecture ✓
- Logic ✓
- Config ✓
- Experiment Design ✓
```

### 5. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

**UNATTENDED Mode**: Auto-progress to Step 9
**Interactive Mode**: Display menu:

"**Select an Option:** [R] Review Archon Project [C] Continue [X] Exit"

#### Menu Handling Logic:
- IF R: Display project details and document upload status, return to menu
- IF C: Load next step
- IF X: Exit workflow gracefully

#### EXECUTION RULES:
- ALWAYS halt and wait for user input after presenting menu (Interactive mode)
- ONLY proceed to next step when user selects 'C' or UNATTENDED mode is active
- After other menu items execution, return to this menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN all 5 documents are uploaded AND verification_state.yaml is updated with real IDs, proceed to load and execute `{workflow_path}/steps/step-09-generate-tasks.md` for task file generation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Pipeline Project ID retrieved from verification_state.yaml
- All 5 documents uploaded successfully to Pipeline Project
- verification_state.yaml updated with real document IDs
- Document IDs stored for reference

### ❌ SYSTEM FAILURE:
- Creating new project per hypothesis ( - use Pipeline Project)
- Using fake/placeholder document IDs
- Missing any document uploads
- Not updating verification_state.yaml
- Not storing real document IDs

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

## BACKWARD COMPATIBILITY NOTE

For existing workflows with `archon_project_id` in `implementation_planning`:
- The old field is still readable for backward compatibility
- New workflows should use `metadata.pipeline_project_id`
- Phase 4 will check both: prefer `pipeline_project_id`, fallback to `archon_project_id`
