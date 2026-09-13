---
name: 'step-06-chain-analysis'
description: 'Analyze connections and relationships among collected research data'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-06-chain-analysis.md'
nextStepFile: '{workflow_path}/steps/step-07-verification.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 6: Chain-of-Relations Analysis

## STEP GOAL:

Analyze connections and relationships among all collected research data from Steps 3-5. Build research evolution paths, concept integration maps, and cross-reference matrices to understand how sources relate to the research question.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on analyzing relationships among collected data
- 🚫 FORBIDDEN to skip auto-resume check
- 🔄 AUTO-RESUME CHECK: Execute before anything else
- 📋 Do not generate hypotheses - only analyze existing data relationships

## EXECUTION PROTOCOLS:

- 🎯 Analyze connections with focus on research question
- 💾 Save analysis results to output file
- 📖 Reference all three data sources (Archon, Scholar, Exa)
- 🚫 FORBIDDEN to propose solutions (Phase 1 boundary)

## CONTEXT BOUNDARIES:

- Available context: All data collected from Steps 3-5
- Focus: Relationship analysis, evolution paths, cross-references
- Limits: Do not generate hypotheses or solutions
- Dependencies: Completed Steps 3-5 with MCP search results

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:research_evolution_path}}` filled.
- If filled → Skip to Step 7 (load {nextStepFile})
- If unfilled → Proceed with this step

### 2. Analyze Connection Relationships

Analyze connection relationships among all collected information, with focus on research question:

**Analysis items specific to {research_question}:**
- How do found papers relate to reference papers (if provided)?
- Which implementations can be adapted to address {detailed_question}?
- What theoretical foundations support the proposed approach?
- How does the research community address similar challenges?
- What is the evolution path of relevant techniques?

### 3. Build Research Evolution Path

Create research evolution path specific to question:

```
1. Foundation: [Paper A] introduced {key_concept_1}
2. Extension: [Paper B] applied to {domain}
3. Implementation: [GitHub Repo C] provides code for {mechanism}
4. Reference Papers: [User Paper] proposes {novel_approach}
5. Research Question: {research_question} combines these approaches
```

### 4. Create Concept Integration Map

Visualize concept integration:

```
{key_concept_1} (from Reference Paper 1)
    ↓
{key_concept_2} (from Reference Paper 2)
    ↓
{proposed_integration} (Research Question)
    ↑
[Supporting Papers] + [Implementation Examples]
```

### 5. Build Cross-Reference Matrix

Create cross-reference matrix:

| Paper/Resource | Relevance to Question | Implementation Available | Adaptability |
|----------------|----------------------|-------------------------|--------------|
| Reference Paper 1 | Direct | Partial | High |
| Found Paper 1 | High | Yes | Medium |
| GitHub Repo 1 | Medium | Yes | High |

### 6. Extract Architectural Insights

Extract architectural insights for {research_question}:
- Design Pattern 1: {pattern_description}
- Design Pattern 2: {pattern_description}
- Potential Solution Approaches: {approaches}

**Note:** Do not propose solutions - only identify patterns from existing data.

### 7. Save Progress

**Save progress after Step 6:**

1. Read {outputFile}
2. Replace `{{UNFILLED:research_evolution_path}}` with research evolution analysis
3. Replace `{{UNFILLED:concept_integration_map}}` with concept integration map
4. Replace `{{UNFILLED:cross_reference_matrix}}` with cross-reference matrix
5. Write file back
6. Display: "✅ Step 6 saved - Chain-of-relations analysis recorded"

### 8. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 7 (Verification) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [chain-of-relations analysis saved], will you then load and read fully `{nextStepFile}` to execute and begin verification summary.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- Research evolution path created
- Concept integration map visualized
- Cross-reference matrix built
- All analysis saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- Not analyzing relationships among collected data
- Generating hypotheses or solutions (Phase 1 boundary violation)
- Not saving analysis to output file
- Not presenting menu for user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
