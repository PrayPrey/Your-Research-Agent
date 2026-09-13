---
name: 'step-02-narrative-design'
description: 'Design the paper narrative structure before any section generation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-02-narrative-design.md'
nextStepFile: '{workflow_path}/steps/step-03-story-group-a.md'
workflowFile: '{workflow_path}/workflow.md'
blueprintTemplate: '{workflow_path}/templates/06_narrative_blueprint_template.yaml'
---

# Step 02: Narrative Design

> **Step Position:** Step 1 (Init) -> **[Step 2: Narrative Design]** -> Step 3: Story Group A
> **Purpose:** Design the paper's story structure BEFORE generating any sections
> **Context Isolation:** NO - Requires broad context from Phase 0-5 artifacts
> **Output:** `06_narrative_blueprint.yaml`

---

## Why This Step Exists

**The Problem with Direct Section Generation:**
```
Old approach:
  Phase 0-5 artifacts → Extract facts → Fill templates → Sections

Result:
  ❌ Disconnected sections
  ❌ No narrative flow
  ❌ "What" without "Why"
  ❌ Technical report, not academic paper
```

**The Narrative-First Approach:**
```
New approach:
  Phase 0-5 artifacts → Design story → Generate sections following story

Result:
  ✅ Coherent narrative arc
  ✅ Each section serves the story
  ✅ "Why" drives "What"
  ✅ Academic paper that engages readers
```

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Focus on STORY DESIGN, not content generation
- 🚫 FORBIDDEN to write actual paper sections in this step
- 💬 Think like a storyteller, not a technical writer
- 📋 Output is a blueprint that guides subsequent steps

---

## Prerequisites

Before executing this step:

1. Step 01 (Init) completed successfully
2. Figure registry created
3. Required artifacts verified

---

## Execution Sequence

### 1. Load Source Artifacts

Load ALL relevant Phase 0-5 artifacts to understand the full research story:

```yaml
required_artifacts:
  # Phase 0: Original motivation
  - file: "{research_folder}/00_brainstorm_session.md"
    extract:
      - "original_research_question"
      - "user_motivation"
      - "initial_problem_framing"
    purpose: "Understand WHY this research was started"

  # Phase 1: Research context
  - file: "{research_folder}/01_targeted_research.md"
    extract:
      - "key_findings_from_literature"
      - "identified_gaps"
      - "relevant_prior_work"
    purpose: "Understand the research landscape"

  # Phase 2A: Hypothesis formulation
  - file: "{research_folder}/03_refinement.yaml"
    extract:
      - "core_hypothesis"
      - "expected_contributions"
      - "methodology_overview"
      - "variables" # IV, DV, CV
      - "h0_statement" # Null hypothesis
    purpose: "Understand our ORIGINAL central claim and experimental design"

  # Phase 2B: Verification design
  - file: "{research_folder}/02b_verification_plan.md"
    extract:
      - "verification_approach"
      - "success_criteria"
    purpose: "Understand how we test our claims"

  # Phase 4.5: Validated hypothesis synthesis
  - file: "{research_folder}/045_validated_hypothesis.md"
    extract:
      - "refined_core_statement" # Section 3.2 — experiment-verified claim
      - "prediction_result_matrix" # Section 2 — P1/P2/P3 status
      - "theoretical_interpretation" # Section 4 — mechanistic explanation
      - "unexpected_findings_analysis" # Section 4.2 — competing explanations
      - "limitations_and_scope" # Section 6 — principled limitations
      - "future_work_directions" # Section 7 — results-grounded
      - "recommended_narrative_hook" # Section 8.1 — suggested hook
      - "verified_key_insight" # Section 8.2 — experiment-verified insight
      - "strongest_claims" # Section 8.3 — paper-ready claims
      - "honest_limitations" # Section 8.4 — must include in paper
      - "evidence_highlights" # Section 8.5 — most persuasive evidence
    purpose: "PRIMARY source for narrative design — experiment-verified claims and interpretation"

  # Phase 5: Baseline comparison (if exists)
  - file: "{hypothesis_folder}/baseline_comparison/05_baseline_comparison.md"
    extract:
      - "comparison_results"
      - "statistical_significance"
      - "relative_performance"
    purpose: "Understand how we compare to baselines"
```

**Action:** Read each artifact and extract key information.

---

### 2. Load Blueprint Template

```yaml
action: "Load narrative blueprint template"
file: "{workflow_path}/templates/06_narrative_blueprint_template.yaml"
purpose: "Get structure for narrative design"
```

---

### 3. Design the Hook

The opening of a paper determines whether reviewers continue reading.

#### 3.1 Analyze the Problem

Answer these questions from the artifacts:

| Question | Source | Answer |
|----------|--------|--------|
| What problem are we solving? | 00_brainstorm, 03_refinement.yaml | |
| Why does this problem matter? | 00_brainstorm | |
| What concrete failure does it cause? | 045_validated_hypothesis.md (Section 5) | |
| Who is affected by this problem? | 00_brainstorm | |

#### 3.2 Craft the Opening Strategy

Choose a hook strategy:

| Strategy | When to Use | Example Pattern |
|----------|-------------|-----------------|
| **Surprising Statistic** | When you have striking numbers | "Despite achieving X%, models still fail at Y" |
| **Counterintuitive Finding** | When result defies expectation | "Contrary to common belief, X actually..." |
| **Practical Failure** | When there's real-world impact | "In production systems, X causes Y failure in Z% of cases" |
| **Puzzle/Paradox** | When there's interesting tension | "Models can do X but mysteriously fail at simpler Y" |

**Write the hook:**

```yaml
hook:
  opening_statement:
    content: "[First sentence that grabs attention]"
    strategy: "[chosen_strategy]"

  why_reader_should_care:
    main_reason: "[Core reason this matters]"
    concrete_example: "[Specific example]"
    stakes: "[What happens if unsolved]"
```

#### 3.3 Anti-Patterns to AVOID

```
❌ BORING: "Deep learning has achieved remarkable success in recent years..."
❌ GENERIC: "X is an important problem in the field of Y..."
❌ BUZZWORD: "With the advent of large language models..."
❌ VAGUE: "Several challenges remain in this area..."

✅ ENGAGING: "A model that achieves 95% accuracy on benchmarks can fail 40% of the time when..."
✅ SPECIFIC: "Medical diagnosis systems misclassify 23% of minority-group patients..."
✅ CONCRETE: "When trained on biased data, even state-of-the-art models learn shortcuts that..."
```

---

### 4. Frame the Problem

Structure the problem in layers to show intellectual depth.

#### 4.1 Three-Level Problem Structure

```
┌─────────────────────────────────────────────┐
│ Level 1: SURFACE PROBLEM │
│ What everyone in the field knows │
│ "Spurious correlations hurt model fairness" │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Level 2: DEEPER PROBLEM │
│ What we emphasize / discovered │
│ "Existing detection methods need labels" │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Level 3: THE GAP │
│ The opportunity we address │
│ "No automatic, training-time intervention" │
└─────────────────────────────────────────────┘
```

#### 4.2 Fill the Problem Framing

From the artifacts, identify:

```yaml
problem_framing:
  surface_problem:
    description: "[Known problem statement]"
    common_understanding: "[What papers typically say]"

  deeper_problem:
    description: "[Our deeper framing]"
    why_overlooked: "[Why others missed this]"
    our_perspective: "[How we see it differently]"

  gap_in_existing_work:
    description: "[The specific gap]"
    why_gap_exists: "[Technical/conceptual reason]"
    why_gap_matters: "[Consequence of the gap]"
```

---

### 5. Articulate the Key Insight

This is the intellectual heart of the paper.

#### 5.1 Identify the "Aha!" Moment

From your research, what is the key insight that enables the solution?

| Insight Type | Description | Example |
|--------------|-------------|---------|
| **Observation-based** | We noticed something others missed | "Fast-learning samples signal spurious patterns" |
| **Connection-based** | We connected two separate ideas | "Learning dynamics + group fairness" |
| **Simplification** | Complex problem has simple core | "The key factor is just X" |
| **Inversion** | Opposite of conventional wisdom | "Instead of X, we should do Y" |

#### 5.2 Write the Insight

```yaml
key_insight:
  aha_moment:
    one_sentence: "[The insight in ONE sentence]"
    expanded_explanation: "[2-3 sentences elaborating]"

  why_others_missed_it:
    common_assumptions: "[What others assumed]"
    our_different_view: "[How we thought differently]"
    enabling_factor: "[What allowed us to see this]"

  what_makes_it_work:
    intuitive_explanation: "[For non-experts]"
    key_mechanism: "[Technical core]"
```

---

### 6. Design the Evidence Story

Results should tell a story, not just report numbers.

#### 6.1 Identify Main Claim

From 045_validated_hypothesis.md (Sections 2, 5, 8.3):

```yaml
evidence_narrative:
  main_claim:
    statement: "[What we're claiming]"
    measurable_criteria: "[How we prove it]"
```

#### 6.2 Structure Supporting Evidence

For each key result, define its role in the story:

```yaml
supporting_evidence:
  - id: "evidence_1"
    what: "[Result/finding]"
    so_what: "[Why it matters]"
    how_it_supports_claim: "[Connection to main claim]"
```

#### 6.3 Identify Surprising Findings

```yaml
surprising_findings:
  finding: "[What was unexpected]"
  why_surprising: "[Why it defied expectation]"
  our_interpretation: "[How we explain it]"
```

---

### 7. Define Broader Impact

Connect the work to larger context.

```yaml
takeaway:
  main_contribution:
    one_sentence: "[THE key contribution]"
    why_significant: "[Why it matters]"

  implications:
    for_field: "[Research community impact]"
    for_practice: "[Practitioner impact]"

  future_possibilities:
    immediate_extensions: "[Near-term follow-ups]"
    longer_term_vision: "[Where this could lead]"
```

---

### 8. Set Section-Level Goals

For each section, define its narrative purpose:

```yaml
section_goals:
  abstract:
    narrative_purpose: "Compress full story into ~150 words — prioritize storytelling over numerical detail"
    key_message: "[ONE thing reader should remember]"

  introduction:
    narrative_purpose: "Hook → Problem → Insight → Preview"
    hook_strategy: "[Chosen strategy from Step 3]"
    transition_to_related: "[How to connect to Related Work]"

  related_work:
    narrative_purpose: "Show existing work insufficient → justify our approach"
    positioning_strategy: "[How we position against prior work]"
    key_comparison_points: [...]

  methodology:
    narrative_purpose: "Show WHY this design solves the problem"
    connection_to_insight: "[How method follows from insight]"
    key_design_decisions: [...]

  experiments:
    narrative_purpose: "Design tests that verify our specific claims"
    experimental_questions: [...]

  results:
    narrative_purpose: "Present evidence supporting claims"
    main_result_highlight: "[THE key result]"

  discussion:
    narrative_purpose: "Interpret results, acknowledge limits"
    honest_limitations: [...]

  conclusion:
    narrative_purpose: "Reinforce message, open future"
    callback_to_hook: "[Close the narrative loop]"
```

---

### 9. Verify Narrative Coherence

Before finalizing, check:

```yaml
narrative_coherence_checklist:
  - check: "Does Introduction hook connect to Conclusion ending?"
    status: ""

  - check: "Does each section naturally flow to the next?"
    status: ""

  - check: "Is key insight consistently emphasized throughout?"
    status: ""

  - check: "Are all major claims supported by evidence?"
    status: ""

  - check: "Would a busy reviewer find Abstract compelling?"
    status: ""
```

---

### 10. Write Blueprint File

Write completed blueprint to:

```
{paper_folder}/06_narrative_blueprint.yaml
```

Include all sections filled from steps 3-9.

---

### 11. Update Checkpoint

Update `06_paper_checkpoint.yaml`:

```yaml
current_step: 3
narrative_design:
  status: "complete"
  blueprint_file: "06_narrative_blueprint.yaml"
  completed_at: "{ISO8601}"
updated_at: "{ISO8601}"
```

---

### 12. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

The blueprint will be used by:
- Step 03 (Story Group A): Introduction, Related Work, Methodology
- Step 04 (Evidence Group B): Experiments, Results, Discussion
- Step 05 (Conclusion & Abstract): Final sections with full context

---

## Output Summary

| Output | Path | Description |
|--------|------|-------------|
| Narrative Blueprint | `{paper_folder}/06_narrative_blueprint.yaml` | Complete story design |
| Updated Checkpoint | `{paper_folder}/06_paper_checkpoint.yaml` | Progress tracking |

---

## 🚨 SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All Phase 0-5 artifacts loaded and analyzed
- Hook designed with specific strategy (not generic opening)
- Problem framed in three levels (surface → deeper → gap)
- Key insight articulated clearly (one sentence)
- Evidence story structured (not just results listing)
- Section goals defined with narrative purpose
- Coherence checklist verified
- Blueprint file written

### ❌ SYSTEM FAILURE:

- Skipping artifact analysis
- Generic/boring hook ("X is important...")
- No clear key insight
- Sections without defined narrative purpose
- Evidence listed without "so what"
- Missing blueprint file

**Master Rule:** This step designs the STORY. Sections are generated in later steps following this blueprint. Do not write actual paper content here.
