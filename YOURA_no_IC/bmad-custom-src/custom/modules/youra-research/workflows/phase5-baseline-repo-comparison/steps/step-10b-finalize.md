---
name: 'step-10b-finalize'
description: 'Finalize Phase 5: Calculate benchmark metrics, update Archon tasks, complete checkpoint'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# File References
thisStepFile: '{workflow_path}/steps/step-10b-finalize.md'
prevStepFile: '{workflow_path}/steps/step-10a-gate-evaluation.md'
workflowFile: '{workflow_path}/workflow.md'

# Reference Files
finalize_templates: '{workflow_path}/_references/finalize-templates.md'

# Input Files
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
verification_state: '{research_folder}/verification_state.yaml'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

## Helper References (BMAD v6)

<helper-reference>
**Helper:** `{helpers_path}/archon_phase_reset.md`
**Function:** `terminate_pipeline_on_phase0_routing(pipeline_project_id, failure_source, failure_reason)`
**Returns:** `{success, terminated_count, project_updated, message}`
**Purpose:** Terminate Archon Pipeline when routing to Phase 0
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/archive_helpers.md`
**Function:** `archive_for_phase0_routing(research_folder, timestamp, failure_reason)`
**Returns:** `{success, archive_folder, archived_count, archived_files, marker_file}`
**Purpose:** Archive entire research folder before Phase 0 routing
</helper-reference>

<helper-reference>
**Helper:** `{workflow_path}/_references/finalize-templates.md`
**Purpose:** Extracted benchmark metrics calculation templates for token efficiency
</helper-reference>

---

# Step 10b: Finalize Phase 5 (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Pattern:** Final step - Benchmark metrics + Archon tasks + Checkpoint completion

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- MUST calculate all three benchmark metrics (failure_recording, termination_quality, gate_compliance)
- MUST update Archon tasks to final state
- MUST archive checkpoint after completion

---

## STEP GOAL

1. Calculate and record final benchmark metrics
2. Update Archon tasks to 'done' status
3. Archive checkpoint and mark Phase 5 complete

---

## 10b.1 Load Context

```python
# Load from previous step
checkpoint = read_yaml("{baseline_folder}/05_baseline_checkpoint.yaml")
verification_state = read_yaml("{research_folder}/verification_state.yaml")

# Get gate result from previous step
gate_result = checkpoint.gate_result # "PASS" or "PARTIAL"
gate_type = "DETERMINES_SUCCESS"
```

---

## 10b.2 Update Benchmark Metrics - Termination Quality

<critical>
**BENCHMARK METRIC 2: Termination Quality**

"Did the system terminate correctly based on gate conditions?"

This is CRITICAL for paper reporting - we must track whether Phase 5 terminated properly.
</critical>

Execute the **Termination Quality (Metric 2)** code from `{finalize_templates}`.

---

## 10b.3 Update Benchmark Metrics - Failure Recording (PARTIAL only)

<critical>
**BENCHMARK METRIC 1: Failure Recording Rate**

"Did the system actually record and report failures?"

For PARTIAL gate results, we must have recorded the failure to Serena Memory.
</critical>

Execute the **Failure Recording (Metric 1 - PARTIAL only)** code from `{finalize_templates}`.

---

## 10b.4 Update Benchmark Metrics - Gate Compliance

<critical>
**BENCHMARK METRIC 3: Gate Compliance Rate**

"How often did the system violate stated constraints?"

We must track that the system followed gate rules correctly.
</critical>

Execute the **Gate Compliance (Metric 3)** code from `{finalize_templates}`.

---

## 10b.5 Calculate Aggregate Integrity Score

<critical>
**AGGREGATE INTEGRITY SCORE**

This is the combined metric for paper reporting:
- Failure Recording Rate
- Proper Termination Rate
- Gate Compliance Rate (1 - violation_rate)

Average of these three = Integrity Score
</critical>

Execute the **Aggregate Integrity Score** code from `{finalize_templates}`.

---

## 10b.6 Update Pipeline Status

<critical>
Step-level Archon tasks removed. Only Pipeline-level status updated.

- Adaptation tasks: Managed in `05_tasks.yaml` (NOT Archon)
- Pipeline tasks: Archon used only for Phase-level status (Phase 5 → done)
</critical>

```python
# ================================================================
# PIPELINE STATUS UPDATE
# ================================================================

# 1. Mark all adaptation tasks as 'done' in 05_tasks.yaml
tasks_data = read_yaml("{baseline_folder}/05_tasks.yaml")
FOR baseline IN tasks_data.baselines:
    FOR task IN baseline.tasks:
        IF task.status == "review":
            task.status = "done"
write_yaml("{baseline_folder}/05_tasks.yaml", tasks_data)

# 2. Update Pipeline Project (Hypothesis-level status only)
IF gate_result == "PASS":
    # Update verification_state.yaml directly
    verification_state.main_hypothesis.baseline_comparison.status = "COMPLETED"
    verification_state.main_hypothesis.baseline_comparison.gate.result = "PASS"
```

---

## 10b.6a Phase 0 Routing

<note>
**ROUTING for PARTIAL Result**

When DETERMINES_SUCCESS gate returns PARTIAL:
1. Failure context is saved to Serena Memory (step-10a)
2. **Archive entire research folder** to `_archive/{timestamp}_failed/`
3. **Terminate current Pipeline** (mark all tasks done, project as FAILED)
4. Phase 0 will create a NEW Pipeline Project

The archive ensures clean separation between research attempts.
</note>

```python
# Reference: {archon_phase_reset}, {archive_helpers}
from archon_phase_reset import terminate_pipeline_on_phase0_routing
from archive_helpers import archive_for_phase0_routing

IF gate_result == "PARTIAL":
    # Add to history for reference
    history.append({
        "event": "DETERMINES_SUCCESS PARTIAL - routing to Phase 0",
        "timestamp": NOW,
        "phase": "Phase 5 Finalize",
        "details": "Failure context saved to Serena Memory. Archiving and terminating Pipeline."
    })

    pipeline_project_id = verification_state.get("metadata", {}).get("pipeline_project_id")
    IF pipeline_project_id:
        # 1. Archive entire research folder FIRST
        archive_result = archive_for_phase0_routing(
            research_folder=research_folder,
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            failure_reason="DETERMINES_SUCCESS_PARTIAL - Approach failed to outperform baselines"
        )
        Log(f"✓ Research folder archived: {archive_result['archived_count']} files to {archive_result['archive_folder']}")

        # 2. THEN terminate Pipeline (mark all tasks done, project as FAILED)
        terminate_result = terminate_pipeline_on_phase0_routing(
            pipeline_project_id=pipeline_project_id,
            failure_source="Phase 5",
            failure_reason="DETERMINES_SUCCESS_PARTIAL - Approach failed to outperform baselines"
        )
        Log(f"✓ Pipeline terminated: {terminate_result['message']}")
```

**Routing on Phase 5 PARTIAL:**

| Gate Result | Routing | Action |
|-------------|---------|--------|
| PASS | Phase 6 | Continue with current Pipeline |
| PARTIAL | Phase 0 | New Pipeline created (failure context via Serena Memory) |

---

## 10b.7 Save Final Verification State Snapshot

```python
IF gate_result == "PASS":
    # Use the "Serena Memory Success Snapshot Template" from {finalize_templates}
    # Populate with: hypothesis_id, per_baseline_results_table, win_count, total_baselines,
    # aggregate metrics, main_hypothesis.statement, main_hypothesis.mechanism,
    # success_factors, recommendations

    mcp__serena__write_memory(
        memory_file_name=f"phase5_success_{hypothesis_id}.md",
        content=snapshot_content # Generated from template
    )
```

---

## 10b.8 Archive Checkpoint

```python
# ================================================================
# CHECKPOINT ARCHIVAL
# ================================================================

# 1. Mark checkpoint as complete
checkpoint.status = "COMPLETED"
checkpoint.completed_at = NOW
checkpoint.current_step = "completed"

# 2. Add final summary
checkpoint.final_summary = {
    "gate_type": "DETERMINES_SUCCESS",
    "gate_result": gate_result,
    "routing_decision": "Phase 6" if gate_result == "PASS" else "Phase 0",
    "benchmark_metrics": {
        "integrity_score": aggregate.integrity_score,
        "failure_recording_rate": aggregate.failure_recording_rate,
        "proper_termination_rate": aggregate.proper_termination_rate,
        "gate_compliance_rate": aggregate.gate_compliance_rate
    }
}

# 3. Save final checkpoint
write_yaml(checkpoint, "{baseline_folder}/05_baseline_checkpoint.yaml")

# 4. Archive checkpoint
archive_name = f"05_baseline_checkpoint_archived_{timestamp}.yaml"
copy_file(
    "{baseline_folder}/05_baseline_checkpoint.yaml",
    "{baseline_folder}/{archive_name}"
)
```

---

## 10b.9 Final Verification State Update

```python
# ================================================================
# FINAL VERIFICATION STATE UPDATE
# ================================================================

# 1. Mark Phase 5 complete
workflow.current_phase = "Phase 5 Complete"
workflow.phase5_completed_at = NOW

# 2. Update status based on gate result
IF gate_result == "PASS":
    workflow.status = "COMPLETED"
    workflow.next_action = "Proceed to Phase 6 (Paper Writing)"
ELSE:
    workflow.status = "ROUTED"
    workflow.routing = {
        "target": "Phase 0",
        "source_hypothesis": main_hypothesis_id,
        "reason": "DETERMINES_SUCCESS_PARTIAL",
        "timestamp": NOW
    }
    workflow.stop_reason = "DETERMINES_SUCCESS gate PARTIAL"
    workflow.next_action = "Route to Phase 0 for new research direction"

# 3. Update statistics
statistics.phase5_statistics.benchmark_recorded = True
statistics.phase5_statistics.completed_at = NOW

# 4. Add to status_history
status_history.append({
    "status": workflow.status,
    "phase": "Phase 5",
    "timestamp": NOW,
    "trigger": "Phase 5 workflow completed",
    "gate_result": gate_result,
    "details": f"Phase 5 completed with gate result: {gate_result}"
})

# 5. Save verification_state.yaml
SAVE verification_state
```

---

## Step Completion Criteria

- [ ] Termination quality benchmark metrics calculated
- [ ] Failure recording benchmark metrics calculated (if PARTIAL)
- [ ] Gate compliance benchmark metrics calculated
- [ ] Aggregate integrity score computed
- [ ] Archon tasks updated to 'done'
- [ ] Final Serena Memory snapshot saved
- [ ] Checkpoint archived
- [ ] Verification state updated with final status

---

## WORKFLOW COMPLETION

**This is the FINAL step of Phase 5.**

| Gate Result | Next Phase | Action |
|-------------|------------|--------|
| PASS | Phase 6 | Proceed to Paper Writing |
| PARTIAL | Phase 0 | Route to new research direction |

---

## SUCCESS/FAILURE

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### SUCCESS:
- All three benchmark metrics calculated
- Aggregate integrity score computed
- Archon tasks in final state (all 'done')
- Checkpoint archived
- Verification state reflects final status
- Phase 5 workflow completed properly

### SYSTEM FAILURE:
- Not calculating benchmark metrics
- Not updating Archon tasks
- Not archiving checkpoint
- Leaving verification_state in inconsistent state
- Skipping any finalization steps
