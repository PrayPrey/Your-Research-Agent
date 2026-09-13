---
name: 'step-10-report'
description: 'Generate final comparison report with full experiment progress and results'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# File References
thisStepFile: '{workflow_path}/steps/step-10-report.md'
prevStepFile: '{workflow_path}/steps/step-09-experiment.md'
nextStepFile: '{workflow_path}/steps/step-10a-gate-evaluation.md'
workflowFile: '{workflow_path}/workflow.md'
reportTemplate: '{workflow_path}/templates/05_baseline_report_template.md'

# Input Files
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
comparison_data: '{baseline_folder}/experiments/comparison_data.csv'
results_summary: '{baseline_folder}/results_summary.md'
verification_state: '{research_folder}/verification_state.yaml'

# Output Files
final_report: '{baseline_folder}/05_baseline_comparison.md'

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 10: Generate Comparison Report (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Pattern:** Report generation step (gate evaluation in step-10a)

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- Focus ONLY on generating final comparison report from real data
- FORBIDDEN to invent statistics or fabricate results
- MUST include hypothesis journey context from verification_state.yaml

## EXECUTION PROTOCOLS:

- Load all experiment data from previous steps
- Extract hypothesis journey from verification_state.yaml
- Generate comprehensive 05_baseline_comparison.md report

## CONTEXT BOUNDARIES:

- Available context: comparison_data.csv, results_summary.md, checkpoint, verification_state.yaml
- Focus: Report generation
- Limits: Do not re-run experiments or modify results
- Dependencies: Step 9 must be completed with experiment results

---

## FAIR COMPARISON PRINCIPLE (CRITICAL!)

<critical>
**REPORT MUST CLEARLY STATE THE FAIR COMPARISON CONTEXT:**

Mode B Fair Comparison: Each baseline uses THEIR OWN environment.

For EACH baseline, both methods used IDENTICAL conditions:
- **SAME model architecture** (BASELINE's model)
- **SAME dataset** (BASELINE's dataset)
- **SAME hyperparameters** (BASELINE's config)

The ONLY difference: **Algorithm/Methodology**
- Baseline: Baseline repository's original algorithm
- Ours: Our algorithm injected into baseline's training loop

**This must be stated in the Executive Summary and Section 1 of the report!**
</critical>

---

## STEP GOAL

Create final comparison report documenting the full experiment process and results.

---

## 10.1 Load Context

Load data from previous steps:

| Source | Information |
|--------|-------------|
| `comparison_data.csv` | Merged experiment results |
| `results_summary.md` | Summary statistics |
| `05_baseline_checkpoint.yaml` | Baseline metadata (includes per-baseline configs) |
| `verification_state.yaml` | Hypothesis journey |
| `figures/` | Comparison figures (learning curves, metric bar chart) |

---

## 10.2 Gather Hypothesis Journey

From `verification_state.yaml`, extract the hypothesis journey:

| Field | Description |
|-------|-------------|
| version_history | All versions and changes |
| reflections | Insights from each iteration |
| lessons_learned | Key learnings |
| modifications | What was changed and why |
| final_result | PASS/PARTIAL/FAIL |

---

## 10.3 Prepare Comparison Data

From `comparison_data.csv`, organize:

### Per Baseline Comparison

For each baseline repository:

| Metric | Baseline Original | Ours Injected | Difference |
|--------|-------------------|---------------|------------|
| Primary Metric | {val} | {val} | {Δ} |
| Secondary Metric | {val} | {val} | {Δ} |

### Overall Comparison

| Baseline | Model | Dataset | Winner | Improvement |
|----------|-------|---------|--------|-------------|
| {baseline_1} | {model} | {dataset} | {ours/baseline} | {+X.X%} |
| {baseline_2} | {model} | {dataset} | {ours/baseline} | {+X.X%} |
| {baseline_3} | {model} | {dataset} | {ours/baseline} | {+X.X%} |

**Win Rate:** {X}/{baselines_count} baselines

---

## 10.4 Generate Final Report

<action>Load report template and populate with data</action>

**Template Location:** `{workflow_path}/templates/05_baseline_report_template.md`

**Generation Process:**

```python
# 1. Load template
template = Read("{workflow_path}/templates/05_baseline_report_template.md")

# 2. Populate variables from collected data
report = template.replace_all({
    "{{hypothesis_id}}": hypothesis_id,
    "{{timestamp}}": NOW,
    "{{executive_summary}}": generate_executive_summary(comparison_data),
    "{{per_baseline_table}}": format_per_baseline_table(comparison_data),
    "{{win_count}}": win_count,
    "{{baselines_won}}": baselines_won,
    "{{version_history_table}}": format_version_history(verification_state),
    "{{lessons_learned}}": format_lessons(verification_state),
    "{{observations}}": generate_observations(comparison_data),
    "{{conclusion}}": generate_conclusion(comparison_data),
    "{{paper_ready_summary}}": generate_paper_summary(comparison_data),
    # ... (all other template variables)
})

# 3. Write final report
Write("{baseline_folder}/05_baseline_comparison.md", report)
```

**Key Template Variables:**

| Variable | Source |
|----------|--------|
| `{{per_baseline_table}}` | comparison_data.csv (per-baseline comparison) |
| `{{win_count}}` | Gate evaluation (baselines beaten) |
| `{{baselines_won}}` | Gate evaluation (list of won baselines) |
| `{{version_history_table}}` | verification_state.yaml |
| `{{observations}}` | LLM analysis of results |
| `{{paper_ready_summary}}` | LLM-generated summary |

---

## Step Completion Criteria

- [ ] Hypothesis journey extracted from verification_state.yaml
- [ ] Comparison data organized from comparison_data.csv
- [ ] **Comparison figures referenced in report** (learning curves, metric bar chart)
- [ ] 05_baseline_comparison.md generated with all sections

---

## STEP ROUTING

**On completion:** Proceed to step-10a-gate-evaluation.md

```python
checkpoint.current_step = "10a"
SAVE checkpoint
Load, read entire file, then execute: {nextStepFile}
```

---

## SUCCESS/FAILURE

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### SUCCESS:
- Hypothesis journey extracted from verification_state.yaml
- Comparison data loaded from comparison_data.csv
- Per-baseline comparison computed (ours vs baseline on their turf)
- Overall win count identified
- **Comparison figures embedded in report**
- Executive summary written with key findings
- 05_baseline_comparison.md generated with all sections
- Paper-ready summary included

### SYSTEM FAILURE:
- Fabricating statistics or results not from actual data
- Not including hypothesis journey context
- Generating report without comparison_data.csv
- **Not including comparison figures in report**
- **Report not stating Mode B Fair Comparison context**
- **Not reporting per-baseline win/lose results**
