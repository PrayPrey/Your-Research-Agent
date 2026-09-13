---
name: 'step-04-convergence'
description: 'Evaluate convergence criteria to determine if another round is needed or finalization can proceed'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-04-convergence.md'
nextStepFile: '{workflow_path}/steps/step-05-adversary-r2.md' # Or step-07-finalize.md if converged
workflowFile: '{workflow_path}/workflow.md'
---

# Step 4: Convergence Check

> **Execution Mode**: Main Session
> **Purpose**: Evaluate if another round is needed or if review can finalize

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Convergence Criteria

### Automatic Convergence (Skip to Finalize)

```yaml
converge_conditions:
  ALL_OF:
    - fatal_issues_remaining == 0
    - major_issues_remaining == 0
    - persuasiveness_passed == true
    - current_round >= 2 # At least R1 and R2 completed
```

### Continue to Next Round

```yaml
continue_conditions:
  ANY_OF:
    - fatal_issues_remaining > 0
    - major_issues_remaining > 0
    - persuasiveness_passed == false
  AND:
    - current_round < max_rounds # Haven't hit limit
```

### Force Stop (Manual Intervention)

```yaml
force_stop_conditions:
  ANY_OF:
    - current_round >= max_rounds AND fatal_issues_remaining > 0
    - same_issue_repeated >= 2 # Same issue found twice
```

---

## Execution Sequence

### 4.1 Load Current State

```yaml
action: "Read checkpoint and latest review"
files:
  - checkpoint: "{review_folder}/065_review_checkpoint.yaml"
  - latest_review: "{review_folder}/065_review_r{current_round}.md"
```

### 4.2 Calculate Remaining Issues

```yaml
action: "Calculate remaining issues after revision"
calculation:
  remaining_fatal: issues_found.fatal - issues_resolved.fatal
  remaining_major: issues_found.major - issues_resolved.major
  remaining_minor: issues_found.minor - issues_resolved.minor
```

### 4.3 Evaluate Convergence

```yaml
action: "Evaluate convergence criteria"

# Case 1: Converged
if:
  condition: "remaining_fatal == 0 AND remaining_major == 0 AND persuasiveness_passed == true"
  action: "Set convergence.met = true"
  next_step: "step-07-finalize.md"
  reason: "All critical issues resolved and paper is persuasive"

# Case 2: Continue to R2
elif:
  condition: "current_round == 1 AND (remaining_fatal > 0 OR remaining_major > 0 OR NOT persuasiveness_passed)"
  action: "Proceed to Round 2"
  next_step: "step-05-adversary-r2.md"
  reason: "R1 complete but issues remain"

# Case 3: Continue to R3
elif:
  condition: "current_round == 2 AND (remaining_fatal > 0 OR remaining_major > 0 OR NOT persuasiveness_passed)"
  action: "Proceed to Round 3"
  next_step: "step-05-adversary-r2.md" # Reuse R2 step with R3 params
  reason: "R2 complete but issues remain"

# Case 4: Force Stop
elif:
  condition: "current_round >= max_rounds"
  action: "Stop for manual intervention"
  status: "MANUAL_REQUIRED"
  reason: "Max rounds reached with unresolved issues"
```

### 4.4 Check for Repeated Issues

```yaml
action: "Check if same issues appearing repeatedly"

if:
  condition: "issue appeared in R1 AND still appears in R2"
  action: "Flag as potential unfixable issue"
  recommendation: "May need human judgment"
```

### 4.5 Update Checkpoint

```yaml
action: "Update checkpoint with convergence decision"
updates:
  updated_at: "{ISO8601}"
  convergence:
    met: "{true/false}"
    reason: "{reason for decision}"
    evaluated_at: "{ISO8601}"
  next_action: "{next_step or MANUAL_REQUIRED}"
```

---

## Decision Tree Visualization

```
                    ┌─────────────────┐
                    │ After Round N │
                    │ Revision │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ FATAL = 0? │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ │
         YES ▼                        NO ▼
    ┌─────────────────┐ ┌─────────────────┐
    │ MAJOR=0 & │
    │ PERSUASIVE? │           │ Round < Max? │
    └────────┬────────┘ └────────┬────────┘
             │ │
    ┌────────┴────────┐ ┌────────┴────────┐
    │ │           │ │
YES ▼ NO ▼      YES ▼            NO ▼
┌───────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│CONVERGE│ │ CONTINUE │  │ CONTINUE │   │ STOP │
│Finalize│ │ Next Round│ │ Next Round│ │ Manual │
└───────┘ └───────────┘ └───────────┘ └───────────┘
```

---

## User Notification (INTERACTIVE mode)

If execution_mode == "INTERACTIVE":

```yaml
action: "Present convergence status to user"
display:
  current_round: "{N}"
  issues_remaining:
    fatal: "{N}"
    major: "{N}"
    minor: "{N}"
  recommendation: "{CONVERGE / CONTINUE / STOP}"

options:
  - "ACCEPT": Follow recommendation
  - "OVERRIDE_CONVERGE": Force finalize even with issues
  - "OVERRIDE_CONTINUE": Force another round
  - "ABORT": Stop for manual work
```

---

## Output

| Update | Value |
|--------|-------|
| `checkpoint.convergence.met` | true/false |
| `checkpoint.convergence.reason` | Explanation |
| `checkpoint.next_action` | Next step or MANUAL_REQUIRED |

---

## Next Step

Based on convergence decision:

| Decision | Next Step |
|----------|-----------|
| CONVERGED | `step-07-finalize.md` |
| CONTINUE (to R2) | `step-05-adversary-r2.md` |
| CONTINUE (to R3) | `step-05-adversary-r2.md` (with R3 params) |
| STOP | End workflow, require manual intervention |
