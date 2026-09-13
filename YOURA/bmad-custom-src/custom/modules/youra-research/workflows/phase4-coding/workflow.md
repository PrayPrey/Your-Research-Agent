---
name: 'Phase 4 Implementation & Validation'
description: 'Converts Phase 3 implementation plans into working code and validates hypotheses through a Coder-Validator agent loop'
web_bundle: false
---

# Phase 4: Implementation & Validation Workflow

**Goal:** Convert Phase 3 implementation plans into working code and validate hypotheses through systematic Coder-Validator loops leveraging Archon MCP for task management and Serena MCP for code analysis.

**Your Role:** In addition to your name, communication_style, and persona, you are also an implementation specialist collaborating with a researcher. This is a partnership, not a client-vendor relationship. You bring code generation, validation expertise, and MCP tool proficiency, while the user brings hypothesis context, domain knowledge, and requirements. Work together as equals.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that is part of an overall workflow that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in output file frontmatter using `stepsCompleted` array when a workflow produces a document
- **Append-Only Building**: Build documents by appending content as directed to the output file

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: If the step has a menu with Continue as an option, only proceed to next step when user selects 'C' (Continue)
5. **SAVE STATE**: Update `stepsCompleted` in frontmatter before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update frontmatter of output files when writing the final output for a specific step
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input
- 📋 **NEVER** create mental todo lists from future steps

---

## INITIALIZATION SEQUENCE

### 0. Session Resume Detection (AUTO-EXECUTE ON EVERY ENTRY)

**CRITICAL: Before starting any step, check if this is a resumed session.**

> `find_tasks(status="doing")` to avoid confusion with multiple "doing" tasks.
> See: `{helpers_path}/checkpoint_helpers.md` - Section "Context Loss Recovery"

```
Step 0.1: Detect Recovery Context
────────────────────────────────────────
from checkpoint_helpers import detect_recovery_context, verify_archon_task_alignment

# Use helper function for Option B compatible recovery
recovery = detect_recovery_context(
    verification_state_path="{research_folder}/verification_state.yaml"
)

IF NOT recovery["success"]:
    → Error: {recovery["error"]}
    → Proceed to Step 1 normally (fresh start)

IF recovery["resume_action"] == "START_NEXT_HYPOTHESIS":
    → No IN_PROGRESS hypothesis found
    → Return to hypothesis-loop for next hypothesis

# Extract recovery context
hypothesis_id = recovery["hypothesis_id"]
current_phase = recovery["current_phase"]
current_step = recovery["current_step"]
checkpoint = recovery["checkpoint"]
resume_step_file = recovery["resume_step_file"]

Step 0.2: Verify Archon Task Alignment
─────────────────────────────────────────────
# Validate cached task IDs match Archon state
alignment = verify_archon_task_alignment(recovery)

IF NOT alignment["aligned"]:
    display: f"⚠ Task alignment discrepancies: {alignment['discrepancies']}"
    # Continue anyway - discrepancies are informational

# Log task status from direct ID lookup (not status search)
step_task_status = alignment["step_task_status"]
phase_task_status = alignment["phase_task_status"]

Step 0.3: Resume from Correct Step
──────────────────────────────────
# Use checkpoint.current_step directly (trusted source)
IF current_step >= 2:
    → Resume at: {resume_step_file}
    → Hypothesis: {hypothesis_id}
    → Phase: {current_phase}
ELSE:
    → Continue from Step 1 (initialization)

Step 0.4: Announce Resume
─────────────────────────
Display to user:
"📢 Session Resume Detected!
- Active Workflow: phase4-coding
- Hypothesis: {hypothesis_id}
- Phase: {current_phase}
- Current Step: {current_step} ({resume_step_file})
- Step Task Status: {step_task_status}
→ Continuing workflow execution..."
```

**IF NO checkpoint found OR current_step == 1:** Proceed to Step 1 normally.

### 0.5 Checkpoint State Persistence Rule

**The checkpoint file (`04_checkpoint.yaml`) is automatically updated at key points:**

- **Step 1**: Created with initial state
- **Step 2**: Updated after each task completion (task_history, tasks.completed)
- **Step 3**: Updated after validation (validation_passed, coder_validator_cycles)
- **Step 4**: Updated with experiment option (experiment_option)
- **Step 5**: Updated with experiment results (experiment_status, error_escalation)
- **Step 6**: Updated with gate result (gate_result, gate_type, gate_action)
- **Step 8**: Archived (renamed to `04_checkpoint_archived_{timestamp}.yaml`)

**Checkpoint fields for recovery:**
```yaml
current_step: 1-8 # Resume from this step
tasks:
  completed: N # Skip completed tasks
  remaining: M # Process remaining tasks
coder_validator_cycles: K # Track loop count (max 5)
partial_results:
  experiment_status: pending|running|completed|skipped
  gate_result: PASS|FAIL|INCOMPLETE|SKIPPED
```

---

### 1. Configuration Loading

Load and read full config from {project-root}/{_bmad_folder_}/custom/modules/youra-research/module.yaml and resolve:

- `project_name`, `output_folder`, `user_name`, `communication_language`, `document_output_language`
- `hypothesis_folder`, `research_folder`

### 2. Load Archon Project ID from verification_state.yaml

Load Archon project connection info from {research_folder}/verification_state.yaml:

```yaml
# Read from verification_state.yaml
hypotheses:
  {{hypothesis_id}}:
    implementation_planning:
      archon_project_id: "uuid-from-phase3" # ← Use this
      archon_document_ids: {...}
      archon_task_count: N
```

- `archon_project_id`: Archon project UUID created in Phase 3 Step 8
- If archon_project_id is null, fall back to Archon search by hypothesis_id

### 3. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-01-initialize.md` to begin the workflow.

---

## Overview

Phase 4 converts Phase 3 implementation plans into working code and validates hypotheses through a Coder-Validator agent loop. This workflow leverages Archon MCP for task management and Serena MCP for code analysis.

## Pipeline Position

```
Phase 0 → Phase 1 → Phase 2A-Dialogue → Phase 2B → (2C → 3 → [Phase 4]) × N → 4.5 → [5] → 6 → 6.5 → 6.5.1
```

## Multi-Agent Design

| Agent | Execution Mode | Purpose |
|-------|---------------|---------|
| **Coder** | Main Session | Cross-task code generation with context |
| **Validator** | Sub-Agent | Structured validation with checklist |

### Coder-Validator Loop

```
┌─────────────────────────────────────────┐
│ Coder-Validator Loop (max 5) │
│ │
│ [Coder: Main Session] │
│ │ - Query todo tasks │
│ │ - Generate code per task │
│ │ - Status: todo → doing → review │
│ ▼                                 │
│ All tasks in "review"? │
│ │                                 │
│ ▼                                 │
│ [Validator: Sub-Agent] │
│ │                                 │
│ ├── Pass → All "done" ────────────┼──→ Exit Loop
│ │                                 │
│ └── Fail → Tasks to "todo" ───────┘
│ │
└─────────────────────────────────────────┘
```

## Steps Overview

| Step | Name | Purpose |
|------|------|---------|
| 1 | Initialize | Load Phase 3 outputs, connect Archon, check checkpoint, **auto-copy previous code (INCREMENTAL)** |
| 1b | Continue | Resume from checkpoint (if exists) |
| 2 | Coder Loop | Generate code per Archon task |
| 3 | Validator | Validate code, update task status |
| 4 | Experiment Confirm | Display experiment brief, select option |
| 5 | Experiment Execute | Execute, Quick Fix loop (3x), Step 2 escalation (1x) |
| 5c | Post-Validation | **Mock Data + Mock Model detection, route to Step 2 if detected** |
| 6 | Gate Processing | Analyze results, route to 6b/7 based on gate result |
| **6b** | **Reflection** | **Analyze FAIL results, decide MODIFY or FAILED (triggers on FAIL+MUST_PASS)** |
| 7 | Report Generation | Generate 04_validation.md |
| 8 | Completion | Cleanup, prepare Phase 5 handoff |

## Input Requirements

### From Phase 3

| File | Description |
|------|-------------|
| `03_prd.md` | Product Requirements Document |
| `03_architecture.md` | Architecture + Epic tasks + complexity |
| `03_logic.md` | API signatures, tensor shapes, pseudo-code |
| `03_config.md` | YAML schemas, dataclasses |
| `02c_experiment_brief.md` | Experiment specification |
| `verification_state.yaml` | Gate conditions, hypothesis status |

### 🚨 CRITICAL: Central verification_state.yaml Rule

**The `verification_state.yaml` is a CENTRAL file located at `{research_folder}/verification_state.yaml`**

```
Location: {research_folder}/verification_state.yaml ← ONE file for ALL hypotheses
NOT: {hypothesis_folder}/verification_state.yaml ← FORBIDDEN!
```

**This file manages state for ALL hypotheses (H-E1, H-M1, H-M2, H-M3, H-CP1, etc.)**

**Rules:**
- ✅ **READ** from `{research_folder}/verification_state.yaml`
- ✅ **UPDATE** specific `hypotheses.{hypothesis_id}` section only
- ✅ **WRITE BACK** to same central file
- ⛔ **NEVER** create new file in `{hypothesis_folder}`
- ⛔ **NEVER** overwrite entire file structure
- ⛔ **NEVER** use `hypothesis:` (singular) - always `hypotheses:` (dictionary)

### Archon Project

- Project with implementation tasks (max 30 tasks recommended)
- Tasks in `todo` status ready for execution

### INCREMENTAL Hypothesis Support (NEW)

**Auto-detection:** Step 1 reads `prerequisites` from `verification_state.yaml`

| Condition | Type | Action |
|-----------|------|--------|
| `prerequisites: []` | FOUNDATION | No code copy, start fresh |
| `prerequisites: [H-E1]` | INCREMENTAL | Auto-copy `H-E1/code/` to current `code/` |

**Code Reuse Flow:**
```
H-E1 (FOUNDATION) → code/ generated fresh
    ↓
H-M1 (INCREMENTAL, prereq: H-E1) → auto-copies H-E1/code/ → modifies for mechanism
    ↓
H-M2 (INCREMENTAL, prereq: H-M1) → auto-copies H-M1/code/ → modifies for new mechanism
```

**Benefits:**
- Proven, working code as starting point
- Focus only on mechanism-specific changes
- Reduces redundant implementation effort

## Output Specifications

### Generated Files

| File | Location | Description |
|------|----------|-------------|
| `04_validation.md` | `{hypothesis_folder}/` | Validation report |
| `04_checkpoint.yaml` | `{hypothesis_folder}/` | Checkpoint for recovery |
| `code/*.py` | `{hypothesis_folder}/code/` | Generated implementation |

### Folder Structure

```
{hypothesis_folder}/
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 04_checkpoint.yaml ← Checkpoint
├── 04_validation.md ← Validation report
└── code/ ← Generated code
    ├── config/
    │ └── config.py
    ├── data/
    │ └── *.py
    ├── models/
    │ └── *.py
    ├── train/
    │ └── *.py
    ├── eval/
    │ └── *.py
    ├── analysis/
    │ └── *.py
    ├── tests/ ← Task-based test files (MANDATORY!)
    │ ├── __init__.py
    │ └── test_*.py ← One per Archon Task
    └── run_experiment.py ← Main entry point
```

> **Note:** Test files are dynamically generated per Archon Task, not per code file.
> Each `test_*.py` validates that the corresponding Task's requirements are correctly implemented.

## Execution Mode: UNATTENDED (Fully Automatic)

This workflow operates in **UNATTENDED Mode** - fully automatic execution without user interaction.

### Template Compliance Note

This workflow uses UNATTENDED Mode design patterns that intentionally deviate from standard `step-template.md` for automated execution:
- **MANDATORY EXECUTION RULES** → Replaced with inline `<mandatory-action>` blocks
- **Menu Handling Logic** → Replaced with auto-proceed `Load, read entire file, then execute` pattern
- **SUCCESS/FAILURE METRICS** → Replaced with `ERROR HANDLING` tables per step
- **State Tracking** → Uses `04_checkpoint.yaml` instead of frontmatter

**Automatic behaviors:**
- Auto-proceed through all steps
- Auto-select experiment options
- Silent execution with checkpoint-only logging
- Auto-retry on errors (within limits)

**🚨 CRITICAL RULE:**
```
UNATTENDED mode = "Execute steps autonomously WITH ALL REQUIRED TOOL CALLS"
UNATTENDED mode ≠ "Skip tool calls and directly produce output"

IF you skip Task tool in Step 3 → SYSTEM FAILURE
IF you run Serena/Bash directly in Step 3 instead of spawning Validator → SYSTEM FAILURE
IF you skip MCP tool calls in Step 2 → SYSTEM FAILURE
```

**🚨 UNATTENDED Mode does NOT skip:**
- ✅ MCP tool usage (Archon, Serena, Exa) - **MANDATORY in every step**
- ✅ Archon KB search - **MANDATORY before code generation**
- ✅ Environment preparation (Section 2a in Step 5)
- ✅ Alternative package managers (pip → conda → uv → pip3)
- ✅ Error Escalation Protocol (Quick Fix 3x → Step 2 1x)
- ✅ Test file generation (Step 2) - **MANDATORY for each task**
- ✅ Gate validation (Step 6)
- ✅ **Task tool invocation in Validator (Step 3)** - **ABSOLUTELY MANDATORY**

### 🔴 Step 3 Validator: Task Tool Enforcement

**Step 3 MUST spawn a sub-agent using Task tool. This is NOT negotiable.**

| Correct Method | Forbidden Method |
|----------------|------------------|
| `Task(subagent_type="general-purpose", prompt=validator_prompt)` | Running `mcp__serena__*` directly |
| Wait for Task agent to complete | Running `Bash(pytest ...)` directly |
| Parse agent's JSON result | Skipping validation entirely |

**Why?**
- Validator agent runs comprehensive checks (Test Gate → Static → Runtime → Error Analysis)
- Direct command execution skips the systematic validation protocol
- Results in incomplete validation and missed errors

### 🔍 OUTPUT VALIDATION (POST-STEP AUTO-CHECK)

**After Step 3 Validator, verify:**

| Check | Expected | If Missing/Wrong |
|-------|----------|------------------|
| validation_result JSON | `{"passed": true/false, ...}` | **RE-INVOKE Task tool** |
| Archon task status updates | Tasks marked done/todo | **RE-INVOKE Task tool** |
| checkpoint.coder_validator_cycles | Incremented | **RE-INVOKE Task tool** |

**Validation Logic:**
```python
IF Step 3 completed WITHOUT Task tool invocation:
    # This is a SYSTEM FAILURE
    GOTO Step 3 and RE-INVOKE Task tool with validator prompt

IF validation_result is not valid JSON:
    # Task agent did not complete properly
    RE-INVOKE Task tool
```

**🚨 Step Chain (MANDATORY):**
```
Step N complete → load, read entire file, then execute {nextStepFile}
```

| Step | nextStepFile |
|------|--------------|
| Step 1 → | step-01a-data-setup.md |
| Step 1a → | step-02-coder-loop.md |
| Step 2 → | step-03-validator.md |
| Step 3 → | step-04-experiment-confirm.md (if PASS) or step-02 (if FAIL) |
| Step 4 → | step-05a-pre-validation.md |
| Step 5a → | step-05b-execution.md |
| Step 5b → | step-05c-post-validation.md |
| Step 5c → | step-06-gate-processing.md |
| Step 6 → | See **Step 6 Routing Logic** below |
| Step 6b → | step-07-report-generation.md (after reflection decision) |

### Step 6 Routing Logic (LLM Execution Reference)

```python
# Gate Processing → Next Step Decision
# NOTE: Mock Data/Model checks are done in Step 5c BEFORE reaching Step 6
# DETERMINES_SUCCESS moved to Phase 5 (Baseline Comparison).

IF gate_result == "PASS":
    NEXT = "step-07-report-generation.md" # Mock checks already done in Step 5c

ELIF gate_result in ["FAIL", "PARTIAL"]:
    IF gate_type == "MUST_WORK":
        NEXT = "step-06b-reflection.md" # Hypothesis problem → reflect
    ELIF gate_type == "SHOULD_WORK":
        NEXT = "step-07-report-generation.md" # Continue with limitation note
```
| Step 7 → | step-08-completion.md |
| Step 8 → | END (workflow complete) |

- `{nextStepFile}` **load/execute is MANDATORY**
- No menus or user prompts - automatic progression

## Gate Types

| Type | Description | On Failure |
|------|-------------|------------|
| `MUST_WORK` | PoC validation - does the methodology work? | Reflect (Step 6b), route to Phase 2A redesign |
| `SHOULD_WORK` | Optional validation - nice to have | Continue with limitation note |

> **Note:** `DETERMINES_SUCCESS` gate moved to Phase 5 (Baseline Comparison).

## Error Recovery

### Task-Level Checkpoints

- Checkpoint saved after each task completion
- Max 3 retry attempts per task
- Max 5 Coder-Validator cycles total

### Mock Detection (Step 5c)

**Step 5c performs comprehensive mock detection BEFORE gate processing:**

1. **Mock Data Detection** - Checks for synthetic/fake data:
   - Config flags (`use_synthetic: true`)
   - Log messages ("using synthetic data")
   - Perfect metrics (100% accuracy, 0.0 loss in first epoch)
   - Tiny datasets (< 100 samples)
   - Faker/mimesis imports

2. **Reality Check (Mock Model Detection)** - Behavioral tests for fake models:

```python
# Step 5c: Evaluate reality check results from experiment output
critical_tests = ["determinism", "sensitivity", "smoothness"]
supplementary_tests = ["gradient_flow", "weight_influence"]

IF NOT all(reality_check.tests[t] for t in critical_tests):
    checkpoint.mock_model_retries += 1
    IF checkpoint.mock_model_retries >= 3:
        Mark as BLOCKED: "Max mock model retries exceeded"
    ELSE:
        checkpoint.return_reason = "MOCK_MODEL_DETECTED"
        NEXT = "step-02-coder-loop.md" # Code problem → fix code
        EXIT # Do not proceed to Step 6

# Supplementary tests → warning only, continue to Step 6
```

**Why Pattern Matching is Insufficient:**
| Pattern Matching | Catches | Misses |
|------------------|---------|--------|
| `MockWrapper` | Named mocks | Renamed mocks |
| `torch.randn` | Direct random | `np.random`, seeded random |
| **Behavioral tests** | **ALL fake models** | Only adversarial mocks |

**Reference:** See `_references/reality-check-guide.md` for full implementation details.

### Step 5 Error Escalation Protocol

When experiment execution (Step 5) encounters persistent runtime errors:

```
Step 5 Error → Phase 3 Analysis → Archon Task Registration
                                           ↓
                    Quick Fix Loop (max 3 attempts)
                                           ↓
                           Success? → Continue experiment
                           Fail? → Step 2 Escalation (max 1)
                                           ↓
                    Coder-Validator Loop → Step 5 retry
                                           ↓
                           Still fail? → User intervention
```

**Key Limits:**
- Quick Fix attempts: max 3
- Step 2 escalation: max 1
- Error Tasks always registered in Archon for tracking

### Recovery Options

1. **Automatic**: Workflow detects checkpoint on restart
2. **Manual**: User can inspect and modify checkpoint
3. **Reset**: Delete checkpoint to start fresh
4. **Error Escalation**: Step 5 errors escalate to Coder-Validator loop with test case generation

## MCP Requirements

### Required

- **Archon MCP**: Task management (`todo` → `doing` → `review` → `done`)
- **Serena MCP**: Code analysis, symbol manipulation

### Required (Fallback)

- **Exa MCP**: PyTorch patterns, GitHub examples, latest documentation

### 🚨 Archon → Exa Fallback Policy (MANDATORY)

**Exa MCP MUST be used when Archon KB returns insufficient or inadequate results.**

```
┌─────────────────────────────────────────────────────────┐
│ Archon KB → Exa Fallback Flow │
├─────────────────────────────────────────────────────────┤
│ │
│ Step 1: Search Archon KB │
│ mcp__archon__rag_search_knowledge_base(...) │
│ │                                        │
│ ▼                                        │
│ Is result SUFFICIENT and RELEVANT? │
│ (>= 3 results AND directly answers query with code) │
│ │                                                 │
│ YES │ NO │
│ ▼         ▼ │
│ Use it Step 2: MUST use Exa MCP │
│ mcp__exa__get_code_context_exa(query) │
│ mcp__exa__web_search_exa(query) │
│ │
└─────────────────────────────────────────────────────────┘
```

**Mandatory Exa Triggers (Generalized Criteria):**

| Trigger Category | Description | Exa Required |
|------------------|-------------|--------------|
| **Insufficient Count** | Archon KB returns < 3 results | ✅ MANDATORY |
| **Low Relevance** | Results are generic, conceptual-only, or don't directly answer the query with concrete code | ✅ MANDATORY |
| **Specialized/Niche Domain** | Query involves specialized libraries, advanced techniques, or domain-specific implementations not commonly covered in general documentation | ✅ MANDATORY |
| **Recency Required** | Query involves recent API changes or specific compatibility constraints | ✅ MANDATORY |
| **Complex Implementation** | Query requires advanced patterns (custom kernels, distributed systems, optimization, integration) | ✅ MANDATORY |
| **Error Resolution Failed** | Archon KB suggestions did not resolve the error | ✅ MANDATORY |
| **Code-Heavy Query** | Query needs concrete implementation examples but Archon returns only conceptual explanations | ✅ MANDATORY |

**How to Detect "Specialized/Niche Domain" (General Heuristics):**
- Library/framework not part of standard PyTorch/TensorFlow/JAX core ecosystem
- Query involves specialized data structures (graph, temporal, geometric, sparse, etc.)
- Implementation requires domain-specific knowledge (molecular, financial, medical, etc.)
- Library has frequent API changes, is relatively new, or has limited mainstream documentation
- Query mentions cutting-edge research techniques or recent papers

## Quick Start

1. Ensure Phase 3 outputs are complete
2. Verify Archon project has tasks in `todo` status
3. Run workflow initialization
4. Follow step prompts (Default) or enable UNATTENDED mode

## Related Documentation

- [Validator Agent Specification](agents/validator-agent.md)
- [Step 5c Post-Validation (Mock Data + Model Detection)](steps/step-05c-post-validation.md)
- [Step 6b Reflection](steps/step-06b-reflection.md)
- [Reality Check Guide (Mock Model Detection)](_references/reality-check-guide.md)
- [04_validation Template](templates/04_validation_template.md)
- [04_checkpoint Schema](templates/04_checkpoint_template.yaml)
- [Workflow Checklist](checklist.md)
