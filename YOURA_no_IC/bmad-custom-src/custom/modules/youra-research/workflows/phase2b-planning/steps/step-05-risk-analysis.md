---
name: 'step-05-risk-analysis'
description: 'Identify risks from assumptions and create mitigation strategies'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-05-risk-analysis.md'
nextStepFile: '{workflow_path}/steps/step-06-dependency-graph.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 5: Risk Analysis

## STEP GOAL:

Identify risks from Phase 2A key assumptions (A1-A5), map risks to hypotheses, and develop mitigation strategies. This step ensures robust verification planning by anticipating potential failure points.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on risk identification and mitigation planning
- 🚫 FORBIDDEN to skip risk analysis
- 💬 Approach: Systematic assumption-to-risk mapping
- 📋 Each assumption violation = potential risk

## EXECUTION PROTOCOLS:

- 🎯 Map each assumption (A1-A5) to potential risks
- 💾 Link risks to affected hypotheses
- 📖 Develop mitigation strategies for each risk
- 🚫 FORBIDDEN to proceed without risk mitigation plans

## CONTEXT BOUNDARIES:

- Available context: Phase 2A key assumptions, hypothesis inventory
- Focus: Risk identification and mitigation
- Limits: No dependency analysis yet, only risk planning
- Dependencies: Step 4 must be completed with hypothesis inventory

---

## Actions

### 1. Load Key Assumptions from Phase 2A

Retrieve `{{key_assumptions}}` from Phase 2A Section 1.4:

```
| ID | Assumption | Evidence | Consequence if Violated |
|----|------------|----------|-------------------------|
| A1 | [Assumption 1] | [Evidence] | [Consequence] |
| A2 | [Assumption 2] | [Evidence] | [Consequence] |
| A3 | [Assumption 3] | [Evidence] | [Consequence] |
| A4 | [Assumption 4] | [Evidence] | [Consequence] |
| A5 | [Assumption 5] | [Evidence] | [Consequence] |
```

---

### 2. Assumption-to-Risk Mapping

For EACH assumption, identify the associated risk:

```
Assumption A{N} → Risk R{N}

Risk R{N}:
- Description: What happens if A{N} is violated?
- Severity: High | Medium | Low
- Likelihood: High | Medium | Low
- Impact: Which hypotheses are affected?
```

**Risk Severity Matrix:**

| Likelihood | Low Impact | Medium Impact | High Impact |
|------------|-----------|---------------|-------------|
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

---

### 3. Risk-Hypothesis Mapping

Map each risk to affected hypotheses:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1, H-M1 | [Severity] |
| R2 | A2 | H-M2, H-M3 | [Severity] |
| R3 | A3 | H-M1 to H-M{N} | [Severity] |
| R4 | A4 | H-C1 (if exists) | [Severity] |
| R5 | A5 | All hypotheses | [Severity] |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4. Develop Mitigation Strategies

For EACH risk, define mitigation strategy:

```markdown
**Risk R{N}: [Risk Title]**

**Source Assumption:** A{N} - [Assumption statement]

**Description:** [What could go wrong]

**Affected Hypotheses:** [List of H-* IDs]

**Severity:** [Critical | High | Medium | Low]

**Mitigation Strategy:**
1. **Prevention:** [How to prevent this risk from occurring]
2. **Detection:** [How to detect if risk is materializing]
3. **Response:** [What to do if risk occurs]
   - PIVOT: [Alternative approach]
   - SCOPE: [Reduced scope option]
   - ABORT: [Conditions for abandoning hypothesis]

**Early Warning Indicators:**
- [Indicator 1]
- [Indicator 2]
```

---

### 5. Baseline Failure Pattern Analysis (OPTIONAL)

If `{{why_baselines_insufficient}}` is available from Phase 2A Section 4:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BASELINE FAILURE PATTERNS → RISKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| [Limitation 1] | [Risk] | [Strategy] |
| [Limitation 2] | [Risk] | [Strategy] |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 6. Generate Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | [Brief] | A1 | [Level] | H-E1, H-M1 | [Strategy] |
| R2 | [Brief] | A2 | [Level] | H-M2-3 | [Strategy] |
| R3 | [Brief] | A3 | [Level] | H-M* | [Strategy] |
| R4 | [Brief] | A4 | [Level] | H-C* | [Strategy] |
| R5 | [Brief] | A5 | [Level] | All | [Strategy] |

Critical Risks: [Count]
High Risks: [Count]
Medium Risks: [Count]
Low Risks: [Count]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:risk_analysis}}`
- `{{UNFILLED:risk_hypothesis_mapping}}`
- `{{UNFILLED:mitigation_strategies}}`
- `{{UNFILLED:risk_summary_table}}`

**Write the file back** after filling placeholders.

---

### 7. Display Risk Analysis Summary

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK ANALYSIS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Risks Identified: {{risk_count}}
- Critical: {{critical_count}}
- High: {{high_count}}
- Medium: {{medium_count}}
- Low: {{low_count}}

All risks mapped to hypotheses with mitigation strategies.
Ready to proceed to Dependency Graph generation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 8. Present MENU OPTIONS

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

ONLY WHEN [C continue option] is selected and [risk analysis complete], will you then load and read fully `{nextStepFile}` to begin Dependency Graph generation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All assumptions (A1-A5) mapped to risks
- Risk-hypothesis mapping complete
- Mitigation strategy for each risk
- Risk summary table generated
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping risk analysis
- Missing assumption-to-risk mapping
- Risks without mitigation strategies
- Missing risk-hypothesis connections
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
