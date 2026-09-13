---
name: 'step-01-init'
description: 'Load pipeline state, verify preconditions, collect hypothesis data, read original hypothesis'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-01-init.md'
nextStepFile: '{workflow_path}/steps/step-02-alignment.md'
---

# Step 01: Initialize

> **Step Position:** **[Step 1: Initialize]** → Step 2: Prediction-Result Alignment
> **Purpose:** Load pipeline state, verify all preconditions, collect per-hypothesis data
> **MCP:** Serena (memory read)
> **Output:** Hypothesis list with statuses, original hypothesis data loaded into working memory

---

## Execution Sequence

### 1. Read Serena Memories

Check for relevant cross-pipeline learning:

```yaml
action: "Read Serena memories"
tool: mcp__serena__list_memories
purpose: "Check for past Phase 4.5 execution insights or pipeline patterns"
```

Read any relevant `.md` memory files and incorporate insights.

---

### 2. Load Verification State

```yaml
action: "Read verification_state.yaml"
file: "{research_folder}/verification_state.yaml"
extract:
  - workflow.sub_hypotheses_complete
  - workflow.current_phase
  - workflow.status
  - sub_hypotheses (list with statuses)
  - main_hypothesis
```

**GATE CHECK:**
```
IF workflow.sub_hypotheses_complete != true:
    ERROR: "Phase 4.5 requires all sub-hypotheses to complete Phase 4."
    EXIT with error message.
```

---

### 3. Collect Hypothesis Folders

Scan `{research_folder}/h-*/` directories:

```yaml
action: "List all hypothesis folders"
for each h-* folder:
  check:
    - h-{id}/04_validation.md exists
    - h-{id}/04_checkpoint.yaml exists
  record:
    - hypothesis_id
    - folder_path
    - has_validation: true/false
    - has_checkpoint: true/false
```

**GATE CHECK:**
```
IF no h-*/04_validation.md found:
    ERROR: "No experiment results found. Run hypothesis-loop first."
    EXIT with error message.
```

Log the collected hypotheses:

```
Found {N} hypothesis folders:
  - h-e1: validation=YES, checkpoint=YES
  - h-e2: validation=YES, checkpoint=YES
  ...
```

---

### 4. Read Original Hypothesis (03_refinement.yaml)

```yaml
action: "Read 03_refinement.yaml"
file: "{research_folder}/03_refinement.yaml"
extract:
  core_statement: "final_hypothesis.core_claim OR core_statement"
  variables:
    IV: "Independent variable name and description"
    DV: "Dependent variable name and description"
    CV: "Controlled variables"
  predictions:
    P1: "statement, test_method, success_criterion"
    P2: "statement, test_method, success_criterion"
    P3: "statement, test_method, success_criterion"
  causal_mechanism:
    steps: "List of mechanism steps with falsifiers"
  key_assumptions: "List of assumptions"
  scope: "Scope conditions"
  established_facts: "Known facts used as basis"
```

**Note:** The `03_refinement.yaml` uses Free-Parse schema. Parse flexibly — field names may vary slightly between pipeline runs.

---

### 5. Read Task Definitions (03_tasks.yaml)

For EACH `h-*/03_tasks.yaml`:

```yaml
action: "Read Phase 3 task definitions"
file: "h-{id}/03_tasks.yaml"
extract:
  planned_tasks: "List of implementation tasks"
  expected_metrics: "Metrics Phase 3 planned to measure"
  success_criteria: "What constitutes success per task"
  implementation_approach: "Planned approach and architecture"
  sdd_expectations: "SDD compliance targets"
```

**Purpose:** Enables planned-vs-actual comparison in Step 2. Understanding what was *intended* reveals whether deviations in results stem from implementation gaps or genuine hypothesis issues.

---

### 6. Read Experiment Briefs (02c_experiment_brief.md)

For EACH `h-*/02c_experiment_brief.md`:

```yaml
action: "Read Phase 2C experiment design"
file: "h-{id}/02c_experiment_brief.md"
extract:
  variables:
    independent: "IV definition and levels"
    dependent: "DV definition and measurement"
    controlled: "CV list and how controlled"
  experimental_conditions: "Treatment vs control groups"
  datasets: "Which datasets, why chosen, statistics"
  evaluation_protocol: "How results are evaluated"
  statistical_tests: "Planned statistical analysis"
  expected_outcomes: "What Phase 2C predicted would happen"
```

**Purpose:** Knowing the experiment design (variables, controls, evaluation protocol) enables rigorous interpretation of whether results are valid or confounded.

---

### 7. Read Optional Files

If available, also read:

```yaml
optional_files:
  - file: "{research_folder}/02_synthesis.yaml"
    purpose: "Additional context from Phase 2A synthesis"

  - file: "{research_folder}/02b_verification_plan.md"
    purpose: "Verification plan context"
```

---

### 8. Verify Readiness

Confirm all data loaded:

```
Phase 4.5 Initialization Complete
═══════════════════════════════════════
  Hypothesis folders found: {N}
  Validation reports: {N}
  Checkpoint files: {N}
  Task definitions: {N}
  Experiment briefs: {N}
  Original hypothesis: LOADED
  Predictions found: P1, P2, P3
  Causal mechanism steps: {N}
  Key assumptions: {N}
═══════════════════════════════════════
```

---

### 9. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 2:
- List of hypothesis IDs and folder paths
- Original hypothesis data (core_statement, predictions, mechanism, assumptions)
- Task definitions data (planned tasks, expected metrics, success criteria)
- Experiment design data (variables, conditions, evaluation protocol)
- Verification state data

---

## Error Handling

| Error | Action |
|-------|--------|
| `verification_state.yaml` not found | EXIT — Phase 2B not completed |
| `sub_hypotheses_complete = false` | EXIT — Run hypothesis-loop first |
| No `h-*/04_validation.md` found | EXIT — No experiments completed |
| `03_refinement.yaml` not found | EXIT — Phase 2A not completed |
| `03_refinement.yaml` parse error | WARN — Try alternative field names |

---
