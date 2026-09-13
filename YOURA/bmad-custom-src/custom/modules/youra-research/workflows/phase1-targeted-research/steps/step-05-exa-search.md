---
name: 'step-05-exa-search'
description: 'Search GitHub repositories and additional resources via Exa MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-05-exa-search.md'
nextStepFile: '{workflow_path}/steps/step-06-chain-analysis.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 5: Exa GitHub and Additional Resources

## STEP GOAL:

Search GitHub repositories and additional resources via Exa MCP using queries generated in Step 2. Execute the exa-search skill to find implementations, tutorials, and code examples relevant to the research question.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Exa GitHub and resource search
- 🚫 FORBIDDEN to skip auto-resume check or skill execution
- ⚠️ MANDATORY: Execute exa-search skill via Skill tool
- 📋 Tag all results with [VERIFIED - EXA]

## EXECUTION PROTOCOLS:

- 🎯 Execute exa-search skill via Claude Code's Skill tool
- 💾 Save all resources with full URLs to output file
- 📖 Use queries from Step 2 as search inputs
- 🚫 FORBIDDEN to proceed without actual MCP call results

## CONTEXT BOUNDARIES:

- Available context: Queries from Step 2, research question
- Focus: Exa GitHub and implementation search only
- Limits: This is the final MCP search step
- Dependencies: Completed Step 4 with Scholar results

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:exa_implementations}}` filled.
- If filled → Skip to Step 6 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. Execute Exa Search Skill

**STOP and execute the exa-search skill NOW using Claude Code's Skill tool:**

```
Use the Skill tool with: skill: "exa-search"
```

This will load the complete skill instructions for Exa GitHub and implementation search.

### 3. Follow Skill Instructions

After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill (mcp__exa__web_search_exa, mcp__exa__get_code_context_exa)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's priority-based search strategy (Priority 1 → 5)
4. Tag all results with [VERIFIED - EXA]

### 4. Verify Skill Execution

**Verify skill execution by confirming:**
- [ ] exa-search skill was loaded via Skill tool
- [ ] At least 3 mcp__exa__web_search_exa or mcp__exa__get_code_context_exa calls were made
- [ ] Results are tagged with [VERIFIED - EXA], [VERIFIED - EXA - TUTORIAL], or [VERIFIED - EXA - CODE_CONTEXT]
- [ ] Each resource has a full URL
- [ ] Output follows the skill's template structure

**IF skill was NOT executed OR no MCP calls were made:**
HALT - You MUST execute the exa-search skill before continuing.

### 5. Save Progress

**Save progress after Step 5:**

1. Read {outputFile}
2. Replace `{{UNFILLED:exa_implementations}}` with implementations found
3. Replace `{{UNFILLED:exa_components}}` with component implementations
4. Replace `{{UNFILLED:exa_tutorials}}` with tutorial resources
5. Replace `{{UNFILLED:exa_code_analysis}}` with code analysis
6. Write file back
7. Display: "✅ Step 5 saved - X repositories and resources recorded"

### 6. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 6 (Chain-of-Relations) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [Exa results saved with proper tags and URLs], will you then load and read fully `{nextStepFile}` to execute and begin chain-of-relations analysis.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- exa-search skill executed via Skill tool
- At least 3 MCP calls made to Exa
- Results tagged with [VERIFIED - EXA]
- Each resource has full URL preserved
- Output file updated with implementations and tutorials
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- NOT executing exa-search skill via Skill tool
- Simulating or faking MCP call results
- Not preserving full URLs for resources
- Not tagging results with proper verification labels
- Proceeding without actual MCP call results

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
