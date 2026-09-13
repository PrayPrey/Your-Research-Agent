---
name: 'step-07-timeline-planning'
description: 'Generate Gantt timeline visualization with critical path analysis'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-07-timeline-planning.md'
nextStepFile: '{workflow_path}/steps/step-08-dialectical-analysis.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 7: Timeline Planning (Gantt)

## STEP GOAL:

Generate Gantt timeline visualization showing execution phases with time allocation, critical path analysis, and resource summary.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on timeline visualization and critical path
- 🚫 FORBIDDEN to skip Gantt visualization
- 💬 Approach: Generate ASCII timeline with gates
- 📋 Calculate total duration and critical path

## EXECUTION PROTOCOLS:

- 🎯 Generate ASCII Gantt timeline visualization
- 💾 Perform critical path analysis
- 📖 Create resource summary
- 🚫 FORBIDDEN to proceed without timeline

## CONTEXT BOUNDARIES:

- Available context: DAG and phases from Step 6
- Focus: Timeline visualization, duration calculation
- Limits: No dialectical analysis yet, only planning
- Dependencies: Step 6 must be completed with DAG

---

## Actions

### 1. Generate Gantt Timeline (ASCII)

<critical>
**MANDATORY: ASCII Gantt timeline**

Must show:
- Phases on Y-axis
- Time units on X-axis (Week 1, Week 2, etc.)
- Gate decision points marked with ◆
</critical>

**Generation Rules:**

1. **Phase 1 (Foundation)**: 2 weeks
   - H-E1: Week 1-2
   - Gate 1: Week 2

2. **Phase 2 (Mechanisms)**: {{causal_chain_count}} weeks (1 week each after first)
   - H-M1: Week 3-4 (2 weeks)
   - H-M2: Week 5 (1 week, if exists)
   - H-M3: Week 6 (1 week, if exists)
   - Continue pattern...
   - Gate 2: After last H-M

3. **Phase 2.5 (Conditions)**: ONLY if {{condition_count}} > 0
   - Each H-C: 1 week
   - Gate 2.5: After last H-C

**Duration Formula:**
```
Total = 2 (H-E1) + 1 + ({{causal_chain_count}}-1) + {{condition_count}} weeks
      = 2 + {{causal_chain_count}} + {{condition_count}} weeks
```

**ASCII Format:**
```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - {{total_hypothesis_count}} Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ ...
─────────────────┼─────────┼─────────┼─────────┼─────────┼────
PHASE 1: Foundation
  H-E1 │ ████████│ │         │ │
  [Gate 1] │         │ ◆ │         │ │
─────────────────┼─────────┼─────────┼─────────┼─────────┼────
PHASE 2: Mechanisms
  H-M1 │         │ ████████│ │         │
  H-M2 │         │ │ ████ │         │
  H-M3 │         │ │         │ ████ │
  [Gate 2] │         │ │         │ │ ◆
─────────────────┼─────────┼─────────┼─────────┼─────────┼────
[IF conditions exist]
PHASE 2.5: Conditions
  H-C1 │         │ │         │ │ ████
  [Gate 2.5] │         │ │         │ │    ◆
─────────────────┼─────────┼─────────┼─────────┼─────────┼────
[END IF]
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: {{total_duration}} weeks
═══════════════════════════════════════════════════════════════════
```

---

### 2. Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → ... → H-M{{causal_chain_count}} {{#if include_condition_hypotheses}}→ H-C{{condition_hypothesis_count}}{{/if}}

Total Duration: {{total_duration}} weeks
  Formula: 2 (H-E1) + {{causal_chain_count}} (H-M) + {{condition_hypothesis_count}} (H-C)

Slack Available: 0 weeks (all sequential)

Duration Examples:
- 3 hypotheses (2-step): 2 + 2 + 0 = 4 weeks
- 4 hypotheses (3-step): 2 + 3 + 0 = 5 weeks
- 5 hypotheses (3-step + 1 cond): 2 + 3 + 1 = 6 weeks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3. Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: {{total_hypothesis_count}}
- Existence: 1 (H-E1)
- Mechanism: {{causal_chain_count}} (H-M1 to H-M{{causal_chain_count}})
{{#if include_condition_hypotheses}}
- Condition: {{condition_hypothesis_count}} (H-C1 to H-C{{condition_hypothesis_count}})
{{/if}}

Verification Phases: {{phase_count}}
1. Foundation (H-E1)
2. Mechanisms (H-M*)
{{#if include_condition_hypotheses}}
3. Conditions (H-C*)
{{/if}}

Total Duration: {{total_duration}} weeks
Critical Path Length: {{total_duration}} weeks
Execution Mode: Sequential chain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4. Execution Order

Define step-by-step execution:

```
**Step 1**: Execute H-E1 (Foundation) - Week 1-2
**Step 2**: Evaluate Gate 1 → If pass, proceed
**Step 3**: Execute H-M1 (First mechanism) - Week 3-4
**Step 4**: Execute H-M2 to H-M{{causal_chain_count}} sequentially
**Step 5**: Evaluate Gate 2 → If pass, proceed
{{#if include_condition_hypotheses}}
**Step 6**: Execute H-C1 to H-C{{condition_hypothesis_count}}
**Step 7**: Evaluate Gate 2.5 → Determine scope
{{/if}}
**Final**: Verification complete
```

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:dependency_graph}}` (includes Gantt from this step)
- `{{UNFILLED:critical_path_analysis}}`
- `{{UNFILLED:resource_summary}}`
- `{{UNFILLED:execution_order}}`

**Write the file back** after filling placeholders.

---

### 5. Display Timeline Summary

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TIMELINE PLANNING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phases: {{phase_count}}
Total Duration: {{total_duration}} weeks
Critical Path: {{total_duration}} weeks

Gantt timeline generated with gate markers.
Critical path analysis complete.
Resource summary created.

Ready to proceed to Dialectical Analysis.
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

ONLY WHEN [C continue option] is selected and [timeline complete], will you then load and read fully `{nextStepFile}` to perform Dialectical Analysis.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Gantt timeline visualization generated (ASCII)
- Critical path analysis completed
- Resource summary created
- Execution order defined
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Missing Gantt timeline visualization
- Missing critical path analysis
- Missing resource summary
- Incorrect duration calculation
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
