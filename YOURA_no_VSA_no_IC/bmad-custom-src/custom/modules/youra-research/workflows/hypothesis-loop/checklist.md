# Hypothesis Loop - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize
- [ ] Configuration loaded from module.yaml
- [ ] **verification_state.yaml located and loaded**
- [ ] **Execution mode parsed:**
  - [ ] From state.workflow.execution_mode (UNATTENDED)
  - [ ] From arguments (--mode=auto/step/single)
  - [ ] Default to AUTO
- [ ] State summary displayed
- [ ] Auto-proceed to Step 2

### Step 2: Check Workflow Status
- [ ] **Workflow status checked:**
  - [ ] If STOPPED → Display stop reason and next action
  - [ ] If COMPLETED → Display completion summary
  - [ ] If IN_PROGRESS → Continue to Step 3
- [ ] Resume handling (if previously interrupted)
- [ ] **BLOCKED hypotheses cascade handling:**
  - [ ] If MUST_WORK failed → dependents marked BLOCKED/CASCADE_FAILED
  - [ ] Blocked count displayed

### Step 3: Get Ready Hypothesis
- [ ] **State validation (Section 0) executed:**
  - [ ] State format compatibility checked
  - [ ] Auto-recovery applied if needed
  - [ ] Archon sync checked
- [ ] **Natural language hypothesis collection:**
  - [ ] "Scan ALL hypotheses in sub_hypotheses" (not `.items()` loop)
  - [ ] Check for IN_PROGRESS first (resume case)
  - [ ] Collect all READY hypotheses
- [ ] READY hypotheses queried from state
- [ ] **Dependency resolution:**
  - [ ] Prerequisites checked (MUST_WORK gates satisfied)
  - [ ] Blocked hypotheses identified
  - [ ] Dependency graph validated (acyclic)
- [ ] **Next hypothesis selected (by priority/dependency order)**
- [ ] **If NO READY hypotheses:**
  - [ ] **:** Check if all hypotheses processed (not just READY)
  - [ ] Unprocessed states: READY, IN_PROGRESS, NOT_STARTED, PENDING
  - [ ] Processed states: VALIDATED, COMPLETED, FAILED, CASCADE_FAILED, BLOCKED, SUPERSEDED, CASCADE_SUPERSEDED
  - [ ] If all processed and MUST_WORK passed → Go to Step 11 (Complete) + EXIT to caller for Phase 5
  - [ ] If some NOT_STARTED/PENDING → Wait for prerequisites
  - [ ] Otherwise → Go to Step 11 (Complete)

### Step 4: Loop Start
- [ ] Current hypothesis displayed
- [ ] Hypothesis context loaded
- [ ] **Hypothesis status → IN_PROGRESS**
- [ ] **Pipeline Task updated (if needed)**
- [ ] Loop iteration counter incremented

### Step 5: Phase 2C (Experiment Design)
- [ ] **/phase2c-experiment-design workflow invoked**
- [ ] Hypothesis folder created/verified
- [ ] **02c_experiment_brief.md generated**
- [ ] **Status updated:** experiment_design.status = COMPLETED
- [ ] Checkpoint saved
- [ ] Auto-proceed to Step 6

### Step 6: Phase 3 (Implementation Planning)
- [ ] **/phase3-implementation-planning workflow invoked**
- [ ] **03_prd.md generated**
- [ ] **03_architecture.md generated**
- [ ] **03_logic.md generated**
- [ ] **03_config.md generated**
- [ ] **03_tasks.yaml generated**
- [ ] Archon project tasks created
- [ ] **Status updated:** implementation_planning.status = COMPLETED
- [ ] Checkpoint saved
- [ ] Auto-proceed to Step 7

### Step 7: Phase 4 (Coding & Validation)
- [ ] **/phase4-coding workflow invoked**
- [ ] **Code generated in `code/` folder**
- [ ] **Experiment executed**
- [ ] **04_validation.md generated**
- [ ] **MUST_WORK gate evaluated:**
  - [ ] Gate result determined (PASS/PARTIAL/FAIL)
  - [ ] Reflection triggered (if needed)
- [ ] **Status updated:** validation.status = COMPLETED
- [ ] Checkpoint saved
- [ ] Proceed to Step 8 (Gate Processing)

### Step 8: Phase 4 Gate Processing
- [ ] **04_checkpoint.yaml loaded**
- [ ] **reflection_outcome read:**
  - [ ] PASS → Status: VALIDATED, continue to next hypothesis
  - [ ] MODIFIED → New hypothesis H-*-v{n} created, continue loop
  - [ ] ROUTED_TO_PHASE_0 → Exit to Phase 0 (Serena Memory saved)
  - [ ] ROUTED_TO_PHASE_2A → Exit to Phase 2A (Serena Memory saved)
- [ ] **State updated appropriately**
- [ ] **Dependency updates after PASS/MODIFIED:**
  - [ ] `update_dependent_hypotheses_status()` called
  - [ ] NOT_STARTED dependents become READY when prerequisites satisfied
  - [ ] Updated count displayed
- [ ] **Archon Phase Task updated**
- [ ] Routing executed (continue or exit)

### Step 9: Loop Continue (Mode Actions)
- [ ] **Execution mode checked:**
  - [ ] AUTO: Continue to next READY hypothesis automatically
  - [ ] STEP: Pause for user confirmation
  - [ ] SINGLE: Exit after one hypothesis
- [ ] **User confirmation (STEP mode only):**
  - [ ] Continue option
  - [ ] Stop option
- [ ] **Loop back to Step 3** (for next hypothesis)

### ~~Step 10: Phase 5~~

> Phase 5 is invoked separately by the caller (e.g., full-pipeline-unattended Step 8)
> after hypothesis-loop completes and returns control.
>
> See: `/phase5-baseline-repo-comparison` for standalone execution.

---

## ⚠️ PHASE 5 EXECUTION PRECONDITION

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 5 can ONLY execute when ALL sub-hypotheses complete │
│ Phase 4 (2C → 3 → 4 loop finished for EVERY hypothesis) │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ✅ Phase 5 ALLOWED when ALL hypotheses in FINAL states: │
│ - VALIDATED, COMPLETED, FAILED, CASCADE_FAILED │
│ - BLOCKED, SUPERSEDED, CASCADE_SUPERSEDED │
│ │
│ ❌ Phase 5 BLOCKED if ANY hypothesis still in: │
│ - READY (waiting in queue) │
│ - IN_PROGRESS (currently processing) │
│ - NOT_STARTED (prerequisites not satisfied) │
│ - PENDING (alias for NOT_STARTED) │
│ │
└─────────────────────────────────────────────────────────────────┘
```

**Validation Checklist:**
- [ ] ALL sub-hypotheses scanned (not just current queue)
- [ ] NO hypothesis has status in [READY, IN_PROGRESS, NOT_STARTED, PENDING]
- [ ] `workflow.sub_hypotheses_complete` is `true`
- [ ] Only then: Proceed to Phase 5 or return to caller

### Step 11: Completion
- [ ] **Statistics calculated:**
  - [ ] Validated count
  - [ ] Failed count
  - [ ] Pending count
  - [ ] Blocked count
- [ ] **Main hypothesis result displayed:**
  - [ ] PASS → Research validated, ready for Phase 6
  - [ ] PARTIAL → Research not validated, route to Phase 0
  - [ ] PENDING → Sub-hypotheses incomplete
- [ ] **Next steps displayed based on result**
- [ ] **Final state update:**
  - [ ] If PASS: workflow.status = COMPLETED
  - [ ] workflow.completed_at set
- [ ] **verification_state.yaml saved**

---

## Pre-Execution Checks

- [ ] `verification_state.yaml` exists in research folder
- [ ] At least one hypothesis has status: READY
- [ ] Pipeline project exists in Archon
- [ ] Execution mode determinable (state/args/default)

---

## State File Validation

- [ ] `workflow.execution_mode` field present
- [ ] `hypotheses` section contains valid entries
- [ ] Each hypothesis has required fields:
  - [ ] `id`
  - [ ] `status` (NOT_STARTED, PENDING, READY, IN_PROGRESS, COMPLETED, BLOCKED, VALIDATED, FAILED, CASCADE_FAILED, SUPERSEDED, CASCADE_SUPERSEDED)
  - [ ] `gate_type` (MUST_WORK, SHOULD_WORK, DETERMINES_SUCCESS)
  - [ ] `prerequisites` (if dependent)

---

## Dependency Resolution

- [ ] Dependency graph is acyclic (no circular dependencies)
- [ ] **:** Prerequisites satisfied if VALIDATED OR COMPLETED with gate.satisfied=True
- [ ] NOT_STARTED hypotheses become READY when all prerequisites satisfied
- [ ] BLOCKED hypotheses correctly identified
- [ ] CASCADE_FAILED status applied to dependents of failed MUST_WORK

> Previously only COMPLETED was checked, causing dependent hypotheses to remain NOT_STARTED
> even when their prerequisites passed Phase 4 (which sets status to VALIDATED, not COMPLETED).

---

## Execution Mode Behavior

### AUTO Mode (UNATTENDED)
- [ ] All READY hypotheses processed automatically
- [ ] No user confirmations requested
- [ ] Stops only on MUST_WORK failure routing

### STEP Mode
- [ ] Confirmation requested after each hypothesis
- [ ] User can continue or stop
- [ ] Partial completion allowed

### SINGLE Mode
- [ ] Only one hypothesis processed
- [ ] Exits after first hypothesis completion

---

## Gate Processing Rules

### MUST_WORK Gate (Phase 4)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | Status: VALIDATED, continue | None |
| MODIFIED | New H-*-v{n} created, continue loop | None |
| ROUTED_TO_PHASE_0 | Exit to Phase 0 | `failure_{h_id}.md` |
| ROUTED_TO_PHASE_2A | Exit to Phase 2A | `pivot_{h_id}_{new_id}.md` |

### DETERMINES_SUCCESS Gate (Phase 5)

| Result | Action | Serena Memory |
|--------|--------|---------------|
| PASS | Research validated → Phase 6 | None |
| PARTIAL | Route to Phase 0 | `phase5_failure_{h_id}.md` |

---

## Serena Memory Reads (On Routing)

| Target Phase | Memory to Read |
|--------------|----------------|
| Phase 0 | `failure_*.md` or `phase5_failure_*.md` |
| Phase 2A | `pivot_*.md` |

---

## Routing Decision Summary

| Condition | Next Action |
|-----------|-------------|
| All sub-hypotheses processed (VALIDATED/COMPLETED/FAILED) | → Step 11 + EXIT to caller (for Phase 5) |
| Phase 4 MUST_WORK FAIL | → Phase 0 (New Direction) |
| Phase 4 MUST_WORK PARTIAL (max) | → Phase 2A-Dialogue (Redesign) |
| No READY but NOT_STARTED/PENDING remain | → Wait for prerequisites |
| No READY hypotheses (all done) | → Step 11 (Complete/Report) |

> hypothesis-loop completes at Step 11 and returns control to the invoking workflow.
> Phase 5 PASS/PARTIAL routing is processed by full-pipeline-unattended, not here.

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode from state.workflow.execution_mode
- [ ] Auto-proceed through all steps
- [ ] Automatic routing on gate failures
- [ ] No user confirmations in AUTO mode

---

## Per-Hypothesis Execution Quality

### Phase 2C
- [ ] `02c_experiment_brief.md` generated and complete
- [ ] All specifications referenced
- [ ] Status updated in verification_state.yaml

### Phase 3
- [ ] All 4 output files generated (PRD, Architecture, Logic, Config)
- [ ] `03_tasks.yaml` generated (local task file)
- [ ] Status updated in verification_state.yaml

### Phase 4
- [ ] Code generated and executable
- [ ] Experiment ran successfully
- [ ] `04_validation.md` generated with gate result
- [ ] Reflection executed (if gate failed)
- [ ] Status updated in verification_state.yaml

---

## Output Verification

### Required State Updates (per hypothesis)
- [ ] `status` field updated at each phase completion
- [ ] `gate.satisfied` set after Phase 4
- [ ] `gate.result` recorded
- [ ] `validation.phase4.status` = COMPLETED
- [ ] `validation.phase4.completed_at` set

### Final State Updates
- [ ] `workflow.status` = COMPLETED (if PASS)
- [ ] `workflow.completed_at` set
- [ ] `statistics` section updated
- [ ] All hypothesis final statuses set

---

## Critical Failures (Immediate Fix Required)

- [ ] State file not loaded before proceeding
- [ ] Execution mode not parsed
- [ ] Dependency resolution skipped
- [ ] MUST_WORK failure not routed properly
- [ ] Phase workflow invocation skipped
- [ ] Gate result not processed
- [ ] Reflection outcome ignored
- [ ] Serena Memory not read on routing
- [ ] State not saved after updates
- [ ] Infinite loop (same hypothesis selected repeatedly)

---

## Validation Summary

**Total Checks:** 100+
**Required:** Step execution + Dependency resolution + Gate processing + State management
**MANDATORY Steps:** Steps 1, 2, 3, 5, 6, 7, 8, 11 | Step 9 CONDITIONAL | ~~Step 10 REMOVED~~

**Minimum Pass Criteria:**
- All steps executed in correct order
- Dependency resolution working correctly
- Gate results processed and routed properly
- State updated after each phase
- Final completion summary displayed
- verification_state.yaml reflects final state

---

**Validation Result:**
- ✅ COMPLETE: All sub-hypotheses validated, Phase 5 passed
- ⚠️ ROUTED: Gate failure, routing to Phase 0/2A with Serena Memory
- ❌ STOPPED: Manual intervention required

**Execution Mode:** _______________
**Hypotheses Processed:** ___
**Validated:** ___
**Failed:** ___

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Hypothesis Loop Workflow (YouRA)
