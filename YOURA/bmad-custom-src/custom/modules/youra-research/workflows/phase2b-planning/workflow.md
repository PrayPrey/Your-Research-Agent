---
name: phase2b-planning
description: Creates detailed verification roadmap from Phase 2A hypothesis with dynamic sub-hypotheses, DAG + Gantt visualizations, and Transfer Validation integration
web_bundle: false
---

# Phase 2B: Verification Planning Workflow

<critical>The workflow execution engine is governed by: {project-root}/_bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {installed_path}/workflow.yaml</critical>
<critical>Communicate in {communication_language} throughout the workflow</critical>

**Goal:** Decompose the validated hypothesis from Phase 2A-Dialogue (03_refinement.yaml) into hierarchical sub-hypotheses (3-7 dynamic), dependency graph (DAG) and execution roadmap, risk analysis and mitigation strategies, and dialectical analysis for robust verification.

**Your Role:** In addition to your name, communication_style, and persona, you are also a **Research Verification Planning Specialist** collaborating with a researcher. This is a partnership, not a client-vendor relationship. You bring systematic verification expertise, research methodology knowledge, and hypothesis decomposition skills, while the user brings domain expertise, hypothesis context, and research goals. Work together as equals.

---

## BMAD CUSTOM MODULE STANDARD

<notice>
**Custom Module Structure (YouRA Research Module)**

This workflow uses a **split-file architecture** which is a valid BMAD custom module standard:

| File | Purpose | BMAD Equivalent |
|------|---------|-----------------|
| `workflow.yaml` | Configuration, variables, MCP settings | workflow.md frontmatter |
| `workflow.md` | Execution instructions, step architecture | workflow.md body |

**Rationale:**
- Separates configuration from execution logic
- Enables YAML validation for config
- Allows independent updates to config vs instructions
- Maintains compatibility with BMAD workflow engine

**Loading Order:**
1. Load `workflow.yaml` first (configuration)
2. Load `workflow.md` second (execution)
3. Execute step files as directed

This is a **documented exception** to the single workflow.md standard.
</notice>

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self contained instruction file that is a part of an overall workflow that must be followed exactly
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

### YouRA-Specific Rules (Domain Extension)

- 🔵 **MANDATORY**: Preserve Established Facts from Phase 2A Dialogue
- 🔵 **MANDATORY**: Include Transfer Validation section (if cross-domain transfer)
- 🔵 **MANDATORY**: Define at least H-E and H-M sub-hypotheses (H-C optional)
- 🛑 **FORBIDDEN**: Skip risk analysis
- 🛑 **FORBIDDEN**: Proceed without dialectical evaluation

> **Note:** H-CP (Comparison) hypotheses have been moved to Phase 5 Baseline Comparison. Phase 2B now focuses on H-E, H-M, and optional H-C sub-hypotheses.

---

## PROGRESSIVE FILE SYSTEM

<critical>
**PROGRESSIVE FILE WRITING - MANDATORY**

**Output File:** {default_output_file}
**Placeholder Pattern:** `{{UNFILLED:variable_name}}`

**RULE:** After EACH step completion:
1. Replace relevant `{{UNFILLED:...}}` placeholders with content
2. Write the file back
3. Display: "Step N saved"
</critical>

### Step-to-Placeholder Mapping

| Step | Placeholders to Fill |
|------|---------------------|
| 0 | (Initialization only - no placeholders) |
| 1 | (Parse Phase 2A - no placeholders) |
| 2 | `hypothesis_id`, `confidence_level`, `total_hypothesis_count`, `core_hypothesis_statement`, `alternative_hypothesis_h0`, `baseline_table`, `assumptions_table`, `gap_and_novelty`, `selected_dataset_*`, `selected_model_*` |
| 3 | (Interactive hypothesis generation - no template placeholders) |
| 4 | `hypothesis_inventory_table`, `all_hypotheses_specs` |
| 5 | `risk_analysis`, `risk_hypothesis_mapping`, `mitigation_strategies`, `risk_summary_table` |
| 6 | `dependency_graph`, `dependency_hierarchy` |
| 7 | `gantt_timeline`, `critical_path_analysis`, `resource_summary`, `execution_order` |
| 8 | `dialectical_analysis`, `thesis_statement`, `antithesis_development`, `synthesis`, `robustness_assessment` |
| 9 | `executive_summary`, `final_summary`, `conclusions`, `appendices` |
| 10 | `verification_state_status`, `pipeline_tasks_updated`, `hypothesis_tasks_created` |

---

## RESUME CHECK

<critical>
**AUTO-RESUME CHECK**

1. Check if {default_output_file} exists
2. If YES: Detect resume point from first unfilled placeholder
3. If NO: Create new file from template, start Step 0
</critical>

---

## STEP NUMBERING CONVENTION

<notice>
**0-Indexed Step Numbering (YouRA Research Module)**

This workflow uses 0-indexed step numbering with **11 steps** (step-00 through step-10):

| Step | Type | Purpose |
|------|------|---------|
| step-00 | `initialization` | Environment setup, MCP verification (NO output placeholders) |
| step-01 | `initialization` | Parse Phase 2A Dialogue data (NO output placeholders) |
| step-02 to step-09 | `core` | Main workflow logic with output placeholders |
| step-10 | `finalization` | State files, Archon tasks, completion |

**Rationale:**
- Step-00 and Step-01 perform setup before actual workflow begins
- Clearly distinguishes initialization from core logic
- Follows programming convention (0-indexed)
- Step-00 and Step-01 produce no output to template (setup only)

This is a **documented exception** to the 1-indexed step standard.
</notice>

---

## MCP TOOL REQUIREMENTS

### Mode-Dependent MCP Usage

**Two Modes:**
1. **Incremental Mode**: Phase 2A Dialogue available → 4-6 MCP calls (optimized)
2. **Comprehensive Mode**: No Phase 2A → 10-14 MCP calls (full analysis)

**Incremental Mode (4-6 MCP calls):**

| Step | MCP Tool | Calls | Purpose |
|------|----------|-------|---------|
| 2 | `mcp__clearThought__collaborativereasoning` | 1x | Validate Phase 2A risks + identify new |
| 3 | `mcp__clearThought__sequentialthinking` | 1x | Validate Phase 2A causal chain (dynamic length) |
| 4 | `mcp__clearThought__scientificmethod` | 1-3x | H-E verification + mechanism (scales with causal chain length) |
| 6 | `mcp__clearThought__structuredargumentation` | 1x | Main hypothesis dialectical analysis only |

**Total: 4-6 MCP calls** (scales with hypothesis count, vs 15-21 in comprehensive)

**Additional Tools (Optional):**
- **Archon MCP**: Past failure case analysis (Step 2)
- **Exa MCP**: Additional research (if needed)

**Comprehensive Mode (10-14 MCP calls):**

| Step | MCP Tool | Calls | Purpose |
|------|----------|-------|---------|
| 2 | `mcp__clearThought__collaborativereasoning` | 1x | Multi-expert risk analysis |
| 3 | `mcp__clearThought__sequentialthinking` | 1x | Systematic decomposition |
| 4 | `mcp__clearThought__scientificmethod` | 3-5x | Each hypothesis type |
| 6 | `mcp__clearThought__structuredargumentation` | 5-7x | All critical hypotheses |

**Total: 10-14 MCP calls**

---

## WORKFLOW OVERVIEW

**Purpose:** Create detailed verification roadmap from Phase 2A hypothesis

- Incremental Mode: **3-7 hypotheses** (dynamic, based on Phase 2A structure)
  - Minimum (3): H-E1, H-M(integrated), H-CP1
  - Default (5): H-E1, H-M1-3, H-CP1 (when 3-step causal chain)
  - Extended (7): H-E1-2, H-M1-N, H-C1, H-CP1 (when conditions need verification)
- Hypothesis specs: 100-200 words (maintained for verification clarity)
- DAG + Gantt timeline: ALWAYS generated (adapts to hypothesis count)
- 4-6 MCP calls total (scales with complexity)
- Target execution time: 8-12 minutes (varies with hypothesis count)

**Phase 2A Compatibility:**
- **Established Facts Integration**: Loads from Phase 2A Dialogue (03_refinement.yaml)
  - Established Facts Registry passed through (DO NOT RE-TEST)
  - Builds-On vs. Proves-New separation applied
  - Only generates hypotheses for "PROVE NEW" claims
- **Scope Reduction**: Calculates efficiency gain from skipping BUILD ON claims
- **Cross-Domain Transfer Validation** (OPTIONAL): Loaded from Phase 2A Dialogue if present
  - Only applicable if hypothesis involves cross-domain mechanism transfer
  - If present: Transfer validation criteria included in H-M hypotheses
  - If absent: Skip transfer validation (most hypotheses)

**Flexibility:** Dynamic hypothesis count based on Phase 2A structure + user choice for condition hypotheses.

---

## STEP FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2B: VERIFICATION PLANNING │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ INITIALIZATION BLOCK │
│ step-00-init-environment → step-01-init-parsing │
│ (MCP/Pipeline check) (Phase 2A parsing) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ INPUT BLOCK │
│ step-02-input-hypothesis │
│ (Verify/edit loaded data) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ HYPOTHESIS BLOCK │
│ step-03-hypothesis-generation → step-04-hypothesis-inventory │
│ (MCP scientificmethod) (Specs & inventory table) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ RISK BLOCK │
│ step-05-risk-analysis │
│ (Assumption risks + Mitigation) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ EXECUTION PLAN BLOCK │
│ step-06-dependency-graph → step-07-timeline-planning │
│ (DAG visualization) (Gantt + gates) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ DIALECTICAL BLOCK │
│ step-08-dialectical-analysis │
│ (Thesis-Antithesis-Synthesis) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ FINALIZATION BLOCK │
│ step-09-summary → step-10-finalize │
│ (Executive summary) (State file + Archon tasks) │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                         ┌──────────┐
                         │ COMPLETE │
                         └──────────┘
```

---

## WORKFLOW STEPS

### Step 0: Initialize Environment
- Welcome user
- Verify MCP services (Archon, ClearThought, Exa)
- Check pipeline status in Archon
- Set research mode based on Phase 2A availability

**Type:** `initialization` (no output placeholders)
**File:** `{workflow_path}/steps/step-00-init-environment.md`

---

### Step 1: Parse Phase 2A Dialogue Data
- Load Phase 2A Dialogue output file (if available)
- Parse all Phase 2A sections systematically
- Extract hypothesis variables for verification planning
- Transform raw Phase 2A data into structured variables

**Type:** `initialization` (no output placeholders)
**File:** `{workflow_path}/steps/step-01-init-parsing.md`

---

### Step 2: Input and Verify Hypothesis
- **Incremental**: Verify loaded Phase 2A data
- **Comprehensive**: Collect hypothesis input (load from file, direct input, or search recent)
- Extract baseline paper metrics for comparison targets
- Confirm with user before proceeding

**File:** `{workflow_path}/steps/step-02-input-hypothesis.md`

---

### Step 3: Sub-Hypothesis Generation with MCP
- Call `mcp__clearThought__scientificmethod`
- Generate sub-hypotheses based on Phase 2A causal chain length
- Apply scope reduction from Established Facts
- Apply transfer validation if applicable
- Dynamic hypothesis count based on causal chain length

**File:** `{workflow_path}/steps/step-03-hypothesis-generation.md`

---

### Step 4: Hypothesis Specifications & Inventory
- Create detailed specifications for each generated hypothesis
- Compile the hypothesis inventory table
- Each specification follows streamlined format (40-50 lines)
- Include verification protocols for each hypothesis

**File:** `{workflow_path}/steps/step-04-hypothesis-inventory.md`

---

### Step 5: Risk Analysis
- Identify risks from Phase 2A key assumptions (A1-A5)
- Map risks to hypotheses
- Develop mitigation strategies
- Call `mcp__clearThought__collaborativereasoning` with expert panel
- Optional: Search Archon MCP for past failure cases

**File:** `{workflow_path}/steps/step-05-risk-analysis.md`

---

### Step 6: Dependency Graph (DAG)
- Analyze hypothesis dependencies
- Build dependency graph (DAG) showing verification order
- Define verification phases with gate conditions
- Generate ASCII DAG visualization

**File:** `{workflow_path}/steps/step-06-dependency-graph.md`

---

### Step 7: Timeline Planning (Gantt)
- Generate Gantt timeline visualization (ASCII)
- Calculate critical path analysis
- Create resource summary
- Define execution order for hypotheses

**File:** `{workflow_path}/steps/step-07-timeline-planning.md`

---

### Step 8: Dialectical Analysis
- Call `mcp__clearThought__structuredargumentation`
- Perform Thesis-Antithesis-Synthesis dialectical evaluation
- Use null hypothesis (H0) from Phase 2A for opposing viewpoint
- Generate robustness assessment
- **Incremental**: 1 call (Main Hypothesis vs H0)
- **Comprehensive**: Multiple calls (all critical hypotheses)

**File:** `{workflow_path}/steps/step-08-dialectical-analysis.md`

---

### Step 9: Executive Summary & Conclusions
- Write executive summary (bullet-point format, concise)
- Document conclusions: achievements, execution order, decision points
- Add open questions and recommendations
- Add appendices (minimal, non-redundant)

**File:** `{workflow_path}/steps/step-09-summary.md`

---

### Step 10: Finalize & State Generation
- **CRITICAL: Generate verification_state.yaml** with all hypotheses, gates, and dependencies
- Update pipeline tasks in Archon
- Create hypothesis tasks in Archon
- Display workflow complete message
- **CRITICAL: Per-hypothesis context files** ({hypothesis_folder}/02b_context.md) are generated JIT by Phase 2C

**File:** `{workflow_path}/steps/step-10-finalize.md`

**IMPORTANT:** Step 10 has MANDATORY post-output actions (state file + Archon tasks). Do NOT skip!

---

## DYNAMIC HYPOTHESIS TYPES

| Type | Prefix | Purpose | Count |
|------|--------|---------|-------|
| **Existence** | H-E | Validate phenomenon exists | 1-2 |
| **Mechanism** | H-M | Test causal chain steps | 1-5 |
| **Condition** | H-C | Boundary conditions (optional) | 0-2 |

**Total: 2-7 sub-hypotheses** (auto-detected from Phase 2A causal chain length)

> **Note:** H-CP (Comparison) hypotheses are now handled exclusively in Phase 5 Baseline Comparison, not in Phase 2B.

---

## MCP SERVER REQUIREMENTS

| Server | Purpose | Required Tools |
|--------|---------|----------------|
| **Archon** | Past failure cases, task management | `rag_search_knowledge_base`, `find_tasks`, `manage_task` |
| **ClearThought** | Multi-method reasoning | `sequentialthinking`, `mentalmodel`, `scientificmethod`, `structuredargumentation`, `collaborativereasoning` |
| **Exa** | Verification approaches | `web_search_exa` |

---

## PIPELINE POSITION

```
Phase 0 → Phase 1 → Phase 2A-Dialogue → [Phase 2B] → (2C → 3 → 4) × N → 4.5 → [5] → 6 → 6.5 → 6.5.1
```

### Inputs
- `03_refinement.yaml` (required) - Phase 2A-Dialogue output with validated hypothesis, variables, and H0
- `02_synthesis.yaml` (optional) - Phase 2A synthesis for additional context

### Outputs
- `02b_verification_plan.md` - Complete verification roadmap
- `verification_state.yaml` - State tracking for hypothesis verification loop
- Per-hypothesis context files generated JIT by Phase 2C

---

## KEY OUTPUT SECTIONS

1. **Section 0**: Established Facts & Scope Reduction
2. **Section 0.5**: Transfer Validation (OPTIONAL - only if cross-domain transfer)
3. **Section 1**: Hypothesis Overview
4. **Section 2**: Risk Analysis
5. **Section 3**: Hierarchical Structure
6. **Section 4**: Sub-Hypothesis Inventory (H-E, H-M, H-C)
7. **Section 5**: Dependency Graph (DAG + Gantt)
8. **Section 6**: Dialectical Analysis
9. **Section 7**: Executive Summary & Appendices

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from {project-root}/_bmad/bmb/config.yaml and resolve:

- `user_name`, `communication_language`, `document_output_language`

Load workflow configuration from: `workflow.yaml`

Key variables:
- `{research_output_path}`: Output directory
- `{hypothesis_config}`: Dynamic hypothesis count settings (min: 3, max: 7)

### 2. First Step Execution

Load, read the full file and then execute `{workflow_path}/steps/step-00-init-environment.md` to begin the workflow.

---

## SUCCESS CRITERIA

- ✅ 3-7 sub-hypotheses defined with clear verification criteria
- ✅ Risk analysis covers all key assumptions with mitigation strategies
- ✅ Dependency graph shows execution order
- ✅ Dialectical analysis provides balanced evaluation (Thesis-Antithesis-Synthesis)
- ✅ Established Facts properly scoped out
- ✅ Pipeline task updated in Archon
- ✅ verification_state.yaml created for Phase 2C integration
