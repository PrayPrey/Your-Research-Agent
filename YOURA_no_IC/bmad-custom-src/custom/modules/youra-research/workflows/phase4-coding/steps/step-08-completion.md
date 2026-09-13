---
name: 'step-08-completion'
description: 'Completion - Cleanup checkpoint and finalize Phase 4'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# File References
thisStepFile: '{workflow_path}/steps/step-08-completion.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
verification_state: '{research_folder}/verification_state.yaml'
validation_report: '{hypothesis_folder}/04_validation.md'
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
code_folder: '{hypothesis_folder}/code'
---

## Helper References (BMAD v6)

<helper-reference>
**Helper:** `{helpers_path}/deferred_archon_operations.md`
**Function:** `execute_deferred_archon_operations(checkpoint, checkpoint_file, verification_state, research_folder)`
**Purpose:** Execute deferred Archon/Archive/Terminate operations from Step 06b
</helper-reference>

---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 8:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, hypothesis_id={checkpoint.hypothesis_id}")
```

---

# Step 8: Completion (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- This is the FINAL step - ensure all outputs verified
- MUST verify all required output files exist before completion
- MUST archive (not delete) checkpoint file with timestamp
- MUST use Read-Modify-Write pattern for verification_state.yaml
- MUST update benchmark_metrics for termination quality tracking
- MUST save verification state snapshot to Serena Memory when ALL hypotheses complete
- MUST update Archon Pipeline task only when ALL hypotheses complete
- Control returns to `/hypothesis-loop` after this step

---

## STEP GOAL

Complete Phase 4 workflow: cleanup checkpoint and update verification state.

---

## EXECUTION SEQUENCE

### 1. Verify Outputs

```python
required_files = [
    validation_report, # 04_validation.md
    code_folder, # Generated code
    verification_state # Updated verification_state.yaml
]

FOR file in required_files:
    IF NOT exists(file):
        completion_status = "incomplete"
```

### 1b. Validate Checkpoint-Verification State Sync

```python
from checkpoint_helpers import validate_checkpoint_verification_sync, sync_checkpoint_from_verification_state

# Load verification_state for sync validation
verification_state = read_yaml(verification_state_path)

# Validate sync
sync_result = validate_checkpoint_verification_sync(
    checkpoint,
    verification_state,
    hypothesis_id
)

IF NOT sync_result["synced"]:
    print(f"⚠ Checkpoint-verification_state sync issues detected:")
    FOR discrepancy in sync_result["discrepancies"]:
        print(f" - {discrepancy}")

    # Auto-sync before archiving
    sync_checkpoint_from_verification_state(
        checkpoint,
        checkpoint_file,
        verification_state,
        hypothesis_id
    )
    print(f"✓ Checkpoint auto-synced before archiving")
ELSE:
    print(f"✓ Checkpoint-verification_state sync validated")
```

### 1c. Validate Experiment Completion

> Option C selected: Deferred experiments are NOT allowed - workflow stops here.

```python
# ================================================================
# EXPERIMENT COMPLETION VALIDATION
# Option C: No deferred experiments - MUST execute before completion
# ================================================================

experiment_status = checkpoint.partial_results.experiment_status
gate_result = checkpoint.partial_results.gate_result

print(f"🔍 Validating experiment completion...")
print(f" experiment_status: {experiment_status}")
print(f" gate_result: {gate_result}")

# VALIDATION: Experiment must be completed
IF experiment_status NOT IN ["completed", "skipped"]:
    print(f"")
    print(f"=" * 60)
    print(f"🚨 EXPERIMENT NOT EXECUTED - WORKFLOW STOPPED")
    print(f"=" * 60)
    print(f"")
    print(f"experiment_status: {experiment_status}")
    print(f"Expected: 'completed' or 'skipped'")
    print(f"")
    print(f"Option C (No Deferred) is active:")
    print(f" - Experiments MUST be executed before Phase 4 completion")
    print(f" - Deferred experiments are NOT allowed")
    print(f"")
    print(f"To resolve:")
    print(f" 1. Return to Step 5 (Experiment Execution)")
    print(f" 2. Execute the experiment")
    print(f" 3. Re-run Step 8 (Completion)")
    print(f"")

    # Update checkpoint with blocked status
    checkpoint.partial_results.completion_blocked = True
    checkpoint.partial_results.completion_blocked_reason = "Experiment not executed (Option C: No Deferred)"
    SAVE checkpoint

    STOP("WORKFLOW_BLOCKED: Experiment not executed. Cannot complete Phase 4.")

# VALIDATION: Gate must be evaluated
IF gate_result NOT IN ["PASS", "FAIL", "PARTIAL"]:
    print(f"")
    print(f"=" * 60)
    print(f"🚨 GATE NOT EVALUATED - WORKFLOW STOPPED")
    print(f"=" * 60)
    print(f"")
    print(f"gate_result: {gate_result}")
    print(f"Expected: 'PASS', 'FAIL', or 'PARTIAL'")
    print(f"")
    print(f"To resolve:")
    print(f" 1. Return to Step 6 (Gate Processing)")
    print(f" 2. Evaluate the gate")
    print(f" 3. Re-run Step 8 (Completion)")
    print(f"")

    # Update checkpoint with blocked status
    checkpoint.partial_results.completion_blocked = True
    checkpoint.partial_results.completion_blocked_reason = "Gate not evaluated"
    SAVE checkpoint

    STOP("WORKFLOW_BLOCKED: Gate not evaluated. Cannot complete Phase 4.")

print(f"✅ Experiment completion validated: {experiment_status}, Gate: {gate_result}")
```

### 2. Archive Checkpoint

```python
# Archive (don't delete) checkpoint
archive_name = f"04_checkpoint_archived_{timestamp}.yaml"
Rename(checkpoint_file, f"{hypothesis_folder}/{archive_name}")
```

### 2.5 Execute Archon/Archive/Terminate Operations

> Executes deferred operations from Step 06b AFTER Report generation.
>
> **Reference:** `{deferred_archon_operations}`

```python
from deferred_archon_operations import execute_deferred_archon_operations

# Execute all deferred Archon/Archive/Terminate operations
# This handles: SELF_MODIFY, ROUTED_TO_PHASE_2A, ROUTED_TO_PHASE_0, LIMITATION_RECORDED
checkpoint = execute_deferred_archon_operations(
    checkpoint=checkpoint,
    checkpoint_file=checkpoint_file,
    verification_state=verification_state,
    research_folder=research_folder
)
```

### 3. Update Verification State (Final)

🚨 **Use Read-Modify-Write pattern for verification_state.yaml**

**3a. Record Phase 4 completion for current hypothesis:**

Add the following to `hypotheses.{hypothesis_id}.validation.phase4`:

| Field | Value |
|-------|-------|
| status | "completed" |
| completed_at | Current timestamp |
| validation_report | "04_validation.md" |
| code_location | "code/" |
| gate_result | Experiment result (PASS/FAIL/PARTIAL) |
| archived_checkpoint | Archived checkpoint filename |

**3b. Update Statistics:**
- Increment `statistics.phases_completed.phase_4` by 1

**4c. Append to Status History:**

Add status history entry for the **current hypothesis only**:

| Field | Value |
|-------|-------|
| status | "ACTIVE" |
| phase | "Phase 4" |
| timestamp | Current timestamp |
| trigger | "Hypothesis validation completed" |
| hypothesis_id | Current hypothesis ID |
| gate_result | Experiment result |
| details | "{hypothesis_id} validation completed with {result}" |

> **IMPORTANT:** Do NOT check other hypotheses' completion status here.
> Cross-hypothesis aggregation (setting `workflow.current_phase = "Phase 5"`,
> `workflow.status = "COMPLETED"`, etc.) is handled by `run_hypothesis_loop.py`
> after all hypotheses finish.

**3d. Save File:**
Write modified verification_state.yaml to the same path

### 5. Update Archon Tasks (Final)

```python
# Verify all tasks in final state
# No tasks should remain in: todo, doing, review
# All should be: done
```

### 5. Pipeline Task Update - Current Hypothesis Only

```python
# Update verification_state.yaml for the CURRENT hypothesis only
# Do NOT check other hypotheses' status — cross-hypothesis orchestration
# is handled by run_hypothesis_loop.py, not by Phase 4.

state = load_yaml(verification_state_file)
state.sub_hypotheses[hypothesis_id].validation.status = "COMPLETED"
state.sub_hypotheses[hypothesis_id].validation.completed_at = now()
save_verification_state(state)

display: f"Phase 4 Complete for {hypothesis_id}"
display: f" validation.status = COMPLETED"
# IMPORTANT: Do NOT read or display other hypotheses' Phase 4 status.
```

### 6. Save Current Hypothesis Snapshot to Serena Memory

#### ⚠️ SERENA MEMORY INTEGRATION - Hypothesis Snapshot

> Save current hypothesis completion snapshot for future Phase 2A runs.
> Cross-hypothesis aggregation is handled by the hypothesis loop orchestrator.

```python
# Save snapshot for the CURRENT hypothesis only
snapshot_content = f"""
# Hypothesis Completion Snapshot: {hypothesis_id}

**Date:** {ISO8601}
**Hypothesis:** {hypothesis_id}
**Statement:** {hypothesis.statement}
**Final Status:** {hypothesis.status}
**Gate Result:** {hypothesis.validation.result}

## Results
- Validation: {gate_result}
- Gate Type: {gate_type}
{IF hypothesis.reflection.triggered:}
- Reflection: {hypothesis.reflection.meaningful_findings_summary}
- Lessons: {hypothesis.reflection.lessons_learned}
{END IF}

---
*Per-hypothesis snapshot for Phase 2A reference*
"""

mcp__serena__write_memory(
    memory_file_name="snapshot_{hypothesis_id}_{timestamp}.md",
    content=snapshot_content
)
```

### 6.5 Update Benchmark Metrics - Termination Quality

🚨 **CRITICAL: Track proper termination for paper metrics**

```python
# ================================================================
# BENCHMARK METRIC 2: Termination Quality
# "Did the system terminate correctly based on gate conditions?"
# ================================================================

# 1. Increment termination events for this sub-hypothesis
episode.benchmark_metrics.termination_quality.total_termination_events += 1

# 2. Determine termination type based on gate result
gate_result = checkpoint.partial_results.gate_result
gate_type = checkpoint.partial_results.gate_type

# 3. Was this a proper (gate-based) termination?
IF gate_result IN ["PASS", "PARTIAL", "FAIL"]:
    # Gate-based termination = proper
    episode.benchmark_metrics.termination_quality.proper_terminations += 1
    proper = true

    # Track by trigger type
    IF gate_type == "MUST_WORK":
        IF gate_result == "PASS":
            # Not a termination, continuation to Phase 5
            pass
        ELIF gate_result == "PARTIAL":
            episode.benchmark_metrics.termination_quality.terminations_by_trigger.must_work_partial_routed += 1
        ELIF gate_result == "FAIL":
            episode.benchmark_metrics.termination_quality.terminations_by_trigger.must_work_fail += 1
ELSE:
    # Non-gate termination = improper
    episode.benchmark_metrics.termination_quality.improper_terminations += 1
    proper = false

    IF completion_status == "incomplete":
        episode.benchmark_metrics.termination_quality.terminations_by_trigger.system_error += 1

# 4. Check routing decision quality
IF gate_result == "PARTIAL" AND gate_type == "MUST_WORK":
    episode.benchmark_metrics.termination_quality.routing_decisions_made += 1

    # Was routing decision correct? (Phase 2A for PARTIAL)
    IF checkpoint.reflection_outcome == "ROUTED_TO_PHASE_2A":
        episode.benchmark_metrics.termination_quality.routing_decisions_correct += 1

ELIF gate_result == "FAIL" AND gate_type == "MUST_WORK":
    episode.benchmark_metrics.termination_quality.routing_decisions_made += 1

    # Was routing decision correct? (Phase 0 for FAIL)
    IF checkpoint.reflection_outcome == "ROUTED_TO_PHASE_0":
        episode.benchmark_metrics.termination_quality.routing_decisions_correct += 1

# 5. Calculate current proper termination rate
total = episode.benchmark_metrics.termination_quality.total_termination_events
proper_count = episode.benchmark_metrics.termination_quality.proper_terminations
IF total > 0:
    episode.benchmark_metrics.termination_quality.proper_termination_rate = proper_count / total

# 6. Calculate routing accuracy
decisions_made = episode.benchmark_metrics.termination_quality.routing_decisions_made
decisions_correct = episode.benchmark_metrics.termination_quality.routing_decisions_correct
IF decisions_made > 0:
    episode.benchmark_metrics.termination_quality.routing_accuracy = decisions_correct / decisions_made

# 7. Update aggregate scores (intermediate calculation)
aggregate = episode.benchmark_metrics.aggregate_scores
aggregate.failure_recording_rate = episode.benchmark_metrics.failure_recording.failure_recording_rate
aggregate.proper_termination_rate = episode.benchmark_metrics.termination_quality.proper_termination_rate

gate_violation_rate = episode.benchmark_metrics.gate_compliance.gate_violation_rate
IF gate_violation_rate is not None:
    aggregate.gate_compliance_rate = 1.0 - gate_violation_rate

# Calculate integrity score (only if all three metrics available)
IF all([aggregate.failure_recording_rate, aggregate.proper_termination_rate, aggregate.gate_compliance_rate]):
    aggregate.integrity_score = (
        aggregate.failure_recording_rate +
        aggregate.proper_termination_rate +
        aggregate.gate_compliance_rate
    ) / 3.0

# 8. Update context
aggregate.sub_hypotheses_count = statistics.total_sub_hypotheses
aggregate.phases_executed = ["Phase 2B", "Phase 2C", "Phase 3", "Phase 4"]

SAVE verification_state

Display: f"[BENCHMARK] Phase 4 Termination: proper={proper}"
Display: f"[BENCHMARK] Current Integrity Score: {aggregate.integrity_score or 'calculating...'}"
```

### 7. Cleanup

```python
# Remove temporary files if any
# *.tmp, *.bak, __pycache__/
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| Missing output file | Mark completion as partial |
| Checkpoint archive fails | Try alternate location |
| Verification state update fails | Retry 3 times |
| Archon update fails | Log warning, continue |

---

## WORKFLOW COMPLETION

**This is the FINAL step of Phase 4.**

| Outcome | Result |
|---------|--------|
| Gate PASS | Phase 4 complete, pipeline finished |
| Gate FAIL | Phase 4 stopped, debugging artifacts preserved |

**Exit status:**
- 0: Success (gate passed)
- 1: Failure (gate failed)
- 2: Partial (some issues)

**After completion:** Control returns to `/hypothesis-loop` for next hypothesis.

---

## 9. EXPLICIT RETURN TO PARENT WORKFLOW (MANDATORY)

#### ⚠️ INVOKE-WORKFLOW RETURN PROTOCOL

> This step ensures proper return to the invoking workflow (hypothesis-loop).
> Without executing this section, the workflow will STOP instead of continuing to the next hypothesis.
>
> **This applies to ALL hypotheses - whether first (FOUNDATION) or subsequent (INCREMENTAL).**

### 9.1 Signal Workflow Completion

Phase 4 workflow is now **COMPLETE** for hypothesis `{hypothesis_id}`.

```python
# Final state update
state = load_yaml(verification_state_file)
state.sub_hypotheses[hypothesis_id].phase4_completed = True
state.sub_hypotheses[hypothesis_id].phase4_returned_at = now()
save_verification_state(state)

display: f"✅ Phase 4 COMPLETE for {hypothesis_id}"
display: f" Gate Result: {gate_result}"
display: f" Returning to hypothesis-loop..."
```

### 9.2 STOP — This Workflow Is Complete

**This Phase 4 Claude session handles ONE hypothesis only.**

The external orchestrator (`run_hypothesis_loop.py`) will:
1. Read the gate result from `verification_state.yaml`
2. Decide whether to run the next hypothesis
3. Launch a NEW Claude session for the next hypothesis if needed

**You do NOT control the hypothesis loop. The external Python script does.**

### 9.3 SESSION TERMINATION

#### 🚨 CRITICAL — DO NOT CONTINUE BEYOND THIS POINT

> After this step completes:
> - ❌ DO NOT execute any other hypothesis (h-m1, h-m2, h-m3, h-m4, etc.)
> - ❌ DO NOT run Phase 2C, Phase 3, or Phase 4 for any other hypothesis
> - ❌ DO NOT read verification_state.yaml to find "next" hypotheses
> - ❌ DO NOT invoke /phase2c-experiment-design, /phase3-implementation-planning, or /phase4-coding
> - ❌ DO NOT ask "What would you like to do next?"
> - ✅ STOP HERE — your work for `{hypothesis_id}` is done
> - ✅ The external script (`run_phase4.py`) will handle everything after this

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- All output files verified (04_validation.md, code/, verification_state.yaml)
- Checkpoint archived with timestamp
- Verification state updated with Phase 4 completion
- Benchmark metrics recorded
- **Session ends after completing ONLY `{hypothesis_id}`**

### ❌ SYSTEM FAILURE:
- Executing Phase 2C/3/4 for a DIFFERENT hypothesis in this session
- Reading verification_state.yaml to find and run "next" hypotheses
- Continuing to work after Phase 4 completion for `{hypothesis_id}`
