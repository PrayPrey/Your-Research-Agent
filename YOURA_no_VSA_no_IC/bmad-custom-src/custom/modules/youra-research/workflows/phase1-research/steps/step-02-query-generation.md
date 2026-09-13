---
name: 'step-02-query-generation'
description: 'Generate comprehensive search queries from research questions and brainstorm insights'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-research'
thisStepFile: '{workflow_path}/steps/step-02-query-generation.md'
nextStepFile: '{workflow_path}/steps/step-03-archon-search.md'
---

# Step 2: Question-Based Query Generation

**Goal:** Generate comprehensive search queries from research questions and brainstorm insights

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

---

## Critical Instructions

<critical>
🔄 **RESUME CHECK**

Before starting, check if this step is already completed:
1. Read {default_output_file}
2. Check if `{{UNFILLED:query_generation_summary}}` is FILLED
3. If FILLED → Skip to next step
4. If UNFILLED → Proceed with this step
</critical>

---

## Step Instructions

### Priority 1: Brainstorm Insights-Based Queries

<check if="brainstorm_context.key_insights exists OR brainstorm_context.areas_for_exploration exists">

<action>
Generate queries from Brainstorm Session Insights:

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

### Priority 2: Direct Question Decomposition

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

### Query Integration and Prioritization

<action>
Integrate all generated queries with priority ordering:

Final Query List Structure:
1. **Brainstorm Insights Queries** (if available): {{brainstorm_queries}} [High Priority]
2. **Direct Question Queries**: {{direct_queries}} [Standard Priority]

Total Query Count: Aim for 10-15 diverse queries

Display to user in {communication_language}:
```
📊 Query generation summary:
- Brainstorm insight queries: {{brainstorm_count}} (from key discoveries + exploration areas)
- Direct question queries: {{direct_count}}
- Total: {{total_count}} queries

Query priority:
🥇 Brainstorm insights (key discoveries + unexplored directions from Phase 0)
🥈 Question decomposition (baseline coverage)
```
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 2:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:query_generation_summary}}` with query source counts
3. Replace `{{UNFILLED:key_insights_queries}}` with queries from Phase 0 Key Discoveries (or `*No brainstorm insights available*`)
4. Replace `{{UNFILLED:exploration_queries}}` with queries from Phase 0 Areas for Further Exploration (or `*No exploration areas provided*`)
5. Replace `{{UNFILLED:direct_decomposition_queries}}` with Technical, Theoretical, Comparative, Problem-Specific queries
6. Replace `{{UNFILLED:query_rationale}}` with reasoning for query construction choices
7. Update frontmatter: Add "step-02-query-generation" to stepsCompleted array
8. Write file back
9. Display: "✅ Step 2 saved - {{total_count}} queries generated"
</file-write>

---

## Menu

<menu>
**Next Step:**

[C] Continue - Move to Step 3 (Archon Knowledge Base Search)
[B] Back - Return to Step 1
[S] Skip - Skip query generation (not recommended)
</menu>

---

## Next Step

<on-continue>
When user selects [C] Continue:
1. Update frontmatter stepsCompleted: [...previous, "step-02-query-generation"]
2. Load and execute: {workflow_path}/steps/step-03-archon-search.md
</on-continue>

<on-back>
When user selects [B] Back:
1. Load and execute: {workflow_path}/steps/step-01-initialize.md
</on-back>

<on-skip>
When user selects [S] Skip:
1. Replace all query placeholders with `*Skipped by user*`
2. Update frontmatter stepsCompleted
3. Load and execute: {workflow_path}/steps/step-03-archon-search.md
</on-skip>
