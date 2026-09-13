---
name: 'archon_phase_reset'
description: 'Functions for resetting/terminating Archon Pipeline tasks on routing'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - reset_phase_tasks
  - terminate_pipeline_on_phase0_routing

# Called By
called_by:
  - 'phase4-coding/steps/step-08-completion.md'
  - 'phase5-baseline-repo-comparison/steps/step-10b-finalize.md'
---

# Archon Phase Reset Helpers

> Functions for resetting Phase Tasks when routing occurs (Phase 4 FAIL → Phase 0, Phase 4 PARTIAL → Phase 2A-Dialogue, Phase 5 PARTIAL → Phase 0).
> Called by: Phase 4 step-08-completion.md, Phase 5 step-10b-finalize.md

---

## Constants

### PHASE_TASK_TITLES

```python
PHASE_TASK_TITLES = {
    "Phase 0": "Phase 0 - Brainstorm",
    "Phase 1": "Phase 1 - Research",
    "Phase 2A-Dialogue": "Phase 2A-Dialogue - Hypothesis",
    "Phase 2B": "Phase 2B - Planning",
    "Phase 2C": "Phase 2C - Experiment",
    "Phase 3": "Phase 3 - Implementation",
    "Phase 4": "Phase 4 - Coding",
    "Phase 5": "Phase 5 - Baseline Comparison",
    "Phase 6": "Phase 6 - Paper Writing",
    "Phase 6.5": "Phase 6.5 - Adversarial Review"
}
```

---

## reset_phase_tasks(pipeline_project_id, route_destination, current_phase)

Reset Phase Tasks when routing to earlier phase due to gate failure.

**Called by:** Phase 4 step-06b-reflection.md, Phase 5 step-10b-finalize.md

```python
def reset_phase_tasks(pipeline_project_id, route_destination, current_phase):
    """
    Reset Phase Tasks when routing occurs.

    Routing rules:
    - Phase 4 FAIL → Phase 0: Reset Phase 0→doing, Phase 1~4→todo
    - Phase 4 PARTIAL (max) → Phase 2A-Dialogue: Reset Phase 2A→doing, Phase 2B~4→todo
      (Execute /phase2a-dialogue workflow for full hypothesis regeneration)
    - Phase 5 PARTIAL → Phase 0: Reset Phase 0→doing, Phase 1~4→todo

    Note: Phase 5, 6, 6.5 tasks are NEVER reset (preserved for potential future attempt)

    Args:
        pipeline_project_id: UUID of the Pipeline Project
        route_destination: "Phase 0" or "Phase 2A-Dialogue"
        current_phase: "Phase 4" or "Phase 5" (where the failure occurred)

    Returns:
        dict: Summary of actions taken
              {
                  "reset_count": 5,
                  "doing_task": "Phase 0 - Brainstorm",
                  "todo_tasks": ["Phase 1 - Research", ...]
              }
    """
    # Define reset ranges based on destination
    if route_destination == "Phase 0":
        # Reset: Phase 0 (doing), Phase 1~4 (todo)
        doing_phase = "Phase 0"
        todo_phases = ["Phase 1", "Phase 2A-Dialogue", "Phase 2B", "Phase 2C", "Phase 3", "Phase 4"]

    elif route_destination == "Phase 2A-Dialogue":
        # Reset: Phase 2A-Dialogue (doing), Phase 2B~4 (todo)
        # NOTE: Execute /phase2a-dialogue workflow for full hypothesis regeneration
        doing_phase = "Phase 2A-Dialogue"
        todo_phases = ["Phase 2B", "Phase 2C", "Phase 3", "Phase 4"]

    else:
        # Unknown destination
        return {
            "reset_count": 0,
            "doing_task": None,
            "todo_tasks": [],
            "error": f"Unknown route destination: {route_destination}"
        }

    reset_count = 0
    todo_tasks = []
    doing_task = None

    # Find and update each Phase Task
    for phase, title in PHASE_TASK_TITLES.items():
        # Query task by title pattern
        response = mcp__archon__find_tasks(
            project_id=pipeline_project_id,
            query=title
        )

        if not response.get("success") or not response.get("tasks"):
            continue

        # Find exact match
        task = None
        for t in response.get("tasks", []):
            if t.get("title") == title:
                task = t
                break

        if not task:
            continue

        task_id = task["id"]
        current_status = task.get("status", "")

        # Determine new status
        new_status = None

        if phase == doing_phase:
            # This is the destination phase - set to 'doing'
            if current_status != "doing":
                new_status = "doing"
                doing_task = title

        elif phase in todo_phases:
            # These phases need to be reset to 'todo'
            if current_status != "todo":
                new_status = "todo"
                todo_tasks.append(title)

        # Update task if status needs to change
        if new_status:
            mcp__archon__manage_task(
                action="update",
                task_id=task_id,
                status=new_status
            )
            reset_count += 1

    return {
        "reset_count": reset_count,
        "doing_task": doing_task,
        "todo_tasks": todo_tasks
    }
```

---

## terminate_pipeline_on_phase0_routing(pipeline_project_id, failure_source, failure_reason)

Terminate entire Pipeline when routing to Phase 0. Unlike `reset_phase_tasks()` which prepares for re-execution,
this function **closes** the current Pipeline permanently (Phase 0 will create a new Pipeline).

**Called by:** Phase 4 step-06b-reflection.md (MUST_WORK FAIL), Phase 5 step-10b-finalize.md (DETERMINES_SUCCESS PARTIAL)

```python
def terminate_pipeline_on_phase0_routing(pipeline_project_id, failure_source, failure_reason):
    """
    Terminate Pipeline when routing to Phase 0 (new Pipeline will be created).

    This is called when:
    - Phase 4 MUST_WORK gate FAIL → Phase 0 (fundamental flaw)
    - Phase 5 DETERMINES_SUCCESS gate PARTIAL → Phase 0 (approach failed)

    NOTE: Phase 0 always creates a NEW Pipeline Project.
          This function closes the CURRENT Pipeline before Phase 0 creates the new one.
          Failure context is passed via Serena Memory (not Archon).

    Args:
        pipeline_project_id: UUID of the Pipeline Project to terminate
        failure_source: "Phase 4" or "Phase 5" (where the failure occurred)
        failure_reason: Descriptive reason for failure (e.g., "MUST_WORK_FAIL - Fundamental flaw detected")

    Returns:
        dict: Summary of actions taken
              {
                  "success": True,
                  "terminated_count": 10,
                  "project_updated": True,
                  "message": "Pipeline terminated: 10 tasks marked done"
              }
    """
    terminated_count = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Mark all Phase Tasks as "done" with [TERMINATED] prefix
    for phase, title in PHASE_TASK_TITLES.items():
        # Query task by title pattern
        response = mcp__archon__find_tasks(
            project_id=pipeline_project_id,
            query=title
        )

        if not response.get("success") or not response.get("tasks"):
            continue

        # Find exact match
        task = None
        for t in response.get("tasks", []):
            if t.get("title") == title:
                task = t
                break

        if not task:
            continue

        task_id = task["id"]
        current_status = task.get("status", "")
        current_desc = task.get("description", "")

        # Skip if already done (avoid duplicate [TERMINATED] prefix)
        if current_status == "done" and "[TERMINATED]" in current_desc:
            continue

        # Update task: status=done, description=[TERMINATED] prefix
        new_description = f"[TERMINATED] {timestamp} - {failure_reason}\n\n{current_desc}"

        mcp__archon__manage_task(
            action="update",
            task_id=task_id,
            status="done",
            description=new_description
        )
        terminated_count += 1

    # 2. Update Pipeline Project title with [FAILED] prefix
    project_updated = False
    project_response = mcp__archon__find_projects(project_id=pipeline_project_id)

    if project_response.get("success") and project_response.get("projects"):
        project = project_response["projects"][0]
        current_title = project.get("title", "")
        current_desc = project.get("description", "")

        # Add [FAILED] prefix if not already present
        if not current_title.startswith("[FAILED]"):
            new_title = f"[FAILED] {current_title}"
            new_project_desc = f"[TERMINATED] {timestamp}\nFailure Source: {failure_source}\nReason: {failure_reason}\n\n{current_desc}"

            mcp__archon__manage_project(
                action="update",
                project_id=pipeline_project_id,
                title=new_title,
                description=new_project_desc
            )
            project_updated = True

    return {
        "success": True,
        "terminated_count": terminated_count,
        "project_updated": project_updated,
        "message": f"Pipeline terminated: {terminated_count} tasks marked done"
    }
```

---

