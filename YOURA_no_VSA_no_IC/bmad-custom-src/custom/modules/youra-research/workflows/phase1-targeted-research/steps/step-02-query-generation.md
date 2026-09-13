---
name: 'step-02-query-generation'
description: 'Generate targeted search queries from research questions and reference papers'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-02-query-generation.md'
nextStepFile: '{workflow_path}/steps/step-03-archon-search.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
---

# Step 2: Question-Based Query Generation

## STEP GOAL:

Generate targeted search queries from research questions, reference paper concepts, and brainstorm insights. Queries will be used in Steps 3-5 for MCP-based data collection across Archon, Scholar, and Exa.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on generating search queries from available inputs
- 🚫 FORBIDDEN to skip auto-resume check
- 🔄 AUTO-RESUME CHECK: Execute before anything else
- 📋 Generate queries in priority order: Reference Paper > Brainstorm Insights > Direct Question

## EXECUTION PROTOCOLS:

- 🎯 Generate 10-15 diverse queries across three priority tiers
- 💾 Save all generated queries to output file
- 📖 Use reference paper concepts as highest priority query source
- 🚫 FORBIDDEN to proceed without generating minimum query set

## CONTEXT BOUNDARIES:

- Available context: Reference paper analysis (Step 0), research question, brainstorm insights
- Focus: Query generation for Archon, Scholar, and Exa searches
- Limits: Do not execute searches yet - only generate queries
- Dependencies: Completed Step 1 with loaded research question

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {outputFile} has `{{UNFILLED:query_summary}}` filled.
- If filled → Skip to Step 3 (load {nextStepFile})
- If unfilled → Proceed with this step

### 1.5. Load Failure Context (ROUTE_TO_0 Case)

<critical>
**Check for `lessons_from_previous_attempts` from Step 1:**

If `lessons_from_previous_attempts` exists and is NOT "N/A - First attempt":
- This is a **ROUTE_TO_0** case (retry after previous failure)
- Extract failure patterns to AVOID in query generation:
  - Failed approaches/methods
  - Problematic metrics or evaluation criteria
  - Approaches that led to inconclusive results

Store as: `failure_patterns_to_avoid = [list of patterns]`

**How to Use in Query Generation:**
- DO NOT generate queries that would lead to the same failed approaches
- PRIORITIZE queries that explore ALTERNATIVE methods
- ADD explicit "alternative to X" or "different from X" queries
</critical>

### 2. Load Reference Paper Concepts (if Step 0 completed)

If Step 0 completed AND Reference Paper Analysis section exists in output file:
1. Read Reference Paper Analysis section from output file
2. Load extracted concepts from reference papers (mechanisms, architectures, terms)
3. Store as: reference_concepts = [list]

### 3. Generate Reference Paper Concept-Based Queries (Priority 1)

If reference_concepts exists, generate concept-based queries using reference paper mechanisms:
- Combine concepts from different papers
- Apply concepts to research_question domain
- Explore hybrid approaches

Store as: reference_queries = [3-5 queries]

### 4. Generate Brainstorm Insights-Based Queries (Priority 2)

If brainstorm_context.key_insights or brainstorm_context.areas_for_exploration exists:

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

Store as: brainstorm_queries = [3-5 queries]

### 5. Generate Direct Question Decomposition Queries (Priority 3)

**Direct Question Decomposition:**
- Break down {research_question} into searchable components
- Extract key technical terms and concepts
- Identify core problem domain

**Multi-Dimensional Query Construction:**

A. **Technical Queries** (specific implementations):
   - "[key_concept_1] + [key_concept_2] implementation"
   - "[mechanism_1] applied to [problem_domain]"

B. **Theoretical Queries** (foundational papers):
   - "[core_concept] theory"
   - "[approach] for [generalization_type]"

C. **Comparative Queries** (related approaches):
   - "[approach_A] vs [approach_B]"
   - "alternatives to [current_approach]"

D. **Problem-Specific Queries**:
   - Directly derived from {detailed_question}
   - Focus on specific architectural challenges

**Target**: Generate 5-8 queries from question decomposition
Store as: direct_queries = [list of 5-8 queries]

### 5.5. Generate Failure-Aware Queries (ROUTE_TO_0 Only)

<check if="failure_patterns_to_avoid exists and is not empty">

**Generate queries that explicitly explore ALTERNATIVES to failed approaches:**

1. **Alternative Method Queries:**
   - "alternative to [failed_method] for [research_domain]"
   - "[research_domain] without [failed_approach]"
   - "different approach to [problem] than [failed_approach]"

2. **Robust Metric Queries (if metric was the issue):**
   - "robust evaluation metrics for [research_domain]"
   - "alternative metrics to [failed_metric]"
   - "[research_domain] evaluation best practices"

3. **Avoid-Pattern Queries:**
   - For each pattern in failure_patterns_to_avoid:
     - Generate queries that explore the OPPOSITE approach
     - Generate queries that use DIFFERENT techniques

Store as: failure_aware_queries = [2-4 queries]

Display:
```
⚠️ ROUTE_TO_0: Generating failure-aware queries
- Avoiding: {failure_patterns_to_avoid}
- Added {count} alternative-focused queries
```
</check>

### 6. Integrate All Queries with Priority Ordering

Final Query List Structure:
1. **Failure-Aware Queries** (ROUTE_TO_0 only): {failure_aware_queries} [HIGHEST Priority]
2. **Reference Paper Queries** (if available): {reference_queries} [High Priority]
3. **Brainstorm Insights Queries** (if available): {brainstorm_queries} [High Priority]
4. **Direct Question Queries**: {direct_queries} [Standard Priority]

Total Query Count: Aim for 10-15 diverse queries (12-19 if ROUTE_TO_0)

Display to user:
```
📊 Query Generation Summary:
- Failure-aware queries (ROUTE_TO_0): {failure_aware_count} (or 'N/A')
- Reference paper queries: {reference_count}
- Brainstorm insights queries: {brainstorm_count}
- Direct question queries: {direct_count}
- Total: {total_count} queries

Query Priority Order:
🔴 Failure-aware queries (ROUTE_TO_0 - avoid past mistakes)
🥇 Reference paper concepts (user-provided context)
🥈 Brainstorm insights (key discoveries + unexplored directions)
🥉 Question decomposition (baseline coverage)
```

### 7. Save Progress

**Save progress after Step 2:**

1. Read {outputFile}
2. Replace `{{UNFILLED:query_summary}}` with query generation summary
3. Replace `{{UNFILLED:reference_queries}}` with reference paper queries (or `*No reference papers provided*`)
4. Replace `{{UNFILLED:brainstorm_queries}}` with brainstorm insights queries
5. Replace `{{UNFILLED:direct_queries}}` with direct question queries
6. Write file back
7. Display: "✅ Step 2 saved - {total_count} queries generated"

### 8. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 3 (Archon Search) [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [queries generated and saved], will you then load and read fully `{nextStepFile}` to execute and begin Archon Knowledge Base search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- **Failure context loaded (if ROUTE_TO_0 case)**
- Reference paper concepts loaded (if available)
- 10-15 diverse queries generated across priority tiers
- **Failure-aware queries generated (if ROUTE_TO_0 case)**
- Queries saved to output file with proper categorization
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check
- **Ignoring lessons_from_previous_attempts in ROUTE_TO_0 case**
- **Generating queries that repeat failed approaches**
- Not using reference paper concepts for query generation
- Generating fewer than 10 queries
- Not saving queries to output file
- Not presenting menu for user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
