---
name: 'step-06-revision-r2'
description: 'Spawn Revision Agent to address Round 2 numerical issues and perform second convergence check'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-06-revision-r2.md'
nextStepFile: '{workflow_path}/steps/step-07-finalize.md' # Or step-05-adversary-r2.md for R3
workflowFile: '{workflow_path}/workflow.md'
---

# Step 6: Revision Agent - Round 2

> **Execution Mode**: Task Agent (isolated context)
> **Agent**: `revision-agent`
> **Round**: R2 - Numerical Issues Fix
> **Input**: R1 revised paper + Adversary R2 review

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Task Agent Spawn Instructions

Spawn the Revision Agent with the following parameters:

```yaml
spawn_task_agent:
  type: "general-purpose"
  agent_file: "{workflow_path}/agents/revision-agent.md"

  parameters:
    paper_file: "{paper_folder}/06_paper_r1.md" # Start from R1 version
    review_file: "{review_folder}/065_review_r2.md"
    round: "R2"
    output_file: "{paper_folder}/06_paper_r2.md"
    changelog_file: "{review_folder}/065_changelog.md" # Append to existing

  prompt: |
    You are the Revision Agent responding to Round 2 review.

    ## Your Mission

    1. Read the R1-revised paper at `{paper_file}`
    2. Read the Adversary R2 review at `{review_file}`
    3. Address ALL numerical issues
    4. Write the R2-revised paper to `{output_file}`
    5. APPEND changes to `{changelog_file}`

    ## Numerical Issue Fix Strategies

    ### Mathematical Validity Issues

    If numbers don't add up:
    - Correct the calculation
    - OR explain why apparent inconsistency is valid
    - Add explicit calculations if helpful

    Example fix:
    ```
    # Before
    "We select top 20% fastest learners from 5% conflict samples"

    # After
    "We select the top 20% fastest learners as candidates. With 5% true
    conflict samples, this yields approximately 25% precision—a deliberate
    trade-off favoring high recall (80%) for our reweighting intervention."
    ```

    ### Baseline Fairness Issues

    If baselines appear unfair:
    - Add context explaining experimental choices
    - Acknowledge literature-reported numbers
    - Clarify what comparison measures

    Example fix:
    ```
    # Before
    "GroupDRO achieves 66.56% WGA"

    # After
    "Under SubpopBench default hyperparameters, GroupDRO achieves 66.56% WGA.
    We note that with dataset-specific tuning, GroupDRO reaches 89% [Sagawa 2020].
    Our comparison isolates mitigation strategy effectiveness under controlled,
    untuned conditions."
    ```

    ### Signal-Performance Gap Issues

    If strong signal doesn't yield strong detection:
    - Explain the relationship more carefully
    - Add nuance about what the signal measures
    - Acknowledge if gap is a limitation

    Example fix:
    ```
    # Before
    "CV ratio of 36.59x indicates strong heterogeneity"
    "Detection achieves 80% sensitivity with 17% FPR"

    # After
    "The CV ratio of 36.59x indicates population-level heterogeneity in
    learning speeds. While this macro-level signal is strong, individual
    sample classification remains challenging due to overlapping
    distributions, yielding 80% sensitivity at 17% FPR."
    ```

    ## Important

    - Numerical changes MUST be accurate
    - Don't fabricate numbers to fix inconsistencies
    - If a number is genuinely wrong, acknowledge uncertainty
    - Preserve all R1 fixes while adding R2 fixes

    ## Return

    Return summary with issues addressed and sections modified.
```

---

## Expected Output

The Task Agent will create:

1. `06_paper_r2.md` - R2 revised paper (includes R1 + R2 fixes)
2. `065_changelog.md` - Appended with R2 changes

---

## After Task Agent Returns

### Update Checkpoint

```yaml
action: "Update checkpoint with R2 revision results"
updates:
  updated_at: "{ISO8601}"
  latest_paper_version: "{paper_folder}/06_paper_r2.md"
  issues_by_round.R2.resolved: "{from agent return}"
  rounds_completed: ["R1", "R2"]
```

### Second Convergence Check

After R2, perform another convergence check:

```yaml
action: "Evaluate convergence after R2"

if:
  condition: "remaining_fatal == 0 AND remaining_major == 0 AND persuasiveness_passed == true"
  next_step: "step-07-finalize.md"

elif:
  condition: "current_round < max_rounds"
  next_step: "step-05-adversary-r2.md" # With R3 parameters
  note: "Rare - usually converges after R2"

else:
  status: "MANUAL_REQUIRED"
  reason: "R2 complete but issues remain"
```

---

## Next Step

Based on convergence:

| Decision | Next Step |
|----------|-----------|
| CONVERGED | `step-07-finalize.md` |
| CONTINUE | `step-05-adversary-r2.md` (R3 params) |
| STOP | Manual intervention required |

Most workflows converge after R2.
