---
name: 'step-06-synthesis'
description: 'Synthesize complete Level 1.5 experiment specification'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-06-synthesis.md'
nextStepFile: '{workflow_path}/steps/step-07-references.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Template References
mechanismVerificationTemplate: '{workflow_path}/templates/mechanism_verification_protocol.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 6: Experiment Design Synthesis

## STEP GOAL:

Synthesize complete Level 1.5 experiment specification by combining all research findings into model architecture, core mechanism pseudo-code (10-30 lines), training protocol, evaluation metrics, and ablation study design. This is the CORE step producing the main experiment design.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus on synthesizing all research into complete specification
- 🚫 FORBIDDEN to generate specs without research backing
- 💬 Approach: Combine findings systematically, cite all sources
- 📋 Pseudo-code must be 10-30 lines, based on analyzed code

### 🧪 EXISTENCE (PoC) Hypothesis Rules (CRITICAL!)

> **PoC Goal**: Demonstrate "this mechanism has an effect" - NOT paper-level rigor.
> PoC validates "worth researching further", not "ready for publication".

**For EXISTENCE hypotheses, OMIT the following entirely (do NOT generate):**
- ❌ Statistical Test section
- ❌ Ablation Study section (beyond baseline vs proposed)
- ❌ Multiple seed specifications (just use 1 seed)
- ❌ Hyperparameter search/grid
- ❌ Detailed success thresholds

**EXISTENCE experiment spec contains ONLY:**
- ✅ Single baseline model
- ✅ Single proposed model (baseline + mechanism)
- ✅ Fixed hyperparameters (defaults from research)
- ✅ 1 seed
- ✅ Success = "proposed > baseline" (direction only)

**EXISTENCE Success = "Mechanism activates AND shows positive effect direction"**

## EXECUTION PROTOCOLS:

- 🎯 All specs must trace back to research findings
- 💾 Generate pseudo-code based on Serena/Exa analysis
- 📖 Reuse hyperparameters from previous hypothesis if continuation
- 🚫 Never include unsupported assumptions

## CONTEXT BOUNDARIES:

- Available context: All findings from Steps 2-5, previous context
- Focus: Complete experiment specification synthesis
- Limits: Do not generate full implementation code
- Dependencies: Dataset, baseline, code analysis from previous steps

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Display Step Start

Display: "🔬 Step 6: Synthesizing complete experiment specification..."

### 2. Model Architecture Specification

**Baseline Model** (from Step 5):

```markdown
### Model Architecture

#### Baseline Model
**Architecture**: [Name from Step 5]
**Configuration**: [Details from Step 5]
**Source**: [Reference]
```

**Proposed Model**:

```markdown
#### Proposed Model
**Architecture**: [Baseline] + [Mechanism from hypothesis]
**Integration Point**: [From Serena analysis or research]
  - Insert after: [Layer name]
  - Before: [Layer name]
**Modification**: [How baseline is modified]
```

Store as part of: `{experiment_specification}`

### 3. Core Mechanism Pseudo-code (10-30 Lines)

**IF Serena analysis performed (Step 4):**
→ Use `{analyzed_pseudocode}` as base, refine for hypothesis

**ELSE:**
→ Abstract code snippets from Archon/Exa into pseudo-code

**Requirements:**
- 10-30 lines (not full implementation)
- Show key operations
- Include input/output dimensions
- Document parameters
- Based on analyzed real code

```python
# Core Mechanism: {mechanism_name}
# Based on: [Source from research]

class MechanismName(nn.Module):
    """
    [Purpose - from hypothesis]
    """
    def __init__(self, channels, num_classes, [params]):
        super().__init__()
        # Key components (from analysis)
        self.component1 = ...
        self.component2 = ...

    def forward(self, x, [additional_inputs]):
        """
        Args:
            x: (B, C, H, W) - feature map
        Returns:
            (B, C, H, W) - enhanced features
        """
        # Step 1: [operation from analysis]
        # Step 2: [operation from analysis]
        # Step 3: [operation from analysis]
        return output

# Integration: Insert after [layer], before [layer]
```

Store as: `{core_mechanism_pseudocode}`

### 4. Training Protocol

**IF {previous_context} exists:**
→ Reuse optimal hyperparameters from previous validation

```markdown
### Training Protocol

**From Previous Hypothesis ({previous_hypothesis_id})**:
- **Optimizer**: [From previous] - Parameters: [details]
- **Learning Rate**: [Optimal value from previous]
- **Schedule**: [From previous]
- **Batch Size**: [Optimal from previous]
- **Epochs**: [From previous]
- **Loss**: [From previous]

**Rationale**: Optimal in {previous_hypothesis_id}, reusing for controlled experiment.
```

**ELSE:**
→ Use researched hyperparameters

```markdown
### Training Protocol

**Optimizer**: [Most common from research]
  - Parameters: [e.g., momentum=0.9, weight_decay=2e-4]
  - **Source**: [Cite Archon/Exa findings]

**Learning Rate**: [Value from research]
  - **Source**: [Cite source]

**Schedule**: [Type from research]
  - Parameters: [e.g., milestones=[100,150], gamma=0.1]
  - **Source**: [Cite source]

**Batch Size**: [Value from research]
  - **Source**: [Cite source]

**Epochs**: [Value from research]
  - **Source**: [Cite source]

**Loss Function**: [From research or hypothesis]
  - **Source**: [Cite source]

**Seeds**: 1 (fixed)

> ⚠️ **EXISTENCE (PoC)**: Do NOT specify multiple seeds. Single run is sufficient.
```

Store as: `{training_protocol}`

### 5. Evaluation Metrics

From Phase 2B success criteria + research findings:

**⚠️ EXISTENCE (PoC): SKIP "Statistical Test" section entirely. Only include Primary Metrics and simple success check.**

```markdown
### Evaluation Metrics

**Primary Metrics**:
- [Metric 1 from Phase 2B]: [Definition]

**Success Criteria**:
- proposed_metric > baseline_metric (effect direction only)

**Expected Baseline Performance** (from research):
- [Metric]: [Value range from researched papers]
- **Source**: [Cite research]
```

Store as: `{evaluation_metrics}`

### 6. Ablation Study Design

**⚠️ EXISTENCE (PoC): SKIP this entire section. PoC only needs baseline vs proposed comparison (already in Model Architecture).**

> For MECHANISM/COMPARISON hypotheses only (handled in Phase 5)

### 7. Visualization Requirements

```markdown
### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)
Based on hypothesis type, model architecture, and evaluation metrics, generate appropriate visualizations that best communicate the experimental results. The LLM should autonomously decide what additional figures would be most informative.

**Output Location**: `{hypothesis_folder}/figures/`
```

Store as: `{recommended_visualizations}`

### 7.5 🔬 Mechanism Verification Protocol (CRITICAL)

> **Purpose:** Define HOW Phase 4 should verify that the mechanism actually works, not just that code runs.

**Load template:** Read `{mechanismVerificationTemplate}` for full protocol structure.

**Quick Reference - Required Elements:**

| Element | Purpose |
|---------|---------|
| Pre-conditions | Verify architecture supports mechanism |
| Activation Indicators | Log messages, tensor shapes, metric deltas |
| Failure Detection | Methods to catch mechanism not working |
| Success Criteria | Thresholds for mechanism-level success |

**Fill these placeholders using template guidance:**
- `mechanism_exists`, `mechanism_isolatable`, `baseline_measurable`
- `architecture_compatibility`
- `mechanism_log_message`, `tensor_shape_change`, `metric_delta_expected`
- `mechanism_verification_code`
- `hypothesis_support_threshold`, `hypothesis_support_metric`

Store as: `{mechanism_verification_protocol}`

### 8. Update Output File

Fill these placeholders in {outputFile}:
- `experiment_specification`
- `core_mechanism_pseudocode`
- `training_protocol`
- `evaluation_metrics`
- `recommended_visualizations`
- 🔬 `mechanism_exists` (NEW!)
- 🔬 `mechanism_isolatable` (NEW!)
- 🔬 `baseline_measurable` (NEW!)
- 🔬 `architecture_compatibility` (NEW!)
- 🔬 `mechanism_log_message` (NEW!)
- 🔬 `tensor_shape_change` (NEW!)
- 🔬 `metric_delta_expected` (NEW!)
- 🔬 `mechanism_verification_code` (NEW!)
- 🔬 `hypothesis_support_threshold` (NEW!)
- 🔬 `hypothesis_support_metric` (NEW!)

Write the file back after filling placeholders.

Display: "✅ Experiment specification synthesized and saved"

### 9. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Save content to {outputFile}, update frontmatter, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#9-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution completes, redisplay the menu
- User can chat or ask questions - always respond and redisplay menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [all specifications synthesized with sources], will you then load and read fully `{workflow_path}/steps/step-07-references.md` to execute and begin reference documentation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Model architecture specified (baseline + proposed)
- Core mechanism pseudo-code generated (10-30 lines)
- Pseudo-code based on analyzed code, not speculation
- Training protocol documented with sources
- Evaluation metrics defined with success criteria
- Ablation study designed (simplified for EXISTENCE)
- Visualization requirements specified (required + LLM autonomous)
- 🔬 **Mechanism Verification Protocol defined**
  - Pre-conditions specified
  - Activation indicators defined
  - Architecture compatibility checked
  - Failure detection methods documented
- All specs trace to research sources
- Findings saved to output file
- Menu presented and user input handled correctly

#### 🧪 EXISTENCE (PoC) Specific Success:
- Statistical Test section: OMITTED
- Ablation Study section: OMITTED
- Seeds: 1 (not specified as multiple)
- Success = "proposed > baseline"

### ❌ SYSTEM FAILURE:

- Generating pseudo-code without code analysis basis
- Including unsupported hyperparameters
- Pseudo-code > 30 lines (too detailed for Level 1.5)
- Missing source citations
- Proceeding without user input/selection
- Not updating output file
- 🔬 **Missing Mechanism Verification Protocol**
- 🔬 **Not checking architecture compatibility**
- 🔬 **Not defining mechanism activation indicators**

#### 🧪 EXISTENCE (PoC) Specific Failures:
- ❌ Including Statistical Test section for PoC
- ❌ Including Ablation Study section for PoC
- ❌ Specifying multiple seeds for PoC

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
