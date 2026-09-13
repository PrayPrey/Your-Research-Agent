---
name: 'step-03-revision-r1'
description: 'Spawn Revision Agent to address Round 1 structural issues from Adversary review'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-03-revision-r1.md'
nextStepFile: '{workflow_path}/steps/step-04-convergence.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 3: Revision Agent - Round 1

> **Execution Mode**: Task Agent (isolated context)
> **Agent**: `revision-agent`
> **Round**: R1 - Structural Issues Fix
> **Input**: Original paper + Adversary R1 review

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
    paper_file: "{paper_folder}/06_paper.md"
    review_file: "{review_folder}/065_review_r1.md"
    round: "R1"
    output_file: "{paper_folder}/06_paper_r1.md"
    changelog_file: "{review_folder}/065_changelog.md"

  prompt: |
    You are the Revision Agent responding to Round 1 review.

    ## Your Mission

    1. Read the original paper at `{paper_file}`
    2. Read the Adversary review at `{review_file}`
    3. Address ALL issues (especially FATAL ones)
    4. Write the revised paper to `{output_file}`
    5. Document all changes in `{changelog_file}`

    ## Priority Order

    1. **FATAL issues** - MUST fix all of these
    2. **MAJOR issues** - Fix as many as possible
    3. **MINOR issues** - Fix if reasonable

    ## Revision Strategies

    For **Logical Conflicts**:
    - Identify which claim is correct based on the actual research
    - Unify terminology and descriptions across sections
    - Add clarifying language if both can be true in different contexts

    For **Methodology Contradictions**:
    - Align Method section with actual Experiments
    - If implementation differs from description, update description
    - Be precise about what "single-run" or "two-stage" means

    For **Novelty Overclaims**:
    - Reframe from "first to" to "we extend/integrate"
    - Acknowledge prior work explicitly
    - Clarify what is genuinely new in this work

    ## Important Rules

    - Do NOT change the research findings
    - Do NOT delete important content (revise instead)
    - Document EVERY change in the changelog
    - Preserve the paper's voice and style

    ## Output

    1. Complete revised paper at `{output_file}`
    2. Changelog entry at `{changelog_file}`

    ## Return

    Return a summary with:
    - issues_addressed (accepted, partial, rejected counts)
    - sections_modified list
    - word_count_delta
    - remaining_concerns (if any issues couldn't be resolved)
```

---

## Expected Output

The Task Agent will create:

1. `06_paper_r1.md` - Complete revised paper
2. `065_changelog.md` - Detailed change log

---

## After Task Agent Returns

### Update Checkpoint

```yaml
action: "Update checkpoint with R1 revision results"
updates:
  updated_at: "{ISO8601}"
  latest_paper_version: "{paper_folder}/06_paper_r1.md"
  issues_by_round.R1.resolved: "{from agent return}"
  rounds_completed: ["R1"]
```

### Prepare for Convergence Check

```yaml
action: "Prepare data for convergence check"
data:
  round: "R1"
  issues_found:
    fatal: "{R1 fatal count}"
    major: "{R1 major count}"
    minor: "{R1 minor count}"
  issues_resolved: "{from revision agent}"
  remaining_fatal: "{fatal - resolved_fatal}"
  remaining_major: "{major - resolved_major}"
```

---

## Next Step

Proceed to **Step 4: Convergence Check** (`step-04-convergence.md`)

```yaml
next_step: "step-04-convergence.md"
execution_mode: "main_session"
input:
  checkpoint: "{review_folder}/065_review_checkpoint.yaml"
  review_r1: "{review_folder}/065_review_r1.md"
  paper_r1: "{paper_folder}/06_paper_r1.md"
```
