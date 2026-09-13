---
name: 'step-09-loop-continue'
description: 'Mode-specific actions and loop continuation control'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-09-loop-continue.md'
loopStartFile: '{workflow_path}/steps/step-04-loop-start.md'
completeStepFile: '{workflow_path}/steps/step-11-complete.md'
workflowFile: '{workflow_path}/workflow.md'
stateManagementHelper: '{workflow_path}/helpers/state_management.md'
---

# Step 9: Loop Continuation Control

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Handle mode-specific actions after hypothesis completion and control loop iteration:
- AUTO mode: Automatically proceed to next hypothesis
- STEP mode: Ask user for confirmation
- SINGLE mode: Exit after first hypothesis
- Check if **ALL** sub-hypotheses are done → only then proceed to completion/Phase 5

<critical>
**PHASE 5 PRECONDITION**

Phase 5 can ONLY be triggered when **ALL sub-hypotheses have completed Phase 4**.

```
H-E1 (Phase 4 PASS) + H-M1 (NOT_STARTED) → ❌ DO NOT go to Phase 5
                                          → ✅ Continue loop (H-M1 becomes READY)

H-E1 (VALIDATED) + H-M1 (VALIDATED) → ✅ ALL done → Phase 5 allowed
```

**NEVER proceed to Phase 5 if ANY hypothesis is still READY, IN_PROGRESS, NOT_STARTED, or PENDING.**
</critical>

## MANDATORY EXECUTION RULES

<critical>
**RE-CHECK EXECUTION MODE BEFORE ANY USER INTERACTION**

Re-read verification_state.yaml to get current execution_mode.
UNATTENDED mode = AUTO mode (no user prompts).

DO NOT assume dictionary structure for sub_hypotheses.
</critical>

---

## EXECUTION SEQUENCE

### 1. Re-Read Execution Mode

1. Load verification_state.yaml
2. Check `workflow.execution_mode`
3. If mode is `UNATTENDED`, treat as `AUTO`

### 2. Check Workflow Status

1. If `workflow.status` is `STOPPED`:
   - Display: `🛑 **Workflow Stopped:** {workflow.stop_reason}`
   - Display: `Run /hypothesis-status for details`
   - EXIT

### 3. Handle SINGLE Mode

If execution_mode is `SINGLE`:
```
1️⃣ **Single mode: 1 hypothesis completed**

Exiting as requested. Run `/hypothesis-loop` to continue with remaining hypotheses.
```
→ EXIT

### 4. Handle STEP Mode (Non-UNATTENDED Only)

If NOT UNATTENDED and execution_mode is `STEP`:

1. Display current hypothesis result:
   ```
   ✓ **{hypothesis_id}** completed
      Result: {action from step-08}
      Gate Satisfied: {gate.satisfied}

   [Y] Next hypothesis
   [N] End for now
   [S] Show status
   [R] Retry this hypothesis
   [Q] Quit
   ```

2. Ask user: "Continue?"

3. Handle response:
   - `N` or `Q`: Save state and EXIT
   - `S`: Show status and re-display menu
   - `R`: Set hypothesis status to READY, go to step-04-loop-start.md
   - `Y` or default: Continue to Section 5

### 5. Handle AUTO Mode (Default)

If UNATTENDED or execution_mode is `AUTO`:
- Display: `✓ **{hypothesis_id}** complete → Proceeding automatically...`
- Do NOT ask user - continue immediately

### 6. Check for More Hypotheses in Current Queue

1. Increment `current_hypothesis_index` by 1
2. Compare with length of `hypothesis_queue`

**If more hypotheses remain in queue:**
- Get next hypothesis from queue
- Go to `step-04-loop-start.md`

**If queue is exhausted:**
- Continue to Section 7 (check if truly all done)

<critical>
**IMPORTANT:** Queue exhausted does NOT mean all hypotheses are done!
New hypotheses may have become READY during processing (e.g., H-M1 after H-E1 validated).
MUST check all_processed in Section 7.
</critical>

---

### 7. Check If All Sub-Hypotheses Are Processed

<critical>
** FIX:** This section uses natural language to avoid structure assumptions.
</critical>

**Instructions:**

1. **Define unprocessed states:**
   - `READY` - Waiting to be picked up
   - `IN_PROGRESS` - Currently being processed
   - `NOT_STARTED` - Prerequisites not yet satisfied
   - `PENDING` - Alias for NOT_STARTED

2. **Scan ALL hypotheses in sub_hypotheses:**
   - For EACH hypothesis, check its status
   - If ANY hypothesis has status in unprocessed states → `all_processed = FALSE`

3. **Determine result:**
   - If found ANY unprocessed hypothesis → `all_processed = FALSE`
   - If ALL hypotheses have processed states → `all_processed = TRUE`

**Processed states (count as done):**
- `VALIDATED`, `COMPLETED`, `FAILED`, `CASCADE_FAILED`, `BLOCKED`, `SUPERSEDED`, `CASCADE_SUPERSEDED`

---

### 8. Handle Based on all_processed Result

<critical>
**/3.8 FIX:** Explicit IF-ELSE to prevent premature Phase 5 trigger
</critical>

---

#### 8A. If NOT all_processed (Unprocessed Hypotheses Exist)

**Condition:** `all_processed = FALSE`

<critical>
** MANDATORY QUEUE REFRESH**

When ANY hypothesis has status in [READY, IN_PROGRESS, NOT_STARTED, PENDING]:
- **MUST** return to step-03-get-ready.md to rebuild the queue
- **DO NOT** proceed to completion or Phase 5

**Common Scenario (H-E1 → H-M1):**
```
1. H-E1 validated → step-08-phase4-gate updates H-M1 to READY
2. Current queue [H-E1] is exhausted
3. Section 7 finds H-M1 with status=READY → all_processed=FALSE
4. MUST go to step-03 to pick up H-M1
```

**If you skip this step:** H-M1 will never be processed!
</critical>

**Action:** New hypotheses may have become READY. Refresh the queue.

1. Display: `📋 Refreshing hypothesis queue (new READY hypotheses may exist)...`
2. Go to `step-03-get-ready.md` to rebuild queue

---

#### 8B. If all_processed (All Hypotheses Done)

**Condition:** `all_processed = TRUE`

**Action:** All sub-hypotheses are in final states. Proceed to completion.

1. Check `workflow.execution_source`:

**If execution_source is "full-pipeline":**

<critical>
** FIX: Phase 5 State Preparation**

MUST prepare verification_state for Phase 5 BEFORE exiting.
This ensures Phase 5 Step 01-init can proceed without state errors.
</critical>

**Step 1: Update workflow markers in verification_state.yaml**

Update the following fields:

| Field | Value | Note |
|-------|-------|------|
| `workflow.current_phase` | "Phase 5" | **CRITICAL:** Phase 5 init checks this value |
| `workflow.sub_hypotheses_complete` | true | Marks all sub-hypotheses as complete |
| `workflow.phase4_completed_at` | Current timestamp | Records Phase 4 completion time |
| `workflow.next_action` | "Proceed to Phase 5 (Baseline Comparison)" | Specifies next action |

**Step 2: Verify sub-hypothesis completion markers**

Scan all sub-hypotheses:
- For each hypothesis with `validation.status` = "COMPLETED"
- If `phase4_completed` field is missing, add:
  - `phase4_completed` = true
  - `phase4_completed_at` = Current timestamp

**Step 3: Add transition marker to history**

Append the following event to `status_history` array:

| Field | Value |
|-------|-------|
| status | "PHASE_TRANSITION" |
| phase | "Phase 4 → Phase 5" |
| timestamp | Current timestamp |
| trigger | "All sub-hypotheses completed" |
| details | "Hypothesis loop complete. {N} hypotheses validated." |

**Step 4: Save and confirm**

- Save verification_state.yaml file.
- Log output: `✅ Phase 5 state prepared`

**Step 5: EXIT**

Return control to full-pipeline Step 7.5 for Phase 5 invocation.

**If execution_source is "standalone" (default):**
- Update `workflow.current_phase` to `Hypothesis Loop Complete`
- Set `workflow.sub_hypotheses_complete` to `true`
- Save verification_state.yaml
- Go to `step-11-complete.md` for summary

---

## LOOP CONTROL SUMMARY

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Section 6: More hypotheses in current queue? │
│ YES → Go to step-04-loop-start.md (next hypothesis in current queue) │
│ NO → Continue to Section 7-8 (queue exhausted, check all_processed) │
├──────────────────────────────────────────────────────────────────────────┤
│ Section 7-8: Check all sub-hypotheses processed │
│ │
│ IF any hypothesis has status in [READY, IN_PROGRESS, NOT_STARTED, │
│ PENDING]: │
│ → Go to step-03-get-ready.md (refresh queue - new READY exists) │
│ │
│ ELSE (all hypotheses in final states): │
│ → execution_source == "full-pipeline"? │
│ YES → EXIT (return to full-pipeline Step 7.5 for Phase 5) │
│ NO → Go to step-11-complete.md (standalone summary) │
└──────────────────────────────────────────────────────────────────────────┘
```

##

**Problem:** Queue exhausted (Section 6) does NOT mean all hypotheses are done.
New hypotheses may become READY during processing (e.g., H-M1 after H-E1 validated).

**Solution:** Section 7-8 uses explicit IF-ELSE structure to ensure:
- `all_processed = FALSE` → Go to step-03-get-ready.md (refresh queue)
- `all_processed = TRUE` → Proceed to completion (ELSE block)

##

| execution_source | Path | Description |
|------------------|------|-------------|
| `full-pipeline` | EXIT → Step 7.5 | Returns control for Phase 5 invocation |
| `standalone` (default) | step-11-complete.md | Summary only (run Phase 5 separately) |

##

**Previous Issue:** Python pseudocode assumed dictionary structure with `.items()` calls.
This caused failures when verification_state.yaml used array structure for sub_hypotheses.

**Fix:** Natural language instructions describe WHAT to check, not HOW to access data.
LLM interprets actual YAML structure correctly.

##

**Previous Issue:** LLM might skip Section 8A queue refresh and proceed directly to completion,
causing dependent hypotheses (e.g., H-M1 after H-E1) to never be processed.

**Fix:** Added explicit critical box in Section 8A with:
- Concrete H-E1 → H-M1 scenario walkthrough
- "If you skip this step: H-M1 will never be processed!" warning
- MANDATORY instruction to return to step-03-get-ready.md

---

## STEP COMPLETION

Loop continuation is determined by the conditions above. This step either:
1. Returns to step-04 for next hypothesis in current queue (Section 6)
2. Returns to step-03 to refresh queue with new READY hypotheses (Section 7-8, CASE A)
3. **[full-pipeline mode]** Exits to return control for Step 7.5 Phase 5 invocation (Section 7-8, CASE B)
4. **[standalone mode]** Proceeds to step-11 for completion summary (Section 7-8, CASE B)
5. Exits (SINGLE mode or user request, Sections 2-4)

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Execution mode re-checked from verification_state.yaml
- Correct mode-specific behavior (AUTO/STEP/SINGLE)
- Loop continuation handled properly (step-04 or step-03)
- Queue refresh triggered when new READY hypotheses exist
- Completion summary triggered ONLY when all_processed is TRUE

### ❌ FAILURE
- Forgetting to re-check execution mode
- Asking user in AUTO mode
- Not continuing loop when hypotheses remain (premature Phase 5)
- Skipping Section 7-8 check when queue is exhausted
- **Proceeding to completion when unprocessed hypotheses exist**
