---
name: 'step-04-scholar-search'
description: 'Search academic papers via Semantic Scholar MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-04-scholar-search.md'
nextStepFile: '{workflow_path}/steps/step-05-exa-search.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 4: Semantic Scholar Paper Search

## STEP GOAL:

Search academic papers via Semantic Scholar MCP using queries generated in Step 2. Execute the scholar-search skill to find relevant papers, foundational works, and citation networks. Extract arXiv IDs for Phase 2A paper download.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Semantic Scholar paper search
- 🚫 FORBIDDEN to skip auto-resume check or skill execution
- ⚠️ MANDATORY: Execute scholar-search skill via Skill tool
- ⚠️ CRITICAL: Extract arXiv ID from externalIds field for Phase 2A
- 📋 Tag all results with [VERIFIED - SCHOLAR]

## EXECUTION PROTOCOLS:

- 🎯 Execute scholar-search skill via Claude Code's Skill tool
- 💾 Save all papers with SS ID and arXiv ID to output file
- 📖 Use queries from Step 2 as search inputs
- 🚫 FORBIDDEN to proceed without actual MCP call results

## CONTEXT BOUNDARIES:

- Available context: Queries from Step 2, research question
- Focus: Semantic Scholar paper search only
- Limits: Do not search Exa yet - only Scholar
- Dependencies: Completed Step 3 with Archon results

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:scholar_relevant_papers}}` filled.
- If filled → Skip to Step 5 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. Execute Scholar Search Skill

**STOP and execute the scholar-search skill NOW using Claude Code's Skill tool:**

```
Use the Skill tool with: skill: "scholar-search"
```

This will load the complete skill instructions for Semantic Scholar paper search.

### 3. Follow Skill Instructions

After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's targeted search strategy (Round 1 → Round 2 → Round 3 → Round 4)
4. If reference papers provided, execute citation network analysis
5. Tag all results with [VERIFIED - SCHOLAR]

### 4. CRITICAL: arXiv ID Extraction for Phase 2A

**Phase 2A REQUIRES arXiv ID to download papers.** You MUST request `externalIds` field.

**Required fields parameter for ALL Semantic Scholar API calls:**
```python
fields=["title", "authors", "year", "citationCount", "abstract", "externalIds", "openAccessPdf", "url"]
```

**Extract arXiv ID from response:**
```python
arxiv_id = paper.get("externalIds", {}).get("ArXiv", None)
```

**If arXiv ID is missing:**
- Log warning: "Paper '{title}' has no arXiv ID - may not be downloadable in Phase 2A"
- Still include paper but mark `arxiv_id: null`

### 5. Verify Skill Execution

**Verify skill execution by confirming:**
- [ ] scholar-search skill was loaded via Skill tool
- [ ] At least 5 Semantic Scholar MCP calls were made
- [ ] Results are tagged with [VERIFIED - SCHOLAR]
- [ ] Each paper has Semantic Scholar ID and URL
- [ ] Each paper has arXiv ID extracted (or marked as null if unavailable)
- [ ] Citation network analysis performed (if reference papers provided)

**IF skill was NOT executed OR no MCP calls were made:**
HALT - You MUST execute the scholar-search skill before continuing.

### 6. Save Progress

**Save progress after Step 4:**

1. Read {outputFile}
2. Replace `{{UNFILLED:scholar_relevant_papers}}` with relevant papers found
3. Replace `{{UNFILLED:scholar_foundational_papers}}` with foundational papers
4. Replace `{{UNFILLED:scholar_citation_network}}` with citation network analysis
5. Write file back
6. Display: "✅ Step 4 saved - X academic papers recorded"

### 7. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 5 (Exa Search) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [Scholar papers saved with SS IDs and arXiv IDs], will you then load and read fully `{nextStepFile}` to execute and begin Exa GitHub and resource search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- scholar-search skill executed via Skill tool
- At least 5 MCP calls made to Semantic Scholar
- Results tagged with [VERIFIED - SCHOLAR]
- arXiv IDs extracted for Phase 2A paper download
- Output file updated with papers including SS IDs
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- NOT executing scholar-search skill via Skill tool
- Not extracting arXiv IDs from externalIds field
- Simulating or faking MCP call results
- Not tagging results with proper verification labels
- Proceeding without actual MCP call results

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
