---
name: 'step-06-dependency-graph'
description: 'Build dependency graph (DAG) for hypothesis verification order'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-06-dependency-graph.md'
nextStepFile: '{workflow_path}/steps/step-07-timeline-planning.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 6: Dependency Graph (DAG)

## STEP GOAL:

Build dependency graph (DAG) showing hypothesis verification order with gate conditions. Analyze dependencies and define verification phases.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on dependency analysis and DAG generation
- 🚫 FORBIDDEN to skip DAG visualization
- 💬 Approach: Analyze hypothesis dependencies systematically
- 📋 Define verification phases with gate conditions

## EXECUTION PROTOCOLS:

- 🎯 Analyze all hypothesis dependencies from Step 4
- 💾 Generate ASCII DAG visualization showing hierarchy
- 📖 Define verification phases and gate conditions
- 🚫 FORBIDDEN to proceed without DAG visualization

## CONTEXT BOUNDARIES:

- Available context: Hypothesis inventory from Step 4, risks from Step 5
- Focus: Dependency analysis, phase definition, gate conditions
- Limits: No timeline yet, only structure
- Dependencies: Step 5 must be completed with risk analysis

---

## Actions

### 1. Dependency Analysis

Analyze all hypotheses from Step 4:

**For each hypothesis:**
- Identify prerequisites (from hypothesis specifications)
- Calculate dependency depth (Level 0 = no dependencies)
- Detect circular dependencies (ERROR if found)
- Identify parallelization opportunities

**Create dependency map (DYNAMIC):**
```
Hypothesis → Prerequisites
H-E1 → []
{{#each causal_steps}}
H-M{{@index+1}} → [{{#if @first}}H-E1{{else}}H-M{{@index}}{{/if}}]
{{/each}}
{{#if include_condition_hypotheses}}
{{#each selected_conditions}}
H-C{{@index+1}} → [H-M{{../causal_chain_count}}]
{{/each}}
{{/if}}
```

---

### 2. Generate Dependency Visualization (DAG)

<critical>
**DYNAMIC GENERATION - NO FIXED EXAMPLES**

Generate DAG based on ACTUAL hypothesis counts.
ALL hypotheses are SEQUENTIAL (no parallelization in incremental mode).
</critical>

**Generation Rules:**

1. **Level 0 (Root)**: Always H-E1 (no dependencies)
2. **Level 1 to N**: H-M1 through H-M{{causal_chain_count}} (sequential)
3. **Level N+1** (optional): H-C hypotheses if condition_count > 0
4. **Level Final**: Terminal (depends on last hypothesis)

**ASCII Format:**
```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - {{total_hypothesis_count}} Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 to {{causal_chain_count}} - Mechanisms]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    ... (continue for each H-M)
         │
         ▼
[IF {{condition_count}} > 0:]
[Level {{causal_chain_count}}+1 - Conditions]
    H-C1 ← H-M{{causal_chain_count}}
         │
         ▼
[END IF]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → ... → H-M{{causal_chain_count}}
═══════════════════════════════════════════════════════════
```

---

### 3. Verification Phases with Gate Conditions

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | {{sh1_existence}} validation | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, reassess entire hypothesis.

**Phase 2 - Core Mechanisms** ({{causal_chain_count}} hypotheses)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
{{#each causal_steps}}
| H-M{{@index+1}} | {{#if @first}}H-E1{{else}}H-M{{@index}}{{/if}} | {{#if @first}}MUST PASS{{else}}Should pass{{/if}} |
{{/each}}

→ **Gate 2**: H-M1 must pass. Later H-M failures = document limitation.

{{#if include_condition_hypotheses}}
**Phase 2.5 - Conditions** ({{condition_hypothesis_count}} hypotheses)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
{{#each selected_conditions}}
| H-C{{@index+1}} | H-M{{../causal_chain_count}} | Should pass |
{{/each}}

→ **Gate 2.5**: Condition failures narrow scope but don't invalidate.
{{/if}}

---

### 4. Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| ... | ... | ... | ... |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5. Display DAG Summary

Present to user:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DEPENDENCY GRAPH COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hypotheses: {{total_hypothesis_count}}
Levels: {{level_count}}
Phases: {{phase_count}}

Gate Conditions Defined:
- Gate 1 (Foundation): MUST_WORK
- Gate 2 (Mechanisms): MUST_WORK (H-M1)
{{#if include_condition_hypotheses}}
- Gate 2.5 (Conditions): SHOULD_WORK
{{/if}}

Ready to generate execution timeline.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Update frontmatter, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - respond then redisplay menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [DAG generated], will you then load and read fully `{nextStepFile}` to create timeline visualization.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Dependency analysis completed for all hypotheses
- DAG visualization generated (ASCII format)
- Verification phases defined with gate conditions
- Dependency hierarchy table created
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Missing DAG visualization
- Gate conditions not defined
- Missing dependency hierarchy table
- Circular dependencies not detected
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
