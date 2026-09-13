---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
document_type: prd
created_at: 2026-05-12
author: Phase 3 Implementation Planning
source: 02c_experiment_brief.md
stepsCompleted:
  - requirements_gathering
  - functional_requirements
  - success_criteria
version: 1.0
---

# Product Requirements Document: H-E1 Quotient Space Existence

## Executive Summary

This PRD defines the implementation requirements for hypothesis H-E1, which validates the existence of a finite-dimensional quotient space that captures task-relevant computational structure across neural network architectures (CNNs, Transformers, RNNs).

**Objective:** Implement and validate a Deep Sets-based encoder with equivariance constraints that projects neural network weights into a shared K-dimensional quotient space.

**Success Criteria:** 
- Reconstruction error <10% 
- Frozen-K generalization to unseen architectures (R_RNN<10%)
- Kernel robustness ≥90% of permutations preserve outputs with D<0.01

**Hypothesis Type:** EXISTENCE (PoC validation) - LIGHT tier implementation (≤15 tasks)

## Problem Statement

**Research Question:** Can a finite-dimensional quotient space capture task-relevant computational structure across heterogeneous neural network architectures?

**Current Gap:** Existing methods (DeepSets ~70% probe transfer, NFN +17% on homogeneous INR zoos) operate within single architecture families or use unstructured embeddings. No prior work demonstrates scalable equivariant processing across heterogeneous families (CNN/Transformer/RNN) with geometric validation.

**Validation Approach:** Train Deep Sets encoder with equivariance loss on ModelZoo-14K, measure reconstruction error, frozen-K generalization, and kernel robustness.

## Functional Requirements

### FR-1: Dataset Acquisition and Preprocessing

**Priority:** P0 (Blocking)
**Complexity:** High

**Requirements:**
- Download 14,000 pretrained models from HuggingFace Model Hub
- Filter models by: 10M-100M parameters, ImageNet-trained, architecture family (CNN/Transformer/RNN)
- Architecture distribution: ResNet/EfficientNet/MobileNet (CNN), BERT/ViT/DeiT (Transformer), LSTM/GRU (RNN)
- Split: 70% train (9,800 models), 15% val (2,100 models), 15% test (2,100 models)
- Preprocess weights: flatten per model, layer-wise normalization (mean=0, std=1)
- Store as weight vectors with architecture labels

**Acceptance Criteria:**
- All 14,000 models successfully downloaded and verified
- Correct split ratios maintained
- Preprocessing produces normalized weight vectors
- Architecture labels correctly assigned

**Data Specification:**
```python
{
  "model_id": str,  # HuggingFace model identifier
  "architecture_family": str,  # "CNN" | "Transformer" | "RNN"
  "parameter_count": int,  # 10M-100M
  "weight_vector": torch.Tensor,  # Flattened, normalized
  "split": str  # "train" | "val" | "test"
}
```

### FR-2: Baseline Model Implementation

**Priority:** P0 (Blocking)
**Complexity:** Medium

**Requirements:**
- Implement standard Deep Sets encoder (Zaheer et al. 2017)
- Architecture: Encoder MLP [512, 256, 128] → Sum pooling → Decoder MLP [128, 256] → K-dim output
- No equivariance constraints (baseline comparison)
- Support K ∈ {16, 32, 64}

**Acceptance Criteria:**
- Model accepts variable-length weight sets as input
- Permutation-invariant aggregation via sum pooling
- Output dimensionality configurable (K parameter)
- Training converges on validation set

### FR-3: Proposed Model Implementation (Slot-Equivariant Encoder)

**Priority:** P0 (Blocking)
**Complexity:** Very High

**Requirements:**
- Extend Deep Sets with architecture-specific embedding layer (3 classes: CNN/Transformer/RNN)
- Implement equivariance loss: L_equiv = MSE(z, z_permuted) where z_permuted uses randomly permuted weights
- Combined loss: L = L_recon + λ_equiv × L_equiv
- Reconstruction decoder: maps K-dim quotient representation back to weight space
- Support λ_equiv ∈ {0.0, 0.25, 0.5, 0.75, 1.0} (ablation study)

**Acceptance Criteria:**
- Architecture embedding injected before per-element encoding
- Equivariance loss correctly computed with random permutations
- Loss weighting configurable via λ_equiv parameter
- Reconstruction decoder produces weight-space outputs

**Model Architecture:**
```python
SlotEquivariantEncoder(
  arch_embedder: Embedding(3, 64),
  phi: MLP([weight_dim+64, 256, 128]),  # Per-element encoder
  rho: MLP([128, 256, K]),  # Aggregation decoder
  reconstruct: MLP([K, 256, weight_dim])  # Reconstruction decoder
)
```

### FR-4: Training Protocol

**Priority:** P0 (Blocking)
**Complexity:** Medium

**Requirements:**
- Optimizer: Adam (lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4)
- Learning rate schedule: CosineAnnealingLR(T_max=100)
- Batch size: 32 models per batch
- Epochs: 100
- Single random seed (seed=42) for EXISTENCE PoC
- Early stopping on validation reconstruction error (patience=10)

**Acceptance Criteria:**
- Training loop implements combined loss correctly
- Learning rate schedule applied per epoch
- Validation metrics logged every epoch
- Early stopping prevents overfitting

### FR-5: Evaluation Metrics Implementation

**Priority:** P0 (Blocking)
**Complexity:** High

**Requirements:**

**Primary Metrics:**
1. **Reconstruction Error:** MSE(W_original, W_reconstructed) / ||W_original||²
   - Target: <10%
   - Computed on test set (2,100 models)

2. **Frozen-K Generalization (R_RNN):** Train on CNN+Transformer only, test on RNN holdout
   - Target: <10%
   - Train on 70% of CNN+Transformer, test on 100% of RNN test set
   - Encoder frozen after training (no fine-tuning)

3. **Kernel Robustness:** Percentage of random neuron permutations preserving outputs
   - Target: ≥90% with divergence D<0.01
   - Apply 1000 random permutations per test model
   - Measure output divergence: ||z_original - z_permuted||

**Secondary Metrics:**
- Training loss curves (reconstruction + equivariance components)
- Per-architecture reconstruction error breakdown
- K-dimensionality sensitivity analysis

**Acceptance Criteria:**
- All three primary metrics computed correctly
- Frozen-K evaluation uses separate train/test architecture splits
- Kernel robustness tested with sufficient permutation samples (1000)
- Metrics pass hypothesis success criteria (reconstruction <10%, R_RNN <10%, robustness ≥90%)

### FR-6: Ablation Studies

**Priority:** P1 (Important)
**Complexity:** Low

**Requirements:**
- λ_equiv ablation: Train models with {0.0, 0.25, 0.5, 0.75, 1.0}
- K dimensionality ablation: Train models with K ∈ {16, 32, 64}
- Compare proposed vs baseline (λ_equiv=0 is baseline)

**Acceptance Criteria:**
- All λ_equiv values tested
- All K values tested
- Results show impact of equivariance loss weight
- Minimal K identified for <10% reconstruction error

### FR-7: Visualization and Reporting

**Priority:** P1 (Important)
**Complexity:** Medium

**Requirements:**

**Mandatory Figure:**
- Gate metrics comparison: Bar chart showing target vs actual for reconstruction error, frozen-K generalization, kernel robustness

**Additional Figures:**
1. Quotient space visualization (t-SNE/UMAP colored by architecture family)
2. Reconstruction error distribution histogram
3. K-dimensionality analysis (reconstruction error vs K line plot)
4. Cross-architecture transfer heatmap
5. Training curves (loss components over epochs)

**Acceptance Criteria:**
- All figures generated automatically during evaluation
- Figures saved to `h-e1/figures/` directory
- Gate metrics figure clearly shows pass/fail status
- Visualizations support hypothesis validation

## Non-Functional Requirements

### NFR-1: Performance

- **Training Time:** Complete 100 epochs within reasonable time on single GPU
- **Memory Efficiency:** Fit model + batch on single GPU (16GB minimum)
- **Inference Speed:** Process test set (2,100 models) within 1 hour

### NFR-2: Reproducibility

- **Fixed Seeds:** All random operations seeded (PyTorch, NumPy, Python)
- **Deterministic Operations:** Use deterministic CUDA operations where possible
- **Version Pinning:** Pin PyTorch, transformers, HuggingFace Hub versions
- **Checkpoint Saving:** Save model checkpoints at best validation performance

### NFR-3: Code Quality

- **Modularity:** Separate data loading, model definition, training, evaluation
- **Documentation:** Docstrings for all public functions and classes
- **Logging:** Structured logging for training progress and metrics
- **Error Handling:** Graceful handling of download failures and OOM errors

### NFR-4: Infrastructure (LIGHT Tier)

- **Configuration:** Hardcoded hyperparameters or argparse (no YAML required)
- **Logging:** Print statements + CSV export (no WandB required)
- **Testing:** Smoke tests for data loading and forward pass (no unit tests required)

## Dependencies and Prerequisites

### External Dependencies

**Python Libraries:**
- `torch>=2.0.0` (Deep learning framework)
- `transformers>=4.30.0` (HuggingFace model loading)
- `numpy>=1.24.0` (Array operations)
- `scikit-learn>=1.3.0` (t-SNE/UMAP for visualization)
- `matplotlib>=3.7.0` (Plotting)
- `tqdm>=4.65.0` (Progress bars)

**Data Dependencies:**
- HuggingFace Model Hub API access
- Internet connection for model downloads (one-time, can cache)
- Storage: ~50GB for cached models

**Compute Requirements:**
- Single GPU with ≥16GB VRAM (NVIDIA recommended)
- CPU: 8+ cores for data preprocessing
- RAM: 32GB minimum for model loading

### Phase Dependencies

**Upstream (Completed):**
- Phase 2C: Experiment design completed (02c_experiment_brief.md exists)

**Downstream (Next):**
- Phase 4: Implementation using generated task list (03_tasks.yaml)
- Phase 5: Baseline comparison (if hypothesis succeeds)

## Success Criteria

### Gate Condition: MUST_WORK

This hypothesis uses a MUST_WORK gate. Failure stops the entire verification workflow.

### Primary Success Criteria (All Required)

1. **Reconstruction Error <10%**
   - Measured on test set (2,100 models)
   - Relative error: MSE / ||W_original||²

2. **Frozen-K Generalization <10%**
   - R_RNN computed on RNN test set with encoder trained only on CNN+Transformer
   - No fine-tuning allowed

3. **Kernel Robustness ≥90%**
   - At least 900/1000 random permutations preserve outputs
   - Output divergence D<0.01 threshold

### Secondary Success Indicators

- Training converges without instability
- Proposed model outperforms baseline (λ_equiv=0)
- Quotient space visualization shows architecture clustering
- K=32 or K=64 sufficient (not all models require K=128)

### Failure Modes and Responses

**If Reconstruction Error >10%:**
- Root cause analysis: Is K too small? Is training unstable?
- Response: Increase K, tune learning rate, extend training epochs

**If Frozen-K Fails (R_RNN >10%):**
- Root cause: Quotient space is architecture-specific, not shared
- Response: PIVOT to per-family encoders, redesign mechanism hypothesis (H-M)

**If Kernel Robustness <90%:**
- Root cause: Permutation symmetries not captured by equivariance loss
- Response: EXPLORE alternative slot encodings (attention-based, graph neural networks)

## Open Questions and Risks

### Open Questions

1. **Optimal K value:** Is K=32 sufficient, or is K=64 required?
   - Mitigation: Ablation study tests {16, 32, 64}

2. **Equivariance loss weight:** What is optimal λ_equiv value?
   - Mitigation: Ablation study tests {0.0, 0.25, 0.5, 0.75, 1.0}

3. **Model download failures:** HuggingFace API rate limits or model unavailability?
   - Mitigation: Implement retry logic, cache downloaded models

### Risks

**High Risk:**
- **ModelZoo-14K scale:** Downloading 14,000 models may take days
  - Mitigation: Parallel downloads, resume capability, start with subset for debugging

**Medium Risk:**
- **GPU memory:** Large models may not fit in batch size 32
  - Mitigation: Dynamic batching based on model size, gradient accumulation

**Low Risk:**
- **Training instability:** Combined loss may have conflicting gradients
  - Mitigation: Learning rate tuning, gradient clipping, loss weight scheduling

## Appendix

### Reference Implementations

**Primary:**
- dpernes/deepsets-digitsum (Deep Sets PyTorch implementation)
- arxiv:2305.16625 (Set-based Neural Network Encoding)

**Model Zoo:**
- Zehong-Wang/Awesome-Weight-Space-Learning (Weight space learning collection)

### Architecture Diagram

```
Input: Weight vectors W (B, N, D)
  ↓
Architecture Embedding (3 → 64)
  ↓
Per-element Encoder φ (MLP: D+64 → 256 → 128)
  ↓
Permutation-Invariant Aggregation (Sum/Mean)
  ↓
Post-aggregation Decoder ρ (MLP: 128 → 256 → K)
  ↓
Output: Quotient representation z (B, K)
  ↓ (for reconstruction)
Reconstruction Decoder (MLP: K → 256 → D)
  ↓
Output: Reconstructed weights W' (B, D)
```

### Traceability Matrix

| Requirement | Source | Implementation |
|-------------|--------|----------------|
| ModelZoo-14K | Phase 2B, 02c_experiment_brief.md | FR-1 |
| Deep Sets baseline | 02c_experiment_brief.md, dpernes/deepsets-digitsum | FR-2 |
| Equivariance loss | Hypothesis statement, 02c_experiment_brief.md | FR-3 |
| K ∈ {16,32,64} | 03_refinement.yaml controlled variables | FR-3, FR-6 |
| λ_equiv ablation | 03_refinement.yaml controlled variables | FR-6 |
| Reconstruction <10% | Hypothesis success criteria | FR-5 |
| Frozen-K generalization | Hypothesis success criteria | FR-5 |
| Kernel robustness ≥90% | Hypothesis success criteria | FR-5 |
| LIGHT infrastructure | Task budget (EXISTENCE hypothesis) | NFR-4 |

---

**Document Status:** Complete
**Next Phase:** Phase 3 Step 3 - Architecture Design
**Task Budget:** LIGHT tier (≤15 tasks total)
