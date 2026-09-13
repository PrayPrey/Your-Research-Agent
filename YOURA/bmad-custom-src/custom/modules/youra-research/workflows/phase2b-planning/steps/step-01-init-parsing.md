---
name: 'step-01-init-parsing'
description: 'Parse Phase 2A Dialogue output and extract all hypothesis variables'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2b-planning'

# File References
thisStepFile: '{workflow_path}/steps/step-01-init-parsing.md'
nextStepFile: '{workflow_path}/steps/step-02-input-hypothesis.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/02b_verification_plan.md'

# Template References
outputTemplate: '{workflow_path}/template.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/workflows/advanced-elicitation/workflow.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'

# Input References
phase2aOutput: '{research_output_path}/03_refinement.yaml'
phase2aSynthesis: '{research_output_path}/02_synthesis.yaml'
phase2aRoundTable: '{research_output_path}/01_round_table/final_opinions.yaml'
---

# Step 1: Parse Phase 2A Dialogue Data

## STEP GOAL:

Parse the Phase 2A Dialogue output files (03_refinement.yaml, 02_synthesis.yaml) and extract all hypothesis variables needed for verification planning. This step transforms Phase 2A Dialogue data into structured variables for subsequent steps.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Phase 2A parsing and variable extraction
- 🚫 FORBIDDEN to proceed without complete parsing if Phase 2A exists
- 💬 Approach: Systematic section-by-section extraction
- 📋 All extracted variables must be stored for later steps

## EXECUTION PROTOCOLS:

- 🎯 Locate and read Phase 2A Dialogue output file
- 💾 Parse each section systematically
- 📖 Extract all variables with proper naming
- 🚫 FORBIDDEN to skip any section if present

## CONTEXT BOUNDARIES:

- Available context: Phase 2A Dialogue output files (03_refinement.yaml, 02_synthesis.yaml)
- Focus: Data extraction and variable storage
- Limits: No hypothesis generation yet, only parsing
- Dependencies: Phase 2A Dialogue files must exist and be readable

---

## Actions

### 1. Discover and Read Phase 2A Output

Execute the `discover_inputs` protocol to find:
- {phase2a_output} - Phase 2A Dialogue output file
- {default_output_file} - Where to write Phase 2B output

**IF {phase2a_output} NOT FOUND:**
- Set `{{research_scope_mode}} = "comprehensive"`
- Warn user: "Phase 2A Dialogue not found. Running in comprehensive mode."
- Skip to Section 6 (Set Research Mode)

**IF {phase2a_output} EXISTS:**
- Proceed with structured parsing below

---

### 2. Phase 2A Dialogue Structured Parsing

<critical>
**IF {phase2a_output} EXISTS:**

Parse EACH section systematically and extract all variables.

**PRIMARY input:** `03_refinement.yaml`
— Contains ALL sections (0, 0.5, 1.1-1.6, 2, 4, 5) with structured YAML keys.

**SUPPLEMENTARY inputs** (loaded but not systematically parsed):
- `02_synthesis.yaml` — Measurement plan, validation strategy, discussion synthesis.
  Used as reference context during later steps (e.g., Step 5 Risk Analysis, Step 8 Dialectical Analysis).
  No variable extraction needed — all required variables are in `03_refinement.yaml`.
- `01_round_table/final_opinions.yaml` — Per-agent perspective assessments.
  Used as qualitative reference, not parsed into variables.
</critical>

#### Section 0: Established Facts & Claim Scope (CRITICAL)

<critical>
**THIS SECTION DETERMINES WHAT TO SKIP IN PHASE 2B-4**

Established Facts should NOT be re-verified. Only "PROVE_NEW" claims need hypothesis generation.
</critical>

**YAML Path:** `established_facts`

```python
ef = refinement_yaml["established_facts"]
all_claims = ef.get("claims", [])

{{established_facts_registry}} = [c for c in all_claims if c["status"] == "BUILD_ON"]
{{builds_on_claims}} = {{established_facts_registry}} # Same: DO NOT re-verify
{{proves_new_claims}} = [c for c in all_claims if c["status"] == "PROVE_NEW"]
{{phase2b_4_instructions}} = ef.get("phase2b_4_instructions", "")
{{scope_reduction_percentage}} = ef.get("scope_reduction_percentage", 0)
```

**SCOPE REDUCTION CHECK:**
```
Count PROVE_NEW claims vs Total claims
If PROVE_NEW < Total → Scope successfully reduced
Store: {{scope_reduction_percentage}} = (Total - PROVE_NEW) / Total * 100
```

#### Section 0.5: Cross-Domain Transfer Summary (OPTIONAL)

<conditional>
**OPTIONAL SECTION** - Only if hypothesis involves cross-domain mechanism transfer.

**YAML Path:** `cross_domain_transfer` (may not exist)

```python
IF "cross_domain_transfer" IN refinement_yaml:
    cdt = refinement_yaml["cross_domain_transfer"]
    {{transfer_source_field}} = cdt["source_field"]
    {{transfer_core_principle}} = cdt["core_principle"]
    {{transfer_dl_translation}} = cdt["dl_translation"]
    {{transfer_preserved}} = cdt["preserved"]
    {{transfer_approximated}} = cdt["approximated"]
    {{transfer_lost}} = cdt["lost"]
    {{transfer_fidelity_score}} = cdt["fidelity_score"]
    {{transfer_validation_criteria}} = cdt.get("validation_criteria", [])
```
</conditional>

**TRANSFER VALIDATION FLAG:**
```
If "cross_domain_transfer" exists AND transfer_validation_criteria non-empty:
  Set {{requires_transfer_validation}} = true
Else:
  Set {{requires_transfer_validation}} = false
```

#### Section 1.1: Core Statement

**YAML Path:** `core_statement`

Extract:
- `{{hypothesis_id}}` ← `core_statement.hypothesis_id` (e.g., "H-ProbVerif-Calibration-v1")
- `{{confidence_level}}` ← `core_statement.confidence_level` (e.g., 0.75)
- `{{core_hypothesis_statement}}` ← `core_statement.core_hypothesis_statement` (Under-If-Then-Because)
- `{{alternative_hypothesis_h0}}` ← `core_statement.alternative_hypothesis_h0`

#### Section 1.2: Variables Table

**YAML Path:** `variables`

Extract:
- `{{variables_table}}` ← `variables` (full structure with independent, dependent, controlled)
- `{{independent_var}}` ← `variables.independent[0]` (name + operationalization)
- `{{dependent_var}}` ← `variables.dependent` where `primary: true` (name + operationalization)
- `{{controlled_vars}}` ← `variables.controlled` (list of {name, operationalization})

#### Section 1.3: Causal Mechanism (DYNAMIC DETECTION)

**YAML Path:** `causal_mechanism`

**DYNAMIC DETECTION:**
```python
cm = refinement_yaml["causal_mechanism"]
{{causal_chain_count}} = cm["causal_chain_count"]
{{causal_steps}} = cm["steps"] # [{step, description, evidence, falsifier}, ...]
{{key_tension}} = cm.get("key_tension", "")
{{evidence_for_links}} = cm.get("evidence_summary", "")
```

Extract:
- `{{causal_chain_count}}` ← `causal_mechanism.causal_chain_count` (typically 2-5)
- `{{causal_steps}}` ← `causal_mechanism.steps` (array with description, evidence, falsifier per step)
- `{{evidence_for_links}}` ← `causal_mechanism.evidence_summary`
- `{{key_tension}}` ← `causal_mechanism.key_tension`

**Note:** Steps become H-M1, H-M2, ... H-M{N} in Step 3.

#### Section 1.4: Key Assumptions (CRITICAL)

**YAML Path:** `key_assumptions`

Extract for Risk Analysis:
- `{{key_assumptions}}` ← `key_assumptions` — array of A1-A5 with:
  - `assumption` → Assumption statement
  - `supporting_evidence` → Supporting evidence
  - `consequence_if_violated` → **Consequence if Violated** → Risk identification input

**Note:** Each assumption violation = potential risk in Step 5.

#### Section 1.5: Scope & Boundaries (CONDITION DETECTION)

**YAML Path:** `scope`

Extract:
- `{{scope_applies}}` ← `scope.applies_to`
- `{{scope_not_applies}}` ← `scope.does_not_apply_to`
- `{{known_limitations}}` ← `scope.known_limitations`

**CONDITION HYPOTHESIS DETECTION:**
```
{{condition_requires_verification}} = false
{{condition_candidates}} = []

For each scope boundary in scope.does_not_apply_to:
  IF boundary is quantitative/testable/critical:
    Set {{condition_requires_verification}} = true
    Add to {{condition_candidates}}
```

#### Section 1.6: Testable Predictions (CRITICAL)

**YAML Path:** `predictions`

Extract:
- `{{prediction_1_primary}}` ← `predictions` where `primary: true` → PRIMARY prediction → basis for H-E1
- `{{prediction_2}}` ← second prediction entry
- `{{prediction_3}}` ← third prediction entry
- `{{falsification_criteria}}` ← `predictions[*].falsification` (collected from all predictions)

#### Section 2: Experimental Setup Selection

**YAML Path:** `experimental_setup`

Extract:
- `{{selected_dataset_name}}` ← `experimental_setup.dataset.name`
- `{{selected_dataset_type}}` ← `experimental_setup.dataset.type` (standard | custom | synthetic)
- `{{selected_dataset_source}}` ← `experimental_setup.dataset.source`
- `{{selected_dataset_path}}` ← `experimental_setup.dataset.path`
- `{{dataset_hypothesis_fit}}` ← `experimental_setup.dataset.hypothesis_fit`
- `{{selected_model_name}}` ← `experimental_setup.model.name`
- `{{selected_model_type}}` ← `experimental_setup.model.type`
- `{{selected_model_source}}` ← `experimental_setup.model.source`
- `{{model_hypothesis_fit}}` ← `experimental_setup.model.hypothesis_fit`

#### Section 4: Key Related Work

**YAML Path:** `related_work`

Extract:
- `{{related_work_table}}` ← `related_work.baselines` (array of {method, performance, dataset, why_insufficient})
- `{{baseline_best_performance}}` ← `related_work.best_baseline_performance`
- `{{baseline_methods}}` ← `[b["method"] for b in related_work.baselines]`
- `{{why_baselines_insufficient}}` ← `[b["why_insufficient"] for b in related_work.baselines]`

#### Section 5: Phase 2B Readiness

**YAML Path:** `phase2b_readiness`

Extract:
- `{{sh1_existence}}` ← `phase2b_readiness.sh1_existence`
- `{{sh2_mechanism}}` ← `phase2b_readiness.sh2_mechanism`
- `{{sh3_comparison}}` ← `phase2b_readiness.sh3_comparison` (→ Phase 5)
- `{{open_questions}}` ← `phase2b_readiness.open_questions`

---

### 3. Set Research Mode

**IF Phase 2A Dialogue loaded successfully:**
- Set `{{research_scope_mode}} = "incremental"`
- Store extracted variables for subsequent steps

**IF Phase 2A Dialogue NOT found:**
- Set `{{research_scope_mode}} = "comprehensive"`

---

### 4. Display Parsing Summary

Present to user:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 2A PARSING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research Mode: {{research_scope_mode}}
Hypothesis ID: {{hypothesis_id}}
Confidence: {{confidence_level}}

Causal Chain: {{causal_chain_count}} steps detected
Scope Reduction: {{scope_reduction_percentage}}%
Transfer Validation: {{requires_transfer_validation}}
Condition Hypotheses: {{condition_requires_verification}}

Variables extracted and stored for Steps 2-10.
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

ONLY WHEN [C continue option] is selected and [Phase 2A parsing complete or comprehensive mode set], will you then load and read fully `{nextStepFile}` to present hypothesis for user confirmation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Phase 2A file located (or comprehensive mode set)
- All sections parsed systematically
- Variables extracted with proper naming
- Research mode correctly set
- Parsing summary displayed to user
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping Phase 2A parsing when file exists
- Missing variable extraction for any present section
- Setting wrong research mode
- Not storing variables for later steps
- Proceeding without user confirmation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
