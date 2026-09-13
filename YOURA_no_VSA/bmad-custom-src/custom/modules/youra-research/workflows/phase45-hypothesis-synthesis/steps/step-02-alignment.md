---
name: 'step-02-alignment'
description: 'Map predictions to experiment results, verify causal mechanism steps'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-02-alignment.md'
nextStepFile: '{workflow_path}/steps/step-03-refinement.md'
---

# Step 02: Prediction-Result Alignment

> **Step Position:** Step 1 (Init) → **[Step 2: Alignment]** → Step 3: Refinement
> **Purpose:** Map each prediction (P1/P2/P3) to experiment results and verify causal mechanism steps
> **Input:** Original hypothesis data (from Step 1), all h-*/04_validation.md, h-*/04_checkpoint.yaml, h-*/03_tasks.yaml, h-*/02c_experiment_brief.md
> **Output:** Prediction-result matrix, causal mechanism verification table, planned-vs-actual comparison

---

## Core Principle

This step answers: **"Did the experiments support what we predicted?"**

For each prediction, assign one of:
- **SUPPORTED** — Experiment results meet or exceed success criterion
- **PARTIALLY_SUPPORTED** — Results show expected direction but don't fully meet criterion
- **REFUTED** — Results contradict the prediction
- **INCONCLUSIVE** — Insufficient evidence to determine (e.g., experiment failed for technical reasons)

---

## Execution Sequence

### 1. Read All Validation Reports

For EACH `h-*/04_validation.md`:

```yaml
action: "Read and parse validation report"
file: "h-{id}/04_validation.md"
extract:
  hypothesis_id: "ID"
  title: "Title"
  gate_type: "MUST_PASS / SHOULD_WORK / NICE_TO_HAVE"
  gate_result: "PASS / FAIL / PARTIAL"
  experiment_metrics: "All quantitative results (tables, numbers)"
  lessons_learned:
    what_worked: [list]
    what_didnt_work: [list]
    unexpected_findings: [list]
  key_insight: "Main takeaway"
  proven_components: "Components table"
  optimal_hyperparameters: "YAML block"
  recommendations: "For dependent hypotheses"
  figure_paths: "Any figures generated"
```

---

### 2. Read All Checkpoints

For EACH `h-*/04_checkpoint.yaml`:

```yaml
action: "Read and parse checkpoint"
file: "h-{id}/04_checkpoint.yaml"
extract:
  pass_rate: "0.0~1.0"
  failed_checks: [list]
  limitation_note: "string"
  reflection_outcome: "SELF_MODIFY | ROUTED_TO_PHASE_2A | LIMITATION_RECORDED | etc."
  modification_attempt: "integer"
  sdd_metrics:
    sdd_compliant_tasks: "integer"
    total_tasks: "integer"
```

---

### 3. Build Planned-vs-Actual Comparison

Using `03_tasks.yaml` (what was planned) and `04_validation.md` (what actually happened):

```yaml
for each hypothesis h-{id}:
  process:
    1. Extract planned metrics and success criteria from 03_tasks.yaml
    2. Extract actual results from 04_validation.md
    3. Compare: Did implementation match the plan? Where did it deviate?
    4. Classify deviations:
       - IMPLEMENTATION_GAP: Plan was sound but implementation fell short
       - DESIGN_ISSUE: Experiment design (from 02c) had flaws revealed during execution
       - HYPOTHESIS_ISSUE: The hypothesis itself was wrong regardless of implementation
       - SCOPE_CHANGE: Plan was modified during Phase 4 execution
```

**Build the comparison table:**

| Hypothesis | Planned Metric | Planned Target | Actual Result | Deviation Type | Notes |
|------------|---------------|----------------|---------------|----------------|-------|
| h-e1 | ... | ... | ... | HYPOTHESIS_ISSUE | ... |
| h-e2 | ... | ... | ... | IMPLEMENTATION_GAP | ... |

**Why this matters:** When a prediction fails, the cause determines interpretation:
- If IMPLEMENTATION_GAP → the hypothesis might still be valid (limitation, not refutation)
- If HYPOTHESIS_ISSUE → genuine refutation (affects refinement in Step 3)
- If DESIGN_ISSUE → inconclusive (experiment didn't properly test the prediction)

---

### 4. Validate Experiment Design Integrity

Using `02c_experiment_brief.md` to assess whether results are trustworthy:

```yaml
for each hypothesis h-{id}:
  check:
    - Were controlled variables (CV) actually held constant during execution?
    - Was the evaluation protocol followed as specified?
    - Were there confounding factors not accounted for in the experiment design?
    - Did the actual datasets match what was specified in the brief?

  flag_issues:
    - Any deviation between planned and executed experimental conditions
    - Any missing control conditions
    - Any evaluation protocol changes
```

**Purpose:** Results from a well-controlled experiment carry more weight than results from an experiment with design deviations. This assessment informs confidence levels in the prediction-result matrix.

---

### 5. Build Prediction-Result Matrix

For EACH prediction (P1, P2, P3):

```yaml
process:
  1. Identify which hypothesis/hypotheses tested this prediction
  2. Extract relevant metrics from those validation reports
  3. Compare actual results against success_criterion from 03_refinement.yaml
  4. Assign status (SUPPORTED / PARTIALLY_SUPPORTED / REFUTED / INCONCLUSIVE)
  5. Assign confidence level (HIGH / MEDIUM / LOW)
  6. Write evidence summary
```

**Status Assignment Rules:**

| Condition | Status |
|-----------|--------|
| Result meets success criterion AND gate PASS | SUPPORTED |
| Result shows expected direction BUT doesn't meet criterion | PARTIALLY_SUPPORTED |
| Result contradicts prediction OR gate FAIL on this prediction | REFUTED |
| Experiment failed technically (not prediction failure) | INCONCLUSIVE |
| No experiment directly tested this prediction | INCONCLUSIVE |

**Confidence Assignment Rules:**

| Condition | Confidence |
|-----------|------------|
| Multiple experiments confirm, strong statistical evidence | HIGH |
| Single experiment confirms, or moderate evidence | MEDIUM |
| Marginal results, small sample, or indirect evidence | LOW |

**Build the matrix:**

| Prediction | Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence |
|------------|-----------|-----------|------------|--------|--------|------------|----------|
| P1 | ... | h-e1 | ... | ... | SUPPORTED | HIGH | ... |
| P2 | ... | h-e2 | ... | ... | PARTIALLY_SUPPORTED | MEDIUM | ... |
| P3 | ... | h-e1,h-e2 | ... | ... | REFUTED | HIGH | ... |

---

### 6. Verify Causal Mechanism Steps

For each step in the causal mechanism chain (from `03_refinement.yaml`):

```yaml
process:
  for each mechanism_step:
    1. Identify: Does any experiment result provide evidence for/against this step?
    2. Check the falsifier: Was the falsifier condition triggered?
    3. Assign verification status:
       - VERIFIED: Direct evidence supports this step
       - PARTIALLY_VERIFIED: Indirect evidence or partially tested
       - UNVERIFIED: No experiment directly tested this step
       - FALSIFIED: Falsifier condition was triggered
    4. Record the evidence
```

**Build the verification table:**

| Step | Description | Falsifier | Evidence | Status |
|------|-------------|-----------|----------|--------|
| 1 | ... | ... | "h-e1 showed..." | VERIFIED |
| 2 | ... | ... | "No direct test" | UNVERIFIED |
| 3 | ... | ... | "h-e2 contradicts..." | FALSIFIED |

---

### 7. Cross-Reference Summary

Create a consolidated view:

```
Prediction-Result Alignment Summary
═══════════════════════════════════════
  P1: {{status}} ({{confidence}})
  P2: {{status}} ({{confidence}})
  P3: {{status}} ({{confidence}})

Causal Mechanism: {{N}}/{{total}} steps verified
  Verified: {{count}}
  Unverified: {{count}}
  Falsified: {{count}}

Per-Hypothesis Summary:
  h-e1: PASS (pass_rate: 0.85)
  h-e2: FAIL (pass_rate: 0.40)
═══════════════════════════════════════
```

---

### 8. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 3:
- Prediction-result matrix (P1, P2, P3 with statuses)
- Planned-vs-actual comparison table (with deviation types)
- Experiment design integrity assessment
- Causal mechanism verification table
- Per-hypothesis results summary
- All extracted metrics and lessons learned

---
