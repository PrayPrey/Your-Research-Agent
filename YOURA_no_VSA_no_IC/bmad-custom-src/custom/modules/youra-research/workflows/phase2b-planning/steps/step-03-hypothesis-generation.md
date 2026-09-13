---
name: 'step-03-hypothesis-generation'
description: 'Generate sub-hypotheses using ClearThought MCP scientific method'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-03-hypothesis-generation.md'
nextStepFile: '{workflow_path}/steps/step-04-hypothesis-inventory.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# MCP Tool References
scientificMethodTool: 'mcp__clearThought__scientificmethod'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 3: Sub-Hypothesis Generation with MCP

## STEP GOAL:

Generate sub-hypotheses using ClearThought MCP scientific method, with dynamic count based on Phase 2A causal chain length. Apply scope reduction from Established Facts and transfer validation if applicable.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on MCP scientificmethod calls and initial hypothesis generation
- 🚫 FORBIDDEN to skip MCP scientific method call
- 💬 Approach: Generate hypotheses based on Phase 2A structure
- 📋 Dynamic hypothesis count based on causal chain length

## EXECUTION PROTOCOLS:

- 🎯 Call mcp__clearThought__scientificmethod (1-3x incremental, 3-5x comprehensive)
- 💾 Apply scope reduction from Phase 2A Established Facts
- 📖 Include transfer validation if required
- 🚫 FORBIDDEN to assume fixed 3-step causal chain

## CONTEXT BOUNDARIES:

- Available context: Phase 2A extracted data, verified hypothesis
- Focus: MCP-based hypothesis generation
- Limits: No inventory table yet, only generation
- Dependencies: Step 2 must be completed with confirmed hypothesis

---

## Important Notes

<critical>
**MANDATORY MCP TOOL:**
This step REQUIRES calling `mcp__clearThought__scientificmethod`

**Mode-Dependent Approach:**
- **Incremental Mode**: 1-3 MCP calls (scales with complexity)
  - Phase 2A pre-mapped sources: Use SH1, SH2, SH3, causal steps, predictions
  - **Target: 3-7 hypotheses (DYNAMIC based on Phase 2A structure)**
    - H-E: 1-2 (from SH count)
    - H-M: {{causal_chain_count}} (from causal step count)
    - H-C: 0-2 (OPTIONAL - user choice)
- **Comprehensive Mode**: 3-5 MCP calls (each hypothesis type)
  - Target: 8-13 hypotheses

**Note:** H-CP (Comparison) hypotheses are now handled in Phase 5 Baseline Comparison, not here.
</critical>

<critical>
**SCOPE REDUCTION FROM PHASE 2A (MANDATORY)**

Before generating hypotheses, check Established Facts:

```
IF {{proves_new_claims}} exists:
  - ONLY generate hypotheses for claims marked "PROVE NEW"
  - DO NOT generate hypotheses for claims marked "BUILD ON"
  - Reference BUILD ON claims as pre-validated assumptions

SCOPE REDUCTION = ((Total Claims - PROVE NEW Claims) / Total Claims) × 100%
```
</critical>

<critical>
**TRANSFER VALIDATION INTEGRATION (IF APPLICABLE)**

If {{requires_transfer_validation}} == true:
1. Add Transfer Validation to H-M Hypotheses
2. Use {{transfer_validation_criteria}} as additional success criteria
3. Include source principle and expected fidelity

If {{requires_transfer_validation}} == false:
- Skip Transfer Validation section in H-M hypotheses
</critical>

---

## Actions

### 1. MODE Selection

**Incremental Mode** (if `{{research_scope_mode}} == "incremental"`):
- Use Phase 2A Pre-Mapped Hypothesis Sources
- Mapping from Phase 2A:
  - SH1 ({{sh1_existence}}) → H-E1 (Existence)
  - SH2 ({{sh2_mechanism}}) → H-M (Mechanism core)
  - Causal Steps ({{causal_chain_count}} detected) → H-M1 to H-M{{causal_chain_count}}
  - Variables: {{variables_table}}

**Comprehensive Mode** (if `{{research_scope_mode}} == "comprehensive"`):
- Generate all hypotheses from scratch
- Call MCP for each hypothesis type (3-5 times)

---

### 2. Condition Hypotheses Decision

{{#if condition_requires_verification}}
**Condition hypotheses recommended based on scope analysis.**

Detected conditions: {{condition_candidates}}

Ask user:
```
Would you like to include condition hypotheses?

[1] Yes - include H-C hypotheses
[2] No - document as constraints only
[3] Select specific conditions
```

**WAIT for user input.**

Store:
- `{{include_condition_hypotheses}}` = true/false
- `{{condition_hypothesis_count}}` = 0-2
{{else}}
No condition hypotheses recommended.
Set `{{include_condition_hypotheses}} = false`, `{{condition_hypothesis_count}} = 0`
{{/if}}

---

### 3. MCP Scientific Method Calls (Incremental Mode)

<critical>
**Call mcp__clearThought__scientificmethod 1-3 TIMES**

Phase 2A provides structure. We only need to validate and design tests.
</critical>

#### Call 1: H-E1 Verification (REQUIRED)

```json
{
  "stage": "hypothesis",
  "inquiryId": "H-E1-verification",
  "hypothesis": {
    "statement": "[H-E1 from {{sh1_existence}}]",
    "variables": "[USE {{variables_table}} from Phase 2A]",
    "assumptions": "[USE {{key_assumptions}} from Phase 2A]",
    "confidence": "{{confidence_level}}",
    "status": "proposed"
  }
}
```

Then progress through stages: `"experiment"` → `"analysis"`

#### Call 2: Mechanism Chain Test (DYNAMIC)

**If {{causal_chain_count}} ≤ 3:** Single integrated call
```json
{
  "stage": "hypothesis",
  "inquiryId": "H-M-integrated",
  "hypothesis": {
    "statement": "Mechanism chain: [causal steps joined]",
    "variables": "[USE {{variables_table}}]",
    "assumptions": "[USE {{key_assumptions}}]",
    "predictions": "[USE {{prediction_2}}]"
  }
}
```

**If {{causal_chain_count}} > 3:** Split into two calls
- Call 2a: First half of mechanism chain
- Call 2b: Second half of mechanism chain

#### Call 3: Condition Hypotheses (OPTIONAL)

**Only if {{include_condition_hypotheses}} == true:**
```json
{
  "stage": "hypothesis",
  "inquiryId": "H-C-conditions",
  "hypothesis": {
    "statement": "Mechanism operates under condition: [condition]",
    "variables": "[Extract condition variable]",
    "predictions": "IF condition met THEN mechanism works ELSE fails"
  }
}
```

---

### 4. MCP Scientific Method Calls (Comprehensive Mode)

Call `mcp__clearThought__scientificmethod` for **each hypothesis type** (3-5 times):
- Existence hypotheses (1-2 calls)
- Mechanism hypotheses (1-2 calls)
- Condition hypotheses (optional, 1 call)

---

### 5. Display Generation Summary

Present to user:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MCP HYPOTHESIS GENERATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MCP Calls Made: {{mcp_call_count}}
Scope Reduction: {{scope_reduction_percentage}}%
Transfer Validation: {{requires_transfer_validation}}

Hypotheses Generated:
- H-E: 1 (Existence)
- H-M: {{causal_chain_count}} (Mechanism)
- H-C: {{condition_hypothesis_count}} (Condition)

Total: {{total_hypothesis_count}} hypotheses

Ready to create specifications and inventory.
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

ONLY WHEN [C continue option] is selected and [MCP calls completed], will you then load and read fully `{nextStepFile}` to create hypothesis specifications and inventory.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- MCP scientific method called (1-3x incremental, 3-5x comprehensive)
- Scope reduction applied from Phase 2A Established Facts
- Causal chain length correctly detected
- User asked about condition hypotheses (if recommended)
- Transfer validation included (if required)
- Generation summary displayed
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping MCP scientific method call
- Assuming fixed 3-step causal chain without checking Phase 2A
- Skipping user question about condition hypotheses (when recommended)
- Ignoring scope reduction from Established Facts
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
