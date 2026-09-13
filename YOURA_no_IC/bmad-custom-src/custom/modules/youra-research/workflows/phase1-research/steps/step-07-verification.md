---
name: 'step-07-verification'
description: 'Summarize verification status of all collected information'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-07-verification.md'
nextStepFile: '{workflow_path}/steps/step-08-gaps-identification.md'
---

# Step 7: Verification Summary

**Goal:** Summarize verification status of all collected information

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
🔄 **RESUME CHECK**

Before starting:
1. Read {default_output_file}
2. Check if `{{UNFILLED:verification_statistics}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Calculate Verification Statistics

<action>
Review all collected sources and calculate:

**Source Verification Counts:**
- Count sources with [VERIFIED - ARCHON] tag
- Count sources with [VERIFIED - SCHOLAR] tag
- Count sources with [VERIFIED - EXA] tag
- Count any [UNVERIFIED] or [INFERRED] sources
- Count [NOT_FOUND] items

**Calculate Percentages:**
- Verified percentage: (verified / total) × 100
- Unverified percentage: (unverified / total) × 100
</action>

### 2. Measure MCP Server Performance

<action>
If performance data was collected during Steps 3-5:

**For each MCP server:**
- Total queries made
- Average response time
- Success rate
- Error count (if any)

Display:
```
**MCP Server Performance:**
- Archon: X queries, Y ms average response
- Semantic Scholar: X queries, Y ms average response
- Exa: X queries, Y ms average response
```
</action>

### 3. Assess Data Quality

<action>
Calculate quality scores (0-100):

**Completeness Score:**
- Based on: Minimum requirements met?
  - 10+ papers ✅
  - 3+ GitHub repos ✅
  - 5+ past cases ✅
  - 3+ research gaps ✅
- Score: (requirements met / total requirements) × 100

**Reliability Score:**
- Based on: Percentage of verified sources
- Score: (verified sources / total sources) × 100

**Recency Score:**
- Based on: Publication dates of papers
- Papers from last 2 years: High score
- Papers from 2-5 years: Medium score
- Papers older than 5 years: Lower score
</action>

### 4. Display Summary

<action>
Display to user in {communication_language}:

```
✅ Verification summary

**Statistics:**
- Total sources: XX
- [VERIFIED]: XX (XX%)
- [UNVERIFIED]: XX (XX%)

**MCP Server Performance:**
- Archon: X queries, Y ms average
- Scholar: X queries, Y ms average
- Exa: X queries, Y ms average

**Data Quality Assessment:**
- Completeness: XX/100
- Reliability: XX/100
- Recency: XX/100
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 7:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:verification_statistics}}` with source statistics
3. Replace `{{UNFILLED:mcp_performance}}` with MCP server performance metrics
4. Replace `{{UNFILLED:data_quality_assessment}}` with quality scores
5. Update frontmatter: Add "step-07-verification" to stepsCompleted array
6. Write file back
7. Display: "✅ Step 7 saved - verification summary recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 8 (Research Gaps Identification)
[B] Back - Return to Step 6
[S] Skip - Skip verification summary
</menu>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Update frontmatter stepsCompleted: [...previous, "step-07-verification"]
2. Load and execute: {workflow_path}/steps/step-08-gaps-identification.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-06-chain-analysis.md
</on-back>

<on-skip>
When user selects [S] Skip:
1. Replace placeholders with `*Skipped by user*`
2. Update frontmatter stepsCompleted
3. Load and execute: {workflow_path}/steps/step-08-gaps-identification.md
</on-skip>
