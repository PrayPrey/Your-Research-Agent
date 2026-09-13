---
name: 'step-08-phase4-gate'
description: 'Process Phase 4 MUST_WORK gate and handle routing'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-08-phase4-gate.md'
nextStepFile: '{workflow_path}/steps/step-09-loop-continue.md'
workflowFile: '{workflow_path}/workflow.md'
stateManagementHelper: '{workflow_path}/helpers/state_management.md'
---

# Step 8: Phase 4 Gate Processing (MUST_WORK)

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Process the Phase 4 MUST_WORK gate result from 04_checkpoint.yaml. Handle routing based on reflection_outcome:
- PASS → Continue to next hypothesis
- MODIFIED → New hypothesis created, continue loop
- ROUTED_TO_PHASE_0 → Fundamental flaw, exit to Phase 0
- ROUTED_TO_PHASE_2A → Max attempts reached, exit to Phase 2A-Dialogue

## MANDATORY EXECUTION RULES

<critical>
**GATE ROUTING IS CRITICAL**

The reflection_outcome in 04_checkpoint.yaml determines the next action:
- Serena Memory has ALREADY been saved by step-06b-reflection.md in Phase 4
- This step reads the outcome and routes accordingly

DO NOT assume dictionary structure for sub_hypotheses.
</critical>

---

## EXECUTION SEQUENCE

### 1. Read Phase 4 Checkpoint

1. Open the hypothesis folder's `04_checkpoint.yaml`
2. Extract `reflection_outcome` field (may be null if gate passed directly)
3. Extract `partial_results.gate_result` field

Display:
```
📊 Phase 4 Gate Result: {gate_result}
   Reflection Outcome: {reflection_outcome}
```

### 2. Process Gate Result

Based on the gate_result and reflection_outcome, execute ONE of the following scenarios:

---

#### 2A. PASS Scenario

**Condition:** `gate_result == "PASS"`

**Actions:**

1. **Update the current hypothesis in verification_state.yaml:**
   - Find the hypothesis with matching ID in sub_hypotheses
   - Set its `status` to `VALIDATED`
   - Set its `gate.satisfied` to `true`

2. **Display success message:**
   ```
   ✅ Phase 4 MUST_WORK gate PASSED
   → Hypothesis validated. Proceeding to next sub-hypothesis...
   ```

3. **Update dependent hypotheses (CRITICAL for loop continuation):**
   - Read `helpers/state_management.md` section "Update Dependent Hypotheses Status"
   - Find ALL hypotheses with status = "NOT_STARTED"
   - For each, check if the current hypothesis is in its prerequisites
   - If ALL prerequisites are now satisfied, change status to "READY"
   - Display count of hypotheses that became READY

4. **Update Archon tasks:**
   - Mark Hypothesis Phase Task as "done"
   - Mark Hypothesis Task as "done" with prefix "[VALIDATED]"

5. **Save verification_state.yaml**

6. **Result:** `action = "VALIDATED"`

---

#### 2B. MODIFIED Scenario

**Condition:** `reflection_outcome == "MODIFIED"`

**Actions:**

1. **Get new hypothesis ID** from checkpoint's `new_hypothesis_id` field

2. **Update the current hypothesis in verification_state.yaml:**
   - Find the hypothesis with matching ID in sub_hypotheses
   - Set its `status` to `COMPLETED`
   - Set its `gate.satisfied` to `true` (for dependency resolution)

3. **Display modification message:**
   ```
   🔄 Hypothesis modified: {hypothesis_id} → {new_hypothesis_id}
   New hypothesis will be processed in next iteration
   ```

4. **Update dependent hypotheses:**
   - Same as PASS scenario - dependents can proceed because new version handles validation

5. **Update Archon tasks:**
   - Mark Hypothesis Task as "done" with prefix "[MODIFIED → {new_id}]"

6. **Save verification_state.yaml**

7. **Result:** `action = "MODIFIED", new_hypothesis_id = {new_id}`

---

#### 2C. ROUTED_TO_PHASE_0 Scenario

**Condition:** `reflection_outcome == "ROUTED_TO_PHASE_0"`

**Actions:**

1. **Update the current hypothesis in verification_state.yaml:**
   - Find the hypothesis with matching ID in sub_hypotheses
   - Set its `status` to `FAILED`
   - Set its `gate.satisfied` to `false`

2. **Update workflow routing:**
   - Set `workflow.status` to `ROUTED`
   - Set `workflow.routing.target` to `Phase 0`
   - Set `workflow.routing.source_hypothesis` to current hypothesis ID
   - Set `workflow.routing.reason` to `MUST_WORK_FAIL`
   - Set `workflow.stop_reason` to `Phase 4 MUST_WORK FAIL - routing to Phase 0`

3. **Display routing message:**
   ```
   🔴 **Phase 4 MUST_WORK gate FAILED (fundamental flaw)**

   Hypothesis has a fundamental flaw that cannot be addressed through modification.

   📝 Serena Memory saved: failure_{hypothesis_id}.md
   🔄 Routing to Phase 0 for new research direction...
   ```

4. **Update Archon tasks:**
   - Mark Hypothesis Task as "done" with prefix "[FAILED → Phase 0]"

5. **Save verification_state.yaml**

6. **Result:** `action = "ROUTE_TO_PHASE_0"`

---

#### 2D. ROUTED_TO_PHASE_2A Scenario

**Condition:** `reflection_outcome == "ROUTED_TO_PHASE_2A"`

**Actions:**

1. **Update the current hypothesis in verification_state.yaml:**
   - Find the hypothesis with matching ID in sub_hypotheses
   - Set its `status` to `FAILED`
   - Set its `gate.satisfied` to `false`

2. **Update workflow routing:**
   - Set `workflow.status` to `ROUTED`
   - Set `workflow.routing.target` to `Phase 2A-Dialogue`
   - Set `workflow.routing.source_hypothesis` to current hypothesis ID
   - Set `workflow.routing.reason` to `MAX_ATTEMPTS_REACHED`
   - Set `workflow.stop_reason` to `Phase 4 PARTIAL - max modification attempts reached`

3. **Display routing message:**
   ```
   🟡 **Phase 4 MUST_WORK gate PARTIAL (max attempts reached)**

   Hypothesis showed partial success but cannot pass gate after maximum attempts.

   📝 Serena Memory saved: pivot_{hypothesis_id}_{new_hypothesis_id}.md
   🔄 Routing to Phase 2A-Dialogue for hypothesis redesign...
   ```

4. **Update Archon tasks:**
   - Mark Hypothesis Task as "done" with prefix "[PARTIAL → Phase 2A-Dialogue]"

5. **Save verification_state.yaml**

6. **Result:** `action = "ROUTE_TO_PHASE_2A"`

---

#### 2E. FAILED Scenario (No Meaningful Findings)

**Condition:** `reflection_outcome == "FAILED"`

**Actions:**

1. **Update the current hypothesis in verification_state.yaml:**
   - Find the hypothesis with matching ID in sub_hypotheses
   - Set its `status` to `FAILED`
   - Set its `gate.satisfied` to `false`

2. **Display failure message:**
   ```
   ❌ **Phase 4 reflection found no meaningful findings**

   Hypothesis failed without actionable insights for modification.

   → Continuing to next sub-hypothesis...
   ```

3. **Update Archon tasks:**
   - Mark Hypothesis Task as "done" with prefix "[FAILED]"

4. **Save verification_state.yaml**

5. **Result:** `action = "FAIL"`

---

#### 2F. Unexpected State

**Condition:** None of the above conditions match

**Actions:**

1. Display warning: `⚠️ Unexpected Phase 4 state - treating as FAIL`
2. Update hypothesis status to `FAILED`, gate.satisfied to `false`
3. Save verification_state.yaml
4. **Result:** `action = "FAIL"`

---

### 3. Handle Routing Actions

Based on the action from Step 2:

**If action is "ROUTE_TO_PHASE_0":**
```
🛑 **Workflow ROUTED - Routing to Phase 0**

Next action: Execute `/phase0-brainstorm` for new research direction
```
→ EXIT (do not proceed to step-09)

**If action is "ROUTE_TO_PHASE_2A":**
```
🛑 **Workflow ROUTED - Routing to Phase 2A-Dialogue**

Next action: Execute `/phase2a-dialogue` for full hypothesis regeneration
```
→ EXIT (do not proceed to step-09)

**If action is "FAIL" (unexpected):**
```
🛑 **Unexpected failure - Check 04_checkpoint.yaml**
```
→ EXIT

**If action is "VALIDATED" or "MODIFIED":**
→ Proceed to STEP COMPLETION

---

## STEP COMPLETION

Gate processing complete. If VALIDATED or MODIFIED, proceed to loop continuation.

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-09-loop-continue.md` to handle mode actions and loop control.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Gate result read from checkpoint
- Correct routing based on reflection_outcome
- Hypothesis status updated in verification_state.yaml
- Dependent hypotheses updated to READY (for PASS/MODIFIED)
- Proper exit for routing cases

### ❌ FAILURE
- Ignoring reflection_outcome
- Not routing FAIL cases properly
- Continuing after ROUTE_TO_PHASE_0/2A
- Not updating state
- **Not updating dependent hypotheses (causes H-M1 skip bug)**
