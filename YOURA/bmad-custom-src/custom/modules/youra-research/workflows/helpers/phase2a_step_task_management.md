---
name: 'phase2a_step_task_management'
description: 'Functions for Phase 2A step-level Archon task creation, template rendering, and cross-step task transitions'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - create_step_tasks
  - render_step_tasks_yaml
  - transition_step_tasks
  - update_step_tasks_gap_id

# Called By
called_by:
  - 'phase2a-dialogue/steps/step-00-initialize.md'
  - 'phase2a-dialogue/steps/step-01-discussion.md'
  - 'phase2a-dialogue/steps/step-02-structuring.md'
---

# Phase 2A Step Task Management Helper Functions

> Functions for Phase 2A step-level Archon task creation, template rendering,
> and cross-step task status transitions.
>
> This helper consolidates the repeated task transition pattern that appears
> in all 3 Phase 2A step files into a single reusable function.
>
> **Note:** This helper is the canonical location for Phase 2A step-level
> task management.
>
> **Template File:** `{workflow_path}/templates/phase2a_step_tasks_template.yaml`

---

## Constants

### PHASE2A_STEP_TASKS

```python
# Step-level task definitions for Phase 2A-Dialogue
# Each task corresponds to a major execution step in the workflow
PHASE2A_STEP_TASKS = [
    {"key": "2A-0", "title": "2A-0: Gap Selection", "order": 100, "initial": "doing"},
    {"key": "2A-P", "title": "2A-P: Paper Preparation", "order": 95, "initial": "todo"},
    {"key": "2A-1", "title": "2A-1: Round Table Discussion", "order": 90, "initial": "todo"},
    {"key": "2A-2", "title": "2A-2: Hypothesis Synthesis", "order": 80, "initial": "todo"},
    {"key": "2A-3", "title": "2A-3: Advocate-Critic Refinement", "order": 70, "initial": "todo"},
]
```

### TASK_KEY_TO_YAML_KEY

```python
# Mapping from step task keys to YAML keys in phase2a_step_tasks.yaml
# Used by transition_step_tasks() to locate task entries in the YAML file
TASK_KEY_TO_YAML_KEY = {
    "2A-0": "gap_selection",
    "2A-P": "paper_prep",
    "2A-1": "discussion",
    "2A-2": "structuring",
    "2A-3": "refinement",
}
```

### TEMPLATE_PLACEHOLDERS

```python
# All {{placeholder}} keys used in phase2a_step_tasks_template.yaml
# render_step_tasks_yaml() substitutes these from the render_context dict
TEMPLATE_PLACEHOLDERS = [
    "version", "feature", "is_recursive", "pipeline_project_id", "gap_id",
    "timestamp",
    "task_id_2a_0", "task_id_2a_p", "task_id_2a_1", "task_id_2a_2", "task_id_2a_3",
    "source_phase", "source_hypothesis", "failure_type", "serena_memory",
]
```

---

## Functions

### 1. create_step_tasks

```python
def create_step_tasks(
    pipeline_project_id: str,
    feature: str,
    is_unattended: bool = True
) -> dict:
    """
    Create 5 step-level Archon tasks for Phase 2A-Dialogue progress tracking.

    Creates tasks defined in PHASE2A_STEP_TASKS constant via mcp__archon__manage_task.
    Phase 2A-Dialogue is always UNATTENDED, so task descriptions are prefixed accordingly.

    Args:
        pipeline_project_id: Archon project ID for the pipeline
        feature: Feature tag, e.g., "Phase2A-v1", "Phase2A-v2"
        is_unattended: Whether to prefix descriptions with "[UNATTENDED]" (default True)

    Returns:
        Dictionary containing:
            - success: bool - True if all 5 tasks created
            - step_task_ids: dict - Mapping from task key to Archon task ID
                e.g., {"2A-0": "t-abc123", "2A-P": "t-def456", ...}
            - created_count: int - Number of tasks successfully created
            - message: str - Summary message

    Usage:
        task_result = create_step_tasks(pipeline_project_id, "Phase2A-v1")
        step_task_ids = task_result["step_task_ids"]
        # → {"2A-0": "t-abc", "2A-P": "t-def", "2A-1": "t-ghi", "2A-2": "t-jkl", "2A-3": "t-mno"}
    """
    desc_prefix = "[UNATTENDED] " if is_unattended else ""
    step_task_ids = {}

    for task_def in PHASE2A_STEP_TASKS:
        result = mcp__archon__manage_task(
            action="create",
            project_id=pipeline_project_id,
            title=task_def["title"],
            description=f"{desc_prefix}{task_def['title']} - Phase 2A step execution",
            status=task_def["initial"],
            task_order=task_def["order"],
            feature=feature
        )

        if result.get("success"):
            step_task_ids[task_def["key"]] = result["task"]["id"]
            Log(f"Created task: {task_def['title']} (ID: {result['task']['id']})")
        else:
            Log(f"WARNING: Failed to create task {task_def['title']}: {result.get('message')}")

    created_count = len(step_task_ids)
    if created_count != 5:
        Log(f"WARNING: Only {created_count}/5 step tasks created. Some steps may not have Archon tracking.")

    return {
        "success": created_count == 5,
        "step_task_ids": step_task_ids,
        "created_count": created_count,
        "message": f"Created {created_count}/5 step tasks for {feature}",
    }
```

### 2. render_step_tasks_yaml

```python
def render_step_tasks_yaml(template_content: str, render_context: dict) -> str:
    """
    Render phase2a_step_tasks_template.yaml by substituting {{placeholder}} values.

    Pure string transformation function. Replaces all {{key}} patterns in the
    template with corresponding values from render_context.

    Args:
        template_content: Raw template string from phase2a_step_tasks_template.yaml
        render_context: Dictionary with placeholder keys and their values.
            Required keys (from TEMPLATE_PLACEHOLDERS):
                - version, feature, is_recursive, pipeline_project_id, gap_id, timestamp
                - task_id_2a_0, task_id_2a_p, task_id_2a_1, task_id_2a_2, task_id_2a_3
                - source_phase, source_hypothesis, failure_type, serena_memory

    Returns:
        Rendered YAML string with all {{placeholder}} values substituted

    Usage:
        template = Read("{templates.step_tasks}")
        render_context = {
            "version": "1", "feature": "Phase2A-v1",
            "is_recursive": "false", "pipeline_project_id": "p-abc",
            "gap_id": "GAP-001", "timestamp": "2026-02-26T10:00:00Z",
            "task_id_2a_0": "t-001", "task_id_2a_p": "t-002",
            "task_id_2a_1": "t-003", "task_id_2a_2": "t-004",
            "task_id_2a_3": "t-005",
            "source_phase": "null", "source_hypothesis": "null",
            "failure_type": "null", "serena_memory": "null",
        }
        rendered = render_step_tasks_yaml(template, render_context)
        Write(step_tasks_file, rendered)
    """
    result = template_content

    for key in TEMPLATE_PLACEHOLDERS:
        placeholder = "{{" + key + "}}"
        value = render_context.get(key, "")
        result = result.replace(placeholder, str(value))

    return result
```

### 3. transition_step_tasks

```python
def transition_step_tasks(
    step_tasks_file: str,
    transitions_spec: list,
    step_name: str,
    message: str
) -> dict:
    """
    Execute Archon task status transitions and update phase2a_step_tasks.yaml.

    Reads the step tasks YAML file, updates each specified task via
    mcp__archon__manage_task, appends a transition log entry, and writes back.

    This function consolidates the repeated task transition pattern from:
    - step-00 Section 7: 2A-0 → done, 2A-P → doing
    - step-01 Section 7: 2A-P → done, 2A-1 → done, 2A-2 → doing
    - step-02 Section 7: 2A-2 → done, 2A-3 → done

    Args:
        step_tasks_file: Path to phase2a_step_tasks.yaml
        transitions_spec: List of transition dicts, each with:
            - task_key: str - Key from TASK_KEY_TO_YAML_KEY (e.g., "2A-0", "2A-P")
            - new_status: str - Target status ("todo" | "doing" | "done")
        step_name: str - Current step file name for transition log (e.g., "step-00-initialize")
        message: str - Human-readable transition message for the log

    Returns:
        Dictionary containing:
            - success: bool - True if all transitions completed
            - step_tasks_data: dict - Updated YAML data (already written to file)
            - message: str - Summary

    Usage:
        # From step-00 Section 7:
        transition_result = transition_step_tasks(
            step_tasks_file=step_tasks_file,
            transitions_spec=[
                {"task_key": "2A-0", "new_status": "done"},
                {"task_key": "2A-P", "new_status": "doing"},
            ],
            step_name="step-00-initialize",
            message="Gap selection complete, starting paper preparation"
        )

        # From step-01 Section 7:
        transition_result = transition_step_tasks(
            step_tasks_file=step_tasks_file,
            transitions_spec=[
                {"task_key": "2A-P", "new_status": "done"},
                {"task_key": "2A-1", "new_status": "done"},
                {"task_key": "2A-2", "new_status": "doing"},
            ],
            step_name="step-01-discussion",
            message="Discussion converged, starting result structuring"
        )

        # From step-02 Section 7:
        transition_result = transition_step_tasks(
            step_tasks_file=step_tasks_file,
            transitions_spec=[
                {"task_key": "2A-2", "new_status": "done"},
                {"task_key": "2A-3", "new_status": "done"},
            ],
            step_name="step-02-structuring",
            message="Phase 2A complete — all output files generated"
        )
    """
    step_tasks_data = yaml.load(Read(step_tasks_file))

    transition_from_tasks = []
    transition_to_tasks = []

    for spec in transitions_spec:
        task_key = spec["task_key"]
        new_status = spec["new_status"]
        yaml_key = TASK_KEY_TO_YAML_KEY[task_key]

        # Get task ID from YAML
        task_id = step_tasks_data["tasks"][yaml_key]["id"]

        # Update via Archon API
        mcp__archon__manage_task(
            action="update",
            task_id=task_id,
            status=new_status
        )

        # Update local YAML data
        step_tasks_data["tasks"][yaml_key]["status"] = new_status

        # Track for transition log
        if new_status == "done":
            transition_from_tasks.append(task_key)
        else:
            transition_to_tasks.append(task_key)

    # Build transition log entry
    from_str = ", ".join(transition_from_tasks) if transition_from_tasks else "N/A"
    to_str = ", ".join(transition_to_tasks) if transition_to_tasks else "null"
    from_status = "done" if transition_from_tasks else "N/A"
    to_status = transition_to_tasks[0] if transition_to_tasks else "null"

    step_tasks_data["transitions"].append({
        "timestamp": current_timestamp(),
        "step": step_name,
        "from_task": from_str,
        "from_status": from_status,
        "to_task": to_str,
        "to_status": new_status if transition_to_tasks else "null",
        "message": message,
    })

    # Write back updated YAML
    Write(step_tasks_file, yaml.dump(step_tasks_data))

    return {
        "success": True,
        "step_tasks_data": step_tasks_data,
        "message": f"Transitioned: {from_str} → done; {to_str} → {new_status if transition_to_tasks else 'N/A'}",
    }
```

### 4. update_step_tasks_gap_id

```python
def update_step_tasks_gap_id(step_tasks_file: str, gap_id: str) -> dict:
    """
    Update the gap_id field in phase2a_step_tasks.yaml after gap selection.

    Called in step-00 Section 6.5 after the selected gap is determined.

    Args:
        step_tasks_file: Path to phase2a_step_tasks.yaml
        gap_id: Selected gap identifier (e.g., "GAP-001")

    Returns:
        Updated step_tasks_data dict

    Usage:
        update_step_tasks_gap_id(step_tasks_file, selected_gap["id"])
    """
    step_tasks_data = yaml.load(Read(step_tasks_file))
    step_tasks_data["gap_id"] = gap_id
    Write(step_tasks_file, yaml.dump(step_tasks_data))
    return step_tasks_data
```

---

## Cross-References

| Related Helper | Relationship |
|---------------|--------------|
| `phase2a_failure_context.md` | Provides `extract_failure_source_info()` output consumed by `render_step_tasks_yaml()` |
| `phase2a_discussion_init.md` | Creates discussion_log.md; runs between task creation and transition |

## Template File Reference

The `render_step_tasks_yaml()` function processes the template at:
`{workflow_path}/templates/phase2a_step_tasks_template.yaml`

See that file for the full list of `{{placeholder}}` positions and their expected types.
