---
name: 'step-08-dialectical-analysis'
description: 'Perform Thesis-Antithesis-Synthesis dialectical evaluation for robust verification'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-08-dialectical-analysis.md'
nextStepFile: '{workflow_path}/steps/step-09-summary.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 8: Dialectical Analysis

## STEP GOAL:

Perform Thesis-Antithesis-Synthesis dialectical evaluation using the null hypothesis (H0) from Phase 2A. This ensures robust verification by considering opposing viewpoints and producing a balanced assessment.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on dialectical evaluation
- 🚫 FORBIDDEN to skip dialectical analysis
- 💬 Approach: Thesis-Antithesis-Synthesis structure
- 📋 Use H0 from Phase 2A as antithesis foundation

## EXECUTION PROTOCOLS:

- 🎯 Develop thesis statement from main hypothesis
- 💾 Construct antithesis from null hypothesis (H0)
- 📖 Synthesize balanced evaluation
- 🚫 FORBIDDEN to proceed without synthesis

## CONTEXT BOUNDARIES:

- Available context: Main hypothesis, H0, timeline from Steps 6-7
- Focus: Balanced dialectical evaluation
- Limits: No finalization yet, only analysis
- Dependencies: Step 7 must be completed with timeline

---

## Actions

### 1. Thesis Statement

Develop thesis from main hypothesis:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim:** {{core_hypothesis_statement}}

**Supporting Evidence:**
1. [Evidence from Phase 2A Section 1.3 causal mechanism]
2. [Evidence from key assumptions A1-A5]
3. [Evidence from testable predictions]

**Strengths:**
- [Strength 1: Based on established theory/evidence]
- [Strength 2: Clear causal mechanism]
- [Strength 3: Testable predictions]

**Expected Outcomes:**
- Primary: {{prediction_1_primary}}
- Secondary: {{prediction_2}}
- Tertiary: {{prediction_3}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 2. Antithesis Development (H0-Based)

Construct antithesis from null hypothesis:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0):** {{alternative_hypothesis_h0}}

**Counter-Arguments:**
1. [Based on baseline limitations from {{why_baselines_insufficient}}]
2. [Based on assumption violations from A1-A5]
3. [Based on scope limitations from {{scope_not_applies}}]

**Potential Failure Points:**
- [Failure point 1: From risk R1]
- [Failure point 2: From risk R2]
- [Failure point 3: From risk R3]

**Conditions Under Which H0 Would Be Supported:**
- If {{falsification_criteria}} is met
- If mechanism step fails at [critical point]
- If assumptions A1-A5 are violated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3. Synthesis

Create balanced evaluation:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment:**

The hypothesis {{hypothesis_id}} presents a testable claim that
[thesis summary]. However, the null hypothesis raises valid concerns
regarding [antithesis summary].

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M*):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass
- {{prediction_1_primary}} is confirmed
- Mechanism chain validates

**Conditions for Antithesis Support:**
- H-E1 fails (existence not demonstrated)
- Critical H-M1 fails (mechanism broken)
- {{falsification_criteria}} is met

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4. Robustness Assessment Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Phenomenon exists | May be artifact | H-E1 test |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-N tests |
| Scope | Applies broadly | Limited conditions | H-C tests |
| Performance | Outperforms baselines | Marginal improvement | Phase 5 |

**Overall Robustness Score:** [High/Medium/Low]

**Confidence in Verification Plan:** {{confidence_level}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:dialectical_analysis}}`
- `{{UNFILLED:thesis_statement}}`
- `{{UNFILLED:antithesis_development}}`
- `{{UNFILLED:synthesis}}`
- `{{UNFILLED:robustness_assessment}}`

**Write the file back** after filling placeholders.

---

### 5. Display Dialectical Summary

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DIALECTICAL ANALYSIS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thesis: {{core_hypothesis_statement}}
Antithesis: {{alternative_hypothesis_h0}}

Synthesis: Verification plan addresses dialectic through
sequential hypothesis testing with gate conditions.

Robustness: [High/Medium/Low]
Confidence: {{confidence_level}}

Ready to generate executive summary.
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

ONLY WHEN [C continue option] is selected and [dialectical analysis complete], will you then load and read fully `{nextStepFile}` to generate executive summary.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Thesis statement developed from main hypothesis
- Antithesis constructed from H0
- Synthesis provides balanced evaluation
- Robustness assessment table generated
- Resolution path defined
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping dialectical analysis
- Missing antithesis development
- No synthesis provided
- Missing robustness assessment
- One-sided evaluation (no H0 consideration)
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
