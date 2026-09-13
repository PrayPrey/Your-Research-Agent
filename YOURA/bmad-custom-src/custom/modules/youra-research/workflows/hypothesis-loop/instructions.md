# Hypothesis Verification Loop - Instructions
---

## CRITICAL: UNATTENDED MODE DEFINITION

<critical>
**⚠️ UNATTENDED MODE - CORRECT DEFINITION:**
```
UNATTENDED ≠ SIMPLIFIED (NOT simplification)
UNATTENDED ≠ SHORTCUT (NOT a shortcut)
UNATTENDED ≠ SKIP_STEPS (NOT skipping steps)
UNATTENDED ≠ FASTER_EXECUTION (NOT faster execution)

UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
           = Execute ALL steps completely + Skip ONLY user prompts
```

**Pre-Step Self-Check (MANDATORY before each phase):**
```
□ Am I about to skip a step-*.md file? → VIOLATION
□ Am I about to skip an MCP tool call? → VIOLATION
□ Am I about to skip a Task agent call? → VIOLATION
□ Am I only skipping [Y/N] confirmation? → ALLOWED
```
</critical>

---

## Workflow Overview

This workflow executes the hypothesis verification loop:
- **Phase 2C → 3 → 4** for each sub-hypothesis (H-E1, H-M1, H-M2, etc.)
- **Phase 5** ONCE after ALL sub-hypotheses complete Phase 4 (operates on main_hypothesis)

**Execution Modes:** `auto` | `step` | `single`

**DO NOT:** Skip `<invoke-workflow>`, manually implement phase logic, or bypass gate validation.

---

## Gate System

| Gate Type | Phase | Success Condition |
|-----------|-------|-------------------|
| 🔴 MUST_WORK | Phase 4 | PoC validates hypothesis |
| 🟢 DETERMINES_SUCCESS | Phase 5 | Our method outperforms baseline |

---

## Routing Rules

### Phase 4 Routing (MUST_WORK Gate)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| **PASS** | → Set VALIDATED, continue to next hypothesis | - |
| **MODIFIED** | → New hypothesis `H-*-v{n}` created, continue loop | `pivot_{h_id}_{new_h_id}.md` |
| **FAIL** | → Route to Phase 0 (fundamental flaw) | `failure_{hypothesis_id}.md` |
| **PARTIAL** (max attempts) | → Route to Phase 2A-Dialogue | `failure_{hypothesis_id}.md` |

### Phase 5 Routing (DETERMINES_SUCCESS Gate)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| **PASS** | → COMPLETED, proceed to Phase 6 | - |
| **PARTIAL** | → Route to Phase 0 (baseline outperforms) | `phase5_failure_{hypothesis_id}.md` |

---

## Step Files (Implementation)

All implementation is in `steps/*.md`. Execute in order:

| Step | File | Purpose |
|------|------|---------|
| 01 | `step-01-init.md` | Initialize, parse execution mode from args/state |
| 02 | `step-02-check-status.md` | Load verification_state.yaml, check status |
| 03 | `step-03-get-ready.md` | Get READY hypotheses, sort by dependency |
| 04 | `step-04-loop-start.md` | Start loop iteration, validate prerequisites |
| 05 | `step-05-phase-2c.md` | Execute Phase 2C (Experiment Design) |
| 06 | `step-06-phase-3.md` | Execute Phase 3 (Implementation Planning) |
| 07 | `step-07-phase-4.md` | Execute Phase 4 (Coding & Validation) |
| 08 | `step-08-phase4-gate.md` | Process MUST_WORK gate, handle routing |
| 09 | `step-09-loop-continue.md` | Mode-specific actions, loop control |
| 11 | `step-11-complete.md` | Complete workflow, update Archon tasks |

> See: `full-pipeline-unattended/instructions.md` Step 8 or `/phase5-baseline-repo-comparison` for standalone execution.

---

## Helper Functions

See `helpers/state_management.md` for:

- `get_original_hypothesis_id(hypothesis_id, state)` - Get original ID for versioned hypotheses
- `is_prerequisite_satisfied(prereq_id, state)` - Check if prerequisite is satisfied
- `update_dependent_hypotheses_status(completed_hypothesis_id, state)` - Update NOT_STARTED → READY
- `block_dependent_hypotheses(failed_hypothesis_id, state)` - Block dependents on MUST_WORK failure
- `update_statistics(state)` - Update hypothesis statistics

---

## Hypothesis States

| State | Description |
|-------|-------------|
| NOT_STARTED | Prerequisites not satisfied |
| PENDING | Alias for NOT_STARTED |
| READY | Ready for processing |
| IN_PROGRESS | Currently being processed |
| VALIDATED | Phase 4 PASS |
| COMPLETED | Finished (e.g., MODIFIED → superseded) |
| FAILED | Phase 4 FAIL |
| CASCADE_FAILED | Blocked by prerequisite failure |
| BLOCKED | Explicitly blocked |

** Fix:** `check_all_sub_hypotheses_processed()` now checks NOT_STARTED and PENDING as unprocessed states.

---

## Error Labels (Quick Reference)

| Label | Description |
|-------|-------------|
| MUST_PASS_FAILURE | Prerequisite with MUST_WORK gate failed |
| PHASE_FAILURE | Phase execution failed |
| PHASE4_ROUTE_TO_PHASE0 | Phase 4 fundamental failure → Phase 0 |
| PHASE4_ROUTE_TO_PHASE2A | Phase 4 max attempts → Phase 2A-Dialogue |
| PHASE5_ROUTE_TO_PHASE0 | Phase 5 baseline outperforms → Phase 0 |
| WORKFLOW_STOPPED | Workflow stopped (check stop_reason) |
| USER_EXIT | User requested exit |

---

## Context Loss Prevention

<critical>
**Re-read execution mode before EVERY hypothesis transition:**
```python
state = load_yaml(verification_state_file)
is_unattended = (state.workflow.execution_mode == "UNATTENDED")
```
This prevents "forgetting" the mode during long workflow execution.
</critical>

---

## Archon Integration (Option B Strategy)

- ALL hypotheses create `[H-XX] Phase 2C/3/4` tasks (including H-E1)
- Pipeline Phase 2C/3/4 tasks = aggregate status indicators
- Use `sync_pipeline_phase_status()` for aggregate sync

See `helpers/archon_hypothesis_phase.md` for Archon task management functions.
