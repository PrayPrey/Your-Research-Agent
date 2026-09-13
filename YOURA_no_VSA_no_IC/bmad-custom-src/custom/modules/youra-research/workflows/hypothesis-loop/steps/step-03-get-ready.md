---
name: 'step-03-get-ready'
description: 'Get READY hypotheses queue sorted by dependency order'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-03-get-ready.md'
nextStepFile: '{workflow_path}/steps/step-04-loop-start.md'
completeStepFile: '{workflow_path}/steps/step-11-complete.md'
workflowFile: '{workflow_path}/workflow.md'
stateManagementHelper: '{workflow_path}/helpers/state_management.md'
---

# Step 3: Get Ready Hypotheses

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Collect all READY sub-hypotheses, prioritize any IN_PROGRESS hypothesis (resume case), and sort by dependency order. Display the execution queue.

## MANDATORY EXECUTION RULES

- 📖 Read complete step file before action
- 🔄 Auto-proceed to loop or Phase 5 based on queue
- 🚫 NEVER skip IN_PROGRESS hypothesis (resume case)

<critical>
DO NOT assume dictionary structure for sub_hypotheses.
</critical>

---

## EXECUTION SEQUENCE

### 1. Check for IN_PROGRESS Hypothesis (Resume Case)

**Instructions:**

1. Scan ALL hypotheses in sub_hypotheses
2. Find any hypothesis with status = `IN_PROGRESS`
3. If found:
   - Display: `📍 **Resuming:** {hypothesis_id}`
   - Set `ready_hypotheses` to contain ONLY this hypothesis
   - Skip to Section 5 (display queue)

**Rationale:** IN_PROGRESS means we're resuming from a previous session. This hypothesis has priority.

### 2. Collect READY Hypotheses

**If no IN_PROGRESS found:**

1. Create empty list for `ready_hypotheses`
2. Scan ALL hypotheses in sub_hypotheses
3. For each hypothesis with status = `READY`:
   - Add its ID to `ready_hypotheses`

### 3. Sort by Dependency Order

**Instructions:**

1. Create empty list for `sorted_hypotheses`
2. Create set of remaining hypotheses from `ready_hypotheses`

3. **Repeat until remaining is empty:**
   - For each hypothesis in remaining:
     - Get its `prerequisites` list
     - Check if ALL prerequisites are either:
       - NOT in remaining list (already sorted or not applicable), OR
       - Already satisfied (status = VALIDATED/COMPLETED)
     - If yes: Add to `sorted_hypotheses` and remove from remaining
     - Break inner loop after adding one

   - If no hypothesis could be added (circular dependency):
     - Add all remaining to sorted_hypotheses as-is
     - Break outer loop

4. Set `ready_hypotheses` to `sorted_hypotheses`

**Result:** Hypotheses ordered so prerequisites come before dependents.

### 4. Check for Empty Queue

**If `ready_hypotheses` is empty:**

1. Display:
   ```
   ℹ️ **No sub-hypotheses available for processing**

   Possible reasons:
   - All sub-hypotheses are VALIDATED or FAILED
   - Dependencies not satisfied (check BLOCKED status)
   - Workflow needs Phase 2B to generate sub-hypotheses

   Run `/hypothesis-status` to see current state.
   ```

2. **Check if all processed (for Phase 5 transition):**

   a. Scan ALL hypotheses in sub_hypotheses
   b. Define unprocessed states: `READY`, `IN_PROGRESS`, `NOT_STARTED`, `PENDING`
   c. For each hypothesis:
      - If status is in unprocessed states:
        - Display: ` ⏳ {hypothesis_id}: {status} (unprocessed)`
        - Set `all_processed = FALSE`

   d. **If all_processed = TRUE:**
      - Display: `→ All sub-hypotheses processed. Proceeding to completion summary...`
      - Go to `step-11-complete.md` **

   e. **If all_processed = FALSE:**
      - Display: `→ Some hypotheses still waiting (NOT_STARTED/PENDING). Check prerequisites.`
      - EXIT

### 5. Display Execution Queue

**If `ready_hypotheses` is NOT empty:**

1. Display: `📋 **Execution Queue:** ({count} hypotheses)`

2. For each hypothesis in `ready_hypotheses` (in order):
   - Get hypothesis details from sub_hypotheses
   - Determine gate icon:
     - 🔴 MUST_WORK
     - 🟡 SHOULD_WORK
     - 🟢 DETERMINES_SUCCESS
   - Get prerequisites list (or "None" if empty)
   - Display: ` {index}. {hypothesis_id} | {icon} {gate_type} | Prereqs: {prerequisites}`

3. Display legend:
   ```
   Legend: 🔴 MUST_WORK | 🟡 SHOULD_WORK | 🟢 DETERMINES_SUCCESS
   ```

### 6. Store Queue in Memory

1. Set `current_hypothesis_index` to 0
2. Set `hypothesis_queue` to `ready_hypotheses`

These values are used by step-04 and step-09 for loop iteration.

---

## STEP COMPLETION

**Immediately** load, read entire file, then execute `{workflow_path}/steps/step-04-loop-start.md` to begin processing first hypothesis.

---

#

**Previous Issue:** Python pseudocode assumed dictionary structure:
```python
for h_id, h in state.sub_hypotheses.items(): # ❌ Fails on array
```

**Fix:** Natural language instructions:
```
For each hypothesis in sub_hypotheses:
  Check if its status is "READY"
```

This works regardless of whether sub_hypotheses is array or dictionary.

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Queue collected and sorted correctly
- IN_PROGRESS hypothesis prioritized
- Empty queue handled gracefully
- Queue displayed clearly
- Unprocessed states correctly identified (including NOT_STARTED)

### ❌ FAILURE
- Ignoring IN_PROGRESS hypothesis
- Incorrect dependency sorting
- Proceeding with empty queue without checking Phase 5
- **Assuming dictionary structure**
