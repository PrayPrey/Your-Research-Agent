# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-19
**Main Hypothesis:** Calibration Inversion as Behavioral Marker for Bidirectional Task Classification
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under standard RLHF training, if we analyze the reward signal, then models optimize for annotator approval (not correctness alone), because annotator ratings conflate multiple dimensions.

### Type
MECHANISM

### Rationale
First causal step establishing that RLHF reward signal carries conflated information. This is foundational to explaining why calibration inversion occurs.

---

## Verification Protocol

### Conceptual Test
1. Sample tasks that require user-state modeling vs pure factual correctness.
2. Analyze reward model scores (if accessible) or proxy via model confidence.
3. Test if both task types receive similar reward signals.

### Success Criteria
- Primary: Evidence of conflated reward signal
- Secondary: Similar confidence on both task types

### Variables (if applicable)
- **Independent Variable:** RLHF training objective
- **Dependent Variable:** Reward model behavior on correctness vs user-modeling tasks
- **Controlled Variables:** Model architecture, training data

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Combined RLHF Benchmarks
- **Type:** standard
- **Source:** TruthfulQA (817 tasks) + ETHICS justice (~500 tasks) + HHH single-turn (~200 tasks)
- **Path:** Hugging Face datasets / lm-evaluation-harness
- **Hypothesis Fit:** These benchmarks evaluate RLHF model behavior with clear correctness labels

### Selected Model
- **Name:** Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct
- **Type:** instruction-following LLMs
- **Source:** meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, mistralai/Mistral-7B-Instruct-v0.2
- **Hypothesis Fit:** Representative RLHF-trained models with accessible logprobs

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Aggregate benchmark accuracy | ~75% on TruthfulQA for top RLHF models | TruthfulQA |
| Topic-stratified evaluation | Varies by topic (~10% variance) | Various |

### Baseline Performance
~75% accuracy on TruthfulQA for top RLHF models

### Gap Analysis
Existing benchmarks lack directionality classification. Shen et al. 2024 established theoretical bidirectional alignment framework but left task-level classification unsolved.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (COMPLETED - silhouette_score: 0.6016, best_k: 2, PASS)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT - Reward models may separate dimensions; alternative mechanism

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 is the first mechanism hypothesis in the causal chain. It depends on H-E1 (existence of calibration inversion clusters, now proven). H-M1's success enables H-M2, H-M3, and H-M4 to proceed.

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED (PASS)
- **Key Findings:** silhouette_score = 0.6016, best_k = 2, total_tasks = 2212, inverted_tasks = 1468
- **Implication for H-M1:** Calibration inversion clusters exist systematically. Now test whether RLHF reward conflation explains this pattern.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Previous hypothesis results for continuation context

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-m1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
