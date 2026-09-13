---
name: 'archon_pipeline_creation'
description: 'Functions for creating Pipeline Project (Phase 0) and Phase-level Tasks'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - create_pipeline_phase_tasks

# Called By
called_by:
  - 'phase0-brainstorm/steps/step-00-init.md'
---

# Archon Pipeline Creation Helpers

> Functions for creating Pipeline Project (Phase 0) and Phase-level Tasks.
> Called by: Phase 0 step-00-init.md
> Only Pipeline Phase Tasks are active (managed in Archon). Step-level tasks
> are tracked via local checkpoint `current_step` field, not Archon.

---

## Constants

### PIPELINE_PHASE_KEY_TO_DISPLAY

```python
PIPELINE_PHASE_KEY_TO_DISPLAY = {
    "phase0": "Phase 0",
    "phase1": "Phase 1",
    "phase2a": "Phase 2A-Dialogue",
    "phase2b": "Phase 2B",
    "phase2c": "Phase 2C",
    "phase3": "Phase 3",
    "phase4": "Phase 4",
    "phase5": "Phase 5",
    "phase6": "Phase 6",
    "phase65": "Phase 6.5",
}
```

### PIPELINE_PHASE_TASKS

```python
PIPELINE_PHASE_TASKS = [
    {"key": "phase0", "title": "Phase 0 - Brainstorm", "order": 100, "initial": "doing"},
    {"key": "phase1", "title": "Phase 1 - Research", "order": 90, "initial": "todo"},
    {"key": "phase2a", "title": "Phase 2A-Dialogue - Hypothesis", "order": 80, "initial": "todo"},
    {"key": "phase2b", "title": "Phase 2B - Planning", "order": 70, "initial": "todo"},
    {"key": "phase2c", "title": "Phase 2C - Experiment", "order": 50, "initial": "todo"},
    {"key": "phase3", "title": "Phase 3 - Implementation", "order": 40, "initial": "todo"},
    {"key": "phase4", "title": "Phase 4 - Coding", "order": 30, "initial": "todo"},
    {"key": "phase5", "title": "Phase 5 - Baseline Comparison", "order": 20, "initial": "todo"},
    {"key": "phase6", "title": "Phase 6 - Paper Writing", "order": 10, "initial": "todo"},
    {"key": "phase65", "title": "Phase 6.5 - Adversarial Review", "order": 5, "initial": "todo"},
]
```

## create_pipeline_phase_tasks(project_title, project_description)

Create Pipeline Project and Phase Tasks for Phase 0.
Task count depends on `skip_baseline_comparison`: 9 tasks (skip) or 10 tasks (include Phase 5).

**Called by:** Phase 0 step-00-init.md (Section 0.5)

```python
def create_pipeline_phase_tasks(project_title, project_description="Research pipeline from brainstorm to implementation", is_unattended=False, skip_baseline_comparison=False):
    """
    Create Pipeline Project and Phase Tasks.

    Args:
        project_title: Project title (e.g., "Anonymous Pipeline: {research_topic}")
        project_description: Project description
        is_unattended: If True, add [UNATTENDED] prefix to task descriptions
        skip_baseline_comparison: If True, exclude Phase 5 task from creation
            Read from module.yaml → pipeline_options.skip_baseline_comparison

    Returns:
        dict: {
            "success": True/False,
            "pipeline_project_id": "uuid",
            "phase_task_ids": {"phase0": "uuid", "phase1": "uuid", ...},
            "pipeline_phase_task_ids": {"Phase 0": "uuid", "Phase 2C": "uuid", ...},
            "created_count": 9 or 10,
            "skip_baseline_comparison": True/False, # 
            "message": "..."
        }

     (Option B):
        - Added `pipeline_phase_task_ids` with display-friendly keys ("Phase 0", "Phase 2C", etc.)
        - This format is used by sync_pipeline_phase_status() for Option B sync
        - Caller should save this to verification_state.metadata.pipeline_phase_task_ids

    :
        - Added `skip_baseline_comparison` parameter
        - When True: Phase 5 task is NOT created (9 tasks total)
        - When False: Phase 5 task IS created (10 tasks total, default behavior)

    Execution:
        1. Create Pipeline Project via mcp__archon__manage_project
        2. Filter PIPELINE_PHASE_TASKS based on skip_baseline_comparison
        3. Create Phase Tasks via mcp__archon__manage_task (individual calls)
        4. Convert keys to display format for Option B sync
        5. Validate expected task count
    """
    desc_prefix = "[UNATTENDED] " if is_unattended else ""

    # Step 1: Create Pipeline Project
    project_result = mcp__archon__manage_project(
        action="create",
        title=project_title,
        description=project_description
    )

    if not project_result.get("success"):
        return {
            "success": False,
            "pipeline_project_id": None,
            "phase_task_ids": {},
            "pipeline_phase_task_ids": {},
            "created_count": 0,
            "skip_baseline_comparison": skip_baseline_comparison,
            "message": f"Failed to create project: {project_result.get('message')}"
        }

    pipeline_project_id = project_result["project"]["id"]
    phase_task_ids = {}

    # Step 2: Filter phase tasks based on skip_baseline_comparison
    tasks_to_create = [
        task_def for task_def in PIPELINE_PHASE_TASKS
        if not (skip_baseline_comparison and task_def["key"] == "phase5")
    ]
    expected_count = len(tasks_to_create) # 9 if skip, 10 if include

    # Step 3: Create Phase Tasks (individual calls, NOT loop)
    for task_def in tasks_to_create:
        result = mcp__archon__manage_task(
            action="create",
            project_id=pipeline_project_id,
            title=task_def["title"],
            description=f"{desc_prefix}{task_def['title']} - Pipeline execution phase",
            status=task_def["initial"],
            task_order=task_def["order"],
            feature="Pipeline"
        )

        if result.get("success"):
            phase_task_ids[task_def["key"]] = result["task"]["id"]

    # Step 4: Convert to display-friendly keys for Option B sync
    pipeline_phase_task_ids = {}
    for internal_key, task_id in phase_task_ids.items():
        display_key = PIPELINE_PHASE_KEY_TO_DISPLAY.get(internal_key)
        if display_key:
            pipeline_phase_task_ids[display_key] = task_id

    # Step 5: Validate
    created_count = len(phase_task_ids)

    if created_count != expected_count:
        return {
            "success": False,
            "pipeline_project_id": pipeline_project_id,
            "phase_task_ids": phase_task_ids,
            "pipeline_phase_task_ids": pipeline_phase_task_ids,
            "created_count": created_count,
            "skip_baseline_comparison": skip_baseline_comparison,
            "message": f"Only {created_count}/{expected_count} Phase Tasks created"
        }

    skip_note = " (Phase 5 skipped)" if skip_baseline_comparison else ""
    return {
        "success": True,
        "pipeline_project_id": pipeline_project_id,
        "phase_task_ids": phase_task_ids,
        "pipeline_phase_task_ids": pipeline_phase_task_ids,
        "created_count": expected_count,
        "skip_baseline_comparison": skip_baseline_comparison, # 
        "message": f"Pipeline Project and {expected_count} Phase Tasks created successfully{skip_note}"
    }
```

---

