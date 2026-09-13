---
name: 'step-10-finalize'
description: 'Generate state files, update pipeline tasks, and complete workflow'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-10-finalize.md'
nextStepFile: null # Final step - no next step
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# State File References
verificationStateFile: '{research_output_path}/verification_state.yaml'
verificationStateTemplate: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/verification_state_template.yaml'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 10: Finalize & State Generation

## STEP GOAL:

Generate verification_state.yaml, update pipeline tasks in Archon, create hypothesis tasks, and complete the workflow.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on state file and task generation
- 🚫 FORBIDDEN to skip state file or task creation
- 💬 Approach: Complete all required system files
- 📋 This is the final step - workflow completes here

## EXECUTION PROTOCOLS:

- 🎯 Generate verification_state.yaml with all hypotheses
- 💾 Update pipeline tasks in Archon
- 📖 Create hypothesis tasks for Phase 2C
- 🚫 FORBIDDEN to complete without state file

## CONTEXT BOUNDARIES:

- Available context: Complete verification plan
- Focus: System file generation and task management
- Limits: This is the final step
- Dependencies: Step 9 must be completed with summary

---

## Actions

### 1. Initialize verification_state.yaml

<mandatory-action type="state-initialization">

**CRITICAL:** Create verification_state.yaml with all sub-hypotheses.

#### Step 1: Load Template

```python
template = Read(verification_state_template)
```

#### Step 2: Get Pipeline Project ID

```python
# Use pipeline_project_id from Step 0
if pipeline_project_id:
    print(f"✓ Using Pipeline Project: {pipeline_project_id}")
else:
    # Fallback search
    result = mcp__archon__find_projects(query=pipeline_project_title)
    if result.get("success") and result.get("projects"):
        pipeline_project_id = result["projects"][0]["id"]
```

#### Step 3: Build sub_hypotheses

```python
sub_hypotheses = {}

for h_id in generated_hypothesis_ids:
    h_spec = hypothesis_specifications[h_id]
    h_type = h_id.split("-")[1][0].upper()

    gate_type = "MUST_WORK" if (h_type == "E" or h_id.endswith("1")) else "SHOULD_WORK"

    # - No prerequisites → READY (can be processed immediately)
    # - Has prerequisites → NOT_STARTED (wait for prerequisites to complete)
    prereqs = h_spec.get("prerequisites", [])
    initial_status = "READY" if not prereqs else "NOT_STARTED"

    sub_hypotheses[h_id.lower()] = {
        "type": h_spec["type"],
        "statement": h_spec["statement"],
        "status": initial_status,
        "gate": {"type": gate_type, "satisfied": None},
        "prerequisites": prereqs,
        "experiment_design": {"status": "NOT_STARTED", "file": None},
        "implementation_planning": {"status": "NOT_STARTED"},
        "validation": {"status": "NOT_STARTED", "result": None},
        "version": 1,
        "completed": False
    }
```

#### Step 4: Write verification_state.yaml

```python
verification_state["metadata"]["project_name"] = project_name
verification_state["metadata"]["main_hypothesis_id"] = main_hypothesis_id
verification_state["metadata"]["pipeline_project_id"] = pipeline_project_id
verification_state["sub_hypotheses"] = sub_hypotheses
verification_state["statistics"]["total_sub_hypotheses"] = len(sub_hypotheses)

Write(verification_state_file, yaml.dump(verification_state))
Log(f"verification_state.yaml created with {len(sub_hypotheses)} sub-hypotheses")
```

</mandatory-action>

---

### 2. Pipeline Task Update (Archon)

```python
# 1. Mark Phase 2B as done
mcp__archon__manage_task(
    action="update",
    task_id="{phase2b_task_id}",
    status="done"
)

# 2. Mark Phase 2C as doing (ready to start)
mcp__archon__manage_task(
    action="update",
    task_id="{phase2c_task_id}",
    status="doing"
)
```

---

### 3. Create Hypothesis Tasks in Pipeline Project

<mandatory-action type="archon-hypothesis-task-creation">

**Prerequisites:** Section 1 must be completed (verification_state.yaml created)

```python
# Check if current Archon "doing" task has [UNATTENDED] prefix in description
is_unattended = False # Default to interactive mode
current_doing_task = mcp__archon__find_tasks(filter_by="status", filter_value="doing")
if current_doing_task.get("success") and current_doing_task.get("tasks"):
    doing_task_desc = current_doing_task["tasks"][0].get("description", "")
    is_unattended = doing_task_desc.startswith("[UNATTENDED]")

desc_prefix = "[UNATTENDED] " if is_unattended else ""

# Create a task for each hypothesis
hypothesis_task_mapping = {}

for h_id, h_data in verification_state["sub_hypotheses"].items():
    result = mcp__archon__manage_task(
        action="create",
        project_id=pipeline_project_id,
        title=f"Hypothesis {h_id.upper()}: {h_data['type']}",
        description=f"{desc_prefix}{h_data['statement']}",
        status="todo",
        feature="Hypothesis Verification"
    )
    if result.get("success"):
        hypothesis_task_mapping[h_id] = result["task"]["id"]

# Store mapping in verification_state
verification_state["metadata"]["hypothesis_task_mapping"] = hypothesis_task_mapping
Write(verification_state_file, yaml.dump(verification_state))

Log(f"Created {len(hypothesis_task_mapping)} hypothesis tasks")
```

</mandatory-action>

---

### 4. Final Actions

1. Update frontmatter in {outputFile}:
   ```yaml
   stepsCompleted: ["step-00-init-environment", "step-01-init-parsing",
                    "step-02-input-hypothesis", "step-03-hypothesis-generation",
                    "step-04-hypothesis-inventory", "step-05-risk-analysis",
                    "step-06-dependency-graph", "step-07-timeline-planning",
                    "step-08-dialectical-analysis", "step-09-summary",
                    "step-10-finalize"]
   status: complete
   completedAt: [timestamp]
   ```

2. **NO NEXT STEP** - Workflow is complete!

---

### 5. Display Completion Status

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    PHASE 2B COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Verification Plan Generated: {outputFile}
✅ State File Created: verification_state.yaml
✅ Pipeline Tasks Updated in Archon
✅ Hypothesis Tasks Created: {{total_hypothesis_count}} tasks

**Files Generated:**
- 02b_verification_plan.md (complete document)
- verification_state.yaml (Phase 2C integration)

**Next Steps:**
1. Review the verification plan
2. Run Phase 2C to design experiments for each hypothesis
3. Use /phase2c-experiment-design or /hypothesis-next skill

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6. Present FINAL MENU

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [Q] Quit → Phase 2B Complete</action>

Display: "**Workflow Complete!** [R] Review Output [P] Party Mode Celebration [Q] Quit"

#### Menu Handling Logic:

- IF R: Display output file summary
- IF P: Execute {partyModeWorkflow} for celebration
- IF Q: Exit workflow gracefully

**This is the FINAL step. No continuation to next step.**

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- verification_state.yaml created with all sub-hypotheses
- Pipeline tasks updated in Archon (Phase 2B done, Phase 2C doing)
- Hypothesis tasks created for each sub-hypothesis
- hypothesis_task_mapping stored in verification_state
- Output file marked as complete
- Completion message shown with Phase 2C guidance

### ❌ SYSTEM FAILURE:

- Missing verification_state.yaml
- Skipping pipeline task update
- Missing hypothesis task creation
- Not marking workflow as complete
- Not providing Phase 2C guidance

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
