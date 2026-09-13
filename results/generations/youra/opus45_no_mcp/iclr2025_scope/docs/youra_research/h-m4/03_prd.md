# Product Requirements Document: H-M4

**Document Version:** 1.0
**Date:** 2026-08-19
**Hypothesis ID:** H-M4
**Author:** Anonymous

---

## Executive Summary

This PRD specifies the implementation requirements for validating hypothesis H-M4: "Under cross-architecture comparison, if tasks vary in retrieval density, then adaptation efficiency change correlates with retrieval density (rho > 0.7)."

The experiment measures Spearman correlation between task retrieval density (0.1-0.9) and LoRA adaptation efficiency delta (Mamba - Transformer) across 4 benchmarks totaling 26,376 evaluation samples.

---

## Problem Statement

Previous hypotheses (H-E1 through H-M3) established individual mechanisms:
- H-E1: Task-dependent pattern exists
- H-M1: Architecture conversion changes loss landscape
- H-M2: SSM state evolution creates sequential-favorable structure
- H-M3: Landscape geometry predicts LoRA efficiency

H-M4 validates the complete causal chain by testing whether adaptation efficiency change **correlates predictably** with task retrieval density across architectures.

---

## Functional Requirements

### FR-1: Multi-Benchmark Data Pipeline

**Description:** Load and preprocess 4 benchmarks spanning retrieval density spectrum.

| Benchmark | Dataset ID | Split | Size | Retrieval Density |
|-----------|------------|-------|------|-------------------|
| GSM8K | gsm8k | test | 1,319 | 0.1 |
| MMLU | cais/mmlu | test | 14,042 | 0.5 |
| HotpotQA | hotpot_qa | validation | 7,405 | 0.7 |
| Natural Questions | natural_questions | validation | 3,610 | 0.9 |

**Acceptance Criteria:**
- All 4 datasets load successfully
- Total samples: 26,376
- Consistent tokenization across benchmarks

### FR-2: Transformer Baseline Model

**Description:** Implement Transformer with LoRA adaptation.

**Architecture:**
- d_model: 512
- n_heads: 8
- n_layers: 4
- LoRA: rank=16, alpha=32, target_modules=["q_proj", "v_proj"]

**Acceptance Criteria:**
- Model initializes with reproducible weights (seed=42)
- LoRA modules apply to query and value projections
- Forward pass produces logits of correct shape

### FR-3: Mamba Model (Reuse from H-M2/M3)

**Description:** Mamba with LoRA adaptation.

**Architecture:**
- d_model: 512
- d_state: 16
- n_layers: 4
- LoRA: rank=16, alpha=32, target_modules=["in_proj"]

**Acceptance Criteria:**
- Architecture matches validated H-M2/M3 implementation
- LoRA applies to input projection
- SSM state evolution functional

### FR-4: Training Protocol

**Description:** Consistent LoRA training across all architecture-task combinations.

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning Rate | 1e-4 |
| LR Schedule | Cosine decay |
| Batch Size | 4 |
| Max Epochs | 5 |
| Early Stopping | patience=2 |
| Weight Decay | 0.01 |
| Gradient Clipping | 1.0 |

**Acceptance Criteria:**
- 8 training runs complete (2 architectures × 4 tasks)
- Loss converges for all runs
- Training logs saved

### FR-5: Evaluation Metrics

**Description:** Compute accuracy and efficiency metrics per task-architecture pair.

**Metrics:**
- Accuracy (task-specific: exact match or MCQ accuracy)
- SAM Sharpness (epsilon=0.05, reuse from H-M2)
- Effective Rank (threshold=0.90, reuse from H-M3)

**Acceptance Criteria:**
- Accuracy computed on full test sets
- Sharpness computed post-training
- All metrics logged to results file

### FR-6: Correlation Analysis

**Description:** Compute Spearman correlation between retrieval density and accuracy delta.

**Gate Condition:**
- Primary: |Spearman rho| > 0.7
- Secondary: p-value < 0.01

**Acceptance Criteria:**
- Correlation computed from 4 data points
- Statistical significance tested
- Monotonicity checked

### FR-7: Visualization

**Description:** Generate analysis figures.

**Required:**
- Retrieval Density vs Accuracy Delta scatter plot with regression line

**Additional:**
- Architecture comparison bar chart
- Sharpness delta by task
- Summary dashboard

**Acceptance Criteria:**
- Figures saved to h-m4/figures/
- Spearman rho annotated on main figure

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed (42)
- Deterministic CUDA operations where possible
- Training checkpoints saved

### NFR-2: Resource Constraints
- GPU memory: <16GB per training run
- Total runtime: <4 hours for all 8 training runs

### NFR-3: Code Reuse
- Reuse MambaWithLoRA from H-M2/M3
- Reuse SAM sharpness from H-M2
- Reuse effective rank from H-M3

---

## Success Criteria

### Primary Gate (MUST_WORK)
- |Spearman rho| > 0.7 between retrieval density and accuracy delta
- p-value < 0.01

### Secondary Criteria
- Monotonic relationship (no outliers)
- Expected pattern: negative correlation (higher retrieval → worse Mamba performance)

### Failure Conditions
- rho ≤ 0.7 → Main hypothesis weakened
- Non-monotonic pattern → Task classification needs revision

---

## Dependencies

### Prerequisites (Validated)
- H-M3: PASS (rho=1.0 sharpness-rank correlation)

### Code Dependencies
- H-E1: TransformerWithLoRA, MambaWithLoRA
- H-M2: compute_sam_sharpness()
- H-M3: compute_effective_rank()

### Data Dependencies
- HuggingFace datasets: gsm8k, cais/mmlu, hotpot_qa, natural_questions

---

## Ablation Studies

### A-1: Retrieval Density Sensitivity
- Alternative operationalizations: binary (0/1), data-driven

### A-2: Efficiency Metric Sensitivity
- Test sharpness delta and rank delta as alternative efficiency measures

---

## Timeline

| Phase | Duration |
|-------|----------|
| Data preparation | 30 min |
| Training (8 runs) | 3-4 hours |
| Evaluation | 30 min |
| Visualization | 15 min |
| **Total** | ~5 hours |

---

## Appendix: Retrieval Density Operationalization

| Task | Retrieval Density | Justification |
|------|-------------------|---------------|
| GSM8K | 0.1 | Sequential reasoning, no fact retrieval |
| MMLU | 0.5 | Mixed knowledge, some retrieval |
| HotpotQA | 0.7 | Multi-hop requires retrieval |
| NQ | 0.9 | Pure factual retrieval |

---

*Generated for Phase 3 Implementation Planning*
*Hypothesis: H-M4 - Task-Dependent Transformation Emergence*
