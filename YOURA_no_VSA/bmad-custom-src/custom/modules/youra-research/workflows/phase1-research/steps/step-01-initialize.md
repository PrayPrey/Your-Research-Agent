---
name: 'step-01-initialize'
description: 'Load Phase 0 inputs and initialize research session'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-01-initialize.md'
nextStepFile: '{workflow_path}/steps/step-02-query-generation.md'
---

# Step 1: Initialize Research Pipeline

**Goal:** Load Phase 0 inputs and initialize research session

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
🔄 **AUTO-RESUME CHECK - EXECUTE FIRST**

Before starting this step, check if output file already exists:
1. Check if {default_output_file} exists
2. If YES → Read file and check for `{{UNFILLED:research_topic}}`
3. If `{{UNFILLED:research_topic}}` is FILLED → Skip to next step
4. If NO file exists → Create from template and proceed with this step

**DO NOT ask user about resuming. Just check and act automatically.**
</critical>

---

## Step Instructions

### 1. Greeting

<action>
Greet {user_name} in {communication_language}:
"Hello {user_name}, starting Phase 1: broad research gathering."
</action>

### 2. Load Phase 0 Brainstorm Session

<check if="brainstorm_session file exists OR data attribute was passed">

<action>
1. Load Phase 0 Brainstorm session file
2. Extract from "phase1-input" section:
   - research_question: From "### research_question" section
   - detailed_question: From "### detailed_question" section (may be empty)
3. Extract from "## Session Insights" section:
   - key_insights: From "### Key Discoveries"
   - techniques_used: From "### Techniques Used"
   - areas_for_exploration: From "### Areas for Further Exploration"
4. Store complete brainstorm context
</action>

<action>
Display to {user_name} in {communication_language}:
```
📋 Loaded inputs from the Phase 0 Brainstorm session:

**Research Inputs:**
- Research question: {{research_question}}
- Detailed question: {{detailed_question}} (or 'Not provided')

**Session Insights:**
- Key discoveries: {{key_insights}}
- Areas for further exploration: {{areas_for_exploration}}

ℹ️ Note: This is broad research mode (no reference papers).
Use *targeted-research for focused research with reference papers.
```
</action>

<ask>
Does this look correct?
[c] Continue / [e] Edit inputs
</ask>

</check>

<check if="no brainstorm_session file found">

<action>
Stop the workflow and notify {user_name}:

```
⚠️ Phase 0 Brainstorm session not found.

Phase 1 requires a research question from Phase 0 Brainstorm.

Run Phase 0 first:
*brainstorm

Phase 0 helps with:
- Discovering and refining research questions
- Identifying detailed subquestions
- Optionally finding relevant reference papers

Run Phase 1 again after Phase 0 is complete.
```
</action>

<critical>Stop workflow execution until Phase 0 is complete</critical>

</check>

### 3. Create Output Directory and Verify MCP

<action>
1. Create output directory if needed: {{default_output_file}}
2. Verify MCP server connection status
3. Communicate all responses in {communication_language}
</action>

### 4. Initialize Output File

<action>
If output file doesn't exist, create from template with header section:

```markdown
# Deep Learning Research Report: {{research_question}}
Date: {date}
Phase: 1 - Broad Research Gathering

## Executive Summary

### Research Question
{{research_question}}

### Detailed Question
{{detailed_question}}

### Approach
This report uses BROAD exploration to gather comprehensive research data without specific reference paper constraints. Ideal for initial exploration of a research area.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 1:**

1. Read {default_output_file} (or create from template if not exists)
2. Replace `{{UNFILLED:research_topic}}` with {{research_question}}
3. Replace `{{UNFILLED:primary_research_question}}` with {{research_question}}
4. Replace `{{UNFILLED:detailed_questions}}` with {{detailed_question}} (or `*Not provided*`)
5. Update frontmatter: Add "step-01-initialize" to stepsCompleted array
6. Write file back
7. Display: "✅ Step 1 saved - research question recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 2 (Query Generation)
[B] Back - Exit workflow
[R] Retry - Re-run Step 1
</menu>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Update frontmatter stepsCompleted: ["step-01-initialize"]
2. Load and execute: {workflow_path}/steps/step-02-query-generation.md
</on-continue>
