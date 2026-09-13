---
name: 'step-03-story-group-a'
description: 'Generate Introduction, Related Work, and Methodology with shared narrative context'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-03-story-group-a.md'
nextStepFile: '{workflow_path}/steps/step-04-evidence-group-b.md'
workflowFile: '{workflow_path}/workflow.md'
narrativeBlueprint: '{paper_folder}/06_narrative_blueprint.yaml'
---

# Step 03: Story Group A - Foundation Sections

> **Step Position:** Step 1 (Init) -> Step 2 (Narrative Design) -> **[Step 3: Story Group A]** -> Step 4: Story Group B
> **Purpose:** Generate Introduction, Related Work, and Methodology in shared context for narrative coherence
> **Context Isolation:** NO - Sections share context within group
> **Execution Mode:** Task Agent with context sharing
> **Outputs:** `01_introduction.md`, `02_related_work.md`, `03_methodology.md`

---

## Why Story Groups?

**The Problem with Isolated Section Generation:**
```
Old approach:
  Each section generated → Fresh context → No awareness of other sections

Result:
  ❌ Disconnected narrative
  ❌ Redundant content between sections
  ❌ Inconsistent terminology
  ❌ No smooth transitions
```

**The Story Group Approach:**
```
New approach:
  Related sections generated → Shared context → Narrative coherence

Result:
  ✅ Unified narrative arc
  ✅ Natural transitions
  ✅ Consistent terminology
  ✅ Each section builds on previous
```

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:

- 🎯 Follow narrative blueprint from Step 02
- 🔄 Maintain shared context across all three sections
- 💬 Focus on "WHY" not just "WHAT"
- 📋 Create smooth transitions between sections
- 🚫 FORBIDDEN to use generic openings ("X is important...")

---

## Prerequisites

Before executing this step:

1. Step 01 (Init) completed successfully
2. Step 02 (Narrative Design) completed
3. `06_narrative_blueprint.yaml` exists
4. Required Phase 0-5 artifacts verified

---

## Task Agent Spawn Instructions

This step is executed as a **Task Agent** with the following parameters:

```yaml
task_agent:
  type: "general-purpose"
  context_isolation: false # CRITICAL: Sections share context

  inputs_to_load:
    - "{paper_folder}/06_narrative_blueprint.yaml"
    - "{research_folder}/045_validated_hypothesis.md"
    - "{research_folder}/00_brainstorm_session.md"
    - "{research_folder}/01_targeted_research.md"
    - "{research_folder}/01_targeted_research_full.md" # For citations
    - "{research_folder}/03_refinement.yaml"
    - "{research_folder}/02_synthesis.yaml"
    - "{hypothesis_folder}/02c_experiment_brief.md"
    - "{hypothesis_folder}/03_architecture.md"

  outputs_to_write:
    - "{sections_folder}/01_introduction.md"
    - "{sections_folder}/02_related_work.md"
    - "{sections_folder}/03_methodology.md"

  mcp_servers:
    - semantic_scholar # For citation verification
    - archon # For knowledge base search
    - serena # For code structure analysis
```

---

## Execution Sequence

### 1. Load Narrative Blueprint

```yaml
action: "Load narrative design from Step 02"
file: "{paper_folder}/06_narrative_blueprint.yaml"
extract:
  - hook.opening_statement
  - hook.why_reader_should_care
  - problem_framing (all three levels)
  - key_insight (aha_moment, why_others_missed_it)
  - section_goals.introduction
  - section_goals.related_work
  - section_goals.methodology
```

**The blueprint guides ALL section generation. Do not deviate from the designed narrative.**

---

### 2. Load Source Artifacts

Load ALL required artifacts to maintain context:

```yaml
artifacts_to_load:
  # Phase 0: Original motivation
  - file: "{research_folder}/00_brainstorm_session.md"
    use_for: "Introduction hook, problem motivation"

  # Phase 1: Research context
  - file: "{research_folder}/01_targeted_research.md"
    use_for: "Related work citations, research landscape"

  - file: "{research_folder}/01_targeted_research_full.md"
    use_for: "Full citation information for Related Work"

  # Phase 4.5: Validated hypothesis synthesis
  - file: "{research_folder}/045_validated_hypothesis.md"
    use_for: "Refined claims, verified key insight, strongest claims, theoretical contributions"

  # Phase 2A: Hypothesis
  - file: "{research_folder}/03_refinement.yaml"
    use_for: "Original hypothesis context, variables, methodology overview"

  - file: "{research_folder}/02_synthesis.yaml"
    use_for: "Research positioning, gap analysis"

  # Phase 2C: Experiment design
  - file: "{hypothesis_folder}/02c_experiment_brief.md"
    use_for: "Methodology details"

  # Phase 3: Architecture
  - file: "{hypothesis_folder}/03_architecture.md"
    use_for: "Method implementation details"
```

---

### 3. Generate Introduction (01_introduction.md)

The Introduction sets up the entire paper narrative. Follow the blueprint's `section_goals.introduction`.

#### 3.1 Opening Hook

**DO NOT** start with generic phrases. Use the designed hook from the blueprint.

```markdown
# AVOID
❌ "Deep learning has achieved remarkable success..."
❌ "X is an important problem in the field of Y..."
❌ "With the advent of large language models..."

# PREFER (from blueprint)
✅ [Use hook.opening_statement.content]
✅ Specific, concrete, attention-grabbing
```

**Template:**
```markdown
## Introduction

[Opening hook from blueprint - specific, concrete, attention-grabbing]

[Connect to why_reader_should_care - what's at stake?]
```

#### 3.2 Problem Escalation

Build up the problem in three levels (from `problem_framing`):

```markdown
[Level 1: Surface problem - what everyone knows]

[Level 2: Deeper problem - our framing / what we discovered]

[Level 3: Gap - the opportunity we address]
```

#### 3.3 Key Insight Preview

Introduce the key insight without full technical details:

```markdown
[One sentence capturing the core insight]

[Why this insight enables a solution - intuitive explanation]
```

#### 3.4 Contributions

**NOT a bullet list dump.** Frame as a coherent narrative:

```markdown
Building on this insight, we make the following contributions:
[Frame contributions as natural outcomes of the insight]
```

#### 3.5 Paper Organization (Optional)

If space allows, briefly mention paper organization:

```markdown
We organize the paper as follows: Section 2 discusses related work...
```

#### 3.6 Introduction Quality Checklist

Before proceeding:
- [ ] Hook is NOT generic
- [ ] Problem is framed in three levels
- [ ] Key insight is clearly previewed
- [ ] Contributions follow from the insight
- [ ] Reader would want to continue reading

---

### 4. Generate Related Work (02_related_work.md)

Related Work justifies our approach by showing existing work is insufficient.

#### 4.1 Positioning Strategy

From `section_goals.related_work.positioning_strategy`:
```
NOT just listing papers - building an argument
```

#### 4.2 Structure by Comparison Points

Use `section_goals.related_work.key_comparison_points`:

```markdown
## Related Work

### [Area 1: e.g., Spurious Correlation Detection]

[Discuss relevant papers]
[Highlight limitation_to_highlight]
[Transition: "However, these methods require..."]

### [Area 2: e.g., Learning Dynamics Analysis]

[Discuss relevant papers]
[Highlight limitation_to_highlight]
[Transition: "While informative, this line of work..."]

### [Our Position]

[Summarize how our approach differs]
[Connect back to key insight]
```

#### 4.3 Citation Verification

**CRITICAL:** Verify all citations using Semantic Scholar MCP:

```yaml
citation_verification:
  tool: "semantic_scholar"
  actions:
    - "paper_title_search" - Verify paper exists
    - "paper_details" - Get correct year, authors, venue

  format:
    in_text: "[Author et al., Year]"
    must_match: "BibTeX entry in references"
```

**Do NOT hallucinate citations.** If unsure, use MCP to verify or mark as `[CITATION NEEDED]`.

#### 4.4 Related Work Quality Checklist

Before proceeding:
- [ ] Organized by themes, not random listing
- [ ] Each theme shows limitation we address
- [ ] All citations verified via MCP
- [ ] Fair to prior work (not dismissive)
- [ ] Clear positioning of our approach

---

### 5. Generate Methodology (03_methodology.md)

Methodology explains WHY this design solves the problem, not just WHAT it does.

#### 5.1 Connection to Key Insight

From `section_goals.methodology.connection_to_insight`:

```markdown
## Methodology

### Overview

[Connect to key insight - "Building on our observation that X, we design..."]

[High-level approach description]
```

#### 5.2 Method Details with Rationale

From `section_goals.methodology.key_design_decisions`:

```markdown
### [Component 1 Name]

[What this component does]
**Rationale:** [WHY this design choice - connect to problem]
[Technical details]

### [Component 2 Name]

[What this component does]
**Rationale:** [WHY this design choice]
[Technical details]
```

#### 5.3 Algorithm Description

If applicable, include algorithm pseudocode:

```markdown
### Algorithm

**Algorithm 1:** [Name]
```
[Pseudocode or step-by-step description]
```

**Complexity Analysis:** [Brief discussion if relevant]
```

#### 5.4 Code Analysis (via Serena MCP)

Use Serena MCP to analyze actual implementation:

```yaml
serena_analysis:
  tool: "serena"
  actions:
    - "get_symbols_overview" - Understand code structure
    - "find_symbol" - Find specific implementations
    - "search_for_pattern" - Find key algorithms

  use_for:
    - Verify methodology matches implementation
    - Extract accurate technical details
    - Get correct hyperparameter values
```

#### 5.5 Methodology Quality Checklist

Before completing:
- [ ] WHY each design choice is explained
- [ ] Connected to key insight
- [ ] Technical details match implementation
- [ ] Figures (if any) are referenced
- [ ] Reader can understand AND replicate

---

### 6. Ensure Narrative Coherence

After generating all three sections, verify coherence:

#### 6.1 Transition Check

| From Section | To Section | Transition Quality |
|--------------|------------|-------------------|
| Introduction | Related Work | Flows naturally? |
| Related Work | Methodology | Gap → Solution clear? |

#### 6.2 Terminology Consistency

```yaml
check:
  - "Key terms defined consistently"
  - "No conflicting definitions"
  - "Same notation throughout"
```

#### 6.3 Narrative Arc

```yaml
verify:
  - "Introduction hook sets up the story"
  - "Related Work shows why existing work insufficient"
  - "Methodology presents solution as natural response"
```

---

### 7. Write Section Files

Write each section to its output file:

```yaml
outputs:
  - file: "{sections_folder}/01_introduction.md"
    content: "[Generated Introduction]"

  - file: "{sections_folder}/02_related_work.md"
    content: "[Generated Related Work]"

  - file: "{sections_folder}/03_methodology.md"
    content: "[Generated Methodology]"
```

---

### 8. Update Checkpoint

Update `06_paper_checkpoint.yaml`:

```yaml
current_step: 4
story_groups:
  group_a:
    status: "complete"
    sections:
      - introduction: "complete"
      - related_work: "complete"
      - methodology: "complete"
    completed_at: "{ISO8601}"
updated_at: "{ISO8601}"
```

---

### 9. Return to Orchestrator

After completing, return summary:

```yaml
agent: "story-group-a"
status: "COMPLETED"
outputs:
  - "01_introduction.md"
  - "02_related_work.md"
  - "03_methodology.md"

summary:
  introduction:
    word_count: {N}
    hook_type: "{strategy from blueprint}"
    contributions_count: {N}

  related_work:
    word_count: {N}
    themes_discussed: {N}
    citations_count: {N}
    citations_verified: {N}

  methodology:
    word_count: {N}
    components_described: {N}
    figures_referenced: {N}

narrative_coherence:
  transitions_smooth: true/false
  terminology_consistent: true/false
  follows_blueprint: true/false
```

---

### 10. Proceed to Next Step

**NEXT:** Load, read the full file, and execute `{nextStepFile}`

---

## Output Summary

| Output | Path | Description |
|--------|------|-------------|
| Introduction | `{sections_folder}/01_introduction.md` | Hook + Problem + Insight + Contributions |
| Related Work | `{sections_folder}/02_related_work.md` | Positioned prior work with verified citations |
| Methodology | `{sections_folder}/03_methodology.md` | WHY-focused method description |
| Updated Checkpoint | `{paper_folder}/06_paper_checkpoint.yaml` | Progress tracking |

---

## 🚨 SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Narrative blueprint loaded and followed
- Introduction has non-generic hook
- Problem framed in three levels
- Key insight clearly articulated
- Related work organized by themes (not random listing)
- All citations verified via Semantic Scholar MCP
- Methodology explains WHY, not just WHAT
- Smooth transitions between all sections
- Consistent terminology throughout
- All three section files written

### ❌ SYSTEM FAILURE:

- Generic opening ("X is important...")
- Citations not verified (hallucinated references)
- Related work is just paper listing
- Methodology only describes WHAT, not WHY
- No connection to narrative blueprint
- Disconnected sections with no transitions
- Missing section files

**Master Rule:** This step generates FOUNDATION sections that set up the paper's story. They must be coherent and follow the narrative blueprint.
