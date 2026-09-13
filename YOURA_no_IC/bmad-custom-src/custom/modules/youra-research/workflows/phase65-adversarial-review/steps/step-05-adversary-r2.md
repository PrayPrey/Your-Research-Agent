---
name: 'step-05-adversary-r2'
description: 'Spawn Adversary Agent for Round 2 numerical verification using Serena MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-05-adversary-r2.md'
nextStepFile: '{workflow_path}/steps/step-06-revision-r2.md'
workflowFile: '{workflow_path}/workflow.md'
---

# Step 5: Adversary Agent - Round 2 (Numerical Verification with Serena)

> **Execution Mode**: Task Agent (isolated context)
> **Agent**: `adversary-agent`
> **Round**: R2 - Numerical Issues
> **Focus**: Mathematical validity, baseline fairness, signal-performance gaps
> **MCP Required**: Serena (MANDATORY), Semantic Scholar (recommended)

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Prerequisites

This step executes only if:
- Step 4 (Convergence Check) determined: CONTINUE
- R1 completed but issues remain

---

## CRITICAL: Serena MCP Verification

Round 2 is the **numerical verification round**. The Adversary Agent MUST use Serena MCP to:

1. **Find actual result files** in the hypothesis folder
2. **Search for specific values** in validation reports
3. **Verify code implementation** matches paper description
4. **Cross-check baseline results** from Phase 5

---

## Task Agent Spawn Instructions

```yaml
spawn_task_agent:
  type: "general-purpose"
  agent_file: "{workflow_path}/agents/adversary-agent-v2.md"

  parameters:
    # Paper to review (R1 revised version)
    paper_file: "{paper_folder}/06_paper_r1.md"
    sections_folder: "{paper_folder}/sections/"

    # CRITICAL: Ground truth and verification files
    ground_truth_file: "{paper_folder}/065_ground_truth.yaml"
    verification_state_file: "{research_folder}/verification_state.yaml"

    # Additional files for numerical verification
    phase4_validation_files: "{from Step 1 discovery}"
    phase5_baseline_files: "{from Step 1 discovery}"
    hypothesis_folder: "{research_folder}/{hypothesis_id_lower}"

    # Round configuration
    round: "R2"
    focus_areas:
      - "mathematical_validity"
      - "baseline_fairness"
      - "signal_performance_gap"
      - "metric_consistency"

    # Output
    output_file: "{review_folder}/065_review_r2.md"
    previous_review: "{review_folder}/065_review_r1.md"

  prompt: |
    You are the Adversary Agent conducting Round 2 NUMERICAL review.

    ## CRITICAL: This Round Requires Serena MCP

    You MUST use Serena MCP to verify every numerical claim. Do NOT rely on
    ground truth file alone - actively search actual files.

    ## Step 1: Load Ground Truth

    Read `{ground_truth_file}` first to know expected values.

    ## Step 2: Serena MCP Verification

    For EACH numerical claim in the paper, perform verification:

    ### Performance Claims

    ```
    Paper claims: "78.19% worst-group accuracy"

    1. Search actual validation file:
       mcp__serena__search_for_pattern:
         pattern: "worst.group.accuracy|WGA|\\d+\\.\\d+%"
         path: "{hypothesis_folder}/04_validation.md"

    2. Compare result to paper claim

    3. Log in Verification Table
    ```

    ### Baseline Claims

    ```
    Paper claims: "GroupDRO achieves 66.56%"

    1. Search Phase 5 results:
       mcp__serena__search_for_pattern:
         pattern: "GroupDRO|DRO.*\\d+\\.\\d+%"
         path: "{hypothesis_folder}/baseline_comparison/"

    2. Also check original paper via Semantic Scholar:
       - What does Sagawa 2020 report for GroupDRO?
       - Is our experimental value fair to compare?

    3. Log discrepancy if found
    ```

    ### Detection Metrics

    ```
    Paper claims: "80.25% sensitivity with 16.83% FPR"

    1. Search detection results:
       mcp__serena__search_for_pattern:
         pattern: "sensitivity|TPR|recall"
         path: "{hypothesis_folder}/"

       mcp__serena__search_for_pattern:
         pattern: "FPR|false.positive"
         path: "{hypothesis_folder}/"

    2. Compare with paper claims
    ```

    ### Methodology Numbers

    ```
    Paper claims: "top 20% fastest learners", "upweight factor 20"

    1. Search actual code:
       mcp__serena__search_for_pattern:
         pattern: "top.*percent|top_k|TOP"
         path: "{hypothesis_folder}/code/"

       mcp__serena__search_for_pattern:
         pattern: "upweight|weight.*factor|lambda"
         path: "{hypothesis_folder}/code/"

    2. Verify paper matches implementation
    ```

    ## Step 3: Mathematical Validity Checks

    ### Check 1: TOP-K vs Conflict Prevalence

    ```
    Paper says: "5% conflict in dataset"
    Paper says: "select top 20% fastest learners"

    Calculate: If only 5% are conflicts, selecting 20% means:
    - Best case precision = 5% / 20% = 25%
    - Paper claims higher precision?
    - Flag if mathematically impossible
    ```

    ### Check 2: CV Ratio vs Detection Performance

    ```
    Paper claims: "CV ratio 36.59x"
    Paper claims: "80% sensitivity, 17% FPR"

    If signal is 36x stronger than baseline, is 80% detection reasonable?
    - Very strong signal should give near-perfect detection
    - If not, explain why (e.g., overlapping distributions)
    ```

    ### Check 3: Stage Consistency

    ```
    Paper says: "single training run" in Section 3
    Paper says: "Stage 2 retrains from scratch" in Section 4

    Use Serena to verify:
    mcp__serena__search_for_pattern:
      pattern: "stage|retrain|from_scratch|scratch"
      path: "{hypothesis_folder}/code/"

    Determine: Is it actually single-run or 2-stage?
    ```

    ## Output Format

    Your review MUST include:

    1. **Serena MCP Verification Log**
       - Every search performed
       - Actual results found
       - Comparison to paper claims

    2. **Ground Truth Verification Table**
       | Claim | Paper | Ground Truth | Serena Verified | Match |
       |-------|-------|--------------|-----------------|-------|

    3. **Mathematical Validity Analysis**
       - Calculations showing if numbers make sense
       - Flag impossible claims

    4. **Baseline Fairness Assessment**
       - Our results vs original paper results
       - Is comparison fair?

    ## Return Summary

    ```yaml
    agent: "adversary"
    round: "R2"
    status: "COMPLETED"
    serena_searches_performed: {count}
    numerical_discrepancies_found: {count}
    mathematical_impossibilities: {count}
    baseline_fairness_issues: {count}
    summary:
      fatal_count: {N}
      major_count: {N}
      minor_count: {N}
    ```
```

---

## Expected Output

`065_review_r2.md` will contain:

1. **Ground Truth Summary** - Pre-loaded values
2. **Serena MCP Verification Log** - All searches performed
3. **Ground Truth Verification Table** - Claim vs actual
4. **Mathematical Validity Analysis** - Calculations
5. **FATAL Issues** - With Serena evidence
6. **MAJOR Issues** - With cross-reference evidence
7. **Baseline Fairness Assessment** - Comparison context

---

## Serena MCP Required Searches

| Search Type | Pattern | Path | Purpose |
|-------------|---------|------|---------|
| Performance | `WGA\|accuracy.*\d+` | 04_validation.md | Verify accuracy claims |
| Detection | `sensitivity\|precision\|FPR` | 04_validation.md | Verify detection claims |
| Baseline | `ERM\|GroupDRO\|JTT\|DFR` | 05_baseline_comparison.md | Verify baseline claims |
| Epochs | `epoch.*\d+\|observation\|intervention` | code/ | Verify methodology |
| Stages | `stage\|retrain\|scratch` | code/ | Verify training process |
| Parameters | `upweight\|top.*percent\|lambda` | code/ | Verify hyperparameters |

---

## After Task Agent Returns

### Update Checkpoint

```yaml
action: "Update checkpoint with R2 results"
updates:
  updated_at: "{ISO8601}"
  current_round: 2
  issues_by_round.R2:
    fatal: "{from agent return}"
    major: "{from agent return}"
    minor: "{from agent return}"
    serena_searches: "{from agent return}"
    numerical_discrepancies: "{from agent return}"
```

---

## Next Step

Proceed to **Step 6: Revision Round 2** (`step-06-revision-r2.md`)

The Revision Agent will receive:
- R1-revised paper
- R2 review with Serena verification evidence
- Ground truth file
- Specific numerical corrections needed
