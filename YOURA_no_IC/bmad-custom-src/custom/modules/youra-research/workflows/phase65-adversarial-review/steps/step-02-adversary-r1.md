---
name: 'step-02-adversary-r1'
description: 'Spawn Adversary Agent for Round 1 review focusing on structural issues with ground truth verification'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-02-adversary-r1.md'
nextStepFile: '{workflow_path}/steps/step-03-revision-r1.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 2: Adversary Agent - Round 1 (with Ground Truth)

> **Execution Mode**: Task Agent (isolated context)
> **Agent**: `adversary-agent`
> **Round**: R1 - Structural Issues
> **Focus**: Logical conflicts, methodology contradictions, novelty overclaims
> **Ground Truth**: Provided from Step 1 extraction

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Task Agent Spawn Instructions

Spawn the Adversary Agent with ground truth access:

```yaml
spawn_task_agent:
  type: "general-purpose"
  agent_file: "{workflow_path}/agents/adversary-agent-v2.md"

  parameters:
    # Paper to review
    paper_file: "{paper_folder}/06_paper.md"
    sections_folder: "{paper_folder}/sections/"

    # CRITICAL: Ground truth files
    ground_truth_file: "{paper_folder}/065_ground_truth.yaml"
    verification_state_file: "{research_folder}/verification_state.yaml"

    # Round configuration
    round: "R1"
    focus_areas:
      - "logical_conflicts"
      - "methodology_contradictions"
      - "novelty_overclaims"
      - "definition_inconsistency"

    # Output
    output_file: "{review_folder}/065_review_r1.md"
    previous_review: null # First round

  prompt: |
    You are the Adversary Agent conducting Round 1 review with ground truth verification.

    ## CRITICAL: Read Ground Truth First

    Before reading the paper, read these files:

    1. **Ground Truth**: `{ground_truth_file}`
       - Contains actual values from Phase 4/5 experiments
       - Extracted from verification_state.yaml and result files
       - Pre-computed discrepancies already identified

    2. **Verification State**: `{verification_state_file}`
       - Full pipeline state with all hypothesis results
       - Baseline comparison results from Phase 5
       - Statistics on sub-hypotheses

    ## Round 1 Focus: Structural Issues

    With ground truth in mind, find:

    1. **Logical Conflicts**
       - Claim in Section A contradicts Section B
       - Example: "conflict samples learn fast" vs "conflict samples have high loss"

    2. **Methodology Contradictions**
       - Paper description ≠ actual implementation
       - Check: `ground_truth.methodology_facts.training_stages`
       - Example: Paper says "single-run" but ground truth shows "2-stage"

    3. **Novelty Overclaims**
       - Claims novelty that prior work already has
       - Example: "first to use learning speed for detection" when papers exist

    4. **Definition Inconsistency**
       - Same term means different things across sections
       - Check consistency with verification_state.yaml terminology

    ## Cross-Reference Checklist

    - [ ] Abstract claims match Results section numbers?
    - [ ] Methodology (Section 3) matches Experiments (Section 4)?
    - [ ] Paper's "observation epochs" matches ground_truth?
    - [ ] Paper's "intervention epochs" matches ground_truth?
    - [ ] Paper's training description matches ground_truth.training_stages?

    ## Output

    Write review to `{output_file}` with:
    - Ground Truth Summary table
    - FATAL/MAJOR/MINOR issues with evidence
    - Ground Truth Verification Log
    - Serena MCP Verification Log (if used)

    ## Return Summary

    Return with:
    - Issue counts (fatal, major, minor)
    - Ground truth discrepancies count
    - Key conflicts found
    - Recommendation
```

---

## Expected Output

The Task Agent will create `065_review_r1.md` containing:

1. **Ground Truth Summary** - Actual values from pipeline
2. **Executive Summary** - Issue counts and recommendation
3. **FATAL Issues** - With ground truth evidence
4. **MAJOR Issues** - With cross-reference evidence
5. **MINOR Issues** - Style/clarity issues
6. **Ground Truth Verification Log** - What was checked
7. **Summary for Revision Agent** - Prioritized fix list

---

## After Task Agent Returns

### Update Checkpoint

```yaml
action: "Update checkpoint with R1 results"
updates:
  updated_at: "{ISO8601}"
  issues_by_round.R1:
    fatal: "{from agent return}"
    major: "{from agent return}"
    minor: "{from agent return}"
    ground_truth_discrepancies: "{from agent return}"
  serena_searches_performed: "{from agent return}"
```

### Gate Decision (INTERACTIVE mode only)

If execution_mode == "INTERACTIVE":
- Present R1 findings with ground truth discrepancies
- User decides: PROCEED / SKIP_REVISION / ABORT

If execution_mode == "UNATTENDED":
- Auto-proceed to Revision Agent

---

## Next Step

Proceed to **Step 3: Revision Round 1** (`step-03-revision-r1.md`)

The Revision Agent will receive:
- Original paper
- R1 review with ground truth evidence
- Ground truth file for reference
