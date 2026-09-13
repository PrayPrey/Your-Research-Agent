---
name: 'step-04-hypothesis-inventory'
description: 'Create hypothesis specifications and inventory table'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-04-hypothesis-inventory.md'
nextStepFile: '{workflow_path}/steps/step-05-risk-analysis.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 4: Hypothesis Specifications & Inventory

## STEP GOAL:

Create detailed specifications for each generated hypothesis and compile the hypothesis inventory table. Each specification follows the streamlined format (40-50 lines) with verification protocols.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on hypothesis specifications and inventory table
- 🚫 FORBIDDEN to generate verbose specifications (>50 lines each)
- 💬 Approach: Streamlined format with essential information only
- 📋 Each hypothesis must include verification protocol

## EXECUTION PROTOCOLS:

- 🎯 Write specifications for each hypothesis type
- 💾 Create hypothesis inventory table
- 📖 Fill template placeholders
- 🚫 FORBIDDEN to skip verification protocols

## CONTEXT BOUNDARIES:

- Available context: MCP-generated hypotheses from Step 3
- Focus: Specification writing and inventory compilation
- Limits: No risk analysis yet, only hypothesis documentation
- Dependencies: Step 3 must be completed with MCP generation

---

## Actions

### 1. Hypothesis Categories Reference

**Incremental Mode - Target: 3-7 hypotheses (DYNAMIC)**

| Type | Count | Source |
|------|-------|--------|
| **H-E (Existence)** | 1 | SH1 from Phase 2A |
| **H-M (Mechanism)** | {{causal_chain_count}} | Causal steps from Phase 2A |
| **H-C (Condition)** | {{condition_hypothesis_count}} | User choice in Step 3 |

**Note:** H-CP (Comparison) hypotheses moved to Phase 5.

**Dynamic Total:**
```
Total = 1 (H-E1) + {{causal_chain_count}} (H-M) + {{condition_hypothesis_count}} (H-C)
Range: 3-7 hypotheses
```

---

### 2. Write Specifications (Streamlined Format)

**Format for EACH Hypothesis (40-50 lines max):**

```markdown
---
**H-[type][num]: [Descriptive Title]**

**Statement**: Under [condition], if [X], then [Y] because [mechanism].

**Rationale** (2-3 sentences):
[WHY is this hypothesis important? What does it validate?]

**Variables** (from Phase 2A {{variables_table}}):
- Independent: [X]
- Dependent: [Y]
- Controlled: [Z1, Z2]

**Verification Protocol** (3-5 steps, 1 sentence each):
1. [Step 1 - concise action]
2. [Step 2 - concise action]
3. [Step 3 - concise action]

**Success Criteria** (PoC: Direction-based):
- Primary: [e.g., "proposed > baseline" or "Accuracy improves"]
- Secondary: [Optional - e.g., "Loss decreases" or "Mechanism activates"]

**Failure Response**:
- IF fails: [PIVOT | EXPLORE | ABANDON]

**Dependencies**: [Prerequisites]

**Source**: Phase 2A [Section reference]
---
```

**Quality Standards:**
- **Target: 40-50 lines per hypothesis**
- **Rationale: 2-3 sentences only**
- **Verification Protocol: 1 sentence per step**
- **NO "Connects to Risks" cross-references**
- **NO detailed effort breakdowns**

---

### 3. Generate Hypothesis Specifications

#### H-E1 (Existence Hypothesis)

Generate specification for H-E1:
- Source: `{{sh1_existence}}` from Phase 2A
- Verification: `{{prediction_1_primary}}`
- Dependencies: None (foundation)

#### H-M1 through H-M{N} (Mechanism Hypotheses)

Generate specifications for each mechanism step:

```
{{#each causal_steps}}
**H-M{{@index+1}}**: {{this.description}}
- Evidence: {{this.evidence}}
- Falsifier: {{this.potential_falsifier}}
- Dependencies: {{#if @first}}H-E1{{else}}H-M{{@index}}{{/if}}
{{/each}}
```

**Transfer Validation (if applicable):**
{{#if requires_transfer_validation}}
Include in each H-M specification:
- Transfer Test: {{transfer_validation_criteria}}
- Source Principle: {{transfer_core_principle}}
- Expected Fidelity: {{transfer_fidelity_score}}
{{/if}}

#### H-C1 through H-C{M} (Condition Hypotheses - OPTIONAL)

{{#if include_condition_hypotheses}}
Generate specifications for each condition:
```
{{#each selected_conditions}}
**H-C{{@index+1}}**: Boundary condition - {{this}}
- Verification: Test mechanism at boundary
- Dependencies: H-M{{causal_chain_count}}
{{/each}}
```
{{else}}
(Condition hypotheses skipped - boundaries documented as constraints)
{{/if}}

---

### 4. Generate Hypothesis Inventory Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY ({{total_hypothesis_count}} hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Type | Statement (Brief) | Prerequisites | Source |
|----|------|-------------------|---------------|--------|
| H-E1 | Existence | [Brief] | None | SH1 |
{{#each causal_steps}}
| H-M{{@index+1}} | Mechanism | [Brief] | {{deps}} | Causal Step {{@index+1}} |
{{/each}}
{{#if include_condition_hypotheses}}
{{#each selected_conditions}}
| H-C{{@index+1}} | Condition | [Brief] | H-M{{../causal_chain_count}} | Scope |
{{/each}}
{{/if}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Outputs to Template

Fill these placeholders in {outputFile}:
- `{{UNFILLED:hypothesis_inventory}}`
- `{{UNFILLED:existence_hypotheses}}`
- `{{UNFILLED:mechanism_hypotheses}}`
- `{{UNFILLED:condition_hypotheses}}`

**Target Output:**
- {{total_hypothesis_count}} hypotheses × 40-50 lines = ~200-350 lines total

**Write the file back** after filling placeholders.

---

### 5. Display Inventory Summary

Present to user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HYPOTHESIS INVENTORY COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated: {{total_hypothesis_count}} hypotheses

| Type | Count | IDs |
|------|-------|-----|
| Existence | 1 | H-E1 |
| Mechanism | {{causal_chain_count}} | H-M1 to H-M{{causal_chain_count}} |
{{#if include_condition_hypotheses}}
| Condition | {{condition_hypothesis_count}} | H-C1 to H-C{{condition_hypothesis_count}} |
{{/if}}

Each specification: 40-50 lines with verification protocol
Total output: ~{{total_lines}} lines

Ready to proceed to Risk Analysis.
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

ONLY WHEN [C continue option] is selected and [inventory complete], will you then load and read fully `{nextStepFile}` to begin Risk Analysis.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Specifications written for all hypotheses
- Each specification: 40-50 lines (streamlined format)
- Rationale: 2-3 sentences (concise)
- Verification protocol included for each
- Hypothesis inventory table generated
- Placeholders filled in output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Specifications exceeding 50 lines each
- Rationale too verbose (>3 sentences)
- Missing verification protocols
- Including "Connects to Risks" cross-references
- Including detailed effort breakdowns
- Total output exceeding 500 lines
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
