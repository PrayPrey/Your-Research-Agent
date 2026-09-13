---
name: 'step-08-gaps-identification'
description: 'Identify research gaps with complete evidence tables'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-08-gaps-identification.md'
nextStepFile: '{workflow_path}/steps/step-09-final-compilation.md'
---

# Step 8: Research Gaps Identification

**Goal:** Identify research gaps with complete evidence tables

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
⚠️ **PHASE BOUNDARY ENFORCEMENT**

This step identifies GAPS ONLY:
- ✅ "X is lacking" (Gap identification)
- ❌ "X can be addressed by Y" (Opportunity - Phase 2A territory)
- ❌ "X can be solved with method Y" (Hypothesis - Phase 2A territory)

DO NOT propose solutions, opportunities, or hypotheses.
Phase 2A will handle hypothesis generation using Party Mode.
</critical>

<critical>
⚠️ **TABLE-BASED EVIDENCE FORMAT (MANDATORY)**

All supporting evidence MUST be in table format with full identifiers:
- [SCHOLAR]: Must include Semantic Scholar ID (SS ID)
- [ARCHON]: Must include KB Entry ID
- [EXA]: Must include full URL

This enables Phase 2A to programmatically extract and reference sources.
</critical>

<critical>
🔄 **RESUME CHECK**

Before starting:
1. Read {default_output_file}
2. Check if `{{UNFILLED:gap1_title}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Identify Research Gaps

<action>
Review all collected data from Steps 3-7 and identify gaps:

**Identification Criteria:**
- Missing techniques or approaches
- Unexplored combinations
- Limitations in current methods
- Lack of implementations for theoretical work
- Absence of empirical validation

**Target**: Identify 3-5 significant gaps
</action>

### 2. For Each Gap: Collect Evidence in Table Format

<critical>
**EVIDENCE TABLE REQUIREMENTS**

For each gap, you MUST create THREE evidence tables:

**1. [SCHOLAR] Academic Papers Table:**
```
| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| "Full Paper Title" | 2024 | First Author et al. | abc123def456... | 25 | How this paper relates to gap |
```

**2. [ARCHON] Past Cases Table:**
```
| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| "Case/Pattern Name" | a402d7be110bf67e | "search query" | Key insight for gap |
```

**3. [EXA] Implementation Resources Table:**
```
| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| owner/repo | https://github.com/... | 139 | Python | Relevant feature |
```
</critical>

### 3. Structure Each Gap

<action>
For each Gap (minimum 3 gaps):

```
#### Gap X: [Field/Domain Title]

**Current State:** [What exists now]

**Missing Piece:** [What is lacking - NO solutions]

**Potential Impact:** High/Medium/Low

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
```
</action>

### 4. Create Gap Priority Matrix

<action>
Create priority matrix for all gaps:

```
| Gap ID | Title | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|--------|------------|----------------|----------|
| Gap 1 | [title] | High | Medium | X sources | Critical |
| Gap 2 | [title] | Medium | Low | X sources | Important |
| Gap 3 | [title] | High | High | X sources | Challenging |
```
</action>

### 5. Create Evidence Label Summary

<action>
Summarize evidence counts per gap:

```
| Source Type | Gap 1 | Gap 2 | Gap 3 | Total |
|-------------|-------|-------|-------|-------|
| [SCHOLAR] | X | X | X | X |
| [ARCHON] | X | X | X | X |
| [EXA] | X | X | X | X |
| **Total** | X | X | X | X |
```
</action>

### 6. Display Summary

<action>
Display to user in {communication_language}:

```
🔍 Research gap identification complete

**Identified Gaps:**
- Gap 1: [Title] - Impact: [High/Medium/Low]
- Gap 2: [Title] - Impact: [High/Medium/Low]
- Gap 3: [Title] - Impact: [High/Medium/Low]

**Total evidence sources: X**
- [SCHOLAR] papers: Y
- [ARCHON] cases: Z
- [EXA] resources: W

All evidence was recorded in table format.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 8:**

<critical>
⚠️ TABLE FORMAT VALIDATION

Verify all evidence placeholders contain TABLE ROWS, not list items:
- ✅ CORRECT: | "Paper Title" | 2024 | Author | abc123... | 25 | Insight |
- ❌ WRONG: - 🏷️ "Paper Title" (2024) - Authors: ...
</critical>

1. Read {default_output_file}
2. For each Gap (1, 2, 3+), replace:
   - `{{UNFILLED:gap1_title}}`, etc. with gap titles
   - `{{UNFILLED:gap1_current_state}}`, etc. with current state
   - `{{UNFILLED:gap1_missing_piece}}`, etc. with what is lacking
   - `{{UNFILLED:gap1_impact}}`, etc. with High/Medium/Low
   - `{{UNFILLED:gap1_scholar_evidence}}`, etc. with [SCHOLAR] TABLE ROWS
   - `{{UNFILLED:gap1_archon_evidence}}`, etc. with [ARCHON] TABLE ROWS
   - `{{UNFILLED:gap1_exa_evidence}}`, etc. with [EXA] TABLE ROWS
3. Replace `{{UNFILLED:gap_priority_matrix}}` with priority table rows
4. Replace `{{UNFILLED:evidence_label_summary}}` with evidence count table
5. Update frontmatter: Add "step-08-gaps-identification" to stepsCompleted array
6. Write file back
7. Display: "✅ Step 8 saved - X research gaps identified with Y supporting sources"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 9 (Final Report Compilation)
[B] Back - Return to Step 7
[R] Retry - Re-run gap identification
</menu>

<critical>
⚠️ DO NOT allow [S] Skip - Gap identification is MANDATORY
</critical>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Verify gaps identified with proper table format
2. Update frontmatter stepsCompleted: [...previous, "step-08-gaps-identification"]
3. Load and execute: {workflow_path}/steps/step-09-final-compilation.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-07-verification.md
</on-back>

<on-retry>
When user selects [R] Retry:
1. Clear current gaps
2. Re-execute this step
</on-retry>
