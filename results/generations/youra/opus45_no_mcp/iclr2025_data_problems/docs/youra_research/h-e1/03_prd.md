# Product Requirements Document (PRD)

**Hypothesis:** H-E1 - SSI Discriminates Contamination Status
**Date:** 2026-08-19
**Type:** EXISTENCE (Proof of Concept)
**Author:** Anonymous

---

## Executive Summary

Implement and validate the Semantic Saturation Index (SSI) as a novel metric for detecting benchmark contamination in language models. SSI measures confidence variance across paraphrased versions of benchmark items—contaminated models are hypothesized to show uniform confidence (low variance, high SSI) while clean models show variable confidence (high variance, low SSI).

**Core Deliverable:** Binary classifier achieving AUC > 0.7 for discriminating clean vs. contaminated models using SSI scores.

---

## Problem Statement

Current contamination detection methods rely on surface-form matching (n-gram overlap, vector similarity) which fail on paraphrased contamination. SSI proposes a behavioral approach: measuring how uniformly a model responds across semantically equivalent phrasings. This experiment tests whether SSI can discriminate contamination status.

---

## Functional Requirements

### FR-1: Data Pipeline

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load MMLU test split (14,042 items) from HuggingFace `cais/mmlu` | 02c_experiment_brief |
| FR-1.2 | Load MMLU auxiliary_train split (99,842 items) for contamination injection | 02c_experiment_brief |
| FR-1.3 | Generate 20 paraphrases per item using T5/GPT-4/rule-based methods | 02c_experiment_brief |
| FR-1.4 | Store paraphrases in structured format with item-to-paraphrase mapping | 02c_experiment_brief |

### FR-2: Model Preparation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Load baseline Mistral-7B-v0.1 from HuggingFace | 02c_experiment_brief |
| FR-2.2 | Fine-tune clean model (0% MMLU contamination) with LoRA | 02c_experiment_brief |
| FR-2.3 | Fine-tune low contamination model (10% = 1,404 MMLU items) | 02c_experiment_brief |
| FR-2.4 | Fine-tune high contamination model (50% = 7,021 MMLU items) | 02c_experiment_brief |

### FR-3: SSI Computation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-3.1 | Format MMLU items as multiple-choice prompts | 02c_experiment_brief |
| FR-3.2 | Extract confidence scores (softmax over answer token logits) | 02c_experiment_brief |
| FR-3.3 | Compute SSI = 1/variance(confidence_scores) per item | 02c_experiment_brief |
| FR-3.4 | Aggregate SSI scores across all test items | 02c_experiment_brief |

### FR-4: Evaluation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-4.1 | Compute AUC for binary classification (clean=0, contaminated=1) | 02c_experiment_brief |
| FR-4.2 | Compute Cohen's d effect size between distributions | 02c_experiment_brief |
| FR-4.3 | Generate SSI distribution plots (violin/box) | 02c_experiment_brief |
| FR-4.4 | Generate ROC curve with AUC annotation | 02c_experiment_brief |
| FR-4.5 | Generate contamination level analysis (SSI vs. contamination %) | 02c_experiment_brief |

### FR-5: Ablation Studies

| ID | Requirement | Source |
|----|-------------|--------|
| FR-5.1 | Test SSI with varying paraphrase counts (5, 10, 15, 20) | 02c_experiment_brief |
| FR-5.2 | Compare paraphrase methods (T5-only, GPT-4-only, mixed) | 02c_experiment_brief |
| FR-5.3 | Analyze per-subject SSI discrimination | 02c_experiment_brief |

---

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Support BF16 inference for memory efficiency | Must |
| NFR-2 | Reproducible results via fixed random seeds | Must |
| NFR-3 | GPU memory < 24GB for single-GPU execution | Should |
| NFR-4 | Process full test set in < 48 hours | Should |
| NFR-5 | Modular code for extension to other benchmarks | Could |

---

## Success Criteria

### Primary Gate (MUST_WORK)

| Metric | Target | Description |
|--------|--------|-------------|
| AUC | > 0.7 | Binary classification of clean vs. contaminated |

### Secondary Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Cohen's d | > 0.5 | Effect size between SSI distributions |
| Per-level AUC | > 0.6 | For each contamination level (10%, 50%) |

### Gate Decision

- **PASS (AUC > 0.7):** Proceed to H-M1 (mechanism hypotheses)
- **FAIL (AUC ≤ 0.7):** ABANDON SSI approach

---

## Dependencies

| Dependency | Type | Source |
|------------|------|--------|
| HuggingFace Transformers | Library | Model loading |
| HuggingFace Datasets | Library | MMLU loading |
| PEFT | Library | LoRA fine-tuning |
| scikit-learn | Library | AUC, metrics |
| PyTorch | Framework | Model inference |
| GPU (A100/V100) | Hardware | Fine-tuning |

---

## Scope Exclusions

- Multi-model generalization (other models beyond Mistral-7B)
- Cross-benchmark testing (other benchmarks beyond MMLU)
- Real-world deployment interface
- Real-time detection capabilities

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-19 | Initial PRD from Phase 2C experiment brief |
