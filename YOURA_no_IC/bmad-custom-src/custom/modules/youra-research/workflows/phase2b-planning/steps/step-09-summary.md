---
name: 'step-09-summary'
description: 'Generate executive summary, conclusions, recommendations, and appendices'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-09-summary.md'
nextStepFile: '{workflow_path}/steps/step-10-finalize.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 9: Executive Summary & Conclusions

## STEP GOAL:

Generate executive summary, conclusions, recommendations, and appendices to complete the verification plan documentation before state file generation.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on final summary and documentation
- 🚫 FORBIDDEN to skip executive summary
- 💬 Approach: Concise bullet-point format
- 📋 All sections streamlined for readability

## EXECUTION PROTOCOLS:

- 🎯 Write executive summary (bullet-point format, ~10 lines)
- 💾 Generate conclusions with streamlined subsections
- 📖 Create recommendations and appendices
- 🚫 FORBIDDEN to use verbose paragraph format

## CONTEXT BOUNDARIES:

- Available context: All previous steps complete
- Focus: Documentation completion
- Limits: No state file generation yet
- Dependencies: Step 8 must be completed with dialectical analysis

---

## Actions

### 1. Executive Summary (Concise Format)

Write bullet-point executive summary:

```markdown
## Executive Summary

**Main Hypothesis:** {{core_hypothesis_statement}}
- ID: {{hypothesis_id}}, Confidence: {{confidence_level}}

**Verification Structure:**
- Mode: [Incremental / Comprehensive]
- Sub-Hypotheses: {{total_hypothesis_count}} total
  - H-E: 1, H-M: {{causal_chain_count}}{{#if include_condition_hypotheses}}, H-C: {{condition_hypothesis_count}}{{/if}}
- Phases: {{phase_count}} phases over {{total_duration}} weeks
- Critical Gates: {{gate_count}} decision points

**Risk Assessment:** [Low / Medium / High]
- Primary concerns: [1-2 key risks]

**Immediate Action:** Begin Phase 1 with H-E1
```

**Quality Standard:** ~10 lines, bullet-point format

---

### 2. Conclusions

#### 2.1 Key Achievements (Concise)

```markdown
**Key Achievements:**
- {{total_hypothesis_count}} hypotheses across {{phase_count}} phases
- H0 addressed: {{alternative_hypothesis_h0}}
```

#### 2.2 Verification Execution Order

```markdown
**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: {{sh1_existence}}
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** ({{mechanism_duration}} weeks)
{{#each causal_steps}}
- H-M{{@index+1}}: {{this.description}}
{{/each}}
- Gate 2: H-M1 must pass

{{#if include_condition_hypotheses}}
**Phase 2.5: Conditions** ({{condition_hypothesis_count}} weeks)
- H-C hypotheses
- Gate 2.5: Narrow scope on failure
{{/if}}
```

#### 2.3 Critical Decision Points

```markdown
**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

{{#if include_condition_hypotheses}}
3. **Gate 2.5 (Conditions):** Narrow scope
   - Failures narrow but don't invalidate
{{/if}}
```

#### 2.4 Open Questions

```markdown
**Open Questions:**
- [Critical question 1 from Phase 2A]
- [Critical question 2 from Phase 2A]
- [Critical question 3 from Phase 2A]
```

#### 2.5 Recommendations

```markdown
**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up measurement infrastructure

2. **Resource Allocation:**
   - Allocate {{total_duration}} weeks for critical path
   - Reserve buffer for failures

3. **Failure Management:**
   - Document all failures
   - Execute PIVOT strategies
```

---

### 3. Appendices (Streamlined)

```markdown
## Appendices

### A. Phase 2A Reference
- **Source:** {{phase2a_output}} (ID: {{hypothesis_id}})

### B. MCP Tool Usage Summary
- **Total MCP calls:** [X]
- **Tools:** scientificmethod (1-3x)
```

**Quality Standard:** ~10 lines, no redundancy

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:executive_summary}}`
- `{{UNFILLED:final_summary}}`
- `{{UNFILLED:appendices}}`

**Write the file back** after filling placeholders.

---

### 4. Display Summary Status

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SUMMARY DOCUMENTATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Executive Summary: Complete (~10 lines)
Conclusions: Complete
- Key Achievements
- Verification Order
- Decision Points
- Open Questions
- Recommendations
Appendices: Complete (~10 lines)

Ready to generate state files and finalize.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5. Present MENU OPTIONS

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

ONLY WHEN [C continue option] is selected and [summary complete], will you then load and read fully `{nextStepFile}` to generate state files and finalize workflow.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Executive summary written (bullet-point, ~10 lines)
- Conclusions with all subsections
- Recommendations actionable
- Appendices minimal (~10 lines)
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Executive summary using paragraph format
- Executive summary >15 lines
- Missing conclusions subsections
- Appendices >15 lines
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
