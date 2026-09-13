---
name: phase2a-dialogue
description: Self-Contained Loop multi-persona hypothesis generation through free-form research discussion and structured output generation
web_bundle: false
---

# Phase 2A Dialogue Workflow

**Goal:** Generate validated research hypotheses through free-form discussion with 6 research personas using a Self-Contained Loop, followed by structured output generation for Phase 2B compatibility.

**Your Role:** You execute research persona responses during a discussion orchestrated by `orchestrate_exchange.py` (called via Bash). The script selects personas and checks convergence via external LLM. You write authentic persona responses in a loop within a single turn.

---

## WORKFLOW ARCHITECTURE

This workflow uses **step-file architecture** for disciplined execution in UNATTENDED mode.

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until directed
- **Sequential Enforcement**: Sequence within step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Progress tracked via Archon tasks and output YAML files
- **Append-Only Building**: Build outputs by appending content as directed to designated files

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **UNATTENDED EXECUTION**: In UNATTENDED mode, auto-progress without user confirmation
4. **CHECK CONTINUATION**: Verify previous step outputs exist before proceeding
5. **SAVE STATE**: Update Archon tasks and output files when completing steps
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update Archon task status when completing steps
- 🎯 **ALWAYS** follow the exact instructions in the step file
- 📋 **NEVER** create mental todo lists from future steps
- 🔄 **ALWAYS** verify prerequisite outputs exist before proceeding

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:

- `research_output_path` - Base path for research outputs
- Workflow paths via `{workflow_path}` variable

### 2. Stage Configuration Reference

Detailed stage configurations are defined in `{workflow_path}/workflow.yaml`:

- **Stage 0**: Gap Selection + Paper Preparation + Discussion Log Initialization
- **Stage 1**: Self-Contained Loop Discussion (6 personas, `orchestrate_exchange.py` for LLM-based convergence)
- **Stage 2**: Result Structuring (discussion_log.md → Phase 2B-compatible YAML/MD files)

### 3. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-00-initialize.md` to begin the workflow.

---

## WORKFLOW STAGES OVERVIEW

| Stage | Name | Execution | Output |
|-------|------|-----------|--------|
| 0 | Gap Selection + Paper Prep + Init | Automatic + Script | Selected gap, `papers/*.md`, `discussion_log.md` |
| 1 | Self-Contained Loop Discussion | INLINE (single turn loop) | `discussion_log.md` (with Final Assessments) |
| 2 | Result Structuring | INLINE | `03_refinement.yaml`, `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`, `03_refinement.md` |

---

## EXECUTION MODE

**Mode:** UNATTENDED

This workflow executes without user intervention. All steps auto-progress upon completion.

**UNATTENDED Rules:**
- Execute all steps without user confirmation prompts
- NEVER skip MCP tool calls or Task agent invocations
- ALWAYS complete full step sequences
- ONLY skip user [Y/N] confirmation prompts

---

## PIPELINE POSITION

```
Phase 0 → Phase 1 → **Phase 2A** → Phase 2B → ...
```

**Input:** `01_targeted_research.md` (from Phase 1)
**Output:** `03_refinement.yaml`, `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`, `03_refinement.md`, `discussion_log.md`

---

## MCP SERVER REQUIREMENTS

| Server | Purpose | Tools |
|--------|---------|-------|
| Semantic Scholar | Academic paper search | paper_relevance_search |
| Exa | Web/code search | web_search_exa |
| Archon | Past cases, task management | rag_search_*, manage_task |
| ClearThought | Structured reasoning | scientificmethod, sequentialthinking |
| Serena | Cross-phase memory | write_memory, read_memory (optional) |

---

