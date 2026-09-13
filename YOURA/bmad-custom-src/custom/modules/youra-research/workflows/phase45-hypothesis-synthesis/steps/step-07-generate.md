---
name: 'step-07-generate'
description: 'Assemble 045_validated_hypothesis.md from all previous step outputs'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-07-generate.md'
nextStepFile: '{workflow_path}/steps/step-08-finalize.md'
templateFile: '{workflow_path}/templates/045_validated_hypothesis_template.md'
---

# Step 07: Generate Document

> **Step Position:** Step 6 (Future Work) → **[Step 7: Generate]** → Step 8: Finalize
> **Purpose:** Assemble `045_validated_hypothesis.md` from all previous step outputs
> **Input:** All accumulated data from Steps 1-6, template file
> **Output:** `{research_folder}/045_validated_hypothesis.md`

---

## Core Principle

This step assembles the final document. **No new analysis** — just organizing and writing the outputs from Steps 1-6 into the template structure. The document must be **directly consumable by Phase 6 Paper Writing**.

---

## Execution Sequence

### 1. Load Template

```yaml
action: "Read template file"
file: "{templateFile}"
purpose: "Get document structure and placeholder locations"
```

---

### 2. Fill Section 1: Executive Summary

Write a 2-3 paragraph summary covering:
- Original hypothesis vs refined hypothesis (key changes)
- Overall validation results (N/M predictions supported, pass rate)
- Main theoretical insight (experiment-verified)
- Key limitations and scope

**Use data from:** Steps 1-6 (high-level summary of all findings)

---

### 3. Fill Section 2: Prediction-Result Matrix

**Use data from:** Step 2 (Alignment)

- Fill the prediction-result table (P1, P2, P3)
- Fill the causal mechanism verification table
- Ensure all status assignments have evidence references

---

### 4. Fill Section 3: Hypothesis Refinement

**Use data from:** Step 3 (Refinement)

- 3.1: Original core statement (verbatim from `03_refinement.yaml`)
- 3.2: Refined core statement (from Step 3)
- 3.3: Verified causal chain diagram
- 3.4: Claims removed/weakened table (from changelog)
- 3.5: Assumptions status table

---

### 5. Fill Section 4: Theoretical Interpretation

**Use data from:** Step 4 (Interpretation)

- 4.1: Mechanistic explanation (verified-only narrative)
- 4.2: Unexpected findings analysis (with competing explanations)
- 4.3: Literature connection table
- 4.4: Theoretical contributions list

---

### 6. Fill Section 5: Experiment Results

**Use data from:** Steps 1-2 (raw experiment data, task definitions, experiment briefs)

- 5.1: Per-hypothesis results table
- 5.2: Aggregate metrics table
- 5.3: Optimal hyperparameters (YAML block)
- 5.4: Proven components table
- 5.5: Key figures reference table
- 5.6: Planned-vs-actual comparison (from `03_tasks.yaml` vs `04_validation.md`)

**Critical:** This section provides the raw data Phase 6 needs for the Results and Experiments sections. Include all quantitative data. The planned-vs-actual comparison helps Phase 6 contextualize whether deviations stem from implementation gaps or genuine hypothesis issues.

---

### 7. Fill Section 6: Limitations & Scope Boundaries

**Use data from:** Step 5 (Limitations)

- 6.1: Principled limitations (with root causes)
- 6.2: Scope conditions table
- 6.3: Assumption violation impact

---

### 8. Fill Section 7: Future Work

**Use data from:** Step 6 (Future Work)

- 7.1: From untested alternative explanations
- 7.2: From unverified assumptions
- 7.3: From scope extension opportunities

---

### 9. Fill Section 8: Implications for Phase 6

**This section is CRITICAL — it directly guides Phase 6 narrative design.**

#### 8.1 Recommended Narrative Hook

Based on the most striking finding from the experiments:
- Choose a hook strategy (surprising statistic, counterintuitive finding, practical failure, puzzle)
- Write a specific hook suggestion (not generic)
- Explain why this hook works

#### 8.2 Key Insight (Experiment-Verified)

- The single most important "aha!" moment from the research
- Must be supported by experiment evidence (reference specific results)
- Written as a single clear sentence

#### 8.3 Strongest Claims (Paper-Ready)

List the 3-5 claims that have the strongest experiment backing:
- Each with evidence reference and confidence level
- Each with suggested paper section (Introduction, Results, Discussion)

#### 8.4 Honest Limitations (Must Include in Paper)

List the 2-4 most important limitations that MUST appear in the paper:
- Each with suggested framing (how to present without undermining contribution)
- Each with "why acceptable" reasoning

#### 8.5 Evidence Highlights (Most Persuasive)

The 3-5 most compelling pieces of evidence:
- Each with data summary, "so what" interpretation
- Each with suggested figure/table for the paper

---

### 10. Write the Document

```yaml
action: "Write 045_validated_hypothesis.md"
file: "{research_folder}/045_validated_hypothesis.md"
content: "Filled template with all 8 sections"
```

**Quality check before writing:**
- [ ] All 8 sections filled (no empty placeholders remaining)
- [ ] All tables have actual data (no template markers like `{{...}}`)
- [ ] Executive summary reflects all sections
- [ ] Section 8 has all 5 subsections filled
- [ ] All evidence references point to actual experiment data

---

### 11. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

---
