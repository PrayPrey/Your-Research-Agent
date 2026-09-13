---
name: 'step-03-archon-search'
description: 'Search past cases and best practices via Archon MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-03-archon-search.md'
nextStepFile: '{workflow_path}/steps/step-04-scholar-search.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 3: Archon Knowledge Base Search

## STEP GOAL:

Search past cases and best practices via Archon MCP using queries generated in Step 2. Execute the archon-research skill to systematically search the knowledge base and collect relevant patterns, implementations, and code examples.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Archon Knowledge Base search
- 🚫 FORBIDDEN to skip auto-resume check or skill execution
- ⚠️ MANDATORY: Execute archon-research skill via Skill tool
- 📋 Tag all results with [VERIFIED - ARCHON]

## EXECUTION PROTOCOLS:

- 🎯 Execute archon-research skill via Claude Code's Skill tool
- 💾 Save all search results to output file with proper tags
- 📖 Use queries from Step 2 as search inputs
- 🚫 FORBIDDEN to proceed without actual MCP call results

## CONTEXT BOUNDARIES:

- Available context: Queries from Step 2, research question
- Focus: Archon Knowledge Base search only
- Limits: Do not search Scholar or Exa yet - only Archon
- Dependencies: Completed Step 2 with generated queries

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:archon_implementations}}` filled.
- If filled → Skip to Step 4 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. Execute Archon Research Skill

**STOP and execute the archon-research skill NOW using Claude Code's Skill tool:**

```
Use the Skill tool with: skill: "archon-research"
```

This will load the complete skill instructions for Archon Knowledge Base search.

### 3. Follow Skill Instructions

After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill (mcp__archon__rag_search_knowledge_base)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's hierarchical search strategy (Level 1 → Level 2 → Level 3)
4. Tag all results with [VERIFIED - ARCHON] as specified in the skill

### 4. Verify Skill Execution

**Verify skill execution by confirming:**
- [ ] archon-research skill was loaded via Skill tool
- [ ] At least 3 mcp__archon__rag_search_knowledge_base calls were made
- [ ] Results are tagged with [VERIFIED - ARCHON] or [INFERRED]
- [ ] Output follows the skill's template structure

**IF skill was NOT executed OR no MCP calls were made:**
HALT - You MUST execute the archon-research skill before continuing.

### 5. Save Progress

**Save progress after Step 3:**

1. Read {outputFile}
2. Replace `{{UNFILLED:archon_implementations}}` with implementations found
3. Replace `{{UNFILLED:archon_patterns}}` with patterns found
4. Replace `{{UNFILLED:archon_code_examples}}` with code examples (or `*No code examples found*`)
5. Write file back
6. Display: "✅ Step 3 saved - Archon KB search results recorded"

### 6. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 4 (Scholar Search) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [Archon search results saved with proper tags], will you then load and read fully `{nextStepFile}` to execute and begin Semantic Scholar paper search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- archon-research skill executed via Skill tool
- At least 3 MCP calls made to Archon Knowledge Base
- Results tagged with [VERIFIED - ARCHON]
- Output file updated with search results
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- NOT executing archon-research skill via Skill tool
- Simulating or faking MCP call results
- Not tagging results with proper verification labels
- Proceeding without actual MCP call results

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
