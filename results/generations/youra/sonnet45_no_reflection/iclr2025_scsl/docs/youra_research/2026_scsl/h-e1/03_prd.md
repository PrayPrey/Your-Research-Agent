# Product Requirements Document (PRD)
# Hypothesis: h-e1 - Jacobian Stable Rank Regularization

**Date:** 2026-05-12  
**Author:** Anonymous
**Hypothesis Type:** EXISTENCE (PoC)  
**Source:** Phase 2C Experiment Brief

---

## Executive Summary

Implement a proof-of-concept experiment to validate that residual-corrected Jacobian stable rank (sr_ℓ^res) regularization can reduce mean stable rank by ≥20% while maintaining iso-perplexity (≤1% deviation) during GPT-2 pretraining on C4 dataset.

**Success Criteria:**
- Mean sr_ℓ^res reduction ≥20% vs baseline
- Perplexity deviation ≤1%
- Layer variance <2× mean
- Measurement CV <15%

---

## Problem Statement

Validate whether Jacobian stable rank is a controllable metric via gradient-based regularization during language model pretraining. This is the foundation hypothesis that must work before testing mechanistic claims.

**Gate Type:** MUST_WORK - failure stops entire pipeline

---

## Functional Requirements

### FR-1: Data Preparation
**Priority:** P0  
**Description:** Download and prepare C4 dataset for GPT-2 pretraining

**Acceptance Criteria:**
- C4 dataset loaded from HuggingFace (allenai/c4, en subset)
- Streaming mode configured for 10B token subset
- Tokenization with GPT-2 tokenizer (sequence length 512)
- Train/validation splits prepared

**Dependencies:** HuggingFace Datasets library

---

### FR-2: Baseline Model Implementation
**Priority:** P0  
**Description:** Implement standard GPT-2 125M model without regularization

**Acceptance Criteria:**
- GPT-2 small architecture (12 layers, 768 hidden, 12 heads)
- Random initialization (train from scratch)
- Standard causal language modeling loss
- AdamW optimizer (lr=3e-4, betas=(0.9, 0.95), weight_decay=0.1)
- Cosine LR schedule with 2000-step warmup
- Batch size 32 with gradient accumulation (effective batch 128)

**Model Configuration:**
```python
{
    "vocab_size": 50257,
    "n_positions": 1024,
    "n_embd": 768,
    "n_layer": 12,
    "n_head": 12
}
```

**Dependencies:** HuggingFace Transformers, PyTorch

---

### FR-3: Stable Rank Regularization Implementation
**Priority:** P0  
**Description:** Implement residual-corrected Jacobian stable rank regularization

**Core Components:**
1. **Hutchinson Trace Estimator:**
   - Estimate ||J̃_ℓ||_F^2 via Rademacher sampling
   - 10 probe vectors per layer
   - Gradient-based Jacobian-vector products

2. **Power Iteration for Spectral Norm:**
   - Estimate ||J̃_ℓ||_2 via power iteration
   - 5 iterations per measurement
   - Residual correction: J̃_ℓ = J_ℓ - I

3. **Stable Rank Computation:**
   - sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2
   - Computed per layer during forward pass
   - Averaged across 12 transformer layers

**Regularization Loss:**
```
L_total = L_CLM + λ * mean(sr_ℓ^res)
```

**Hyperparameters:**
- λ (adaptive): tuned to maintain perplexity ≤1% deviation
- Initial λ: 0.01
- Hutchinson probes: 10
- Power iterations: 5

**Acceptance Criteria:**
- Regularization term computed correctly per layer
- Gradient flow through regularization term
- Adaptive λ tuning implemented
- Numerical stability (epsilon=1e-12)

**Dependencies:** PyTorch autodiff, spectral norm utilities

**Reference Implementations:**
- PyTorch spectral_norm (power iteration pattern)
- curvlinops HutchinsonTraceEstimator (Rademacher sampling)
- BackPACK (Jacobian-vector products)

---

### FR-4: Training Variants
**Priority:** P0  
**Description:** Train three model variants for comparison

**Variants:**
1. **Baseline:** Standard GPT-2 (λ=0)
2. **Proposed:** With stable rank regularization (λ adaptive)
3. **Implicit Control:** Adaptive LR without explicit regularization

**Training Configuration:**
- Total tokens: 10B (C4 subset)
- Estimated steps: ~78,125
- Checkpoint frequency: every 10,000 steps
- Seed: 42 (fixed, single seed for PoC)

**Acceptance Criteria:**
- All three variants trained successfully
- Checkpoints saved at regular intervals
- Training logs captured (loss, metrics)

---

### FR-5: Evaluation Metrics
**Priority:** P0  
**Description:** Implement evaluation metrics for hypothesis validation

**Primary Metrics:**

1. **Residual-Corrected Jacobian Stable Rank (sr_ℓ^res):**
   - Measured per layer every 1000 steps
   - Mean across 12 layers
   - Target: ≥20% reduction vs baseline

2. **Perplexity:**
   - Evaluated on C4 validation set
   - Sliding window evaluation (stride=256)
   - Target: ≤1% deviation from baseline

3. **Layer-wise Variance:**
   - Coefficient of variation across layers
   - Target: <2× mean (no compensatory redistribution)

4. **Measurement Precision:**
   - CV for spectral norm estimation
   - Target: <15%

**Acceptance Criteria:**
- All metrics computed correctly
- Metrics logged at specified intervals
- Comparison to baseline automated

**Dependencies:** torchmetrics (Perplexity), custom metric implementations

---

### FR-6: Visualization
**Priority:** P1  
**Description:** Generate figures for results analysis

**Required Figures:**
1. Gate Metrics Comparison (mandatory)
2. Layer-wise Stable Rank Evolution
3. Stable Rank Reduction Distribution
4. Perplexity Trajectory
5. Measurement Precision Analysis

**Output Format:** PNG/PDF saved to `{hypothesis_folder}/figures/`

**Acceptance Criteria:**
- Figures generated automatically during/after training
- Clear visualization of success criteria
- Saved to designated folder

---

## Non-Functional Requirements

### NFR-1: Performance
- Training must complete on single GPU
- GPU memory usage < available VRAM
- Training speed: target 3-5 days on single A100

### NFR-2: Reproducibility
- Fixed seed (42) for reproducibility
- All hyperparameters logged
- Model checkpoints saved

### NFR-3: Code Quality
- Minimal structure (PoC level)
- Single model.py, train.py, config.py, evaluate.py
- Hardcoded/argparse configuration acceptable
- Print + CSV logging sufficient

---

## Data Specifications

### Primary Dataset: C4
- **Source:** HuggingFace Datasets (allenai/c4)
- **Subset:** English only ("en")
- **Size:** 10B token subset
- **Format:** Streaming mode
- **Preprocessing:** GPT-2 tokenizer, sequence length 512

### Robustness Dataset: The Stack
- **Source:** HuggingFace Datasets (bigcode/the-stack)
- **Purpose:** Domain robustness validation (optional for PoC)

---

## Technical Dependencies

### Required Libraries:
- PyTorch >= 2.0
- HuggingFace Transformers
- HuggingFace Datasets
- torchmetrics
- numpy, matplotlib (visualization)

### Hardware:
- Single GPU (CUDA required)
- Recommended: A100 or V100
- Minimum VRAM: 40GB

### Environment:
```bash
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
```

---

## Success Criteria Summary

**PoC Pass Condition:**
1. Code runs without error
2. Mean sr_ℓ^res reduction ≥20% vs baseline
3. Perplexity deviation ≤1%

**Gate Validation (MUST_WORK):**
- sr_ℓ^res reduction ≥20%
- AND perplexity deviation ≤1%
- AND layer variance <2× mean
- AND measurement CV <15%

**If Gate Fails:**
Stop pipeline - stable rank not controllable → pivot to alternative metrics (SVD-based rank, gradient flow analysis)

---

## Out of Scope (PoC)

- Multiple seeds (single seed sufficient)
- Extensive ablations
- Transfer validation
- Domain robustness testing (deferred)
- Production-quality code structure
- Extensive hyperparameter tuning

---

## Timeline (Reference Only)

Phase 3 → Phase 4 → Validation

**Note:** No time estimates per workflow policy - focus on WHAT, not WHEN

---

## Appendix: Phase 2C Reference

**Source Document:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_scsl_sonnet45_no_reflection/docs/youra_research/20260512_scsl/h-e1/02c_experiment_brief.md`

**Key Research Findings:**
- PyTorch spectral_norm provides power iteration pattern
- curvlinops offers Hutchinson trace implementation
- NVIDIA Megatron-LM provides GPT-2 pretraining infrastructure
- C4 dataset validated for language model pretraining (T5 v1.1)

---

**Status:** Ready for Phase 3 Architecture Design  
**Next Steps:** Generate 03_architecture.md via architecture-agent
