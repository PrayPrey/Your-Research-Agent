# Product Requirements Document (PRD)

**Hypothesis:** H-M1 - Contamination Injection Creates Training Exposure
**Date:** 2026-08-19
**Type:** MECHANISM (Causal Validation)
**Author:** Anonymous
**Base Hypothesis:** H-E1 (PASSED)

---

## Executive Summary

Validate that controlled contamination injection via LoRA fine-tuning on MMLU benchmark items creates measurable training exposure. This MECHANISM hypothesis tests the first causal link in the SSI chain: that including benchmark items in training data causes the model to demonstrably learn those specific items, producing higher accuracy on contaminated items versus clean items.

**Core Deliverable:** Demonstrated accuracy differential between contaminated and clean items across 5 contamination levels (0%, 5%, 10%, 20%, 50%), with monotonic increase in differential.

---

## Problem Statement

For SSI to work as a contamination detector, contamination must actually create detectable behavioral changes. H-M1 validates this prerequisite: does fine-tuning on benchmark items create measurable learning? This mechanism must work (MUST_WORK gate) before testing whether SSI can detect the resulting behavioral signatures.

**Continuation from H-E1:** Reuses validated Mistral-7B + LoRA configuration (lr=2e-5, batch=4, grad_accum=8, epochs=3).

---

## Functional Requirements

### FR-1: Data Pipeline

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load MMLU test split (14,042 items) from HuggingFace `cais/mmlu` | 02c_experiment_brief |
| FR-1.2 | Create contamination subsets at 5 levels: 0 (0), 702 (5%), 1404 (10%), 2808 (20%), 7021 (50%) items | 02c_experiment_brief |
| FR-1.3 | Format items as QA pairs: "Question: {q}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\nAnswer: {correct}" | 02c_experiment_brief |
| FR-1.4 | Maintain item-level tracking (contaminated_ids set) for per-item evaluation | 02c_experiment_brief |
| FR-1.5 | Deterministic selection using seed=42 for reproducibility | 02c_experiment_brief |

### FR-2: Contamination Injection (LoRA Fine-tuning)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Load Mistral-7B-v0.1 base model from HuggingFace | H-E1 validated |
| FR-2.2 | Apply LoRA config: rank=16, alpha=32, dropout=0.05, target_modules=[q_proj, v_proj, k_proj, o_proj] | 02c_experiment_brief |
| FR-2.3 | Train 5 model variants (one per contamination level) | 02c_experiment_brief |
| FR-2.4 | Training params: lr=2e-5, batch=4, grad_accum=8, epochs=3 | H-E1 validated |
| FR-2.5 | Run with 3 seeds (42, 123, 456) for mechanism reproducibility | 02c_experiment_brief |

### FR-3: Evaluation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-3.1 | Evaluate each model on FULL test set (14,042 items) | 02c_experiment_brief |
| FR-3.2 | Extract per-item accuracy (correct/incorrect) | 02c_experiment_brief |
| FR-3.3 | Compute contaminated_accuracy: mean accuracy on contaminated items | 02c_experiment_brief |
| FR-3.4 | Compute clean_accuracy: mean accuracy on non-contaminated items | 02c_experiment_brief |
| FR-3.5 | Compute effect_size: contaminated_accuracy - clean_accuracy | 02c_experiment_brief |

### FR-4: Visualization

| ID | Requirement | Source |
|----|-------------|--------|
| FR-4.1 | Line plot: Accuracy (contaminated vs clean) across contamination levels | 02c_experiment_brief |
| FR-4.2 | Bar chart: Effect size (accuracy differential) per contamination level | 02c_experiment_brief |
| FR-4.3 | Per-item accuracy distribution (contaminated vs clean) | 02c_experiment_brief |

### FR-5: Mechanism Verification

| ID | Requirement | Source |
|----|-------------|--------|
| FR-5.1 | Verify mechanism_active: contaminated_acc > clean_acc at all non-zero levels | 02c_experiment_brief |
| FR-5.2 | Verify monotonic_trend: effect_size increases with contamination level | 02c_experiment_brief |
| FR-5.3 | Log mechanism check results with [MECHANISM CHECK] prefix | 02c_experiment_brief |

---

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | BF16 inference for memory efficiency (<24GB GPU) | Must |
| NFR-2 | Reproducible results via fixed seeds (42, 123, 456) | Must |
| NFR-3 | Complete evaluation on full 14,042 test set | Must |
| NFR-4 | Total runtime < 24 hours per contamination level | Should |
| NFR-5 | Modular code reusable by H-M2 (representation analysis) | Should |

---

## Success Criteria

### Primary Gate (MUST_WORK)

| Metric | Target | Description |
|--------|--------|-------------|
| Mechanism Active | TRUE | contaminated_acc > clean_acc at ALL non-zero levels |
| Effect Size | > 0.05 | At least 5% accuracy gain on contaminated items |

### Secondary Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Monotonic Trend | TRUE | effect_size(5%) < effect_size(10%) < effect_size(20%) < effect_size(50%) |
| Reproducibility | 3/3 seeds | Effect consistent across all 3 random seeds |

### Gate Decision

- **PASS:** Proceed to H-M2 (representation invariance analysis)
- **FAIL:** PIVOT contamination injection procedure (longer training, different format, different LR)

---

## Dependencies

| Dependency | Type | Source |
|------------|------|--------|
| H-E1 code | Codebase | Reuse data.py, model.py from H-E1 |
| HuggingFace Transformers | Library | Model loading |
| HuggingFace Datasets | Library | MMLU loading |
| PEFT | Library | LoRA fine-tuning |
| lm-evaluation-harness | Library | Standardized MMLU evaluation |
| PyTorch | Framework | Model training/inference |
| GPU (A100/V100) | Hardware | Fine-tuning |

---

## Scope Exclusions

- Paraphrase generation (handled in H-M2)
- SSI computation (handled in H-M3/M4)
- Multi-model generalization
- Cross-benchmark testing

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-19 | Initial PRD from Phase 2C experiment brief |
