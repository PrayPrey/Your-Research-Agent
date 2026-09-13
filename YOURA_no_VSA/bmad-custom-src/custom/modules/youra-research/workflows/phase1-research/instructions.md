# Phase 1: Research Gathering Instructions (Broad Exploration)

<critical>
- All agent communication must be in {communication_language}
- MCP servers must be used according to their designated roles only
- This workflow REQUIRES Phase 0 Brainstorm session output
- This is the BROAD exploration path (no reference papers) - use phase1-targeted for focused research with reference papers
</critical>

<critical>
🔄 **MCP ERROR RETRY PROTOCOL - APPLY TO ALL MCP CALLS**

When ANY MCP tool call (Scholar, Exa, Archon) fails with errors like:
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

---

<progressive-file-system>
<critical>
🔄 **PROGRESSIVE FILE WRITING - MANDATORY**

**Output File:** {default_output_file}
**Placeholder Pattern:** `{{UNFILLED:variable_name}}`
**Filled Content:** Actual text replaces the placeholder
**Skipped Content:** `*Skipped by user*` replaces the placeholder

**RULE:** After EACH step completion, you MUST:
1. Read the output file
2. Replace the relevant `{{UNFILLED:...}}` placeholders with actual content
3. Write the file back
4. Display: "✅ Step N saved"

This enables automatic resume after /compact.
</critical>

<step-to-placeholder-mapping>
| Step | Placeholders to Fill |
|------|---------------------|
| 1 | `research_topic`, `primary_research_question`, `detailed_questions` |
| 2 | `query_generation_summary`, `key_insights_queries`, `exploration_queries`, `direct_decomposition_queries`, `query_rationale` |
| 3 | `archon_implementations`, `archon_patterns`, `archon_code_examples` |
| 4 | `scholar_core_papers`, `scholar_citation_network` |
| 5 | `exa_repositories`, `exa_additional_resources`, `exa_code_analysis` |
| 6 | `research_evolution_path`, `cross_reference_matrix` |
| 7 | `verification_statistics`, `mcp_performance`, `data_quality_assessment` |
| 8 | `gap1_title`, `gap1_current_state`, `gap1_missing_piece`, `gap1_impact`, `gap1_archon_evidence`, `gap1_scholar_evidence`, `gap1_exa_evidence`, `gap2_title`, `gap2_archon_evidence`, `gap2_scholar_evidence`, `gap2_exa_evidence`, `gap3_title`, `gap3_archon_evidence`, `gap3_scholar_evidence`, `gap3_exa_evidence`, `gap_priority_matrix`, `evidence_label_summary` |
| 9 | `executive_summary`, `key_findings`, `phase2_readiness`, `next_steps`, `processing_time` |
</step-to-placeholder-mapping>
</progressive-file-system>

---

<resume-check>
<critical>
🔄 **AUTO-RESUME CHECK - EXECUTE BEFORE ANYTHING ELSE**

When this workflow starts, IMMEDIATELY check for existing output file:
1. Check if {default_output_file} exists
2. If YES → Read file and detect resume point
3. If NO → Create new file from template and start from Step 1

**DO NOT ask user if they want to resume. Just check and resume automatically.**
</critical>

<action>**On workflow start, execute this check:**
```
IF file {default_output_file} exists:
    READ file content
    SCAN for first {{UNFILLED:...}} placeholder
    DETERMINE which step this belongs to (use step_markers from workflow.yaml)

    IF no {{UNFILLED:...}} found:
        → Session COMPLETE, inform user
    ELSE:
        → Display: "🔄 Resuming from Step N"
        → Show brief summary of completed steps
        → Jump to Step N (do NOT re-ask completed steps)
ELSE:
    CREATE new file from template
    START from Step 1
```
</action>

<action>**Determine resume point by checking placeholders:**
```
Scan order:
1. Check "research_topic" → if {{UNFILLED:research_topic}} → Resume Step 1
2. Check "query_generation_summary" → if {{UNFILLED:query_generation_summary}} → Resume Step 2
3. Check "archon_implementations" → if {{UNFILLED:archon_implementations}} → Resume Step 3
4. Check "scholar_core_papers" → if {{UNFILLED:scholar_core_papers}} → Resume Step 4
5. Check "exa_repositories" → if {{UNFILLED:exa_repositories}} → Resume Step 5
6. Check "research_evolution_path" → if {{UNFILLED:research_evolution_path}} → Resume Step 6
7. Check "verification_statistics" → if {{UNFILLED:verification_statistics}} → Resume Step 7
8. Check "gap1_title" → if {{UNFILLED:gap1_title}} → Resume Step 8
9. Check "executive_summary" → if {{UNFILLED:executive_summary}} → Resume Step 9
10. If NO {{UNFILLED:...}} found → Session COMPLETE
```
</action>

<action>**On resume, load existing data:**
If resuming from Step N (N > 1):
1. Extract all filled content from Steps 1 to N-1
2. Store in memory for reference (don't re-ask user)
3. Display brief summary: "Previously collected: X papers, Y repos, Z gaps"
4. Jump directly to Step N
</action>
</resume-check>

---

## ⚠️ MANDATORY SKILL EXECUTION REQUIREMENT

<critical>
**THIS WORKFLOW REQUIRES EXECUTING 3 SKILLS VIA CLAUDE CODE'S SKILL TOOL**

Steps 3, 4, and 5 are NOT optional text instructions - they REQUIRE actual skill execution:

1. **Step 3**: You MUST execute `skill: "archon-research"` via the Skill tool
2. **Step 4**: You MUST execute `skill: "scholar-search"` via the Skill tool
3. **Step 5**: You MUST execute `skill: "exa-search"` via the Skill tool

**FAILURE TO EXECUTE SKILLS = INCOMPLETE WORKFLOW**

Each skill will:
- Load detailed MCP function instructions
- Guide you through the exact MCP calls to make
- Provide output templates for structuring results

DO NOT simulate or skip skill execution. DO NOT proceed to next step without actual MCP call results.
</critical>

## MCP Server Role Enforcement

<mandatory>
- **Archon MCP**: Exclusively for searching past cases and best practices
  - Activated via: `skill: "archon-research"`
- **Exa MCP**: Exclusively for GitHub repositories and additional resource search
  - Activated via: `skill: "exa-search"`
- **Semantic Scholar MCP**: Exclusively for academic paper search and detailed analysis
  - Activated via: `skill: "scholar-search"`
</mandatory>

## Workflow Steps

<step n="1" goal="Initialize Research Pipeline">
<action>Greet {user_name}: "Hello {user_name}, starting Phase 1: Broad Research Gathering."</action>

<!-- Load Phase 0 Brainstorm Session Input (REQUIRED) -->
<check if="brainstorm_session file exists OR data attribute was passed">
  <action>Load Phase 0 Brainstorm session file</action>
  <action>Extract from the phase1-input section:
    - research_question: Extract from "### research_question" section
    - detailed_question: Extract from "### detailed_question" section (may be empty)
  </action>
  <action>Extract from "## Session Insights" section:
    - key_insights: Extract from "### Key Discoveries" section
    - techniques_used: Extract from "### Techniques Used" section
    - areas_for_exploration: Extract from "### Areas for Further Exploration" section
  </action>
  <action>Store complete brainstorm context:
    {{brainstorm_context}} = {
      research_question: {{research_question}},
      detailed_question: {{detailed_question}},
      key_insights: {{key_insights}},
      techniques_used: {{techniques_used}},
      areas_for_exploration: {{areas_for_exploration}}
    }
  </action>
  <action>Display to {user_name}:
    "📋 Loaded inputs from Phase 0 Brainstorm session:

    **Research Inputs:**
    - Research Question: {{research_question}}
    - Detailed Question: {{detailed_question}} (or 'Not provided')

    **Session Insights:**
    - Key Discoveries: {{key_insights}}
    - Areas for Further Exploration: {{areas_for_exploration}}

    ℹ️ Note: This is BROAD research mode (no reference papers).
    For focused research with reference papers, use *targeted-research instead."
  </action>
  <ask>Does this look correct? [c] Continue / [e] Edit inputs</ask>
</check>

<check if="no brainstorm_session file found">
  <action>STOP workflow and notify {user_name}:

  "⚠️ No Phase 0 Brainstorm session found.

  Phase 1 requires a research question from Phase 0 Brainstorm.

  Please run Phase 0 first:
  ```
  *brainstorm
  ```

  Phase 0 will help you:
  - Discover and refine your research question
  - Identify detailed sub-questions
  - Optionally find relevant reference papers

  After completing Phase 0, run Phase 1 again."
  </action>
  <critical>HALT workflow execution until Phase 0 is completed.</critical>
</check>

<action>Confirm inputs:
- Main research question: {{research_question}}
- Detailed question: {{detailed_question}} (if provided)
</action>

<action>Create output directory if needed: {{default_output_file}}</action>
<action>Verify MCP server connection status</action>
<action>Communicate all responses to {user_name} in {communication_language}</action>

<template-output section="header">
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
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 1**
1. Read {default_output_file} (or create from template if not exists)
2. Replace `{{UNFILLED:research_topic}}` with {{research_question}}
3. Replace `{{UNFILLED:primary_research_question}}` with {{research_question}}
4. Replace `{{UNFILLED:detailed_questions}}` with {{detailed_question}} (or `*Not provided*`)
5. Write file back
6. Display: "✅ Step 1 saved - Research questions recorded"
</file-write>
</step>

<step n="2" goal="Question-Based Query Generation">

<!-- Priority 1: Brainstorm Insights-Based Queries (from Phase 0 Session Insights) -->
<check if="brainstorm_context.key_insights exists OR brainstorm_context.areas_for_exploration exists">
  <action>Generate queries from Brainstorm Session Insights:

  **From Key Discoveries (key_insights):**
  - Extract technical concepts and terms discovered during brainstorm
  - Create queries that explore these discovered concepts deeper
  - Format: "[discovered_concept] in [research_domain]"
  - Format: "[insight_term] mechanism/architecture/approach"

  **From Areas for Further Exploration:**
  - These are promising directions user identified but hasn't explored
  - Create queries that investigate these unexplored areas
  - Format: "[exploration_area] research/implementation"
  - Format: "[exploration_direction] for [research_question_domain]"

  Example:
  - Key Insight: "recursive attention patterns"
    → Query: "recursive attention patterns in sequence models"
  - Area for Exploration: "biological memory consolidation"
    → Query: "biological memory consolidation inspired neural networks"

  Store as: brainstorm_queries = [3-5 queries]
  </action>
</check>

<!-- Priority 2: Direct Question Decomposition (always execute) -->
<action>
1. **Direct Question Decomposition**:
   - Break down {{research_question}} into searchable components
   - Extract key technical terms and concepts
   - Identify core problem domain

2. **Multi-Dimensional Query Construction**:

   A. **Technical Queries** (specific implementations):
      - "[key_concept_1] + [key_concept_2] implementation"
      - "[mechanism_1] applied to [problem_domain]"
      - "[architecture_component] for [task]"

   B. **Theoretical Queries** (foundational papers):
      - "[core_concept] theory"
      - "[approach] for [generalization_type]"
      - "compositional [property] in [domain]"

   C. **Comparative Queries** (related approaches):
      - "[approach_A] vs [approach_B]"
      - "alternatives to [current_approach]"
      - "comparison of [technique] methods"

   D. **Problem-Specific Queries**:
      - Directly derived from {{detailed_question}}
      - Focus on specific architectural challenges
      - Target known limitations or gaps

3. **Target**: Generate 8-12 queries from question decomposition

Store as: direct_queries = [list of 8-12 queries]
</action>

<!-- Query Integration and Prioritization -->
<action>Integrate all generated queries with priority ordering:

Final Query List Structure:
1. **Brainstorm Insights Queries** (if available): {{brainstorm_queries}} [High Priority]
2. **Direct Question Queries**: {{direct_queries}} [Standard Priority]

Total Query Count: Aim for 10-15 diverse queries

Display to user:
"📊 Query Generation Summary:
- Brainstorm insights queries: {{brainstorm_count}} (from key discoveries + areas for exploration)
- Direct question queries: {{direct_count}}
- Total: {{total_count}} queries

Query Priority Order:
🥇 Brainstorm insights (key discoveries + unexplored directions from Phase 0)
🥈 Question decomposition (baseline coverage)"
</action>

<template-output section="queries">
## Search Queries Generated

### Query Generation Source Summary
- **Brainstorm Insights**: {{brainstorm_count}} queries (from Phase 0 key discoveries + areas for exploration)
- **Direct Question Decomposition**: {{direct_count}} queries (from research question)
- **Total**: {{total_count}} queries

### 🥇 Priority 1: Brainstorm Insights Queries (from Phase 0)

**From Key Discoveries:**
{{key_insights_queries_list}}

**From Areas for Further Exploration:**
{{areas_exploration_queries_list}}

### 🥈 Priority 2: Direct Question Decomposition Queries
{{direct_queries_list}}

### Query Rationale
{{query_generation_rationale}}

*Note: Queries are ordered by priority. Brainstorm insights queries explore directions discovered during Phase 0 brainstorming session.*
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 2**
1. Read {default_output_file}
2. Replace `{{UNFILLED:query_generation_summary}}` with query source counts (brainstorm insights: X, direct: Y, total: Z)
3. Replace `{{UNFILLED:key_insights_queries}}` with queries derived from Phase 0 Key Discoveries (or `*No brainstorm insights available*`)
4. Replace `{{UNFILLED:exploration_queries}}` with queries from Phase 0 Areas for Further Exploration (or `*No exploration areas provided*`)
5. Replace `{{UNFILLED:direct_decomposition_queries}}` with Technical, Theoretical, Comparative, Problem-Specific queries
6. Replace `{{UNFILLED:query_rationale}}` with reasoning for query construction choices
7. Write file back
8. Display: "✅ Step 2 saved - {{total_count}} queries generated"
</file-write>
</step>

<step n="3" goal="Archon Knowledge Base Search" critical="true">
<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP
This step REQUIRES executing the archon-research skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 4 until this skill has been executed and results obtained.
</critical>

<action>STOP and execute the archon-research skill NOW using Claude Code's Skill tool:
```
Use the Skill tool with: skill: "archon-research"
```
This will load the complete skill instructions for Archon Knowledge Base search.
</action>

<action>After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill (mcp__archon__rag_search_knowledge_base)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's hierarchical search strategy (Level 1 → Level 2 → Level 3)
4. Tag all results with [VERIFIED - ARCHON] as specified in the skill
</action>

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>HALT - You MUST execute the archon-research skill before continuing.</critical>
  <action>Execute: Skill tool with skill: "archon-research"</action>
  <action>Then make actual mcp__archon__rag_search_knowledge_base calls</action>
</check>

<action>Verify skill execution by confirming:
- [ ] archon-research skill was loaded via Skill tool
- [ ] At least 3 mcp__archon__rag_search_knowledge_base calls were made
- [ ] Results are tagged with [VERIFIED - ARCHON] or [INFERRED]
- [ ] Output follows the skill's template structure
</action>

<template-output section="archon_results">
<!-- This section MUST contain actual Archon MCP search results -->
<!-- If empty or placeholder, the skill was NOT properly executed -->
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 3**
1. Read {default_output_file}
2. Replace `{{UNFILLED:archon_implementations}}` with successful implementations found
3. Replace `{{UNFILLED:archon_patterns}}` with known patterns found
4. Replace `{{UNFILLED:archon_code_examples}}` with code examples (or `*No code examples found*`)
5. Write file back
6. Display: "✅ Step 3 saved - Archon KB search results recorded"
</file-write>
</step>

<step n="4" goal="Semantic Scholar Paper Search" critical="true">
<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP
This step REQUIRES executing the scholar-search skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 5 until this skill has been executed and results obtained.
</critical>

<action>STOP and execute the scholar-search skill NOW using Claude Code's Skill tool:
```
Use the Skill tool with: skill: "scholar-search"
```
This will load the complete skill instructions for Semantic Scholar paper search.
</action>

<action>After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill (mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search, etc.)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's targeted search strategy (Round 1 → Round 2 → Round 3 → Round 4)
4. Tag all results with [VERIFIED - SCHOLAR] as specified in the skill
</action>

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>HALT - You MUST execute the scholar-search skill before continuing.</critical>
  <action>Execute: Skill tool with skill: "scholar-search"</action>
  <action>Then make actual Semantic Scholar MCP calls</action>
</check>

<action>Verify skill execution by confirming:
- [ ] scholar-search skill was loaded via Skill tool
- [ ] At least 5 mcp__hamid-vakilzadeh-mcpsemanticscholar__* calls were made
- [ ] Results are tagged with [VERIFIED - SCHOLAR]
- [ ] Each paper has Semantic Scholar ID and URL
- [ ] Output follows the skill's template structure
</action>

<template-output section="scholar_results">
<!-- This section MUST contain actual Semantic Scholar MCP search results -->
<!-- If empty or placeholder, the skill was NOT properly executed -->
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 4**
1. Read {default_output_file}
2. Replace `{{UNFILLED:scholar_core_papers}}` with verified papers list
3. Replace `{{UNFILLED:scholar_citation_network}}` with citation analysis
5. Write file back
6. Display: "✅ Step 4 saved - X academic papers recorded"
</file-write>
</step>

<step n="5" goal="Exa GitHub and Additional Resources" critical="true">
<critical>
⚠️ MANDATORY SKILL EXECUTION - DO NOT SKIP
This step REQUIRES executing the exa-search skill via Claude Code's Skill tool.
You MUST NOT proceed to Step 6 until this skill has been executed and results obtained.
</critical>

<action>STOP and execute the exa-search skill NOW using Claude Code's Skill tool:
```
Use the Skill tool with: skill: "exa-search"
```
This will load the complete skill instructions for Exa GitHub and implementation search.
</action>

<action>After the skill loads, you MUST:
1. Execute ALL MCP calls specified in the skill (mcp__exa__web_search_exa, mcp__exa__get_code_context_exa)
2. Use the queries generated in Step 2 as search inputs
3. Follow the skill's priority-based search strategy (Priority 1 → 5)
4. Tag all results with [VERIFIED - EXA] as specified in the skill
</action>

<check if="skill was NOT executed OR no MCP calls were made">
  <critical>HALT - You MUST execute the exa-search skill before continuing.</critical>
  <action>Execute: Skill tool with skill: "exa-search"</action>
  <action>Then make actual Exa MCP calls</action>
</check>

<action>Verify skill execution by confirming:
- [ ] exa-search skill was loaded via Skill tool
- [ ] At least 3 mcp__exa__web_search_exa or mcp__exa__get_code_context_exa calls were made
- [ ] Results are tagged with [VERIFIED - EXA], [VERIFIED - EXA - TUTORIAL], or [VERIFIED - EXA - CODE_CONTEXT]
- [ ] Each resource has a full URL
- [ ] Output follows the skill's template structure
</action>

<template-output section="exa_results">
<!-- This section MUST contain actual Exa MCP search results -->
<!-- If empty or placeholder, the skill was NOT properly executed -->
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 5**
1. Read {default_output_file}
2. Replace `{{UNFILLED:exa_repositories}}` with GitHub repositories found
3. Replace `{{UNFILLED:exa_additional_resources}}` with additional resources
4. Replace `{{UNFILLED:exa_code_analysis}}` with code analysis summary
5. Write file back
6. Display: "✅ Step 5 saved - X repositories and resources recorded"
</file-write>
</step>

<step n="6" goal="Chain-of-Relations Analysis">
<action>Analyze connection relationships among all collected information</action>

Analysis items:
- Matching papers with implementation code
- Theoretical development pathways
- Technical evolution processes
- Research community networks

<template-output section="analysis">
## Chain-of-Relations Analysis

### Research Evolution Path
1. Foundation: [Paper A] introduced concept
2. Improvement: [Paper B] optimized algorithm
3. Implementation: [GitHub Repo C] provides code
4. Application: [Case D] deployed in production

### Cross-Reference Matrix
| Paper | GitHub Implementation | Archon Case |
|-------|---------------------|-------------|
| Paper1 | Repo1 ✅ | Case1 ✅ |
| Paper2 | Repo2 ✅ | - |
| Paper3 | - | Case2 ✅ |
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 6**
1. Read {default_output_file}
2. Replace `{{UNFILLED:research_evolution_path}}` with research evolution analysis
3. Replace `{{UNFILLED:cross_reference_matrix}}` with cross-reference matrix
5. Write file back
6. Display: "✅ Step 6 saved - Chain-of-relations analysis recorded"
</file-write>
</step>

<step n="7" goal="Verification Summary">
<action>Summarize verification status of all collected information</action>

<template-output section="verification">
## Verification Status Summary

### Statistics
- Total sources: XX
- [VERIFIED]: XX (XX%)
- [UNVERIFIED]: XX (XX%)
- [NOT_FOUND]: XX (XX%)

### MCP Server Performance
- Archon: XX queries, XX ms avg response
- Semantic Scholar: XX queries, XX ms avg response
- Exa: XX queries, XX ms avg response

### Data Quality Assessment
- Completeness: XX/100
- Reliability: XX/100
- Recency: XX/100
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 7**
1. Read {default_output_file}
2. Replace `{{UNFILLED:verification_statistics}}` with source statistics
3. Replace `{{UNFILLED:mcp_performance}}` with MCP server performance metrics
4. Replace `{{UNFILLED:data_quality_assessment}}` with quality scores
5. Write file back
6. Display: "✅ Step 7 saved - Verification summary recorded"
</file-write>
</step>

<step n="8" goal="Research Gaps Identification">
<action>Identify research gaps (specific solutions and opportunities will be generated in Phase 2A)</action>

<critical>
Identify Gaps ONLY - DO NOT propose opportunities, hypotheses, or solutions
- ✅ "X is lacking" (Gap identification)
- ❌ "X can be addressed by Y" (Opportunity - Phase 2A territory)
- ❌ "X can be solved with method Y" (Hypothesis - Phase 2A territory)
</critical>

<action>For each identified gap, label ALL supporting evidence from collected sources:

<critical>
⚠️ TABLE-BASED EVIDENCE FORMAT (MANDATORY)

All supporting evidence MUST be output in table format with full identifiers.
This enables Phase 2A to programmatically extract and reference sources.

Each source MUST include its unique identifier:
- [SCHOLAR]: Semantic Scholar ID (SS ID) - REQUIRED
- [ARCHON]: KB Entry ID - REQUIRED
- [EXA]: Full URL - REQUIRED
</critical>

Source Labeling Requirements (TABLE FORMAT):

1. **[SCHOLAR]** Academic Papers - Use this table format:

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| "Full Paper Title" | 2024 | First Author et al. | abc123def456... | 25 | How this paper relates to gap |

- **SS ID**: Semantic Scholar ID from paper_details (e.g., "ebf945c38d6bccbbd337246f9bd8ddd3de192e8d")
- **Key Insight**: Specific relevance to THIS gap (not general description)

2. **[ARCHON]** Past Cases - Use this table format:

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| "Case/Pattern Name" | a402d7be110bf67e | "search query" | Key insight/pattern applicable to gap |

3. **[EXA]** Implementation Resources - Use this table format:

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| owner/repo | https://github.com/... | 139 | Python | Specific feature relevant to gap |
</action>

<template-output section="gaps">
## Research Gaps

### Identified Gaps

#### Gap 1: [Field/Domain]

**Current State:** [Current research status]

**Missing Piece:** [What is lacking]

**Potential Impact:** High/Medium/Low

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| "Paper Title" | 2024 | Author et al. | abc123... | 25 | How this relates to the gap |
| "Paper Title 2" | 2023 | Author et al. | xyz789... | 37 | How this relates to the gap |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| "Case/Pattern Name" | a402d7be... | "search query" | Key insight from case |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| owner/repo | https://github.com/... | 139 | Python | Relevant feature |

---

#### Gap 2: [Field/Domain]

**Current State:** ...

**Missing Piece:** ...

**Potential Impact:** ...

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| ... | ... | ... | ... | ... | ... |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| ... | ... | ... | ... |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| ... | ... | ... | ... | ... |

---

#### Gap 3: [Field/Domain]

**Current State:** ...

**Missing Piece:** ...

**Potential Impact:** ...

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| ... | ... | ... | ... | ... | ... |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| ... | ... | ... | ... |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| ... | ... | ... | ... | ... |

---

### Gap Priority Matrix for Phase 2A

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | [title] | High | Medium | X sources | Critical |
| Gap 2 | [title] | Medium | Low | X sources | Important |
| Gap 3 | [title] | High | High | X sources | Challenging |

### Evidence Label Summary

| Source Type | Gap 1 | Gap 2 | Gap 3 | Total |
|-------------|-------|-------|-------|-------|
| [SCHOLAR] | X | X | X | X |
| [ARCHON] | X | X | X | X |
| [EXA] | X | X | X | X |
| **Total** | X | X | X | X |
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 8**
1. Read {default_output_file}
2. For each Gap (1, 2, 3), replace the following placeholders:
   - `{{UNFILLED:gap1_title}}`, `{{UNFILLED:gap2_title}}`, `{{UNFILLED:gap3_title}}` with gap field/domain titles
   - `{{UNFILLED:gap1_current_state}}`, etc. with current research status
   - `{{UNFILLED:gap1_missing_piece}}`, etc. with what is lacking
   - `{{UNFILLED:gap1_impact}}`, etc. with High/Medium/Low
   - `{{UNFILLED:gap1_scholar_evidence}}`, etc. with [SCHOLAR] papers TABLE ROWS:
     ```
     | "Paper Title" | 2024 | Author et al. | abc123def456... | 25 | Key insight for gap |
     | "Paper Title 2" | 2023 | Author et al. | xyz789... | 37 | Key insight for gap |
     ```
   - `{{UNFILLED:gap1_archon_evidence}}`, etc. with [ARCHON] cases TABLE ROWS:
     ```
     | "Case Title" | a402d7be110bf67e | "search query" | Key pattern for gap |
     | "Case Title 2" | b503e8cf221c... | "query" | Key pattern for gap |
     ```
   - `{{UNFILLED:gap1_exa_evidence}}`, etc. with [EXA] resources TABLE ROWS:
     ```
     | owner/repo | https://github.com/... | 139 | Python | Key feature for gap |
     | owner/repo2 | https://github.com/... | 85 | PyTorch | Key feature for gap |
     ```
3. Replace `{{UNFILLED:gap_priority_matrix}}` with table rows (one per Gap)
4. Replace `{{UNFILLED:evidence_label_summary}}` with evidence counts
5. Write file back
6. Display: "✅ Step 8 saved - X research gaps identified with Y supporting sources"

<critical>
⚠️ TABLE FORMAT VALIDATION
Verify that all evidence placeholders contain TABLE ROWS, not list items.
- ✅ CORRECT: | "Paper Title" | 2024 | Author | abc123... | 25 | Insight |
- ❌ WRONG: - 🏷️ "Paper Title" (2024) - Authors: ... - SS ID: ...
</critical>
</file-write>
</step>

<step n="9" goal="Final Report Compilation">
<action>Compile and save final research report</action>
<action>Present findings to {user_name} in {communication_language}</action>

<critical>
⚠️ PHASE BOUNDARY: Phase 1 is purely a research collection stage.
- NO Hypothesis generation ❌
- NO Validation Approach proposals ❌
- NO "Primary Hypothesis" section ❌
- NO Experiment design ❌
- ONLY perform data collection and Gap/Opportunity analysis ✅
- Hypothesis generation will occur in Phase 2A using Party Mode
</critical>

<template-output section="conclusion">
## Conclusion

### Key Findings
- Finding 1: ...
- Finding 2: ...
- Finding 3: ...

### Ready for Phase 2
✅ Sufficient literature collected (X verified sources)
✅ Implementation examples identified (X repositories)
✅ Research gaps analyzed (X gaps identified)
✅ All sources verified

### Phase 1 Deliverables Summary
- **Academic Papers**: X papers with Y+ citations
- **Code Repositories**: X implementations verified
- **Past Cases**: X patterns from knowledge base
- **Research Gaps**: X critical gaps identified (ready for Phase 2A)

### Next Step
Proceed to Phase 2A: Hypothesis Validation
- Phase 2A will use Party Mode (4 agents with feedback loop)
- Innovator, Skeptic, Strategist, Judge will generate and validate hypotheses
- Target: 3-5 FEASIBLE hypotheses based on identified gaps

<!-- DO NOT ADD HYPOTHESIS HERE - Phase 2A Party Mode will handle hypothesis generation -->

---
*Phase: 1 - Research Gathering (Pre-Hypothesis)*
*Total processing time: {{processing_time}}*
</template-output>

<file-write>
**MANDATORY: Save progress to file after Step 9 (FINAL)**
1. Read {default_output_file}
2. Replace `{{UNFILLED:executive_summary}}` with executive summary
3. Replace `{{UNFILLED:key_findings}}` with key findings list
4. Replace `{{UNFILLED:phase2_readiness}}` with readiness checklist
5. Replace `{{UNFILLED:next_steps}}` with next step guidance
6. Replace `{{UNFILLED:processing_time}}` with total processing time
7. Write file back
8. Display: "✅ Phase 1 Research COMPLETE - Report saved to {default_output_file}"
</file-write>
</step>
