---
name: 'step-09-final-compilation'
description: 'Compile final research report and prepare Phase 2A lightweight summary'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-09-final-compilation.md'
# Final step - no nextStepFile
---

# Step 9: Final Report Compilation

**Goal:** Compile final research report and prepare Phase 2A lightweight summary

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

### 📖 File Reading Protocol (CRITICAL):

Complete execution of this step file **requires reading the entire file at once**.

**File Information**:
- 📏 Total length: ~584 lines (under 2000 lines)
- 📂 Read entire file before execution

**Required Reading Method**:
```python
# ✅ Correct Method (Recommended)
Read(file_path="{thisStepFile}") # Without limit/offset parameters

# ❌ Incorrect Method (Prohibited)
Read(file_path="{thisStepFile}", offset=0, limit=200) # Partial reading
Read(file_path="{thisStepFile}", offset=200, limit=200)
```

**⚠️ Critical Warning**: Read the entire file before execution.

---

<critical>
🚨 **ABSOLUTE REQUIREMENT - DUAL FILE OUTPUT SYSTEM** 🚨

This step MUST generate TWO files:
1. **01_research_data.md** - Lightweight summary for Phase 2A (500-1000 lines) ⭐ DEFAULT
2. **01_research_data_full.md** - Complete report for user review (5000-10000 lines)

⚠️ **BOTH files must exist before Step 9 is considered complete!**
⚠️ **Phase 2A will FAIL if lightweight version is missing!**
⚠️ **DO NOT mark Step 9 complete until BOTH files pass validation!**

Phase 2A reads the default file (01_research_data.md) which contains optimized lightweight summary.
Users can review the full report in 01_research_data_full.md.
</critical>

<critical>
⚠️ **PHASE BOUNDARY: Phase 1 = Research Collection ONLY**

- NO Hypothesis generation ❌
- NO Validation Approach proposals ❌
- NO "Primary Hypothesis" section ❌
- NO Experiment design ❌
- ONLY data collection and Gap analysis ✅

Hypothesis generation occurs in Phase 2A using Party Mode.
</critical>

<critical>
🔄 **RESUME CHECK**

Before starting:
1. Read {default_output_file}
2. Check if `{{UNFILLED:executive_summary}}` is FILLED
3. If FILLED → Report complete
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Create Executive Summary

<action>
Synthesize all findings into concise executive summary:

**Include:**
- Research question addressed
- Total sources collected (papers, repos, cases)
- Key discoveries
- Main research gaps identified
- Readiness for Phase 2A

Display in {communication_language}
</action>

### 2. Extract Key Findings

<action>
Identify 3-5 key findings from the research:

**Examples:**
- "Finding 1: Current approaches lack [specific capability]"
- "Finding 2: Strong theoretical foundation exists in [area]"
- "Finding 3: Implementation gap between [theory] and [practice]"

Focus on insights, NOT solutions.
</action>

### 3. Create Phase 2 Readiness Checklist

<action>
Verify Phase 1 deliverables:

```
✅ Sufficient literature collected (X verified sources)
✅ Implementation examples identified (X repositories)
✅ Research gaps analyzed (X gaps identified)
✅ All sources verified with proper identifiers (SS ID, KB ID, URL)
```
</action>

### 4. Select Top Evidence Sources

<action>
For the lightweight Phase 2A summary, select:

**Top 5 Academic Papers:**
- Criteria: Most cited + Most recent + Most relevant to gaps
- Must include: Title, Year, Authors, SS ID, Citations, Why Top

**Top 3 Implementation Examples:**
- Criteria: Most stars + Best documented + Most complete
- Must include: Repository, URL, Stars, Language, Why Top
</action>

### 5. Calculate Processing Time

<action>
Calculate total time from workflow start to now.
</action>

### 6. Display Completion Message

<action>
Display to user in {communication_language}:

```
🎉 Phase 1 research gathering complete!

**Collected Data:**
- Academic papers: X
- GitHub repositories: Y
- Past cases: Z
- Research gaps: W

**Generated Files:**
1. 01_research_data.md (lightweight summary for Phase 2A) ⭐ DEFAULT
2. 01_research_data_full.md (full report for user review)

**Next Step:**
Phase 2A: Hypothesis validation (Party Mode)

To start Phase 2A: *phase2a-dialogue
```
</action>

---

## ⚠️ CRITICAL: Dual Output File Generation (MANDATORY)

<critical>
🚨 **ABSOLUTE REQUIREMENT - NO EXCEPTIONS** 🚨

This step MUST generate TWO files:
1. **Lightweight Summary** (01_research_data.md) - Phase 2A input
2. **Full Report** (01_research_data_full.md) - User review

⚠️ **BOTH files must exist before Step 9 is considered complete!**
⚠️ **Phase 2A will FAIL if lightweight version is missing!**
⚠️ **DO NOT mark Step 9 complete until BOTH files pass validation!**
</critical>

---

### File 1 of 2: Lightweight Summary (01_research_data.md) ⭐ DEFAULT

<file-write>
**Create Phase 2A lightweight summary (default file):**

File path: {default_output_file} (01_research_data.md)

Content structure:

```markdown
---
phase: 1
output_for: phase2a-dialogue
generated: {{date}}
full_report: 01_research_data_full.md
phase1_complete: true
lightweight: true
---

# Phase 1 Research Summary for Phase 2A

## Research Context

### Primary Research Question
{{primary_research_question}}

### Detailed Question
{{detailed_question}}

### Phase 0 Insights

**Key Discoveries:**
{{key_insights from Phase 0}}

**Areas for Exploration:**
{{areas_for_exploration from Phase 0}}

---

## Research Gaps (CRITICAL for Hypothesis Generation)

### Gap 1: {{gap1_title}}

**Current State:** {{gap1_current_state}}

**Missing Piece:** {{gap1_missing_piece}}

**Potential Impact:** {{gap1_impact}}

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
{{gap1_scholar_evidence - ALL rows from full report}}

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
{{gap1_archon_evidence - ALL rows from full report}}

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
{{gap1_exa_evidence - ALL rows from full report}}

---

### Gap 2: {{gap2_title}}

**Current State:** {{gap2_current_state}}

**Missing Piece:** {{gap2_missing_piece}}

**Potential Impact:** {{gap2_impact}}

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
{{gap2_scholar_evidence - ALL rows}}

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
{{gap2_archon_evidence - ALL rows}}

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
{{gap2_exa_evidence - ALL rows}}

---

### Gap 3: {{gap3_title}}

**Current State:** {{gap3_current_state}}

**Missing Piece:** {{gap3_missing_piece}}

**Potential Impact:** {{gap3_impact}}

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
{{gap3_scholar_evidence - ALL rows}}

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
{{gap3_archon_evidence - ALL rows}}

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
{{gap3_exa_evidence - ALL rows}}

---

## Gap Priority Matrix

| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
{{gap_priority_matrix - from full report}}

---

## Top Evidence Sources (Quick Reference)

### Top 5 Academic Papers (Most Relevant)

**Selection Criteria:** Most cited + Most recent + Most relevant to identified gaps

| Paper Title | Year | Authors | SS ID | Citations | Why Top |
|-------------|------|---------|-------|-----------|---------|
{{Top 5 papers selected from scholar_core_papers}}

### Top 3 Implementation Examples

**Selection Criteria:** Most stars + Best documented + Most complete implementation

| Repository | URL | Stars | Language | Why Top |
|------------|-----|-------|----------|---------|
{{Top 3 repos selected from exa_repositories}}

---

## Key Findings Summary

{{key_findings - 3-5 bullet points}}

---

## Phase 2A Readiness Checklist

{{phase2_readiness - checklist from full report}}

---

## Instructions for Phase 2A

**This lightweight summary contains:**
- ✅ Research gaps with COMPLETE evidence tables (all SS IDs, KB IDs, URLs)
- ✅ Gap priority matrix for strategic hypothesis generation
- ✅ Top papers and implementations for quick reference
- ✅ Phase 0 insights for contextual understanding

**NOT included (see full report 01_research_data_full.md):**
- All search queries (10-15 queries)
- Complete literature review (all papers - only top 5 here)
- All implementation resources (all repos - only top 3 here)
- Detailed chain-of-relations analysis
- Full verification statistics

**Phase 2A Task:**
Generate 3-5 FEASIBLE hypotheses based on identified gaps using Party Mode (4 agents).

**Evidence Access:**
- All Gap evidence includes full identifiers (SS ID, KB ID, URL)
- Use these IDs to retrieve detailed information if needed
- Example: `mcp__hamid-vakilzadeh-mcpsemanticscholar__get_paper_details(paper_id="SS_ID")`

---

## Next Steps

Proceed to **Phase 2A: Hypothesis Generation**

**Command to run:**
```
*phase2a-dialogue
```

**Phase 2A Process:**
- Uses Party Mode (4 agents with feedback loop)
- Innovator, Skeptic, Strategist, Judge collaborate
- Generate and validate hypotheses
- Target: 3-5 FEASIBLE hypotheses based on gaps

---

*For complete research data and detailed analysis, see: 01_research_data_full.md*
*Total evidence sources: {{total_sources}}*
*Processing time: {{processing_time}}*
```

Write this file to: {default_output_file}

Display: "✅ File 1/2 complete - Lightweight summary saved: 01_research_data.md"
</file-write>

<checkpoint>
**✅ CHECKPOINT 1/2: Verify Lightweight Summary Created**

Before proceeding to File 2, confirm:
- [ ] 01_research_data.md file exists and is readable
- [ ] File size is 500-1000 lines (approximate)
- [ ] File contains Research Gaps section with all evidence tables
- [ ] File saved successfully

If any check fails, STOP and fix before continuing to File 2.
</checkpoint>

---

### File 2 of 2: Complete Report (01_research_data_full.md)

<critical>
⚠️ **DO NOT SKIP THIS FILE** ⚠️

**File 2 is MANDATORY for system completeness!**
- Provides complete data for user review
- Backup if lightweight version has issues
- Full documentation of research process

**YOU MUST COMPLETE THIS FILE BEFORE MARKING STEP 9 AS DONE!**
</critical>

<file-write>
**Save complete report with all details:**

File path: {research_output_path}/01_research_data_full.md

1. Read the current {default_output_file} (which still has all {{UNFILLED:...}} placeholders)
2. This is the template.md file that was initially created
3. Replace ALL `{{UNFILLED:...}}` placeholders with complete data:
   - `{{UNFILLED:executive_summary}}` with executive summary
   - `{{UNFILLED:key_findings}}` with key findings list
   - `{{UNFILLED:phase2_readiness}}` with readiness checklist
   - `{{UNFILLED:next_steps}}` with next step guidance (Phase 2A)
   - `{{UNFILLED:processing_time}}` with total processing time
   - All other placeholders filled during Steps 1-8
4. Update frontmatter:
   - Add "step-09-final-compilation" to stepsCompleted array
   - Mark status: "completed"
   - Add note: "full_report: true"
5. Write to: 01_research_data_full.md
6. Display: "✅ File 2/2 complete - Full report saved: 01_research_data_full.md"

**Note:** This file contains ALL collected data:
- All search queries
- All papers (10-20+)
- All GitHub repos (10-15+)
- Complete chain-of-relations analysis
- Full verification statistics
- All research gaps with complete evidence tables
</file-write>

<checkpoint>
**✅ CHECKPOINT 2/2: Verify Full Report Created**

After File 2, confirm:
- [ ] 01_research_data_full.md file exists and is readable
- [ ] File size > 01_research_data.md (full version should be larger)
- [ ] File size is 5000-10000 lines (approximate)
- [ ] All {{UNFILLED:...}} placeholders filled
- [ ] File saved successfully

If any check fails, regenerate full report before proceeding.
</checkpoint>

---

## ✅ FINAL VALIDATION - MUST PASS BEFORE COMPLETING STEP 9

<critical>
**⚠️ MANDATORY VALIDATION CHECKLIST ⚠️**

Before displaying completion message or marking Step 9 as complete, verify ALL of the following:

### File Existence Checks:
- [ ] 01_research_data.md exists and is readable
- [ ] 01_research_data_full.md exists and is readable

### File Size Validation:
- [ ] 01_research_data_full.md has > 5000 lines
- [ ] 01_research_data.md has 500-1000 lines AND < full report line count
- [ ] Lightweight is 20-30% of full file size

### Content Validation (Lightweight Summary):
- [ ] Contains Research Gaps section with COMPLETE evidence tables
- [ ] All [SCHOLAR] sources have SS IDs
- [ ] All [ARCHON] sources have KB Entry IDs
- [ ] All [EXA] sources have full URLs
- [ ] Gap Priority Matrix included
- [ ] Top 5 papers selected with justification
- [ ] Top 3 implementations selected with justification

### Phase Boundary Validation:
- [ ] NO "Hypothesis" section in either file
- [ ] NO "Validation Approach" section
- [ ] NO "Primary Hypothesis" text
- [ ] NO Experiment design
- [ ] NO "Innovation Opportunities" section
- [ ] Only mentions readiness for Phase 2A (no actual hypothesis generation)

### Full Report Validation:
- [ ] All {{UNFILLED:...}} placeholders filled in conclusion section
- [ ] Contains all search queries
- [ ] Contains all papers (10-20+)
- [ ] Contains all GitHub repos (10-15+)
- [ ] Complete chain-of-relations analysis
- [ ] Full verification statistics

**IF ANY CHECK FAILS:**
1. Display error: "⚠️ Step 9 validation failed - [specific check that failed]"
2. Fix the issue immediately
3. Re-run validation
4. DO NOT proceed to completion message until ALL checks pass

**ONLY AFTER ALL CHECKS PASS:**
Proceed to Completion Message and Menu below.
</critical>

---

## Menu

<menu>
**Workflow Complete:**

[V] View Reports - View generated reports
[P] Proceed to Phase 2A - Start Phase 2A hypothesis generation
[E] Exit - Return to BMad Builder
</menu>

---

## Completion Actions

<on-view>
When user selects [V] View Reports:
1. Display file paths:
   - Lightweight Summary (DEFAULT): {default_output_file} (01_research_data.md)
   - Full Report: 01_research_data_full.md
2. Display file size comparison:
   - Lightweight: ~500-1000 lines (for Phase 2A)
   - Full Report: ~5000-10000 lines (for user review)
3. Explain: "Phase 2A reads 01_research_data.md (lightweight) to reduce token usage by 85%."
4. Return to menu
</on-view>

<on-proceed>
When user selects [P] Proceed to Phase 2A:
1. Display: "Run the following command to start Phase 2A:"
2. Display: "*phase2a-dialogue"
3. Explain: "Phase 2A reads 01_research_data.md (lightweight summary), then four agents collaborate to generate hypotheses."
4. Display: "Using the lightweight summary reduces token usage by 85%! 🚀"
</on-proceed>

<on-exit>
When user selects [E] Exit:
1. Display final summary
2. Display both file locations
3. Exit workflow
4. Return to BMad Builder agent
</on-exit>

---

## Workflow Completion

<completion>
🎊 **Phase 1: Research Gathering - COMPLETE**

This workflow has successfully:
- ✅ Loaded Phase 0 brainstorm inputs
- ✅ Generated targeted search queries
- ✅ Searched Archon knowledge base
- ✅ Searched Semantic Scholar papers
- ✅ Searched Exa GitHub and resources
- ✅ Analyzed chain-of-relations
- ✅ Verified all sources
- ✅ Identified research gaps with evidence tables
- ✅ Generated lightweight summary (01_research_data.md) for Phase 2A
- ✅ Compiled full report (01_research_data_full.md) for user review

**Output Files:**
1. **Lightweight Summary (DEFAULT):** 01_research_data.md (Phase 2A automated handoff)
2. **Full Report:** 01_research_data_full.md (user review)

**Token Optimization:**
- Phase 2A reads 01_research_data.md: only 500-1000 lines instead of 5000-10000 lines
- 85% token reduction while preserving all critical evidence
- All Gap evidence tables with identifiers (SS ID, KB ID, URL) included
- Full report available for user review anytime

**Ready for:** Phase 2A-Dialogue - Hypothesis Generation (Round Table)
</completion>
