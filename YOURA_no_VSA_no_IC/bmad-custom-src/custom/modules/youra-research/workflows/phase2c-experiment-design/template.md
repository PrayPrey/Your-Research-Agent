# Experiment Design: {{UNFILLED:hypothesis_id}}

**Date:** {{date}}
**Author:** {{user_name}}
**Hypothesis Statement:** {{UNFILLED:hypothesis_statement}}
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** {{UNFILLED:workflow_status}}
**Prerequisites Satisfied:** {{UNFILLED:prerequisites_satisfied}}
**Gate Status:** {{UNFILLED:gate_status}}

---

## Hypothesis Context

### Current Hypothesis
- **ID:** {{UNFILLED:hypothesis_id}}
- **Type:** {{UNFILLED:hypothesis_type}}
- **Prerequisites:** {{UNFILLED:prerequisites_list}}

### Gate Condition
{{UNFILLED:gate_condition}}

---

## Continuation Context

{{UNFILLED:continuation_context}}

### Previous Hypothesis Results (if applicable)
{{UNFILLED:previous_hypothesis_results}}

---

## Implementation Research Summary

### Archon Knowledge Base Findings

{{UNFILLED:archon_knowledge_findings}}

### Archon Code Examples

{{UNFILLED:archon_code_findings}}

### Exa GitHub Implementations

{{UNFILLED:exa_github_findings}}

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

{{UNFILLED:implementation_priority}}

**Recommended Implementation Path:**
- Primary: {{UNFILLED:primary_implementation}}
- Fallback: {{UNFILLED:fallback_implementation}}
- Justification: {{UNFILLED:implementation_justification}}

### Code Analysis (Serena MCP)

{{UNFILLED:serena_code_analysis}}

---

## Experiment Specification

### Dataset

{{UNFILLED:dataset_specification}}

**Loading Information** (for Phase 4 download):
- Method: {{UNFILLED:dataset_loading_method}}
- Identifier: {{UNFILLED:dataset_loading_identifier}}
- Code: {{UNFILLED:dataset_loading_code}}

### Models

#### Baseline Model

{{UNFILLED:baseline_model}}

**Loading Information** (for Phase 4 download):
- Method: {{UNFILLED:model_loading_method}}
- Identifier: {{UNFILLED:model_loading_identifier}}
- Code: {{UNFILLED:model_loading_code}}

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

{{UNFILLED:core_mechanism_pseudocode}}

### Training Protocol

{{UNFILLED:training_protocol}}

### Evaluation

{{UNFILLED:evaluation_metrics}}

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: {{UNFILLED:task_type}}
- Library: {{UNFILLED:metrics_library}}
- Code: {{UNFILLED:metrics_loading_code}}

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

{{UNFILLED:recommended_visualizations}}

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

{{UNFILLED:reference_implementations}}

---

## State Information

**State File:** verification_state.yaml
**Date:** {{timestamp}}

### Workflow History for This Hypothesis
{{UNFILLED:hypothesis_history}}

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
