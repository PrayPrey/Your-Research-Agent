---
name: 'step-04-scholar-search'
description: 'Search academic papers using Semantic Scholar MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-04-scholar-search.md'
nextStepFile: '{workflow_path}/steps/step-05-exa-search.md'
---

# Step 4: Semantic Scholar Paper Search

**Goal:** Search academic papers using Semantic Scholar MCP

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP

This step REQUIRES executing the scholar-search skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 5 until this skill has been executed and results obtained.
</critical>

<critical>
🔄 **MCP ERROR RETRY PROTOCOL - APPLY TO ALL MCP CALLS**

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
2. Check if `{{UNFILLED:scholar_core_papers}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Execute Scholar Search Skill

<action>
STOP and execute the scholar-search skill NOW:

```
Use the Skill tool with: skill: "scholar-search"
```

This will load complete skill instructions for Semantic Scholar paper search.
</action>

### 2. Follow Skill Instructions

<action>
After the skill loads, you MUST:

1. Execute ALL MCP calls specified (mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search, etc.)
2. Use queries generated in Step 2 as search inputs
3. Follow skill's targeted search strategy (Round 1 → Round 2 → Round 3 → Round 4)
4. Tag all results with [VERIFIED - SCHOLAR]
5. Apply MCP ERROR RETRY PROTOCOL to all calls
</action>

### 3. Verify Skill Execution

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>
  HALT - You MUST execute the scholar-search skill before continuing.
  </critical>

  <action>
  1. Execute: Skill tool with skill: "scholar-search"
  2. Make actual Semantic Scholar MCP calls
  </action>
</check>

<action>
Verify skill execution:
- [ ] scholar-search skill loaded via Skill tool
- [ ] At least 5 mcp__hamid-vakilzadeh-mcpsemanticscholar__* calls made
- [ ] Results tagged with [VERIFIED - SCHOLAR]
- [ ] Each paper has Semantic Scholar ID and URL
- [ ] Output follows skill's template structure
</action>

### 4. Display Results Summary

<action>
Display to user in {communication_language}:

```
📄 Semantic Scholar paper search complete

**Items Found:**
- Core papers: X
- Citation analysis links: Y
- Total citations: Z

All results were marked with [VERIFIED - SCHOLAR] tags and SS IDs.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 4:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:scholar_core_papers}}` with verified papers list
3. Replace `{{UNFILLED:scholar_citation_network}}` with citation analysis
4. Update frontmatter: Add "step-04-scholar-search" to stepsCompleted array
5. Write file back
6. Display: "✅ Step 4 saved - X academic papers recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 5 (Exa GitHub and Additional Resources)
[B] Back - Return to Step 3
[R] Retry - Re-run Scholar search
</menu>

<critical>
⚠️ DO NOT allow [S] Skip - Scholar search is MANDATORY
</critical>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Verify Scholar search performed (check for [VERIFIED - SCHOLAR] tags and SS IDs)
2. If verification fails, HALT and require re-execution
3. Update frontmatter stepsCompleted: [...previous, "step-04-scholar-search"]
4. Load and execute: {workflow_path}/steps/step-05-exa-search.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-03-archon-search.md
</on-back>

<on-retry>
When user selects [R] Retry:
1. Clear current Scholar results
2. Re-execute this step
</on-retry>
