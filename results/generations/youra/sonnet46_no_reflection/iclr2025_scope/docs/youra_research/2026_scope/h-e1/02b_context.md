# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan (JIT by Phase 2C step-01)
**Date:** 2026-05-20
**Main Hypothesis:** JointLoRA-KV: Task-Aware Joint Training of LoRA Adapters and KV Eviction Heads
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under LLaMA-3.1-8B fine-tuned with LoRA (r=16) on MNLI, the Spearman rank correlation between LoRA-modified attention weights and Locret retaining head scores (trained on LM loss) is systematically below 0.7 for task-discriminative tokens across 100 MNLI validation examples, indicating that task-adapted attention patterns are misaligned with LM-loss-trained eviction heuristics.

### Type
EXISTENCE

### Rationale
This is the existence precondition for the entire hypothesis chain. If misalignment is absent (ρ ≥ 0.7), existing eviction heuristics already align with task-relevant tokens and joint training provides no additional signal. This experiment tests cheaply using existing fine-tuned models with no new training required.

---

## Verification Protocol

### Conceptual Test
1. Load existing LoRA-fine-tuned LLaMA-3.1-8B on MNLI from HuggingFace Model Hub.
2. Load Locret retaining heads (LM-distillation-trained) for same base model.
3. Extract per-token attention weights and retaining scores on 100 MNLI validation examples.
4. Compute Spearman ρ per example; report mean ± std; flag misaligned token types.
5. If borderline (0.65–0.75), extend to 500 examples and check SST-2, QNLI.

### Success Criteria
- Primary: Mean Spearman ρ < 0.7 across 100 MNLI validation examples
- Secondary: Misaligned tokens concentrated at hypothesis/contrast positions (qualitative)

### Variables (if applicable)
- **Independent Variable:** LoRA attention weights vs. Locret retaining head scores (both from existing models)
- **Dependent Variable:** Spearman ρ (mean across 100 MNLI examples, all attention heads)
- **Controlled Variables:** LLaMA-3.1-8B checkpoint, LoRA r=16, seed=42, 100 fixed validation examples

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** GLUE MNLI validation set (100 examples)
- **Type:** standard
- **Source:** HuggingFace datasets (`glue`, `mnli`)
- **Path:** auto (HuggingFace download)
- **Hypothesis Fit:** MNLI provides sentence-pair classification with well-defined hypothesis/premise tokens that are discriminatively relevant for NLI. Standard benchmark with clear task-discriminative token positions.

### Selected Model
- **Name:** LLaMA-3.1-8B + LoRA fine-tuned on MNLI (existing HuggingFace checkpoint)
- **Type:** Decoder-only transformer LLM with LoRA PEFT adapter
- **Source:** meta-llama/Meta-Llama-3.1-8B on HuggingFace Model Hub + existing LoRA MNLI checkpoint
- **Hypothesis Fit:** Most widely benchmarked open-weight model for PEFT research; Locret tested on LLaMA family; LoRA injection via HuggingFace PEFT fully supported.

---

## Baseline & Comparison Targets

### Baseline Methods
This is an EXISTENCE hypothesis — no training baseline required. The comparison is between:
- LoRA-modified attention weights (task-adapted)
- Locret retaining head scores (LM-distillation-trained)

The test is diagnostic: does the correlation ρ < 0.7?

### Baseline Performance
N/A — this is a correlation measurement, not a classification accuracy test.

### Gap Analysis
If ρ < 0.7: misalignment confirmed → joint training hypothesis chain proceeds.
If ρ ≥ 0.7: revisit assumption A1; test gradient attribution before abandoning.

---

## Dependencies and Gate Conditions

### Prerequisites
None — H-E1 is the first hypothesis, no prerequisites.

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** PIVOT — re-examine A1; test whether task-loss gradient still differs from LM-loss gradient in a gradient attribution experiment before abandoning H-M1/H-M2.

**Phase Assignment:** Phase 2C → Phase 3 → Phase 4

**Estimated Duration:** 1-2 hours (no training required, inference only)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the root existence precondition. H-M1 and H-M2 both depend on H-E1. H-M3 depends on H-M1 and H-M2. H-M4 depends on H-M3. If H-E1 fails, the entire hypothesis chain is blocked.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-e1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
