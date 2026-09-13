---
name: 'step-07-verification'
description: 'Summarize verification status of all collected information'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-07-verification.md'
nextStepFile: '{workflow_path}/steps/step-08-gaps-identification.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 7: Verification Summary

## STEP GOAL:

Summarize verification status of all collected information from Steps 3-5. Calculate statistics, assess MCP server performance, and evaluate overall data quality for the research question.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on verification statistics and quality assessment
- 🚫 FORBIDDEN to skip auto-resume check
- 🔄 AUTO-RESUME CHECK: Execute before anything else
- 📋 Count all [VERIFIED] and [UNVERIFIED] tags from previous steps

## EXECUTION PROTOCOLS:

- 🎯 Calculate verification statistics from collected data
- 💾 Save verification summary to output file
- 📖 Assess MCP server performance metrics
- 🚫 FORBIDDEN to modify or re-verify collected data

## CONTEXT BOUNDARIES:

- Available context: All data from Steps 3-5 with verification tags
- Focus: Statistics, performance metrics, quality scores
- Limits: Do not re-collect or modify data
- Dependencies: Completed Steps 3-5 and Step 6 analysis

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:verification_statistics}}` filled.
- If filled → Skip to Step 8 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. Calculate Verification Statistics

Summarize verification status of all collected information:

**Statistics:**
- Total sources: XX
- [VERIFIED]: XX (XX%)
- [UNVERIFIED]: XX (XX%)
- [NOT_FOUND]: XX (XX%)

### 3. Assess MCP Server Performance

Record MCP server performance:

**MCP Server Performance:**
- Archon: XX queries, XX ms avg response
- Semantic Scholar: XX queries, XX ms avg response
- Exa: XX queries, XX ms avg response

### 4. Evaluate Data Quality

Assess overall data quality:

**Data Quality Assessment:**
- Completeness: XX/100
- Reliability: XX/100
- Recency: XX/100
- Relevance to Question: XX/100

### 5. Save Progress

**Save progress after Step 7:**

1. Read {outputFile}
2. Replace `{{UNFILLED:verification_statistics}}` with source statistics
3. Replace `{{UNFILLED:mcp_performance}}` with MCP server performance
4. Replace `{{UNFILLED:data_quality_assessment}}` with quality scores
5. Write file back
6. Display: "✅ Step 7 saved - Verification summary recorded"

### 6. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 8 (Gaps Identification) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [verification summary saved], will you then load and read fully `{nextStepFile}` to execute and begin research gaps identification.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- Verification statistics calculated
- MCP server performance recorded
- Data quality assessed
- All metrics saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- Not calculating verification statistics
- Not assessing data quality
- Not saving metrics to output file
- Not presenting menu for user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
