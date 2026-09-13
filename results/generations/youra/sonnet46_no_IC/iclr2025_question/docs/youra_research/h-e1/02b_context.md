# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-05
**Main Hypothesis:** Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection (H-LayerLensUQ-v2)
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under white-box single-greedy-pass inference on TriviaQA and TruthfulQA, if per-layer logit-lens statistics (entropy, max-prob, adjacent-layer KL; mean over answer tokens) are computed at every intermediate layer, then at least one screened (layer, signal) pair per model exhibits class-separable statistics on the selection split (corrected AUROC >= 0.55, both datasets), because unresolved candidate competition for hallucinated answers leaves separation in token space at depth.

Includes mandatory A2 protocol-validity anchor: prior-run (h-e1/v1) final-layer reference AUROCs must be reproduced within ±0.03 BEFORE the full sweep.

### Type
EXISTENCE

### Rationale
The signal must EXIST in token space at depth before any selection, rescue, transfer, or fusion claim is testable. LLaMA-2-7B is the binding existence case — its documented final-layer failure (AUROC 0.5186 on TriviaQA) is exactly what depth reading must escape.

---

## Verification Protocol

### Conceptual Test
1. Load datasets with v1-verbatim prompts/labels; stratified 50/50 selection/test split per dataset (seed 42); write and lock test split.
2. Smoke run (10 examples/model, shape + memory assert), then full sweep: 1,817 examples x 3 models, single greedy pass with teacher-forced re-forward, streaming 3 signals x 32 layers per example to scalar CSV (reuse v1 code + 871/1000 llama2/TriviaQA cache where protocol-identical).
3. Reproduce v1 final-layer references within ±0.03 (A2 halt gate).
4. Apply degeneracy screen on selection split (drop layers with entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%).
5. Evaluate existence criterion per model on selection split.

### Success Criteria
- **Primary:** >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on both datasets
- **Secondary:** A2 anchor reproduced ±0.03; degeneracy screen retains >= 5 layers per model

### Variables (if applicable)
- **Independent Variable:** readout_layer (1-31 screened), signal_type (3 levels: entropy, max_token_probability, adjacent_layer_KL), model_family (3 levels)
- **Dependent Variable:** AUROC_corrected on selection split
- **Controlled Variables:** greedy decoding (do_sample=False), v1-verbatim prompts/labels, fp16 weights / float32 statistics, stratified 50/50 split seed 42, log(p+1e-12) guard, KL NaN at layer 1 excluded

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** TriviaQA (rc.nocontext) + TruthfulQA (generation)
- **Type:** standard
- **Source:** HuggingFace: mandarjoshi/trivia_qa (validation[:1000]), truthfulqa/truthful_qa (validation, 817)
- **Path:** HF cache (verified present by v1 runs); labels/prompts reused verbatim from v1
- **Hypothesis Fit:** Existing real benchmarks with the documented final-layer failure baseline (llama2/TriviaQA 0.5186) — the rescue test is only meaningful on the exact protocol where the failure was recorded; no new benchmarks, no synthetic data, no human evaluation

### Selected Model
- **Name:** meta-llama/Llama-2-7b-hf + mistralai/Mistral-7B-v0.1 + meta-llama/Meta-Llama-3-8B-Instruct
- **Type:** frozen decoder-only LLMs, 32 layers each, fp16, single GPU
- **Source:** HuggingFace (HF cache verified by v1)
- **Hypothesis Fit:** Identical model set to v1 preserves baseline comparability; LLaMA-2-7B is the designated rescue stress test; uniform lens path `model.lm_head(model.model.norm(h_l))` across all three; base/instruct asymmetry documented as scope limitation R3

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Final-layer mean token entropy (v1) | AUROC 0.5186/0.5153 (llama2, FAIL), 0.5268/0.5886 (mistral), 0.6583/0.6161 (llama3) | TriviaQA/TruthfulQA |
| Final-layer max-token probability | Single-pass confidence foil at output layer (within-sweep) | TriviaQA/TruthfulQA |
| FEPoID + hidden-state probing | AUROC avg 0.7253 (LLaMA-3.1-8B-It), 0.8531 (Mistral-7B-It) — supervised skyline, deferred to Phase 5 | QA benchmarks |
| Semantic Entropy [Farquhar et al., 2024] | AUROC 0.5311/0.6560 avg; 10x inference cost — excluded direction | QA benchmarks |
| SAPLMA [Azaria & Mitchell, 2023] | 71-83% accuracy; supervised probe | True-False statements |

### Baseline Performance
Final-layer references to reproduce (A2 anchor, ±0.03): llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161 (TriviaQA/TruthfulQA).

### Gap Analysis
No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob / adjacent-layer KL) as per-layer hallucination-detection AUROC scores exists in the literature (GAP-001). Entropy-Lens computes the identical feature as a computation signature, never for detection. h-e1 existence target (0.55 selection-split) is deliberately below the H-M1 rescue target (0.60 test-split).

---

## Dependencies and Gate Conditions

### Prerequisites
None (Level 0 root hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** Separation absent in token space at depth — entire hypothesis tree dies. If failure is screen-driven (A1 lens degeneracy), tuned-lens fallback is a documented pivot with relabeled claims (trained components).

**Phase Assignment:** Phase A — Foundation (Gate 1)

**Estimated Duration:** 2 weeks (W1-2); all GPU compute front-loaded here

---

## Dependency Context

### Relationship to Other Hypotheses
h-e1 is the root of the DAG. h-m1 (rescue, MUST_WORK), h-m3 (fusion, SHOULD_WORK), and h-c1 (transfer, SHOULD_WORK) all depend on h-e1's artifacts: locked splits, streamed per-layer scalar CSVs, degeneracy screen results, and per-model selections. h-m2 depends on h-m1. Everything after this sweep is CPU-side analysis of streamed scalars — a Gate 1 failure kills the plan at 1/3 of timeline cost.

Key risks affecting this hypothesis: RISK-1 lens degeneracy (High), RISK-2 anchor reproduction failure (halt gate), RISK-3 aggregation noise, RISK-6 sweep interruption (v1 died at 871/1000 samples — streaming resumable CSV required).

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** Will be updated by Phase 2C
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Baseline comparison targets

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes — final-layer references serve as the A2 anchor and the floor the depth signal must escape

---

*Optimized for single-hypothesis experiment design*
