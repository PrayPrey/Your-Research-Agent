---
name: 'step-08-gaps-identification'
description: 'Identify research gaps specific to the research question with relevance validation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-08-gaps-identification.md'
nextStepFile: '{workflow_path}/steps/step-09-final-compilation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 8: Research Gaps Identification

## STEP GOAL:

Identify research gaps specific to the research question with relevance validation. Every gap MUST be directly connected to user inputs. This step is CRITICAL for Phase 2A hypothesis generation.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on identifying gaps connected to user inputs
- 🚫 FORBIDDEN to skip auto-resume check or gap relevance validation
- ⚠️ GAP RELEVANCE ENFORCEMENT: Every gap MUST connect to research_question
- 📋 Identify Gaps ONLY - DO NOT propose opportunities, hypotheses, or solutions
- ⚠️ CRITICAL: Output evidence in TABLE FORMAT for Phase 2A extraction

## EXECUTION PROTOCOLS:

- 🎯 Validate each gap against user inputs before including
- 💾 Save gaps with supporting evidence tables to output file
- 📖 Label all evidence with proper source tags
- 🚫 FORBIDDEN to include tangential or general field gaps

## CONTEXT BOUNDARIES:

- Available context: All collected data, research question, detailed question, reference papers
- Focus: Gap identification with strict relevance validation
- Limits: Do not propose solutions or hypotheses (Phase 1 boundary)
- Dependencies: Completed Steps 3-7 with verified data

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:gap1_title}}` filled.
- If filled → Skip to Step 9 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. User Input Recall (Gap Relevance Anchor)

**Pre-Gap Identification: Review User Inputs**

Before identifying ANY gaps, explicitly recall and display:

📌 **User's Original Inputs:**
1. **Main Research Question**: {research_question}
2. **Detailed Question**: {detailed_question} (or "Not provided")
3. **Reference Papers**: {reference_papers} (or "Not provided")

All gaps identified below MUST pass the relevance test against these inputs.

### 3. Gap Relevance Validation Protocol

**For EACH potential gap, answer these questions before including:**

1. **Research Question Connection** (MANDATORY):
   - Q: "Does this gap directly affect our ability to answer {research_question}?"
   - If NO → DISCARD this gap
   - If YES → Document HOW it affects the research question

2. **Detailed Question Connection** (if {detailed_question} provided):
   - Q: "Does this gap relate to {detailed_question}?"
   - If YES → Mark as "Addresses Detailed Question" and explain connection

3. **Reference Paper Connection** (if {reference_papers} provided):
   - Q: "Is this gap identified or implied in the reference papers?"
   - If YES → Mark as "Extends Reference Paper" and cite specific limitation

**Relevance Classification for Each Gap:**
- 🎯 `PRIMARY` - Directly blocks answering {research_question}
- 🔗 `SECONDARY` - Relates to {detailed_question} or extends {reference_papers}
- ⚠️ `CONTEXTUAL` - Provides important background but less direct

Only include gaps classified as PRIMARY or SECONDARY.

### 4. Identify Research Gaps (3 gaps minimum)

Identify research gaps specific to {research_question}

**For each gap, provide:**

1. **Gap Title**: Brief descriptive title
2. **Relevance Classification**: PRIMARY or SECONDARY
3. **Connection Type**:
   - ☑️ Blocks answering {research_question}: [Explain how]
   - ☐/☑️ Relates to {detailed_question}: [Explain if applicable]
   - ☐/☑️ Extends {reference_papers} limitation: [Cite specific limitation if applicable]
4. **Current State**: What exists currently
5. **Missing Piece**: What is lacking for {research_question}
6. **Potential Impact**: High/Medium/Low

### 5. Label Supporting Evidence (TABLE FORMAT - CRITICAL!)

**All supporting evidence MUST be output in table format with full identifiers.**
This enables Phase 2A to programmatically extract and reference sources.

**[SCHOLAR] Academic Papers - Use this table format:**

| Paper Title | Year | Authors | SS ID | Citations | Key Insight |
|-------------|------|---------|-------|-----------|-------------|
| "Full Paper Title" | 2024 | First Author et al. | abc123def456... | 25 | How this paper relates to gap |

**[ARCHON] Past Cases - Use this table format:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| "Case/Pattern Name" | a402d7be110bf67e | "search query" | Key insight/pattern applicable to gap |

**[EXA] Implementation Resources - Use this table format:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| owner/repo | https://github.com/... | 139 | Python | Specific feature relevant to gap |

**[REFERENCE] Reference Papers (if provided) - Use this table format:**

| Paper Title | Source | Limitation | Open Question |
|-------------|--------|------------|---------------|
| "Reference Paper Title" | Local/arXiv | Specific limitation leading to gap | Specific open question |

### 6. Build Gap Priority Matrix

Create gap priority matrix for Phase 2A:

| Gap ID | Relevance | Connection to {research_question} | Connection to {detailed_question} | Extends Reference Paper | Impact | Evidence Count | Priority |
|--------|-----------|-----------------------------------|-----------------------------------|-------------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ [How] | ☐/☑️ [If applicable] | ☐/☑️ [Paper & limitation] | High | X sources | Critical |

### 7. Create User Input → Gap Traceability Summary

**{research_question}** directly addressed by:
- Gap 1: [Brief explanation]
- Gap X: [Brief explanation]

**{detailed_question}** (if provided) addressed by:
- Gap 2: [Brief explanation]

**{reference_papers}** limitations (if provided) extended by:
- Gap 3: Extends "[Paper Title]" limitation on [specific limitation]

### 8. Save Progress

**Save progress after Step 8:**

1. Read {outputFile}
2. Replace `{{UNFILLED:user_input_recall}}` with user input recall section
3. For each Gap (1, 2, 3), replace placeholders with gap content and TABLE ROWS
4. Replace `{{UNFILLED:gap_priority_matrix}}` with table rows
5. Replace `{{UNFILLED:gap_traceability}}` with traceability summary
6. Write file back
7. Display: "✅ Step 8 saved - X research gaps identified with Y supporting sources"

### 9. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 9 (Final Compilation) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [gaps identified with TABLE format evidence], will you then load and read fully `{nextStepFile}` to execute and begin final report compilation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- User inputs recalled and displayed before gap identification
- At least 3 gaps identified with relevance validation
- All gaps have PRIMARY or SECONDARY classification
- Supporting evidence in TABLE format with full identifiers
- Gap priority matrix and traceability summary created
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check or user input recall
- Including gaps not connected to research_question
- Not validating gap relevance
- Using list format instead of TABLE format for evidence
- Proposing solutions or hypotheses (Phase 1 boundary violation)
- Not presenting menu for user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
