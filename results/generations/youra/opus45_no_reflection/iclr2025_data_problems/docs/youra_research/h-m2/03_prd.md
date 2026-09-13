# Product Requirements Document: H-M2

**Date:** 2026-08-18
**Hypothesis:** H-M2 - Different attention structures create different Hessian curvature patterns (block-diagonal vs dense)
**Type:** MECHANISM
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines requirements for validating that different transformer attention structures (bidirectional vs causal) create measurably different Hessian curvature patterns. Building on H-M1's confirmation of attention pattern differences (98.82% sparsity difference), we now test whether these structural differences propagate to second-order curvature properties.

---

## Problem Statement

Attribution approximation methods (EK-FAC, TracIn, TRAK) make assumptions about Hessian curvature structure. Understanding how architecture affects curvature is essential for selecting appropriate attribution methods per architecture.

**Core Question:** Do bidirectional (BERT) and causal (GPT-2) attention structures produce different Hessian spectra?

---

## Functional Requirements

### FR-1: Model Loading and Preparation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load BERT-base-uncased from HuggingFace with sequence classification head | P0 |
| FR-1.2 | Load GPT-2 from HuggingFace with sequence classification head | P0 |
| FR-1.3 | Fine-tune both models on SST-2 for 3 epochs | P0 |
| FR-1.4 | Save fine-tuned checkpoints for reproducibility | P1 |

### FR-2: Dataset Loading

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Load SST-2 from GLUE benchmark via HuggingFace datasets | P0 |
| FR-2.2 | Use full training set (67,349 samples) for Hessian computation | P0 |
| FR-2.3 | Use validation set (872 samples) for consistency with H-M1 | P0 |
| FR-2.4 | Apply model-specific tokenization (BERT tokenizer, GPT-2 tokenizer) | P0 |

### FR-3: Hessian Spectrum Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Compute top-20 Hessian eigenvalues via Lanczos iteration | P0 |
| FR-3.2 | Estimate Hessian trace (sum of all eigenvalues) | P0 |
| FR-3.3 | Compute eigenvalue ratio (λ_max / λ_min) as condition number proxy | P0 |
| FR-3.4 | Generate spectral density estimate | P1 |
| FR-3.5 | Use hessian-eigenthings library (primary) or PyHessian (fallback) | P0 |

### FR-4: Kronecker Factorization Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Compute GGN approximation for attention layers | P1 |
| FR-4.2 | Estimate Kronecker factorization fit quality per layer | P1 |
| FR-4.3 | Compare fit quality between BERT and GPT-2 | P1 |

### FR-5: Ablation Studies

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Run with multiple random seeds (2 seeds minimum) | P0 |
| FR-5.2 | Test different batch sizes (256, 512) for Hessian estimation | P1 |
| FR-5.3 | Compute attention-only parameter subset Hessian | P2 |
| FR-5.4 | Compare full model vs MLP-only Hessian | P2 |

### FR-6: Evaluation and Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Generate bar chart comparing BERT vs GPT-2 spectral metrics | P0 |
| FR-6.2 | Plot top-20 eigenvalue spectrum (log scale) | P0 |
| FR-6.3 | Generate spectral density comparison plot | P1 |
| FR-6.4 | Save all figures to {hypothesis_folder}/figures/ | P0 |
| FR-6.5 | Output structured results as YAML/JSON | P0 |

---

## Non-Functional Requirements

### NFR-1: Performance
- Hessian computation must complete within 4 hours on single GPU
- Lanczos iterations: 40-60 steps for convergence
- Batch size for Hessian: 256-512 samples

### NFR-2: Reproducibility
- All experiments use fixed random seeds
- Model checkpoints saved after fine-tuning
- Full configuration logged

### NFR-3: Dependencies
- pytorch >= 2.0
- transformers >= 4.30
- hessian-eigenthings >= 0.1.0
- datasets >= 2.0
- numpy, scipy, matplotlib

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
Measurable difference (>10%) in at least one Hessian spectral metric between BERT and GPT-2.

### Primary Metrics
| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| Top Eigenvalue Difference | \|λ_max(BERT) - λ_max(GPT-2)\| / max(...) | > 10% |
| Eigenvalue Ratio Difference | Difference in condition number proxy | > 10% |
| Trace Difference | Total curvature difference | > 10% |

### Secondary Metrics
| Metric | Description | Expected Direction |
|--------|-------------|-------------------|
| Kronecker Fit Error | GPT-2 should fit better (causal structure) | GPT-2 < BERT |
| Spectral Density Shape | Different distribution shapes | Visually distinct |

---

## Data Requirements

### Input Data
| Data | Source | Size |
|------|--------|------|
| SST-2 Train | HuggingFace GLUE | 67,349 samples |
| SST-2 Validation | HuggingFace GLUE | 872 samples |

### Output Data
| Output | Format | Location |
|--------|--------|----------|
| Hessian metrics | YAML | h-m2/results.yaml |
| Eigenvalue arrays | NPZ | h-m2/eigenvalues.npz |
| Figures | PNG | h-m2/figures/*.png |
| Validation report | Markdown | h-m2/04_validation.md |

---

## Dependencies

### Prerequisite Hypotheses
- **H-E1:** PASSED - Architecture-method interaction exists
- **H-M1:** PASSED - Attention patterns differ (98.82% sparsity difference)

### External Dependencies
- HuggingFace Hub access
- GPU with 16GB+ VRAM (recommended)
- hessian-eigenthings or PyHessian library

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Library incompatibility with HuggingFace models | Medium | High | Fallback to PyHessian or manual HVP |
| Memory exhaustion on large models | Medium | Medium | Reduce batch size, use gradient checkpointing |
| Hessian computation too slow | Low | Medium | Use top-k approximation, reduce Lanczos steps |

---

## Implementation Notes

### Recommended Library: hessian-eigenthings
```python
from hessian_eigenthings import HessianOperator, lanczos, trace
H = HessianOperator(model, dataloader, loss_fn)
eigenvalues = lanczos(H, k=20, seed=42).eigenvalues
trace_estimate = trace(H, num_matvecs=100, seed=42)
```

### Fallback: PyHessian
```python
from pyhessian import hessian
hess = hessian(model, criterion, data=(inputs, targets), cuda=True)
eigenvalues, _ = hess.eigenvalues(top_n=20)
trace_val = hess.trace()
```

---

*Generated from Phase 2C: 02c_experiment_brief.md*
*Next Phase: Architecture Design (03_architecture.md)*
