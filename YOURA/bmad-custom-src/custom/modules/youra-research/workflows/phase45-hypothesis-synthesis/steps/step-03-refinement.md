---
name: 'step-03-refinement'
description: 'Remove overclaims, generate refined core statement, verify assumptions'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-03-refinement.md'
nextStepFile: '{workflow_path}/steps/step-04-interpretation.md'
---

# Step 03: Hypothesis Refinement

> **Step Position:** Step 2 (Alignment) → **[Step 3: Refinement]** → Step 4: Interpretation
> **Purpose:** Keep only experiment-supported claims, remove overclaims, generate refined core statement
> **MCP:** ClearThought (structured argumentation)
> **Input:** Prediction-result matrix, causal mechanism verification, original hypothesis
> **Output:** Refined hypothesis, claims changelog, assumptions status

---

## Core Principle

**Phase 2A theories are motivating theories — Phase 4.5 keeps ONLY what the experiments support.**

This step transforms the speculative hypothesis into an evidence-grounded claim by:
1. Identifying which parts of the original claim are supported
2. Removing or weakening unsupported assertions
3. Generating a new core statement that reflects actual evidence
4. Tracking every change with explicit reasoning

---

## Execution Sequence

### 1. Analyze Original Claims Against Evidence

Using the prediction-result matrix from Step 2, evaluate each component of the original hypothesis:

```yaml
for each component of original_core_statement:
  question: "Is this specific claim supported by experiment results?"
  categories:
    KEEP: "Directly supported by SUPPORTED predictions"
    WEAKEN: "Partially supported — needs qualification"
    REMOVE: "Not supported or REFUTED by experiments"
    MODIFY: "Supported but in a different way than originally claimed"
```

**Use ClearThought if available:**

```yaml
tool: mcp__clearThought__structuredargumentation
purpose: "Systematically evaluate each claim against evidence"
input:
  claim: "Original core statement component"
  evidence_for: "Supporting experiment results"
  evidence_against: "Contradicting results"
  output: "KEEP / WEAKEN / REMOVE / MODIFY with reasoning"
```

---

### 2. Build Claims Changelog

Document every change from original to refined hypothesis:

| Original Claim | Action | Reason | Supporting Evidence |
|----------------|--------|--------|---------------------|
| "Method X improves Y by Z%" | WEAKEN | "Improvement was 15%, not Z%" | h-e1 results |
| "Works across all domains" | REMOVE | "Only tested on domain A" | Scope limitation |
| "Causal mechanism via step 2" | MODIFY | "Step 2 falsified, but step 2' works" | h-e2 unexpected finding |
| "P1 prediction holds" | KEEP | "Fully supported" | h-e1 pass_rate 0.92 |

**Rules for changelog:**
- Every REMOVE requires explicit evidence of non-support
- Every WEAKEN requires specification of what qualifier to add
- Every MODIFY requires the new formulation
- KEEP entries still need evidence reference

---

### 3. Verify Assumption Status

For each `key_assumption` from `03_refinement.yaml`:

```yaml
for each assumption:
  evaluate:
    - Was this assumption explicitly tested?
    - Did any experiment result bear on this assumption?
    - Was the assumption violated during experiments?
  assign_status:
    VERIFIED: "Experiment directly confirmed this assumption"
    UNVERIFIED: "No experiment tested this assumption"
    VIOLATED: "Experiment results contradict this assumption"
  record:
    - evidence (what experiment showed)
    - impact_if_violated (what happens to our claims)
```

**Build assumptions status table:**

| Assumption | Status | Evidence | Impact if Violated |
|------------|--------|----------|-------------------|
| "Data is i.i.d." | UNVERIFIED | "Not explicitly tested" | "Results may not generalize" |
| "Model converges" | VERIFIED | "h-e1 training curves show convergence" | "Method would be impractical" |
| "Linear relationship" | VIOLATED | "h-e2 showed non-linear pattern" | "Need non-linear extension" |

---

### 4. Generate Refined Core Statement

Based on the claims changelog and assumption status:

```yaml
process:
  1. Start with original core statement
  2. Remove all REMOVE-marked components
  3. Add qualifiers for WEAKEN-marked components
  4. Substitute MODIFY-marked components with new formulations
  5. Add scope qualifiers for UNVERIFIED assumptions
  6. Result: Refined core statement that is FULLY SUPPORTED by evidence
```

**Quality Criteria for Refined Statement:**
- Every claim in the statement has experiment backing
- No overclaims (claims beyond what evidence supports)
- Appropriate hedging language for partially supported claims
- Explicit scope boundaries where assumptions are unverified
- Must be different from original (otherwise refinement didn't happen)

**Example transformation:**

```
ORIGINAL: "SCSL improves worst-group accuracy by 15% through learning-speed-based
           sample separation, enabling robust classification without group annotations."

REFINED: "SCSL improves worst-group accuracy by 8-12% on datasets with strong
           spurious correlations (Waterbirds, CelebA) through CV-ratio-based sample
           separation, providing a competitive alternative to annotation-dependent
           methods under the conditions tested."
```

---

### 5. Verify Refined Causal Chain

Using the mechanism verification from Step 2:

```yaml
process:
  1. Take original causal mechanism chain
  2. Remove FALSIFIED steps
  3. Mark UNVERIFIED steps with [UNVERIFIED] qualifier
  4. Keep VERIFIED steps as the confirmed chain
  5. If chain is broken (falsified step in middle), note the gap
```

**Output format:**

```
Original Chain: Step 1 → Step 2 → Step 3 → Step 4
Verified Chain: Step 1 [VERIFIED] → Step 2 [UNVERIFIED] → Step 4 [VERIFIED]
Note: Step 3 FALSIFIED — chain has gap between Step 2 and Step 4
```

---

### 6. Summary

```
Hypothesis Refinement Complete
═══════════════════════════════════════
  Claims KEPT: {N}
  Claims WEAKENED: {N}
  Claims REMOVED: {N}
  Claims MODIFIED: {N}

  Assumptions VERIFIED: {N}
  Assumptions UNVERIFIED: {N}
  Assumptions VIOLATED: {N}

  Causal chain: {verified}/{total} steps verified
═══════════════════════════════════════
```

---

### 7. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 4:
- Refined core statement
- Claims changelog (full table)
- Assumptions status table
- Verified causal chain
- All data from Step 1 and Step 2

---
