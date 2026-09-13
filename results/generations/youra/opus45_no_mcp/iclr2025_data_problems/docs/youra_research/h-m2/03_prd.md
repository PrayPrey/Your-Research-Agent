# Product Requirements Document (PRD)

**Hypothesis:** H-M2 - Training Develops Robust Semantic Representations
**Date:** 2026-08-19
**Type:** MECHANISM (Causal Validation)
**Author:** Anonymous
**Base Hypothesis:** H-M1 (PASSED - effect size 15.1-31.1%)

---

## Executive Summary

Validate that diverse training exposure (paraphrase-augmented contamination) creates representation invariance compared to verbatim-only training. This MECHANISM hypothesis tests the second causal link in the SSI chain: that learning benchmark items in various phrasings develops representations invariant to surface form.

**Core Deliverable:** Demonstrated higher Mean Paraphrase Similarity (MPS) in paraphrase-trained models versus verbatim-trained models, with effect size > 0.3 (Cohen's d).

---

## Problem Statement

For SSI to detect contamination via confidence variance, contaminated models must develop phrasing-invariant representations. H-M2 validates this prerequisite: does diverse training create more invariant internal representations? This mechanism should work (SHOULD_WORK gate) to justify the SSI theoretical foundation.

**Continuation from H-M1:** Reuses validated contamination injection procedure (LoRA config, training params) and extends with paraphrase augmentation.

---

## Functional Requirements

### FR-1: Data Pipeline

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load MMLU test split (14,042 items) from HuggingFace `cais/mmlu` | 02c_experiment_brief |
| FR-1.2 | Generate K=5 paraphrases per item using T5-paraphrase (40%), GPT-4 (40%), rule-based (20%) | 02c_experiment_brief |
| FR-1.3 | Create contamination subset at 10% level (1,404 items) for both training conditions | 02c_experiment_brief |
| FR-1.4 | Format items as QA pairs: "Question: {q}\nA. {A}\nB. {B}\nC. {C}\nD. {D}\nAnswer: {correct}" | 02c_experiment_brief |
| FR-1.5 | Deterministic selection using seed=42 for reproducibility | 02c_experiment_brief |

### FR-2: Verbatim Model Training (Baseline)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Load Mistral-7B-v0.1 base model from HuggingFace | H-M1 validated |
| FR-2.2 | Apply LoRA config: rank=16, alpha=32, dropout=0.05, target_modules=[q_proj, v_proj, k_proj, o_proj] | 02c_experiment_brief |
| FR-2.3 | Train on VERBATIM items only: 1,404 samples | 02c_experiment_brief |
| FR-2.4 | Training params: lr=2e-5, batch=4, grad_accum=8, epochs=12 (match compute with paraphrase) | 02c_experiment_brief |
| FR-2.5 | Alternative: Load H-M1 10% contaminated checkpoint directly | 02c_experiment_brief |

### FR-3: Paraphrase-Augmented Model Training (Proposed)

| ID | Requirement | Source |
|----|-------------|--------|
| FR-3.1 | Load Mistral-7B-v0.1 base model from HuggingFace | H-M1 validated |
| FR-3.2 | Apply same LoRA config as verbatim model | 02c_experiment_brief |
| FR-3.3 | Train on items + 3 paraphrases each: 1,404 × 4 = 5,616 samples | 02c_experiment_brief |
| FR-3.4 | Training params: lr=2e-5, batch=4, grad_accum=8, epochs=3 | 02c_experiment_brief |
| FR-3.5 | Run with 3 seeds (42, 123, 456) for statistical validity | 02c_experiment_brief |

### FR-4: Representation Extraction

| ID | Requirement | Source |
|----|-------------|--------|
| FR-4.1 | Extract last-layer hidden state for each input | 02c_experiment_brief |
| FR-4.2 | Mean-pool over sequence (exclude padding tokens) | 02c_experiment_brief |
| FR-4.3 | Store representations as tensors shape [4096] per item | 02c_experiment_brief |
| FR-4.4 | Extract for 1000 contaminated items + 5 paraphrases each | 02c_experiment_brief |

### FR-5: Similarity Computation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-5.1 | Compute cosine similarity between original and each paraphrase | 02c_experiment_brief |
| FR-5.2 | Calculate Mean Paraphrase Similarity (MPS) per item | 02c_experiment_brief |
| FR-5.3 | Aggregate MPS distributions for both model conditions | 02c_experiment_brief |

### FR-6: Visualization

| ID | Requirement | Source |
|----|-------------|--------|
| FR-6.1 | Histogram/density: MPS distributions for verbatim vs paraphrase models | 02c_experiment_brief |
| FR-6.2 | Box plot: Side-by-side MPS comparison by training condition | 02c_experiment_brief |
| FR-6.3 | t-SNE/UMAP of representations colored by training condition (optional) | 02c_experiment_brief |

### FR-7: Mechanism Verification

| ID | Requirement | Source |
|----|-------------|--------|
| FR-7.1 | Verify mechanism_active: MPS_paraphrase > MPS_verbatim | 02c_experiment_brief |
| FR-7.2 | Compute statistical significance via t-test | 02c_experiment_brief |
| FR-7.3 | Compute effect size (Cohen's d) | 02c_experiment_brief |
| FR-7.4 | Log mechanism check results with [MECHANISM CHECK] prefix | 02c_experiment_brief |

---

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | BF16 inference for memory efficiency (<24GB GPU) | Must |
| NFR-2 | Reproducible results via fixed seeds (42, 123, 456) | Must |
| NFR-3 | Representation extraction for 6000+ samples (1000 items × 6 variants) | Must |
| NFR-4 | Total runtime < 48 hours (training + evaluation) | Should |
| NFR-5 | Modular code reusable by H-M3 (confidence analysis) | Should |

---

## Success Criteria

### Primary Gate (SHOULD_WORK)

| Metric | Target | Description |
|--------|--------|-------------|
| Mechanism Active | TRUE | MPS_paraphrase > MPS_verbatim |
| MPS Difference | > 0.05 | At least 5% higher similarity in paraphrase model |

### Secondary Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Effect Size | > 0.3 | Cohen's d > 0.3 (medium effect) |
| p-value | < 0.05 | Statistically significant difference |
| Reproducibility | 3/3 seeds | Effect consistent across all random seeds |

### Gate Decision

- **PASS:** Proceed to H-M3 (uniform confidence analysis)
- **FAIL:** EXPLORE alternative mechanisms (attention pattern analysis, layer-specific effects)

---

## Dependencies

| Dependency | Type | Source |
|------------|------|--------|
| H-M1 code | Codebase | Reuse data.py, model.py from H-M1 |
| H-M1 checkpoint | Model | 10% contaminated model for baseline |
| HuggingFace Transformers | Library | Model loading, hidden state extraction |
| HuggingFace Datasets | Library | MMLU loading |
| PEFT | Library | LoRA fine-tuning |
| T5 Paraphrase | Model | Vamsi995/T5_Paraphrase_Paws |
| PyTorch | Framework | Model training/inference |
| SciPy | Library | Statistical tests |
| GPU (A100/V100) | Hardware | Fine-tuning |

---

## Scope Exclusions

- Confidence distribution analysis (handled in H-M3)
- SSI computation (handled in H-M4)
- Multi-model generalization (single model comparison)
- Cross-benchmark testing (MMLU only)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-19 | Initial PRD from Phase 2C experiment brief |
