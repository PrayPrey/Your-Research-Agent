---
name: 'archon_hypothesis_tasks'
description: 'Functions for creating and managing hypothesis-level tasks in the Pipeline Project'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - get_pipeline_project_id
  - create_hypothesis_tasks
  - update_hypothesis_task_status

# Called By
called_by:
  - 'phase2b-planning/steps/step-10-finalize.md'
  - 'phase4-coding/steps/step-01-initialize.md'
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-06b-reflection.md'
---

# Archon Hypothesis Task Helpers

> Functions for creating and managing hypothesis-level tasks in the Pipeline Project.
> Called by: Phase 2B step-10-finalize.md, Phase 4 step-01-initialize.md
>

---

## get_pipeline_project_id(verification_state)

Retrieve the Pipeline Project ID from verification_state.yaml.

```python
def get_pipeline_project_id(verification_state):
    """
    Get the unified Pipeline Project ID.


    Priority order:
    1. metadata.pipeline_project_id
    2. pipeline.project_id
    3. Raise explicit error (no search fallback)

    Args:
        verification_state: Loaded verification_state.yaml content

    Returns:
        str: Pipeline Project UUID

    Raises:
        ValueError: If pipeline_project_id not found in any location
    """
    # Priority 1: metadata.pipeline_project_id
    project_id = verification_state.get("metadata", {}).get("pipeline_project_id")

    # Priority 2: pipeline.project_id
    if not project_id:
        project_id = verification_state.get("pipeline", {}).get("project_id")
        if project_id:
            print(f"⚠ Using fallback location: pipeline.project_id")

    # Priority 3: Remove search fallback - raise explicit error
    # Note: find_projects(query="Anonymous Pipeline") is unreliable because:
    # - Project name is dynamic: "Anonymous Pipeline: {research_topic}"
    # - Multiple pipelines may exist, causing wrong project selection
    if not project_id:
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

    return project_id
```

---

## create_hypothesis_tasks(pipeline_project_id, hypotheses, verification_state)

Create placeholder tasks for each hypothesis in Phase 2B.

**Called by:** Phase 2B step-10-finalize.md

```python
def create_hypothesis_tasks(pipeline_project_id, hypotheses, verification_state, is_unattended=False):
    """
    Create a task for each hypothesis (H-E1, H-M1, etc.) in the Pipeline Project.

    Args:
        pipeline_project_id: UUID of the Pipeline Project
        hypotheses: Dict of hypothesis definitions from verification_state
        verification_state: Full state for dependency info
        is_unattended: If True, add [UNATTENDED] prefix to task descriptions

    Returns:
        dict: Mapping of hypothesis_id to task_id

    Example output:
        {"H-E1": "uuid-1", "H-M1": "uuid-2", "H-M2": "uuid-3", ...}
    """
    desc_prefix = "[UNATTENDED] " if is_unattended else ""

    task_mapping = {}

    # Priority ordering: H-E (100-90), H-M (89-50), H-C (49-30), H-CP (29-20)
    priority_map = {
        "E": 95, # Existence hypotheses
        "M": 80, # Mechanism hypotheses (decreasing)
        "C": 40, # Condition hypotheses
        "CP": 25 # Comparison hypotheses
    }

    for h_id, h_data in hypotheses.items():
        # Determine hypothesis type from ID (H-E1, H-M1, etc.)
        h_type = h_id.split("-")[1][0] if "-" in h_id else "M"
        h_num = int(h_id.split("-")[1][1:]) if len(h_id.split("-")[1]) > 1 else 1

        # Calculate priority (higher = earlier execution)
        base_priority = priority_map.get(h_type, 50)
        if h_type == "M":
            # H-M1 = 80, H-M2 = 79, H-M3 = 78, etc.
            base_priority = 80 - (h_num - 1)

        # Get gate type
        gate_type = h_data.get("gate", {}).get("type", "SHOULD_WORK")

        # Create task
        response = mcp__archon__manage_task(
            action="create",
            project_id=pipeline_project_id,
            title=f"[{h_id}] {h_data.get('statement', h_id)[:50]}...",
            description=f"""{desc_prefix}Hypothesis: {h_id}
Type: {h_data.get('type', 'UNKNOWN')}
Gate: {gate_type}

Statement:
{h_data.get('statement', 'No statement provided')}

Prerequisites: {h_data.get('prerequisites', [])}

---
This is a hypothesis-level task. Implementation subtasks will be added in Phase 3.
""",
            feature=h_id, # CRITICAL: Use hypothesis ID as feature
            task_order=base_priority,
            status="todo",
            assignee="User"
        )

        if response.get("success"):
            task_mapping[h_id] = response["task"]["id"]

    return task_mapping
```

---

## update_hypothesis_task_status(verification_state, hypothesis_id, new_status, description_prefix=None)

Update status of the Hypothesis-level task in Archon.

**Called by:** Phase 4 step-01-initialize.md, step-06-gate-processing.md, step-06b-reflection.md

> Implementation task status is tracked in local 04_checkpoint.yaml.

```python
def update_hypothesis_task_status(verification_state, hypothesis_id, new_status, description_prefix=None):
    """
    Update the status of the Hypothesis-level task in Archon.


    Args:
        verification_state: Loaded verification_state.yaml content
        hypothesis_id: e.g., "h-e1", "h-m1"
        new_status: "todo" | "doing" | "review" | "done"
        description_prefix: Optional prefix like "[FAILED]", "[SUPERSEDED]"

    Returns:
        bool: Success status
    """
    # Get task ID from mapping
    h_id = hypothesis_id.lower()
    task_id = verification_state.get("metadata", {}).get("hypothesis_task_mapping", {}).get(h_id)

    if not task_id:
        print(f"⚠ Hypothesis Task ID not found for {hypothesis_id}")
        return False

    params = {
        "action": "update",
        "task_id": task_id,
        "status": new_status
    }

    # Add description prefix if provided
    if description_prefix:
        params["description"] = f"{description_prefix} - Updated at {datetime.now().isoformat()}"

    response = mcp__archon__manage_task(**params)

    return response.get("success", False)
```

---
