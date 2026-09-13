---
name: 'archon_hypothesis_phase'
description: 'Functions for managing Phase Tasks per hypothesis in the hypothesis-loop'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - is_first_hypothesis #
  - get_or_create_hypothesis_phase_tasks
  - update_hypothesis_phase_status
  - sync_pipeline_phase_status

# Called By
called_by:
  - 'hypothesis-loop/instructions.md'
  - 'hypothesis-loop/steps/step-01-init.md'
  - 'hypothesis-loop/steps/step-04-loop-start.md'
---

# Archon Hypothesis-Level Phase Task Helpers

> Functions for managing Phase Tasks per hypothesis in the hypothesis-loop.
> **Option B Strategy:** ALL hypotheses (including H-E1) create `[H-XX] Phase 2C/3/4` tasks.
> Pipeline Phase 2C/3/4 tasks serve as "aggregate status" indicators only.
> Called by: hypothesis-loop/instructions.md, step-01-init.md, step-04-loop-start.md

---

## Constants

### HYPOTHESIS_PHASE_TITLES

```python
HYPOTHESIS_PHASE_TITLES = {
    "Phase 2C": "Phase 2C - Experiment",
    "Phase 3": "Phase 3 - Implementation",
    "Phase 4": "Phase 4 - Coding"
}
```

---

## ~~is_first_hypothesis~~ []

> Kept for backward compatibility with existing callers - will be.
> **Callers should remove this call and the is_first_hypothesis parameter.**

```python
def is_first_hypothesis(hypothesis_id, verification_state):
    """: Option B no longer differentiates first hypothesis.
    All hypotheses now create [H-XX] Phase 2C/3/4 tasks.

    Returns True for H-E1 for backward compatibility, but callers should
    remove this check entirely.
    """

    # This function should NOT be used - callers should remove the is_first_hypothesis check
    return hypothesis_id.lower() == "h-e1"
```

---

## get_or_create_hypothesis_phase_tasks(pipeline_project_id, hypothesis_id, verification_state)

Create `[H-XX] Phase 2C/3/4` tasks for a hypothesis, or return cached task IDs if already created.

**Called by:** hypothesis-loop/instructions.md at hypothesis start

> The `is_first_hypothesis` parameter is removed - all hypotheses follow the same path.
> Pipeline Phase 2C/3/4 tasks are synced separately via `sync_pipeline_phase_status()`.

```python
def get_or_create_hypothesis_phase_tasks(pipeline_project_id, hypothesis_id, verification_state, is_first_hypothesis=None):
    """
    Get or create Phase Tasks for a hypothesis.

    Strategy (Option B):
    - ALL hypotheses create "[H-XX] Phase 2C/3/4" tasks
    - Pipeline Phase 2C/3/4 tasks are aggregate status only (synced separately)

    Args:
        pipeline_project_id: UUID of the Pipeline Project
        hypothesis_id: Hypothesis ID (e.g., "h-e1", "h-m1")
        verification_state: Current verification_state dict (for caching task IDs)
        is_first_hypothesis: (ignored). Kept for backward compatibility.

    Returns:
        dict: {
            "success": True/False,
            "task_ids": {
                "Phase 2C": "task-uuid-1",
                "Phase 3": "task-uuid-2",
                "Phase 4": "task-uuid-3"
            },
            "created_new": False/True, # Whether new tasks were created
            "message": "..."
        }

     Changes:
        - Removed is_first_hypothesis differentiation
        - All hypotheses create [H-XX] prefixed tasks
        - Idempotency check applies to ALL hypotheses (including H-E1)
    """
    hypothesis_id_upper = hypothesis_id.upper() # e.g., "H-E1", "H-M1"
    hypothesis_id_lower = hypothesis_id.lower()
    task_ids = {}

    if is_first_hypothesis is not None:
        print(f"⚠ Warning: is_first_hypothesis parameter is (Option B)")

    # === ALL HYPOTHESES: Check cache first (idempotency) ===
    existing_mapping = verification_state.get("metadata", {}).get("hypothesis_phase_tasks", {})
    if hypothesis_id_lower in existing_mapping:
        cached_tasks = existing_mapping[hypothesis_id_lower]
        # Verify cache has all 3 phases
        if len(cached_tasks) == 3:
            return {
                "success": True,
                "task_ids": cached_tasks,
                "created_new": False,
                "message": f"Using cached [H-XX] Phase Tasks for {hypothesis_id_upper}"
            }

    # === CREATE NEW [H-XX] Phase Tasks ===
    # Priority: Between hypothesis placeholder (90) and implementation tasks (80-)
    base_priority = 85

    for i, (phase, title) in enumerate(HYPOTHESIS_PHASE_TITLES.items()):
        prefixed_title = f"[{hypothesis_id_upper}] {title}"

        response = mcp__archon__manage_task(
            action="create",
            project_id=pipeline_project_id,
            title=prefixed_title,
            description=f"Phase task for hypothesis {hypothesis_id_upper}. Auto-created by hypothesis-loop (Option B).",
            feature=hypothesis_id_upper, # Group with hypothesis tasks
            task_order=base_priority - i, # Phase 2C: 85, Phase 3: 84, Phase 4: 83
            status="todo",
            assignee="User"
        )

        if response.get("success"):
            task_ids[phase] = response["task"]["id"]
        else:
            return {
                "success": False,
                "task_ids": task_ids,
                "created_new": True,
                "message": f"Failed to create {prefixed_title}: {response.get('message')}"
            }

    return {
        "success": True,
        "task_ids": task_ids,
        "created_new": True,
        "message": f"Created 3 new [H-XX] Phase Tasks for {hypothesis_id_upper}"
    }
```

---

## update_hypothesis_phase_status(pipeline_project_id, hypothesis_id, phase, status, verification_state)

Update the status of a hypothesis's `[H-XX]` Phase Task.

**Called by:** Phase 2C/3/4 start and end steps

> The `is_first_hypothesis` parameter is and ignored.
> Cache lookup is attempted for ALL hypotheses.

```python
def update_hypothesis_phase_status(pipeline_project_id, hypothesis_id, phase, status, verification_state, is_first_hypothesis=None):
    """
    Update the status of a hypothesis's [H-XX] Phase Task (doing/done).

    Args:
        pipeline_project_id: UUID of the Pipeline Project
        hypothesis_id: Hypothesis ID (e.g., "h-e1", "h-m1")
        phase: Phase name ("Phase 2C", "Phase 3", or "Phase 4")
        status: New status ("doing" or "done")
        verification_state: verification_state dict for Task ID cache lookup.
        is_first_hypothesis: (ignored). Kept for backward compatibility.

    Returns:
        dict: {
            "success": True/False,
            "task_id": "...",
            "message": "...",
            "from_cache": True/False
        }

     Changes (Option B):
        - Removed is_first_hypothesis differentiation
        - Cache lookup applies to ALL hypotheses (including H-E1)
        - Search query always uses [H-XX] prefix
    """
    hypothesis_id_upper = hypothesis_id.upper()
    hypothesis_id_lower = hypothesis_id.lower()

    if is_first_hypothesis is not None:
        print(f"⚠ Warning: is_first_hypothesis parameter is (Option B)")

    # ===== : TRY CACHE FIRST (ALL hypotheses) =====
    if verification_state:
        cached_tasks = verification_state.get("metadata", {}).get("hypothesis_phase_tasks", {})
        cached_phase_ids = cached_tasks.get(hypothesis_id_lower, {})
        cached_task_id = cached_phase_ids.get(phase)

        if cached_task_id:
            # Cache hit! Update directly without searching
            update_response = mcp__archon__manage_task(
                action="update",
                task_id=cached_task_id,
                status=status
            )

            if update_response.get("success"):
                return {
                    "success": True,
                    "task_id": cached_task_id,
                    "message": f"Updated [{hypothesis_id_upper}] {phase} to '{status}' (from cache)",
                    "from_cache": True
                }
            else:
                # Cache hit but update failed - fall through to search
                print(f"⚠ Cache hit but update failed for {cached_task_id}, falling back to search")

    # ===== FALLBACK: Search by [H-XX] prefix (Option B: always prefixed) =====
    search_query = f"[{hypothesis_id_upper}] {HYPOTHESIS_PHASE_TITLES[phase]}"

    # Find the task
    response = mcp__archon__find_tasks(
        project_id=pipeline_project_id,
        query=search_query
    )

    if not response.get("success") or not response.get("tasks"):
        return {
            "success": False,
            "task_id": None,
            "message": f"[H-XX] Phase Task not found: {search_query}",
            "from_cache": False
        }

    # Find exact match (with [H-XX] prefix)
    task_id = None
    for task in response["tasks"]:
        task_title = task.get("title", "")
        if search_query in task_title:
            task_id = task["id"]
            break

    if not task_id:
        return {
            "success": False,
            "task_id": None,
            "message": f"Exact [H-XX] Phase Task not found: {search_query}",
            "from_cache": False
        }

    # Update status
    update_response = mcp__archon__manage_task(
        action="update",
        task_id=task_id,
        status=status
    )

    if update_response.get("success"):
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Updated {search_query} to '{status}'",
            "from_cache": False
        }
    else:
        return {
            "success": False,
            "task_id": task_id,
            "message": f"Failed to update: {update_response.get('message')}",
            "from_cache": False
        }
```

---

## sync_pipeline_phase_status(pipeline_project_id, phase, verification_state) [NEW ]

Synchronize Pipeline Phase Task status based on all hypothesis phase tasks.

**Called by:** hypothesis-loop/instructions.md after each phase status update

> - ANY hypothesis doing Phase X → Pipeline Phase X = "doing"
> - ALL hypotheses done Phase X → Pipeline Phase X = "done"
> - Otherwise → Pipeline Phase X = "todo"

```python
def sync_pipeline_phase_status(pipeline_project_id, phase, verification_state):
    """
    Sync Pipeline Phase Task status based on all hypothesis phase tasks.

    Option B Logic:
    - If ANY hypothesis has this phase as "doing" → Pipeline = "doing"
    - If ALL hypotheses have this phase as "done" → Pipeline = "done"
    - Otherwise → Pipeline = "todo"

    Args:
        pipeline_project_id: UUID of the Pipeline Project
        phase: Phase name ("Phase 2C", "Phase 3", or "Phase 4")
        verification_state: Current verification_state dict

    Returns:
        dict: {
            "success": True/False,
            "pipeline_status": "todo"|"doing"|"done",
            "pipeline_task_id": "uuid",
            "hypothesis_statuses": {"h-e1": "doing", "h-m1": "todo", ...},
            "message": "..."
        }

    Prerequisites:
        - verification_state.metadata.pipeline_phase_task_ids must contain Pipeline Task IDs
        - verification_state.metadata.hypothesis_phase_tasks must contain [H-XX] Task IDs
    """
    # === 1. Get Pipeline Phase Task ID from cache ===
    pipeline_task_ids = verification_state.get("metadata", {}).get("pipeline_phase_task_ids", {})
    pipeline_task_id = pipeline_task_ids.get(phase)

    if not pipeline_task_id:
        return {
            "success": False,
            "pipeline_status": None,
            "pipeline_task_id": None,
            "hypothesis_statuses": {},
            "message": f"Pipeline Task ID not found for {phase}. Run Phase 0 with Option B support."
        }

    # === 2. Get all hypothesis phase task IDs ===
    hypothesis_phase_tasks = verification_state.get("metadata", {}).get("hypothesis_phase_tasks", {})

    if not hypothesis_phase_tasks:
        # No hypotheses created yet - Pipeline stays at current status
        return {
            "success": True,
            "pipeline_status": "todo",
            "pipeline_task_id": pipeline_task_id,
            "hypothesis_statuses": {},
            "message": "No hypothesis phase tasks found - Pipeline status unchanged"
        }

    # === 3. Collect hypothesis statuses for this phase ===
    hypothesis_statuses = {}
    any_doing = False
    all_done = True

    for h_id, phase_tasks in hypothesis_phase_tasks.items():
        task_id = phase_tasks.get(phase)
        if not task_id:
            # This hypothesis doesn't have this phase task yet
            hypothesis_statuses[h_id] = "not_created"
            all_done = False
            continue

        # Query task status from Archon
        response = mcp__archon__find_tasks(task_id=task_id)
        if response.get("success") and response.get("tasks"):
            status = response["tasks"][0].get("status", "todo")
            hypothesis_statuses[h_id] = status

            if status == "doing":
                any_doing = True
            if status != "done":
                all_done = False
        else:
            hypothesis_statuses[h_id] = "unknown"
            all_done = False

    # === 4. Determine Pipeline status ===
    if any_doing:
        pipeline_status = "doing"
    elif all_done and len(hypothesis_statuses) > 0:
        pipeline_status = "done"
    else:
        pipeline_status = "todo"

    # === 5. Update Pipeline Phase Task ===
    update_response = mcp__archon__manage_task(
        action="update",
        task_id=pipeline_task_id,
        status=pipeline_status
    )

    if update_response.get("success"):
        return {
            "success": True,
            "pipeline_status": pipeline_status,
            "pipeline_task_id": pipeline_task_id,
            "hypothesis_statuses": hypothesis_statuses,
            "message": f"Pipeline {phase} synced to '{pipeline_status}'"
        }
    else:
        return {
            "success": False,
            "pipeline_status": pipeline_status,
            "pipeline_task_id": pipeline_task_id,
            "hypothesis_statuses": hypothesis_statuses,
            "message": f"Failed to update Pipeline {phase}: {update_response.get('message')}"
        }
```

---

