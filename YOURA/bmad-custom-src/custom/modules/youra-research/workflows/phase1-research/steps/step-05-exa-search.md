---
name: 'step-05-exa-search'
description: 'Search GitHub repositories and implementation resources using Exa MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-05-exa-search.md'
nextStepFile: '{workflow_path}/steps/step-06-chain-analysis.md'
---

# Step 5: Exa GitHub and Additional Resources

**Goal:** Search GitHub repositories and implementation resources using Exa MCP

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP

This step REQUIRES executing the exa-search skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 6 until this skill has been executed and results obtained.
</critical>

<critical>
🔄 **MCP ERROR RETRY PROTOCOL**

When ANY MCP tool call fails:
1. Display: "⏳ MCP error. Waiting 15 seconds before retry (attempt X/3)..."
2. Wait 15 seconds: `sleep 15`
3. Retry the SAME MCP call
4. Repeat up to 3 total attempts
5. Only skip/fail after 3 consecutive failures
</critical>

<critical>
🔄 **RESUME CHECK**

Before starting:
1. Read {default_output_file}
2. Check if `{{UNFILLED:exa_repositories}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Execute Exa Search Skill

<action>
STOP and execute the exa-search skill NOW:

```
Use the Skill tool with: skill: "exa-search"
```

This will load complete skill instructions for Exa GitHub and implementation search.
</action>

### 2. Follow Skill Instructions

<action>
After the skill loads, you MUST:

1. Execute ALL MCP calls specified (mcp__exa__web_search_exa, mcp__exa__get_code_context_exa)
2. Use queries generated in Step 2 as search inputs
3. Follow skill's priority-based search strategy (Priority 1 → 5)
4. Tag all results with [VERIFIED - EXA]
5. Apply MCP ERROR RETRY PROTOCOL to all calls
</action>

### 3. Verify Skill Execution

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>
  HALT - You MUST execute the exa-search skill before continuing.
  </critical>

  <action>
  1. Execute: Skill tool with skill: "exa-search"
  2. Make actual Exa MCP calls
  </action>
</check>

<action>
Verify skill execution:
- [ ] exa-search skill loaded via Skill tool
- [ ] At least 3 mcp__exa__web_search_exa or mcp__exa__get_code_context_exa calls made
- [ ] Results tagged with [VERIFIED - EXA], [VERIFIED - EXA - TUTORIAL], or [VERIFIED - EXA - CODE_CONTEXT]
- [ ] Each resource has full URL
- [ ] Output follows skill's template structure
</action>

### 4. Display Results Summary

<action>
Display to user in {communication_language}:

```
🔍 Exa search complete

**Items Found:**
- GitHub repositories: X
- Additional resources (tutorials, blogs): Y
- Code context analyses: Z

All results were marked with [VERIFIED - EXA] tags and full URLs.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 5:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:exa_repositories}}` with GitHub repositories found
3. Replace `{{UNFILLED:exa_additional_resources}}` with additional resources
4. Replace `{{UNFILLED:exa_code_analysis}}` with code analysis summary
5. Update frontmatter: Add "step-05-exa-search" to stepsCompleted array
6. Write file back
7. Display: "✅ Step 5 saved - X repositories and resources recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 6 (Chain-of-Relations Analysis)
[B] Back - Return to Step 4
[R] Retry - Re-run Exa search
</menu>

<critical>
⚠️ DO NOT allow [S] Skip - Exa search is MANDATORY
</critical>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Verify Exa search performed (check for [VERIFIED - EXA] tags and URLs)
2. If verification fails, HALT and require re-execution
3. Update frontmatter stepsCompleted: [...previous, "step-05-exa-search"]
4. Load and execute: {workflow_path}/steps/step-06-chain-analysis.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-04-scholar-search.md
</on-back>

<on-retry>
When user selects [R] Retry:
1. Clear current Exa results
2. Re-execute this step
</on-retry>
