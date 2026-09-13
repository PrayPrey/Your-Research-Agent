---
name: 'step-05-limitations'
description: 'Define principled boundary conditions, root cause analysis, scope conditions'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-05-limitations.md'
nextStepFile: '{workflow_path}/steps/step-06-future-work.md'
---

# Step 05: Limitations & Scope Boundaries

> **Step Position:** Step 4 (Interpretation) → **[Step 5: Limitations]** → Step 6: Future Work
> **Purpose:** Define principled limitations with root cause analysis and explicit scope boundaries
> **Input:** Prediction-result matrix, assumptions status, checkpoints, causal mechanism verification
> **Output:** Limitations analysis, scope boundary conditions

---

## Core Principle

Limitations must be **principled, not superficial**. Instead of "we didn't test on more datasets," explain:
- WHY the limitation exists (root cause)
- WHAT impact it has on claims
- WHEN results are expected to hold vs not hold
- WHETHER the limitation is fundamental or addressable

---

## Execution Sequence

### 1. Categorize Limitation Sources

Limitations come from four sources. Analyze each:

#### 1.1 From Failed/Partially Supported Predictions

```yaml
for each REFUTED or PARTIALLY_SUPPORTED prediction:
  analyze:
    what_failed: "What specific aspect didn't work?"
    root_cause: "Why did it fail? (technical, conceptual, or scope issue)"
    impact_on_claims: "Which claims are affected?"
    is_fundamental: "Is this a fundamental flaw or addressable limitation?"
```

#### 1.2 From Violated/Unverified Assumptions

```yaml
for each VIOLATED or UNVERIFIED assumption (from Step 3):
  analyze:
    violation_description: "How was the assumption violated?"
    impact: "What happens to our results if this assumption doesn't hold?"
    scope_restriction: "Under what conditions does the assumption hold?"
```

#### 1.3 From Experiment Failures (Checkpoints)

```yaml
for each hypothesis checkpoint with failures:
  analyze:
    failed_checks: "What validation checks failed?"
    limitation_note: "Recorded limitation"
    reflection_outcome: "How was the failure handled?"
    remaining_impact: "What limitations remain after handling?"
```

#### 1.4 From Unverified Mechanism Steps

```yaml
for each UNVERIFIED or FALSIFIED causal mechanism step:
  analyze:
    gap_description: "What part of the explanation is not confirmed?"
    impact: "Does this gap invalidate the overall claim?"
    alternative: "Is there an alternative path that IS verified?"
```

---

### 2. Construct Principled Limitations

For each identified limitation, write a principled analysis:

```markdown
#### [Limitation Title]

- **What:** [Clear description of the limitation]
- **Why This Matters:** [Impact on claims and conclusions]
- **Root Cause:** [Why this limitation exists — not just "we didn't test X"]
- **Impact on Claims:** [Which specific claims are affected and how]
- **Why Acceptable:** [Why this limitation doesn't invalidate the contribution]
```

**Anti-patterns to AVOID:**
```
BAD: "We only tested on two datasets."
GOOD: "Our evaluation covers datasets with strong spurious correlations
       (Waterbirds, CelebA). The method's effectiveness on datasets with
       subtle or distributed spurious features remains untested because
       detecting learning speed separation requires a minimum level of
       spurious correlation strength. This means our claims about sample
       separation applicability should be qualified to high-spurious settings."
```

---

### 3. Define Scope Boundaries

Explicitly state where results hold and where they may not:

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Dataset type | High spurious correlation | Low/subtle spurious | h-e2 failure analysis |
| Model size | ResNet-50 scale | Very large/small models | Only tested at one scale |
| Training regime | Standard SGD | Different optimizers | Assumption, not tested |

**For each boundary:**
```yaml
analyze:
  condition: "What variable defines the boundary?"
  inside_boundary: "Under what values do our results hold?"
  outside_boundary: "Under what values might they not hold?"
  evidence: "What experiment result defines this boundary?"
  confidence: "How confident are we in this boundary?"
```

---

### 4. Assess Assumption Violation Impact

For each VIOLATED assumption from Step 3:

```yaml
impact_analysis:
  assumption: "[The violated assumption]"
  violation: "[How it was violated]"
  impact_severity: "HIGH / MEDIUM / LOW"
  affected_claims: "[Which claims are affected]"
  mitigation: "[What we did or could do about it]"
```

---

### 5. Summary

```
Limitations & Scope Analysis Complete
═══════════════════════════════════════
  Principled limitations: {N}
  Scope boundary conditions: {N}
  Assumption violations: {N}

  Fundamental limitations: {N}
  Addressable limitations: {N}
═══════════════════════════════════════
```

---

### 6. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 6:
- Principled limitations list (with root causes and impacts)
- Scope boundary conditions table
- Assumption violation impact analysis
- All data from Steps 1-4

---
