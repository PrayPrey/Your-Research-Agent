# Product Requirements Document (PRD): h-m2

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis:** Selective SSM adapter distills Q/K/V to A/B/C/Δ preserving Jacobian geometry (W2 < 0.05)
**Phase:** Phase 3 - Implementation Planning
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## Executive Summary

This PRD specifies the implementation requirements for hypothesis h-m2, which validates that selective State Space Model (SSM) adapters can distill attention mechanisms (Q/K/V operators) to SSM parameters (A/B/C/Δ) while preserving Jacobian geometry. The experiment tests adapter-based knowledge distillation using the MOHAWK framework on a single LLaMA-7B layer (L28), measuring Wasserstein-2 distance between teacher (attention) and student (SSM) Jacobian eigenvalue distributions.

**Key Success Criterion:** W2 Jacobian distance < 0.05 at SSM state size N=512

**Gate Type:** MUST_WORK - failure indicates attention-SSM operator incompatibility, requiring PIVOT to LTI control analysis.

---

## Problem Statement

### Context
Following h-m1's finding that deep Transformer layers do NOT exhibit low-rank structure (r_eff ~1554-1647), h-m2 tests whether adapter distillation can convert full-rank attention operators to bounded-state SSM while preserving operator-level geometry (not just output matching). This validates the feasibility of post-hoc Transformer-to-SSM conversion independent of rank assumptions.

### Hypothesis Statement
Selective SSM with input-conditioned parameters Δ(x) can compress attention operators via adapter-based distillation while preserving Jacobian geometry (Wasserstein-2 eigenvalue distance < 0.05).

### Research Questions
1. Can MOHAWK distillation preserve Jacobian geometry (W2 < 0.05) when converting attention to SSM?
2. Does distillation MSE exhibit exponential decay with increasing SSM state size N?
3. Is cross-domain stability maintained (The Pile vs LongBench error delta < 3%)?
4. Does selective SSM (input-conditioned Δ) outperform LTI control (fixed Δ) by 2×?

---

## Functional Requirements

### FR-1: Data Preparation Module
**Priority:** P0 (Critical Path)
**Description:** Download and preprocess calibration and evaluation datasets for adapter distillation training.

**Requirements:**
- FR-1.1: Download The Pile dataset from HuggingFace (streaming mode) with fallback to C4 dataset if unavailable
- FR-1.2: Download LongBench dataset from THUDM/LongBench (4 tasks: narrativeqa, qasper, hotpotqa, multifieldqa_en)
- FR-1.3: Tokenize datasets using LLaMA tokenizer with context windowing (8K standard, 128K extended)
- FR-1.4: Create streaming data loaders for The Pile (calibration, 3B tokens total across 3 stages)
- FR-1.5: Create evaluation data loaders for LongBench test split (~4.75K samples)

**Acceptance Criteria:**
- Datasets loaded successfully from HuggingFace
- Tokenization produces correct context lengths (8K/128K)
- Data loaders yield batches of 8 sequences × 4096 tokens

**Dependencies:** None

---

### FR-2: Model Loading and Layer Extraction
**Priority:** P0 (Critical Path)
**Description:** Load LLaMA-7B model and extract target attention layer L28 for distillation.

**Requirements:**
- FR-2.1: Load LLaMA-2-7b-hf from HuggingFace with HF access token
- FR-2.2: Extract attention layer L28: `model.model.layers[28].self_attn`
- FR-2.3: Extract Q/K/V projection matrices: `q_proj`, `k_proj`, `v_proj` (4096 → 4096 each)
- FR-2.4: Configure model for FP16 mixed precision and single GPU inference
- FR-2.5: Implement RoPE scaling for 128K context window extension

**Acceptance Criteria:**
- Model loads successfully with HF token authentication
- Layer L28 accessible via `model.model.layers[28]`
- Q/K/V projections have correct dimensions (4096 × 4096)

**Dependencies:** None

---

### FR-3: Selective SSM Adapter Implementation
**Priority:** P0 (Critical Path)
**Description:** Implement SelectiveSSMAdapter module using official Mamba SSM library.

**Requirements:**
- FR-3.1: Install mamba-ssm library (`pip install mamba-ssm --no-build-isolation`)
- FR-3.2: Implement SelectiveSSMAdapter class with configurable state size N
- FR-3.3: Initialize Mamba SSM core with parameters: d_model=4096, d_state=N, d_conv=4, expand=2
- FR-3.4: Implement adapter projection layer (Linear: d_model → d_model)
- FR-3.5: Implement forward pass: input → adapter_proj → SSM → output

**Acceptance Criteria:**
- SelectiveSSMAdapter produces outputs with shape (B, L, 4096)
- SSM state size N is configurable via constructor argument
- Forward pass executes without CUDA errors on single GPU

**Dependencies:** FR-2 (model loading)

---

### FR-4: MOHAWK Distillation Training Loop
**Priority:** P0 (Critical Path)
**Description:** Implement 3-stage MOHAWK distillation framework for adapter training.

**Requirements:**
- FR-4.1: **Stage 1 - Matrix Orientation** (100M tokens, 1 epoch)
  - Loss: Frobenius norm ||M_Teacher - M_Student||_F
  - Optimizer: AdamW, lr=1e-4
  - Batch size: 8 sequences × 4096 tokens
- FR-4.2: **Stage 2 - Hidden-State Alignment** (500M tokens, 1 epoch)
  - Loss: MSE(h_teacher, h_student) + 0.1 * W2(eigenvals_teacher, eigenvals_student)
  - Optimizer: AdamW, lr=5e-5
  - Batch size: 8 sequences
- FR-4.3: **Stage 3 - End-to-End Distillation** (2.4B tokens, ~5 epochs)
  - Loss: MSE(y_teacher, y_student) + perplexity_loss
  - Optimizer: AdamW, lr=1e-5
  - Batch size: 8 sequences
- FR-4.4: Implement gradient accumulation (4 steps, effective batch size = 32 sequences)
- FR-4.5: Save adapter checkpoints after each stage

**Acceptance Criteria:**
- Training completes 3 stages sequentially without OOM errors
- Loss curves saved for each stage (100M → 500M → 2.4B tokens)
- Adapter checkpoints saved with state_dict for each stage

**Dependencies:** FR-3 (SSM adapter), FR-1 (data loaders)

---

### FR-5: Jacobian Alignment Computation
**Priority:** P0 (Critical Path)
**Description:** Compute Wasserstein-2 distance between teacher and student Jacobian eigenvalue distributions.

**Requirements:**
- FR-5.1: Implement Jacobian computation using `torch.autograd.functional.jacobian`
- FR-5.2: Compute eigenvalues of J @ J.T for teacher (attention) and student (SSM)
- FR-5.3: Compute Wasserstein-2 distance using `scipy.stats.wasserstein_distance`
- FR-5.4: Evaluate on 100 random samples from LongBench test set per task
- FR-5.5: Report W2 distance with mean and standard deviation across samples

**Acceptance Criteria:**
- W2 distance computation completes without numerical instability
- Results reported for N ∈ {64, 128, 256, 512, 1024}
- W2 < 0.05 at N=512 (success criterion)

**Dependencies:** FR-4 (trained adapter)

---

### FR-6: Distillation MSE Evaluation
**Priority:** P0 (Critical Path)
**Description:** Measure output MSE between teacher and student across SSM state sizes.

**Requirements:**
- FR-6.1: Compute MSE(y_teacher, y_student) for each SSM state size N
- FR-6.2: Fit exponential decay curve: MSE(N) = a * exp(-b * N)
- FR-6.3: Report exponential fit R² (success criterion: R² > 0.95)
- FR-6.4: Generate log-log plot of MSE vs N with fitted curve

**Acceptance Criteria:**
- MSE decreases monotonically with increasing N
- Exponential fit R² > 0.95
- Plot saved to `figures/mse_decay_vs_N.png`

**Dependencies:** FR-4 (trained adapter)

---

### FR-7: Cross-Domain Stability Test
**Priority:** P1 (Important)
**Description:** Validate generalization by comparing calibration (The Pile) vs evaluation (LongBench) errors.

**Requirements:**
- FR-7.1: Compute MSE on held-out subset of The Pile (100 samples)
- FR-7.2: Compute MSE on LongBench test set (4 tasks × 100 samples)
- FR-7.3: Calculate absolute error delta: |Error(Pile) - Error(LongBench)|
- FR-7.4: Report domain stability (success criterion: delta < 3%)

**Acceptance Criteria:**
- Error delta < 3% absolute difference
- Scatter plot saved to `figures/cross_domain_stability.png`

**Dependencies:** FR-4 (trained adapter), FR-6 (MSE evaluation)

---

### FR-8: Selective vs LTI Control Experiment
**Priority:** P1 (Important)
**Description:** Compare selective SSM (input-conditioned Δ) vs LTI SSM (fixed Δ) baseline.

**Requirements:**
- FR-8.1: Train LTI control variant with frozen Δ parameters (Δ(x) = constant)
- FR-8.2: Use identical training protocol (3 stages, same token budget)
- FR-8.3: Compute MSE ratio: MSE_selective / MSE_LTI
- FR-8.4: Report selectivity advantage (success criterion: ratio < 0.5, i.e., 2× improvement)

**Acceptance Criteria:**
- LTI control training completes successfully
- MSE_selective / MSE_LTI < 0.5 (2× advantage)
- Bar chart comparison saved to `figures/selective_vs_lti.png`

**Dependencies:** FR-4 (MOHAWK training protocol)

---

### FR-9: SSM State Size Sweep
**Priority:** P0 (Critical Path)
**Description:** Train adapters with varying SSM state sizes to validate exponential MSE decay.

**Requirements:**
- FR-9.1: Train adapters for N ∈ {64, 128, 256, 512, 1024}
- FR-9.2: Use identical training protocol for fair comparison
- FR-9.3: Evaluate all metrics (W2, MSE, cross-domain) for each N
- FR-9.4: Generate comparative plots across state sizes

**Acceptance Criteria:**
- 5 adapters trained (one per state size)
- Metrics computed for all 5 variants
- Comparison table saved to validation report

**Dependencies:** FR-4 (training protocol), FR-5/6/7 (evaluation metrics)

---

### FR-10: Visualization Generation
**Priority:** P2 (Nice-to-Have)
**Description:** Generate publication-quality figures for validation report.

**Requirements:**
- FR-10.1: MSE Decay vs SSM State Size (log-log plot)
- FR-10.2: Jacobian Eigenvalue Distributions (teacher vs student histograms)
- FR-10.3: Cross-Domain Stability (scatter plot with delta annotation)
- FR-10.4: Distillation Loss Curves (3 stages: 100M → 500M → 2.4B tokens)
- FR-10.5: Selective vs LTI Control (bar chart comparison)
- FR-10.6: Gate Metrics Comparison (target vs actual, MANDATORY)

**Acceptance Criteria:**
- All 6 figures saved to `docs/youra_research/20260318_scope/h-m2/figures/`
- Figures use consistent style (font, color scheme, axis labels)
- Gate metrics figure shows PASS/FAIL status clearly

**Dependencies:** FR-5/6/7/8 (metric computations)

---

## Non-Functional Requirements

### NFR-1: Performance
- Training completes within 5 days on single A100 40GB GPU
- Memory footprint ≤ 40GB (FP16 mixed precision required)
- Data loading does not bottleneck training (streaming prefetch)

### NFR-2: Reproducibility
- Random seed setting for reproducible results
- Checkpoint saving at each distillation stage
- Hyperparameter logging to YAML config file

### NFR-3: Monitoring
- Loss logging at each training step
- W2 distance computed every 10M tokens (Stage 2)
- GPU memory usage tracked with `nvidia-smi`

### NFR-4: Error Handling
- Graceful fallback from The Pile to C4 dataset if download fails
- HF token authentication error handling with clear user message
- CUDA OOM detection with automatic batch size reduction suggestion

### NFR-5: Code Quality
- Type annotations for all functions (Python 3.10+)
- Docstrings following Google style
- Unit tests for Jacobian computation and W2 distance

---

## Dependencies

### External Libraries
- `mamba-ssm` (official Mamba SSM implementation, requires `pip install mamba-ssm --no-build-isolation`)
- `transformers` (HuggingFace, for LLaMA-7B loading)
- `datasets` (HuggingFace, for The Pile and LongBench loading)
- `torch` (PyTorch 2.1+, for model training and Jacobian computation)
- `scipy` (for Wasserstein distance: `scipy.stats.wasserstein_distance`)
- `matplotlib` / `seaborn` (for visualization generation)

### Data Dependencies
- **The Pile** (EleutherAI, calibration data, 825GB uncompressed)
  - Fallback: C4 dataset (`allenai/c4`) if The Pile unavailable
- **LongBench** (THUDM/LongBench, evaluation data, ~4.75K test samples)

### Model Dependencies
- **LLaMA-2-7b-hf** (Meta AI, requires HF access token from meta.com/llama)

### Prerequisite Hypotheses
- **h-m1** (Low-Rank Compression Mechanism)
  - Status: experiment_design COMPLETED, implementation FAILED
  - Impact: h-m2 proceeds WITHOUT low-rank assumption (tests full-rank distillation)
  - Lessons:
    1. Do NOT assume low-rank structure
    2. Test larger SSM state sizes (N up to 1024)
    3. Focus on Jacobian alignment as primary criterion

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)
1. ✅ **W2 Jacobian Distance** < 0.05 at N=512
2. ✅ **Exponential MSE Decay** confirmed (R² > 0.95)
3. ✅ **Cross-Domain Stability** maintained (error delta < 3%)
4. ✅ **Selective SSM Advantage** over LTI (2× improvement, ratio < 0.5)

**Gate Decision:**
- **PASS:** All 4 criteria met → Enable h-m3 (calibration efficiency)
- **FAIL:** Any criterion fails → PIVOT to LTI baseline analysis, document attention-SSM incompatibility

### Secondary Success Criteria
- Training completes without CUDA OOM errors
- All 6 visualization figures generated
- Validation report (04_validation.md) documents findings

---

## Out of Scope

- Full model conversion (only single layer L28 tested)
- Inference latency benchmarking (focus on operator geometry preservation)
- Multi-GPU distributed training (single GPU sufficient for 7B model)
- Hyperparameter tuning beyond MOHAWK defaults (use paper values directly)
- Perplexity evaluation on standard LM benchmarks (focus on distillation metrics)

---

## Risks and Mitigations

### R1: The Pile Dataset Unavailable
**Likelihood:** Medium
**Impact:** High (blocks calibration data)
**Mitigation:** Use C4 dataset (`allenai/c4`) as fallback calibration source

### R2: CUDA Out-of-Memory During Training
**Likelihood:** Medium
**Impact:** High (blocks training)
**Mitigation:**
- Use FP16 mixed precision
- Reduce batch size from 8 to 4 sequences
- Enable gradient accumulation (4 steps)

### R3: Jacobian Computation Numerical Instability
**Likelihood:** Low
**Impact:** High (blocks W2 metric)
**Mitigation:**
- Use double precision (FP64) for Jacobian computation only
- Clip eigenvalues to avoid zero/negative values
- Validate on synthetic data with known Jacobian

### R4: W2 Distance Fails Criterion (W2 ≥ 0.05)
**Likelihood:** Medium (h-m1 failed, attention may not be SSM-compatible)
**Impact:** Critical (MUST_WORK gate failure)
**Mitigation:**
- PIVOT to LTI control comparison to isolate selectivity necessity
- Document operator family incompatibility for Phase 4.5 synthesis
- Consider alternative distillation losses (e.g., spectral norm alignment)

---

## Implementation Phases

### Phase 1: Environment Setup (Epic-001)
- Install mamba-ssm library
- Configure HF access token for LLaMA
- Verify CUDA environment (single GPU, FP16 support)

### Phase 2: Data Preparation (Epic-002)
- Download The Pile / C4 (streaming mode)
- Download LongBench test set
- Implement tokenization and data loaders

### Phase 3: Model and Adapter Implementation (Epic-003)
- Load LLaMA-7B and extract L28
- Implement SelectiveSSMAdapter
- Implement LTI control variant

### Phase 4: MOHAWK Training (Epic-004)
- Stage 1: Matrix Orientation (100M tokens)
- Stage 2: Hidden-State Alignment (500M tokens)
- Stage 3: End-to-End Distillation (2.4B tokens)

### Phase 5: Evaluation and Validation (Epic-005)
- Compute W2 Jacobian distance
- Measure distillation MSE and exponential decay
- Cross-domain stability test
- Selective vs LTI control comparison

### Phase 6: Visualization and Reporting (Epic-006)
- Generate all 6 figures
- Write validation report (04_validation.md)
- Document gate decision (PASS/FAIL)

---

## Appendix A: Reference Implementations

### A1: Official Mamba SSM
- Repository: https://github.com/state-spaces/mamba
- Authors: Albert Gu, Tri Dao
- Version: v2.3.1
- Installation: `pip install mamba-ssm --no-build-isolation`

### A2: MOHAWK Distillation Framework
- Repository: https://github.com/goombalab/phi-mamba
- Paper: "Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models" (NeurIPS 2024)
- Authors: Aviv Bick, Kevin Y. Li, Eric P. Xing, J. Zico Kolter, Albert Gu
- Method: 3-stage distillation (Matrix Orientation → Hidden-State → End-to-End)

### A3: Jacobian Alignment Literature
- GrokAlign (arXiv:2506.12284): Jacobian alignment as training objective
- Transformer Alignment in LLMs (arXiv:2407.07810): SVD analysis of Residual Jacobians
- Edge of Stability (arXiv:2406.00127): Layerwise Jacobian alignment mechanism

---

## Appendix B: Hyperparameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | LLaMA-2-7b-hf | Phase 2C |
| Target Layer | L28 | Phase 2C |
| SSM State Sizes | {64, 128, 256, 512, 1024} | Phase 2C |
| SSM d_conv | 4 | Mamba paper |
| SSM expand | 2 | Mamba paper |
| Stage 1 LR | 1e-4 | MOHAWK paper |
| Stage 2 LR | 5e-5 | MOHAWK paper |
| Stage 3 LR | 1e-5 | MOHAWK paper |
| Batch Size | 8 sequences × 4096 tokens | MOHAWK paper |
| Gradient Accumulation | 4 steps | Memory optimization |
| Mixed Precision | FP16 | A100 40GB constraint |
| Calibration Tokens | 3B (100M + 500M + 2.4B) | Phi-Mamba |
| Jacobian Weight (λ) | 0.1 | Phase 2C |

---

## Appendix C: File Structure

```
docs/youra_research/20260318_scope/h-m2/
├── 02b_context.md                # (Existing) Hypothesis context
├── 02c_experiment_brief.md       # (Existing) Phase 2C specification
├── 03_prd.md                     # (This file) Product Requirements
├── 03_architecture.md            # (To be generated) System architecture
├── 03_logic.md                   # (To be generated) API signatures
├── 03_config.md                  # (To be generated) Hyperparameters
├── 03_tasks.yaml                 # (To be generated) Implementation tasks
├── 04_checkpoint.yaml            # (To be generated) Task tracking
├── 04_validation.md              # (To be generated) Results report
└── figures/                      # Visualization outputs
    ├── mse_decay_vs_N.png
    ├── jacobian_eigenvalues.png
    ├── cross_domain_stability.png
    ├── distillation_loss_curves.png
    ├── selective_vs_lti.png
    └── gate_metrics_comparison.png (MANDATORY)
```

---

**PRD Version:** 1.0
**Last Updated:** 2026-03-18
**Status:** Ready for Architecture Design (Phase 3 Step 3)
