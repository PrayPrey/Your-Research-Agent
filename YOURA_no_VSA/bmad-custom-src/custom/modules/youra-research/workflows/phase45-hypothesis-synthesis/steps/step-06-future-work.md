---
name: 'step-06-future-work'
description: 'Derive results-grounded future directions from untested alternatives and unverified assumptions'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-06-future-work.md'
nextStepFile: '{workflow_path}/steps/step-07-generate.md'
---

# Step 06: Future Work

> **Step Position:** Step 5 (Limitations) → **[Step 6: Future Work]** → Step 7: Generate
> **Purpose:** Derive future work directions that are grounded in current experiment results
> **Input:** Refined hypothesis, theoretical interpretation, limitations analysis
> **Output:** Results-grounded future work directions (3 categories)

---

## Core Principle

Future work must be **grounded in experiment results**, not speculative.

Every future direction must trace back to:
- An untested alternative explanation (from Step 4)
- An unverified assumption (from Step 3)
- A scope boundary that could be extended (from Step 5)

**Anti-pattern:** "Future work includes testing on more datasets and larger models."
**Correct:** "Our CV-ratio separation mechanism was not tested under low-spurious conditions. A future experiment measuring CV-ratio distribution on datasets with subtle spurious features (e.g., ImageNet-A) would determine whether the approach generalizes beyond high-spurious settings."

---

## Execution Sequence

### 1. Future Work from Untested Alternative Explanations

From Step 4 (Theoretical Interpretation), for each unexpected finding with competing explanations:

```yaml
for each competing_explanation where status != "confirmed":
  derive_future_work:
    alternative: "The competing explanation"
    why_not_tested: "Why current experiments don't distinguish this"
    proposed_experiment:
      design: "What experiment would test this alternative"
      expected_outcome_if_true: "What we'd see if this explanation is correct"
      expected_outcome_if_false: "What we'd see if it's wrong"
    priority: "HIGH / MEDIUM / LOW"
    rationale: "Why this matters for the field"
```

**Example:**
```markdown
- **Alternative:** The improvement may come from implicit data augmentation
  rather than explicit spurious feature separation.
  - **Why Not Yet Tested:** Our experiment design didn't include an
    augmentation-only baseline that matches the data diversity.
  - **Proposed Experiment:** Compare SCSL against a model trained with
    matched augmentation diversity but without the separation mechanism.
  - **Expected Outcome:** If augmentation explains the improvement,
    the augmentation baseline should match SCSL performance.
```

---

### 2. Future Work from Unverified Assumptions

From Step 3 (Assumptions Status), for each UNVERIFIED assumption:

```yaml
for each assumption where status == "UNVERIFIED":
  derive_future_work:
    assumption: "The unverified assumption"
    current_status: "UNVERIFIED"
    proposed_test:
      design: "How to explicitly test this assumption"
      required_data: "What data or setup is needed"
      success_criterion: "How to determine if assumption holds"
    if_violated:
      impact: "What changes about our claims"
      adaptation: "How the method could be adapted"
    priority: "HIGH if assumption is critical, LOW if peripheral"
```

---

### 3. Future Work from Scope Extension

From Step 5 (Limitations & Scope), for each scope boundary:

```yaml
for each scope_boundary:
  derive_future_work:
    current_scope: "Where results currently hold"
    extension: "Where we'd like results to hold"
    feasibility_evidence: "Why we think extension might work"
    required_resources: "What's needed to test this"
    expected_challenges: "What might go wrong"
    priority: "Based on significance of the extension"
```

---

### 4. Prioritize and Organize

Rank all future work directions by:

1. **Impact:** How much would this advance understanding?
2. **Feasibility:** How practical is the proposed experiment?
3. **Urgency:** Does this address a critical gap in current claims?

```yaml
priority_matrix:
  HIGH_IMPACT + HIGH_FEASIBILITY: "Immediate next experiment"
  HIGH_IMPACT + LOW_FEASIBILITY: "Medium-term research direction"
  LOW_IMPACT + HIGH_FEASIBILITY: "Quick validation to strengthen claims"
  LOW_IMPACT + LOW_FEASIBILITY: "Long-term vision"
```

---

### 5. Summary

```
Future Work Derivation Complete
═══════════════════════════════════════
  From untested alternatives: {N} directions
  From unverified assumptions: {N} directions
  From scope extensions: {N} directions

  Priority: HIGH={N}, MEDIUM={N}, LOW={N}

  All directions grounded in:
    - Experiment results: YES
    - Specific evidence: YES
    - Speculative: NO
═══════════════════════════════════════
```

---

### 6. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 7:
- Future work directions (3 categories, prioritized)
- All data from Steps 1-5

---
