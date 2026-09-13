---
name: 'step-03-archon-search'
description: 'Search past cases and best practices using Archon MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-03-archon-search.md'
nextStepFile: '{workflow_path}/steps/step-04-scholar-search.md'
---

# Step 3: Archon Knowledge Base Search

**Goal:** Search past cases and best practices using Archon MCP

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP

This step REQUIRES executing the archon-research skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 4 until this skill has been executed and results obtained.
</critical>

<critical>
🔄 **MCP ERROR RETRY PROTOCOL - APPLY TO ALL MCP CALLS**

When ANY MCP tool call fails with errors like:
- "rate_limit", "timeout", "connection_error", "server_overload"
- "MCP server", "tool execution failed"

**DO NOT immediately fail. Instead:**
1. Display: "⏳ MCP error. Waiting 15 seconds before retry (attempt X/3)..."
2. Wait 15 seconds using Bash: `sleep 15`
3. Retry the SAME MCP call
4. Repeat up to 3 total attempts
5. Only skip/fail after 3 consecutive failures

**Why:** Parallel batch processing can cause MCP overload. Retry with delay resolves most issues.
</critical>

<critical>
🔄 **RESUME CHECK**

Before starting, check if this step is already completed:
1. Read {default_output_file}
2. Check if `{{UNFILLED:archon_implementations}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Execute Archon Research Skill

<action>
STOP and execute the archon-research skill NOW using Claude Code's Skill tool:

```
Use the Skill tool with: skill: "archon-research"
```

This will load the complete skill instructions for Archon Knowledge Base search.
</action>

### 2. Follow Skill Instructions

<action>
After the skill loads, you MUST:

1. Execute ALL MCP calls specified in the skill (mcp__archon__rag_search_knowledge_base)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's hierarchical search strategy (Level 1 → Level 2 → Level 3)
4. Tag all results with [VERIFIED - ARCHON] as specified in the skill
5. Apply MCP ERROR RETRY PROTOCOL to all MCP calls
</action>

### 3. Verify Skill Execution

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>
  HALT - You MUST execute the archon-research skill before continuing.
  </critical>

  <action>
  1. Execute: Skill tool with skill: "archon-research"
  2. Then make actual mcp__archon__rag_search_knowledge_base calls
  </action>
</check>

<action>
Verify skill execution by confirming:
- [ ] archon-research skill was loaded via Skill tool
- [ ] At least 3 mcp__archon__rag_search_knowledge_base calls were made
- [ ] Results are tagged with [VERIFIED - ARCHON] or [INFERRED]
- [ ] Output follows the skill's template structure
</action>

### 4. Display Results Summary

<action>
Display to user in {communication_language}:

```
📚 Archon Knowledge Base search complete

**Items Found:**
- Successful implementations: X
- Known patterns: Y
- Code examples: Z

All results were marked with [VERIFIED - ARCHON] tags.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 3:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:archon_implementations}}` with successful implementations found
3. Replace `{{UNFILLED:archon_patterns}}` with known patterns found
4. Replace `{{UNFILLED:archon_code_examples}}` with code examples (or `*No code examples found*`)
5. Update frontmatter: Add "step-03-archon-search" to stepsCompleted array
6. Write file back
7. Display: "✅ Step 3 saved - Archon KB search results recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 4 (Semantic Scholar Paper Search)
[B] Back - Return to Step 2
[R] Retry - Re-run Archon search
</menu>

<critical>
⚠️ DO NOT allow [S] Skip option for this step.
Archon search is MANDATORY for workflow completion.
</critical>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Verify that Archon search was actually performed (check for [VERIFIED - ARCHON] tags)
2. If verification fails, HALT and require re-execution
3. Update frontmatter stepsCompleted: [...previous, "step-03-archon-search"]
4. Load and execute: {workflow_path}/steps/step-04-scholar-search.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-02-query-generation.md
</on-back>

<on-retry>
When user selects [R] Retry:
1. Clear current Archon results
2. Re-execute this step from beginning
</on-retry>
