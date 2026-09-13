# Phase 1: Targeted Research Validation Checklist

## Step Execution Tracking

### Step 0: Reference Paper Analysis (Optional)
- [ ] Auto-resume check executed (check `reference_paper_analysis` placeholder)
- [ ] If reference papers provided:
  - [ ] Local files (.md) read completely
  - [ ] arXiv/DOI papers fetched via Semantic Scholar MCP
  - [ ] Key mechanisms extracted
  - [ ] Core concepts and technical terms identified
  - [ ] Connection to research question established
- [ ] If no reference papers: Step skipped appropriately
- [ ] File write: `reference_paper_analysis` saved

### Step 1: Initialize Research Pipeline
- [ ] Auto-resume check executed (check `research_question` placeholder)
- [ ] **Pipeline Status Check executed (Archon)**
- [ ] Pipeline Project found using `pipeline_project_title` from Phase 0
- [ ] Phase 1 Task verified as "doing" status
- [ ] Pipeline IDs stored (pipeline_project_id, phase1_task_id, phase2a_task_id)
- [ ] Phase 0 brainstorm session file loaded
- [ ] Research question, detailed question, reference papers extracted
- [ ] Phase 0 insights extracted (key_insights, areas_for_exploration)
- [ ] **Lessons from Previous Attempts extracted (ROUTE_TO_0 case)**
- [ ] Output directory created
- [ ] Output file initialized from template
- [ ] File write: `research_question`, `primary_research_question`, `detailed_questions`, `lessons_from_previous_attempts` saved

### Step 2: Query Generation
- [ ] Resume check executed (check `query_generation_summary` placeholder)
- [ ] **Failure context loaded (if ROUTE_TO_0 case)**
- [ ] **Failure-aware queries generated (if ROUTE_TO_0 case)**
- [ ] Reference-based queries generated (from extracted concepts)
- [ ] Brainstorm insights-based queries generated
- [ ] Direct question decomposition queries generated
- [ ] Query integration and prioritization completed
- [ ] Target 10-15 diverse queries achieved (12-19 if ROUTE_TO_0)
- [ ] **No queries repeat failed approaches (ROUTE_TO_0 case)**
- [ ] File write: Query placeholders saved

### Step 3: Archon Knowledge Base Search (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `archon_implementations` placeholder)
- [ ] **archon-research skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 3 `mcp__archon__rag_search_knowledge_base` calls made
- [ ] Results tagged with [VERIFIED - ARCHON]
- [ ] File write: `archon_implementations`, `archon_patterns`, `archon_code_examples` saved

### Step 4: Semantic Scholar Paper Search (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `scholar_core_papers` placeholder)
- [ ] **scholar-search skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 5 Semantic Scholar MCP calls made
- [ ] Results tagged with [VERIFIED - SCHOLAR]
- [ ] Each paper has Semantic Scholar ID, arXiv ID, and URL
- [ ] File write: `scholar_core_papers`, `scholar_citation_network` saved

### Step 5: Exa GitHub and Additional Resources (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `exa_repositories` placeholder)
- [ ] **exa-search skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 3 Exa MCP calls made
- [ ] Results tagged with [VERIFIED - EXA]
- [ ] File write: `exa_repositories`, `exa_additional_resources` saved

### Step 6: Chain-of-Relations Analysis (Optional - Can Skip)
- [ ] Resume check executed
- [ ] Paper-to-Implementation matching analyzed
- [ ] Reference papers integrated into evolution path
- [ ] Concept Integration Map created (if reference papers provided)
- [ ] Cross-reference matrix created
- [ ] File write: `research_evolution_path`, `cross_reference_matrix` saved

### Step 7: Verification Summary (Optional - Can Skip)
- [ ] Resume check executed
- [ ] Source verification counts calculated
- [ ] MCP server performance metrics recorded
- [ ] Data quality scores calculated (including Relevance to Question score)
- [ ] File write: `verification_statistics`, `mcp_performance`, `data_quality_assessment` saved

### Step 8: Research Gaps Identification (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `gap1_title` placeholder)
- [ ] Phase boundary enforced (Gaps ONLY, NO solutions/hypotheses)
- [ ] "📌 User Input Recall" section created at top
- [ ] Minimum 3 research gaps identified
- [ ] Each gap has **Relevance Classification** (PRIMARY/SECONDARY)
- [ ] Each gap has **Connection Type** checklist
- [ ] TABLE-BASED evidence format used for ALL gaps
- [ ] [REFERENCE] sources included (if reference papers provided)
- [ ] Gap Priority Matrix with question relevance columns
- [ ] User Input → Gap Traceability Summary completed
- [ ] File write: All gap placeholders saved

### Step 9: Final Report Compilation
- [ ] Resume check executed (check `executive_summary` placeholder)
- [ ] **DUAL OUTPUT FILE SYSTEM executed (Full → Compact)**
- [ ] Phase boundary validation passed (no forbidden content)
- [ ] **Archon Pipeline Task updated (Phase 1 done, Phase 2A doing)**
- [ ] Completion message displayed with both file locations

---

## CRITICAL: Dual Output File Validation

### File 1: Full Report ({full_output_file} = _full.md)
- [ ] File created and readable
- [ ] File size: > 2000 lines (approximate)
- [ ] All `{{UNFILLED:...}}` placeholders filled in conclusion section
- [ ] Contains complete detailed report with all sections
- [ ] Reference Paper Analysis section included (if applicable)

### File 2: Compact Report ({default_output_file} = .md) - Phase 2A Input
- [ ] File created and readable
- [ ] File size: > 500 lines AND < full report size
- [ ] Compact file is 40-60% of full file size
- [ ] **Compaction Rules applied correctly:**
  - [ ] Section 0-1 (Reference & Questions): FULL
  - [ ] Section 2 (Queries): SAMPLE (top 3 each)
  - [ ] Section 3 (Archon): COMPACT (KB ID, Query, Key Pattern)
  - [ ] Section 4 (Scholar): COMPACT (Title | Year | SS ID | arXiv ID | Citations)
  - [ ] Section 5 (Exa): COMPACT (Name | URL | Stars | Key Feature)
  - [ ] Section 6 (Chain): COMPACT
  - [ ] Section 8 (Gaps): **FULL** (CRITICAL for Phase 2A!)
  - [ ] Section 9 (Conclusion): COMPACT

---

## Archon Pipeline Integration

- [ ] Pipeline Project found with exact `pipeline_project_title`
- [ ] Phase 1 Task status verified as "doing" at start
- [ ] Phase 1 Task updated to "done" at completion
- [ ] Phase 2A Task updated to "doing" at completion
- [ ] Pipeline status display shown after update

---

## MCP Server Usage Compliance

### Archon MCP (Past Cases Only)
- [ ] `mcp__archon__rag_search_knowledge_base` function used
- [ ] `mcp__archon__rag_search_code_examples` function used
- [ ] NOT used for GitHub or paper searches

### Semantic Scholar MCP (Academic Papers Only)
- [ ] Paper search and get functions used
- [ ] Citation analysis performed
- [ ] NOT used for GitHub or blog searches

### Exa MCP (GitHub and Additional Resources Only)
- [ ] GitHub repository search performed
- [ ] Additional blog/tutorial search performed
- [ ] NOT used as primary paper search

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## Reference Paper Analysis Quality (if provided)

### Paper Loading and Extraction
- [ ] All provided reference papers loaded correctly
- [ ] Key mechanisms extracted from each reference paper
- [ ] Core concepts and technical terms identified
- [ ] Technical terms defined and explained

### Concept Integration
- [ ] Extracted concepts used in query generation (Step 2)
- [ ] Reference paper context incorporated into research
- [ ] Connection to research question clearly established
- [ ] [REFERENCE] label used in Gap evidence tables

---

## Gap Relevance Validation (CRITICAL)

### User Input Recall
- [ ] "📌 User Input Recall" section present at top of gaps section
- [ ] `{{research_question}}` explicitly stated before gaps
- [ ] `{{detailed_question}}` explicitly stated (or marked "Not provided")
- [ ] `{{reference_papers}}` explicitly stated (or marked "Not provided")

### Gap-to-Question Connection
- [ ] Each gap has **Relevance Classification** (PRIMARY or SECONDARY)
- [ ] Each gap has **Connection Type** checklist showing:
  - [ ] Connection to `{{research_question}}` (MANDATORY for all gaps)
  - [ ] Connection to `{{detailed_question}}` (if applicable)
  - [ ] Connection to `{{reference_papers}}` limitations (if applicable)
- [ ] NO gaps with only CONTEXTUAL relevance included
- [ ] NO gaps unrelated to user's original inputs

### Gap Priority Matrix Columns
- [ ] "Relevance" column (PRIMARY/SECONDARY)
- [ ] "Connection to {{research_question}}" column
- [ ] "Connection to {{detailed_question}}" column
- [ ] "Extends Reference Paper" column
- [ ] Evidence Count column

---

## Content Quality Standards

### Research Coverage
- [ ] Minimum 10 core papers included (directly relevant to question)
- [ ] Minimum 3 GitHub implementation examples
- [ ] Minimum 5 past cases/patterns included
- [ ] Minimum 3 research gaps identified (specific to research question)

### Table-Based Evidence Format (MANDATORY)
- [ ] All Gap evidence in TABLE format (not list format)
- [ ] [SCHOLAR] table with SS ID and arXiv ID
- [ ] [ARCHON] table with KB Entry ID
- [ ] [EXA] table with full URLs
- [ ] [REFERENCE] table for reference paper insights (if applicable)

---

## Phase Boundary Validation

### Phase 1 Scope Compliance
- [ ] Confirm NO Hypothesis section exists
- [ ] Confirm NO Validation Approach section exists
- [ ] Confirm NO "Primary Hypothesis" text exists
- [ ] Confirm NO "Experiment" design included
- [ ] Confirm NO "Recommendations for Implementation" section
- [ ] Confirm NO "Critical Success Factors" section
- [ ] Confirm NO "Expected Contributions" section
- [ ] Only mentions readiness for Phase 2A

### Content Boundaries
- [ ] Gap identification: "X is lacking for {{research_question}}" ✅
- [ ] Opportunity proposals ❌
- [ ] Solution proposals ❌
- [ ] Specific methods ❌

---

## Ready for Next Phase

### Prerequisites for Phase 2A
- [ ] Research question clearly documented
- [ ] Reference paper insights documented (if provided)
- [ ] Sufficient literature collected and relevant to question
- [ ] Implementation examples secured
- [ ] Research gaps clearly defined with connection to question
- [ ] Gap Priority Matrix with question relevance completed
- [ ] Compact version contains Gaps in FULL format

### Handover Requirements
- [ ] Full report (_full.md) created - for archival
- [ ] Compact report (.md) created - Phase 2A input
- [ ] Executive Summary includes research question and approach
- [ ] Minimum 3 Key Findings specific to research question
- [ ] Answer to Detailed Question (Preliminary) section completed
- [ ] Next Step mentions Phase 2A 2-Agent Dialogue
- [ ] All sources verified with identifiers

---

## Critical Failures (Immediate Fix Required)

- [ ] No MCP server role violations
- [ ] No MANDATORY steps skipped (Steps 3, 4, 5, 8, 9)
- [ ] BOTH output files exist (full AND compact)
- [ ] Compact file has Gaps in FULL format (not compacted)
- [ ] Research question properly addressed throughout
- [ ] Gaps connected to research question
- [ ] Reference papers properly analyzed (if provided)
- [ ] No hypotheses or solutions in output (Phase boundary violation)
- [ ] Archon Pipeline updated (Phase 1 done, Phase 2A doing)

---

## Validation Summary

**Total Checks:** 120+
**Required:** Step execution + Dual output + MCP compliance + Gap relevance + Phase boundary
**MANDATORY Steps:** Steps 3, 4, 5, 8, 9 (cannot be skipped)

**Minimum Pass Criteria:**
- All MANDATORY steps completed
- Both output files created (Full + Compact)
- Compact file has Gaps in FULL format
- Gap-to-Question traceability established
- Phase boundary compliance verified
- Archon Pipeline updated

---

**Validation Result:**
- ✅ PASS: All checklist items passed, research question thoroughly addressed
- ⚠️ PASS WITH WARNINGS: Some improvements needed in question coverage
- ❌ FAIL: Critical failures detected or question inadequately addressed

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 1 Targeted Research Workflow (YouRA)
