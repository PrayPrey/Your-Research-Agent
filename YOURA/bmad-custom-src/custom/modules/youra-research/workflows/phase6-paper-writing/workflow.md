---
name: "Phase 6: Paper Writing"
description: "Generate ICML-format academic paper with narrative-first architecture from Phase 0-5 research artifacts"
version: "2.0"
web_bundle: false
---

# Phase 6: Paper Writing

> **Pipeline Position:** Phase 5 (Baseline Comparison) -> **[Phase 6: Paper Writing]** -> Phase 6.5 (Adversarial Review)
> **Principle:** "Narrative-First Architecture: Design the story BEFORE writing sections"
> **Mode:** UNATTENDED (Fully Automatic)

**Goal:** Transform all research pipeline artifacts (Phase 0-5) into a publication-ready ICML-format academic paper by first designing the narrative structure, then generating sections in story-coherent groups.

**Your Role:** You are a seasoned researcher who has published at top ML venues and served as an area chair. You know that a great paper is an argument, not a data dump. You have taste — you know which results belong in the main text and which go in the appendix, which numbers sharpen the story and which clutter it. Write like a human who cares about the reader's experience, not like a system filling templates. When you catch yourself listing metrics mechanically, stop and rewrite as prose a colleague would actually want to read.

---

## Overview

This workflow generates an ICML 2025 format academic paper by:

1. **Initializing** - Create folder structure, collect figures from Phase 4/5
2. **Designing** - **Design the narrative structure BEFORE generating sections**
3. **Generating** - Sections in **story groups** with shared context
4. **Compiling** - References with citation verification
5. **Merging** - Final assembly with ground truth extraction for Phase 6.5

### Why Narrative-First?

**The Old Way:**
```
Abstract → Introduction → Related Work → ... → Conclusion
           ↑ No awareness of what comes later
           ↑ No narrative coherence
           ↑ Generic openings ("X is important")
```

**The New Way:**
```
Narrative Blueprint → Story Groups → Abstract LAST
           ↑ Design the story first
           ↑ Sections know their role in the narrative
           ↑ Hook-based openings ("Neural networks routinely fail...")
           ↑ Conclusion callbacks to Introduction hook
```

### Why Story Groups?

| Problem with Isolated Sections | Solution with Story Groups |
|--------------------------------|---------------------------|
| Each section written in isolation | Related sections share context |
| No narrative flow between sections | Story groups have coherent arcs |
| Results don't connect to Introduction claims | Evidence group proves Foundation claims |
| Abstract written without knowing results | Closure group written with full awareness |

---

## Story Group Architecture

### The Three Story Groups

| Group | Sections | Narrative Role | Context |
|-------|----------|----------------|---------|
| **Group A: Foundation** | Introduction, Related Work, Methodology | Hook → Problem → Insight → Solution | Shared |
| **Group B: Evidence** | Experiments, Results, Discussion | Test design → Evidence → Interpretation | Shared |
| **Group C: Closure** | Conclusion, Abstract | Callback to hook → Compress full story | Full paper context |

### Narrative Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ NARRATIVE BLUEPRINT │
│ (Designed in Step 02 BEFORE any section generation) │
│ │
│ Hook Strategy: "What surprising fact grabs attention?" │
│ Problem Levels: "What problem at 3 levels of detail?" │
│ Key Insight: "What 'aha' moment is the core contribution?" │
│ Evidence Story: "How do experiments prove the insight?" │
│ Takeaway: "What should reader remember?" │
└─────────────────────────────────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │ │                   │
           ▼ ▼                   ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │ STORY GROUP A │ │ STORY GROUP B │ │ STORY GROUP C │
   │ (Foundation) │ │   (Evidence) │   │ (Closure) │
   │ │   │ │   │ │
   │ • Introduction│ │ • Experiments │ │ • Conclusion │
   │ (Hook→ │   │ (Test design)│ │   (Callback │
   │ Problem) │   │ │   │ to hook) │
   │ │   │ • Results │   │ │
   │ • Related Work│ │   (Evidence) │   │ • Abstract │
   │ (Position) │   │ │   │ (Compress │
   │ │   │ • Discussion │   │ full story)│
   │ • Methodology │ │   (Interpret) │ │               │
   │ (Solution) │   │ │   │ [GENERATED │
   │ │   │ │   │ LAST!] │
   └───────────────┘ └───────────────┘ └───────────────┘
```

---

## Workflow Steps

| Step | Name | Purpose | Output |
|------|------|---------|--------|
| **1** | Initialize | Create folders, collect figures | `figure_registry.yaml` |
| **2** | Narrative Design | Design story structure BEFORE sections | `06_narrative_blueprint.yaml` |
| **3** | Story Group A | Introduction + Related Work + Methodology | `01-03_*.md` |
| **4** | Story Group B | Experiments + Results + Discussion | `04-06_*.md` |
| **5** | Story Group C | Conclusion + **Abstract (LAST)** | `07_conclusion.md`, `00_abstract.md` |
| **6** | References | Compile and verify citations | `06_references.bib` |
| **7** | Finalize | Merge, coherence check, ground truth extraction | `06_paper.md`, `065_ground_truth.yaml` |

### Execution Types

| Type | Steps | Description |
|------|-------|-------------|
| **Main Session** | 1, 2, 6, 7 | Run in main conversation context |
| **Task Agent** | 3, 4, 5 | Run in isolated Task Agent context |

### Step Details

#### Step 1: Initialize
- Create `paper/`, `sections/`, `figures/` folders
- Collect figures from Phase 4/5 outputs
- Create `figure_registry.yaml` with figure metadata
- Initialize `06_paper_checkpoint.yaml`

#### Step 2: Narrative Design
- Design the paper's story structure
- Define: hook, problem levels, key insight, evidence story, takeaway
- Output: `06_narrative_blueprint.yaml`
- **CRITICAL:** This step MUST complete before any section generation

#### Step 3: Story Group A (Foundation)
- Generate Introduction, Related Work, Methodology
- Sections share context and narrative awareness
- Follow narrative blueprint structure
- Avoid generic openings ("X is important...")

#### Step 4: Story Group B (Evidence)
- Generate Experiments, Results, Discussion
- Each result has "so what?" interpretation
- Connect evidence to claims from Introduction

#### Step 5: Story Group C (Closure)
- Generate Conclusion FIRST (callbacks to Introduction hook)
- Generate Abstract LAST (compresses full story)
- **CRITICAL:** Requires full paper context

#### Step 6: References
- Extract all citations from sections
- Verify with Semantic Scholar MCP
- Generate `06_references.bib`

#### Step 7: Finalize
- Merge all sections into `06_paper.md`
- Cross-section coherence check
- **Extract ground truth** for Phase 6.5 adversarial review
- Output: `065_ground_truth.yaml`

---

## ICML 2025 Format Requirements

| Requirement | Specification |
|-------------|---------------|
| **Main Paper** | 8 pages maximum |
| **Abstract** | Single paragraph, ~150 words |
| **Heading Levels** | Maximum 3 levels |
| **Impact Statement** | Required, in Discussion section |
| **References** | Unlimited pages |
| **Appendix** | Unlimited pages (same PDF) |

---

## Paper Section Structure

| Section | Guideline | Focus |
|---------|-----------|-------|
| Abstract | ~150 words | Compress full story (written LAST) |
| Introduction | ~800-1000 words | Hook → Problem → Contributions |
| Related Work | ~600-800 words | Position work, avoid survey |
| Methodology | ~1000-1200 words | Key insight explanation |
| Experiments | ~800-1000 words | Test design for each claim |
| Results | ~1000-1200 words | Evidence + "so what?" |
| Discussion | ~400-600 words | Limitations + Impact Statement |
| Conclusion | ~300-400 words | Callback to hook + future vision |

**Note:** These are guidelines, not strict limits. Focus on narrative quality over word count.

---

## Output Specifications

### Output Folder Structure

```
{research_folder}/paper/
├── 06_paper.md # Final merged paper
├── 06_paper_checkpoint.yaml # Progress tracking
├── 06_references.bib # BibTeX references
├── 06_narrative_blueprint.yaml
├── 065_ground_truth.yaml
├── figure_registry.yaml # Figure metadata
├── sections/ # Individual section files
│ ├── 00_abstract.md # Generated LAST
│ ├── 01_introduction.md
│ ├── 02_related_work.md
│ ├── 03_methodology.md
│ ├── 04_experiments.md
│ ├── 05_results.md
│ ├── 06_discussion.md
│ └── 07_conclusion.md
└── figures/ # Collected from Phase 4/5
    └── *.png, *.pdf
```

### Primary Outputs

**`06_paper.md`** - Complete ICML-format paper containing:
- YAML frontmatter with metadata
- All sections merged with narrative coherence
- Hook-based Introduction opening
- Conclusion that callbacks to Introduction
- Abstract that tells the story concisely (written LAST)

**`06_narrative_blueprint.yaml`** - Story design containing:
- Hook strategy and implementation
- Problem framing at 3 levels
- Key insight (aha moment)
- Evidence narrative structure
- Takeaway message

**`065_ground_truth.yaml`** - Ground truth for Phase 6.5:
- Actual metric values from Phase 4/5
- Claimed vs actual comparison table
- Hyperparameters from implementation
- Baseline comparison data

**Note:** Overleaf LaTeX generation moved to Phase 6.5.1 (after adversarial review).

---

## MCP Server Requirements

### Required MCPs

| MCP | Purpose | Used In |
|-----|---------|---------|
| **Semantic Scholar** | Citation verification, paper metadata | Step 3 (Related Work), Step 6 |
| **Serena** | Code structure analysis, figure discovery | Step 1, 4 |

### Recommended MCPs

| MCP | Purpose | Used In |
|-----|---------|---------|
| **Archon** | Knowledge base search | Step 3 (Related Work) |

---

## Input Artifacts Mapping

| Phase | Artifact | Usage in Paper |
|-------|----------|----------------|
| **Phase 0** | `00_brainstorm_session.md` | Introduction (motivation) |
| **Phase 1** | `01_targeted_research.md` | Related Work, Introduction |
| **Phase 2A** | `03_refinement.yaml`, `02_synthesis.yaml` | Introduction (original hypothesis context) |
| **Phase 4.5** | `045_validated_hypothesis.md` | Introduction (refined claims), Results, Discussion, Conclusion (future work) |
| **Phase 2B** | `02b_verification_plan.md` | Methodology (approach) |
| **Phase 2C** | `02c_experiment_brief.md` | Methodology, Experiments |
| **Phase 3** | `03_prd.md`, `03_architecture.md` | Methodology (algorithm), Experiments |
| **Phase 4** | `04_validation.md` | Results, Discussion, Ground Truth |
| **Phase 5** | `05_baseline_comparison.md` | Results, Ground Truth |
| **State** | `verification_state.yaml` | All (status tracking) |

---

## Citation Verification Process

### Using Semantic Scholar MCP

For each citation in the paper:

1. **Extract** paper title or DOI from source artifact
2. **Search** using `paper_relevance_search` or `paper_details`
3. **Verify** paper exists and metadata matches
4. **Record** paperId, title, authors, year, venue, citationCount
5. **Generate** BibTeX entry for `06_references.bib`

### Verification Levels

| Level | Criteria | Action |
|-------|----------|--------|
| **VERIFIED** | Found in Scholar, metadata matches | Include with confidence |
| **PARTIAL** | Found but metadata differs | Include with note |
| **UNVERIFIED** | Not found in Scholar | Mark as [UNVERIFIED] |

---

## Narrative Blueprint Structure

The narrative blueprint (`06_narrative_blueprint.yaml`) defines:

### Hook Strategy
```yaml
hook:
  strategy: "counterintuitive_finding" # or "surprising_statistic", "common_assumption_wrong"
  opening_statement: "Neural networks routinely fail on 35% of inputs..."
  avoid: "X is important" generic openings
```

### Problem Framing (3 Levels)
```yaml
problem:
  level_1_big_picture: "AI systems deployed in production must be reliable"
  level_2_technical: "Group robustness requires identifying which samples fail"
  level_3_specific_gap: "Existing methods require expensive group annotations"
```

### Key Insight
```yaml
key_insight:
  aha_moment: "Learning speed reveals group membership without annotations"
  explanation: "Spurious correlation samples are learned faster than core feature samples"
  evidence_preview: "CV ratio reaches 36x separation between groups"
```

### Section Goals
```yaml
section_goals:
  introduction:
    hook_implementation: "Open with the 35% failure rate statistic"
    contributions: ["Method", "Theory", "Empirical validation"]
  conclusion:
    callback_to_hook: "Return to the 35% failure rate, now solved"
    memorable_ending: "Vision for deployment-ready robustness"
```

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Narrative-First**: Design the story BEFORE writing sections
- **Story Group Cohesion**: Related sections share context
- **Closure-Last**: Abstract written LAST with full paper awareness
- **Ground Truth Extraction**: Prepare data for Phase 6.5 verification

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **DESIGN FIRST**: Step 2 (Narrative Blueprint) MUST complete before section generation
4. **SHARE CONTEXT**: Sections within story groups share narrative context
5. **SAVE STATE**: Update checkpoint file before loading next step
6. **EXTRACT TRUTH**: Step 7 extracts ground truth for Phase 6.5

### Critical Rules (NO EXCEPTIONS)

- NEVER skip the Narrative Blueprint step (Step 2)
- ALWAYS generate Abstract and Conclusion LAST (Step 5)
- NEVER use generic openings like "X is important"
- ALWAYS ensure Conclusion callbacks to Introduction hook
- ALWAYS extract ground truth in Step 7

---

## Session Resume Detection

**Check for existing checkpoint at** `{research_folder}/paper/06_paper_checkpoint.yaml`:

| Condition | Action |
|-----------|--------|
| Checkpoint exists AND `current_step > 1` | Resume from that step |
| Checkpoint does not exist | Start fresh from Step 1 |

---

## Error Handling

### Recoverable Errors

| Error | Recovery Action |
|-------|-----------------|
| Artifact missing | Use available artifacts, note limitation |
| Citation not found | Mark as [UNVERIFIED], continue |
| MCP timeout | Retry with backoff |

### Fatal Errors

| Error | Action |
|-------|--------|
| No Phase 4 validation | Stop, require PoC completion |
| verification_state.yaml missing | Stop, require Phase 2B completion |

---

## File Structure

| Path | Description |
|------|-------------|
| `workflow.md` | This file |
| `workflow.yaml` | Configuration with settings |
| `checklist.md` | Quality checklist |
| `steps/_common-rules.md` | Shared rules for all step files |
| `steps/step-01-init.md` | Initialize folders, collect figures |
| `steps/step-02-narrative-design.md` | **Design story structure** |
| `steps/step-03-story-group-a.md` | **Foundation sections** |
| `steps/step-04-evidence-group-b.md` | **Evidence sections** |
| `steps/step-05-conclusion-abstract.md` | **Closure sections (LAST)** |
| `steps/step-06-references.md` | Compile and verify citations |
| `steps/step-07-finalize.md` | Final merge, ground truth extraction |
| `templates/06_narrative_blueprint_template.yaml` | **Narrative design template** |
| `templates/06_paper_checkpoint_template.yaml` | Checkpoint template |

---

## Related Workflows

| Workflow | Relationship |
|----------|--------------|
| `phase5-baseline-repo-comparison` | Input: baseline comparison results |
| `phase4-coding` | Input: validation results |
| `phase65-adversarial-review` | **Output: paper goes here for review** |
| `full-pipeline-unattended` | Parent orchestrator |

---

## Quick Start

```bash
# Run paper generation for completed research
/phase6-paper-writing

# Or as part of full pipeline
/full-pipeline-complete
```

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:

- `research_output_path`, `research_folder`

### 2. Session Resume Detection

Check for existing checkpoint at `{research_folder}/paper/06_paper_checkpoint.yaml`:

- If exists and `current_step > 1`: Resume from that step
- If not exists: Start fresh from Step 1

### 3. Execution Flow

Refer to `workflow.yaml` for execution configuration:
- Step 1: Initialize (Main Session)
- Step 2: Narrative Design (Main Session) - **MUST complete before sections**
- Steps 3-5: Story Groups (Task Agents with shared context)
- Steps 6-7: References and Finalize (Main Session)

### 4. First Step

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
