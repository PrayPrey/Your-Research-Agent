---
name: 'step-01-initialize'
description: 'Load Phase 0 inputs and initialize targeted research session'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-01-initialize.md'
nextStepFile: '{workflow_path}/steps/step-02-query-generation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'

# Template References
outputTemplate: '{workflow_path}/template.md'
---

# Step 1: Initialize Research Pipeline

## STEP GOAL:

Load Phase 0 Brainstorm session inputs (research_question, detailed_question, reference_papers) and initialize the targeted research session. Verify Archon Pipeline status and prepare output file for progressive data collection.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on loading Phase 0 inputs and initializing session
- 🚫 FORBIDDEN to skip auto-resume check or pipeline verification
- 🔄 AUTO-RESUME CHECK: Execute before anything else
- 📋 Halt workflow if Phase 0 Brainstorm session is not found

## EXECUTION PROTOCOLS:

- 🎯 Verify Archon Pipeline status before proceeding
- 💾 Create or update output file with research question
- 📖 Load complete Phase 0 Brainstorm session data
- 🚫 FORBIDDEN to proceed without valid Phase 0 input

## CONTEXT BOUNDARIES:

- Available context: Phase 0 Brainstorm session file
- Focus: Session initialization, input validation, pipeline verification
- Limits: Do not start data collection yet - only initialization
- Dependencies: Completed Phase 0 Brainstorm with research_question

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Before starting this step, check if output file already exists:

1. Check if {outputFile} exists
2. If YES → Read file and check for `{{UNFILLED:research_question}}`
3. If `{{UNFILLED:research_question}}` is FILLED → Skip to Step 2 (load {nextStepFile})
4. If NO file exists → Create from template and proceed with this step

**DO NOT ask user about resuming. Just check and act automatically.**

### 2. Pipeline Status Verification (Archon)

Verify Pipeline Project exists and Phase 1 is the current phase.

**Check Pipeline Status:**

```
1. Find Pipeline Project:
   - Read Phase 0 output to get pipeline_project_title from frontmatter
   - Search Archon: mcp__archon__find_projects(query=pipeline_project_title)
   - If not found by title, fallback: mcp__archon__find_projects(query="Anonymous Pipeline")

2. Verify Phase 1 is current:
   - mcp__archon__find_tasks(project_id=pipeline_project_id, filter_by="status", filter_value="doing")
   - Expected: "Phase 1 - Research" should be "doing"
```

| Result | Action |
|--------|--------|
| **"Phase 1 - Research" doing** | ✅ Correct, proceed |
| **"Phase 0 - Brainstorm" doing** | → Phase 0 not complete, redirect user |
| **Other phase doing** | → Pipeline out of sync, ask user |
| **Not Found** | → ERROR: Pipeline missing, ask user to run Phase 0 first |

Display if correct:
```
✅ **Pipeline Status Verified**
• Current Phase: Phase 1 - Research [doing]
• Previous: Phase 0 - Brainstorm [done]
```

**Store Pipeline IDs for Step 9:**
- `pipeline_project_id`: Project UUID
- `phase1_task_id`: Phase 1 Task UUID
- `phase2a_task_id`: Phase 2A Task UUID

### 3. Greeting

Greet {user_name} in {communication_language}:
"Hello {user_name}, starting Phase 1: Targeted Research."

### 4. Load Phase 0 Brainstorm Session

**IF brainstorm_session file exists:**

1. Load Phase 0 Brainstorm session file
2. Extract from "phase1-input" section:
   - research_question: From "### research_question" section
   - detailed_question: From "### detailed_question" section (may be empty)
   - reference_papers: From "### reference_papers" section (may be empty)
3. Extract from "## Session Insights" section:
   - key_insights: From "### Key Discoveries"
   - techniques_used: From "### Techniques Used"
   - areas_for_exploration: From "### Areas for Further Exploration"
4. **Extract from "## Lessons from Previous Attempts" section (ROUTE_TO_0 case):**
   - lessons_from_previous_attempts: From the section content
   - If section contains "N/A - First attempt" → Set to empty/null
   - If section contains actual lessons → Store for Step 2 query filtering
5. Store complete brainstorm context

Display to {user_name} in {communication_language}:
```
📋 Inputs loaded from Phase 0 Brainstorm session:

**Research Inputs:**
- Research Question: {research_question}
- Detailed Question: {detailed_question} (or 'Not provided')
- Reference Papers: {reference_papers} (or 'Not provided')

**Session Insights:**
- Key Discoveries: {key_insights}
- Areas for Exploration: {areas_for_exploration}

**Failure Context (ROUTE_TO_0):**
- Lessons from Previous Attempts: {lessons_from_previous_attempts} (or 'N/A - First attempt')

ℹ️ Note: This is targeted research mode (reference paper based).
For broad research, use phase1-research.
```

**IF NO brainstorm_session file found:**

Stop workflow and notify {user_name}:

```
⚠️ Phase 0 Brainstorm session not found.

Phase 1 requires research questions from Phase 0 Brainstorm.

Please run Phase 0 first:
/phase0-brainstorm

Phase 0 will help you:
- Discover and refine research questions
- Identify detailed sub-questions
- Optionally find relevant reference papers

After Phase 0 completes, run Phase 1 again.
```

**HALT workflow execution until Phase 0 is completed.**

### 5. Confirm Inputs

Ask user to confirm inputs are correct:

"Does this look correct?
[C] Continue / [E] Edit inputs"

If E: Allow user to modify research_question, detailed_question, or reference_papers.

### 6. Create Output Directory and Verify MCP

1. Create output directory if needed: {outputFile}
2. Verify MCP server connection status
3. Communicate all responses in {communication_language}

### 7. Initialize Output File

If output file doesn't exist, create from template with header section:

```markdown
# Targeted Research Report: {research_question}
Date: {date}
Phase: 1 - Targeted Research Gathering

## Executive Summary

### Research Question
{research_question}

### Detailed Question
{detailed_question}

### Approach
This report focuses on targeted research to address the specific research question above, utilizing MCP tools to gather relevant academic papers, implementation examples, and past cases.
```

### 8. Save Progress

**Save progress after Step 1:**

1. Read {outputFile} (or create from template if not exists)
2. Replace `{{UNFILLED:research_question}}` with {research_question}
3. Replace `{{UNFILLED:primary_research_question}}` with {research_question}
4. Replace `{{UNFILLED:detailed_questions}}` with {detailed_question} (or `*Not provided*`)
5. Replace `{{UNFILLED:lessons_from_previous_attempts}}` with:
   - If lessons exist: The extracted lessons content
   - If no lessons (first attempt): `*N/A - First attempt*`
6. Write file back
7. Display: "✅ Step 1 saved - Research question recorded"

### 9. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 2 (Query Generation) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [Phase 0 inputs loaded and confirmed], will you then load and read fully `{nextStepFile}` to execute and begin query generation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- Pipeline status verified via Archon
- Phase 0 Brainstorm session loaded successfully
- User confirmed inputs are correct
- Output file initialized with research question
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check or pipeline verification
- Proceeding without valid Phase 0 Brainstorm session
- Not confirming inputs with user
- Not saving progress to output file
- Not presenting menu for user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
