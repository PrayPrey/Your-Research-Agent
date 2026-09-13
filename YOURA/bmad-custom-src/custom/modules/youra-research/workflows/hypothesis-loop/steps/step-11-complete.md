---
name: 'step-11-complete'
description: 'Completion summary and next steps'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop'

# File References
thisStepFile: '{workflow_path}/steps/step-11-complete.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 11: Completion Summary

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## STEP GOAL

Display the sub-hypothesis loop completion summary with statistics and next steps.

<critical>
**PHASE 5 EXECUTION PRECONDITION**

Phase 5 can ONLY be executed when **ALL sub-hypotheses have completed Phase 4**.

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 5 Precondition: │
│ │
│ ✅ ALL sub-hypotheses must be in FINAL states: │
│ - VALIDATED (Phase 4 PASS) │
│ - COMPLETED (MODIFIED → new version handles validation) │
│ - FAILED (Phase 4 FAIL) │
│ - BLOCKED / CASCADE_FAILED │
│ - SUPERSEDED / CASCADE_SUPERSEDED │
│ │
│ ❌ If ANY sub-hypothesis is still in: │
│ - READY, IN_PROGRESS, NOT_STARTED, PENDING │
│ → DO NOT proceed to Phase 5 │
│ → Continue hypothesis-loop until all complete │
└─────────────────────────────────────────────────────────────────┘
```

Phase 5 is invoked separately:
- full-pipeline: Step 7.5 invokes Phase 5 automatically
- standalone: User should run `/phase5-baseline-repo-comparison` separately
</critical>

---

## EXECUTION SEQUENCE

### 1. Calculate Statistics

**Instructions:**

1. **Initialize counters** to zero:
   - `validated_count`, `failed_count`, `pending_count`, `blocked_count`, `superseded_count`

2. **Scan ALL hypotheses in sub_hypotheses** and categorize by status:

   | Status | Counter | Description |
   |--------|---------|-------------|
   | `VALIDATED` | validated_count | Phase 4 PASS |
   | `COMPLETED` | validated_count | MODIFIED (gate satisfied) |
   | `FAILED` | failed_count | Phase 4 FAIL |
   | `CASCADE_FAILED` | failed_count | Blocked by prerequisite failure |
   | `SUPERSEDED` | superseded_count | Replaced by new version |
   | `CASCADE_SUPERSEDED` | superseded_count | Cascaded from superseded parent |
   | `READY` | pending_count | Waiting in queue |
   | `IN_PROGRESS` | pending_count | Currently processing |
   | `NOT_STARTED` | pending_count | Prerequisites not satisfied |
   | `PENDING` | pending_count | Alias for NOT_STARTED |
   | `BLOCKED` | blocked_count | Explicitly blocked |

3. **Get execution_source** from `workflow.execution_source` (default: "standalone")

### 2. Display Summary

```
═══════════════════════════════════════════════════════════════
                    HYPOTHESIS LOOP COMPLETE
                    (Phase 2C → 3 → 4) × N
═══════════════════════════════════════════════════════════════

📊 **Sub-Hypothesis Results:**
   ✅ Validated: {{sub_stats.validated}}
   ❌ Failed: {{sub_stats.failed}}
   ⏳ Pending: {{sub_stats.pending}}
   🚫 Blocked: {{sub_stats.blocked}}
   🔄 Superseded: {{sub_stats.superseded}}

📋 **Phase 5 Status:** Not yet executed (separate step)

═══════════════════════════════════════════════════════════════
```

### 3. Display Next Steps

**Instructions:**

---

#### 3A. If execution_source is "full-pipeline"

> Note: This branch is typically not reached because full-pipeline mode exits in step-09 before reaching step-11.

Display:
```
📤 **Returning to full-pipeline-unattended...**

Phase 5 will be invoked automatically by Step 7.5.
```

---

#### 3B. If execution_source is "standalone" (default)

**First, determine if all hypotheses are validated:**
- `all_validated = TRUE` if: `failed_count == 0` AND `pending_count == 0`

---

**If all_validated is TRUE:**

Display:
```
✅ **All Sub-Hypotheses Validated!**

Phase 2C → 3 → 4 completed successfully for ALL sub-hypotheses.

**Phase 5 Precondition: ✅ SATISFIED**
- All sub-hypotheses in final states
- Ready for baseline comparison

**Next Steps:**
1. Execute `/phase5-baseline-repo-comparison` to compare against baseline
2. After Phase 5 PASS: Execute `/phase6-paper-writing` for paper generation
3. Review with `/phase65-adversarial-review`

**Key Artifacts:**
- verification_state.yaml: Complete research state
- {hypothesis_id}/04_validation.md: Per-hypothesis validation results
```

---

**If failed_count > 0:**

Display:
```
⚠️ **Some Sub-Hypotheses Failed**

Failed: {failed_count}

**Phase 5 Precondition:** Check if MUST_WORK hypotheses passed

**Next Steps:**
1. Run `/hypothesis-status` to see failed hypotheses
2. Check 04_validation.md for failure details
3. Consider running Phase 5 if MUST_WORK hypotheses passed
   - `/phase5-baseline-repo-comparison`

**Note:** SHOULD_WORK failures don't block Phase 5.
```

---

**Otherwise (pending_count > 0):**

Display:
```
⏳ **Some Sub-Hypotheses Still Pending**

Pending: {pending_count}

**Phase 5 Precondition: ❌ NOT SATISFIED**
- Some sub-hypotheses have not completed Phase 4
- DO NOT proceed to Phase 5 yet

**Next Steps:**
1. Run `/hypothesis-status` to check current state
2. Resume with `/hypothesis-loop` to continue processing
3. Check for blocking dependencies
```

### 4. Final State Update

**Instructions:**

1. **Update verification_state.yaml workflow section:**
   - Set `workflow.current_phase` to `"Hypothesis Loop Complete"`
   - Set `workflow.sub_hypotheses_complete` to `true`
   - Set `workflow.hypothesis_loop_completed_at` to current timestamp

2. **Save verification_state.yaml**

> **Note:** hypothesis-loop only marks loop complete, not full workflow.
> Workflow `COMPLETED` status is set after Phase 5 passes.

### 5. Exit

```
═══════════════════════════════════════════════════════════════
               HYPOTHESIS LOOP WORKFLOW FINISHED
                 (Next: Phase 5 → 6 → 6.5 → 6.5.1)
═══════════════════════════════════════════════════════════════
```

GOTO EXIT

---

## SUCCESS/FAILURE METRICS

### ✅ SUCCESS
- Statistics calculated correctly
- Appropriate next steps displayed based on execution source
- State updated (sub_hypotheses_complete = True)
- Clean exit with Phase 5 guidance

### ❌ FAILURE
- Incorrect statistics
- Missing next steps guidance
- Not saving state update
- Not guiding user to Phase 5 (standalone mode)
