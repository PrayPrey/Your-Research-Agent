---
name: "Phase 6.5: Adversarial Review"
description: "Multi-round adversarial review with three-persona system to detect accuracy issues AND improve persuasiveness"
version: "2.0"
web_bundle: false
---

# Phase 6.5: Adversarial Review

> **Pipeline Position:** Phase 6 (Paper Writing) -> **[Phase 6.5: Adversarial Review]** -> Phase 6.5.1 (Overleaf LaTeX/PDF)
> **Principle:** "Devil's Advocate review with role separation AND persuasiveness verification"
> **Mode:** UNATTENDED (Fully Automatic) or INTERACTIVE (User gate between rounds)
**Goal:** Systematically identify and resolve logical conflicts, numerical inconsistencies, methodology contradictions, AND ensure the paper is compelling and persuasive through multi-round adversarial review with specialized personas.

**Your Role:** In addition to your name, communication_style, and persona, you are also an orchestrator of a three-persona adversarial system collaborating with a researcher. This is a partnership, not a client-vendor relationship. You bring adversarial review expertise, multi-agent coordination skills, and systematic validation methodology, while the user brings their research paper and domain knowledge. Work together as equals.

> **System Design:** The Adversary Agent uses THREE PERSONAS (accuracy_checker, bored_reviewer, skeptical_expert) to attack the paper from different angles, while the Revision Agent defends and improves the paper. This ensures both accuracy AND persuasiveness.

---

## Overview

This workflow implements a multi-round adversarial review process with THREE specialized personas:

### The Three Personas

| Persona | Role | Key Questions |
|---------|------|---------------|
| **Accuracy Checker** | Fact-checker and claim verifier | "Do the numbers match ground truth?" |
| **Bored Reviewer** | Busy NeurIPS reviewer with 5 papers today | "Would I continue reading?" |
| **Skeptical Expert** | Domain expert looking for holes | "Is this really novel? Are claims fair?" |

### Review Rounds

1. **Round 1 (R1)**: Accuracy + Engagement - All three personas
2. **Round 2 (R2)**: Verification + Credibility - Accuracy Checker + Skeptical Expert
3. **Round 3 (R3)**: Final Check - Bored Reviewer (if needed)

### Core Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Three-Persona Review** | Different angles: accuracy, engagement, credibility |
| **Role Separation** | Adversary (attack) ≠ Revision (fix) |
| **Context Isolation** | Each agent runs in fresh Task Agent context |
| **Evidence-Based** | All challenges must cite specific locations |
| **FATAL/MAJOR Only** | MINOR issues → human_review_notes (not auto-fixed) |
| **Persuasiveness-Aware** | Convergence requires "would continue reading" |

### Why Three Personas?

| Problem with Single Adversary | Solution with Three Personas |
|-------------------------------|------------------------------|
| Focuses only on accuracy | Bored Reviewer checks engagement |
| Misses "paper is boring" issue | "Would I continue reading?" check |
| Doesn't catch overclaims | Skeptical Expert looks for holes |
| Same review angle each round | Different perspectives each pass |

---

## Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 6.5 Orchestrator │
│ (Main workflow session) │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │ │                  │
        ▼ ▼                  ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Round 1 │ ───▶ │ Round 2 │ ───▶ │ Round 3 │
   │ (R1) │       │ (R2) │       │ (R3) │
   └────┬────┘ └────┬────┘ └────┬────┘
        │ │                 │
   ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
   │Adversary│ │Adversary│ │Adversary│
   │ (3 Personas) │ (2 Personas) │ (1 Persona)
   │ - accuracy │ - accuracy │ - bored
   │ - bored │ - skeptical │   reviewer
   │ - skeptical │                 │
   └────┬────┘ └────┬────┘ └────┬────┘
        │ │                 │
        ▼ ▼                 ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Review │       │ Review │       │ Review │
   │ Report │       │ Report │       │ Report │
   │+ persuasiveness │+ ground truth │+ final flow
   │ checks │      │ verification │  check │
   └────┬────┘ └────┬────┘ └────┬────┘
        │ │                 │
   [Gate: FATAL=0, [Gate: FATAL=0, [Gate: FATAL=0,
    MAJOR=0, MAJOR=0] MAJOR=0]
    persuasive?] │                 │
        │ │                 │
   ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
   │Revision │ │Revision │ │Revision │
   │ Agent │       │ Agent │       │ Agent │
   │(FATAL/MAJOR only) (FATAL/MAJOR only) (FATAL/MAJOR only)
   └────┬────┘ └────┬────┘ └────┬────┘
        │ │                 │
        ▼ ▼                 ▼
   paper_r1.md paper_r2.md paper_final.md
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Phase 6.5.1 │
                                    │ (Overleaf/PDF)│
                                    └───────────────┘
```

---

## Adversary Agent Personas

### Persona 1: Accuracy Checker

**Role:** Fact-checker and claim verifier

**Uses:**
- `065_ground_truth.yaml` (from Phase 6 Step 7)
- `04_validation.md` (Phase 4)
- `05_baseline_comparison.md` (Phase 5)

**Key Questions:**
- Do the reported numbers match ground truth?
- Is the methodology description accurate?
- Are baseline comparisons fair?
- Do the claims match the evidence?

### Persona 2: Bored Reviewer

**Role:** Busy NeurIPS reviewer with 5 papers to review today

**Uses:**
- `06_narrative_blueprint.yaml` (from Phase 6 Step 2)

**Key Questions:**
- Would I continue reading after the abstract?
- Is the problem clear in the first minute?
- Is the novelty clear in 2 minutes?
- Can I understand Figure 1 without reading the text?
- At what point did I lose attention?

**Persuasiveness Checks:**

| Check | Question | Pass | Fail |
|-------|----------|------|------|
| `abstract_compelling` | Would I continue reading? | Concrete results, clear contribution | Generic, no numbers |
| `problem_clear_in_1_minute` | Do I understand the problem quickly? | Concrete example, clear impact | Buried in jargon |
| `novelty_clear_in_2_minutes` | Do I understand what's new? | Clear "unlike prior work" statement | Hidden in related work |
| `figure_1_self_explanatory` | Can I understand Figure 1 alone? | Clear flow, labeled components | Requires full paper context |

### Persona 3: Skeptical Expert

**Role:** Domain expert looking for holes in claims

**Uses:**
- Section files (for detailed analysis)
- References file (for citation accuracy)

**Key Questions:**
- Is this really novel?
- Are the baselines fairly compared?
- Are there overclaims?
- What limitations are missing?
- Would I accept or reject this paper?

---

## Issue Severity Classification

| Severity | Definition | Examples | Required Action | Blocks Convergence? |
|----------|------------|----------|-----------------|---------------------|
| **FATAL** | Fundamental contradiction or impossible claim | "single-run" vs "2-stage retrain" reality | MUST fix or WITHDRAW | **YES** |
| **MAJOR** | Significant weakness attackable by reviewers | Unfair baseline, missing justification | MUST fix with evidence | **YES** |
| **~~MINOR~~** | ~~Polish issues~~ | ~~Typos, awkward phrasing~~ | ~~OPTIONAL fix~~ | ~~No~~ |

##

**MINOR issues are NO LONGER auto-fixed.** Instead, they are:

1. **Collected** in `065_human_review_notes.md`
2. **Categorized** by type (typo, grammar, style, clarity, formatting)
3. **Left for human review** after workflow completes

**Rationale:**
- AI auto-fixing style/grammar can introduce new errors
- Minor issues don't block acceptance
- Human can review and fix more carefully
- Reduces unnecessary paper churn

---

## Convergence Criteria

### Automatic Convergence (UNATTENDED mode)

```yaml
auto_converge:
  conditions:
    - fatal_issues == 0 # MUST be true
    - major_issues == 0
    - persuasiveness_passed == true
    - round_number >= 2 # Minimum 2 rounds

  force_stop:
    - max_rounds: 3
    - same_issues_repeated: 2 # Same issue found twice = needs human
```

### Convergence Recommendations

| Condition | Recommendation |
|-----------|----------------|
| FATAL=0, MAJOR=0, persuasive | `CONDITIONAL_ACCEPT` |
| FATAL=0, MAJOR>0 OR not persuasive | `MINOR_REVISION` |
| FATAL>0 | `MAJOR_REVISION` |

---

## WORKFLOW STEPS OVERVIEW

**Architecture**: Multi-Round with Three-Persona Adversary-Revision Agent Pairs

| Step | File | Name | Type | Output |
|------|------|------|------|--------|
| 1 of 7 | step-01-init.md | Initialize | Main | Checkpoint, ground truth loaded |
| 2 of 7 | step-02-adversary-r1.md | Adversary R1 | **Task Agent** (`adversary-agent-v2`) | 065_review_r1.md |
| 3 of 7 | step-03-revision-r1.md | Revision R1 | **Task Agent** (`revision-agent`) | 06_paper_r1.md |
| 4 of 7 | step-04-convergence.md | Convergence Check | Main | Decision: continue/stop |
| 5 of 7 | step-05-adversary-r2.md | Adversary R2 | **Task Agent** (`adversary-agent-v2`) | 065_review_r2.md |
| 6 of 7 | step-06-revision-r2.md | Revision R2 | **Task Agent** (`revision-agent`) | 06_paper_r2.md |
| 7 of 7 | step-07-finalize.md | **Finalize** | Main | 06_paper_final.md, review summary |

### Conditional Steps

- **Steps 5-6 (R2)**: Only if R1 convergence not met
- **R3**: Only if R2 convergence not met AND max_rounds=3

---

## INPUT REQUIREMENTS

### Required Inputs (from Phase 6)

| File | Description | Check |
|------|-------------|-------|
| `{research_folder}/paper/06_paper.md` | Paper to review | Must exist |
| `{research_folder}/paper/065_ground_truth.yaml` | Ground truth values for accuracy verification | Must exist |

### Recommended Inputs

| File | Description | Usage |
|------|-------------|-------|
| `{research_folder}/paper/06_narrative_blueprint.yaml` | Narrative blueprint | Persuasiveness checks |
| `{research_folder}/paper/sections/*.md` | Individual sections | Cross-reference |
| `{research_folder}/paper/06_references.bib` | Citations | Verify citation accuracy |

### Optional Inputs (for context)

| File | Description | Usage |
|------|-------------|-------|
| `{hypothesis_folder}/04_validation.md` | Phase 4 results | Cross-check reported numbers |
| `{hypothesis_folder}/baseline_comparison/` | Phase 5 results | Verify baseline claims |

---

## OUTPUT ARTIFACTS

### Per-Round Outputs

| Round | Adversary Output | Revision Output |
|-------|------------------|-----------------|
| R1 | `065_review_r1.md` | `06_paper_r1.md` |
| R2 | `065_review_r2.md` | `06_paper_r2.md` |
| R3 | `065_review_r3.md` | `06_paper_r3.md` |

### Final Outputs

| File | Description |
|------|-------------|
| `06_paper_final.md` | Reviewed and revised paper |
| `065_review_summary.md` | All issues found and resolution status |
| `065_changelog.md` | Detailed change log across rounds |
| `065_review_checkpoint.yaml` | Workflow state and progress |
| `065_human_review_notes.md` | **Minor issues for human review** |

### Output Folder Structure

```
{research_folder}/paper/
├── 06_paper.md # Original (Phase 6 output)
├── 06_paper_r1.md # After Round 1 revision
├── 06_paper_r2.md # After Round 2 revision
├── 06_paper_final.md # Final reviewed paper
├── 06_references.bib # References (may be updated)
├── 06_narrative_blueprint.yaml # Narrative design (from Phase 6)
├── 065_ground_truth.yaml # Ground truth (from Phase 6)
├── review/ # Review artifacts folder
│ ├── 065_review_r1.md # Adversary R1 report
│ ├── 065_review_r2.md # Adversary R2 report
│ ├── 065_review_summary.md # Consolidated summary
│ ├── 065_changelog.md # All changes made
│ ├── 065_review_checkpoint.yaml # State tracking
│ └── 065_human_review_notes.md
└── overleaf/ # Generated by Phase 6.5.1 (next phase)
```

**NOTE:** The `overleaf/` folder is generated by Phase 6.5.1 (Overleaf LaTeX/PDF), not Phase 6.5.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that you will adhere to, 1 file at a time as directed
- **Just-In-Time Loading**: Only 1 current step file will be loaded, read, and executed to completion - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in checkpoint file using `065_review_checkpoint.yaml`
- **Append-Only Building**: Build review reports and changelogs by appending content as directed to the output files
- **Round-Based Iteration**: R1 → R2 → R3 with convergence checks between rounds

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: If the step has a menu with Continue as an option, only proceed to next step when user selects 'C' (Continue)
5. **SAVE STATE**: Update `065_review_checkpoint.yaml` in checkpoint before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- NEVER load multiple step files simultaneously
- ALWAYS read entire step file before execution
- NEVER skip steps or optimize the sequence
- ALWAYS update checkpoint file when writing the final output for a specific step
- ALWAYS follow the exact instructions in the step file
- ALWAYS halt at menus and wait for user input (except in UNATTENDED mode)
- NEVER create mental todo lists from future steps

### Workflow-Specific Rules

- **NEVER** skip convergence checks between rounds
- **ALWAYS** update `065_review_checkpoint.yaml` when completing a step
- **ALWAYS** preserve original paper (`06_paper.md`) - create new versions only

---

## MCP Server Requirements

### Required MCPs

| MCP | Purpose | Used In |
|-----|---------|---------|
| **Serena** | Cross-reference Phase 4/5 actual results, verify code | Adversary R2 (numerical validation) |

### Recommended MCPs

| MCP | Purpose | Used In |
|-----|---------|---------|
| **Semantic Scholar** | Verify citation accuracy, check baseline reported values | Adversary R1/R2 |
| **ClearThought** | Structured argumentation for challenges | Adversary Agent |

### Optional MCPs

| MCP | Purpose | Used In |
|-----|---------|---------|
| **Archon** | Knowledge base for prior art check | Adversary R1 (novelty) |

---

## Session Resume Detection

**Check for existing checkpoint at** `{research_folder}/paper/review/065_review_checkpoint.yaml`:

| Condition | Action |
|-----------|--------|
| Checkpoint exists AND `current_round > 0` | Resume from that round |
| Checkpoint exists AND `status == CONVERGED` | Skip to finalize |
| Checkpoint does not exist | Start fresh from Step 1 |

---

## Error Handling

### Recoverable Errors

| Error | Recovery Action |
|-------|-----------------|
| Adversary finds no issues | Log as clean, proceed to next round or finalize |
| Revision cannot fix FATAL | Flag for manual review, continue with others |
| Round timeout | Save state, allow resume |
| Missing ground truth | Warn, continue with limited accuracy checks |
| Missing narrative blueprint | Warn, continue with limited persuasiveness checks |

### Fatal Errors

| Error | Action |
|-------|--------|
| Paper file missing | Stop, require Phase 6 completion |
| 3 rounds completed, still FATAL issues | Stop, require manual intervention |

---

## File Structure

| Path | Description |
|------|-------------|
| `workflow.md` | This file |
| `workflow.yaml` | Configuration with settings |
| `agents/adversary-agent-v2.md` | **Three-persona Adversary Agent** |
| `agents/revision-agent.md` | Revision Agent definition |
| `steps/step-*.md` | Step instruction files (01-07) |
| `templates/065_review_checkpoint_template.yaml` | **Updated checkpoint template** |

---

## Related Workflows

| Workflow | Relationship |
|----------|--------------|
| `phase6-paper-writing` | Input: generates paper, narrative blueprint, ground truth |
| `full-pipeline-unattended` | Parent orchestrator |

---

## Quick Start

```bash
# Run adversarial review for completed paper
/phase65-adversarial-review

# Or as part of full pipeline (after Phase 6)
/full-pipeline-complete
```

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:

- `research_output_path`, `research_folder`

### 2. Session Resume Detection

Check for existing checkpoint at `{research_folder}/paper/review/065_review_checkpoint.yaml`:

- If exists and `current_round > 0`: Resume from that round
- If exists and `status == CONVERGED`: Skip to finalize
- If not exists: Start fresh from Step 1

### 3. Execution Flow

Refer to `workflow.yaml` for execution configuration:
- Each round has Three-Persona Adversary → Gate → Revision sequence
- Convergence check after each round (FATAL=0, MAJOR=0, persuasiveness_passed)
- Maximum 3 rounds

### 4. First Step

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
