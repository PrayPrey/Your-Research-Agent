---
name: hypothesis-loop
description: "Execute hypothesis verification loop. Runs Phase 2C → 3 → 4 for each sub-hypothesis. Phase 5 is invoked separately."
architecture: "orchestration"
author: "Anonymous"
phase_output: "Validated sub-hypotheses ready for Phase 5"
web_bundle: false
---

# Hypothesis Verification Loop

**Goal:** Execute the hypothesis verification loop (Phase 2C → 3 → 4) for each sub-hypothesis in dependency order.

** Change:** Phase 5 is now completely separate from hypothesis-loop:
- full-pipeline: Step 7.5 invokes Phase 5 automatically
- standalone: User runs `/phase5-baseline-repo-comparison` separately

**Your Role:** You are an autonomous research pipeline orchestrator. This workflow executes WITHOUT user interaction in UNATTENDED mode. You coordinate phase executions, manage state transitions, and handle gate validation.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file
- **Just-In-Time Loading**: Only the current step file is in memory
- **Sequential Enforcement**: Steps must be completed in order
- **State Tracking**: Progress tracked via verification_state.yaml
- **Loop Support**: Step 4-9 form a loop over sub-hypotheses

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order
3. **CHECK CONTINUATION**: Auto-proceed in UNATTENDED mode
4. **SAVE STATE**: Update verification_state.yaml after each phase
5. **LOAD NEXT**: When directed, load, read entire file, then execute next step

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or bypass invoke-workflow
- 💾 **ALWAYS** save verification_state.yaml after state changes
- 🎯 **ALWAYS** follow gate routing (FAIL → Phase 0, PARTIAL → Phase 2A-Dialogue)
- 🔄 **ALWAYS** re-read execution_mode at hypothesis transitions

---

## STEP FLOW OVERVIEW

```
step-01-init.md → Parse mode + Load state
step-02-check-status.md → Check workflow status (STOPPED/COMPLETED)
step-03-get-ready.md → Get READY hypotheses queue
    ↓
┌─→ step-04-loop-start.md → Gate validation + IN_PROGRESS
│ step-05-phase-2c.md → Execute Phase 2C
│ step-06-phase-3.md → Execute Phase 3
│ step-07-phase-4.md → Execute Phase 4
│ step-08-phase4-gate.md → Process MUST_WORK gate + routing
│ step-09-loop-continue.md → Mode actions + loop control
└───────────────────────────────────────────────────────────┘
    ↓ (when all sub-hypotheses done)
    │
    ├─→ [full-pipeline mode] EXIT → Return to full-pipeline Step 7.5 for Phase 5
    │
    └─→ [standalone mode] step-11-complete.md → Summary (run Phase 5 separately)
```

##

| Caller | execution_source | After All Done |
|--------|------------------|----------------|
| `/full-pipeline-unattended` | `full-pipeline` | EXIT → Step 7.5 (Phase 5 invoked automatically) |
| `/hypothesis-loop` (direct) | `standalone` | step-11 → summary (run `/phase5-baseline-repo-comparison` separately) |

**Note:** Phase 5 is no longer part of hypothesis-loop workflow.

---

## VARIABLE DEFINITIONS

```yaml
# Config source
config_source: "{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml"

# From config
research_output_path: "{config_source}:research_output_path"
research_folder: "{research_output_path}/youra_research"

# State tracking
verification_state_file: "{research_folder}/verification_state.yaml"

# Workflow paths
workflow_path: "{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/hypothesis-loop"
workflow_base_path: "{project-root}/bmad-custom-src/custom/modules/youra-research/workflows"

# Phase workflows
phase2c_workflow: "{workflow_base_path}/phase2c-experiment-design/workflow.yaml"
phase3_workflow: "{workflow_base_path}/phase3-implementation-planning/workflow.yaml"
phase4_workflow: "{workflow_base_path}/phase4-coding/workflow.yaml"
phase5_workflow: "{workflow_base_path}/phase5-baseline-repo-comparison/workflow.yaml"
```

---

## GATE SYSTEM

| Gate Type | Phase | On PASS | On FAIL/PARTIAL |
|-----------|-------|---------|-----------------|
| MUST_WORK | 4 | → Next hypothesis | FAIL → Phase 0, PARTIAL (max) → Phase 2A-Dialogue |
| DETERMINES_SUCCESS | 5 | → COMPLETED | PARTIAL → Phase 0 |

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml`:
- `research_output_path`
- `user_name`
- `communication_language`

### 2. First Step Execution

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
