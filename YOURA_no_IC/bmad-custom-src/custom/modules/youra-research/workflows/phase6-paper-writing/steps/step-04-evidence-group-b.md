---
name: 'step-04-evidence-group-b'
description: 'Generate Experiments, Results, and Discussion with shared narrative context'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-04-evidence-group-b.md'
nextStepFile: '{workflow_path}/steps/step-05-conclusion-abstract.md'
workflowFile: '{workflow_path}/workflow.md'
narrativeBlueprint: '{paper_folder}/06_narrative_blueprint.yaml'
---

# Step 04: Story Group B - Evidence Sections

> **Step Position:** ... -> Step 3 (Story Group A) -> **[Step 4: Story Group B]** -> Step 5: Closure
> **Purpose:** Generate Experiments, Results, and Discussion in shared context for evidence coherence
> **Context Isolation:** NO - Sections share context within group
> **Execution Mode:** Task Agent with context sharing
> **Outputs:** `04_experiments.md`, `05_results.md`, `06_discussion.md`

---

## Why Evidence Needs Coherence

**The Problem with Isolated Evidence Sections:**
```
Old approach:
  Experiments → isolated → Results → isolated → Discussion

Result:
  ❌ Experimental questions don't match claims
  ❌ Results presented without interpretation
  ❌ Discussion disconnected from results
  ❌ "Table 1 shows X, Table 2 shows Y" (no meaning)
```

**The Coherent Evidence Approach:**
```
New approach:
  Experiments → shared context → Results → Discussion

Result:
  ✅ Experiments designed to test specific claims
  ✅ Results interpreted, not just reported
  ✅ Discussion naturally flows from results
  ✅ "This result supports our claim because..."
```

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Follow narrative blueprint's evidence_narrative section
- 🔄 Each result should have a "so what?" interpretation
- 💬 Connect experiments to claims from Introduction
- 📋 Discussion must acknowledge honest limitations
- 🚫 FORBIDDEN to just list tables without interpretation

---

## Prerequisites

Before executing this step:

1. Steps 01-03 completed successfully
2. `06_narrative_blueprint.yaml` exists
3. Story Group A sections generated (Introduction, Related Work, Methodology)
4. Figure registry created in Step 01

---

## Task Agent Spawn Instructions

```yaml
task_agent:
  type: "general-purpose"
  context_isolation: false # CRITICAL: Sections share context

  inputs_to_load:
    - "{paper_folder}/06_narrative_blueprint.yaml"
    - "{research_folder}/045_validated_hypothesis.md"
    - "{sections_folder}/03_methodology.md" # For experimental setup connection
    - "{hypothesis_folder}/02c_experiment_brief.md"
    - "{hypothesis_folder}/03_prd.md"
    - "{hypothesis_folder}/baseline_comparison/05_baseline_comparison.md"
    - "{research_folder}/verification_state.yaml"
    - "{paper_folder}/figure_registry.yaml"

  outputs_to_write:
    - "{sections_folder}/04_experiments.md"
    - "{sections_folder}/05_results.md"
    - "{sections_folder}/06_discussion.md"

  mcp_servers:
    - serena # For code analysis and actual results extraction
```

---

## Execution Sequence

### 1. Load Narrative Blueprint

```yaml
action: "Load evidence narrative design"
file: "{paper_folder}/06_narrative_blueprint.yaml"
extract:
  - evidence_narrative.main_claim
  - evidence_narrative.supporting_evidence
  - evidence_narrative.surprising_findings
  - evidence_narrative.what_results_mean
  - section_goals.experiments
  - section_goals.results
  - section_goals.discussion
```

---

### 2. Load Phase 4/5 Results

Load actual results data:

```yaml
artifacts_to_load:
  # Phase 4.5: Validated hypothesis synthesis
  - file: "{research_folder}/045_validated_hypothesis.md"
    use_for: "Prediction-result matrix, aggregate metrics, theoretical interpretation, evidence highlights, limitations"

  # Phase 2C: Experiment design
  - file: "{hypothesis_folder}/02c_experiment_brief.md"
    use_for: "Experimental questions, metrics definition"

  # Phase 3: PRD
  - file: "{hypothesis_folder}/03_prd.md"
    use_for: "Implementation details, hyperparameters"

  # Phase 5: Baseline comparison
  - file: "{hypothesis_folder}/baseline_comparison/05_baseline_comparison.md"
    use_for: "Comparison with baselines, statistical significance"

  # Verification state
  - file: "{research_folder}/verification_state.yaml"
    use_for: "Final metrics, success criteria evaluation"
```

---

### 3. Generate Experiments Section (04_experiments.md)

Experiments section explains HOW we test our claims.

#### 3.1 Experimental Questions

From `section_goals.experiments.experimental_questions`:

```markdown
## Experimental Setup

We design experiments to answer the following questions:

**RQ1:** [Question from experimental_questions]
**RQ2:** [Question from experimental_questions]
**RQ3:** [Question from experimental_questions]
```

**CRITICAL:** Each RQ should map to a claim from Introduction.

#### 3.2 Datasets

From `section_goals.experiments.dataset_rationale`:

```markdown
### Datasets

We evaluate on the following datasets:

**[Dataset 1]:** [Description] [Why chosen - connects to claims]
- Statistics: [N samples, features, etc.]
- [Relevant characteristics for our method]

**[Dataset 2]:** [Description] [Why chosen]
- Statistics: ...
```

**Include table if multiple datasets:**

| Dataset | # Samples | # Features | Task | Why Chosen |
|---------|-----------|------------|------|------------|
| ... | ... | ... | ... | ... |

#### 3.3 Baselines

From `section_goals.experiments.baseline_rationale`:

```markdown
### Baselines

We compare against the following methods:

**[Baseline 1]:** [Citation] - [Brief description]
  - Why included: [Connection to our claims]

**[Baseline 2]:** [Citation] - [Brief description]
  - Why included: ...
```

**CRITICAL:** Justify WHY each baseline is included.

#### 3.4 Implementation Details

```markdown
### Implementation Details

[Framework, hardware, training procedure]

**Hyperparameters:** [Key hyperparameters with values]
  - Learning rate: X
  - Batch size: X
  - Training epochs: X
  - [Method-specific parameters]

**Compute Resources:** [GPU type, training time]

**Reproducibility:** Code available at [URL if applicable]
```

**Use Serena MCP** to extract accurate implementation details:

```yaml
serena_extraction:
  tool: "serena"
  actions:
    - "search_for_pattern" - Find hyperparameter definitions
    - "find_symbol" - Find training configuration
```

#### 3.5 Evaluation Metrics

From `section_goals.experiments.metric_rationale`:

```markdown
### Evaluation Metrics

We use the following metrics:

**[Metric 1]:** [Definition] - Why: [Connection to claims]
**[Metric 2]:** [Definition] - Why: ...

Statistical significance evaluated using [method] with p < 0.05.
```

---

### 4. Generate Results Section (05_results.md)

Results section presents EVIDENCE with INTERPRETATION.

#### 4.1 Main Results

From `evidence_narrative.main_claim`:

```markdown
## Results

### Main Results

[One sentence restating main claim]

Table 1 presents our main comparison results.

| Method | Metric 1 | Metric 2 | Metric 3 |
|--------|----------|----------|----------|
| Baseline 1 | X | X | X |
| Baseline 2 | X | X | X |
| **Ours** | **X** | **X** | **X** |

**Key Observations:**

1. [First key observation with interpretation]
   - This result shows that [what it means for our claim]

2. [Second key observation]
   - This supports [which part of our hypothesis]

3. [Third observation if applicable]
```

**CRITICAL: Do NOT just say "Table 1 shows X". Interpret what X means.**

**Writing principle:** Results should read like an argument, not a spreadsheet. Every number you include should serve the narrative — if removing a number doesn't weaken the argument, it doesn't belong in the main text. When in doubt, move detailed metrics to an Appendix and keep the main body focused on telling the story of what you found and why it matters.

#### 4.2 Supporting Evidence

From `evidence_narrative.supporting_evidence`:

For each piece of evidence:

```markdown
### [Evidence Topic, e.g., "Ablation Study"]

**Question:** [What are we testing?]

[Table or Figure]

**Finding:** [What the data shows]
**Interpretation:** [What this means for our claims]
```

#### 4.3 Surprising Findings

From `evidence_narrative.surprising_findings`:

```markdown
### Analysis: [Surprising Finding Title]

Interestingly, we observe that [surprising finding].

[Data/visualization supporting this]

**Our interpretation:** [Why we think this happens]

This suggests that [broader implication].
```

#### 4.4 Figure Placement

Reference figures from the figure registry:

```markdown
Figure [N] shows [what the figure shows].

[Reference: {figures_folder}/fig_results_X.png]

[Interpretation of what the figure reveals]
```

**CRITICAL:** Every figure must be:
1. Referenced in text BEFORE it appears
2. Interpreted, not just shown

---

### 5. Generate Discussion Section (06_discussion.md)

Discussion interprets results and acknowledges limitations.

#### 5.1 Key Findings Interpretation

From `section_goals.discussion.key_findings_interpretation`:

```markdown
## Discussion

### Key Findings

Our experiments reveal several important findings:

**Finding 1:** [Main finding with broader interpretation]
  - This suggests that [implication for field/practice]

**Finding 2:** [Secondary finding]
  - This indicates that [implication]
```

#### 5.2 Honest Limitations

From `section_goals.discussion.honest_limitations`:

**CRITICAL: Be honest. Reviewers will find these anyway.**

```markdown
### Limitations

Our work has several limitations:

**Limitation 1:** [Limitation description]
  - Why acceptable: [Why this doesn't invalidate our claims]
  - Future work: [How this could be addressed]

**Limitation 2:** [Limitation description]
  - Why acceptable: ...
  - Future work: ...
```

#### 5.3 Broader Impact Statement

Required for ICML:

```markdown
### Broader Impact

[Positive impacts of this research]

[Potential negative impacts or misuse concerns]

[Mitigation strategies if applicable]
```

---

### 6. Ensure Evidence Coherence

After generating all three sections, verify:

#### 6.1 Claim-Evidence Alignment

| Claim (from Intro) | RQ (Experiments) | Evidence (Results) | Interpretation (Discussion) |
|-------------------|------------------|--------------------|-----------------------------|
| [Claim 1] | RQ1 | Table X | Finding Y |
| [Claim 2] | RQ2 | Figure Y | Finding Z |

**Every claim must have supporting evidence.**

#### 6.2 Number Consistency

```yaml
verify:
  - "Numbers in Results match Phase 4/5 reports"
  - "Baseline numbers match literature"
  - "Statistical significance properly reported"
```

#### 6.3 Figure-Text Consistency

```yaml
check:
  - "All figures are referenced in text"
  - "Figure descriptions match actual figure content"
  - "Figure numbers are sequential"
```

---

### 7. Write Section Files

```yaml
outputs:
  - file: "{sections_folder}/04_experiments.md"
    content: "[Generated Experiments section]"

  - file: "{sections_folder}/05_results.md"
    content: "[Generated Results section]"

  - file: "{sections_folder}/06_discussion.md"
    content: "[Generated Discussion section]"
```

---

### 8. Update Checkpoint

Update `06_paper_checkpoint.yaml`:

```yaml
current_step: 5
story_groups:
  group_a:
    status: "complete"
  group_b:
    status: "complete"
    sections:
      - experiments: "complete"
      - results: "complete"
      - discussion: "complete"
    completed_at: "{ISO8601}"
updated_at: "{ISO8601}"
```

---

### 9. Return to Orchestrator

```yaml
agent: "story-group-b"
status: "COMPLETED"
outputs:
  - "04_experiments.md"
  - "05_results.md"
  - "06_discussion.md"

summary:
  experiments:
    word_count: {N}
    research_questions: {N}
    datasets_count: {N}
    baselines_count: {N}

  results:
    word_count: {N}
    tables_count: {N}
    figures_count: {N}
    key_findings: {N}

  discussion:
    word_count: {N}
    limitations_count: {N}
    broader_impact_included: true/false

evidence_coherence:
  claims_supported: {N}/{total}
  all_figures_referenced: true/false
  numbers_verified: true/false
```

---

### 10. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

---

## Output Summary

| Output | Path | Description |
|--------|------|-------------|
| Experiments | `{sections_folder}/04_experiments.md` | RQs, datasets, baselines, metrics |
| Results | `{sections_folder}/05_results.md` | Evidence with interpretation |
| Discussion | `{sections_folder}/06_discussion.md` | Interpretation + honest limitations |
| Updated Checkpoint | `{paper_folder}/06_paper_checkpoint.yaml` | Progress tracking |

---

## 🚨 SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Evidence narrative from blueprint followed
- Experimental questions map to claims from Introduction
- All results have "so what?" interpretation
- Numbers match Phase 4/5 reports exactly
- All figures referenced before appearing
- Limitations are honest (not superficial)
- Broader impact statement included
- Claims are supported by evidence

### ❌ SYSTEM FAILURE:

- "Table 1 shows X" without interpretation
- Numbers don't match Phase 4/5 reports
- Figures not referenced in text
- No limitations acknowledged
- Claims without supporting evidence
- Copy-pasting from Phase 4/5 without synthesis
- Missing broader impact statement

**Master Rule:** Evidence sections must PROVE the claims. Every result needs interpretation. Every claim needs evidence.
