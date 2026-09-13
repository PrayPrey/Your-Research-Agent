# Product Requirements Document: H-E1 AUROC Discriminative Degradation Analysis

**Document ID:** PRD-H-E1-001
**Version:** 1.0
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Hypothesis:** H-E1 (EXISTENCE)
**Status:** COMPLETE

---

## Executive Summary

This PRD defines the requirements for validating hypothesis H-E1: that instruction-tuned LLMs exhibit significantly lower AUROC for margin-based correctness prediction compared to their base model counterparts. This is a MUST_WORK gate hypothesis that forms the foundation for subsequent mechanism hypotheses (H-M1, H-M2, H-M3).

The experiment compares 3 model families (Qwen, Llama, Mistral) across base vs instruct variants using the MMLU benchmark dataset (~14,000 samples). Success criteria require AUROC_base > AUROC_instruct for all 3 families with non-overlapping 95% confidence intervals.

---

## Problem Statement

### Background

RLHF instruction tuning has been shown to improve model helpfulness and instruction-following capabilities. However, there is concern that this training process may degrade the discriminative quality of confidence signals - specifically, the ability for prediction margins to distinguish correct from incorrect answers.

### Problem

**Research Question:** Does RLHF instruction tuning degrade the discriminative quality of confidence signals (measured via AUROC for margin-based correctness prediction)?

**Hypothesis Statement:** Instruction-tuned LLMs exhibit significantly lower AUROC for margin-based correctness prediction compared to their base model counterparts across Qwen, Llama, and Mistral families.

### Impact

- **If validated:** Establishes existence of discriminative degradation, enabling investigation of underlying mechanisms
- **If falsified:** Terminates hypothesis chain, requires return to Phase 0 for alternative research direction

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1:** Load MMLU dataset from HuggingFace (`cais/mmlu`, "all" configuration)
- Use test split as primary evaluation set (~14,000 samples)
- Validate dataset structure: question, choices (4 options), answer (0-3 index)

**FR-1.2:** Format MCQ prompts consistently
- Template: "Question: {question}\nA. {choice_a}\nB. {choice_b}\nC. {choice_c}\nD. {choice_d}\nAnswer:"
- No few-shot examples (zero-shot evaluation)

**FR-1.3:** Implement progress tracking
- Log processing progress every 100 samples
- Support checkpoint/resume for large-scale evaluation

### FR-2: Model Loading

**FR-2.1:** Load 6 models (3 families × 2 variants):

| Family | Base Model | Instruct Model |
|--------|-----------|----------------|
| Qwen | `Qwen/Qwen2.5-7B` | `Qwen/Qwen2.5-7B-Instruct` |
| Llama | `meta-llama/Llama-2-7b-hf` | `meta-llama/Llama-2-7b-chat-hf` |
| Mistral | `mistralai/Mistral-7B-v0.1` | `mistralai/Mistral-7B-Instruct-v0.2` |

**FR-2.2:** Model configuration
- Precision: float16 (for GPU memory efficiency)
- Device: CUDA with single GPU
- Memory management: Clear GPU memory between model loads

**FR-2.3:** Tokenizer configuration
- Use model-specific tokenizers
- Handle padding token configuration for causal LMs

### FR-3: Logit Extraction

**FR-3.1:** Extract logits at last token position for answer choices
- Access `outputs.logits[0, -1, :]` for last token
- Map A/B/C/D to tokenizer-specific token IDs

**FR-3.2:** Handle tokenizer variations
- Use `tokenizer.encode(f" {chr(65+i)}")[-1]` pattern for choice tokens
- Validate token IDs exist in vocabulary

**FR-3.3:** Implement greedy decoding
- Temperature = 0 (deterministic)
- No sampling or beam search

### FR-4: Margin Computation

**FR-4.1:** Compute confidence margin for each sample
- Definition: `margin = logit_top1 - logit_top2`
- Sort logits descending, take difference of top 2

**FR-4.2:** Determine prediction correctness
- Compare argmax of choice logits to ground truth answer
- Store as binary label (1 = correct, 0 = incorrect)

### FR-5: AUROC Computation

**FR-5.1:** Compute AUROC for margin → correctness prediction
- Use `sklearn.metrics.roc_auc_score(correctness_labels, margins)`
- Handle edge cases: all correct/incorrect predictions

**FR-5.2:** Compute bootstrap 95% confidence intervals
- N = 1000 bootstrap iterations
- Sample with replacement
- Report 2.5th and 97.5th percentiles

**FR-5.3:** Compute per-family AUROC comparison
- Base AUROC vs Instruct AUROC for each family
- Delta = AUROC_base - AUROC_instruct

### FR-6: Secondary Metrics

**FR-6.1:** Compute conditional mean margins
- E[margin | correct prediction]
- E[margin | incorrect prediction]

**FR-6.2:** Compute I² heterogeneity statistic
- For meta-analysis across model families
- Quantify consistency of effect across families

### FR-7: Visualization

**FR-7.1:** Generate AUROC comparison bar chart (REQUIRED)
- 3 grouped bars (one per family)
- Each group: base vs instruct comparison
- Include 95% CI error bars

**FR-7.2:** Generate margin distribution plots
- KDE plots for correct vs incorrect predictions
- Compare base and instruct distributions

**FR-7.3:** Generate forest plot
- AUROC difference (base - instruct) per family
- Pooled estimate with CI

**FR-7.4:** Save all figures to `h-e1/figures/` directory

### FR-8: Results Reporting

**FR-8.1:** Generate structured results file
- YAML/JSON format with all metrics
- Include raw data for reproducibility

**FR-8.2:** Generate validation report
- Summary statistics per model family
- Gate evaluation (MUST_WORK criteria)
- Recommendation for hypothesis outcome

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1:** Complete evaluation within 4 hours
- Target: ~14,000 samples × 6 models
- Estimated: ~1 second per sample inference

**NFR-1.2:** GPU memory management
- Support single 40GB GPU (A100)
- Implement model unloading between families

### NFR-2: Reproducibility

**NFR-2.1:** Fixed random seeds
- Seed = 42 for all random operations
- Bootstrap sampling uses numpy random state

**NFR-2.2:** Deterministic inference
- Temperature = 0
- No dropout at inference time

### NFR-3: Reliability

**NFR-3.1:** Checkpoint support
- Save intermediate results every 1000 samples
- Support resume from checkpoint

**NFR-3.2:** Error handling
- Graceful handling of OOM errors
- Retry logic for transient failures

### NFR-4: Observability

**NFR-4.1:** Logging
- Log model loading events
- Log inference progress
- Log metric computation

**NFR-4.2:** Timing
- Track wall-clock time per model
- Track total experiment duration

---

## Success Criteria

### Primary Gate Criteria (MUST_WORK)

**SC-1:** AUROC_base > AUROC_instruct for ALL 3 model families
- Qwen: AUROC_base > AUROC_instruct
- Llama: AUROC_base > AUROC_instruct
- Mistral: AUROC_base > AUROC_instruct

**SC-2:** 95% CI of AUROC difference does not overlap zero
- For each family, CI_lower(AUROC_base - AUROC_instruct) > 0

### Secondary Criteria (Informational)

**SC-3:** Effect consistency
- I² < 50% indicates low heterogeneity
- Similar effect direction across families

**SC-4:** Effect size
- Cohen's d for AUROC difference reportable

---

## Dependencies

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | >=4.35.0 | Model loading |
| torch | >=2.0.0 | Inference |
| datasets | >=2.14.0 | MMLU loading |
| scikit-learn | >=1.3.0 | AUROC computation |
| numpy | >=1.24.0 | Numerical operations |
| matplotlib | >=3.7.0 | Visualization |
| seaborn | >=0.12.0 | Statistical plots |

### Internal Dependencies

| Dependency | Source |
|------------|--------|
| Phase 2C Experiment Brief | `h-e1/02c_experiment_brief.md` |
| verification_state.yaml | Pipeline state tracking |

### Model Access Requirements

- HuggingFace account with model access
- Llama-2 model access approval (Meta)
- Qwen model access (open)
- Mistral model access (open)

---

## Data Specifications

### Input Data

**MMLU Dataset:**
- Source: `cais/mmlu` on HuggingFace
- Split: test (~14,000 samples)
- Format: question (str), choices (list[str]), answer (int 0-3)

### Output Data

**Primary Outputs:**
- `h-e1/results/auroc_results.yaml` - Structured results
- `h-e1/04_validation.md` - Validation report
- `h-e1/figures/auroc_comparison.png` - Main figure

**Cache Outputs:**
- `h-e1/cache/{model_name}_margins.npy` - Margin cache per model
- `h-e1/cache/{model_name}_correctness.npy` - Correctness cache

---

## Constraints

### Technical Constraints

- Single GPU execution (no multi-GPU parallelism for this PoC)
- Float16 precision required for memory efficiency
- Sequential model evaluation (one model loaded at a time)

### Scope Constraints

- MMLU dataset only (no TruthfulQA for H-E1)
- Zero-shot evaluation only (no few-shot)
- 7B parameter models only (no smaller/larger variants)

### Budget Constraints

- Task budget: 15 tasks maximum (LIGHT tier for EXISTENCE hypothesis)
- Epic range: 4-8 epics

---

## Risks and Mitigations

### Risk 1: Llama-2 Access Denied
- **Probability:** Low (requires Meta approval)
- **Impact:** High (lose one model family)
- **Mitigation:** Alternative models (Llama-3 if available)

### Risk 2: GPU Memory Overflow
- **Probability:** Medium (7B models in fp16)
- **Impact:** Medium (experiment fails)
- **Mitigation:** Batch size 1, model unloading, gradient checkpointing off

### Risk 3: AUROC Near 0.5 (No Discriminative Power)
- **Probability:** Low (margins should have some signal)
- **Impact:** High (hypothesis fails)
- **Mitigation:** This is a valid scientific outcome, not a code failure

---

## Appendix: Phase 2C Traceability

| PRD Requirement | Phase 2C Source |
|-----------------|-----------------|
| FR-1 (Dataset) | Dataset section |
| FR-2 (Models) | Models section, Table |
| FR-3 (Logits) | Code Analysis section |
| FR-4 (Margin) | Core Mechanism Implementation |
| FR-5 (AUROC) | Evaluation section |
| FR-6 (Secondary) | Secondary Metrics |
| FR-7 (Viz) | Visualization Requirements |
| Success Criteria | PoC Success Check |

---

*Generated by Phase 3 Implementation Planning Workflow*
*Source: h-e1/02c_experiment_brief.md*
*Next: Architecture Design (03_architecture.md)*
