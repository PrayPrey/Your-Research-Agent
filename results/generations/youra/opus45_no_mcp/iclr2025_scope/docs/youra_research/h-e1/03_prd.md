# Product Requirements Document: H-E1

**Date:** 2026-08-19
**Author:** YouRA Research System
**Hypothesis:** H-E1 - Task-Dependent Adaptation Transformation Exists
**Type:** EXISTENCE (PoC Validation)
**Phase 2C Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This PRD defines requirements for validating hypothesis H-E1: Under controlled conversion from Transformer to Mamba architecture, LoRA adaptation exhibits measurable task-dependent patterns across benchmarks spanning the retrieval density spectrum.

**Primary Objective:** Demonstrate that task-dependent adaptation transformation exists by comparing LoRA fine-tuning efficiency between Transformer (Llama-2-7B) and Mamba architectures across 4 benchmarks with varying retrieval density.

**Success Criteria:** 
- Sequential tasks (GSM8K): delta >= -5%
- Retrieval tasks (NQ): delta <= -15%
- Pattern correlation: Spearman rho > 0.5 for delta vs retrieval density

---

## 2. Problem Statement

### 2.1 Research Question
Does converting from quadratic attention (Transformer) to sub-quadratic (SSM/Mamba) architecture produce predictable, task-dependent changes in LoRA adaptation efficiency?

### 2.2 Hypothesis Statement
Under controlled conversion from Transformer to Mamba architecture, if LoRA adaptation is applied to analogous projection layers across 4+ benchmarks spanning retrieval density spectrum, then measurable task-dependent patterns emerge.

### 2.3 Gate Condition
**MUST_WORK Gate:** If no task-dependent pattern is observed, abandon main hypothesis H-AdaptTransform-v1.

---

## 3. Functional Requirements

### FR-1: Baseline Model Training (Transformer + LoRA)
**Description:** Fine-tune Llama-2-7B with LoRA on 4 benchmarks
**Source:** 02c_experiment_brief.md - Baseline Model section
**Acceptance Criteria:**
- LoRA config: rank=16, alpha=32, target_modules=[q_proj, k_proj, v_proj, o_proj]
- Train 3 epochs per benchmark
- Record accuracy for each benchmark

### FR-2: Proposed Model Training (Mamba + LoRA)
**Description:** Fine-tune Mamba model with LoRA on same 4 benchmarks
**Source:** 02c_experiment_brief.md - Proposed Model section
**Acceptance Criteria:**
- LoRA config: rank=16, alpha=32, target_modules=[in_proj, out_proj]
- Same training protocol as baseline
- Record accuracy for each benchmark

### FR-3: Multi-Benchmark Evaluation Suite
**Description:** Evaluate both models on 4 benchmarks spanning retrieval density
**Source:** 02c_experiment_brief.md - Dataset section
**Benchmarks:**
| Benchmark | Test Size | Retrieval Density | Metric |
|-----------|-----------|-------------------|--------|
| GSM8K | 1,319 | 0.1 (low) | Exact Match |
| Natural Questions | 3,610 | 0.9 (high) | F1 |
| MMLU | 14,042 | 0.5 (medium) | Accuracy |
| HotpotQA | 7,405 | 0.7 (medium-high) | F1 |

### FR-4: Adaptation Efficiency Delta Calculation
**Description:** Calculate (Mamba_accuracy - Transformer_accuracy) per benchmark
**Source:** 02c_experiment_brief.md - Evaluation section
**Acceptance Criteria:**
- Delta computed for all 4 benchmarks
- Spearman correlation computed between delta and retrieval density

### FR-5: Mechanism Verification
**Description:** Verify SSM state evolution is active during Mamba forward pass
**Source:** 02c_experiment_brief.md - Mechanism Verification Protocol
**Acceptance Criteria:**
- verify_mechanism_active() returns True
- SSM A_log and D matrices present in model

### FR-6: Visualization Generation
**Description:** Generate required figures for analysis
**Source:** 02c_experiment_brief.md - Visualization Requirements
**Figures:**
- Gate Metrics Comparison: Bar chart (Transformer vs Mamba × 4 benchmarks)
- Accuracy Delta vs Retrieval Density: Scatter plot with correlation
- Training Loss Curves: Transformer vs Mamba

---

## 4. Data Specification

### 4.1 Datasets

| Dataset | Source | Split | Size | Download Method |
|---------|--------|-------|------|-----------------|
| GSM8K | openai/gsm8k | test | 1,319 | HuggingFace auto-download |
| Natural Questions | google-research-datasets/natural_questions | validation | 3,610 | HuggingFace auto-download |
| MMLU | cais/mmlu | test | 14,042 | HuggingFace auto-download |
| HotpotQA | hotpot_qa | validation | 7,405 | HuggingFace auto-download |

**Total Evaluation Samples:** 26,376

### 4.2 Model Checkpoints

| Model | Source | Size | Download Method |
|-------|--------|------|-----------------|
| Llama-2-7B | meta-llama/Llama-2-7b-hf | ~7B | HuggingFace (requires auth) |
| Mamba-2 | state-spaces/mamba | varies | pip install mamba-ssm |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Single seed (42) sufficient for EXISTENCE validation
- All hyperparameters documented
- Training configs saved

### NFR-2: Compute Requirements
- GPU: 1× A100 80GB (recommended) or 2× RTX 4090
- Training time: ~4-6 hours per model per benchmark
- Storage: ~50GB for checkpoints

### NFR-3: Memory Efficiency
- Gradient accumulation: 4 steps (effective batch 16)
- Mixed precision training (fp16/bf16)

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
| Benchmark | Expected Delta | Threshold |
|-----------|---------------|-----------|
| GSM8K (sequential) | >= -5% | delta >= -5% |
| Natural Questions (retrieval) | <= -15% | delta <= -15% |
| Pattern | Correlation | Spearman rho > 0.5 |

### PoC Pass Condition
1. Code runs without error on all 4 benchmarks
2. Task-dependent pattern direction matches hypothesis
3. Mechanism verification passes

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
datasets>=2.16.0
evaluate>=0.4.0
mamba-ssm>=1.2.0
accelerate>=0.25.0
```

### 7.2 External Repositories
- state-spaces/mamba (official Mamba implementation)
- huggingface/peft (LoRA implementation)

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| SSM-attention routing equivalence failure | CRITICAL | Early detection via H-E1 |
| Isocapacity comparison failure | HIGH | State dimension calibration |
| LoRA rank interpretation issues | MEDIUM | Multiple thresholds |

---

## 9. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup | 0.5 days | Environment, data download |
| Baseline Training | 1 day | Transformer + LoRA checkpoints |
| Proposed Training | 1 day | Mamba + LoRA checkpoints |
| Evaluation | 0.5 days | Metrics, figures |
| **Total** | **3 days** | Complete H-E1 validation |

---

*Generated from Phase 2C Experiment Brief*
*Ready for Phase 3 Architecture Design*
