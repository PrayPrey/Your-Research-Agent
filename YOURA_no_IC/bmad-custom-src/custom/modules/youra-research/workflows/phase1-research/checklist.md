# Phase 1: Research Gathering Validation Checklist

## Step Execution Tracking

### Step 1: Initialize Research Pipeline
- [ ] Auto-resume check executed (check for existing output file)
- [ ] Phase 0 brainstorm session file loaded
- [ ] Research question extracted from `<phase1-input>` section
- [ ] Detailed question extracted (if provided)
- [ ] Phase 0 insights extracted (key_insights, areas_for_exploration)
- [ ] Output directory created
- [ ] Output file initialized from template
- [ ] File write: `research_topic`, `primary_research_question`, `detailed_questions` saved

### Step 2: Query Generation
- [ ] Resume check executed (check `query_generation_summary` placeholder)
- [ ] Brainstorm insights-based queries generated (from key_insights, areas_for_exploration)
- [ ] Direct question decomposition queries generated (Technical, Theoretical, Comparative, Problem-Specific)
- [ ] Query integration and prioritization completed
- [ ] Target 10-15 diverse queries achieved
- [ ] File write: `query_generation_summary`, `key_insights_queries`, `exploration_queries`, `direct_decomposition_queries`, `query_rationale` saved

### Step 3: Archon Knowledge Base Search (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `archon_implementations` placeholder)
- [ ] **archon-research skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 3 `mcp__archon__rag_search_knowledge_base` calls made
- [ ] Results tagged with [VERIFIED - ARCHON] or [INFERRED]
- [ ] Skill execution verification passed
- [ ] File write: `archon_implementations`, `archon_patterns`, `archon_code_examples` saved

### Step 4: Semantic Scholar Paper Search (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `scholar_core_papers` placeholder)
- [ ] **scholar-search skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 5 Semantic Scholar MCP calls made
- [ ] Results tagged with [VERIFIED - SCHOLAR]
- [ ] Each paper has Semantic Scholar ID and URL
- [ ] Skill execution verification passed
- [ ] File write: `scholar_core_papers`, `scholar_citation_network` saved

### Step 5: Exa GitHub and Additional Resources (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `exa_repositories` placeholder)
- [ ] **exa-search skill executed via Skill tool**
- [ ] MCP ERROR RETRY PROTOCOL applied (3 attempts with 15s delay)
- [ ] At least 3 Exa MCP calls made
- [ ] Results tagged with [VERIFIED - EXA], [VERIFIED - EXA - TUTORIAL], or [VERIFIED - EXA - CODE_CONTEXT]
- [ ] Each resource has full URL
- [ ] Skill execution verification passed
- [ ] File write: `exa_repositories`, `exa_additional_resources`, `exa_code_analysis` saved

### Step 6: Chain-of-Relations Analysis (Optional - Can Skip)
- [ ] Resume check executed (check `research_evolution_path` placeholder)
- [ ] Paper-to-Implementation matching analyzed
- [ ] Theoretical development pathways traced
- [ ] Technical evolution processes documented
- [ ] Research community networks mapped
- [ ] Cross-reference matrix created
- [ ] File write: `research_evolution_path`, `cross_reference_matrix` saved

### Step 7: Verification Summary (Optional - Can Skip)
- [ ] Resume check executed (check `verification_statistics` placeholder)
- [ ] Source verification counts calculated ([VERIFIED - ARCHON], [VERIFIED - SCHOLAR], [VERIFIED - EXA])
- [ ] MCP server performance metrics recorded
- [ ] Data quality scores calculated (Completeness, Reliability, Recency)
- [ ] File write: `verification_statistics`, `mcp_performance`, `data_quality_assessment` saved

### Step 8: Research Gaps Identification (MANDATORY - NO SKIP)
- [ ] Resume check executed (check `gap1_title` placeholder)
- [ ] Phase boundary enforced (Gaps ONLY, NO solutions/hypotheses)
- [ ] Minimum 3 research gaps identified
- [ ] **TABLE-BASED evidence format used for ALL gaps**
- [ ] [SCHOLAR] evidence has SS IDs in table format
- [ ] [ARCHON] evidence has KB Entry IDs in table format
- [ ] [EXA] evidence has full URLs in table format
- [ ] Gap Priority Matrix created
- [ ] Evidence Label Summary completed
- [ ] File write: All gap placeholders (title, current_state, missing_piece, impact, evidence tables) saved

### Step 9: Final Report Compilation
- [ ] Resume check executed (check `executive_summary` placeholder)
- [ ] **DUAL OUTPUT FILE SYSTEM executed**
- [ ] Executive summary created
- [ ] Key findings extracted (3-5 findings)
- [ ] Phase 2 readiness checklist verified
- [ ] Top 5 academic papers selected
- [ ] Top 3 implementation examples selected
- [ ] Processing time calculated

---

## CRITICAL: Dual Output File Validation

### File 1: Lightweight Summary (01_research_data.md) - DEFAULT
- [ ] File created and readable
- [ ] File size: 500-1000 lines (approximate)
- [ ] Contains Research Gaps section with COMPLETE evidence tables
- [ ] All [SCHOLAR] sources have SS IDs
- [ ] All [ARCHON] sources have KB Entry IDs
- [ ] All [EXA] sources have full URLs
- [ ] Gap Priority Matrix included
- [ ] Top 5 papers with justification
- [ ] Top 3 implementations with justification
- [ ] Phase 0 insights included

### File 2: Full Report (01_research_data_full.md)
- [ ] File created and readable
- [ ] File size: 5000-10000 lines (approximate)
- [ ] File size > lightweight summary
- [ ] All `{{UNFILLED:...}}` placeholders filled
- [ ] Contains all search queries (10-15+)
- [ ] Contains all papers (10-20+)
- [ ] Contains all GitHub repos (10-15+)
- [ ] Complete chain-of-relations analysis
- [ ] Full verification statistics

---

## MCP Server Usage Compliance

### Archon MCP (Past Cases Only)
- [ ] `mcp__archon__rag_search_knowledge_base` function used
- [ ] `mcp__archon__rag_search_code_examples` function used
- [ ] NOT used for GitHub or paper searches
- [ ] Only searches for past cases and best practices

### Semantic Scholar MCP (Academic Papers Only)
- [ ] `mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search` used
- [ ] `mcp__hamid-vakilzadeh-mcpsemanticscholar__get_paper_details` used
- [ ] Citation analysis performed
- [ ] NOT used for GitHub or blog searches

### Exa MCP (GitHub and Additional Resources Only)
- [ ] `mcp__exa__web_search_exa` used
- [ ] `mcp__exa__get_code_context_exa` used (optional)
- [ ] GitHub repository search performed
- [ ] Additional blog/tutorial search performed
- [ ] NOT used as primary paper search

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry (rate_limit, timeout, connection_error, server_overload)
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Error handling display: "⏳ MCP error. Waiting 15 seconds before retry (attempt X/3)..."
- [ ] Only skip/fail after 3 consecutive failures

---

## Content Quality Standards

### Research Coverage
- [ ] Minimum 10 core papers included
- [ ] Minimum 3 GitHub implementation examples included
- [ ] Minimum 5 past cases/patterns included
- [ ] Minimum 3 research gaps identified

### Verification Status
- [ ] All papers marked with [VERIFIED - SCHOLAR] status
- [ ] All GitHub links verified with [VERIFIED - EXA]
- [ ] Archon search results marked with [VERIFIED - ARCHON]
- [ ] Unverifiable items clearly marked

### Analysis Depth
- [ ] Chain-of-Relations analysis completed
- [ ] Paper-implementation matching table created
- [ ] Research evolution pathway derived
- [ ] Cross-reference matrix completed

### Table-Based Evidence Format (MANDATORY)
- [ ] All Gap evidence in TABLE format (not list format)
- [ ] [SCHOLAR] table: Paper Title | Year | Authors | SS ID | Citations | Key Insight
- [ ] [ARCHON] table: Case Title | KB Entry ID | Query Used | Key Pattern
- [ ] [EXA] table: Resource Name | URL | Stars | Language | Key Feature
- [ ] Gap Priority Matrix table completed
- [ ] Evidence Label Summary table completed

---

## Phase Boundary Validation

### Phase 1 Scope Compliance
- [ ] Confirm NO Hypothesis section exists
- [ ] Confirm NO Validation Approach section exists
- [ ] Confirm NO "Primary Hypothesis" text exists
- [ ] Confirm NO "Experiment" design included
- [ ] Confirm NO Innovation Opportunities section exists
- [ ] Only mentions readiness for Phase 2A, no actual hypothesis generation
- [ ] Only derives Gaps, no opportunities or specific solutions proposed

### Content Boundaries
- [ ] Gap identification: "X is lacking" ✅
- [ ] Opportunity proposals: "Research direction Z is possible" ❌
- [ ] Solution proposals: "Solve X with Y" ❌
- [ ] Specific methods: "Implement with A+B+C" ❌

---

## Ready for Next Phase

### Prerequisites for Phase 2A
- [ ] Sufficient literature collected (10+ papers)
- [ ] Implementation examples secured (3+ repos)
- [ ] Research gaps clearly defined (3+ gaps)
- [ ] Gap Priority Matrix completed
- [ ] All evidence in table format with identifiers

### Handover Requirements
- [ ] 01_research_data.md (lightweight) created - Phase 2A input
- [ ] 01_research_data_full.md (full) created - User review
- [ ] Executive Summary completed
- [ ] Minimum 3 Key Findings derived
- [ ] Next Step clearly stated (mentioning Phase 2A Party Mode)
- [ ] All sources verified with identifiers (SS ID, KB ID, URL)
- [ ] Phase 1 Deliverables Summary completed

---

## Critical Failures (Immediate Fix Required)

- [ ] No MCP server role violations
- [ ] No unverified information marked as verified
- [ ] No missing required sections
- [ ] No below minimum quality standards
- [ ] No MANDATORY steps skipped (Steps 3, 4, 5, 8)
- [ ] BOTH output files exist (01_research_data.md AND 01_research_data_full.md)
- [ ] No hypotheses or solutions in output (Phase boundary violation)

---

## Validation Summary

**Total Checks:** 110+
**Required:** Step execution + Dual output + MCP compliance + Content quality + Phase boundary
**MANDATORY Steps:** Steps 3, 4, 5, 8, 9 (cannot be skipped)

**Minimum Pass Criteria:**
- All MANDATORY steps completed
- Both output files created and valid
- Table-based evidence format used for all gaps
- Phase boundary compliance verified
- MCP server role compliance verified

---

**Validation Result:**
- ✅ PASS: All checklist items passed
- ⚠️ PASS WITH WARNINGS: Some improvements needed
- ❌ FAIL: Critical failures detected

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 1 Research Workflow (YouRA)
