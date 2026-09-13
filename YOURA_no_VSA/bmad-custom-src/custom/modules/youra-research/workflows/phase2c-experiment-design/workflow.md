---
name: Phase 2C Experiment Design
description: "Generate detailed, research-backed experiment specifications from Phase 2B hypothesis verification protocols using MCP-powered implementation search and code analysis"
web_bundle: false

# Module path configuration
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
config_source: '{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml'

# YouRA Module Variables (resolved from config)
research_output_path: '{config_source}:research_output_path'

# Input files
phase2b_context: '{hypothesis_folder}/02b_context.md'
phase2b_roadmap: '{research_folder}/02b_verification_plan.md'
verification_state_file: '{research_folder}/verification_state.yaml'

# Output file
default_output_file: '{hypothesis_folder}/02c_experiment_brief.md'

# Template and validation
template: '{workflow_path}/template.md'
validation_checklist: '{workflow_path}/checklist.md'

# Session parameters
target_execution_time: '5-8 minutes'
specification_level: '1.5'
---

# Phase 2C: Research-Driven Experiment Design

**Goal:** Transform Phase 2B hypothesis into executable experiment specification (Level 1.5) using MCP-powered implementation research with full state tracking and gate validation.

**Your Role:** In addition to your name, communication_style, and persona, you are also a **Research Implementation Specialist** collaborating with a **ML Researcher**. This is a partnership, not a client-vendor relationship. You bring expertise in implementation research, code analysis, and experiment design patterns, while the user brings domain knowledge and research objectives. Work together as equals to produce research-backed experiment specifications.

---

## WORKFLOW ARCHITECTURE

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in output file frontmatter using `stepsCompleted` array
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

## PIPELINE POSITION

**Sequence:** Phase 0 → Phase 1 → Phase 2A-Dialogue → Phase 2B → (**Phase 2C** → 3 → 4) × N → 4.5 → [5] → 6 → 6.5 → 6.5.1

### Inputs
| From | File | Required | Description |
|------|------|----------|-------------|
| Phase 2B | `{hypothesis_folder}/02b_context.md` | Yes | Per-hypothesis context (optimized, 91% smaller) |
| Phase 4 | `{previous_hypothesis_folder}/04_validation.md` | No | Previous hypothesis validation results |

### Outputs
| File | Description | Used By |
|------|-------------|---------|
| `{hypothesis_folder}/02c_experiment_brief.md` | Research-backed experiment specification (Level 1.5) | Phase 3 PRD Workflow |

---

## MCP SERVER REQUIREMENTS

### MANDATORY
- **Archon MCP**: `rag_search_knowledge_base`, `rag_search_code_examples` - Past implementation cases and proven patterns
- **Exa MCP**: `get_code_context_exa` - Real GitHub implementations and live code search

### CONDITIONAL
- **Serena MCP**: `get_symbols_overview`, `find_symbol`, `search_for_pattern` - Semantic code analysis for complex implementations

**Validation:** Archon and Exa MUST be available. Serena is optional but recommended.

---

## SPECIFICATION REQUIREMENTS (Level 1.5)

### Must Include
- **Dataset**: Exact name/version, source, splits, preprocessing, augmentation
- **Model**: Baseline architecture, proposed architecture, core mechanism pseudo-code (10-30 lines)
- **Training**: Optimizer, learning rate + schedule, batch size, epochs, loss, regularization
- **Evaluation**: Metrics, success criteria, expected baseline (PoC: direction-based, no statistical tests)
- **Ablation**: Variants to test, what each measures
- **References**: All sources, GitHub repos, code snippets

### Must NOT Include
- Complete file structure (Phase 3)
- Full code implementation (Phase 4)
- Task decomposition (Phase 3)

---

## STATE TRACKING INTEGRATION

### Phase 2C Responsibilities

**On Start (Step 1):**
1. Validate workflow status (check not STOPPED)
2. Validate hypothesis status (check not BLOCKED)
3. Check prerequisite gate satisfaction
4. Apply gate logic (MUST_WORK failures stop workflow)
5. Update hypothesis experiment_design.status = "IN_PROGRESS"

**On Complete (Step 8):**
1. Update hypothesis experiment_design.status = "COMPLETED"
2. Update hypothesis experiment_design.file = output filename
3. Log completion event in history
4. Update statistics

### Gate Validation Logic
- **MUST_WORK**: If failed → STOP workflow, update state, block dependents, EXIT
- **SHOULD_WORK**: If failed → CONTINUE with limitation note, log, proceed
- **DETERMINES_SUCCESS**: Final validation gate (Phase 4)

---

## PROGRESSIVE FILE SYSTEM

**Output File:** `{default_output_file}`
**Placeholder Pattern:** `{UNFILLED:variable_name}`

### Step-to-Placeholder Mapping
| Step | Placeholders to Fill |
|------|---------------------|
| 1 | `hypothesis_id`, `hypothesis_statement`, `gate_condition`, `workflow_status`, `continuation_context` |
| 2 | `archon_knowledge_findings`, `archon_code_findings` |
| 3 | `exa_github_findings` |
| 4 | `serena_code_analysis` (conditional) |
| 5 | `dataset_specification`, `baseline_model` |
| 6 | `experiment_specification`, `core_mechanism_pseudocode`, `training_protocol`, `evaluation_metrics` |
| 7 | `reference_implementations` |
| 8 | Quality validation, state file update |

---

## ERROR HANDLING

### MCP Server Unavailable
- **Archon/Exa unavailable**: STOP workflow, display error, instruct to start MCP servers
- **Serena unavailable**: Continue with warning, rely on Archon/Exa code snippets

### Workflow STOPPED (Gate Violation)
Display recovery options:
1. Review and retry failed hypothesis
2. Modify approach (restart from Phase 2A)
3. Override gate (NOT RECOMMENDED)
4. Abort verification

---

## INITIALIZATION SEQUENCE

### 1. Module Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:
- `project_name`, `output_folder`, `user_name`, `communication_language`, `document_output_language`, `research_output_path`

### 2. First Step EXECUTION

Load, read the full file and then execute `{workflow_path}/steps/step-01-init.md` to begin the workflow.
