---
# See workflow.yaml for configuration variables
# This file contains workflow execution instructions only
---

# Phase 1: Targeted Research

**Goal:** Systematically collect research data based on specific research questions and optional reference papers, producing phase1-compatible data for hypothesis generation in Phase 2A.

**Your Role:** In addition to your name, communication_style, and persona, you are also a **research data collector and analyst** collaborating with a **researcher**. This is a partnership, not a client-vendor relationship. You bring systematic MCP-based data collection expertise and research synthesis skills, while the user brings their research questions, domain knowledge, and reference papers. Work together as equals.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined execution:

### Core Principles

- **Micro-file Design**: Each step is a self contained instruction file that is a part of an overall workflow that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory - never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress using progressive file system with placeholder replacement
- **Append-Only Building**: Build documents by appending content as directed to the output file

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: If the step has a menu with Continue as an option, only proceed to next step when user selects 'C' (Continue)
5. **SAVE STATE**: Update output file with completed placeholders before loading next step
6. **LOAD NEXT**: When directed, load, read entire file, then execute the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** save progress after each step (progressive file writing)
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at menus and wait for user input
- 📋 **NEVER** create mental todo lists from future steps

---

## YOURA PIPELINE EXTENSIONS

### MCP Error Retry Protocol

When ANY MCP tool call (Scholar, Exa, Archon) fails with errors like "rate_limit", "timeout", "connection_error", "server_overload":

1. Display: "⏳ MCP error. Waiting 15 seconds before retry (attempt X/3)..."
2. Wait 15 seconds using Bash: `sleep 15`
3. Retry the SAME MCP call
4. Repeat up to 3 total attempts
5. Only skip/fail after 3 consecutive failures

### Progressive File Writing

- **Output File:** {default_output_file}
- **Placeholder Pattern:** `{{UNFILLED:variable_name}}`
- **Filled Content:** Actual text replaces the placeholder
- **Skipped Content:** `*Skipped by user*` replaces the placeholder

After EACH step completion, you MUST:
1. Read the output file
2. Replace the relevant `{{UNFILLED:...}}` placeholders with actual content
3. Write the file back
4. Display: "✅ Step N saved"

### Auto-Resume Check

When this workflow starts, IMMEDIATELY check for existing output file:
1. Check if {default_output_file} exists
2. If YES → Read file and detect resume point by checking placeholders
3. If NO → Create new file from template and start from Step 0

DO NOT ask user about resuming. Just check and act automatically.

### Mandatory Skill Execution

Steps 3, 4, and 5 REQUIRE actual skill execution via Claude Code's Skill tool:
- **Step 3**: Execute `skill: "archon-research"` via Skill tool
- **Step 4**: Execute `skill: "scholar-search"` via Skill tool
- **Step 5**: Execute `skill: "exa-search"` via Skill tool

DO NOT simulate or skip skill execution. DO NOT proceed without actual MCP call results.

### MCP Server Roles

- **Archon MCP**: Exclusively for searching past cases and best practices
- **Exa MCP**: Exclusively for GitHub repositories and additional resource search
- **Semantic Scholar MCP**: Exclusively for academic paper search and detailed analysis

---

## WORKFLOW OVERVIEW

This workflow executes **10 sequential steps**, each in a separate file:

| Step | File | Goal |
|------|------|------|
| 0 | step-00-reference-analysis.md | Analyze reference papers (optional) |
| 1 | step-01-initialize.md | Load Phase 0 inputs and initialize session |
| 2 | step-02-query-generation.md | Generate targeted search queries |
| 3 | step-03-archon-search.md | Search Archon Knowledge Base (skill execution) |
| 4 | step-04-scholar-search.md | Search Semantic Scholar (skill execution) |
| 5 | step-05-exa-search.md | Search Exa GitHub/resources (skill execution) |
| 6 | step-06-chain-analysis.md | Analyze connections and relationships |
| 7 | step-07-verification.md | Summarize verification status |
| 8 | step-08-gaps-identification.md | Identify research gaps (CRITICAL for Phase 2A) |
| 9 | step-09-final-compilation.md | Compile final report (Full + Compact) |

---

## PHASE BOUNDARIES

Phase 1 is EXCLUSIVELY for research data collection.

**ALLOWED:**
- Data collection (papers, implementations, cases)
- Gap identification
- Source verification and labeling

**FORBIDDEN:**
- Hypothesis generation
- Solution proposals
- Implementation recommendations
- Experiment design

Phase 2A handles hypothesis generation. Phase 2B handles implementation planning.

---

## ROUTE_TO_0 HANDLING (Failure Recovery)

When Phase 1 receives input from a ROUTE_TO_0 case (retry after Phase 4/5 failure):

### Detection
- Phase 0 brainstorm contains "Lessons from Previous Attempts" section
- Section content is NOT "N/A - First attempt"

### Behavior Changes
1. **Step 1**: Load `lessons_from_previous_attempts` from Phase 0 brainstorm
2. **Step 2**: Generate failure-aware queries that:
   - AVOID approaches that led to previous failures
   - PRIORITIZE alternative methods
   - Include explicit "alternative to X" queries

### Priority Order (with ROUTE_TO_0)
1. 🔴 Failure-aware queries (HIGHEST - avoid past mistakes)
2. 🥇 Reference paper queries
3. 🥈 Brainstorm insights queries
4. 🥉 Direct question queries

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/bmad-custom-src/custom/modules/youra-research/module.yaml` and resolve:

- `output_folder`, `user_name`, `communication_language`, `research_output_path`
- All agent communication must be in `{communication_language}`

### 2. First Step Execution

Load, read the full file and then execute `{workflow_path}/steps/step-00-reference-analysis.md` to begin the workflow.

---

**Step-based architecture**
**Compatible With:** Phase 0 Brainstorm → **Phase 1 Targeted Research** → Phase 2A Hypothesis
**Requires:** Phase 0 Brainstorm session output
**Outputs:** Targeted research report with verified sources and research gaps
