---
name: 'deferred_archon_operations'
description: 'Functions for deferred Archon/Archive/Terminate operations (executed in Step 08 after Report generation)'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - prepare_archon_operations_context
  - execute_deferred_archon_operations

# Called By
called_by:
  - 'phase4-coding/steps/step-06b-reflection.md' # prepare_archon_operations_context
  - 'phase4-coding/steps/step-08-completion.md' # execute_deferred_archon_operations

# Dependencies
dependencies:
  - archon_cascade.md
  - archon_phase_reset.md
  - archive_helpers.md
---

# Deferred Archon Operations Helper

> Functions for executing Archon/Archive/Terminate operations that are DEFERRED from Step 06b to Step 08.
> This ensures data integrity: Report (04_validation.md) is generated BEFORE external state changes.
>
> Called by: Phase 4 step-06b-reflection.md (prepare), step-08-completion.md (execute)

---

## Overview

When reflection occurs in Step 06b, routing decisions are made but NOT immediately executed.
Instead, the decision context is saved to checkpoint and operations are executed in Step 08.

**Flow:**
```
Step 06b Section 7:
  → prepare_archon_operations_context() # Save decision to checkpoint
  → update_verification_state_cascade() # Local state only (from archon_cascade.md)

Step 07:
  → Generate 04_validation.md # Report created FIRST

Step 08 Section 2.5:
  → execute_deferred_archon_operations() # Execute Archon/Archive/Terminate
```

---

## Constants

```python
# Reflection outcomes that require Archon operations
ROUTING_OUTCOMES = {
    "SELF_MODIFY": "Retry with modifications",
    "ROUTED_TO_PHASE_2A": "Superseded, route to Phase 2A-Dialogue",
    "ROUTED_TO_PHASE_0": "Failed, route to Phase 0",
    "FAILED": "Failed, no routing",
    "LIMITATION_RECORDED": "SHOULD_WORK failure, continue to Phase 5"
}
```

---

## prepare_archon_operations_context

Prepare checkpoint with deferred Archon operations context.
Called from Step 06b Section 7 to defer operations to Step 08.

```python
def prepare_archon_operations_context(
    checkpoint: dict,
    checkpoint_file: str,
    verification_state: dict,
    hypothesis_id: str,
    reflection_outcome: str,
    modification_attempt: int = 0,
    new_hypothesis_id: str = None,
    failure_reason: str = None
) -> dict:
    """
    Prepare checkpoint with context for deferred Archon operations.

    This function is called from Step 06b Section 7 AFTER reflection decision is made.
    The actual Archon/Archive/Terminate operations are executed in Step 08 Section 2.5
    AFTER Report generation completes.

    Args:
        checkpoint: Current checkpoint dictionary
        checkpoint_file: Path to checkpoint file for saving
        verification_state: Loaded verification_state.yaml content
        hypothesis_id: Current hypothesis ID (e.g., "H-E1")
        reflection_outcome: Decision from reflection (SELF_MODIFY, ROUTED_TO_PHASE_2A, etc.)
        modification_attempt: Current modification attempt number (for SELF_MODIFY)
        new_hypothesis_id: New hypothesis ID if created (e.g., "H-E1-v2")
        failure_reason: Reason for failure (for FAILED, ROUTED_TO_PHASE_0)

    Returns:
        Updated checkpoint dictionary

    Usage (in step-06b-reflection.md Section 7):
        from deferred_archon_operations import prepare_archon_operations_context

        checkpoint = prepare_archon_operations_context(
            checkpoint=checkpoint,
            checkpoint_file=checkpoint_file,
            verification_state=verification_state,
            hypothesis_id=hypothesis_id,
            reflection_outcome=reflection_outcome,
            modification_attempt=modification_attempt,
            new_hypothesis_id=new_hypothesis_id,
            failure_reason=failure_reason
        )
    """
    # Get IDs from verification_state metadata
    metadata = verification_state.get("metadata", {})
    hypothesis_task_id = metadata.get("hypothesis_task_mapping", {}).get(hypothesis_id)
    pipeline_project_id = metadata.get("pipeline_project_id")

    # Set pending flag and context
    checkpoint["archon_operations_pending"] = True
    checkpoint["archon_operations_context"] = {
        "reflection_outcome": reflection_outcome,
        "hypothesis_id": hypothesis_id,
        "hypothesis_task_id": hypothesis_task_id,
        "pipeline_project_id": pipeline_project_id,
        "new_hypothesis_id": new_hypothesis_id,
        "failure_reason": failure_reason,
        "modification_attempt": modification_attempt,
        "dependents": [] # Will be populated by cascade update
    }

    # Save checkpoint
    write_yaml(checkpoint_file, checkpoint)
    Log(f"✓ Archon operations deferred to Step 08: {reflection_outcome}")

    return checkpoint

def add_dependents_to_context(
    checkpoint: dict,
    checkpoint_file: str,
    dependents: list
) -> dict:
    """
    Add dependent hypotheses to the Archon operations context.
    Called after update_verification_state_cascade() finds dependents.

    Args:
        checkpoint: Current checkpoint dictionary
        checkpoint_file: Path to checkpoint file
        dependents: List of dependent hypothesis info from find_dependent_hypotheses()

    Returns:
        Updated checkpoint dictionary
    """
    if "archon_operations_context" in checkpoint:
        checkpoint["archon_operations_context"]["dependents"] = dependents
        write_yaml(checkpoint_file, checkpoint)
        Log(f"✓ Added {len(dependents)} dependents to Archon operations context")

    return checkpoint
```

---

## execute_deferred_archon_operations

Execute all deferred Archon/Archive/Terminate operations.
Called from Step 08 Section 2.5 AFTER Report generation.

```python
def execute_deferred_archon_operations(
    checkpoint: dict,
    checkpoint_file: str,
    verification_state: dict,
    research_folder: str
) -> dict:
    """
    Execute deferred Archon/Archive/Terminate operations from Step 06b.

    This function is called from Step 08 Section 2.5 AFTER Report generation.
    It reads the context saved by prepare_archon_operations_context() and
    executes the appropriate operations.

    Args:
        checkpoint: Current checkpoint dictionary (with archon_operations_context)
        checkpoint_file: Path to checkpoint file for saving completion status
        verification_state: Loaded verification_state.yaml content
        research_folder: Path to research folder (for archive operations)

    Returns:
        Updated checkpoint dictionary with archon_operations_completed = True

    Usage (in step-08-completion.md Section 2.5):
        from deferred_archon_operations import execute_deferred_archon_operations

        checkpoint = execute_deferred_archon_operations(
            checkpoint=checkpoint,
            checkpoint_file=checkpoint_file,
            verification_state=verification_state,
            research_folder=research_folder
        )
    """
    from archon_cascade import (
        update_dependent_hypothesis_tasks,
        mark_hypothesis_superseded
    )
    from archon_phase_reset import (
        reset_phase_tasks,
        terminate_pipeline_on_phase0_routing
    )
    from archive_helpers import (
        archive_for_phase0_routing,
        archive_for_phase2a_routing
    )

    # Check if operations are pending
    if not checkpoint.get("archon_operations_pending", False):
        Log(f"✓ No deferred Archon operations (PASS gate or no reflection)")
        return checkpoint

    # Extract context
    ctx = checkpoint.get("archon_operations_context", {})
    reflection_outcome = ctx.get("reflection_outcome")
    hypothesis_id = ctx.get("hypothesis_id")
    hypothesis_task_id = ctx.get("hypothesis_task_id")
    pipeline_project_id = ctx.get("pipeline_project_id")
    new_hypothesis_id = ctx.get("new_hypothesis_id")
    failure_reason = ctx.get("failure_reason")
    modification_attempt = ctx.get("modification_attempt", 0)
    dependents = ctx.get("dependents", [])

    Log(f"⚙ Executing deferred Archon operations for: {reflection_outcome}")

    # ========================================================================
    # STEP 1: Update Archon Hypothesis Task based on reflection_outcome
    # ========================================================================
    if hypothesis_task_id:
        if reflection_outcome == "SELF_MODIFY":
            mcp__archon__manage_task(
                action="update",
                task_id=hypothesis_task_id,
                status="doing",
                description=f"[RETRY] Self-modify attempt #{modification_attempt + 1}"
            )
            Log(f"✓ Hypothesis task updated: [RETRY] attempt #{modification_attempt + 1}")

        elif reflection_outcome == "ROUTED_TO_PHASE_2A":
            mark_hypothesis_superseded(
                hypothesis_task_id, hypothesis_id, new_hypothesis_id,
                "LLM self-assessment: incompatible with dependent hypotheses"
            )
            Log(f"✓ Hypothesis task marked: [SUPERSEDED → {new_hypothesis_id}]")

        elif reflection_outcome in ["FAILED", "ROUTED_TO_PHASE_0"]:
            mcp__archon__manage_task(
                action="update",
                task_id=hypothesis_task_id,
                status="done",
                description=f"[FAILED] {failure_reason}"
            )
            Log(f"✓ Hypothesis task marked: [FAILED]")

        elif reflection_outcome == "LIMITATION_RECORDED":
            Log(f"✓ SHOULD_WORK limitation recorded, continuing to Phase 5")

    # ========================================================================
    # STEP 2: Execute Archive and Terminate/Reset for Phase 0/2A routing
    # ========================================================================
    if reflection_outcome == "ROUTED_TO_PHASE_0" and pipeline_project_id:
        # Archive entire research folder FIRST
        archive_result = archive_for_phase0_routing(
            research_folder=research_folder,
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            failure_reason="MUST_WORK_FAIL - Fundamental flaw detected"
        )
        Log(f"✓ Research folder archived: {archive_result['archived_count']} files")

        # THEN terminate Pipeline
        terminate_result = terminate_pipeline_on_phase0_routing(
            pipeline_project_id=pipeline_project_id,
            failure_source="Phase 4",
            failure_reason="MUST_WORK_FAIL - Fundamental flaw detected"
        )
        Log(f"✓ Pipeline terminated: {terminate_result['message']}")

    elif reflection_outcome == "ROUTED_TO_PHASE_2A" and pipeline_project_id:
        # Archive Phase 2A+ results FIRST
        archive_result = archive_for_phase2a_routing(
            research_folder=research_folder,
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            supersede_reason=f"SUPERSEDED: {hypothesis_id} incompatible with dependents"
        )
        Log(f"✓ Phase 2A+ results archived: {archive_result['archived_count']} files")

        # THEN reset phase tasks
        reset_result = reset_phase_tasks(
            pipeline_project_id=pipeline_project_id,
            route_destination="Phase 2A-Dialogue", # Archon task name matching /phase2a-dialogue workflow
            current_phase="Phase 4"
        )
        Log(f"✓ Reset {reset_result['reset_count']} Phase Tasks for Phase 2A-Dialogue re-entry")

    # ========================================================================
    # STEP 3: Update Archon tasks for dependent hypotheses (cascade)
    # ========================================================================
    if len(dependents) > 0:
        if reflection_outcome == "SELF_MODIFY":
            update_dependent_hypothesis_tasks(
                verification_state, "BLOCKED", hypothesis_id, dependents, new_hypothesis_id
            )
        elif reflection_outcome == "ROUTED_TO_PHASE_2A":
            update_dependent_hypothesis_tasks(
                verification_state, "CASCADE_SUPERSEDED", hypothesis_id, dependents, new_hypothesis_id
            )
        elif reflection_outcome in ["FAILED", "ROUTED_TO_PHASE_0"]:
            update_dependent_hypothesis_tasks(
                verification_state, "CASCADE_FAILED", hypothesis_id, dependents
            )

        Log(f"✓ Archon cascade updated for {len(dependents)} dependent hypotheses")

    # ========================================================================
    # STEP 4: Mark Archon operations as completed
    # ========================================================================
    checkpoint["archon_operations_completed"] = True
    checkpoint["archon_operations_completed_at"] = datetime.now().isoformat()
    write_yaml(checkpoint_file, checkpoint)
    Log(f"✓ All deferred Archon operations completed")

    return checkpoint
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Missing context | Log warning, skip operations |
| Archon API failure | Retry 3 times, log error |
| Archive failure | Log error, continue with other operations |
| Missing hypothesis_task_id | Skip task update, log warning |

---

