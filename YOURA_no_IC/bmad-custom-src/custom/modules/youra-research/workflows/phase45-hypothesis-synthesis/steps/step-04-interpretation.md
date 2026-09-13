---
name: 'step-04-interpretation'
description: 'Connect to literature, analyze unexpected findings, identify theoretical contributions'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-04-interpretation.md'
nextStepFile: '{workflow_path}/steps/step-05-limitations.md'
---

# Step 04: Theoretical Interpretation

> **Step Position:** Step 3 (Refinement) → **[Step 4: Interpretation]** → Step 5: Limitations
> **Purpose:** Connect experiment results to existing literature, analyze unexpected findings, identify contributions
> **MCP:** Semantic Scholar (literature search), ClearThought (competing explanations)
> **Input:** Prediction-result matrix, refined hypothesis, validation reports, experiment briefs (02c), task definitions (03_tasks), planned-vs-actual comparison
> **Output:** Theoretical interpretation, literature connections, contribution claims

---

## Core Principle

This step answers: **"What do our results MEAN in the broader context of the field?"**

Phase 2A provided speculative theoretical motivation. Now we have actual results. This step:
1. Explains WHY our results turned out the way they did (mechanistic explanation)
2. Analyzes unexpected findings with multiple competing explanations
3. Connects our findings to existing literature
4. Identifies what our work genuinely contributes to the field

---

## Execution Sequence

### 1. Construct Mechanistic Explanation

Using the verified causal chain from Step 3:

```yaml
process:
  1. For each VERIFIED mechanism step, explain WHY it works based on evidence
  2. For UNVERIFIED steps, state clearly that mechanism is hypothesized, not confirmed
  3. For FALSIFIED steps, explain what actually happened instead
  4. Connect mechanism to actual metrics (e.g., "CV ratio separation of 36x confirms...")

output: "A coherent mechanistic narrative using ONLY verified steps"
```

**Critical Rule:** The mechanistic explanation must NOT include speculative elements from Phase 2A that weren't verified. Use language like:
- "Our experiments demonstrate that..." (for verified)
- "We hypothesize that..." (for unverified, clearly marked)
- "Contrary to our initial expectation..." (for falsified)

---

### 2. Analyze Unexpected Findings

For each unexpected finding from the validation reports:

```yaml
for each unexpected_finding:
  1. State the observation clearly
  2. Explain why it was unexpected (what was the prior expectation from 02c_experiment_brief?)
  3. Check planned-vs-actual comparison: Is this unexpected because of IMPLEMENTATION_GAP or DESIGN_ISSUE?
     - If IMPLEMENTATION_GAP: the "unexpected" finding may be an artifact, not genuine
     - If DESIGN_ISSUE: the finding may reflect confounding, not the hypothesis
     - If HYPOTHESIS_ISSUE: genuine unexpected result worth analyzing
  4. Generate competing explanations (at least 2-3)
  5. Evaluate plausibility of each explanation
  6. Identify which explanation is most likely given available evidence
  7. Note what additional evidence would be needed to distinguish
```

**Use ClearThought if available:**

```yaml
tool: mcp__clearThought__scientificmethod
purpose: "Generate and evaluate competing explanations for unexpected findings"
```

**Output format per finding:**

```markdown
#### Finding: [Title]

- **Observation:** [What happened]
- **Why Unexpected:** [What we expected vs what occurred]
- **Competing Explanations:**
  1. **[Explanation A]:** [Details] (Plausibility: HIGH/MEDIUM/LOW)
  2. **[Explanation B]:** [Details] (Plausibility: HIGH/MEDIUM/LOW)
  3. **[Explanation C]:** [Details] (Plausibility: HIGH/MEDIUM/LOW)
- **Most Likely:** [Which and why]
- **Evidence Needed:** [What experiment would distinguish these]
```

---

### 3. Connect to Existing Literature

**Use Semantic Scholar MCP if available:**

```yaml
for each key finding or contribution:
  tool: mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search
  query: "[finding description + relevant keywords]"
  purpose: "Find related work that either supports, contradicts, or extends our finding"
```

Build literature connection table:

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| "CV ratio separates groups" | "Smith et al. 2024 - Learning dynamics..." | SUPPORTS | [Smith24] |
| "Non-linear improvement curve" | "Jones et al. 2023 - Scaling laws..." | EXTENDS | [Jones23] |
| "Failure on low-spurious data" | "Lee et al. 2024 - When debiasing..." | CONSISTENT_WITH | [Lee24] |

**Relationship types:**
- **SUPPORTS:** Their work provides additional evidence for our finding
- **CONTRADICTS:** Their results differ — explain why
- **EXTENDS:** Our work extends their finding to new domain/setting
- **CONSISTENT_WITH:** Independent work with consistent conclusions
- **BUILDS_ON:** We directly build on their contribution

**If Semantic Scholar MCP is unavailable:**
- Use references already present in Phase 1 research (`01_targeted_research.md`)
- Use references from Phase 2A (`03_refinement.yaml` established_facts)
- Note: "Literature connections based on available references. Comprehensive search recommended."

---

### 4. Identify Theoretical Contributions

Based on refined hypothesis and literature connections:

```yaml
for each potential contribution:
  evaluate:
    - Is this genuinely novel? (Not already known in literature)
    - Is it supported by our experiments? (Not just claimed)
    - Is it significant? (Would the field care?)
  categories:
    METHODOLOGICAL: "New method or technique"
    EMPIRICAL: "New empirical finding"
    THEORETICAL: "New understanding or explanation"
    PRACTICAL: "New practical application or guideline"
```

**Quality criteria for contributions:**
- Must be directly supported by experiment evidence
- Must be positioned against existing literature (what's new vs what's known)
- Must have clear significance statement ("This matters because...")
- Should NOT overclaim (e.g., "first to..." without proper literature check)

---

### 5. Summary

```
Theoretical Interpretation Complete
═══════════════════════════════════════
  Mechanistic explanation: CONSTRUCTED (based on {N} verified steps)
  Unexpected findings: {N} analyzed
  Competing explanations: {N} generated
  Literature connections: {N} found
  Theoretical contributions: {N} identified
═══════════════════════════════════════
```

---

### 6. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

Carry forward into Step 5:
- Mechanistic explanation (verified-only)
- Unexpected findings analysis (with competing explanations)
- Literature connection table
- Theoretical contributions list
- All data from Steps 1-3

---
