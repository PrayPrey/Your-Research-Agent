---
name: 'archon_cascade'
description: 'Functions for handling dependent hypotheses when a parent hypothesis is modified, fails, or is superseded'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - find_dependent_hypotheses
  - mark_hypothesis_superseded
  - update_verification_state_cascade
  - update_dependent_hypothesis_tasks

# Called By
called_by:
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-06b-reflection.md' # verification_state only
  - 'phase4-coding/steps/step-08-completion.md' # Archon operations
---

# Archon Cascade Handling Helpers

> Functions for handling dependent hypotheses when a parent hypothesis is modified, fails, or is superseded.
> Called by: Phase 4 step-06-gate-processing.md, step-06b-reflection.md (verification_state only), step-08-completion.md (Archon operations)

---

## find_dependent_hypotheses(verification_state, hypothesis_id)

Find all hypotheses that depend on the specified hypothesis.

```python
def find_dependent_hypotheses(verification_state, hypothesis_id):
    """
    Find all hypotheses that have the given hypothesis as a prerequisite.

    Args:
        verification_state: Loaded verification_state.yaml content
        hypothesis_id: The hypothesis ID to find dependents for (e.g., "h-e1")

    Returns:
        list: List of dependent hypothesis IDs with their current status
              [{"id": "h-m1", "status": "READY", "type": "direct"},
               {"id": "h-m2", "status": "IN_PROGRESS", "type": "transitive"}]

    Note:
        - "direct": Directly depends on hypothesis_id
        - "transitive": Depends on a hypothesis that depends on hypothesis_id
    """
    sub_hypotheses = verification_state.get("sub_hypotheses", {})
    h_id_lower = hypothesis_id.lower()

    direct_dependents = []
    transitive_dependents = []

    # Find direct dependents (hypothesis_id in their prerequisites)
    for h_id, h_data in sub_hypotheses.items():
        prereqs = [p.lower() for p in h_data.get("prerequisites", [])]
        if h_id_lower in prereqs:
            direct_dependents.append({
                "id": h_id,
                "status": h_data.get("status", "READY"),
                "type": "direct"
            })

    # Find transitive dependents (depend on direct dependents)
    def find_transitive(dependent_id, visited):
        transitive = []
        for h_id, h_data in sub_hypotheses.items():
            if h_id in visited:
                continue
            prereqs = [p.lower() for p in h_data.get("prerequisites", [])]
            if dependent_id.lower() in prereqs:
                visited.add(h_id)
                transitive.append({
                    "id": h_id,
                    "status": h_data.get("status", "READY"),
                    "type": "transitive"
                })
                # Recursively find more transitive dependents
                transitive.extend(find_transitive(h_id, visited))
        return transitive

    visited = set([d["id"] for d in direct_dependents])
    for dep in direct_dependents:
        transitive_dependents.extend(find_transitive(dep["id"], visited))

    return direct_dependents + transitive_dependents
```

---

## mark_hypothesis_superseded(hypothesis_task_id, old_hypothesis_id, new_hypothesis_id, reason)

Mark a hypothesis task as SUPERSEDED in Archon.

**Called by:** Phase 4 step-06b-reflection.md when hypothesis needs Phase 2A redesign

```python
def mark_hypothesis_superseded(hypothesis_task_id, old_hypothesis_id, new_hypothesis_id, reason):
    """
    Mark a hypothesis task as SUPERSEDED in Archon.

     NEW: SUPERSEDED indicates the hypothesis had partial results but
    is incompatible with dependent hypotheses and needs Phase 2A redesign.

    This is different from FAILED:
    - FAILED: Complete failure, no useful results
    - SUPERSEDED: Partial results exist, but need fundamental redesign

    Args:
        hypothesis_task_id: UUID of the Hypothesis Task in Archon
        old_hypothesis_id: Original hypothesis ID (e.g., "h-e1")
        new_hypothesis_id: New hypothesis version ID (e.g., "h-e1-v2")
        reason: Reason for superseding (from LLM self-assessment)

    Returns:
        bool: Success status

    Side Effects:
        - Adds [SUPERSEDED] prefix to task title
        - Updates description with superseded info
        - Sets task status to "done"
    """
    from datetime import datetime

    # Get current task details
    response = mcp__archon__find_tasks(task_id=hypothesis_task_id)

    if not response.get("success"):
        print(f"⚠ Failed to fetch task {hypothesis_task_id}")
        return False

    tasks = response.get("tasks", [])
    if not tasks:
        print(f"⚠ Task {hypothesis_task_id} not found")
        return False

    task = tasks[0]
    old_title = task.get("title", "")
    old_desc = task.get("description", "")

    # Don't double-supersede
    if "[SUPERSEDED]" in old_title:
        print(f"⚠ Task already marked as SUPERSEDED")
        return True

    # Build new title with [SUPERSEDED] prefix
    new_title = f"[SUPERSEDED → {new_hypothesis_id}] {old_title}"

    # Build superseded info for description
    superseded_note = f"""🔄 SUPERSEDED: This hypothesis has been superseded

**Old Hypothesis:** {old_hypothesis_id}
**New Hypothesis:** {new_hypothesis_id}
**Superseded At:** {datetime.now().isoformat()}

**Reason:**
{reason}

**What This Means:**
- This hypothesis had PARTIAL results (some tests passed)
- LLM self-assessment determined incompatibility with dependent hypotheses
- A new hypothesis version will be designed in Phase 2A
- Partial results and lessons learned are preserved in Serena Memory

**Next Steps:**
- New hypothesis {new_hypothesis_id} enters Phase 2A for redesign
- Dependent hypotheses are marked CASCADE_SUPERSEDED

---
"""
    new_desc = superseded_note + old_desc

    # Update task in Archon
    update_response = mcp__archon__manage_task(
        action="update",
        task_id=hypothesis_task_id,
        title=new_title,
        description=new_desc,
        status="done" # Mark as done (completed with superseded outcome)
    )

    if update_response.get("success"):
        print(f"✓ Marked {old_hypothesis_id} as SUPERSEDED → {new_hypothesis_id}")
        return True
    else:
        print(f"⚠ Failed to update task: {update_response.get('message', 'Unknown error')}")
        return False
```

---

## update_verification_state_cascade(verification_state, action, source_hypothesis, affected_hypotheses, new_hypothesis_id=None)

Update verification_state.yaml with cascade status changes.

**Called by:** Phase 4 step-06-gate-processing.md, step-06b-reflection.md

```python
def update_verification_state_cascade(verification_state, action, source_hypothesis, affected_hypotheses, new_hypothesis_id=None):
    """
    Update verification_state.yaml with cascade status changes.

    Args:
        verification_state: Full verification state to update
        action: "BLOCKED" | "CASCADE_FAILED" | "CASCADE_SUPERSEDED" | "UNBLOCKED"
        source_hypothesis: Hypothesis that triggered the cascade
        affected_hypotheses: List of affected hypothesis IDs
        new_hypothesis_id: New version ID (for BLOCKED/CASCADE_SUPERSEDED action)

    Returns:
        dict: Updated verification_state

    Side Effects:
        - Updates sub_hypotheses status and cascade fields
        - Updates statistics
        - Adds to history

     CHANGE: Added CASCADE_SUPERSEDED action for SUPERSEDED hypotheses.
    """
    sub_hypotheses = verification_state.get("sub_hypotheses", {})
    timestamp = now_iso8601()

    for h_id in affected_hypotheses:
        h_id_lower = h_id.lower()
        if h_id_lower not in sub_hypotheses:
            continue

        h_data = sub_hypotheses[h_id_lower]

        if action == "BLOCKED":
            h_data["status"] = "BLOCKED"
            h_data["blocked_by"] = source_hypothesis
            h_data["awaiting"] = new_hypothesis_id

        elif action == "CASCADE_FAILED":
            h_data["status"] = "CASCADE_FAILED"
            h_data["failed_by"] = source_hypothesis
            h_data["blocked_by"] = None
            h_data["awaiting"] = None

        elif action == "CASCADE_SUPERSEDED":

            h_data["status"] = "CASCADE_SUPERSEDED"
            h_data["awaiting"] = new_hypothesis_id
            h_data["superseded"] = {
                "superseded_by": source_hypothesis,
                "superseded_at": timestamp,
                "superseded_reason": f"Cascade superseded by {source_hypothesis}",
                "partial_results_preserved": False
            }

        elif action == "UNBLOCKED":
            h_data["status"] = "READY"
            h_data["blocked_by"] = None
            h_data["awaiting"] = None
            h_data["superseded"] = None # Clear nested superseded object

        sub_hypotheses[h_id_lower] = h_data

    verification_state["sub_hypotheses"] = sub_hypotheses

    # Update statistics
    stats = verification_state.get("statistics", {})
    blocked_count = sum(1 for h in sub_hypotheses.values() if h.get("status") == "BLOCKED")
    failed_count = sum(1 for h in sub_hypotheses.values() if h.get("status") in ["FAILED", "CASCADE_FAILED"])
    superseded_count = sum(1 for h in sub_hypotheses.values() if h.get("status") in ["SUPERSEDED", "CASCADE_SUPERSEDED"])

    stats["blocked_sub_hypotheses"] = blocked_count
    stats["failed_sub_hypotheses"] = failed_count
    stats["superseded_sub_hypotheses"] = superseded_count
    verification_state["statistics"] = stats

    # Add to history
    history = verification_state.get("history", [])
    history.append({
        "event": f"Cascade {action}",
        "timestamp": timestamp,
        "source_hypothesis": source_hypothesis,
        "affected_hypotheses": affected_hypotheses,
        "new_hypothesis_id": new_hypothesis_id,
        "details": f"{len(affected_hypotheses)} hypotheses affected"
    })
    verification_state["history"] = history

    # Update metadata
    verification_state["metadata"]["last_updated"] = timestamp

    return verification_state
```

---

## update_dependent_hypothesis_tasks(verification_state, action, source_hypothesis, affected_hypotheses, new_hypothesis_id=None)

Update Archon tasks for dependent hypotheses when parent hypothesis fails or is superseded.

**Called by:** Phase 4 step-06b-reflection.md after update_verification_state_cascade()

```python
def update_dependent_hypothesis_tasks(verification_state, action, source_hypothesis, affected_hypotheses, new_hypothesis_id=None):
    """
    Update Archon tasks for dependent hypotheses.

    This function ensures Archon tasks are updated in sync with verification_state
    when a parent hypothesis fails, is superseded, or is blocked.

    Args:
        verification_state: Full verification state (for hypothesis_task_mapping)
        action: "BLOCKED" | "CASCADE_FAILED" | "CASCADE_SUPERSEDED"
        source_hypothesis: Hypothesis that triggered the cascade
        affected_hypotheses: List of affected hypothesis IDs (from find_dependent_hypotheses)
        new_hypothesis_id: New version ID (for BLOCKED/CASCADE_SUPERSEDED action)

    Returns:
        dict: {
            "success": True/False,
            "updated_count": int,
            "failed_updates": list,
            "message": str
        }

    Side Effects:
        - Updates dependent hypothesis task titles with cascade prefix
        - Updates task descriptions with cascade reason
        - Sets task status to appropriate state

     NEW: This function complements update_verification_state_cascade()
    to ensure both verification_state AND Archon tasks are updated together.
    """
    from datetime import datetime

    hypothesis_task_mapping = verification_state.get("metadata", {}).get("hypothesis_task_mapping", {})
    updated_count = 0
    failed_updates = []
    timestamp = datetime.now().isoformat()

    for dependent in affected_hypotheses:
        # Handle both dict format [{"id": "h-m1", ...}] and string format ["h-m1"]
        h_id = dependent["id"] if isinstance(dependent, dict) else dependent
        h_id_lower = h_id.lower()

        # Get Archon task ID for this hypothesis
        task_id = hypothesis_task_mapping.get(h_id_lower)

        if not task_id:
            failed_updates.append({
                "hypothesis_id": h_id,
                "reason": "No task ID in hypothesis_task_mapping"
            })
            continue

        # Fetch current task details
        response = mcp__archon__find_tasks(task_id=task_id)
        if not response.get("success") or not response.get("tasks"):
            failed_updates.append({
                "hypothesis_id": h_id,
                "reason": f"Task {task_id} not found in Archon"
            })
            continue

        task = response["tasks"][0]
        old_title = task.get("title", "")
        old_desc = task.get("description", "")

        # Build update based on action
        if action == "BLOCKED":
            # Hypothesis is blocked waiting for parent to complete retry
            prefix = f"[BLOCKED by {source_hypothesis}]"
            if prefix in old_title:
                continue # Already marked

            new_title = f"{prefix} {old_title}"
            cascade_note = f"""⏸️ BLOCKED: Waiting for prerequisite hypothesis

**Blocked At:** {timestamp}
**Blocked By:** {source_hypothesis}
**Awaiting:** {new_hypothesis_id} to complete

**What This Means:**
- This hypothesis cannot proceed until {source_hypothesis} passes
- {source_hypothesis} is retrying with modifications
- This hypothesis will be UNBLOCKED when {new_hypothesis_id} passes

---
"""
            new_desc = cascade_note + old_desc
            new_status = "todo" # Keep as todo (will be unblocked later)

        elif action == "CASCADE_FAILED":
            # Hypothesis cascade failed due to parent fundamental failure
            prefix = f"[CASCADE_FAILED from {source_hypothesis}]"
            if prefix in old_title:
                continue

            new_title = f"{prefix} {old_title}"
            cascade_note = f"""❌ CASCADE_FAILED: Prerequisite hypothesis fundamentally failed

**Failed At:** {timestamp}
**Failed By:** {source_hypothesis}

**What This Means:**
- Prerequisite hypothesis {source_hypothesis} has fundamentally failed
- This hypothesis cannot proceed as designed
- Routing to Phase 0 for new research direction

---
"""
            new_desc = cascade_note + old_desc
            new_status = "done" # Mark as done (failed outcome)

        elif action == "CASCADE_SUPERSEDED":
            # Hypothesis cascade superseded - parent needs Phase 2A redesign
            prefix = f"[CASCADE_SUPERSEDED → {new_hypothesis_id}]"
            if "[CASCADE_SUPERSEDED" in old_title:
                continue

            new_title = f"{prefix} {old_title}"
            cascade_note = f"""🔄 CASCADE_SUPERSEDED: Prerequisite hypothesis needs redesign

**Superseded At:** {timestamp}
**Superseded By:** {source_hypothesis} → {new_hypothesis_id}

**What This Means:**
- Prerequisite hypothesis {source_hypothesis} had partial results
- LLM self-assessment determined incompatibility with this hypothesis
- A new version {new_hypothesis_id} will be designed in Phase 2A
- This hypothesis will be re-evaluated after Phase 2A redesign

---
"""
            new_desc = cascade_note + old_desc
            new_status = "done" # Mark as done (superseded - new hypothesis will be created in Phase 2A)

        else:
            failed_updates.append({
                "hypothesis_id": h_id,
                "reason": f"Unknown action: {action}"
            })
            continue

        # Update task in Archon
        update_response = mcp__archon__manage_task(
            action="update",
            task_id=task_id,
            title=new_title,
            description=new_desc,
            status=new_status
        )

        if update_response.get("success"):
            updated_count += 1
            print(f"✓ Updated dependent task {h_id}: {action}")
        else:
            failed_updates.append({
                "hypothesis_id": h_id,
                "reason": f"Update failed: {update_response.get('message', 'Unknown error')}"
            })

    # Return summary
    success = updated_count > 0 or len(affected_hypotheses) == 0
    if failed_updates:
        print(f"⚠ {len(failed_updates)} dependent task updates failed")

    return {
        "success": success,
        "updated_count": updated_count,
        "failed_updates": failed_updates,
        "message": f"Updated {updated_count}/{len(affected_hypotheses)} dependent hypothesis tasks"
    }
```

---

