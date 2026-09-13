# Verification State Tracking System - Complete Guide

**Applies to:** Anonymous Research Pipeline (Phase 2B → Phase 2C → Phase 3 → Phase 4 → Phase 5)

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [State File Schema](#state-file-schema)
4. [Phase Responsibilities](#phase-responsibilities)
5. [Gate Validation Logic](#gate-validation-logic)
6. [Failure Routing Rules](#failure-routing-rules-v22) ← **NEW**
7. [State Transitions](#state-transitions)
8. [Recovery Procedures](#recovery-procedures)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)
11. [Hypothesis Versioning System](#hypothesis-versioning-system-v20)
12. [Automatic Retry Logic](#automatic-retry-logic-v20)
13. [SHOULD_WORK Findings Carry-forward](#should_work-findings-carry-forward-v20)
14. [MCP Phase Configuration](#mcp-phase-configuration-v20)
15. [Workflow Status History](#workflow-status-history-v21)
16. [Phase 5 Baseline Comparison & Serena Memory Integration](#phase-5-baseline-comparison--serena-memory-integration-v22)
17. [Step-Level Archon Task Management](#step-level-archon-task-management-v31)
18. [Phase 4 Local Checkpoint Task Management](#phase-4-local-checkpoint-task-management-v35)
19. [SUPERSEDED Status Handling](#superseded-status-handling-v35)
20. [SHOULD_WORK SELF_MODIFY Flow](#should_work-self_modify-flow-v39) ← **NEW**

---

## Overview

### Purpose

The Verification State Tracking System provides centralized management of hypothesis verification progress across the entire YouRA research pipeline. It ensures:

- **Gate Enforcement**: MUST_WORK gates stop workflow if hypothesis fails
- **Dependency Management**: Hypotheses cannot proceed until prerequisites are satisfied
- **Progress Tracking**: Real-time status of all hypotheses across all phases
- **Audit Trail**: Complete history of workflow events and decisions
- **Recovery Support**: Clear recovery paths when failures occur

### Key Concepts

**State File**: `verification_state.yaml` - Central YAML file tracking all workflow state

**Gate Types**:
- `MUST_WORK`: PoC validation - does the methodology work? On failure → Phase 2A
- `MUST_WORK`: Failure stops entire workflow
- `SHOULD_WORK`: Failure documented as limitation, workflow continues
  - After max self-recovery retries, LLM assessment can trigger SELF_MODIFY → Phase 2C
- `DETERMINES_SUCCESS`: Final validation gate - baseline comparison

**Hypothesis Status**:
- `READY`: Has no prerequisites or all prerequisites satisfied
- `NOT_STARTED`: Has unsatisfied prerequisites
- `IN_PROGRESS`: Currently being worked on
- `COMPLETED`: All phases completed successfully
- `BLOCKED`: Cannot proceed due to failed prerequisite
- `FAILED`: Hypothesis validation failed
- `SUPERSEDED`: PARTIAL result + LLM determined incompatibility with dependents → Phase 2A-Dialogue redesign
- `CASCADE_SUPERSEDED`: Dependent of a SUPERSEDED hypothesis, awaiting new version

**Workflow Status**:
- `ACTIVE`: Normal operation
- `STOPPED`: Halted due to gate violation
- `COMPLETED`: All hypotheses completed
- `FAILED`: Critical failure, cannot continue

---

## System Architecture

### File Location

```
{research_output_path}/{date}_youra_research/verification_state.yaml
```

Example:
```
/home/anonymous/output/20251204_youra_research/verification_state.yaml
```

### Workflow Integration

```
Phase 2B (Planning)
    ↓ Creates initial state file
    ↓ Initializes all hypotheses

Phase 2C (Experiment Design)
    ↓ Reads state file
    ↓ Validates gates before proceeding
    ↓ Updates experiment_design status

Phase 3 (Implementation Planning)
    ↓ Reads state file
    ↓ Updates implementation_planning status

Phase 4 (Validation)
    ↓ Executes experiments
    ↓ Updates validation results
    ↓ Sets gate.satisfied = true/false
    ↓ Triggers gate logic

Phase 5 (Final Report)
    ↓ Reads state file
    ↓ Summarizes all results
```

---

## State File Schema

### Complete Structure

```yaml
# Metadata Section
metadata:
  project_name: string # Project/hypothesis title
  main_hypothesis_id: string # Main hypothesis being verified (e.g., "H-M3")
  phase2b_roadmap: string # Phase 2B output filename
  created_at: timestamp
  last_updated: timestamp
  version: string # Format identifier

# Workflow Status
workflow:
  status: enum # ACTIVE | STOPPED | COMPLETED | FAILED
  current_phase: string # Current phase name
  execution_mode: enum # UNATTENDED | INTERACTIVE
  stop_reason: string | null # Reason if STOPPED
  next_action: string # Guidance for next step

  # NEW: Cumulative status change history
  status_history: [ # Array of status transitions (append-only, never deleted)
    - status: enum # Status at this point
      phase: string # Phase when status changed
      timestamp: timestamp # When change occurred
      trigger: string # What caused the change
      hypothesis_id: string | null # Related hypothesis (if any)
      gate_type: string | null # Gate type (if gate-related)
      details: string # Human-readable description
  ]

# Hypothesis Tracking (one entry per hypothesis)
hypotheses:
  {hypothesis_id}: # e.g., H-E1, H-M1, etc.
    type: enum # EXISTENCE | MECHANISM | CONDITION | COMPARISON
    statement: string # Full hypothesis statement
    status: enum # READY | NOT_STARTED | IN_PROGRESS | COMPLETED | BLOCKED | FAILED

    gate:
      type: enum # MUST_WORK | SHOULD_WORK | DETERMINES_SUCCESS
      consequence_if_fail: string
      satisfied: bool | null # null = not yet tested, true = passed, false = failed

    prerequisites: [string] # List of hypothesis IDs that must complete first

    experiment_design: # Phase 2C tracking
      status: enum # NOT_STARTED | IN_PROGRESS | COMPLETED
      file: string | null # Output filename
      started_at: timestamp | null
      completed_at: timestamp | null

    implementation_planning: # Phase 3 tracking
      status: enum
      files: [string] # PRD, Architecture, Archon tasks
      started_at: timestamp | null
      completed_at: timestamp | null

    validation: # Phase 4 tracking
      status: enum # NOT_STARTED | IN_PROGRESS | COMPLETED | FAILED
      file: string | null # Validation report filename
      result: enum | null # PASS | FAIL | PARTIAL
      started_at: timestamp | null
      completed_at: timestamp | null
      success_criteria_met: bool | null
      key_findings: string | null

    blocked_by: string | null # Hypothesis ID that blocks this one
    blocked_reason: string | null
    completed: bool
    completed_at: timestamp | null

# Gate Violations Log
gate_violations:
  - hypothesis_id: string
    gate_type: enum
    validation_result: enum
    timestamp: timestamp
    consequence: string
    action_taken: string

# Workflow History (chronological log)
history:
  - event: string
    timestamp: timestamp
    phase: string | null
    hypothesis_id: string | null
    result: string | null
    details: string | null

# Statistics Summary
statistics:
  total_hypotheses: int
  completed_hypotheses: int
  failed_hypotheses: int
  blocked_hypotheses: int
  in_progress_hypotheses: int
  gates_passed: int
  gates_failed: int
  phases_completed:
    phase_2b: bool
    phase_2c: int # Count of completed experiment designs
    phase_3: int # Count of completed implementation plans
    phase_4: int # Count of completed validations
    phase_5: bool
```

---

## Phase Responsibilities

### Phase 2B (Planning)

**Responsibility**: Initialize state file

**Actions**:
1. Create `verification_state.yaml` from template
2. Parse all hypotheses from Section 4 of roadmap
3. Extract gate conditions from Section 5
4. Extract dependencies from dependency graph
5. Initialize all hypotheses:
   - Hypotheses with no prerequisites → status: "READY"
   - All others → status: "NOT_STARTED"
6. Set workflow.status = "ACTIVE"
7. Set workflow.next_action = "Begin Phase 2C with H-E1"
8. Add initial event to history

**File Modified**: Creates new file

**Example**:
```yaml
workflow:
  status: "ACTIVE"
  current_phase: "Phase 2B"
  next_action: "Begin Phase 2C with H-E1"

hypotheses:
  H-E1:
    status: "READY"
    prerequisites: []
  H-M1:
    status: "NOT_STARTED"
    prerequisites: ["H-E1"]

history:
  - event: "Phase 2B completed"
    timestamp: "2025-12-04T10:00:00"
    details: "Generated verification roadmap with 5 hypotheses"
```

---

### Phase 2C (Experiment Design)

**Responsibility**: Validate gates before experiment design, update design status

**Step 0A: State File Validation** (MANDATORY FIRST STEP)

1. Read `verification_state.yaml`
2. Check `workflow.status`:
   - If "STOPPED" → Display recovery options and EXIT
   - If "ACTIVE" → Continue
3. Parse available hypotheses and display status table

**Step 0B: Select Hypothesis**

1. User selects hypothesis ID
2. Validate hypothesis exists in state

**Step 0C: Validate Hypothesis Status**

1. Check `hypotheses[{id}].status`:
   - If "BLOCKED" → Show blocking reason and EXIT
   - If "COMPLETED" → Ask if user wants to overwrite
   - If "READY" or "NOT_STARTED" → Continue

**Step 0D: Gate Validation for Prerequisites** (CRITICAL)

1. Parse Phase 2B Section 5 for prerequisite gate information
2. For each prerequisite:
   ```python
   if prerequisite.gate.type == "MUST_WORK":
       if prerequisite.gate.satisfied == False:
           # STOP WORKFLOW
           update_state(workflow.status = "STOPPED")
           update_state(workflow.stop_reason = f"Gate violation: {prereq_id} MUST_WORK failed")
           update_state(hypotheses[current_id].status = "BLOCKED")
           update_state(hypotheses[current_id].blocked_by = prereq_id)
           log_gate_violation(prereq_id, "MUST_WORK", "FAIL")
           display_recovery_options()
           EXIT

   if prerequisite.gate.type == "SHOULD_WORK":
       if prerequisite.gate.satisfied == False:
           # CONTINUE WITH LIMITATION
           add_limitation_note_to_output()
           log_history(f"{prereq_id} SHOULD_WORK failed, continuing with limitation")
           CONTINUE
   ```

**Step 0F: Update State Before Proceeding**

1. Update `hypotheses[{id}].experiment_design.status = "IN_PROGRESS"`
2. Update `hypotheses[{id}].experiment_design.started_at = [timestamp]`
3. Update `workflow.current_phase = "Phase 2C"`
4. Add history event
5. Save state file

**On Completion** (Last step of Phase 2C):

1. Update `hypotheses[{id}].experiment_design.status = "COMPLETED"`
2. Update `hypotheses[{id}].experiment_design.file = "02c_experiment_brief_{id}.md"`
3. Update `hypotheses[{id}].experiment_design.completed_at = [timestamp]`
4. Add history event
5. Save state file

**Files Modified**: Updates existing file

---

### Phase 3 (Implementation Planning)

**Responsibility**: Track implementation planning status

**Actions**:
1. Read state file
2. Check hypothesis status (should have experiment_design.status = "COMPLETED")
3. Update `implementation_planning.status = "IN_PROGRESS"`
4. On completion:
   - Update status to "COMPLETED"
   - Add files (PRD, Architecture, Archon tasks)
   - Add history event

**Files Modified**: Updates existing file

---

### Phase 4 (PoC Validation)
**Responsibility**: PoC validation - prove methodology has effect (Does it work?)

- Gate type: `MUST_WORK` (not MUST_WORK or DETERMINES_SUCCESS)
- Experiment scope: Smoke test level (reduced epochs/seeds)
- Focus: "Does it work?" not "How well does it perform?"
- DETERMINES_SUCCESS moved to Phase 5

**Actions**:
1. Read state file
2. Execute PoC experiment (smoke test level)
3. Analyze results: Does the mechanism work?
4. **CRITICAL**: Update gate satisfaction:
   ```yaml
   hypotheses[{id}].validation.status = "COMPLETED"
   hypotheses[{id}].validation.result = "WORKS" | "DOES_NOT_WORK"
   hypotheses[{id}].validation.poc_verified = true | false
   hypotheses[{id}].gate.type = "MUST_WORK"
   hypotheses[{id}].gate.satisfied = true | false
   ```
5. If gate.satisfied = false (MUST_WORK failed):
   - Route to Phase 2A-Dialogue for hypothesis redesign
   - NOT Phase 0 (mechanism issue, not fundamental flaw)
6. If gate.satisfied = true:
   - Proceed to Phase 5 for baseline comparison
7. Save state file

**Files Modified**: Updates existing file

---

### Phase 5 (Baseline Comparison + DETERMINES_SUCCESS)
**Responsibility**: Full-scale baseline comparison and final hypothesis validation

- Now handles DETERMINES_SUCCESS gate (moved from Phase 4)
- Full-scale experiment for both Ours AND Baseline
- Same conditions from Phase 2A-Extended applied to both
- Statistical comparison determines final hypothesis validation

**Actions**:
1. Read state file
2. Search and select baseline repository
3. Adapt baseline code to use OUR model/dataset/conditions
4. Execute full-scale experiments: Ours (90 runs) + Baseline (90 runs)
5. Statistical comparison (p-value, Cohen's d)
6. **CRITICAL**: Update DETERMINES_SUCCESS gate:
   ```yaml
   hypotheses[{id}].baseline_comparison.status = "COMPLETED"
   hypotheses[{id}].baseline_comparison.gate_result = "PASS" | "PARTIAL"
   hypotheses[{id}].baseline_comparison.results:
     ours_best_psi: {value}
     baseline_best_psi: {value}
     performance_gap: {delta}
   ```
7. If gate_result = "PASS" (ours > baseline):
   - Proceed to Phase 6 (Paper Writing)
   - workflow.status = "COMPLETED"
8. If gate_result = "PARTIAL" (ours <= baseline):
   - Route to Phase 0 for NEW research direction
   - Approach fundamentally inferior to baseline
9. Save final state

**Files Modified**: Updates existing file

---

## Gate Validation Logic

### Gate Types

#### MUST_WORK

**Definition**: PoC validation gate - proves methodology has effect (Does it work?)

**Used In**: Phase 4 only

**Criteria**:
- Code executes without errors
- Mechanism is correctly implemented
- Metrics can be measured (even if not optimal)

**On Failure**:
1. Route to Phase 2A-Dialogue for hypothesis redesign
2. NOT Phase 0 (mechanism issue, not fundamental flaw)
3. Log failure with lessons learned
4. Save to Serena memory for Phase 2A-Dialogue context

**On Success**:
1. Proceed to Phase 5 for baseline comparison
2. Mark hypothesis as PoC verified

**Example**:
```yaml
H-M1:
  gate:
    type: "MUST_WORK"
    consequence_if_fail: "Route to Phase 2A-Dialogue for redesign"
    satisfied: true # WORKS

# Proceed to Phase 5
workflow:
  status: "ACTIVE"
  next_action: "Begin Phase 5 baseline comparison"
```

---

#### MUST_WORK

**Definition**: Critical hypothesis that MUST succeed for workflow to continue

**On Failure**:
1. Immediately stop workflow
2. Update workflow.status = "STOPPED"
3. Update workflow.stop_reason
4. Mark all dependent hypotheses as BLOCKED
5. Log gate violation
6. Display recovery options to user
7. EXIT workflow

**Example**:
```yaml
H-E1:
  gate:
    type: "MUST_WORK"
    consequence_if_fail: "STOP entire workflow - reassess hypothesis"
    satisfied: false # FAIL

# Workflow stops immediately
workflow:
  status: "STOPPED"
  stop_reason: "Gate violation: H-E1 MUST_WORK failed"

hypotheses:
  H-M1:
    status: "BLOCKED"
    blocked_by: "H-E1"
  H-M2:
    status: "BLOCKED"
    blocked_by: "H-E1"
```

#### SHOULD_WORK

**Definition**: Important hypothesis, but failure doesn't stop workflow

**On Failure**:
1. Continue workflow
2. Add limitation note to output documents
3. Log in history
4. Warn user
5. Proceed to next hypothesis

**Example**:
```yaml
H-M1:
  gate:
    type: "SHOULD_WORK"
    consequence_if_fail: "Document limitation, continue with reduced confidence"
    satisfied: false # FAIL

# Workflow continues
workflow:
  status: "ACTIVE"

history:
  - event: "H-M1 SHOULD_WORK failed, continuing with limitation"
    timestamp: "2025-12-04T15:00:00"
    details: "Mechanism partially effective, documenting boundary conditions"
```

#### DETERMINES_SUCCESS

**Definition**: Final gate that determines overall success

**On Failure**:
1. Mark workflow as completed but unsuccessful
2. Generate summary report
3. Document outcomes

**Example**:
```yaml
H-CP1:
  gate:
    type: "DETERMINES_SUCCESS"
    consequence_if_fail: "Main hypothesis not fully validated"
    satisfied: false # FAIL

# Workflow completes but marked as unsuccessful
workflow:
  status: "COMPLETED"
  final_result: "UNSUCCESSFUL"
```

---

## Failure Routing Rules

### Overview

This section defines where hypotheses are routed when validation or baseline comparison fails.

### Tiered Routing System

| Scenario | Gate Type | Result | Max Attempts | Route To | Reason |
|----------|-----------|--------|--------------|----------|--------|
| **Phase 4 PoC** | MUST_WORK | DOES_NOT_WORK | **1** | Phase 2A-Dialogue | Mechanism needs redesign |
| Phase 4 PoC | SHOULD_WORK | FAIL/PARTIAL (retry < 3) | 3 | Self-recovery | Re-run validation |
| **Phase 4 PoC** | **SHOULD_WORK** | **FAIL/PARTIAL (retry ≥ 3)** | **3** | **LLM Assessment** | **SELF_MODIFY → Phase 2C, or FAIL → Continue** |
| **Phase 5 Baseline** | DETERMINES_SUCCESS | **PARTIAL** | - | **Phase 0** | **Approach fundamentally inferior** |
| Phase 5 Baseline | DETERMINES_SUCCESS | **PASS** | - | Phase 6 | Hypothesis validated |

### Phase 4 MUST_WORK Routing

```
Phase 4 MUST_WORK Result
         │
    ┌────┴────┐
    │ │
  WORKS DOES_NOT_WORK
    │ │
    ↓ ↓
 Phase 5 1st try?
 Baseline │
 Comparison ┌──┴──┐
          YES NO
           │ │
           ↓ ↓
         Modify Phase 2A
          and (Hypothesis
         Retry redesign)
```

**DOES_NOT_WORK (1st attempt)**:
1. Trigger reflection (Step 6B)
2. If meaningful findings → Create modified hypothesis (H-{id}-v2)
3. Re-enter Phase 2C with modified hypothesis

**DOES_NOT_WORK (2nd attempt)** - Still fails after modification:
1. Save to Serena memory: `failure_{hypothesis_id}.md`
2. Route to Phase 2A-Dialogue for hypothesis redesign

**Note**: Phase 4 MUST_WORK does NOT route to Phase 0. It's a mechanism issue, not a fundamental flaw.

### Phase 5 Baseline Routing

> **CRITICAL**: Phase 5 PARTIAL always routes to Phase 0, NOT Phase 2A.

```
Phase 5 Baseline Result
         │
    ┌────┴────┐
    │ │
   PASS PARTIAL
    │ │
    ↓ ↓
 Phase 6 Save failure
 Paper context to
 Writing Serena Memory
              │
              ↓
           Phase 0
           (NEW research
            direction)
```

**Why Phase 0, not Phase 2A?**:
- Baseline underperformance = approach fundamentally inferior
- Modifying the hypothesis won't fix a fundamentally flawed approach
- Need a completely new research direction

### Serena Memory Integration

| Phase | Gate Result | Memory File | Purpose |
|-------|-------------|-------------|---------|
| Phase 2A | - | `phase2a_summary_{gap_id}.md` | **OPTIONAL** (retry context) |
| Phase 4 | PARTIAL | `pivot_{h_id}_{new_h_id}.md` | Hypothesis modification guidance |
| Phase 4 | FAIL | `failure_{hypothesis_id}.md` | Fundamental failure analysis |
| Phase 5 | PARTIAL | `phase5_failure_{hypothesis_id}.md` | Baseline outperformance analysis |
| Phase 5 | PASS | `phase5_success_{hypothesis_id}.md` | Success factors for future reference |
| Phase 0 | - | Reads all failure/pivot memories | Loads previous context |
| Phase 2A-Ext | - | Reads all failure/pivot memories | Loads previous context |

### Configuration in verification_state.yaml

```yaml
workflow:
  failure_routing:
    phase4_must_work_fail:
      max_attempts: 1 # 1 modification attempt, then Phase 2A
      route_after_max: "Phase 2A-Dialogue"
      serena_memory: "failure_{hypothesis_id}.md"
      note: "Mechanism issue, not fundamental flaw"

    phase5_determines_success_partial:
      route_to: "Phase 0" # NOT Phase 2A!
      reason: "Approach fundamentally inferior to baseline"
      serena_memory: "phase5_failure_{hypothesis_id}.md"

    phase5_determines_success_pass:
      route_to: "Phase 6" # Paper Writing
      status: "HYPOTHESIS_VALIDATED"

    phase5_retry_limit:
      max_retries: 3
      route_after_max: "Phase 0"
      stop_pipeline: true
```

---

## State Transitions

### Hypothesis Status Flow

```
NOT_STARTED → READY → IN_PROGRESS → COMPLETED
                ↓
              BLOCKED (if prerequisite fails MUST_WORK)
                ↓
              FAILED (if validation fails)
```

### Workflow Status Flow

```
ACTIVE → STOPPED (gate violation) → [User resolves] → ACTIVE
  ↓
COMPLETED (all hypotheses done)
  ↓
FAILED (critical error)
```

### Example: Full Hypothesis Lifecycle

**Initial State (Phase 2B)**:
```yaml
H-M1:
  status: "NOT_STARTED"
  prerequisites: ["H-E1"]
  experiment_design: {status: "NOT_STARTED"}
  validation: {status: "NOT_STARTED", satisfied: null}
```

**After H-E1 Completes (Phase 4)**:
```yaml
H-E1:
  gate: {satisfied: true}

H-M1:
  status: "READY" # Changed by Phase 2C
  prerequisites: ["H-E1"]
```

**Phase 2C Started**:
```yaml
H-M1:
  status: "READY"
  experiment_design:
    status: "IN_PROGRESS"
    started_at: "2025-12-04T11:00:00"
```

**Phase 2C Completed**:
```yaml
H-M1:
  experiment_design:
    status: "COMPLETED"
    file: "02c_experiment_brief_H-M1.md"
    completed_at: "2025-12-04T11:15:00"
```

**Phase 4 Completed**:
```yaml
H-M1:
  status: "COMPLETED"
  validation:
    status: "COMPLETED"
    result: "PASS"
    file: "04_validation_H-M1.md"
    success_criteria_met: true
  gate: {satisfied: true}
  completed: true
  completed_at: "2025-12-04T14:00:00"
```

---

## Recovery Procedures

### Scenario 1: MUST_WORK Gate Failure

**Problem**: H-E1 (MUST_WORK) validation failed

**State**:
```yaml
workflow:
  status: "STOPPED"
  stop_reason: "Gate violation: H-E1 MUST_WORK failed"

H-E1:
  gate: {type: "MUST_WORK", satisfied: false}

H-M1:
  status: "BLOCKED"
  blocked_by: "H-E1"
```

**Recovery Options**:

**Option 1: Review and Retry**
1. Analyze why H-E1 failed (check 04_validation_H-E1.md)
2. Fix issues (code bugs, hyperparameters, data issues)
3. Re-run Phase 4 for H-E1
4. If passes, manually update state:
   ```yaml
   H-E1:
     gate: {satisfied: true}

   workflow:
     status: "ACTIVE"
     stop_reason: null

   H-M1:
     status: "READY"
     blocked_by: null
   ```
5. Continue with H-M1

**Option 2: Modify Hypothesis**
1. Return to Phase 2A Extended
2. Revise hypothesis based on findings
3. Re-run Phase 2B to generate new roadmap
4. Create new state file
5. Start fresh verification

**Option 3: Change Gate Type (Risky)**
1. Evaluate if H-E1 is truly critical
2. If not, edit Phase 2B roadmap Section 5:
   - Change gate type from MUST_WORK to SHOULD_WORK
3. Re-run Phase 2B Step 7 to regenerate state file
4. Continue workflow with limitation note

**Option 4: Abort**
1. Accept that hypothesis cannot be validated with current approach
2. Document lessons learned
3. Generate final report with findings
4. Archive project

---

### Scenario 2: Workflow Stuck Due to Blocking

**Problem**: Cannot proceed to H-M2 because H-M1 is BLOCKED

**State**:
```yaml
H-M1:
  status: "BLOCKED"
  blocked_by: "H-E1"

H-M2:
  prerequisites: ["H-M1"]
  status: "NOT_STARTED"
```

**Recovery**:
1. Resolve the blocking issue (H-E1) using Scenario 1 procedures
2. Update H-M1 status to READY
3. Proceed with H-M1
4. Once H-M1 completes, H-M2 becomes READY

---

### Scenario 3: State File Corruption

**Problem**: State file is corrupted or has invalid format

**Recovery**:
1. Restore from backup if available
2. If no backup:
   - Re-run Phase 2B Step 7 to regenerate initial state
   - Manually update with progress made so far
   - Use validation reports (04_validation_*.md) to reconstruct gate.satisfied values

---

## Examples

### Example 1: Simple Linear Flow

**Hypotheses**: H-E1 → H-M1 → H-CP1

**Initial State** (Phase 2B completed):
```yaml
workflow: {status: "ACTIVE", current_phase: "Phase 2B"}

hypotheses:
  H-E1:
    status: "READY"
    gate: {type: "MUST_WORK", satisfied: null}
    prerequisites: []

  H-M1:
    status: "NOT_STARTED"
    gate: {type: "SHOULD_WORK", satisfied: null}
    prerequisites: ["H-E1"]

  H-CP1:
    status: "NOT_STARTED"
    gate: {type: "DETERMINES_SUCCESS", satisfied: null}
    prerequisites: ["H-M1"]
```

**After H-E1 Validation Passes**:
```yaml
H-E1:
  status: "COMPLETED"
  gate: {satisfied: true}
  validation: {result: "PASS"}

H-M1:
  status: "READY" # Can now proceed
```

**After H-M1 Validation Fails (SHOULD_WORK)**:
```yaml
H-M1:
  status: "COMPLETED"
  gate: {satisfied: false}
  validation: {result: "FAIL"}

H-CP1:
  status: "READY" # Can still proceed (SHOULD_WORK doesn't block)

history:
  - event: "H-M1 SHOULD_WORK failed, continuing with limitation"
```

**After H-CP1 Validation Fails (DETERMINES_SUCCESS)**:
```yaml
H-CP1:
  gate: {satisfied: false}

workflow:
  status: "COMPLETED"
  final_result: "UNSUCCESSFUL - main hypothesis not fully validated"
```

---

### Example 2: Parallel Hypotheses with Failure

**Hypotheses**:
```
       H-E1 (MUST_WORK)
       / \
    H-M1 H-M2
       \ /
      H-CP1
```

**After H-E1 Fails**:
```yaml
workflow:
  status: "STOPPED"
  stop_reason: "Gate violation: H-E1 MUST_WORK failed"

H-E1:
  gate: {satisfied: false}

H-M1:
  status: "BLOCKED"
  blocked_by: "H-E1"

H-M2:
  status: "BLOCKED"
  blocked_by: "H-E1"

H-CP1:
  status: "NOT_STARTED"
  blocked_reason: "Prerequisites H-M1 and H-M2 are blocked"

gate_violations:
  - hypothesis_id: "H-E1"
    gate_type: "MUST_WORK"
    validation_result: "FAIL"
    timestamp: "2025-12-04T12:00:00"
    consequence: "Workflow STOPPED - H-M1, H-M2, H-CP1 cannot proceed"
    action_taken: "User notified, recovery options displayed"
```

---

## Troubleshooting

### Issue: Phase 2C doesn't see state file

**Symptoms**: Phase 2C Step 0A reports "State file not found"

**Causes**:
1. Phase 2B Step 7 didn't complete
2. State file path misconfigured
3. File permissions issue

**Solutions**:
1. Check if Phase 2B completed: Look for "✅ Verification state file created" message
2. Verify path in workflow.yaml: `verification_state_file` variable
3. Check file exists: `{research_output_path}/{date}_youra_research/verification_state.yaml`
4. If missing, re-run Phase 2B Step 7

---

### Issue: Gate validation not triggering

**Symptoms**: Phase 2C proceeds even though prerequisite failed MUST_WORK

**Causes**:
1. Phase 4 didn't update `gate.satisfied` field
2. Phase 2C Step 0D not executing

**Solutions**:
1. Check Phase 4 validation report: Should show gate satisfaction result
2. Manually update state file if Phase 4 missed it
3. Verify Phase 2C instructions.md has Step 0D gate validation section

---

### Issue: Hypothesis stuck in BLOCKED state

**Symptoms**: Cannot proceed to hypothesis even after resolving blocking issue

**Causes**:
1. State file not updated after resolution
2. Workflow status still "STOPPED"

**Solutions**:
1. Manually update state file:
   ```yaml
   workflow: {status: "ACTIVE", stop_reason: null}
   hypotheses[{id}]: {status: "READY", blocked_by: null}
   ```
2. Add history entry documenting resolution

---

### Issue: State file and actual progress out of sync

**Symptoms**: State file shows status that doesn't match reality

**Causes**:
1. Phase didn't update state file on completion
2. Manual interventions not logged

**Solutions**:
1. Compare state file against actual output files
2. Use validation reports (04_validation_*.md) as source of truth for gate.satisfied
3. Manually synchronize state file with reality
4. Add corrective history entries

---

## Best Practices

### For Workflow Developers

1. **Always update state file**: Every phase must update state on start and completion
2. **Atomic updates**: Update all related fields together (status + file + timestamp)
3. **Log everything**: Add history entry for every significant event
4. **Validate before proceed**: Always read and validate state before starting work
5. **Handle failures gracefully**: Provide clear error messages and recovery guidance

### For Users

1. **Don't manually edit state file**: Unless absolutely necessary for recovery
2. **Review gate violations immediately**: Don't ignore STOPPED status
3. **Keep validation reports**: They are source of truth for gate.satisfied values
4. **Document manual interventions**: Add notes to history if you manually update state
5. **Backup state file**: Before manual edits or major workflow steps

---

## Hypothesis Versioning System

### Overview

The schema introduces hypothesis versioning to support automatic retry logic. When a hypothesis fails validation (PARTIAL or FAIL), the system can create a modified version for re-testing.

### Version Naming Convention

```
{original_id}-v{version_number}

Examples:
- H-M1 (original, version 1)
- H-M1-v2 (first modification)
- H-M1-v3 (second modification)
- ...
- H-M1-v5 (final modification attempt)
```

### New State Fields

Each hypothesis now includes version tracking fields:

```yaml
hypotheses:
  H-M1-v2:
    # === VERSION TRACKING ===
    version: 2 # Current version number
    original_hypothesis_id: "H-M1" # Base hypothesis ID
    modified_from: "H-M1" # Direct parent version
    modification_attempt: 1 # 0-indexed attempt counter
    max_modification_attempts: 3 # Hard limit (default: 3)

    # === REFLECTION DATA ===
    reflection:
      triggered: true # Was reflection executed?
      has_meaningful_findings: true # Did LLM find meaningful results?
      meaningful_findings_summary: "..."
      modification_rationale: "..." # Why modification was made
      lessons_learned: ["...", "..."] # Array of lessons

    # === VERSION HISTORY ===
    version_history:
      - version: 1
        statement: "Original statement..."
        result: "PARTIAL"
        key_findings: "..."
        modified_to: "H-M1-v2"
        timestamp: "2025-12-17T10:00:00Z"

    # === FINDINGS FROM FAILED PREREQUISITES ===
    findings_from_failed_prerequisites:
      - source_hypothesis: "H-E2"
        gate_type: "SHOULD_WORK"
        findings: "..."
        limitations: "..."
```

### Accessing Previous Version Context

When starting Phase 2C for a versioned hypothesis, the system automatically:

1. Detects if `version > 1`
2. Loads previous version's validation report
3. Loads previous version's reflection report
4. Extracts lessons learned and modification rationale
5. Stores as `previous_version_context` for experiment design

---

## Automatic Retry Logic

### Flow Overview

```
Phase 4 Gate Processing
         │
         ▼
   ┌───────────┐
   │ PASS? │───YES──► Continue to Report Generation
   └───────────┘
         │NO
         ▼
   ┌────────────────┐
   │ SHOULD_WORK? │───YES──► Extract findings, Continue
   └────────────────┘
         │NO (MUST_WORK or DETERMINES_SUCCESS)
         ▼
   ┌────────────────┐
   │ attempts < 5? │───NO───► Mark FAILED (max attempts)
   └────────────────┘
         │YES
         ▼
   Step 6B: Reflection
         │
   ┌────────────────────┐
   │ Meaningful Findings?│───NO───► Mark FAILED
   └────────────────────┘
         │YES
         ▼
   Create H-{id}-v{N+1}
         │
         ▼
   Re-enter Phase 2C
```

### Trigger Conditions for Reflection

Reflection (Step 6B) is triggered when **ALL** of these are true:

| Condition | Check |
|-----------|-------|
| Gate Result | `gate_result == "PARTIAL"` OR `gate_result == "FAIL"` |
| Gate Type | `gate.type == "MUST_WORK"` OR `gate.type == "DETERMINES_SUCCESS"` |
| Attempt Count | `modification_attempt < max_modification_attempts` (default: 3) |

**SHOULD_WORK failures do NOT trigger reflection** - they continue with findings carry-forward.

### Meaningful Findings Criteria

The LLM auto-judges "meaningful findings" based on:

| Criterion | Description | Weight |
|-----------|-------------|--------|
| **Partial Success** | At least one metric showed significant improvement | HIGH |
| **Identified Mechanism** | Understood why failure occurred | MEDIUM |
| **Actionable Insight** | Found specific change that could improve results | HIGH |
| **Reproducible Pattern** | Failure is consistent and analyzable | MEDIUM |
| **Scope Clarity** | Discovered that hypothesis scope needs adjustment | MEDIUM |

### Modification Types

| Type | When Used |
|------|-----------|
| `PARAMETER_ADJUSTMENT` | Partial success + actionable insight |
| `SCOPE_REDUCTION` | Identified mechanism + scope clarity |
| `METHODOLOGY_CHANGE` | Reproducible pattern + actionable insight |
| `REFINEMENT` | PARTIAL result with >50% metric improvement |

### State Updates on Modification

When creating a new version:

```yaml
# 1. Mark current version as COMPLETED
hypotheses[H-M1]:
  status: "COMPLETED"
  reflection:
    triggered: true
    has_meaningful_findings: true
    modification_rationale: "..."
  version_history:
    - version: 1
      modified_to: "H-M1-v2"

# 2. Create new version entry
hypotheses[H-M1-v2]:
  version: 2
  original_hypothesis_id: "H-M1"
  modified_from: "H-M1"
  modification_attempt: 1
  status: "READY"
  statement: "Modified statement..."

# 3. Update statistics
statistics:
  total_modifications: +1

# 4. Add to modification_history
modification_history:
  - original_id: "H-M1"
    from_version: "v1"
    to_version: "v2"
    trigger: "PARTIAL result in Phase 4"
    modification_type: "PARAMETER_ADJUSTMENT"
```

### Maximum Modifications

After 5 modification attempts (version 6), the hypothesis is marked as **FAILED**:

```yaml
hypotheses[H-M1-v5]:
  status: "FAILED"
  reflection:
    triggered: true
    has_meaningful_findings: false
    lessons_learned: ["Maximum attempts reached without success"]

statistics:
  failed_hypotheses: +1
  failed_modifications: +1
```

---

## SHOULD_WORK Findings Carry-forward

### Overview

When a SHOULD_WORK gate fails, instead of stopping the workflow:

1. Extract meaningful findings from the validation
2. Propagate these findings to dependent hypotheses
3. Continue workflow with limitation notes

### Extraction Process

```yaml
# Step 6 Gate Processing - SHOULD_WORK Failure
IF gate.type == "SHOULD_WORK" AND gate_result IN ["FAIL", "PARTIAL"]:
    # Extract findings
    findings = extract_from_validation_report({
        "metrics_achieved": [...],
        "metrics_failed": [...],
        "partial_success_areas": [...],
        "identified_limitations": [...],
        "applicable_constraints": [...]
    })

    # Store in hypothesis
    hypotheses[{id}].validation.extracted_findings = findings

    # Propagate to dependents
    FOR EACH dependent IN find_dependent_hypotheses({id}):
        dependent.findings_from_failed_prerequisites.append({
            "source_hypothesis": {id},
            "gate_type": "SHOULD_WORK",
            "findings": findings,
            "limitations": "..."
        })
```

### Using Findings in Phase 2C

When starting Phase 2C for a hypothesis with failed SHOULD_WORK prerequisites:

```python
# Step 1: Load prerequisites' findings
prereq_findings = hypothesis.findings_from_failed_prerequisites

IF prereq_findings:
    Display: "⚠️ SHOULD_WORK Limitations Detected"

    FOR finding IN prereq_findings:
        Display: f"From {finding.source_hypothesis}:"
        Display: f" - Limitations: {finding.limitations}"
        Display: f" - Constraints: {finding.findings.applicable_constraints}"

    # Store for experiment design
    limitation_context = {
        "has_limitations": True,
        "sources": prereq_findings,
        "design_constraints": extract_design_constraints(prereq_findings)
    }
```

---

## MCP Phase Configuration

### Overview

MCP (Model Context Protocol) servers are loaded dynamically based on the current phase. This optimizes resource usage and ensures the right tools are available for each task.

### Configuration File

Location: `bmad-custom-src/custom/modules/youra-research/mcp-phase-config.yaml`

### Phase Requirements

| Phase | Required MCP | Optional MCP | Reasoning |
|-------|--------------|--------------|-----------|
| Phase 0 | Archon | - | Pipeline creation only |
| Phase 1 | Archon, Scholar, Exa | - | Comprehensive research |
| Phase 2A | Archon, ClearThought, Scholar, Exa | - | Evidence + reasoning |
| Phase 2A-Ext | Archon, ClearThought, Scholar, Exa | - | Deep clarification |
| Phase 2B | Archon, ClearThought, Exa | - | Structured planning |
| Phase 2C | Archon, Exa | Serena | Implementation search |
| Phase 3 | Archon, Serena | - | Code analysis |
| Phase 4 | Archon, Serena, Exa | - | Validation + implementation search |
| Reflection | Archon, ClearThought, Exa | - | Structured analysis |

### MCP Server Definitions

```yaml
mcp_servers:
  archon:
    name: "Archon"
    type: "core"
    tools: ["rag_search_knowledge_base", "find_tasks", "manage_task", ...]

  scholar:
    name: "Semantic Scholar"
    type: "research"
    skill_name: "scholar-search"

  exa:
    name: "Exa"
    type: "research"
    skill_name: "exa-search"

  clearthought:
    name: "ClearThought"
    type: "reasoning"
    skill_name: "clearthought-reasoning"

  serena:
    name: "Serena"
    type: "implementation"
    tools: ["find_symbol", "get_symbols_overview", ...]
```

### Python Session Manager

Location: `bmad-custom-src/custom/modules/youra-research/session_manager.py`

```python
from session_manager import MCPSessionManager

# Initialize
manager = MCPSessionManager()

# Load phase requirements
availability = manager.initialize_for_phase("phase_4")
# Returns: {"archon": True, "serena": True, "exa": True}

# Check specific server
if manager.is_available("serena"):
    # Use serena tools...

# Get status report
print(manager.get_status_report())

# Validate phase transition
result = manager.validate_phase_transition("phase_2c", "phase_3")
```

### Error Handling

```yaml
error_handling:
  on_required_unavailable: "FAIL" # Stop if required MCP missing
  on_optional_unavailable: "WARN" # Continue if optional missing
  max_retries: 3
  retry_delay_seconds: 15
```

---

## Recovery Procedures

### Scenario 5: Maximum Modification Attempts Reached

**Problem**: Hypothesis has been modified 5 times without success

**State**:
```yaml
hypotheses:
  H-M1-v5:
    modification_attempt: 5
    status: "FAILED"
    reflection:
      has_meaningful_findings: false
      lessons_learned:
        - "Maximum attempts reached"
        - "Core assumption may be invalid"
```

**Recovery Options**:

**Option 1: Fundamental Redesign**
1. Review all 5 version histories
2. Identify common failure patterns
3. Return to Phase 2A with new approach
4. Generate completely new hypothesis

**Option 2: Scope Pivot**
1. Analyze what DID work across versions
2. Create new hypothesis based on partial successes
3. Narrow focus to validated components

**Option 3: Accept Negative Result**
1. Document hypothesis as "disproven"
2. Publish negative findings (valuable for research)
3. Update dependent hypotheses accordingly

**Option 4: External Review**
1. Share findings with domain experts
2. Get feedback on methodology
3. Consider if fundamental assumption is wrong

---

### Scenario 6: Reflection Server Unavailable

**Problem**: ClearThought MCP needed for reflection but unavailable

**State**:
```yaml
# Reflection triggered but ClearThought not available
checkpoint:
  reflection_triggered: true
  clearthought_available: false
```

**Recovery**:
1. Use simplified reflection mode (manual analysis)
2. LLM performs structured analysis without MCP tools
3. Document limitation in reflection report
4. Proceed with modification decision

---

## Workflow Status History

### Overview

The schema introduces **cumulative workflow status tracking** via the `workflow.status_history` array. This enables full traceability of workflow state transitions throughout the pipeline lifecycle.

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Cumulative** | Entries are only appended, never modified or deleted |
| **Chronological** | Each entry includes a timestamp for ordering |
| **Context-Rich** | Each entry captures trigger, phase, and related hypothesis |
| **Traceable** | Enables post-hoc analysis of workflow progression |

### Status History Entry Schema

Each entry in `workflow.status_history` contains:

| Field | Type | Description |
|-------|------|-------------|
| status | enum | Workflow status at this point (ACTIVE/STOPPED/COMPLETED/FAILED) |
| phase | string | Phase when the status change occurred |
| timestamp | ISO8601 | When the change happened |
| trigger | string | What caused the status change |
| hypothesis_id | string? | Related hypothesis ID (if applicable) |
| gate_type | string? | Gate type (if gate-related: MUST_WORK/SHOULD_WORK/DETERMINES_SUCCESS) |
| details | string | Human-readable description of the event |

### When Status History is Updated

| Event | Status | Trigger Example |
|-------|--------|-----------------|
| Pipeline initialization | ACTIVE | "Pipeline initialized" |
| Gate violation (MUST_WORK) | STOPPED | "Gate violation" |
| Reflection completion (modified) | ACTIVE | "Hypothesis modified" |
| Reflection completion (failed) | ACTIVE or FAILED | "No meaningful findings" |
| Individual hypothesis completed | ACTIVE | "Hypothesis validation completed" |
| All hypotheses completed | COMPLETED | "All hypotheses validated" |
| Critical error | FAILED | "Critical error occurred" |

### Example Status History

```yaml
workflow:
  status: "COMPLETED"
  status_history:
    - status: "ACTIVE"
      phase: "Phase 2C"
      timestamp: "2025-12-17T10:00:00Z"
      trigger: "Pipeline initialized"
      details: "Generated from Phase 2B verification plan with 5 hypotheses"

    - status: "ACTIVE"
      phase: "Phase 4"
      timestamp: "2025-12-17T12:00:00Z"
      trigger: "Hypothesis validation completed"
      hypothesis_id: "H-E1"
      gate_result: "PASS"
      details: "H-E1 validation completed with PASS"

    - status: "STOPPED"
      phase: "Phase 4"
      timestamp: "2025-12-17T14:00:00Z"
      trigger: "Gate violation"
      hypothesis_id: "H-M1"
      gate_type: "MUST_WORK"
      details: "H-M1 MUST_WORK failed - workflow paused for reflection"

    - status: "ACTIVE"
      phase: "Phase 4 Reflection"
      timestamp: "2025-12-17T14:30:00Z"
      trigger: "Hypothesis modified"
      hypothesis_id: "H-M1-v2"
      details: "H-M1 modified to H-M1-v2 (SCOPE_REDUCTION)"

    - status: "COMPLETED"
      phase: "Phase 4"
      timestamp: "2025-12-17T18:00:00Z"
      trigger: "All hypotheses validated"
      details: "All 5 hypotheses completed Phase 4 (4 PASS, 1 PARTIAL)"
```

### Querying Status History

To analyze workflow progression:

```python
# Find all STOPPED events
stopped_events = [e for e in status_history if e["status"] == "STOPPED"]

# Find gate violations
gate_violations = [e for e in status_history if e.get("trigger") == "Gate violation"]

# Calculate time between events
from datetime import datetime
durations = []
for i in range(1, len(status_history)):
    t1 = datetime.fromisoformat(status_history[i-1]["timestamp"])
    t2 = datetime.fromisoformat(status_history[i]["timestamp"])
    durations.append((t2 - t1).total_seconds())
```

### Recovery Using Status History

When recovering from a session restart:

1. Read `verification_state.yaml`
2. Check `workflow.status_history[-1]` for last known state
3. Use the last entry's `trigger` and `details` to understand context
4. Resume from appropriate point based on status

---

## Phase 5 Baseline Comparison & Serena Memory Integration

### Overview

The schema introduces Phase 5 Baseline Comparison tracking with Serena Memory integration for cross-phase context persistence. This enables automatic retry of hypotheses when baseline comparison fails, with lessons learned from previous attempts.

### Key Components

| Component | Purpose |
|-----------|---------|
| `baseline_comparison` | Tracks Phase 5 state in verification_state.yaml |
| `05_baseline_checkpoint.yaml` | Per-hypothesis checkpoint with detailed tracking |
| Serena Memory | Cross-phase persistence for failure context (Phase 5 failure → Phase 0) |
| Retry Tracking | Prevents infinite Phase 5 → Phase 0 loops |

### Baseline Comparison Gate

Phase 5 introduces a new gate type for baseline comparison:

| Condition | Gate Result | Action |
|-----------|-------------|--------|
| `ours_best_psi` > `baseline_best_psi` | **PASS** | Proceed to Phase 6 Paper Writing |
| `ours_best_psi` ≤ `baseline_best_psi` | **PARTIAL** | Return to **Phase 0** for NEW research direction |

> **CRITICAL**: Phase 5 PARTIAL routes to **Phase 0**, NOT Phase 2A.
> Baseline underperformance indicates a fundamental approach problem, not an implementation issue.
> A new research direction is needed rather than hypothesis modification.

### State Schema (verification_state.yaml)

Each hypothesis now includes a `baseline_comparison` block:

```yaml
hypotheses:
  H-E1:
    baseline_comparison:
      status: "COMPLETED" # NOT_STARTED | IN_PROGRESS | COMPLETED
      gate_result: "PARTIAL" # PASS | PARTIAL

      selected_baseline:
        name: "repo-name"
        url: "https://github.com/owner/repo"

      results:
        ours_best_psi: 0.65
        baseline_best_psi: 0.78
        performance_gap: -0.13 # negative = we underperform

      failure_context:
        failure_type: "WORSE_THAN_BASELINE"
        gap_percentage: -16.7
        root_cause_analysis: ["Mechanism ineffective at high LR"]
        lessons_learned: ["Combine with baseline optimization"]
        phase2a_feedback:
          suggested_modifications: ["Add momentum-based optimization"]
          avoid_approaches: ["Pure SGD without momentum"]
          what_showed_promise: ["Mechanism effective at LR=0.1"]
        serena_memory_file: "phase5_failure_H-E1.md"

      retry_tracking:
        phase5_retry_count: 1
        max_phase5_retries: 3
        previous_attempts:
          - attempt_number: 1
            hypothesis_id: "H-E1"
            baseline_gate_result: "PARTIAL"
            performance_gap: -0.13
            key_insight: "Mechanism effective at LR=0.1"
```

### Checkpoint Schema (05_baseline_checkpoint.yaml)

The Phase 5 checkpoint includes detailed tracking:

```yaml
version: "2.0"
hypothesis_id: "H-E1"
status: "COMPLETED"

# Gate tracking
baseline_gate:
  result: "PARTIAL"
  ours_best_psi: 0.65
  baseline_best_psi: 0.78
  performance_gap: -0.13

# Failure analysis (Phase 4 pattern)
failure_analysis:
  failure_type: "WORSE_THAN_BASELINE"
  performance_gap:
    ours_best: 0.65
    baseline_best: 0.78
    delta: -0.13
    percentage_gap: -16.7
  root_cause_analysis: [...]
  lessons_learned: [...]
  phase2a_feedback:
    suggested_modifications: [...]
    avoid_approaches: [...]
    what_showed_promise: [...]

# Retry tracking
retry_tracking:
  phase5_retry_count: 1
  max_phase5_retries: 3
  previous_attempts: [...]
  return_to_phase2a: true

# Serena Memory integration
serena_memory:
  failure_memory_file: "phase5_failure_H-E1.md"
  memory_written: true
  memory_written_at: "2025-12-24T10:00:00Z"
```

### Serena Memory Integration

When Phase 5 results in PARTIAL, failure context is saved to Serena Memory:

#### Memory Files Written

| File Pattern | Content | When Written |
|--------------|---------|--------------|
| `phase5_comparison_{id}.md` | Comparison summary | Always (PASS or PARTIAL) |
| `phase5_failure_{id}.md` | Detailed failure analysis | Only on PARTIAL |

#### Memory Content Structure

```markdown
# Phase 5 Failure Record: {hypothesis_id}

**Date:** {timestamp}
**Final Status:** PARTIAL (Baseline Outperforms)
**Retry Attempt:** {n}/{max}

## Performance Gap
| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best ψ | 0.65 | 0.78 | -0.13 (-16.7%) |

**Failure Type:** WORSE_THAN_BASELINE

## Root Cause Analysis
- Mechanism ineffective at high learning rates
- Baseline uses more sophisticated optimization

## Lessons Learned
1. Combine hypothesis with baseline optimization strategy
2. Focus on LR range where mechanism showed promise

## Phase 2A Feedback

### Suggested Modifications
- Add momentum-based optimization
- Narrow focus to LR=0.1 regime

### What NOT To Do
- Pure SGD without momentum
- High learning rates (>0.5)

### What Showed Partial Promise
- Mechanism effective at LR=0.1
- Partial improvement in early epochs
```

#### Phase 2A Memory Loading

When Phase 2A or Phase 0 starts, it checks Serena Memory for previous failures:

```python
# Phase 2A-Extended step-00-initialize.md / Phase 0 step-00-init.md
mcp__serena__list_memories()

# Look for failure/pivot context (priority order)
phase5_failures = [m for m in memories if m.startswith("phase5_failure_")] # Phase 5 PARTIAL
phase4_failures = [m for m in memories if m.startswith("failure_")] # Phase 4 FAIL
phase4_pivots = [m for m in memories if m.startswith("pivot_")] # Phase 4 PARTIAL

# Load with priority: Phase 5 > Phase 4 FAIL > Phase 4 PARTIAL
IF phase5_failures:
    failure_context = mcp__serena__read_memory(memory_file_name=latest_failure)
    # Baseline outperformed - need new research direction
ELIF phase4_failures:
    failure_context = mcp__serena__read_memory(memory_file_name=latest_failure)
    # Fundamental failure - need major hypothesis change
ELIF phase4_pivots:
    pivot_context = mcp__serena__read_memory(memory_file_name=latest_pivot)
    # Hypothesis modification - use suggested new direction
```

### Retry Tracking (Infinite Loop Prevention)

To prevent infinite Phase 5 → Phase 0 loops:

| Field | Default | Description |
|-------|---------|-------------|
| `phase5_retry_count` | 0 | Current retry count |
| `max_phase5_retries` | 3 | Maximum allowed retries |
| `previous_attempts` | [] | History of all attempts |

#### Maximum Retries Reached

When `phase5_retry_count >= max_phase5_retries`:

1. Workflow status set to `STOPPED`
2. Stop reason: "Maximum Phase 5 retries reached"
3. User intervention required

#### Recovery Options (Max Retries)

| Option | Action |
|--------|--------|
| Override limit | Continue (NOT RECOMMENDED) |
| Accept negative | Document findings, conclude research |
| Redesign | Fundamental hypothesis change |
| Abort | End verification |

### Phase 5 Flow with Routing Logic

```
Phase 4 Validation
    ↓ PASS
Phase 5 Baseline Comparison
    ↓
┌────────────────────────┐
│ Gate Evaluation │
│ ours_best vs baseline │
└────────────────────────┘
    ↓ ↓
   PASS PARTIAL
    ↓ ↓
Phase 6 Save to Serena Memory
Paper Writing (phase5_failure_{id}.md)
                       ↓
                  ┌───────────────┐
                  │ Route to │
                  │ Phase 0 │
                  └───────────────┘
                       ↓
                  /phase0-brainstorm
                  (NEW research direction
                   with failure context)
```

> **Why Phase 0, not Phase 2A?**
>
> | Scenario | Routing | Reason |
> |----------|---------|--------|
> | Phase 4 MUST_WORK PARTIAL | Phase 2A-Dialogue | Implementation issue, hypothesis OK |
> | Phase 4 MUST_WORK FAIL | Phase 0 | Fundamental flaw in hypothesis |
> | **Phase 5 Baseline PARTIAL** | **Phase 0** | **Approach fundamentally inferior** |

### Recovery Procedure: Phase 5 PARTIAL Result

**Problem**: Baseline outperforms our method

**State**:
```yaml
baseline_comparison:
  gate_result: "PARTIAL"
  results:
    ours_best_psi: 0.65
    baseline_best_psi: 0.78
```

**Recovery Flow**:

1. **Failure Analysis** (Step 10.5b)
   - Classify failure type: `WORSE_THAN_BASELINE` or `MARGINAL_LOSS`
   - Generate root cause analysis
   - Extract lessons learned
   - Create Phase 0 feedback (NOT Phase 2A)

2. **Save to Serena Memory**
   - Write `phase5_failure_{id}.md` with complete failure context
   - Include lessons learned for Phase 0 brainstorming

3. **Route to Phase 0** (NOT Phase 2A)
   - Execute `/phase0-brainstorm`
   - Phase 0 loads failure context from Serena Memory
   - Generate **NEW research direction**, not just modified hypothesis

> **IMPORTANT**: Phase 5 PARTIAL does NOT route to Phase 2A.
> Baseline underperformance = approach fundamentally inferior = need NEW direction.

---

## Step-Level Archon Task Management

### Overview

The schema introduces **Step-Level Archon Task Management** specifically for Phase 2A. This enables fine-grained progress tracking at the step level within complex workflows.

#### Problem Statement

Phase 2A is a complex multi-step workflow that sometimes causes Claude to:
- Skip sub-agent calls and process directly
- Lose track of which step was completed
- Miss step transition signals

#### Solution

Create Archon tasks at the step level (not just phase level) with:
- Explicit status tracking per step
- Version management for recursive cases
- Clear transition logic between steps

### Task Structure

Phase 2A creates 5 step-level tasks using the `feature` field for version grouping:

```yaml
Pipeline Project (existing)
├── Phase 2A-Dialogue - Hypothesis [doing] # Parent task (existing)
├──── 2A-0: Gap Selection [done] # feature="Phase2A-v1"
├──── 2A-P: Paper Preparation [done]
├──── 2A-1: Round Table [doing]
├──── 2A-2: Hypothesis Synthesis [todo]
└──── 2A-3: Refinement [todo]
```

### Task Creation (step-00-initialize)

When Phase 2A starts, step-00-initialize creates 5 step tasks:

```python
# In phase2a-dialogue/steps/step-00-initialize.md

steps = [
    ("2A-0: Gap Selection", "doing", 100),
    ("2A-P: Paper Preparation", "todo", 95),
    ("2A-1: Round Table Discussion", "todo", 90),
    ("2A-2: Hypothesis Synthesis", "todo", 80),
    ("2A-3: Advocate-Critic Refinement", "todo", 70),
]

for title, status, order in steps:
    mcp__archon__manage_task(
        action="create",
        project_id=pipeline_project_id,
        title=title,
        status=status,
        task_order=order,
        feature=f"Phase2A-v{version}"
    )
```

### Version Management for Recursive Cases

When Phase 4 FAIL or Phase 5 PARTIAL routes back to Phase 2A-Dialogue:

```python
# Detect if this is a recursive entry
memories = mcp__serena__list_memories()
is_recursive = any(
    m.startswith("failure_") or
    m.startswith("pivot_") or
    m.startswith("phase5_failure_")
    for m in memories
)

# Determine version based on existing 2A-0 tasks
IF is_recursive:
    existing = mcp__archon__find_tasks(
        query="2A-0",
        project_id=pipeline_project_id
    )
    version = len(existing) + 1
ELSE:
    version = 1

# Apply version to feature field
feature = f"Phase2A-v{version}" # e.g., Phase2A-v1, Phase2A-v2, ...
```

### Step Transition Logic

Each step is responsible for updating its own task status and starting the next step:

| Step | On Start | On Complete | Next Action |
|------|----------|-------------|-------------|
| step-00 | 2A-0 → doing | 2A-0 → done, 2A-P → doing | Proceed to Paper Prep |
| step-01a | 2A-P → doing | 2A-P → done, 2A-1 → doing | Proceed to Round Table |
| step-01 | 2A-1 → doing | 2A-1 → done, 2A-2 → doing | Proceed to Synthesis |
| step-02 | 2A-2 → doing | 2A-2 → done, 2A-3 → doing | Proceed to Refinement |
| step-03 | 2A-3 → doing | 2A-3 → done, Phase 2A → done, Phase 2A-Ext → doing | Proceed to Phase 2A-Extended |

#### Example: step-01 Completion

```python
# step-01-round-table.md - On Convergence

# 1. Mark current step complete
mcp__archon__manage_task(
    action="update",
    task_id="{2A-1_task_id}",
    status="done"
)

# 2. Start next step
mcp__archon__manage_task(
    action="update",
    task_id="{2A-2_task_id}",
    status="doing"
)

# Display
print("""
✅ Round Table Complete
━━━━━━━━━━━━━━━━━━━━
• 2A-0: Gap Selection [done]
• 2A-P: Paper Preparation [done]
• 2A-1: Round Table [done]
• 2A-2: Synthesis [doing] ← CURRENT
• 2A-3: Refinement [todo]
━━━━━━━━━━━━━━━━━━━━
→ Proceeding to Synthesis
""")
```

### Phase 2A-Extended Integration

Phase 2A-Extended step-00 now checks **step completion** (not phase completion):

```python
# phase2a-extended/steps/step-00-initialize.md

# OLD: Check Phase 2A-Dialogue task done
# phase2a = mcp__archon__find_tasks(query="Phase 2A-Dialogue", status="done")

# NEW: Check 2A-3 (Refinement) step done
latest_version = get_latest_phase2a_version()
refinement_task = mcp__archon__find_tasks(
    query="2A-3",
    filter_by="status",
    filter_value="done"
)

IF NOT refinement_task:
    ERROR: "Phase 2A Step 3 (Refinement) not completed"
    DISPLAY: "Please complete Phase 2A workflow first"
    EXIT
```

### Task ID Storage and Retrieval

Task IDs are stored in a YAML file for cross-step access:

```yaml
# research_folder/phase2a_step_tasks.yaml
version: 1
feature: "Phase2A-v1"
pipeline_project_id: "uuid-pipeline"
tasks:
  gap_selection:
    id: "uuid-1"
    title: "2A-0: Gap Selection"
    status: "done"
  paper_prep:
    id: "uuid-2"
    title: "2A-P: Paper Preparation"
    status: "done"
  round_table:
    id: "uuid-3"
    title: "2A-1: Round Table Discussion"
    status: "doing"
  synthesis:
    id: "uuid-4"
    title: "2A-2: Hypothesis Synthesis"
    status: "todo"
  refinement:
    id: "uuid-5"
    title: "2A-3: Advocate-Critic Refinement"
    status: "todo"
```

#### Fallback: Query by Feature

If the YAML file is lost, tasks can be queried by feature:

```python
# Fallback query
tasks = mcp__archon__find_tasks(
    query="2A-1",
    project_id=pipeline_project_id
)
# Filter by latest version feature
latest_tasks = [t for t in tasks if t["feature"] == f"Phase2A-v{version}"]
task_id = latest_tasks[0]["id"]
```

### Recursive Trigger Points

| Phase | Gate | Result | Action |
|-------|------|--------|--------|
| Phase 4 | MUST_WORK | FAIL | Route to Phase 2A-Dialogue, create step tasks with v{n+1} |
| Phase 5 | DETERMINES_SUCCESS | PARTIAL | Route to Phase 0, Phase 2A-Dialogue (when reached) creates v{n+1} |

#### Phase 4 Gate Processing (Recursive)

```python
# phase4-coding/steps/step-06-gate-processing.md

IF gate_result == "DOES_NOT_WORK":
    # 1. Save failure context to Serena Memory
    mcp__serena__write_memory(
        memory_file_name=f"failure_{hypothesis_id}.md",
        content=failure_context
    )

    # 2. Display routing message
    # (Phase 2A step-00 will detect recursive and use v{n+1})
    DISPLAY:
    """
    ⚠️ MUST_WORK Gate FAIL
    ━━━━━━━━━━━━━━━━━━━━
    Routing to Phase 2A-Dialogue for hypothesis redesign

    Note: Phase 2A will create new step tasks
    with version v{n+1} (feature=Phase2A-v{n+1})

    Previous attempt context saved to:
    failure_{hypothesis_id}.md
    ━━━━━━━━━━━━━━━━━━━━
    → Next: /phase2a-dialogue
    """
```

### Configuration in verification_state.yaml

Add step tracking to the metadata section:

```yaml
workflow:
  # Existing fields...

  # NEW: Step-level tracking for Phase 2A
  phase2a_step_tracking:
    enabled: true
    current_version: 1
    step_tasks_file: "phase2a_step_tasks.yaml"

    versions:
      - version: 1
        feature: "Phase2A-v1"
        created_at: "2025-12-29T10:00:00Z"
        trigger: "initial"
        status: "IN_PROGRESS" # IN_PROGRESS | COMPLETED | FAILED

      # On recursive entry:
      - version: 2
        feature: "Phase2A-v2"
        created_at: "2025-12-29T15:00:00Z"
        trigger: "phase4_must_work_fail"
        previous_failure: "failure_H-M1.md"
        status: "IN_PROGRESS"
```

### Best Practices

1. **Always update step tasks atomically**: Update current step to done AND next step to doing in the same action block
2. **Use feature field consistently**: All step tasks for one attempt share the same feature (e.g., "Phase2A-v1")
3. **Save task IDs immediately**: Write phase2a_step_tasks.yaml right after task creation
4. **Check step status before proceeding**: Each step should verify the previous step is done before starting
5. **Log step transitions in history**: Add workflow.status_history entries for step transitions

---

## Phase 4 Local Checkpoint Task Management

### Overview

The schema introduces **Local Checkpoint Task Management** for Phase 4. Implementation tasks are tracked locally in `04_checkpoint.yaml` instead of Archon MCP, reducing MCP calls from ~30-45 per hypothesis to 2-3.

### Task Hierarchy

| Level | Tracked In | Example | Purpose |
|-------|------------|---------|---------|
| **Hypothesis Task** | Archon | "Phase 4: Implementation (H-E1)" | High-level progress |
| **Implementation Task** | Local `04_checkpoint.yaml` | "A-1: ONNX Export Pipeline" | Detailed execution |

### File Structure

**`03_tasks.yaml`** (Generated by Phase 3 step-09):
```yaml
version: "1.0"
metadata:
  hypothesis_id: "h-e1"
  generated_by: "Phase 3 step-09"
  tier: "FULL" # or "SMOKE_TEST"
tasks:
  - id: "h-e1-task-1"
    title: "A-1: ONNX Export Pipeline"
    description: "Export model to ONNX format"
    status: "todo"
    retry_count: 0
```

**`04_checkpoint.yaml`** (Extended with tasks section):
```yaml
version: "3.1"
hypothesis_id: "h-e1"

# Tasks loaded from 03_tasks.yaml
tasks:
  summary:
    total: 8
    completed: 3
    in_progress: 1
    remaining: 4
  items:
    - id: "h-e1-task-1"
      title: "A-1: ONNX Export Pipeline"
      status: "done"
      started_at: "2026-01-05T10:00:00"
      completed_at: "2026-01-05T10:30:00"
      sdd_phases:
        test: "passed"
        impl: "passed"
        verify: "passed"
    - id: "h-e1-task-2"
      status: "doing"
      # ...

current_task_index: 3
```

### Phase 4 Resume Logic

```python
# Priority: checkpoint > verification_state > Archon

# 1. Check local checkpoint first (PRIMARY)
checkpoint = read_yaml("{hypothesis_folder}/04_checkpoint.yaml")
IF checkpoint.current_step > 0:
    resume_from_step = checkpoint.current_step
    current_task_index = checkpoint.current_task_index
    tasks = checkpoint.tasks.items

# 2. If no checkpoint, check verification_state
verification_state = read_yaml("{research_folder}/verification_state.yaml")
IF h_data["validation"]["status"] == "IN_PROGRESS":
    # Initialize from 03_tasks.yaml

# 3. Archon only for Hypothesis Task status update
hypothesis_task_id = verification_state["metadata"]["hypothesis_task_mapping"][hypothesis_id]
```

### Task Status Flow (Local Checkpoint)

```
todo → doing → review → done
  ↑ │
  └──────┘ (on retry)
```

Tasks transition:
- `todo` → `doing`: When Coder Agent starts task
- `doing` → `review`: When SDD cycle completes (TEST → IMPL → VERIFY)
- `review` → `done`: When Validator confirms all tests pass

### Archon Integration (Hypothesis-Level Only)

Archon is only updated for:
1. **Hypothesis Task status** (e.g., "Phase 4: Implementation (H-E1)")
2. **Gate results** (PASS, PARTIAL, FAIL)

```python
# On gate evaluation (step-06)
mcp__archon__manage_task(
    action="update",
    task_id=hypothesis_task_id,
    status="done", # or "review" for PARTIAL
    description=f"Gate Result: {gate_result}"
)
```

### Benefits

| Aspect | Before (Archon) | After (Local Checkpoint) |
|--------|-----------------|-------------------------|
| MCP Calls | ~30-45/hypothesis | 2-3/hypothesis |
| Latency | High (API calls) | Low (local file I/O) |
| Offline Support | No | Yes |
| Recovery | Query Archon | Read checkpoint file |

---

## SUPERSEDED Status Handling

### Overview

The schema introduces **SUPERSEDED** status for hypotheses that have PARTIAL results but are incompatible with dependent hypotheses. This is different from FAILED (complete failure) and triggers Phase 2A-Dialogue redesign with a new hypothesis version.

### Status Distinction

| Status | Trigger | Route | Partial Results |
|--------|---------|-------|-----------------|
| **VALIDATED** | Gate PASS | Phase 5 | N/A |
| **PARTIAL** | Gate 50-99% criteria met | Reflection | Yes |
| **SUPERSEDED** | Reflection: incompatible with dependents | Phase 2A-Dialogue | Preserved |
| **FAILED** | Gate FAIL or unrecoverable | Phase 0 | Lost |
| **CASCADE_SUPERSEDED** | Parent SUPERSEDED | Await new | N/A |
| **CASCADE_FAILED** | Parent FAILED | N/A (done) | N/A |

### LLM Self-Assessment Flow (step-06b-reflection.md)

```python
# For PARTIAL results, LLM self-assessment determines next action
IF gate_result == "PARTIAL":
    assessment = llm_self_assessment(
        hypothesis_id=hypothesis_id,
        partial_results=results,
        dependents=find_dependent_hypotheses(hypothesis_id)
    )

    # Assessment criteria:
    # 1. Interface compatibility: Do outputs match dependent inputs?
    # 2. Data flow validity: Are tensor shapes/types correct?
    # 3. Behavioral assumptions: Are guarantees met?
    # 4. Recovery potential: Can issues be fixed without redesign?

    IF all_criteria_compatible:
        # SELF_MODIFY: Retry within same hypothesis ID
        action = "SELF_MODIFY"
    ELSE:
        # SUPERSEDED: Needs Phase 2A-Dialogue redesign with new hypothesis ID
        action = "SUPERSEDED"
        new_hypothesis_id = f"{hypothesis_id}-v2"
```

### Cascade Handling

When a hypothesis is SUPERSEDED:

1. **Mark source hypothesis as SUPERSEDED**
   ```python
   verification_state["sub_hypotheses"][hypothesis_id]["status"] = "SUPERSEDED"
   verification_state["sub_hypotheses"][hypothesis_id]["superseded"] = {
       "superseded_by": new_hypothesis_id,
       "superseded_at": datetime.now().isoformat(),
       "superseded_reason": "LLM self-assessment determined incompatibility"
   }
   ```

2. **Mark dependent hypothesis tasks as CASCADE_SUPERSEDED**
   ```python
   for dep in find_dependent_hypotheses(hypothesis_id):
       verification_state["sub_hypotheses"][dep]["status"] = "CASCADE_SUPERSEDED"
       verification_state["sub_hypotheses"][dep]["awaiting"] = new_hypothesis_id
   ```

3. **Update Archon Hypothesis Task**
   ```python
   mcp__archon__manage_task(
       action="update",
       task_id=hypothesis_task_id,
       title=f"[SUPERSEDED → {new_hypothesis_id}] {old_title}",
       status="done"
   )
   ```

4. **Save to Serena Memory**
   ```python
   mcp__serena__write_memory(
       memory_file_name=f"superseded_{hypothesis_id}.md",
       content=superseded_record
   )
   ```

### State Schema Fields

```yaml
sub_hypotheses:
  h-e1:
    status: "SUPERSEDED" # or CASCADE_SUPERSEDED

    # SUPERSEDED fields
    superseded:
      superseded_by: "h-e1-v2"
      superseded_at: "2026-01-05T10:00:00"
      superseded_reason: "LLM self-assessment: tensor shape mismatch"
      partial_results_preserved: true

    # For CASCADE_SUPERSEDED
    awaiting: "h-e1-v2" # New version to wait for

statistics:
  superseded_sub_hypotheses: 1 # NEW counter
```

### Related Helper Files

| File | Purpose |
|------|---------|
| `helpers/archon_cascade.md` | `mark_hypothesis_superseded()`, `mark_dependent_tasks_cascade_superseded()` |
| `helpers/gate_evaluation.md` | `get_superseded_routing()` |
| `phase4-coding/steps/step-06b-reflection.md` | LLM self-assessment logic |

---

## SHOULD_WORK SELF_MODIFY Flow

### Overview

The schema introduces **LLM Self-Assessment for SHOULD_WORK gates** that enables optional hypotheses to trigger SELF_MODIFY after exhausting self-recovery retries. This extends the Phase 4 reflection capability to SHOULD_WORK gates.

### Key Difference from MUST_WORK

| Aspect | MUST_WORK | SHOULD_WORK |
|--------|-----------|-------------|
| **Gate Type** | Required (blocks pipeline) | Optional (doesn't block) |
| **LLM Assessment** | 4 questions (with compatibility check) | 2 questions (no compatibility check) |
| **On FAIL after max retries** | Route to Phase 0 | Record limitation, continue |
| **On SELF_MODIFY decision** | Route to Phase 2A-Dialogue | Route to Phase 2C |
| **Cascade Handling** | Yes (dependents affected) | No (optional gate) |
| **Helper File** | `llm_self_assessment.md` | `llm_self_assessment_should_work.md` |

### Flow Diagram

```
SHOULD_WORK Gate Result: FAIL/PARTIAL
              │
              ▼
    ┌─────────────────┐
    │ Retry Count < 3?│
    └─────────────────┘
         │YES │NO
         ▼ ▼
    Self-Recovery LLM Assessment
    (Step 6b) (Step 6b)
         │ │
         ▼ ┌────┴────┐
    Re-run │         │
    Validation SELF_ FAIL
                MODIFY │
                  │ ▼
                  ▼ Record
             Phase 2C Limitation
             (Modify) │
                  │ ▼
                  ▼ Phase 5
             Phase 3 (Continue)
                  │
                  ▼
             Phase 4
             (Retry)
```

### LLM Assessment Questions (2 Questions)

Unlike MUST_WORK's 4-question assessment, SHOULD_WORK uses a simplified 2-question assessment:

| Question | Purpose |
|----------|---------|
| **Improvement Potential** | "Can you identify a specific, actionable modification that would improve results?" |
| **Worth Retry** | "Is there at least 50% probability that Phase 2C modifications would lead to passing?" |

### Decision Matrix

| Improvement Potential | Worth Retry | Decision | Action |
|-----------------------|-------------|----------|--------|
| Yes | Yes | **SELF_MODIFY** | Route to Phase 2C |
| Yes | No | FAIL | Record limitation |
| No | Yes | FAIL | Record limitation |
| No | No | FAIL | Record limitation |
| Error | Error | FAIL (default) | Record limitation |

> **Conservative Default:** On assessment failure, default to FAIL (record limitation).
> This is appropriate for optional gates - we don't block the pipeline on uncertainty.

### State Schema Fields

```yaml
hypotheses:
  h-m1:
    gate:
      type: "SHOULD_WORK"
      satisfied: false

    should_work_retry_count: 3

    llm_assessment:
      type: "SHOULD_WORK_SELF_MODIFY" # or "SHOULD_WORK_FAIL"
      improvement_potential: true
      worth_retry: true
      modification_suggestion: "Reduce learning rate from 0.1 to 0.01"
      confidence: "60%"

    # For SELF_MODIFY decision
    reflection_outcome: "SELF_MODIFY" # or "LIMITATION_RECORDED"
    modification_attempt: 1

    # For FAIL decision
    should_work_failed: true
    limitation_note: "h-m1: No specific improvement identified; Low probability of success"
```

### Checkpoint Fields (04_checkpoint.yaml)

```yaml
version: "3.2"
hypothesis_id: "h-m1"

reflection_type: "llm_assessment_should_work" # or "self_recovery"
should_work_retry_count: 3
allow_phase2c_route: true # NEW: Can route to Phase 2C

# After LLM assessment
llm_assessment: "SHOULD_WORK_SELF_MODIFY" # or "SHOULD_WORK_FAIL"
reflection_outcome: "SELF_MODIFY" # or "LIMITATION_RECORDED"
modification_suggestion: "..."

# For FAIL decision
should_work_failed: true
limitation_note: "..."
```

### Related Files

| File | Purpose |
|------|---------|
| `helpers/llm_self_assessment_should_work.md` | 2-question LLM assessment functions |
| `helpers/gate_evaluation.md` | SHOULD_WORK config with `llm_assessment_available: true` |
| `phase4-coding/steps/step-06-gate-processing.md` | Section 5: LLM assessment trigger |
| `phase4-coding/steps/step-06b-reflection.md` | Section 1b: LLM assessment branch |

### Usage Example (step-06b-reflection.md)

```python
# When gate_type == "SHOULD_WORK" AND reflection_type == "llm_assessment_should_work"

from llm_self_assessment_should_work import perform_llm_self_assessment_should_work

result = perform_llm_self_assessment_should_work(
    hypothesis_id,
    pass_rate,
    failed_checks,
    experiment_summary=checkpoint.get("experiment_summary")
)

IF result["decision"] == "SELF_MODIFY":
    # Create new hypothesis version (e.g., h-m1-v2)
    new_hypothesis_id = f"{hypothesis_id}-v{version + 1}"
    checkpoint.route_to = "phase2c"
    # → Phase 2C → Phase 3 → Phase 4 retry
ELSE:
    # Record limitation, continue to Phase 5
    checkpoint.should_work_failed = True
    checkpoint.limitation_note = result["reasoning"]
    # → Phase 5 (acceptable for optional gate)
```

---

## Related Documents

- **Phase 2B Instructions**: `bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning/instructions.md`
- **Phase 2C Instructions**: `bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design/instructions.md`
- **Phase 2C Workflow**: `bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design/workflow.yaml`
- **Phase 5 Workflow**: `bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison/workflow.yaml`
- **Phase 5 Fair Comparison Guide**: `bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison/_references/fair-comparison-principle.md`
- **State Template**: `bmad-custom-src/custom/modules/youra-research/workflows/verification_state_template.yaml`

---

*Generated as part of the Anonymous Research Pipeline state tracking system*
