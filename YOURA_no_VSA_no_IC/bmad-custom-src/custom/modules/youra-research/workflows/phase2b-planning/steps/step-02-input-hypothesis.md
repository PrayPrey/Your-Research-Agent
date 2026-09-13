---
name: 'step-02-input-hypothesis'
description: 'Verify loaded Phase 2A data or collect hypothesis input for verification planning'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-02-input-hypothesis.md'
nextStepFile: '{workflow_path}/steps/step-03-hypothesis-generation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Template References
outputTemplate: '{workflow_path}/template.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 2: Input and Verify Hypothesis

## STEP GOAL:

Verify loaded Phase 2A data (incremental mode) or collect hypothesis input (comprehensive mode). This step ensures the hypothesis is clearly defined before proceeding with verification planning.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on hypothesis verification and input collection
- 🚫 FORBIDDEN to proceed without user confirmation of hypothesis data
- 💬 Approach: Present extracted data clearly, allow user corrections
- 📋 Ensure hypothesis statement is complete and falsifiable

## EXECUTION PROTOCOLS:

- 🎯 Show all extracted Phase 2A information for user verification
- 💾 Allow user to edit or correct any extracted data
- 📖 Collect hypothesis input if comprehensive mode
- 🚫 FORBIDDEN to proceed without explicit user confirmation

## CONTEXT BOUNDARIES:

- Available context: Phase 2A extracted data (if incremental), user input (if comprehensive)
- Focus: Hypothesis data verification and confirmation
- Limits: No risk analysis yet, only hypothesis confirmation
- Dependencies: Step 1 must be completed, research mode must be set

---

## Actions

### MODE: Incremental (Phase 2A Dialogue Available)

If `{{research_scope_mode}} == "incremental"`:

#### 1. Verify Extracted Phase 2A Information

Present to the user what was extracted in Step 1:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EXTRACTED PHASE 2A EXTENDED INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Hypothesis:**
- ID: {{hypothesis_id}}
- Confidence: {{confidence_level}}
- Statement: {{core_hypothesis_statement}}

**Alternative Hypothesis (H0):**
{{alternative_hypothesis_h0}}

**Experimental Setup (from Phase 2A Section 2):**
- Dataset: {{selected_dataset_name}} ({{selected_dataset_type}})
  - Source: {{selected_dataset_source}}
  - Fit: {{dataset_hypothesis_fit}}
- Model: {{selected_model_name}} ({{selected_model_type}})
  - Fit: {{model_hypothesis_fit}}

**Causal Mechanism ({{causal_chain_count}} Steps):**
{{#each causal_steps}}
{{@index+1}}. {{this.description}}
{{/each}}

**Key Assumptions (A1-A5):**
[Show {{key_assumptions}} table]

**Testable Predictions:**
1. PRIMARY: {{prediction_1_primary}}
2. {{prediction_2}}
3. {{prediction_3}}

**Recommended Sub-Hypotheses:**
- SH1 (Existence): {{sh1_existence}}
- SH2 (Mechanism): {{sh2_mechanism}}
- SH3 (Comparison): {{sh3_comparison}} (-> Phase 5)

**Scope:**
- Applies: {{scope_applies}}
- Does NOT apply: {{scope_not_applies}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 2. Ask for User Confirmation

Present confirmation options:
```
Is this information correct?

[Y] Yes, proceed with this data (Incremental Mode)
[E] Need corrections - let me edit
[S] Switch to Comprehensive Mode (ignore Phase 2A)
```

**WAIT for user input.**

- If [Y]: Continue with incremental mode
- If [E]: Allow user to edit specific fields, then continue
- If [S]: Switch to comprehensive mode (see below)

---

### MODE: Comprehensive (No Phase 2A / User Chose Switch)

If `{{research_scope_mode}} == "comprehensive"`:

#### 1. Hypothesis Input Method

Ask user:
```
How would you like to provide the hypothesis?

[1] Load from document (provide file path)
[2] Direct input (paste hypothesis text)
[3] Check recent hypothesis files in output folder
```

**WAIT for user input.**

Based on selection:
- **[1]**: Ask for file path, load and parse
- **[2]**: Ask user to paste hypothesis statement
- **[3]**: Search output folder for recent files

#### 2. Collect Hypothesis Title

Ask: "Enter hypothesis title (short descriptive name):"

Store in `{{hypothesis_title}}`

#### 3. Select Extension Depth

```
Select verification plan detail level:

[0] Default (Level 2 - Detailed)
[1] Basic (Level 1 - Essential only)
[2] Detailed (Level 2 - Standard)
[3] Comprehensive (Level 3 - Maximum detail)
```

Store in `{{extension_depth}}`

#### 4. Store Inputs

Store collected information:
- `{{initial_hypothesis}}` - Full hypothesis statement
- `{{original_assumptions}}` - Any assumptions mentioned

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:hypothesis_title}}`
- `{{UNFILLED:extension_depth}}`
- `{{UNFILLED:initial_hypothesis}}`
- `{{UNFILLED:original_assumptions}}`
- `{{UNFILLED:related_work_summary}}`
- `{{UNFILLED:gap_analysis}}`

**Write the file back** after filling placeholders.

---

### Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

Additionally show status:

**Incremental Mode:**
```
✅ Phase 2A data verified!
Proceeding to Sub-Hypothesis Generation with pre-seeded data.
```

**Comprehensive Mode:**
```
✅ Hypothesis input complete!

| Field | Value |
|-------|-------|
| Title | {{hypothesis_title}} |
| Extension Depth | Level {{extension_depth}} |
```

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

ONLY WHEN [C continue option] is selected and [hypothesis data confirmed], will you then load and read fully `{nextStepFile}` to begin sub-hypothesis generation with MCP scientificmethod.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Phase 2A data presented clearly for user verification (incremental)
- Hypothesis input collected completely (comprehensive)
- User confirmed or corrected all extracted data
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Proceeding without user confirmation of hypothesis data
- Missing required hypothesis fields
- Not allowing user to edit extracted data
- Skipping placeholder updates in output file
- Proceeding to next step without explicit user selection

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
