---
name: "Phase 5: Baseline Repository Comparison"
description: "Compare validated hypothesis results with official GitHub baseline implementations using adapter pattern and minimal modifications"
web_bundle: false
---

# Phase 5: Baseline Repository Comparison

> **Pipeline Position:** Phase 4 → **[Phase 5: Baseline Comparison]** → Paper Writing
> **Principle:** "Suitability first, modification second"
> **Mode:** UNATTENDED (Fully Automatic)

**Goal:** Compare validated hypothesis results with official GitHub baseline implementations to provide rigorous, reproducible comparison data for academic papers.

**Your Role:** In addition to your name, communication_style, and persona, you are also a baseline comparison specialist and experiment execution expert collaborating with a deep learning researcher. This is a partnership, not a client-vendor relationship. You bring expertise in repository analysis, code adaptation, and experimental methodology, while the user brings hypothesis context and domain knowledge. Work together as equals to produce rigorous baseline comparisons.

---

## Overview

This workflow compares validated hypothesis results with official baseline implementations from GitHub. Instead of implementing baselines from scratch (which risks "easy direction" bias), this workflow:

1. **Searches** for official GitHub repositories implementing comparable methods
2. **Evaluates** candidate repos based on suitability and adaptability
3. **Adapts** the selected repository with minimal modifications
4. **Executes** experiments with identical conditions (model, dataset, task, metrics)
5. **Generates** comparison reports

---

## Core Principle

### Suitability First, Modification Second

**Selection Priority:**
1. **Most suitable repository** - Best methodological match
2. **Then minimal adaptation** - Only necessary changes

**NOT:**
- ~~Select easiest to modify~~
- ~~Avoid complex repositories~~
- ~~Implement from scratch~~

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self contained instruction file that is a part of an overall workflow that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in checkpoint file using current_step field
- **Append-Only Building**: Build documents by appending content as directed to the output file

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: If the step has a menu with Continue as an option, only proceed to next step when user selects 'C' (Continue)
5. **SAVE STATE**: Update checkpoint file before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update checkpoint file when completing a step
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input
- 📋 **NEVER** create mental todo lists from future steps

### Step Flow Diagram

```
START → step-01-init.md
         ↓ (load next step only on success)
      step-02-define.md
         ↓
      step-03-search.md
         ↓
      step-04-evaluate.md
         ↓
      step-05-select.md
         ↓
      step-05.5-baseline-env-verification.md
         ↓
      step-06-setup.md
         ↓
      step-07-adaptation-coding.md ← Phase 4 Coder pattern
         ↓
      step-08-validation.md ← Phase 4 Validator pattern
         ↓
      step-09-experiment.md ← Phase 4 Experiment pattern
         ↓
      step-10-report.md
         ↓
      step-10a-gate-evaluation.md ← DETERMINES_SUCCESS gate
         ↓
      step-10b-finalize.md → END
```

---

## Workflow Steps

| Step | Name | Description | Pattern |
|------|------|-------------|---------|
| 01 | Initialize | Verify Phase 4 completion, understand hypothesis journey | - |
| 02 | Define Comparison | Define scope, requirements, metrics | - |
| 03 | Search Repositories | Search GitHub for candidates (Exa MCP) | - |
| 04 | Evaluate Candidates | Score and rank repositories (Serena MCP) | - |
| 05 | Select Baselines | Choose top 3 baselines | - |
| 05.5 | Environment Verification | Verify baseline's environment is usable (Mode B) | - |
| 06 | Setup & Analyze | Clone, setup conda, analyze code (Serena MCP) | - |
| 07 | **Adaptation Coding** | Generate adapter code per Archon task | **Phase 4 Coder** |
| 08 | **Validation** | Validate adaptation code (static + runtime) | **Phase 4 Validator** |
| 09 | **Experiment Execution** | Run baseline experiments (nohup, 6 runs - Mode B) | **Phase 4 Experiment** |
| 10 | Report Generation | Generate comparison report | - |
| 10a | Gate Evaluation | Evaluate DETERMINES_SUCCESS gate | - |
| 10b | Finalize | Calculate benchmark metrics, archive checkpoint | - |

---

## Phase 4 Pattern Reuse (Steps 7-9)

### Coder-Validator Loop for Adaptation

```
┌─────────────────────────────────────────┐
│ Adaptation Coding Loop (max 3) │
│ │
│ [Step 6: Setup & Analyze] │
│ │ - Generate 05_tasks.yaml │   ← NEW
│ ▼                                 │
│ [Step 7: Adaptation Coding] │
│ │ - Load tasks from 05_tasks.yaml │ ←  CHANGED
│ │ - Generate adapter code │
│ │ - Status: pending → doing → review │
│ ▼                                 │
│ All tasks in "review"? │
│ │                                 │
│ ▼                                 │
│ [Step 8: Validation] │
│ │ - Update 05_tasks.yaml │   ← CHANGED
│ ├── Pass → All "done" ────────────┼──→ Step 9 (Experiment)
│ │                                 │
│ └── Fail → Tasks to "pending" ────┘
│ │
└─────────────────────────────────────────┘
```

### Task Management

**Change:** Adaptation tasks use a local YAML file.

| Component | Old | New |
|-----------|------------|------------|
| Task storage | Archon MCP | `05_tasks.yaml` |
| Task generation | Step 7 (dynamic) | Step 6 (pre-generated) |
| Task query | `mcp__archon__find_tasks` | Read YAML file |
| Task update | `mcp__archon__manage_task` | Write YAML file |
| Archon role | Task + Hypothesis status | Hypothesis status only |

### MCP Tools

| MCP | Purpose | Key Tools |
|-----|---------|-----------|
| **Archon** | Knowledge search, Hypothesis status | `rag_search_*` (NOT `find_tasks/manage_task` for adaptation) |
| **Serena** | Code analysis | `get_symbols_overview`, `find_symbol`, `search_for_pattern` |
| **Exa** | Fallback search | `get_code_context_exa`, `web_search_exa` |

### Error Escalation Protocol

From Phase 4 step-05:
- Quick Fix (max 3 attempts)
- Step 7 Escalation (max 1 retry)
- User intervention (final fallback)

---

## Session Resume Detection

**Check for existing checkpoint at** `{baseline_folder}/05_baseline_checkpoint.yaml`:

| Condition | Action |
|-----------|--------|
| Checkpoint exists AND `current_step > 1` | Load `step-{current_step}` file, display "Resuming from Step {current_step}" |
| Checkpoint does not exist | Start fresh from Step 1, load `step-01-init.md` |

---

## Input Requirements

### From Phase 4 (Required)

| File | Description |
|------|-------------|
| `04_validation.md` | Validation report with results |
| `experiment_results.json` | Structured experiment data |
| `code/outputs/results.csv` | Raw experimental data (15 runs) |
| `code/measurements.py` | Measurement implementations |

### From verification_state.yaml

- Hypothesis validation status must be `COMPLETED`
- Gate result (PASS/PARTIAL/FAIL) determines comparison context
- Hypothesis journey (version_history, lessons_learned) for context

---

## Output Specifications

### Primary Output

**`05_baseline_comparison.md`** - Final comparison report containing:
- Executive summary
- Experimental setup (shared conditions)
- Results by learning rate
- Overall comparison
- Hypothesis journey context
- Conclusion

### Secondary Outputs

| File | Description |
|------|-------------|
| `comparison_data.csv` | Merged ours + baseline data |
| `experiment_log.md` | Experiment execution log |
| `CHANGES.md` | All code modifications documented |

### Artifacts

| Folder | Description |
|--------|-------------|
| `baselines/{repo}/` | Cloned baseline repository |
| `adaptations/{repo}/` | Adaptation code + tests |
| `experiments/` | Baseline experiment results |

---

## Adaptation Strategy

### Strategy Types (from Step 6 analysis)

1. **Adapter Pattern** (Preferred)
   - Create wrapper/adapter classes
   - No modification to original code
   - Easy to track and rollback

2. **Config Override**
   - Override via configuration files
   - No code changes needed
   - Limited to configurable parameters

3. **Direct Modification** (Minimal)
   - Only when adapter pattern impossible
   - Document every change in CHANGES.md

### Adaptation Components (Mode B)

> **Mode B Principle:** Inject OUR algorithm into BASELINE's environment.
> We USE baseline's model, dataset, config as-is. Only the algorithm differs.

| Component | Purpose | Strategy |
|-----------|---------|----------|
| Algorithm Injection | Replace/wrap baseline's optimizer with ours | optimizer_replacement / wrapper |
| Metric Injection | Add psi measurement | adapter_pattern + modification |
| Results Saver | Save in CSV format | adapter_pattern |
| Training Script | Minimal modification to baseline's train.py | direct_modification (minimal) |

---

## Experiment Configuration (Mode B)

### Mode B: Per-Baseline Comparison

> **Each baseline uses its OWN environment.** The ONLY difference is the algorithm.

| Parameter | Value |
|-----------|-------|
| Model | BASELINE's model architecture (per baseline) |
| Dataset | BASELINE's dataset (per baseline) |
| Config | BASELINE's hyperparameters (per baseline) |
| Seeds | 1 |
| Methods | 2 per baseline (baseline_original vs ours_injected) |
| Baselines | 3 |
| **Total Runs** | 6 (3 baselines × 2 methods × 1 seed) |

---

## Integration with Pipeline

### Trigger Conditions

This workflow can be triggered:
1. After Phase 4 completion (any hypothesis)
2. Manually via `/phase5-baseline-repo-comparison`
3. As part of full pipeline in UNATTENDED mode

### verification_state.yaml Updates

```yaml
# Mode B: Updates at main_hypothesis level (not hypotheses.{id})
main_hypothesis:
  baseline_comparison:
    status: "COMPLETED" # or "FAILED", "IN_PROGRESS"
    completed_at: "2026-01-15T15:30:00Z"
    report_file: "h-main/baseline_comparison/05_baseline_comparison.md"
    mode: "B"
    gate:
      type: "DETERMINES_SUCCESS"
      satisfied: true
      result: "PASS"
    per_baseline_results:
      - baseline_repo: "repo1"
        baseline_model: "ResNet18"
        baseline_dataset: "CIFAR10"
        winner: "ours"
        improvement: "+2.3%"
      - baseline_repo: "repo2"
        baseline_model: "VGG16"
        baseline_dataset: "CIFAR100"
        winner: "ours"
        improvement: "+1.5%"
    aggregate_results:
      baselines_won: "2/3"
      threshold_met: true
```

---

## Error Handling

### Recoverable Errors

| Error | Recovery Action |
|-------|-----------------|
| Network timeout | Retry with backoff |
| gh rate limit | Wait and retry |
| Conda conflict | Try alternative packages |
| Adaptation test fail | Return to Step 7 (Coder) |

### Fatal Errors

| Error | Action |
|-------|--------|
| No suitable repo | Stop, generate failure report |
| Adaptation impossible | Stop, explain why |
| All experiments failed | Stop, investigate |

---

## File Structure

```
phase5-baseline-repo-comparison/
├── workflow.md # This file
├── workflow.yaml # Configuration
├── checklist.md # Quality checklist
├── steps/
│ ├── step-01-init.md
│ ├── step-02-define.md
│ ├── step-03-search.md
│ ├── step-04-evaluate.md
│ ├── step-05-select.md
│ ├── step-05.5-baseline-env-verification.md ← Baseline environment verification (Mode B)
│ ├── step-06-setup.md
│ ├── step-07-adaptation-coding.md ← Phase 4 Coder pattern
│ ├── step-08-validation.md ← Phase 4 Validator pattern
│ ├── step-09-experiment.md ← Phase 4 Experiment pattern
│ ├── step-10-report.md
│ ├── step-10a-gate-evaluation.md ← DETERMINES_SUCCESS gate
│ └── step-10b-finalize.md ← Benchmark metrics & cleanup
├── templates/
│ ├── 05_baseline_checkpoint_template.yaml
│ ├── 05_tasks_template.yaml ←  NEW (Local YAML task management)
│ └── comparison_report_template.md
└── _references/
    └── (shared with phase4-coding)
```

---

## Related Workflows

| Workflow | Relationship |
|----------|--------------|
| `phase4-coding` | Input: validation results, Pattern source for Steps 7-9 |
| `hypothesis-loop` | Can trigger after Phase 4 |

---

## Quick Start

```bash
# Run baseline comparison for a specific hypothesis
/phase5-baseline-repo-comparison --hypothesis H-E1

# Or as part of full pipeline
/full-pipeline-unattended "research_idea.md"
```

---

## Intentional Deviations from BMAD v6 Standards

> **Purpose:** This workflow is designed for UNATTENDED deep learning research automation. The following deviations from BMAD v6 `workflow-template.md` and `step-template.md` are intentional and documented.

### 1. UNATTENDED Mode Execution

**Standard:** Interactive mode with user confirmations and menu prompts.
**Deviation:** Fully automatic execution without user interaction.
**Rationale:** Research pipeline automation requires uninterrupted execution across multiple phases.

### 2. Checkpoint-Based State Tracking

**Standard:** Uses `stepsCompleted: []` array in workflow context.
**Deviation:** Uses `current_step: N` field in `05_baseline_checkpoint.yaml`.
**Rationale:** Checkpoint file provides richer state tracking including experiment progress, coder-validator cycles, and Archon task synchronization.

### 3. Section 0 Archon Integration

**Standard:** Steps begin with step content directly.
**Deviation:** Each step begins with "Section 0: Update Step Task Status" for Archon MCP synchronization.
**Rationale:** Archon task management enables external visibility into pipeline progress and cross-phase coordination.

### 4. Non-Standard Step Naming

**Standard:** Sequential step numbering (step-01, step-02, ...).
**Deviation:** Includes substeps (step-05.5-baseline-env-verification, step-10a-gate-evaluation, step-10b-finalize).
**Rationale:** Complex research workflow requires logical grouping without disrupting established step numbers.

### 5. Research-Specific Frontmatter Fields

**Standard:** `name`, `description`, `schema_version` only.
**Deviation:** Additional fields: `baselines_count`, `datasets_count`, `max_coder_validator_cycles`, `mode`.
**Rationale:** Deep learning experiments require experiment-specific configuration at step level.

### 6. Highly Prescriptive Approach

**Standard:** Balance between Intent (~40%) and Prescriptive (~60%) content.
**Deviation:** Near 100% prescriptive with explicit code blocks and step-by-step procedures.
**Rationale:** Research reproducibility requires exact execution paths, leaving no room for interpretation.

### 7. Reference File Extraction

**Standard:** Self-contained step files.
**Deviation:** Large templates and code blocks extracted to `_references/` directory.
**Rationale:** Token efficiency for LLM context while maintaining full documentation availability.

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from {project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml and resolve:

- `research_output_path`, `hypothesis_folder`, `hypothesis_id`

### 2. Session Resume Detection

Check for existing checkpoint at `{hypothesis_folder}/baseline_comparison/05_baseline_checkpoint.yaml`:

- If exists and `current_step > 1`: Resume from that step
- If not exists: Start fresh from Step 1

### 3. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.

---
