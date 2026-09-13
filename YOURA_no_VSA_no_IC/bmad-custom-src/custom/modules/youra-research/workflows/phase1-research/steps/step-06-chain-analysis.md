---
name: 'step-06-chain-analysis'
description: 'Analyze connection relationships among all collected information'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-06-chain-analysis.md'
nextStepFile: '{workflow_path}/steps/step-07-verification.md'
---

# Step 6: Chain-of-Relations Analysis

**Goal:** Analyze connection relationships among all collected information

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
🔄 **RESUME CHECK**

Before starting:
1. Read {default_output_file}
2. Check if `{{UNFILLED:research_evolution_path}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### 1. Analyze Connection Relationships

<action>
Analyze connections among all collected information from Steps 3, 4, and 5:

**Analysis Items:**
1. **Paper-to-Implementation Matching**
   - Which papers have corresponding GitHub implementations?
   - Which repositories cite specific papers?
   - Are there implementation gaps?

2. **Theoretical Development Pathways**
   - Trace evolution of key concepts across papers
   - Identify foundational vs. applied research
   - Map chronological development

3. **Technical Evolution Processes**
   - How has the approach evolved over time?
   - What improvements were made and when?
   - What are the current state-of-the-art methods?

4. **Research Community Networks**
   - Which authors/groups are most active?
   - Citation relationships and influence
   - Collaboration patterns
</action>

### 2. Create Research Evolution Path

<action>
Document the evolution path:

```
1. **Foundation**: [Paper A] introduced [core concept] (Year)
2. **Improvement**: [Paper B] optimized [specific aspect] (Year)
3. **Implementation**: [GitHub Repo C] provides working code
4. **Application**: [Case D from Archon] deployed in production
5. **Current State**: [Latest developments and directions]
```
</action>

### 3. Create Cross-Reference Matrix

<action>
Create table mapping papers, implementations, and cases:

| Paper | Year | GitHub Implementation | Archon Case | Status |
|-------|------|--------------------- |-------------|--------|
| Paper1 | 2024 | Repo1 ✅ | Case1 ✅ | Complete |
| Paper2 | 2023 | Repo2 ✅ | - | Partial |
| Paper3 | 2022 | - | Case2 ✅ | Theory Only |
| - | - | Repo3 ⚠️ | - | No Paper |
</action>

### 4. Display Summary

<action>
Display to user in {communication_language}:

```
🔗 Relationship analysis complete

**Connection Statistics:**
- Paper-implementation matches: X
- Complete links (paper + implementation + case): Y
- Implementation gaps (paper only): Z
- Theoretical path steps traced: W

Analysis has been saved.
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 6:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:research_evolution_path}}` with research evolution analysis
3. Replace `{{UNFILLED:cross_reference_matrix}}` with cross-reference matrix table
4. Update frontmatter: Add "step-06-chain-analysis" to stepsCompleted array
5. Write file back
6. Display: "✅ Step 6 saved - relationship analysis recorded"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 7 (Verification Summary)
[B] Back - Return to Step 5
[R] Retry - Re-run analysis
[S] Skip - Skip relationship analysis
</menu>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Update frontmatter stepsCompleted: [...previous, "step-06-chain-analysis"]
2. Load and execute: {workflow_path}/steps/step-07-verification.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-05-exa-search.md
</on-back>

<on-retry>
When user selects [R] Retry:
1. Clear current analysis
2. Re-execute this step
</on-retry>

<on-skip>
When user selects [S] Skip:
1. Replace placeholders with `*Skipped by user*`
2. Update frontmatter stepsCompleted
3. Load and execute: {workflow_path}/steps/step-07-verification.md
</on-skip>
